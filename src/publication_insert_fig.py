import os
from bs4 import BeautifulSoup

class FigureInserter:
    def __init__(self, html_file, fig_path):
        self.html_file = html_file
        self.fig_path = fig_path

    def insert_figure(self):
        with open(self.html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        img_tag = soup.new_tag('img', src=self.fig_path, alt="Publication Trends", 
                               style="width:100%; margin-bottom:20px; display:block; margin-left:auto; margin-right:auto;")

        h1_tag = soup.find('h1')
        if h1_tag:
            h1_tag.insert_before(img_tag)
        else:
            raise ValueError("<h1> tag not found in HTML file.")

        with open(self.html_file, 'w', encoding='utf-8') as file:
            file.write(str(soup))

if __name__ == "__main__":
    inserter = FigureInserter('../publications.html', 'figs/publication_trends.png')
    inserter.insert_figure()