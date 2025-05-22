import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict

class PublicationParser:
    def __init__(self, source_html):
        self.source_html = source_html
        self.publications = []

    def parse_html(self):
        with open(self.source_html, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        self.extract_publications(soup)

    def extract_publications(self, soup):
        pub_divs = soup.find_all('div', class_='rendering_researchoutput')
        for div in pub_divs:
            text = div.get_text(separator=' ', strip=True)
            year_match = re.search(r'\((\d{4})(?:,\s*[a-zA-Z]{3}\s*\d{1,2})?\)', text)
            year = year_match.group(1) if year_match else "No year"
            self.publications.append({'year': year, 'full_citation': text})

    def get_publications_by_year(self):
        publications_by_year = defaultdict(list)
        for pub in self.publications:
            publications_by_year[pub['year']].append(pub)
        return dict(sorted(publications_by_year.items(), reverse=True))


class HTMLPopulator:
    def __init__(self, template_html, output_html, publications_by_year):
        self.template_html = template_html
        self.output_html = output_html
        self.publications_by_year = publications_by_year

    def populate_publications(self):
        # Load the template file
        with open(self.template_html, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Find insertion point (after <h1>Publications</h1>)
        h1_tag = soup.find('h1', string='Publications')

        # Add publications after the h1 tag
        insertion_point = h1_tag

        for year, pubs in self.publications_by_year.items():
            year_header = soup.new_tag('h4')
            year_header.string = year
            insertion_point.insert_after(year_header)
            insertion_point = year_header

            ul = soup.new_tag('ul')
            for pub in pubs:
                li = soup.new_tag('li')
                li.string = pub['full_citation']
                ul.append(li)

            insertion_point.insert_after(ul)
            insertion_point = ul

        # Write output HTML
        with open(self.output_html, 'w', encoding='utf-8') as file:
            file.write(str(soup))


def main():
    source_html = '../files/pure_research_outputs.html'
    template_html = '../publications_template.html'
    output_html = '../publications.html'

    parser = PublicationParser(source_html)
    parser.parse_html()
    publications_by_year = parser.get_publications_by_year()

    populator = HTMLPopulator(template_html, output_html, publications_by_year)
    populator.populate_publications()

if __name__ == "__main__":
    main()
