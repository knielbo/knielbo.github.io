
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from bs4 import BeautifulSoup
from collections import defaultdict

class PublicationBipartiteGraph:
    def __init__(self, html_file):
        self.html_file = html_file
        self.publications = defaultdict(list)  # {year: [(authors, journal)]}

    def parse_html(self):
        with open(self.html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        pub_divs = soup.find_all('div', class_='rendering_researchoutput')

        for div in pub_divs:
            text = self.normalize_year(div.get_text(separator=' ', strip=True))
            year_match = re.search(r'\((\d{4})\)', text)
            if year_match:
                year = int(year_match.group(1))
                authors = self.extract_authors(div, text)
                journal = self.extract_journal(div)
                if authors and journal:
                    self.publications[year].append((authors, journal))

    def normalize_year(self, text):
        return re.sub(r'\((\d{4}), [A-Za-z]{3} \d{1,2}\)', r'(\1)', text)

    def clean_author_text(self, text):
        return re.sub(r'\(.*?ed.*?\)', '', text, flags=re.IGNORECASE)

    def abbreviate_journal(self, journal_name):
        return journal_name.split()[0].upper()

    def extract_authors(self, div, text):
        authors_text = re.split(r'\(\d{4}\)', text)[0]
        authors_text = self.clean_author_text(authors_text)
        authors_raw = re.split(r', & | & |, ', authors_text)
        authors_cleaned = []
        i = 0
        while i < len(authors_raw):
            surname = authors_raw[i].strip().replace(' ', '')
            initials = ''
            if i + 1 < len(authors_raw):
                potential_initials = authors_raw[i + 1].strip().replace('.', '').replace(' ', '')
                if re.match(r'^[A-Z]+$', potential_initials):
                    initials = potential_initials
                    i += 1
            author_full = f'{surname}-{initials}' if initials else surname.replace('.', '')
            authors_cleaned.append(author_full)
            i += 1
        return authors_cleaned

    def extract_journal(self, div):
        journal = div.find('em')
        return self.abbreviate_journal(journal.get_text(strip=True)) if journal else None

    def plot_bigraphs(self, output_folder='../figs'):
        years = sorted(self.publications.keys())
        n_years = len(years)

        fig, axes = plt.subplots(1, n_years, figsize=(4*n_years, 4), squeeze=False)
        axes = axes.flatten()

        for idx, year in enumerate(years):
            B = nx.Graph()
            for authors, journal in self.publications[year]:
                journal_upper = journal.upper()
                B.add_nodes_from(authors, bipartite=0, color=(194/255, 178/255, 128/255))
                B.add_node(journal_upper, bipartite=1, color=(46/255, 82/255, 66/255))
                B.add_edges_from([(author, journal_upper) for author in authors])

            colors = [B.nodes[n]['color'] for n in B.nodes]
            pos = nx.spring_layout(B, k=0.3, seed=42)
            nx.draw(B, pos, ax=axes[idx], node_size=100, with_labels=True,
                    font_size=7, edge_color='gray', node_color=colors, width=2.0, font_weight='bold')
            axes[idx].set_title(f'{year}', fontsize=14, fontweight='bold')

        plt.tight_layout()
        os.makedirs(output_folder, exist_ok=True)
        plt.savefig(os.path.join(output_folder, 'yearly_publication_bigraphs.png'), dpi=300)
        plt.close()

if __name__ == "__main__":
    html_path = '../files/pure_research_outputs.html'
    bigraph = PublicationBipartiteGraph(html_path)
    bigraph.parse_html()
    bigraph.plot_bigraphs()