
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

## Adding Collaborators to a Private Repository

If this repository is private and you need to grant access to collaborators, follow these steps:

### Via GitHub Web Interface

1. **Navigate to the repository** on GitHub (github.com/knielbo/knielbo.github.io)
2. Click on **Settings** tab (requires admin/owner access)
3. In the left sidebar, click **Collaborators** (or **Collaborators and teams** for organization repositories)
4. Click the **Add people** button
5. Enter the GitHub username or email address of the person you want to add
6. Select the appropriate permission level:
   - **Read**: View and clone the repository
   - **Triage**: Read access plus manage issues and pull requests
   - **Write**: Read and clone, plus push to the repository
   - **Maintain**: Write access plus manage settings (without access to sensitive actions)
   - **Admin**: Full access including repository deletion
7. Click **Add [username] to this repository**
8. The collaborator will receive an invitation email and must accept it to gain access

### Via GitHub CLI (gh)

```bash
# Add a collaborator with write permission
gh api repos/knielbo/knielbo.github.io/collaborators/USERNAME -X PUT -f permission=push

# Add a collaborator with read permission
gh api repos/knielbo/knielbo.github.io/collaborators/USERNAME -X PUT -f permission=pull

# Add a collaborator with admin permission
gh api repos/knielbo/knielbo.github.io/collaborators/USERNAME -X PUT -f permission=admin
```

### Permission Levels Explained

- **Read (pull)**: Best for contributors who need to view or discuss the project
- **Write (push)**: Best for contributors who actively work on the project
- **Admin**: Best for project managers who need full control

### Notes

- Only repository owners and admins can add collaborators
- Collaborators must have a GitHub account
- For organization repositories, you may need to be an organization owner or have appropriate team permissions
- Invited collaborators can accept the invitation from their email or from the repository page
