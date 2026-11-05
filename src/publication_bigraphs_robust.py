import os
import matplotlib.pyplot as plt
import networkx as nx
import bibtexparser
from collections import defaultdict

class PublicationBigraphRobust:
    def __init__(self, bib_file, output_path):
        self.bib_file = bib_file
        self.output_path = output_path
        self.publications = defaultdict(list)
        self._parse_bib()

    def _parse_bib(self):
        with open(self.bib_file, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        pub_counter = defaultdict(int)

        for entry in bib_database.entries:
            year = entry.get('year', 'UNKNOWN')
            pub_counter[year] += 1
            pub_id = f"pub_{year}_{pub_counter[year]}"

            authors = entry.get('author', '').split(' and ')
            authors = [author.replace('.', '').replace(',', '').replace(' ', '-').strip() for author in authors]

            journal = entry.get('journal', entry.get('booktitle', 'UNKNOWN')).split()[0].upper()

            self.publications[year].append({
                'pub_id': pub_id,
                'authors': authors,
                'journal': journal
            })

    def plot_yearly_bigraphs(self):
        years = sorted(self.publications.keys())
        n_years = len(years)
        fig, axes = plt.subplots(1, n_years, figsize=(4 * n_years, 4), squeeze=False)

        for idx, year in enumerate(years):
            G = nx.Graph()

            for pub in self.publications[year]:
                pub_node = pub['pub_id']
                G.add_node(pub_node, bipartite=0, color='#FFFFFF')

                for author in pub['authors']:
                    G.add_node(author, bipartite=1, color='#C2B280')  # Sand
                    G.add_edge(pub_node, author)

                journal = pub['journal']
                G.add_node(journal, bipartite=1, color='#2E5242')  # Pine Green
                G.add_edge(pub_node, journal)

            ax = axes[0][idx]
            pos = nx.spring_layout(G, k=0.15, iterations=20, seed=42)
            colors = [data['color'] for _, data in G.nodes(data=True)]

            nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors,
                    edge_color='grey', font_weight='bold', node_size=800,
                    font_size=8, edgecolors='black', linewidths=1, width=1.5)

            ax.set_title(year, fontsize=16, fontweight='bold')

        plt.tight_layout()
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        plt.savefig(self.output_path, dpi=300)


if __name__ == "__main__":
    input_bib = '../files/pure_research_outputs.bib'
    output_fig = '../figs/yearly_publication_bigraphs_robust.png'

    pub_bigraph = PublicationBigraphRobust(input_bib, output_fig)
    pub_bigraph.plot_yearly_bigraphs()