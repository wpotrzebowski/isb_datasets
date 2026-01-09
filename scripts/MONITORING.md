# Dataset Monitoring System

This document describes how to monitor various repositories for new multimodal structural biology datasets from SciLifeLab's Integrated Structural Biology platform.

## Automated Monitoring

Run the monitoring script:

```bash
python scripts/monitor_datasets.py
```

The script checks multiple repositories and saves results to `scripts/new_datasets.json`.

## Manual Monitoring Checklist

Since many repositories don't have public APIs or require authentication, regular manual checks are recommended:

### Weekly Checks

#### 1. SciLifeLab Data Repository (Figshare)
- **URL**: https://figshare.scilifelab.se/
- **Search**: "structural biology" OR "cryo-EM" OR "NMR" OR "SAXS" OR "multimodal"
- **Filter**: Sort by "Date published" (newest first)
- **Look for**: Datasets combining multiple techniques (Cryo-EM + SAXS, NMR + MS, etc.)

#### 2. EMDB (Electron Microscopy Data Bank)
- **URL**: https://www.ebi.ac.uk/emdb/
- **Search**: Filter by "Country: Sweden" or search for "SciLifeLab", "Stockholm", "Uppsala"
- **Look for**: Recent depositions with related SAXS/SANS or NMR data mentioned in publications

#### 3. SASBDB (Small Angle Scattering Biological Data Bank)
- **URL**: https://www.sasbdb.org/
- **Search**: Filter by author affiliation containing "Sweden" or "SciLifeLab"
- **Look for**: Entries with related Cryo-EM or NMR structures (check publication links)

#### 4. RCSB PDB
- **URL**: https://www.rcsb.org/
- **Search**: 
  - Advanced search: Author affiliation contains "Sweden" OR "SciLifeLab"
  - Filter by: Method = "ELECTRON MICROSCOPY" OR "SOLUTION NMR" OR "SOLUTION SCATTERING"
  - Sort by: Release date (newest first)
- **Look for**: Structures with multiple experimental methods listed

#### 5. PDB-Dev (Integrative Structures)
- **URL**: https://pdb-dev.wwpdb.org/
- **Search**: Browse recent entries, filter by author country
- **Look for**: Integrative structures combining Cryo-EM, NMR, SAXS, or MS data

#### 6. PRIDE (Proteomics)
- **URL**: https://www.ebi.ac.uk/pride/archive
- **Search**: 
  - Keywords: "HDX" OR "cross-linking" OR "XL-MS" OR "structural proteomics"
  - Filter by: Country = "Sweden"
- **Look for**: HDX-MS or XL-MS datasets linked to structural studies

#### 7. BMRB (Biological Magnetic Resonance Data Bank)
- **URL**: https://bmrb.io/
- **Search**: Filter by author affiliation containing "Sweden" or "SciLifeLab"
- **Look for**: NMR structures with related SAXS or Cryo-EM data

### Monthly Deep Dive

#### Check Recent Publications
1. **PubMed/Europe PMC**
   - Search: `("SciLifeLab" OR "Swedish NMR Centre" OR "Stockholm University" OR "Uppsala University") AND ("cryo-EM" OR "NMR" OR "SAXS" OR "structural biology")`
   - Filter: Last 30 days
   - Check supplementary materials for data repository links

2. **Google Scholar**
   - Search: `SciLifeLab structural biology multimodal`
   - Filter: Past month
   - Check for new publications mentioning multiple techniques

#### Check SciLifeLab News
- **URL**: https://www.scilifelab.se/news/
- Look for: Infrastructure updates, new facility capabilities, user publications

## Criteria for Adding Datasets

A dataset should be added if it meets ALL of the following:

1. **Multimodal**: Combines at least 2 different experimental/computational techniques
2. **SciLifeLab Infrastructure**: Data collected using SciLifeLab ISB platform facilities
3. **Public Access**: Data available in public repositories (PDB, EMDB, SASBDB, etc.)
4. **Repository Links**: Has persistent identifiers (DOIs, accession codes) that can be linked

### Example Multimodal Combinations:
- Cryo-EM + SAXS/SANS
- Cryo-EM + NMR
- Cryo-EM + HDX-MS or XL-MS
- NMR + SAXS
- SAXS + SANS + MD simulations
- Any combination with integrative modeling

## Adding New Datasets

When a new dataset is found:

1. **Verify it's multimodal** - Check publication/repository for multiple techniques
2. **Gather metadata**:
   - Title
   - Organism/system
   - Techniques used
   - Repository links (PDB IDs, EMDB IDs, DOIs, etc.)
   - Data collection years
   - Facility/unit
3. **Create dataset file**: `datasets/dataset-N.md` following the template
4. **Update index.html**: Add new dataset card
5. **Run build script**: `python scripts/build.py` to generate HTML

## Monitoring Schedule

- **Weekly**: Run automated script + quick manual checks of Figshare and EMDB
- **Monthly**: Deep dive into all repositories + check recent publications
- **Quarterly**: Review and update monitoring criteria

## State File

The monitoring script maintains state in `scripts/monitor_state.json`:
- `last_check`: Timestamp of last run
- `known_datasets`: List of already-discovered datasets (to avoid duplicates)

## Output File

Results are saved to `scripts/new_datasets.json`:
- `check_date`: When the check was performed
- `results`: Array of potential new datasets with metadata

## GitHub Actions (Optional)

To automate weekly checks, add a GitHub Actions workflow (`.github/workflows/monitor.yml`):

```yaml
name: Monitor Datasets

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday at midnight UTC
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install requests
      - run: python scripts/monitor_datasets.py
      - uses: actions/upload-artifact@v3
        with:
          name: monitoring-results
          path: scripts/new_datasets.json
```

## Notes

- Many repositories require manual checking due to API limitations
- Some APIs require authentication for full access
- Always verify datasets meet the multimodal criteria before adding
- Keep the monitoring state file in `.gitignore` if it contains sensitive information

