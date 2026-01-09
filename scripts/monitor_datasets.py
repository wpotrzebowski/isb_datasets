#!/usr/bin/env python3
"""
Monitor various repositories for new multimodal structural biology datasets
from SciLifeLab's Integrated Structural Biology platform.

This script checks:
- SciLifeLab Data Repository (Figshare API)
- EMDB (Electron Microscopy Data Bank)
- SASBDB (Small Angle Scattering Biological Data Bank)
- PDB-Dev (for integrative structures)
- PRIDE (for HDX-MS/XL-MS datasets)
- BMRB (for NMR datasets)

Run periodically (e.g., weekly) to discover new datasets.
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
STATE_FILE = SCRIPT_DIR / "monitor_state.json"
OUTPUT_FILE = SCRIPT_DIR / "new_datasets.json"

# Swedish institutions and keywords to search for
SWEDISH_KEYWORDS = [
    "Sweden", "Swedish", "SciLifeLab", "SciLifeLab", "Stockholm", "Uppsala",
    "Gothenburg", "Lund", "Umeå", "Karolinska", "KTH", "SU", "Stockholm University",
    "Uppsala University", "University of Gothenburg", "Lund University", "Umeå University"
]

ISB_TECHNIQUES = [
    "cryo-EM", "cryoEM", "cryo electron microscopy", "electron microscopy",
    "NMR", "nuclear magnetic resonance", "SAXS", "SANS", "small angle scattering",
    "HDX-MS", "hydrogen deuterium exchange", "XL-MS", "cross-linking",
    "structural proteomics", "integrative", "multimodal"
]


def load_state() -> Dict:
    """Load the last check timestamp from state file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_check": None,
        "known_datasets": []
    }


def save_state(state: Dict):
    """Save the current state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def check_scilifelab_figshare(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check SciLifeLab Figshare repository for new structural biology datasets.
    
    Note: Figshare API requires authentication for full access. This is a basic check.
    """
    results = []
    try:
        # Figshare API endpoint for SciLifeLab institution
        # Note: This is a simplified check - full API access may require authentication
        base_url = "https://api.figshare.com/v2"
        
        # Search for articles with structural biology keywords
        search_params = {
            "search_for": "structural biology OR cryo-EM OR NMR OR SAXS",
            "institution": "SciLifeLab",
            "page_size": 20
        }
        
        # This is a placeholder - actual implementation would need proper API access
        # For now, we'll document the approach
        print("  [Figshare] Note: Full API access requires authentication")
        print("  [Figshare] Check manually at: https://figshare.scilifelab.se/")
        
    except Exception as e:
        print(f"  [Figshare] Error: {e}")
    
    return results


