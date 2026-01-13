# Dataset JSON Files

This directory contains individual JSON files for each dataset in the ISB Dataset Portal.

## Structure

- **index.json** - Main index file containing schema, source information, controlled vocabularies, mapping rules, and a list of all datasets with references to their individual files
- **ISB-D-XXXX.json** - Individual dataset files, one per dataset

## Individual Dataset Files

Each dataset has its own JSON file named by its ID (e.g., `ISB-D-0001.json`). These files contain the complete metadata for a single dataset, including:

- Basic information (title, description, portal links)
- Unit/facility and system information
- Access and licensing information
- Techniques used
- Repository records
- Publications
- Keywords

## Usage

To load a specific dataset:
```python
import json

with open('datasets/ISB-D-0001.json', 'r') as f:
    dataset = json.load(f)
```

To load the index and iterate through all datasets:
```python
import json
import os

with open('datasets/index.json', 'r') as f:
    index = json.load(f)

for dataset_ref in index['datasets']:
    dataset_file = os.path.join('datasets', dataset_ref['file'])
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)
        # Process dataset...
```

## Main datasets.json

The main `datasets.json` file in the scripts directory (`scripts/datasets.json`) contains the complete combined dataset collection for backward compatibility. The individual JSON files in this directory (`datasets/`) are co-located with the Markdown and HTML files for easier access and are linked from each dataset webpage.

