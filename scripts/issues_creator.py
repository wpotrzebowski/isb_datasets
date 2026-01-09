import os
import requests

# ============================
# CONFIGURATION
# ============================

# Set these to your repo
OWNER = "wpotrzebowski"
REPO = "isb_datasets"  # e.g. "isb_datasets"

# GitHub token with 'repo' scope
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise SystemExit("Please set GITHUB_TOKEN environment variable with a GitHub personal access token.")

BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# ============================
# MILESTONES
# ============================

milestones_data = [
    {
        "title": "2026-Q1 – Prototype & MVP foundation",
        "description": "Clean up prototype, define scope and metadata, and create a reusable system template.",
        "due_on": "2026-03-31T23:59:59Z",
    },
    {
        "title": "2026-Q2 – MVP catalogue & hosting plan",
        "description": "Populate 5–10 systems and decide short-/long-term hosting strategy.",
        "due_on": "2026-06-30T23:59:59Z",
    },
    {
        "title": "2026-Q3 – Curation & data model",
        "description": "Run internal review, curate priority systems, and draft the common data model including mmCIF exploration.",
        "due_on": "2026-09-30T23:59:59Z",
    },
    {
        "title": "2026-Q4 – Integration & sustainability",
        "description": "Map to OpenBIS/logs, define governance, and integrate with the ISB portal.",
        "due_on": "2026-12-31T23:59:59Z",
    },
]

def create_milestones():
    milestone_numbers = {}

    # Optionally fetch existing milestones to avoid duplicates
    existing = requests.get(f"{BASE_URL}/milestones", headers=HEADERS).json()
    existing_by_title = {m["title"]: m for m in existing if isinstance(m, dict) and "title" in m}

    for m in milestones_data:
        title = m["title"]
        if title in existing_by_title:
            print(f"Milestone already exists: {title}")
            milestone_numbers[title] = existing_by_title[title]["number"]
            continue

        payload = {
            "title": m["title"],
            "state": "open",
            "description": m["description"],
            "due_on": m["due_on"],
        }
        r = requests.post(f"{BASE_URL}/milestones", headers=HEADERS, json=payload)
        if r.status_code == 201:
            data = r.json()
            milestone_numbers[title] = data["number"]
            print(f"Created milestone: {title}")
        else:
            print(f"Failed to create milestone {title}: {r.status_code} {r.text}")
    return milestone_numbers

# ============================
# ISSUES
# ============================

