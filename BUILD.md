# Building HTML from Markdown

This project uses Markdown files with YAML frontmatter to define dataset pages, which are automatically converted to HTML using a template.

## Structure

- `datasets/*.md` - Markdown source files with YAML frontmatter
- `templates/dataset-template.html` - Jinja2 template for generating HTML
- `scripts/build.py` - Python script that converts Markdown to HTML
- `datasets/*.html` - Generated HTML files (do not edit manually)

## Editing Datasets

To edit a dataset, modify the corresponding `.md` file in the `datasets/` directory. The Markdown files use YAML frontmatter to define structured data:

```markdown
---
title: "Dataset Title"
unit_facility: "Facility name"
system_target: "Description"
organism_source: "Organism"
data_collection_years: "~2020–2023"
access_status: "Public"
main_repository: "Repository info"
techniques:
  - "Technique 1"
  - "Technique 2"
repositories:
  - type: "PDB"
    links:
      - url: "https://example.com"
        text: "Link text"
        note: "Optional note"
  - type: "EMDB"
    note: "Note without link"
---
```

## Building Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python scripts/build.py
   ```

This will regenerate all HTML files from the Markdown sources.

## GitHub Actions

The GitHub Actions workflow (`.github/workflows/build.yml`) automatically:
- Runs when Markdown files, templates, or the build script are changed
- Converts all Markdown files to HTML
- Commits the generated HTML files back to the repository

## Adding a New Dataset

1. Create a new `.md` file in the `datasets/` directory (e.g., `dataset-7.md`)
2. Use the same YAML frontmatter structure as existing files
3. Commit and push - GitHub Actions will generate the HTML automatically
4. Update `index.html` to add a link to the new dataset

