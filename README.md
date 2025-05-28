
# Kristoffer Nielbo's Personal Website

A minimal personal website hosted via GitHub Pages. It contains basic information and a dynamically generated chronological list of publications enriched with visualizations.

## Repository Structure

```
.
├── README.md                          # Documentation of the repository
├── figs
│   ├── publication_trends.png         # Trends and analytics of publications
│   └── yearly_publication_bigraphs.png # Annual bipartite author-journal graphs
├── files
│   └── pure_research_outputs.html     # Source HTML publication data
├── index.html                         # Homepage
├── publications.html                  # Chronological publication list (generated)
├── publications_template.html         # Template for the publication list
├── requirements.txt                   # Python package dependencies
└── src
    ├── publication_bigraphs.py        # Generates yearly bipartite graphs (authors & journals)
    ├── publication_insert_fig.py      # Inserts header figures into publications.html
    ├── publication_trend.py           # Creates publication trends and analytics plots
    ├── pure_to_web.py                 # Generates publications.html from HTML source
    └── update_publications.sh         # Bash script to automate publications update
```

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd knielbo.github.io
pip install -r requirements.txt
```

## Usage

Run the `update_publications.sh` script to regenerate your publications and visualizations:

```bash
cd src
bash update_publications.sh
```

This script executes the following processes in order:

- Parse and update the publication list (`pure_to_web.py`)
- Generate yearly bipartite author-journal graphs (`publication_bigraphs.py`)
- Insert header figures into the HTML file (`publication_insert_fig.py`)
- Update publication trend analytics (`publication_trend.py`)

The updated `publications.html` will contain your latest publications and visualizations.

## Requirements

- Python 3.x
- See `requirements.txt` for detailed dependencies.
