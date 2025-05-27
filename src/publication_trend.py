import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
import networkx as nx
import community as community_louvain
import os

class PublicationTrendVisualizer:
    def __init__(self, html_file):
        self.html_file = html_file
        self.publications = []
        self.authors_list = []
        self.journals = []

    def parse_html(self):
        with open(self.html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        self.extract_publications(soup)
        self.extract_authors(soup)
        self.extract_journals(soup)

    def normalize_year(self, text):
        return re.sub(r'\((\d{4}), [A-Za-z]{3} \d{1,2}\)', r'(\1)', text)

    def clean_author_text(self, text):
        return re.sub(r'\(.*?ed.*?\)', '', text, flags=re.IGNORECASE)

    def abbreviate_journal(self, journal_name):
        return journal_name.split()[0].upper()

    def extract_publications(self, soup):
        pub_divs = soup.find_all('div', class_='rendering_researchoutput')
        for div in pub_divs:
            text = self.normalize_year(div.get_text(separator=' ', strip=True))
            year_match = re.search(r'\((\d{4})\)', text)
            if year_match:
                self.publications.append(int(year_match.group(1)))

    def extract_authors(self, soup):
        pub_divs = soup.find_all('div', class_='rendering_researchoutput')
        for div in pub_divs:
            text = self.normalize_year(div.get_text(separator=' ', strip=True))
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
                if initials:
                    authors_cleaned.append(f'{surname}-{initials}')
                else:
                    authors_cleaned.append(surname.replace('.', ''))
                i += 1
            self.authors_list.append(authors_cleaned)

    def extract_journals(self, soup):
        pub_divs = soup.find_all('div', class_='rendering_researchoutput')
        for div in pub_divs:
            journal = div.find('em')
            if journal:
                abbreviated = self.abbreviate_journal(journal.get_text(strip=True))
                self.journals.append(abbreviated)

    def prepare_data(self):
        self.df = pd.DataFrame(self.publications, columns=['Year'])
        self.df = self.df.groupby('Year').size().reset_index(name='Count')

    def estimate_trend(self, n_bootstrap=1000):
        x = self.df['Year'].values.reshape(-1, 1)
        y = self.df['Count'].values

        self.model = LinearRegression().fit(x, y)
        self.df['Trend'] = self.model.predict(x)

        bootstrapped_preds = []
        for _ in range(n_bootstrap):
            x_sample, y_sample = resample(x, y)
            boot_model = LinearRegression().fit(x_sample, y_sample)
            bootstrapped_preds.append(boot_model.predict(x).flatten())

        bootstrapped_preds = np.array(bootstrapped_preds)
        self.pred_mean = np.mean(bootstrapped_preds, axis=0)
        self.pred_std = np.std(bootstrapped_preds, axis=0)

    def plot_trend_and_authors(self, output_folder='../figs'):
        sns.set(style='whitegrid', font_scale=1.2)
        fig, axes = plt.subplots(1, 5, figsize=(50, 10))

        # Trend Plot
        axes[0].bar(self.df['Year'], self.df['Count'], color='#6baed6', edgecolor='black', linewidth=1.2)
        axes[0].plot(self.df['Year'], self.df['Trend'], color='#e34a33', linewidth=2.5)
        axes[0].fill_between(
            self.df['Year'],
            self.pred_mean - 1.96 * self.pred_std,
            self.pred_mean + 1.96 * self.pred_std,
            color='#fdd0a2', alpha=0.4
        )
        axes[0].set_xlabel('Year')
        axes[0].set_ylabel('Number of Publications')

        # Author Collaboration Network
        G = nx.Graph()
        for authors in self.authors_list:
            G.add_nodes_from(authors)
            G.add_edges_from([(a, b) for i, a in enumerate(authors) for b in authors[i + 1:]])

        partition = community_louvain.best_partition(G)
        pos = nx.spring_layout(G, k=0.15)
        cmap = sns.color_palette('tab10', max(partition.values()) + 1)
        nx.draw(G, pos, ax=axes[1], node_size=150, node_color=[cmap[partition[n]] for n in G.nodes], edge_color='grey', with_labels=True, font_size=8)

        # Radial Plot
        theta = np.linspace(0.0, 2 * np.pi, len(self.df), endpoint=False)
        radii = self.df['Count']
        ax_polar = plt.subplot(1, 5, 3, polar=True)
        ax_polar.bar(theta, radii, width=(2*np.pi)/len(radii), color=sns.color_palette('coolwarm', len(radii)), edgecolor='black')
        ax_polar.set_theta_offset(np.pi / 2)
        ax_polar.set_theta_direction(-1)
        ax_polar.set_xticks(theta)
        ax_polar.set_xticklabels(self.df['Year'])

        # Bipartite Graph
        B = nx.Graph()
        for authors, journal in zip(self.authors_list, self.journals):
            journal = journal.upper()
            B.add_nodes_from(authors, bipartite=0, color='skyblue')
            B.add_node(journal, bipartite=1, color='salmon')
            B.add_edges_from([(author, journal) for author in authors])

        colors = [B.nodes[n]['color'] for n in B.nodes]
        pos_bipartite = nx.spring_layout(B, k=0.2)
        nx.draw(B, pos_bipartite, ax=axes[3], node_size=100, with_labels=True, font_size=8, edge_color='gray', node_color=colors)

        # Co-authorship Density Heatmap
        coauthor_matrix = nx.to_pandas_adjacency(G, nodelist=sorted(G.nodes()))
        sns.heatmap(coauthor_matrix, cmap='YlGnBu', ax=axes[4], cbar=True)
        axes[4].plot([0, len(coauthor_matrix)], [0, len(coauthor_matrix)], 'r--')

        plt.tight_layout()
        os.makedirs(output_folder, exist_ok=True)
        plt.savefig(os.path.join(output_folder, 'publication_trends.png'), dpi=300)
        plt.close()

if __name__ == "__main__":
    visualizer = PublicationTrendVisualizer('../files/pure_research_outputs.html')
    visualizer.parse_html()
    visualizer.prepare_data()
    visualizer.estimate_trend()
    visualizer.plot_trend_and_authors()