issues_data = [
    # ---------- Q1 ----------
    {
        "title": "Clean up prototype site text and add roadmap section",
        "milestone": "2026-Q1 – Prototype & MVP foundation",
        "labels": ["documentation"],
        "body": """### Description
Polish the current prototype site so it clearly explains the purpose of the ISB multimodal dataset catalogue and where the project is heading.

### Tasks
- [ ] Rewrite intro text to be concise and goal-oriented.
- [ ] Add a short "Project objectives" section.
- [ ] Add a "Roadmap" section summarising the 2026 plan (Q1–Q4).
- [ ] Ensure links and formatting on the landing page are clean and consistent.

### Acceptance criteria
- [ ] Landing page clearly explains what the catalogue is and who it is for.
- [ ] Roadmap section visible and up to date with 2026 milestones.
- [ ] No obvious broken links or placeholder text.
""",
    },
    {
        "title": "Define scope and criteria for “truly multimodal systems”",
        "milestone": "2026-Q1 – Prototype & MVP foundation",
        "labels": ["planning", "documentation"],
        "body": """### Description
Write down what qualifies as a "truly multimodal system" for inclusion in the catalogue.

### Tasks
- [ ] Decide the minimum number/type of modalities required (e.g. ≥ 2 specified techniques).
- [ ] Specify requirements for data availability (public repos, DOIs, etc.).
- [ ] Define minimal stability requirements (e.g. not a transient test dataset).
- [ ] Document the criteria in the repo (e.g. in README or docs/scope.md).

### Acceptance criteria
- [ ] Scope and inclusion criteria are documented in a single, easy-to-find place.
- [ ] Criteria are precise enough that another person could decide if a system belongs or not.
""",
    },
    {
        "title": "Define minimal metadata schema for each multimodal system",
        "milestone": "2026-Q1 – Prototype & MVP foundation",
        "labels": ["enhancement", "documentation"],
        "body": """### Description
Design a minimal metadata schema that each system entry must follow (e.g. YAML/JSON).

### Tasks
- [ ] List required fields (e.g. system name, organism, techniques, key references, data links).
- [ ] Decide optional/advanced fields (e.g. known caveats, recommended tools).
- [ ] Choose a representation (YAML/JSON/Markdown front matter).
- [ ] Document the schema with examples.

### Acceptance criteria
- [ ] A metadata schema is documented (fields + brief description of each).
- [ ] Example system file exists that follows the schema.
""",
    },
    {
        "title": "Create system template and migrate existing entries",
        "milestone": "2026-Q1 – Prototype & MVP foundation",
        "labels": ["enhancement", "documentation"],
        "body": """### Description
Create a reusable template for system entries and migrate current systems to it.

### Tasks
- [ ] Implement a system template (e.g. Markdown + front matter or YAML file + rendered page).
- [ ] Migrate all existing systems to the new template.
- [ ] Ensure the static site correctly renders the template for each system.
- [ ] Update documentation to explain how to add a new system using the template.

### Acceptance criteria
- [ ] All existing systems follow the same template.
- [ ] Site builds successfully and displays systems consistently.
- [ ] Clear instructions exist for adding new systems.
""",
    },

    # ---------- Q2 ----------
    {
        "title": "Populate catalogue with 5–10 multimodal systems",
        "milestone": "2026-Q2 – MVP catalogue & hosting plan",
        "labels": ["enhancement", "data"],
        "body": """### Description
Fill the catalogue with an initial set of 5–10 well-documented multimodal systems.

### Tasks
- [ ] Identify candidate systems where ≥ 2 modalities are available and data is accessible.
- [ ] Create system entries using the defined template and metadata schema.
- [ ] Add links to data repositories and key publications for each system.
- [ ] Add short notes on potential analysis use-cases for each system.

### Acceptance criteria
- [ ] At least 5 systems documented, aiming for up to 10.
- [ ] Each system meets the inclusion criteria.
- [ ] All system pages render correctly on the site.
""",
    },
    {
        "title": "Decide short- and long-term hosting strategy (GitHub/Data Centre)",
        "milestone": "2026-Q2 – MVP catalogue & hosting plan",
        "labels": ["planning", "infra"],
        "body": """### Description
Make an explicit decision about current and future hosting of the catalogue.

### Tasks
- [ ] List options: personal GitHub, ISB/department GitHub org, Data Centre GitHub.
- [ ] Assess constraints (permissions, sustainability, CI, visibility).
- [ ] Decide where the repo stays for 2026 (short-term).
- [ ] Document desired long-term host (e.g. SciLifeLab Data Centre GitHub) and steps to migrate.

### Acceptance criteria
- [ ] Hosting decision (short-term) is documented in the repo.
- [ ] Long-term hosting target is written down, including a short migration plan.
""",
    },
    {
        "title": "Add project overview and initial contribution guidelines",
        "milestone": "2026-Q2 – MVP catalogue & hosting plan",
        "labels": ["documentation"],
        "body": """### Description
Provide a simple project overview and first version of contribution instructions.

### Tasks
- [ ] Add a "Project overview" section to README or docs.
- [ ] Describe what the catalogue is for (internal ISB resource, benchmarking, etc.).
- [ ] Add an initial "How to contribute a system" section (even if contributions are limited initially).
- [ ] Link to scope, criteria and template documentation.

### Acceptance criteria
- [ ] Someone unfamiliar with the project can understand its purpose from the README/docs.
- [ ] There is a clearly documented way to propose or add new systems.
""",
    },

    # ---------- Q3 ----------
    {
        "title": "Run internal ISB review of MVP catalogue",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["discussion", "planning"],
        "body": """### Description
Present the MVP catalogue internally and collect feedback and additional system suggestions.

### Tasks
- [ ] Prepare a short overview (slides or demo) of the catalogue.
- [ ] Present at an ISB/platform meeting or via email.
- [ ] Ask for candidate systems and feedback on scope/metadata.
- [ ] Capture feedback as notes or GitHub issues.

### Acceptance criteria
- [ ] At least one round of internal feedback has been collected.
- [ ] Feedback and new system ideas are recorded (issues or notes).
""",
    },
    {
        "title": "Add expert annotations to priority systems",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["enhancement", "data"],
        "body": """### Description
For a subset of high-priority systems, add deeper expert annotations.

### Tasks
- [ ] Select 2–4 priority systems to annotate first.
- [ ] Add notes on data quality, known caveats and complementary modalities.
- [ ] Document recommended analysis tools/workflows where applicable.
- [ ] Add a simple flag/badge (e.g. `curated_by_ISB: true`) to metadata.

### Acceptance criteria
- [ ] At least 2 systems marked as "curated" with richer annotations.
- [ ] Curated systems clearly identified in metadata and/or UI.
""",
    },
    {
        "title": "Draft common data model for multimodal systems",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["enhancement", "design"],
        "body": """### Description
Design a logical data model describing systems, samples, experiments, datasets and modalities.

### Tasks
- [ ] Identify key entities (system, sample, experiment, dataset, modality, reference).
- [ ] Define relationships (e.g. which datasets come from which experiments/samples).
- [ ] Create a simple diagram (e.g. PNG or Mermaid) illustrating the model.
- [ ] Document the model in docs/data_model.md.

### Acceptance criteria
- [ ] A documented data model exists with a diagram and explanations.
- [ ] Model is realistic for mapping to file-based metadata and future OpenBIS integration.
""",
    },
    {
        "title": "Evaluate mmCIF without model as base representation",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["research", "design"],
        "body": """### Description
Explore whether mmCIF (without atomic coordinates) can serve as a central representation for multimodal systems.

### Tasks
- [ ] Review mmCIF categories relevant to multimodal experiments and metadata.
- [ ] Experiment with representing one or two systems in mmCIF without coordinates.
- [ ] Identify gaps (information that cannot be captured easily).
- [ ] Document pros/cons and recommended usage pattern.

### Acceptance criteria
- [ ] Short technical note exists describing feasibility and limitations.
- [ ] Clear recommendation is made (e.g. "use mmCIF for X, keep Y in separate metadata").
""",
    },
    {
        "title": "Create pilot analysis workflow for 1–2 systems",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["enhancement", "workflow"],
        "body": """### Description
Demonstrate how the catalogue can be used in practice by creating a small analysis workflow.

### Tasks
- [ ] Select 1–2 systems with good, accessible data.
- [ ] Implement a basic workflow (e.g. Jupyter notebook, Snakemake) that reads catalogue metadata.
- [ ] Show how multiple modalities can be combined or compared in the workflow.
- [ ] Add documentation / README for running the workflow.

### Acceptance criteria
- [ ] At least one runnable example workflow is included in the repo.
- [ ] Workflow clearly uses the catalogue metadata rather than hard-coded paths.
""",
    },
    {
        "title": "Restructure repo and add basic CI/schema validation",
        "milestone": "2026-Q3 – Curation & data model",
        "labels": ["infra", "enhancement"],
        "body": """### Description
Make the repository easier to maintain by separating content and site code and adding minimal CI.

### Tasks
- [ ] Organise directories (e.g. /systems or /data for metadata, /site for website).
- [ ] Define a simple schema/validator for system metadata.
- [ ] Add CI job to build the static site.
- [ ] Add CI job to validate all metadata files against the schema.

### Acceptance criteria
- [ ] Repo structure is documented and logical.
- [ ] CI (e.g. GitHub Actions) builds the site and validates metadata on each push/PR.
""",
    },

    # ---------- Q4 ----------
    {
        "title": "Define mapping between catalogue model and OpenBIS/logs",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["design", "integration"],
        "body": """### Description
Map the common data model to OpenBIS concepts and logging systems.

### Tasks
- [ ] Map entities to OpenBIS: projects, experiments, samples, datasets.
- [ ] Identify what should be stored primarily in OpenBIS vs. in the catalogue.
- [ ] Sketch how analysis logs could be linked back to systems.
- [ ] Document mapping in docs/openbis_mapping.md.

### Acceptance criteria
- [ ] A documented conceptual mapping exists between the catalogue and OpenBIS/logs.
- [ ] Mapping is realistic enough to support manual linking or future automation.
""",
    },
    {
        "title": "Add example OpenBIS/log links for selected systems",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["integration", "enhancement"],
        "body": """### Description
For a few systems, add concrete links between the catalogue and existing OpenBIS entries/logs.

### Tasks
- [ ] Select 1–3 systems with corresponding OpenBIS projects/experiments/samples.
- [ ] Add OpenBIS identifiers/URLs to system metadata.
- [ ] If available, link relevant logs or analysis runs.
- [ ] Ensure links are clearly presented in the site UI.

### Acceptance criteria
- [ ] At least one system has working links to OpenBIS entities.
- [ ] Links are visible and understandable from the system page.
""",
    },
    {
        "title": "Write governance and contribution model",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["documentation", "planning"],
        "body": """### Description
Define how the catalogue is maintained and how contributions are handled.

### Tasks
- [ ] Decide who approves new systems and major changes (initially: you + named group, if applicable).
- [ ] Define update rhythm (e.g. review contributions twice a year).
- [ ] Create issue/PR templates for proposing new systems and changes.
- [ ] Document governance and contribution guidelines in docs/contributing.md or similar.

### Acceptance criteria
- [ ] Governance model is documented and linked from README.
- [ ] Contribution process (issues/PRs, templates) is in place.
""",
    },
    {
        "title": "Integrate catalogue into ISB portal",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["integration", "enhancement"],
        "body": """### Description
Ensure the catalogue is visible from the ISB portal (or related platforms).

### Tasks
- [ ] Identify the appropriate place in the ISB portal to link to the catalogue.
- [ ] Provide required metadata (title, short description, URL, logo if needed).
- [ ] Verify that the link appears correctly in the portal.
- [ ] Update project docs to mention that the resource is accessible via the portal.

### Acceptance criteria
- [ ] Catalogue is discoverable from the ISB portal (at least via a link).
- [ ] Docs mention the portal integration.
""",
    },
    {
        "title": "Improve user-facing documentation and examples",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["documentation"],
        "body": """### Description
Polish documentation so that ISB users can understand and start using the catalogue easily.

### Tasks
- [ ] Add a "Getting started" section for users who just want to browse systems.
- [ ] Add a "For tool developers" section explaining how to use metadata/workflows.
- [ ] Ensure example workflows are linked from the docs.
- [ ] Review and simplify wording where possible.

### Acceptance criteria
- [ ] Users can understand what the catalogue is and how to use it from the docs alone.
- [ ] Example workflows are clearly discoverable.
""",
    },
    {
        "title": "Stretch: add extra workflow or initial OpenBIS sync automation",
        "milestone": "2026-Q4 – Integration & sustainability",
        "labels": ["enhancement", "stretch-goal"],
        "body": """### Description
If time allows, extend the practical use of the catalogue.

### Possible tasks (pick 1–2)
- [ ] Add a second example workflow using a different combination of modalities.
- [ ] Prototype a small script/tool that reads metadata from OpenBIS and generates catalogue entries.
- [ ] Add optional logging hook to record analysis runs and link them back to systems.

### Acceptance criteria
- [ ] At least one stretch task completed, extending either workflows or integration.
""",
    },
]

