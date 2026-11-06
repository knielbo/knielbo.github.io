# Kristoffer Nielbo’s academic website

This repository holds the static HTML served by GitHub Pages for Kristoffer Nielbo’s [academic website](https://knielbo.github.io/).

- **Homepage.** Edit [index.html](index.html) directly to update the biography, current affiliations, projects, selected publications, advising, or contact information. The selected publications are handpicked. The contact email is written out in words.
- **Publications.** The [publications page](https://knielbo.github.io/publications.html) lists research outputs by year, newest first. A banner shows yearly author–venue networks. The expandable *Research areas over time* map shows one dot per output, grouped by year and primary research area. Select a group to see its titles.

The Aarhus University Pure export dated **4 November 2026** contains 193 outputs spanning 2011–2026, classified into eight research areas.

Typing `emergence` on the homepage reveals a small Game of Life beneath the name. Click the pattern to reseed it, use Pause/Play to control the animation, and press Escape or select Hide to close it. With reduced motion enabled, it starts paused. The implementation lives in [assets/emergence.js](assets/emergence.js) and [assets/emergence.css](assets/emergence.css).

## Update the publications

1. Export the full research output list from Pure as HTML in APA format. Replace [files/pure_research_outputs.html](files/pure_research_outputs.html) with the new export.
2. Run the update from the repository root using the commands below. The first three commands set up a Python environment for the standard publication scripts. On later runs, activate the same environment and run the last command again.

   ```sh
   python3 -m venv .venv
   . .venv/bin/activate
   python -m pip install beautifulsoup4 matplotlib networkx seaborn
   (cd src && MPLBACKEND=Agg bash update_publications.sh)
   ```

3. Review any outputs reported as **Awaiting classification**. In [files/research_areas.json](files/research_areas.json), assign each new output a unique numeric `id` and a `domain` from the file’s list of areas. Copy its `year` and `title` from the export and include its `url` if available. Keep existing IDs when correcting records. If two records share all three matching fields, include each full citation in its `citation` field. Rerun the update after editing assignments.

The [update script](src/update_publications.sh) runs three steps from `src/`. The figure scripts resolve paths relative to that directory.

| Step | What it produces |
| --- | --- |
| [pure_to_web.py](src/pure_to_web.py) | Builds [publications.html](publications.html) from the Pure export, area assignments, and [HTML template](publications_template.html). It embeds both the citations and the data for the dot map. |
| [publication_bigraphs.py](src/publication_bigraphs.py) | Draws the yearly author–venue networks from the HTML export and saves the [banner image](figs/yearly_publication_bigraphs.png). |
| [publication_insert_fig.py](src/publication_insert_fig.py) | Inserts the banner above the heading in the generated publications page. |

For layout changes, edit the template and rebuild. For the map’s appearance or interactions, edit its [CSS](assets/research-areas.css) or [JavaScript](assets/research-areas.js).

## Preview and publish

From the repository root, run `python3 -m http.server 8000 --bind 127.0.0.1` and open the [local homepage](http://127.0.0.1:8000/) or [local publications page](http://127.0.0.1:8000/publications.html). After a publication update, check the newest citations, open the dot map, and select a group to verify its titles.

GitHub Pages serves the repository root on `main`. Commit the changed source files together with the regenerated `publications.html` and banner when they change, then push to `main` to publish.

## Optional figures

Two standalone scripts produce additional figures. Run them from `src/` if needed.

- [publication_bigraphs_robust.py](src/publication_bigraphs_robust.py) uses the [BibTeX export](files/pure_research_outputs.bib) and `bibtexparser` 1.x to generate [an alternative network figure](figs/yearly_publication_bigraphs_robust.png).
- [publication_trend.py](src/publication_trend.py) uses the HTML export to generate [publication trend and coauthorship plots](figs/publication_trends.png). It also imports `scikit-learn` and `python-louvain` (as `community`).
