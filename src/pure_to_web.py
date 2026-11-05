import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString


ROOT = Path(__file__).resolve().parents[1]
AREA_FILE = ROOT / 'files' / 'research_areas.json'
YEAR_PATTERN = re.compile(r'\((\d{4})(?:,\s*[a-zA-Z]{3}\s*\d{1,2})?\)')


class PublicationParser:
    def __init__(self, source_html):
        self.source_html = Path(source_html)
        self.publications = []
        self.export_date = None

    def parse_html(self):
        soup = BeautifulSoup(self.source_html.read_text(encoding='utf-8'), 'html.parser')
        report = soup.select_one('div.reportrendering > span.body')
        if report:
            date = re.search(r',\s*(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}\s*$', report.get_text())
            if date:
                self.export_date = datetime.strptime(date[1], '%d/%m/%Y').date()
        self.extract_publications(soup)

    def extract_publications(self, soup):
        self.publications.clear()
        for div in soup.select('div.rendering_researchoutput'):
            citation = div.get_text(separator=' ', strip=True)
            # In Pure APA output the title element immediately follows the author/date text.
            date = next((node for node in div.children
                         if isinstance(node, NavigableString) and YEAR_PATTERN.search(node)), None)
            title_tag = date.find_next_sibling() if date else None
            title = ' '.join(title_tag.get_text().split()) if title_tag else citation
            year = YEAR_PATTERN.search(citation)
            link = div.select_one('a.link[href]')
            self.publications.append({
                'year': int(year[1]) if year else None,
                'title': title,
                'url': link['href'] if link else None,
                'full_citation': citation,
            })
        if not self.publications:
            raise ValueError(f'No Pure research outputs found in {self.source_html}. Check the export format.')

    def get_publications_by_year(self):
        groups = defaultdict(list)
        for pub in self.publications:
            groups[pub['year']].append(pub)
        return dict(sorted(groups.items(), key=lambda item: item[0] or 0, reverse=True))


def record_key(record):
    return record['year'], ' '.join(record['title'].casefold().split()), record.get('url')


def assign_research_areas(publications, area_file=AREA_FILE):
    manifest = json.loads(Path(area_file).read_text(encoding='utf-8'))
    domains = dict(manifest['domains'])
    assignments = defaultdict(list)
    assigned_ids = set()
    for item in manifest['assignments']:
        if item['id'] in assigned_ids or item['domain'] not in domains:
            raise ValueError(f'Check the ID and domain of {item["title"]!r} in {area_file}.')
        assigned_ids.add(item['id'])
        assignments[record_key(item)].append(item)

    frequencies = Counter(record_key(pub) for pub in publications)
    unmatched = []
    next_id = max(assigned_ids, default=0) + 1
    used_ids = set()
    for pub in publications:
        key = record_key(pub)
        candidates = assignments.get(key, [])
        # Authors/venues can distinguish records even when title, year and URL coincide.
        matches = [item for item in candidates if item.get('citation') == pub['full_citation']
                   or ('citation' not in item and len(candidates) == 1 and frequencies[key] == 1)]
        if len(matches) == 1 and matches[0]['id'] not in used_ids:
            pub['id'], pub['domain'] = matches[0]['id'], matches[0]['domain']
            used_ids.add(pub['id'])
        else:
            pub['id'], pub['domain'] = next_id, 'pending'
            next_id += 1
            unmatched.append(pub)
    if unmatched:
        domains['pending'] = 'Awaiting classification'
        print(f'{len(unmatched)} output(s) awaiting classification. Add or update their year, title, '
              f'URL (if present), unique ID and domain in {area_file}. For matching year/title/URL '
              'pairs, also set each entry’s citation to its full citation text.', file=sys.stderr)
        for pub in unmatched:
            print(f'  {pub["year"] or "No year"} | {pub["title"]} | {pub["url"] or "no URL"}', file=sys.stderr)
    return domains


class HTMLPopulator:
    def __init__(self, template_html, output_html, publications_by_year, domains, export_date=None):
        self.template_html = Path(template_html)
        self.output_html = Path(output_html)
        self.publications_by_year = publications_by_year
        self.domains = domains
        self.export_date = export_date

    def populate_publications(self):
        soup = BeautifulSoup(self.template_html.read_text(encoding='utf-8'), 'html.parser')
        listing = soup.select_one('#publication-list')
        chart = soup.select_one('script#research-area-data[type="application/json"]')
        if listing is None or chart is None:
            raise ValueError('The template must provide #publication-list and a research-area-data JSON script.')
        listing.clear()
        rows = []
        for year, publications in self.publications_by_year.items():
            heading = soup.new_tag('h4')
            heading.string = str(year or 'No year')
            ul = soup.new_tag('ul')
            for pub in publications:
                li = soup.new_tag('li', id=f'publication-{pub["id"]}')
                li.string = pub['full_citation']
                ul.append(li)
                rows.append({field: pub[field] for field in ('id', 'title', 'year', 'domain')})
            listing.extend([heading, ul])

        payload = json.dumps({'rows': rows, 'domains': self.domains}, ensure_ascii=False, separators=(',', ':'))
        chart.string = payload.replace('<', r'\u003c')  # Keep citation text inside the JSON script element.
        years = [year for year in self.publications_by_year if year is not None]
        year_range = '–'.join(str(year) for year in sorted({min(years), max(years)})) if years else ''
        through_date = (f' · through {self.export_date.day} {self.export_date:%B %Y}' if self.export_date else '')
        for marker, text in [('years', year_range), ('count', str(len(rows))), ('export', through_date)]:
            for tag in soup.select(f'[data-area-{marker}]'):
                tag.string = text
        self.output_html.write_text(str(soup), encoding='utf-8')


def main():
    parser = PublicationParser(ROOT / 'files' / 'pure_research_outputs.html')
    parser.parse_html()
    domains = assign_research_areas(parser.publications)
    populator = HTMLPopulator(ROOT / 'publications_template.html', ROOT / 'publications.html',
                             parser.get_publications_by_year(), domains, parser.export_date)
    populator.populate_publications()


if __name__ == '__main__':
    main()