def check_emdb(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check EMDB for new entries from Swedish institutions.
    Uses EMDB REST API.
    """
    results = []
    try:
        # EMDB REST API
        base_url = "https://www.ebi.ac.uk/emdb/api"
        
        # Get recent entries (last 30 days if since_date not provided)
        if since_date is None:
            since_date = datetime.now() - timedelta(days=30)
        
        # EMDB API endpoint for searching
        search_url = f"{base_url}/search"
        
        # Search for entries with Swedish affiliations
        # Note: EMDB API structure may vary - this is a template
        params = {
            "query": "Sweden OR Swedish OR SciLifeLab OR Stockholm OR Uppsala",
            "limit": 50
        }
        
        response = requests.get(search_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Process results based on EMDB API structure
            print(f"  [EMDB] Found {len(data.get('results', []))} potential entries")
        else:
            print(f"  [EMDB] API returned status {response.status_code}")
            print(f"  [EMDB] Check manually at: https://www.ebi.ac.uk/emdb/")
            
    except Exception as e:
        print(f"  [EMDB] Error: {e}")
        print(f"  [EMDB] Check manually at: https://www.ebi.ac.uk/emdb/")
    
    return results


def check_sasbdb(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check SASBDB for new SAXS/SANS entries from Swedish institutions.
    """
    results = []
    try:
        # SASBDB doesn't have a public API, but we can check their website
        # or use web scraping (with proper rate limiting)
        print("  [SASBDB] No public API available")
        print("  [SASBDB] Check manually at: https://www.sasbdb.org/")
        print("  [SASBDB] Search for: Sweden OR Swedish OR SciLifeLab")
        
    except Exception as e:
        print(f"  [SASBDB] Error: {e}")
    
    return results


def check_pdb_dev(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check PDB-Dev for new integrative structures.
    """
    results = []
    try:
        # PDB-Dev API endpoint
        base_url = "https://pdb-dev.wwpdb.org"
        
        # Search for integrative structures
        print("  [PDB-Dev] Check manually at: https://pdb-dev.wwpdb.org/")
        print("  [PDB-Dev] Look for integrative structures with Swedish authors")
        
    except Exception as e:
        print(f"  [PDB-Dev] Error: {e}")
    
    return results


def check_pride(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check PRIDE for HDX-MS and XL-MS datasets from Swedish institutions.
    """
    results = []
    try:
        # PRIDE API endpoint
        base_url = "https://www.ebi.ac.uk/pride/archive"
        
        # Search for HDX-MS or XL-MS datasets
        search_url = f"{base_url}/api/v2/projects"
        
        # Search parameters
        params = {
            "keywords": "HDX OR cross-linking OR XL-MS",
            "pageSize": 20
        }
        
        response = requests.get(search_url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Filter for Swedish affiliations
            print(f"  [PRIDE] Found {len(data.get('_embedded', {}).get('projects', []))} potential entries")
            print(f"  [PRIDE] Check manually at: https://www.ebi.ac.uk/pride/archive")
        else:
            print(f"  [PRIDE] API returned status {response.status_code}")
            print(f"  [PRIDE] Check manually at: https://www.ebi.ac.uk/pride/archive")
            
    except Exception as e:
        print(f"  [PRIDE] Error: {e}")
        print(f"  [PRIDE] Check manually at: https://www.ebi.ac.uk/pride/archive")
    
    return results


def check_bmrb(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check BMRB for NMR datasets from Swedish institutions.
    """
    results = []
    try:
        # BMRB doesn't have a comprehensive public API
        print("  [BMRB] No public API available")
        print("  [BMRB] Check manually at: https://bmrb.io/")
        print("  [BMRB] Search for: Sweden OR Swedish OR SciLifeLab")
        
    except Exception as e:
        print(f"  [BMRB] Error: {e}")
    
    return results


def check_rcsb_pdb(since_date: Optional[datetime] = None) -> List[Dict]:
    """
    Check RCSB PDB for structures with Swedish authors and multimodal data.
    """
    results = []
    try:
        # RCSB PDB REST API
        base_url = "https://search.rcsb.org/rcsbsearch/v2/query"
        
        # Search for structures with Swedish affiliations
        # This is a complex query - simplified version
        query = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {
                    "attribute": "rcsb_entry_info.structure_determination_methodology",
                    "operator": "contains_words",
                    "value": "electron microscopy OR NMR OR solution scattering"
                }
            },
            "return_type": "entry"
        }
        
        response = requests.post(base_url, json=query, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"  [RCSB PDB] Found {len(data.get('result_set', []))} potential entries")
            print(f"  [RCSB PDB] Filter manually for Swedish affiliations")
        else:
            print(f"  [RCSB PDB] API returned status {response.status_code}")
            print(f"  [RCSB PDB] Check manually at: https://www.rcsb.org/")
            
    except Exception as e:
        print(f"  [RCSB PDB] Error: {e}")
        print(f"  [RCSB PDB] Check manually at: https://www.rcsb.org/")
    
    return results


def main():
    """Main monitoring function."""
    print("=" * 60)
    print("ISB Dataset Monitoring System")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}\n")
    
    state = load_state()
    last_check = None
    if state.get("last_check"):
        try:
            last_check = datetime.fromisoformat(state["last_check"])
        except:
            pass
    
    if last_check:
        print(f"Last check: {last_check.isoformat()}")
    else:
        print("First run - checking last 30 days")
        last_check = datetime.now() - timedelta(days=30)
    
    print("\nChecking repositories...\n")
    
    all_results = []
    
    # Check each repository
    print("1. SciLifeLab Data Repository (Figshare)")
    results = check_scilifelab_figshare(last_check)
    all_results.extend(results)
    time.sleep(1)  # Rate limiting
    
    print("\n2. EMDB (Electron Microscopy Data Bank)")
    results = check_emdb(last_check)
    all_results.extend(results)
    time.sleep(1)
    
    print("\n3. SASBDB (Small Angle Scattering Biological Data Bank)")
    results = check_sasbdb(last_check)
    all_results.extend(results)
    time.sleep(1)
    
    print("\n4. PDB-Dev (Integrative Structures)")
    results = check_pdb_dev(last_check)
    all_results.extend(results)
    time.sleep(1)
    
    print("\n5. PRIDE (Proteomics)")
    results = check_pride(last_check)
    all_results.extend(results)
    time.sleep(1)
    
    print("\n6. BMRB (NMR)")
    results = check_bmrb(last_check)
    all_results.extend(results)
    time.sleep(1)
    
    print("\n7. RCSB PDB")
    results = check_rcsb_pdb(last_check)
    all_results.extend(results)
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    # Save results
    if all_results:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({
                "check_date": datetime.now().isoformat(),
                "results": all_results
            }, f, indent=2)
        print(f"\n✓ Found {len(all_results)} potential new datasets")
        print(f"  Results saved to: {OUTPUT_FILE}")
    else:
        print("\n✓ No new datasets found (or manual checks required)")
    
    print("\n" + "=" * 60)
    print("Monitoring complete!")
    print("=" * 60)
    print("\nNote: Many repositories require manual checking or API authentication.")
    print("See MONITORING.md for detailed instructions on manual checks.")


if __name__ == "__main__":
    main()

