# HR Offer Agent and Three-Role Intelligent Interview System

## Overview

This project provides a production-ready three-role intelligent interview workflow (Tech/HR/Boss) and an HR Offer Agent. It automates interviews, scoring, candidate profile extraction, result archiving, and offer generation. It also includes an MCP server to integrate external market salary data (Adzuna).

## Project Structure

```
agent_training/
├── agents/                          # Agent modules
│   ├── __init__.py
│   ├── hr_offer_agent.py           # HR Offer generator agent
│   ├── technical_interviewer.py    # Technical interviewer
│   ├── hr_interviewer.py           # HR interviewer
│   ├── boss_interviewer.py         # Boss interviewer (Director/CTO)
│   ├── candidate_agent.py          # Candidate agent
│   ├── score_evaluator.py          # Scoring evaluator
│   └── info_extractor.py           # Information extractor
│
├── mcp_servers/                     # MCP servers
│   └── adzuna_mcp_server.py        # Adzuna API MCP server
│
├── data/                           # Data outputs
│   └── interview_results/
│       ├── 60plus/                 # Candidates with score >= 60
│       │   └── [CandidateName]/
│       │       ├── interview_results_*.json
│       │       └── offer_letter_*.txt
│       └── below60/                # Candidates with score < 60
│           └── [CandidateName]/
│               └── interview_results_*.json
│
├── docs/                           # Docs and exported images
│   └── flowchart.jpg               # Interview flowchart (if generated)
│
├── smart_interview.py              # Main entrypoint
├── smart_interview_annotated.py    # Annotated copy (optional)
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation (Chinese)
```

## Features

- Three-role interview flow: Technical → HR → Boss
- Automated scoring and recommendations: aggregate round scores and overall decision
- Candidate profile extraction: extract structured data from conversations and infer target position
- Result archiving: full dialogues, scores, and summaries saved to JSON
- Offer generation: auto-generate offer letter when score threshold is met
- Market salary integration (optional): integrate Adzuna via MCP server

## Business Workflow

Mermaid source (render in environments that support Mermaid):

```mermaid
graph TD
  A[Candidate enters pipeline] --> B[Pre-screen & role matching]
  B --> C{Matched to an open role?}
  C -->|No| Z[Talent pool / End]
  C -->|Yes| D[Schedule interviews]
  D --> E[Technical interview]
  E --> F[HR interview]
  F --> G[Boss interview]
  G --> H[Aggregate evaluation and scoring]
  H --> I{Meets offer threshold (>= 60)?}
  I -->|No| J[Reject / Talent pool]
  I -->|Pending| K[Hold: extra docs / additional round]
  I -->|Yes| L[Generate offer letter]
  L --> M[HR review and send offer]
  M --> N{Candidate accepts?}
  N -->|Yes| O[Onboarding process]
  N -->|No| P[Archive / Talent pool]
  H --> Q[Archive interview records]
```

If you need a JPG export, see the "Documentation Export" section below.

## Installation and Setup

### Python Environment

Using Conda is recommended:

```bash
conda create -n rag4 python=3.10 -y
conda activate rag4
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### API Configuration

- Adzuna API (optional):
  - App ID and App Key: obtain from Adzuna console
  - API URL: `https://api.adzuna.com/v1/api/jobs/gb/search/1`

- LLM provider keys: set via environment variables (avoid hardcoding in source):

```bash
export SILICONFLOW_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

If you prefer local `.env` loading, install `python-dotenv` and load it in your entrypoint (already integrated in `smart_interview.py`).

#### Quick setup

1) Create `.env` from the example:

```bash
cp env_example.txt .env
```

2) Edit `.env` and fill real secrets (do not commit real values):

```
# LLM providers
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Adzuna market salary data
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
ADZUNA_BASE_URL=https://api.adzuna.com/v1/api/jobs/gb/search/1
```

3) Run (the program auto-loads `.env`):

```bash
python smart_interview.py
```

4) Alternative: export environment variables directly:

```bash
export SILICONFLOW_API_KEY=your_key
export OPENAI_API_KEY=your_key
export ADZUNA_APP_ID=your_adzuna_app_id
export ADZUNA_APP_KEY=your_adzuna_app_key
python smart_interview.py
```

5) Verify loading (choose one):

```bash
python - <<'PY'
import os
print(bool(os.getenv('SILICONFLOW_API_KEY')),
      bool(os.getenv('OPENAI_API_KEY')),
      bool(os.getenv('ADZUNA_APP_ID')),
      bool(os.getenv('ADZUNA_APP_KEY')))
PY
```

#### Security notes

- Never hardcode or commit real secrets. `.env` is ignored by `.gitignore`.
- For production, inject secrets via CI/CD or a secret manager.
- Use separate secrets per environment (local/staging/prod).

## Quick Start

```bash
python smart_interview.py
```

The program will:
1. Load the default candidate profile
2. Create four agents (Technical/HR/Boss/Candidate)
3. Run three interview rounds sequentially
4. Generate scoring and summary
5. Save complete results under `data/interview_results/`
6. If overall score >= 60, generate an offer under `60plus/[CandidateName]/`

## Using the HR Offer Agent Standalone

```python
from agents.hr_offer_agent import generate_offer_letter

# interview_data should include scores and candidate profile
offer = generate_offer_letter(interview_data)
print(offer)
```

## MCP Server

Start the Adzuna MCP server (Python 3.10+ environment):

```bash
python mcp_servers/adzuna_mcp_server.py
```

Clients can query the MCP server for market salary data to support offer decisions.

## Data and Files

- Interview result JSON: `data/interview_results/[60plus|below60]/[CandidateName]/interview_results_YYYYMMDD_HHMMSS.json`
- Offer letter TXT: `data/interview_results/60plus/[CandidateName]/offer_letter_YYYYMMDD_HHMMSS.txt`

Example:

```
data/interview_results/
├── 60plus/
│   └── Alice/
│       ├── interview_results_20250820_123456.json
│       └── offer_letter_20250820_123456.txt
└── below60/
    └── Bob/
        └── interview_results_20250820_345678.json
```

## Documentation Export

To export the interview flowchart locally:
1. Save the Mermaid source as `docs/flowchart.mmd`
2. Render with `mermaid-cli` or an online service to produce PNG/SVG
3. If JPG is required, convert PNG to JPG using Pillow

## Security and Compliance

- Do not commit plaintext API keys to the repository; use environment variables or a secret manager
- Interview dialogues and candidate profiles may contain personal data; follow data minimization and retention policies
- Generated files are for internal decision-making; anonymize or redact when needed

## FAQ

- JSON scoring parse failed: the system falls back to default scoring; check output length and format
- Inaccurate candidate info extraction: key fields are protected; position inference is applied; improve the default profile if needed
- Missing Boss recommendations: ensure the first two rounds produce valid summaries

## Changelog

- v2.1.0: Candidate folder structure optimization; unified threshold bifurcation (60 points)
- v2.0.0: Project structure reorganization and path improvements
- v1.0.0: Initial release; basic interview system, Adzuna integration, MCP support

## License

MIT License.