def create_issues(milestone_numbers):
    # Fetch existing issues to avoid duplicates by title (optional but handy)
    existing_titles = set()
    page = 1
    while True:
        r = requests.get(f"{BASE_URL}/issues", headers=HEADERS, params={"state": "all", "per_page": 100, "page": page})
        data = r.json()
        if not isinstance(data, list) or not data:
            break
        for issue in data:
            if "title" in issue:
                existing_titles.add(issue["title"])
        page += 1

    for issue in issues_data:
        title = issue["title"]
        if title in existing_titles:
            print(f"Issue already exists: {title}")
            continue

        milestone_title = issue["milestone"]
        milestone_number = milestone_numbers.get(milestone_title)
        if milestone_number is None:
            print(f"Warning: milestone not found for issue '{title}': {milestone_title}")
            continue

        payload = {
            "title": title,
            "body": issue["body"],
            "milestone": milestone_number,
            "labels": issue["labels"],
        }

        r = requests.post(f"{BASE_URL}/issues", headers=HEADERS, json=payload)
        if r.status_code == 201:
            print(f"Created issue: {title}")
        else:
            print(f"Failed to create issue {title}: {r.status_code} {r.text}")

if __name__ == "__main__":
    print("Creating milestones...")
    milestone_numbers = create_milestones()
    print("Milestones:", milestone_numbers)
    print("Creating issues...")
    create_issues(milestone_numbers)
    print("Done.")

