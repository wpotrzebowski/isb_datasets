# AGENTS.md

## Cursor Cloud specific instructions

This is the **ISB Dataset Portal** — a static website for SciLifeLab displaying integrated structural biology datasets. There is no Node.js, no Docker, and no backend server involved.

### Key commands

| Action | Command |
|---|---|
| Install deps | `pip install -r requirements.txt` |
| Build HTML from Markdown | `python3 scripts/build.py` |
| Serve locally | `python3 -m http.server 8000` (from repo root) |
| View site | `http://localhost:8000` |

### Notes

- Use `python3` (not `python`) — the system does not have `python` aliased to Python 3.
- The build script (`scripts/build.py`) converts `datasets/*.md` (Markdown + YAML frontmatter) into `datasets/*.html` using the Jinja2 template at `templates/dataset-template.html`. Generated HTML files should not be edited manually.
- There are no formal lint or test commands configured in this project. The primary verification is running `python3 scripts/build.py` successfully and confirming the site renders correctly in a browser.
- `index.html` is hand-maintained and must be updated manually when adding/removing datasets.
- See `BUILD.md` for the Markdown→HTML workflow and `README.md` for project overview and GitHub Pages deployment.
