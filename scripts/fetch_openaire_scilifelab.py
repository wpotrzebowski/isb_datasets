#!/usr/bin/env python3
"""
Fetch SciLifeLab community datasets from the OpenAIRE Graph API, filter to
structural-biology–relevant records, and optionally add draft ISB-AP JSON +
Markdown under datasets/.

API reference: https://scilifelab.openaire.eu/data-and-api
Graph docs: https://graph.openaire.eu/docs/
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
INDEX_JSON = DATASETS_DIR / "index.json"
KEYWORDS_DEFAULT = SCRIPT_DIR / "openaire_structural_keywords.txt"
STATE_FILE = SCRIPT_DIR / "openaire_sync_state.json"
LOG_FILE = SCRIPT_DIR / "openaire_sync.log"

GRAPH_API = "https://api.openaire.eu/graph/v2/researchProducts"

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"\'<>]+)", re.I)

# Prefer Swedish / SciLifeLab-affiliated organization labels when present.
_SWEDISH_HINTS = (
    "sweden",
    "scilifelab",
    "uppsala",
    "stockholm",
    "stockholms",
    "lund ",
    "lund university",
    "umeå",
    "umea",
    "karolinska",
    "kth",
    "chalmers",
    "gothenburg",
    "göteborg",
    "linköping",
    "örebro",
    "swedish",
    "su ",
    "gu ",
    "uu ",
    "liu ",
    "slu ",
)

# OpenAIRE allows at most 4 OR operators per search string (see API 400 message).
DEFAULT_SEARCH_QUERIES = [
    "cryo-EM OR cryo EM OR EMDB OR tomography OR subtomogram",
    "SAXS OR SASBDB OR NMR OR BMRB OR HDX",
    "SANS OR SASBDB OR scattering OR neutron",
    "PDB OR AlphaFold OR structural biology OR integrative",
    "XL-MS OR cross-linking OR multimodal OR crystallography",
]

TECH_RULES: List[Tuple[List[str], Tuple[str, str]]] = [
    (["cryo-em", "cryo em", "cryoem", "cryo electron", "single particle", "emdb", "subtomogram"], ("cryo_em", "Cryo-EM")),
    (["x-ray", "xray", "crystallography", "diffraction", "xfel", "pdb ", " pdb"], ("xray_crystallography", "X-ray crystallography")),
    (["saxs", "sasbdb"], ("saxs", "SAXS")),
    (["sans", "small angle neutron"], ("sans", "SANS")),
    (["nmr", "bmrb"], ("nmr", "NMR")),
    (["hdx", "hydrogen deuterium"], ("ms_proteomics", "MS / Proteomics")),
    (["xl-ms", "xl ms", "cross-linking ms", "crosslinking"], ("xl_ms", "Cross-linking MS (XL-MS)")),
    (["proteomics", "mass spectrometry"], ("ms_proteomics", "MS / Proteomics")),
    (["maldi", "msi"], ("maldi_msi", "MALDI-MSI")),
    (["spatial transcriptomics", "visium"], ("spatial_transcriptomics", "Spatial Transcriptomics")),
    (["itc", "spr", "mst", "dsf", "biophysics"], ("biophysics", "Biophysics (ITC/SPR/MST/DSF etc.)")),
    (["molecular dynamics", "all-atom", "gromacs", "amber", "namd"], ("md_simulation", "MD / other simulations")),
    (["alphafold", "rosetta", "haddock", "integrative model", "computational model"], ("integrative_modelling", "Integrative / computational modelling (non-MD)")),
    (["bioinformatic", "integration", "pipeline"], ("bioinformatics_integration", "Bioinformatics / Data Integration")),
]


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
    )


def load_keywords(path: Path) -> List[str]:
    lines: List[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            lines.append(s)
    return lines


def normalize_doi(raw: str) -> Optional[str]:
    if not raw:
        return None
    s = raw.strip().lower()
    s = s.replace("https://doi.org/", "").replace("http://doi.org/", "").replace("http://dx.doi.org/", "")
    s = s.split("?", 1)[0].strip().rstrip(").,;]")
    m = DOI_RE.search(s)
    return m.group(1).lower() if m else None


def extract_dois_from_text(text: str) -> Set[str]:
    out: Set[str] = set()
    for m in DOI_RE.finditer(text or ""):
        out.add(m.group(1).lower())
    return out


def extract_primary_doi(hit: Dict[str, Any]) -> Optional[str]:
    """Prefer dataset DOI from instances (alternateIdentifiers)."""
    instances = hit.get("instances") or []
    for inst in instances:
        for aid in inst.get("alternateIdentifiers") or []:
            if (aid.get("scheme") or "").lower() == "doi":
                d = normalize_doi(aid.get("value") or "")
                if d:
                    return d
        for url in inst.get("urls") or []:
            d = normalize_doi(url)
            if d:
                return d
    pids = hit.get("pids") or []
    for p in pids:
        if (p.get("scheme") or "").lower() in ("doi", "hdl"):
            d = normalize_doi(p.get("value") or "")
            if d:
                return d
    return None


def hit_text_blob(hit: Dict[str, Any]) -> str:
    parts: List[str] = []
    parts.append(hit.get("mainTitle") or "")
    parts.append(hit.get("subTitle") or "")
    for d in hit.get("descriptions") or []:
        parts.append(str(d))
    for sub in hit.get("subjects") or []:
        subj = sub.get("subject") or {}
        parts.append(subj.get("value") or "")
    return "\n".join(parts)


def keyword_score(blob: str, keywords: List[str]) -> int:
    lower = blob.lower()
    n = 0
    for kw in keywords:
        if kw.lower() in lower:
            n += 1
    return n


def infer_techniques(blob: str) -> List[Dict[str, str]]:
    lower = blob.lower()
    seen: Set[str] = set()
    out: List[Dict[str, str]] = []
    for tokens, (code, label) in TECH_RULES:
        if any(t in lower for t in tokens):
            if code not in seen:
                seen.add(code)
                out.append({"code": code, "label": label})
    if not out:
        out.append({"code": "integrative_modelling", "label": "Integrative / computational modelling (non-MD)"})
    return out


def pick_unit_facility(hit: Dict[str, Any]) -> str:
    orgs = hit.get("organizations") or []
    for org in orgs:
        name = (org.get("legalName") or "").lower()
        if any(h in name for h in _SWEDISH_HINTS):
            return org.get("legalName") or "Unknown"
    if orgs:
        return orgs[0].get("legalName") or "Unknown"
    return "TBD (curate from OpenAIRE record)"


def map_access_status(hit: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    bar = hit.get("bestAccessRight") or {}
    label = (bar.get("label") or "").upper()
    code = (bar.get("code") or "").lower()
    if "OPEN" in label or "open" in code:
        return "public", None
    if "embargo" in label.lower():
        return "embargoed", None
    if "restricted" in label.lower():
        return "restricted", None
    instances = hit.get("instances") or []
    for inst in instances:
        ar = inst.get("accessRight") or {}
        lab = (ar.get("label") or "").upper()
        if "OPEN" in lab:
            return "public", None
    return "public", None


def infer_repository_kind(url: str, hosted_by: str) -> str:
    u = url.lower()
    h = hosted_by.lower()
    if "zenodo" in u or "zenodo" in h:
        return "Zenodo"
    if "figshare" in u or "figshare" in h:
        return "Figshare"
    if "10.17044" in u or "scilifelab" in u or "figshare.scilifelab" in u:
        return "SciLifeLab Data Repository"
    if "ebi.ac.uk" in u or "ena" in h:
        return "ENA / EBI"
    return hosted_by or "Repository"


def build_repository_records(hit: Dict[str, Any], doi: Optional[str]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    instances = hit.get("instances") or []
    for inst in instances:
        hosted = (inst.get("hostedBy") or {}).get("value") or ""
        lic = inst.get("license")
        for aid in inst.get("alternateIdentifiers") or []:
            if (aid.get("scheme") or "").lower() == "doi":
                d = normalize_doi(aid.get("value") or "")
                if d:
                    url = f"https://doi.org/{d}"
                    kind = infer_repository_kind(url, hosted)
                    rec: Dict[str, Any] = {
                        "kind": kind,
                        "doi": d,
                        "url": url,
                        "relation": "primary_dataset",
                    }
                    if lic:
                        rec["note"] = f"License (instance): {lic}"
                    records.append(rec)
        for url in inst.get("urls") or []:
            if url and url not in [r.get("url") for r in records]:
                kind = infer_repository_kind(url, hosted)
                records.append({"kind": kind, "url": url, "relation": "landing_page"})
    if doi and not any(r.get("doi") == doi for r in records):
        records.insert(
            0,
            {
                "kind": "Dataset",
                "doi": doi,
                "url": f"https://doi.org/{doi}",
                "relation": "primary_dataset",
            },
        )
    return records[:12]


def portal_base_url(index_path: Path) -> str:
    with open(index_path, encoding="utf-8") as f:
        idx = json.load(f)
    raw = (idx.get("source") or {}).get("portal_url") or "https://example.github.io/isb_datasets/index.html"
    # https://host/path/index.html -> https://host/path
    if raw.endswith("/index.html"):
        return raw[: -len("/index.html")]
    return str(Path(raw).parent)


def load_controlled_technique_labels(index_path: Path) -> Dict[str, str]:
    with open(index_path, encoding="utf-8") as f:
        idx = json.load(f)
    cv = (idx.get("controlled_vocabularies") or {}).get("techniques") or []
    return {x["code"]: x["label"] for x in cv if isinstance(x, dict) and "code" in x}


def refine_techniques(
    inferred: List[Dict[str, str]], code_to_label: Dict[str, str]
) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for t in inferred:
        code = t["code"]
        label = code_to_label.get(code, t["label"])
        out.append({"code": code, "label": label})
    return out


def collect_existing_dois(datasets_dir: Path) -> Set[str]:
    dois: Set[str] = set()
    for path in sorted(datasets_dir.glob("ISB-D-*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for rec in data.get("repository_records") or []:
            for key in ("doi", "url", "accession"):
                val = rec.get(key)
                if isinstance(val, str):
                    dois.update(extract_dois_from_text(val))
                    d = normalize_doi(val)
                    if d:
                        dois.add(d)
        for pub in data.get("publications") or []:
            for key in ("doi", "url"):
                val = pub.get(key)
                if isinstance(val, str):
                    dois.update(extract_dois_from_text(val))
    return dois


def max_dataset_md_number(datasets_dir: Path) -> int:
    best = 0
    for p in datasets_dir.glob("dataset-*.md"):
        m = re.match(r"dataset-(\d+)\.md$", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return best


def max_isb_numeric_id(datasets_dir: Path) -> int:
    best = 0
    for p in datasets_dir.glob("ISB-D-*.json"):
        m = re.match(r"ISB-D-(\d+)\.json$", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return best


def max_portal_index_disk(datasets_dir: Path) -> int:
    best = 0
    for p in datasets_dir.glob("ISB-D-*.json"):
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            pi = data.get("portal_index")
            if isinstance(pi, int):
                best = max(best, pi)
        except (json.JSONDecodeError, OSError):
            continue
    return best


def max_portal_index_index_json(index_path: Path) -> int:
    if not index_path.exists():
        return 0
    with open(index_path, encoding="utf-8") as f:
        idx = json.load(f)
    best = 0
    for d in idx.get("datasets") or []:
        pi = d.get("portal_index")
        if isinstance(pi, int):
            best = max(best, pi)
    return best


def fetch_search_pages(
    session: requests.Session,
    search_query: str,
    from_publication_date: Optional[str],
    page_size: int,
    sleep_s: float,
    max_pages: int,
) -> List[Dict[str, Any]]:
    """Cursor-based pagination for one search string."""
    results: List[Dict[str, Any]] = []
    cursor: Optional[str] = "*"
    pages = 0
    while cursor and pages < max_pages:
        params: Dict[str, Any] = {
            "relCommunityId": "scilifelab",
            "type": "dataset",
            "pageSize": min(100, page_size),
            "sortBy": "publicationDate DESC",
            "search": search_query,
            "cursor": cursor,
        }
        if from_publication_date:
            params["fromPublicationDate"] = from_publication_date
        r = session.get(GRAPH_API, params=params, timeout=120)
        r.raise_for_status()
        payload = r.json()
        header = payload.get("header") or {}
        batch = payload.get("results") or []
        results.extend(batch)
        pages += 1
        next_c = header.get("nextCursor")
        cursor = next_c if next_c else None
        time.sleep(sleep_s)
    return results


def merge_hits_by_id(hits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for h in hits:
        oid = h.get("id")
        if oid:
            by_id[oid] = h
    return by_id


def load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def render_stub_markdown(
    *,
    title: str,
    json_file: str,
    unit_facility: str,
    techniques_labels: List[str],
    repo_url: Optional[str],
    access_status: str,
    main_repository: str,
) -> str:
    repos_yaml = ""
    if repo_url:
        repos_yaml = f"""repositories:
  - type: "OpenAIRE"
    links:
      - url: "{repo_url}"
        text: "Dataset landing page"
