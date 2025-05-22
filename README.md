# Kristoffer Nielbo's Personal Website

Minimal personal website hosted via GitHub Pages. Contains basic information and a dynamically generated chronological list of publications.

## Repository Structure

```
.
├── files
│   └── pure_research_outputs.html   # Source publication data
├── index.html                       # Homepage
├── publications.html                # Chronological publication list (generated)
├── publications_template.html       # Template for publication list
└── src
    └── pure_to_web.py               # Script to generate publications.html
```

## Usage

To update your publication list:

```bash
cd src
python pure_to_web.py
```

This script parses `pure_research_outputs.html` and regenerates `publications.html` based on the provided template.

## Requirements

- Python 3.x
- BeautifulSoup4 (`pip install beautifulsoup4`)

 
