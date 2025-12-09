# ISB Dataset Portal

A lightweight static HTML portal for browsing Integrated Structural Biology (ISB) multi-technique datasets from SciLifeLab facilities.

## Overview

This portal provides an overview of datasets that combine multiple experimental and computational techniques, including:
- Cryo-EM
- X-ray crystallography
- SAXS/SANS
- NMR
- Mass spectrometry/Proteomics
- Biophysics
- Molecular dynamics simulations
- Integrative computational modeling

Each dataset has its own dedicated page with detailed information and links to public repositories (PDB, EMDB, EMPIAR, SASBDB, SciLifeLab Data Repository, etc.).

## Visual Identity

This portal uses the official SciLifeLab visual identity:
- **Colors**: Lime (#A7C947), Teal (#045C64), Aqua (#4C979F), Grape (#491F53)
- **Typography**: Lato (headlines) and Lora (body text) from Google Fonts

## Structure

```
isb_simple_portal/
├── index.html              # Main index page with all datasets
├── datasets/               # Individual dataset pages
│   ├── dataset-1.html     # GLIC lipid-binding & gating
│   ├── dataset-2.html     # DeCLIC Ca²⁺-stabilised N-terminal domain
│   ├── dataset-3.html     # MUC2 CysD2 domain
│   ├── dataset-4.html     # MecA/ClpC/ClpP AAA⁺ protease
│   ├── dataset-5.html     # FusB-mediated rescue of EF-G from fusidic acid
│   └── dataset-6.html     # Sodium caprate scattering + CG-MD
├── css/
│   └── style.css          # Stylesheet with SciLifeLab branding
└── README.md              # This file
```

## GitHub Pages Setup

This portal is designed to be hosted on GitHub Pages. To set it up:

1. **Push this repository to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: ISB Dataset Portal"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Navigate to **Settings** → **Pages**
   - Under **Source**, select **Deploy from a branch**
   - Choose **main** branch and **/ (root)** folder
   - Click **Save**

3. **Access your site**
   - Your site will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`
   - It may take a few minutes for the site to be available after enabling Pages

## Local Development

To view the portal locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. Open `index.html` in a web browser, or use a local server:
   ```bash
   # Using Python 3
   python3 -m http.server 8000
   
   # Using Python 2
   python -m SimpleHTTPServer 8000
   
   # Using Node.js (if you have http-server installed)
   npx http-server
   ```

3. Navigate to `http://localhost:8000` in your browser

## Features

- **Clean, responsive design** using SciLifeLab visual identity
- **Repository links** automatically parsed and linked to:
  - PDB (RCSB)
  - EMDB (Electron Microscopy Data Bank)
  - EMPIAR (Electron Microscopy Public Image Archive)
  - SASBDB (Small Angle Scattering Biological Data Bank)
  - SciLifeLab Data Repository (via DOI)
  - Other repositories as available
- **Technique badges** showing which methods were used for each dataset
- **Simple navigation** between index and individual dataset pages

## Data Source

The datasets are sourced from the ISB multi-technique inventory CSV file. Each dataset entry includes:
- Unit/Facility information
- System/target description
- Organism/source
- Techniques used
- Public repository links and IDs
- Data collection years
- Access/reuse status

## Notes

- The `.nojekyll` file is included to prevent GitHub Pages from processing the site with Jekyll (not needed for static HTML)
- All paths are relative, making the site portable and GitHub Pages compatible
- The portal excludes "Internal notes" as they are marked as "not public"

## License

This portal is part of SciLifeLab's ISB initiative. Please refer to SciLifeLab's policies for usage and attribution.

## Contact

For questions or suggestions about this portal, please contact the SciLifeLab ISB team.