"""
    else:
        repos_yaml = "repositories: []\n"
    tech_lines = "\n".join(f'  - "{t}"' for t in techniques_labels) if techniques_labels else '  - "TBD"'
    return f"""---
title: "{title.replace('"', '\\"')}"
json_file: "{json_file}"
unit_facility: "{unit_facility.replace('"', '\\"')}"
system_target: "TBD — curate (from OpenAIRE / publication)."
organism_source: "TBD"
data_collection_years: "TBD"
access_status: "{access_status}"
main_repository: "{main_repository.replace('"', '\\"')}"
techniques:
{tech_lines}
{repos_yaml}---

Draft from OpenAIRE (SciLifeLab community). Please curate system/target, organism, repository details, and index card text.
"""


def build_isb_record(
    hit: Dict[str, Any],
    *,
    isb_id: str,
    portal_index: int,
    portal_landing_page_url: str,
    code_to_label: Dict[str, str],
    now_iso: str,
) -> Dict[str, Any]:
    title = (hit.get("mainTitle") or "Untitled dataset").strip()
    desc_parts = hit.get("descriptions") or []
    portal_description = (str(desc_parts[0]) if desc_parts else title)[:500]
    blob = hit_text_blob(hit)
    status, lic = map_access_status(hit)
    access_obj: Dict[str, Any] = {"status": status, "license": None, "license_url": None}
    instances = hit.get("instances") or []
    if instances:
        lic = instances[0].get("license")
        if lic:
            access_obj["license"] = str(lic)
    doi = extract_primary_doi(hit)
    hosted = (instances[0].get("hostedBy") or {}).get("value") if instances else ""
    main_repo = ", ".join(filter(None, [hit.get("publisher"), hosted])) or "See repository links"

    inferred = infer_techniques(blob)
    techniques = refine_techniques(inferred, code_to_label)
    tech_labels = [t["label"] for t in techniques]

    keywords_set: Set[str] = set()
    for sub in hit.get("subjects") or []:
        v = (sub.get("subject") or {}).get("value")
        if v:
            keywords_set.add(str(v)[:200])
    for tok in tech_labels:
        keywords_set.add(tok)
    keywords = sorted(keywords_set)[:25]

    record: Dict[str, Any] = {
        "id": isb_id,
        "portal_index": portal_index,
        "title": title,
        "portal_description": portal_description,
        "portal_landing_page_url": portal_landing_page_url,
        "unit_facility": pick_unit_facility(hit),
        "system_target": portal_description[:400] if portal_description else "TBD",
        "organism_source": "TBD",
        "approx_data_collection_years": "TBD",
        "access": access_obj,
        "main_public_repository_storage": main_repo,
        "techniques": techniques,
        "repository_records": build_repository_records(hit, doi),
        "publications": [],
        "keywords": keywords,
        "provenance": {
            "openaire_graph_id": hit.get("id"),
            "synced_at": now_iso,
            "publisher": hit.get("publisher"),
        },
    }
    return record


def run_sync(args: argparse.Namespace) -> int:
    setup_logging()
    keywords_path = Path(args.keywords_file)
    keywords = load_keywords(keywords_path)
    if not keywords:
        logging.error("No keywords loaded from %s", keywords_path)
        return 1

    code_to_label = load_controlled_technique_labels(INDEX_JSON)
    existing_dois = collect_existing_dois(DATASETS_DIR)
    logging.info("Loaded %s existing DOIs from ISB-D-*.json", len(existing_dois))

    session = requests.Session()
    session.headers["accept"] = "application/json"

    all_hits: Dict[str, Dict[str, Any]] = {}
    for sq in args.search_queries:
        logging.info("Fetching search: %s", sq[:80] + ("..." if len(sq) > 80 else ""))
        chunk = fetch_search_pages(
            session,
            sq,
            args.from_publication_date,
            args.page_size,
            args.sleep,
            args.max_pages_per_query,
        )
        merged = merge_hits_by_id(chunk)
        all_hits.update(merged)
        logging.info("  ... accumulated unique ids: %s", len(all_hits))

    min_kw = max(1, args.min_keyword_matches)
    filtered: List[Dict[str, Any]] = []
    for hit in all_hits.values():
        blob = hit_text_blob(hit)
        if keyword_score(blob, keywords) < min_kw:
            continue
        filtered.append(hit)

    logging.info("After structural keyword filter: %s records", len(filtered))

    skipped_no_doi: List[str] = []
    skipped_existing_doi: List[str] = []
    duplicate_report: List[Tuple[str, str]] = []
    candidates: List[Dict[str, Any]] = []
    for hit in filtered:
        doi = extract_primary_doi(hit)
        blob_id = hit.get("id") or ""
        if not doi:
            skipped_no_doi.append(blob_id)
            continue
        if doi in existing_dois:
            skipped_existing_doi.append(doi)
            if args.include_duplicate_report:
                duplicate_report.append((doi, hit.get("mainTitle") or ""))
            continue
        candidates.append(hit)

    logging.info("New candidates (new DOI): %s", len(candidates))
    if args.max_new is not None:
        candidates = candidates[: args.max_new]
        logging.info("After --max-new cap: %s", len(candidates))

    base = portal_base_url(INDEX_JSON)
    now_iso = datetime.now(timezone.utc).isoformat()

    next_isb = max_isb_numeric_id(DATASETS_DIR) + 1
    next_md = max_dataset_md_number(DATASETS_DIR) + 1
    next_portal = max(max_portal_index_disk(DATASETS_DIR), max_portal_index_index_json(INDEX_JSON)) + 1

    planned: List[Tuple[Dict[str, Any], str, str, int, int]] = []
    for hit in candidates:
        isb_num = next_isb
        md_num = next_md
        pi = next_portal
        isb_id = f"ISB-D-{isb_num:04d}"
        md_name = f"dataset-{md_num}.md"
        landing = f"{base}/datasets/dataset-{md_num}.html"
        planned.append((hit, isb_id, md_name, md_num, pi))
        next_isb += 1
        next_md += 1
        next_portal += 1

    print("\n--- OpenAIRE sync summary ---")
    print(f"Unique API hits (union of searches): {len(all_hits)}")
    print(f"After keyword filter: {len(filtered)}")
    print(f"Skipped (no DOI): {len(skipped_no_doi)}")
    print(f"Skipped (DOI already in portal): {len(skipped_existing_doi)}")
    print(f"Planned new datasets: {len(planned)}")

    for hit, isb_id, md_name, md_num, pi in planned:
        doi = extract_primary_doi(hit) or ""
        print(f"  - {isb_id} / {md_name}  DOI {doi}")
        print(f"    {hit.get('mainTitle', '')[:100]}...")

    if args.include_duplicate_report and duplicate_report:
        print("\nDuplicates (existing portal DOI matched OpenAIRE):")
        for doi, title in duplicate_report[:50]:
            print(f"  {doi}  {title[:80]}")
        if len(duplicate_report) > 50:
            print(f"  ... and {len(duplicate_report) - 50} more")

    if not args.apply:
        print("\nDry run — no files written. Pass --apply to create datasets.")
        state = load_state()
        state["last_check"] = now_iso
        state["last_dry_run_new_count"] = len(planned)
        save_state(state)
        return 0

    # --apply
    new_index_entries: List[Dict[str, Any]] = []
    for hit, isb_id, md_name, md_num, pi in planned:
        landing = f"{base}/datasets/dataset-{md_num}.html"
        record = build_isb_record(
            hit,
            isb_id=isb_id,
            portal_index=pi,
            portal_landing_page_url=landing,
            code_to_label=code_to_label,
            now_iso=now_iso,
        )
        json_name = f"{isb_id}.json"
        json_path = DATASETS_DIR / json_name
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logging.info("Wrote %s", json_path)

        doi = extract_primary_doi(hit)
        repo_url = f"https://doi.org/{doi}" if doi else None
        acc_label = "Public" if record["access"]["status"] == "public" else record["access"]["status"].title()
        md_body = render_stub_markdown(
            title=record["title"],
            json_file=json_name,
            unit_facility=record["unit_facility"],
            techniques_labels=[t["label"] for t in record["techniques"]],
            repo_url=repo_url,
            access_status=acc_label,
            main_repository=record["main_public_repository_storage"],
        )
        md_path = DATASETS_DIR / md_name
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_body)
        logging.info("Wrote %s", md_path)

        new_index_entries.append({"id": isb_id, "portal_index": pi, "file": json_name})

    if new_index_entries:
        with open(INDEX_JSON, encoding="utf-8") as f:
            index_data = json.load(f)
        index_data["schema"]["generated_at"] = now_iso
        index_data.setdefault("datasets", [])
        index_data["datasets"].extend(new_index_entries)
        with open(INDEX_JSON, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logging.info("Updated %s with %s entries", INDEX_JSON, len(new_index_entries))

    state = load_state()
    state["last_apply"] = now_iso
    state["last_new_count"] = len(planned)
    save_state(state)
    print(f"\nApplied {len(planned)} new dataset(s). Update index.html manually; run python scripts/build.py to regenerate HTML.")
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sync SciLifeLab OpenAIRE datasets into ISB-AP JSON + Markdown drafts.")
    p.add_argument(
        "--apply",
        action="store_true",
        help="Write ISB-D-*.json, dataset-*.md, and append datasets/index.json (default is dry-run).",
    )
    p.add_argument("--max-new", type=int, default=None, help="Maximum number of new datasets to add this run.")
    p.add_argument("--keywords-file", type=str, default=str(KEYWORDS_DEFAULT), help="Path to keyword list file.")
    p.add_argument("--min-keyword-matches", type=int, default=1, help="Minimum keyword substring matches required.")
    p.add_argument("--sleep", type=float, default=0.4, help="Seconds between API pages.")
    p.add_argument("--page-size", type=int, default=100, help="Graph API page size (max 100).")
    p.add_argument("--max-pages-per-query", type=int, default=25, help="Safety cap on cursor pages per search query.")
    p.add_argument("--from-publication-date", type=str, default=None, help="YYYY-MM-DD lower bound (optional).")
    p.add_argument(
        "--search-query",
        action="append",
        dest="search_queries",
        default=None,
        help="Extra OpenAIRE search string (repeatable). Defaults to built-in OR-query set.",
    )
    p.add_argument(
        "--include-duplicate-report",
        action="store_true",
        help="Print OpenAIRE titles for DOIs that already exist in the portal.",
    )
    return p


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    if not args.search_queries:
        args.search_queries = DEFAULT_SEARCH_QUERIES
    sys.exit(run_sync(args))


if __name__ == "__main__":
    main()
