# TruthGuard

TruthGuard is an enterprise adversarial multi-agent verification engine for question-answering over conflicting and evolving document corpora. Built for Virtusa Jatayu Season 6 under the TIME BU track (Telecom, Information, Media and Entertainment), TruthGuard systematically detects factual contradictions, enforces legal supersedence via a Temporal Knowledge Graph, and surfaces transparent dissent whenever policies clash without clear precedence.

## Project Overview

Enterprise knowledge bases naturally accumulate conflicting documents across contractual amendments, regulatory revisions, outdated standard operating procedures (SOPs), and clinical guidelines.

Conventional Retrieval-Augmented Generation (RAG) systems fail in three major ways:
1. Hallucinated Compromises: When encountering conflicting facts (such as a $5,000 penalty in a 2023 agreement versus a $25,000 penalty in a 2025 amendment), standard LLMs frequently average or fabricate an ungrounded compromise.
2. Staleness Blindness: Standard vector similarity searches retrieve both outdated and active documents without understanding version lineages, treating deprecated clauses as active policy.
3. Lack of Provenance: Standard pipelines generate synthesized text without providing an auditable justification of why one document was preferred over another.

TruthGuard solves these issues through a multi-agent dialectical pipeline that decouples retrieval, hypothesis drafting, adversarial cross-examination, and temporal DAG resolution with cryptographic provenance.

## Key Features

1. Zero Hallucination Compromises
An independent Adversarial Critic agent stresses synthesized candidate propositions, identifying factual contradictions across numbers, time windows, and operational directives to block fabricated compromises.

2. Temporal Knowledge Graph (DAG)
Tracks parent-child document relationships (amends, supersedes, invalidates) and temporal metadata (effective dates, issuing authorities) to automatically resolve policy revisions.

3. Transparent Dissent Surfacing
When simultaneous regulations clash without a hierarchical supersedence relationship (e.g., Regional 200W vs Federal 400W 5G limits), TruthGuard refuses to guess and instead surfaces both positions side-by-side with an automated compliance escalation ticket.

4. Cryptographic Provenance Ledger
Every verified claim is backed by SHA-256 fingerprint hashes, document version numbers, effective dates, and authority hierarchies, allowing one-click verification in the auditor dashboard.

5. High-Throughput Sub-50ms Pipeline
Features an in-memory hybrid search engine (BM25 Okapi and dense cosine similarity) and an optimized DAG arbiter that executes in under 5 milliseconds locally without heavy external dependencies.

6. Enterprise Auditor Dashboard
An obsidian glassmorphic interface with real-time telemetry KPIs, interactive temporal DAG visualization, document ingestion studio, automated benchmark runner, and print-ready compliance audit reporting.

## Datasets Used

TruthGuard includes a curated enterprise benchmark dataset containing intentionally contradictory document clusters across three core domains:

1. Telecom & Media (TIME BU Track)
- DOC-TIME-001: Telecom SLA Framework 2023 Base Agreement (Tier-1 Outage penalty capped at $5,000, MTTR 4 hours, issued by Global Telecom Operations).
- DOC-TIME-002: Telecom SLA Amendment 2025 Superseding Addendum (Revises penalty cap to $25,000, MTTR shortened to 1 hour, explicitly voids DOC-TIME-001 Section 4.1).
- DOC-TIME-003: Private 5G Spectrum Power Regulation Circular A (Band 78 EIRP limited to 200 Watts in suburban corridors by Regional Spectrum Authority).
- DOC-TIME-004: Federal Industrial 5G Power Directive Circular B (Band 78 power authorized up to 400 Watts on suburban campuses by Federal Communications Oversight Board; issued simultaneously with Circular A).

2. Healthcare & Life Sciences
- DOC-MED-001: Cardiovascular Clinical Guideline v2022 (Cardipril dosage recommended at 50mg to 100mg twice daily).
- DOC-MED-002: FDA Drug Safety Communication 2025 (Black Box Warning revoking previous guidelines and capping Cardipril dosage strictly at 25mg once daily).

3. Legal & IT Security
- DOC-SEC-001: Enterprise Data Retention & Archival SOP 2021 (Requires minimum 7-year storage of subscriber access logs on encrypted cold tape).
- DOC-SEC-002: Global Privacy & Log Sanitization Directive 2024 (Mandates permanent purging of subscriber logs older than 3 years to ensure GDPR Right-To-Be-Forgotten compliance).

## Architecture in a Diagramatical Representation

```
                    +------------------------------------+
                    |             User Query             |
                    +-----------------+------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|  1. RETRIEVER AGENT (Hybrid BM25 Okapi + Dense Cosine Vector Space)             |
|     - Queries in-memory dual index                                              |
|     - Binds temporal metadata (effective_date, version, authority, hash)        |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|  2. SYNTHESIZER AGENT (Hypothesis & Claim Extraction Engine)                    |
|     - Decomposes query context into discrete atomic claims                      |
|     - Maps each claim to specific source passage citations                      |
|     - Operates under strict zero-blended-compromise instructions                |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|  3. CRITIC / ADVERSARY AGENT (3-Pass Cross-Examination Loop)                    |
|     - Pass A: Pairwise NLI Contradiction Cross-Check                            |
|     - Pass B: Temporal Staleness Audit (Checks if DAG marks doc as superseded)  |
|     - Pass C: Grounding Audit (Checks unsupported or speculative assertions)    |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|  4. RESOLUTION ARBITER (Temporal Knowledge Graph & Dissent Arbiter)              |
|                                                                                 |
|     [Resolvable via Lineage]                 [Unresolvable / Simultaneous]      |
|                |                                            |                   |
|                v                                            v                   |
|  Applies Temporal Supersedence:              Surfaces Transparent Dissent:      |
|  Enforces newest valid amendment,            Presents both active policies      |
|  marks outdated clauses as voided.           side-by-side with escalation note. |
+-------------------------------------+-------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|               Audited Canonical Answer + SHA-256 Provenance Ledger              |
+---------------------------------------------------------------------------------+
```

## Repo Structure

```
TruthGuard/
├── backend/
│   ├── agents/
│   │   ├── critic_agent.py          # 3-pass adversarial contradiction and staleness checker
│   │   ├── orchestrator.py          # State machine coordinator and benchmark runner
│   │   ├── resolution_agent.py      # DAG precedence arbiter and dissent engine
│   │   ├── retriever_agent.py       # Hybrid passage retrieval and metadata binder
│   │   └── synthesizer_agent.py     # Proposition extractor and hypothesis drafter
│   ├── core/
│   │   ├── temporal_graph.py        # Directed Acyclic Graph (DAG) for version lineage
│   │   └── vector_store.py          # Hybrid Dense and BM25 sparse search engine
│   └── data/
│       └── sample_corpus.json       # Benchmark inconsistent enterprise documents
├── frontend/
│   ├── app.js                       # Real-time state visualizer, benchmark runner, and client
│   ├── index.html                   # Obsidian glassmorphic auditor dashboard UI
│   └── style.css                    # Responsive CSS design system with print stylesheet
├── tests/
│   └── test_agents.py               # Unit test suite verifying all multi-agent components
├── docs/
│   ├── ARCHITECTURE_DOCUMENT.md     # C4 architecture specifications and SOC2 compliance
│   ├── BENCHMARK_REPORT.md          # 50-case empirical evaluation report
│   ├── DEMO_PITCH_SCRIPT.md         # Presentation pitch script and jury Q&A defense
│   ├── CodeBots_Stage2_Architecture_Pitch.pptx # Technical jury pitch slide deck
│   └── assets/                      # System diagrams and visual architecture assets
├── CodeBots_TruthGuard.pptx         # Virtusa Jatayu Season 6 Stage 1 submission deck
├── server.py                        # HTTP REST API server and static asset host
├── activate_venv.bat                # Command Prompt virtual environment activator
├── activate_venv.ps1                # PowerShell virtual environment activator
├── run_truthguard.bat               # One-click launcher for Windows
├── Dockerfile                       # Production container specification
├── docker-compose.yml               # Container orchestration configuration
├── requirements.txt                 # Python dependencies
├── LICENSE                          # MIT License
└── README.md                        # Project documentation
```

## Models and Evaluation

TruthGuard was evaluated against 50 adversarial benchmark queries containing deliberate factual contradictions, superseded amendments, and simultaneous conflicting directives.

1. Evaluation Metrics
- Factual Accuracy: 100.0% on benchmark conflict suites.
- Hallucinated Compromise Rate: 0.0% (TruthGuard never outputs a fabricated middle-ground value).
- Temporal Supersedence Precision: 100.0% (All outdated clauses accurately identified and voided).
- Transparent Dissent Recall: 100.0% (Simultaneous contradictions surfaced without false consensus).
- Average End-to-End Latency: 3.6ms locally across all agents.

2. Benchmark Test Suites
- Case 01: Telecom Outage Penalty ($5,000 in 2023 vs $25,000 in 2025 amendment) -> Successfully applies temporal supersedence, voiding the 2023 clause.
- Case 02: 5G Suburban Radiated Power (200W Regional vs 400W Federal simultaneously) -> Successfully detects lack of supersedence and surfaces transparent dissent.
- Case 03: Cardipril Clinical Dosage (100mg in 2022 vs 25mg FDA 2025 black box limit) -> Successfully enforces FDA revocation and voids stale medical guideline.
- Case 04: Data Retention Mandate (7-year tape archival vs 3-year GDPR purge) -> Enforces privacy directive supersedence while preserving litigations exceptions.

## Tech Stack

- Backend Runtime: Python 3.9+ standard library (http.server, json, sqlite3, hashlib, math)
- Search Architecture: Hybrid Vector Store (BM25 Okapi ranking + dense semantic overlap)
- Graph Engine: Directed Acyclic Graph (DAG) with parent-child supersedence traversal
- Frontend Interface: Vanilla HTML5, Modern CSS3 with glassmorphism, Vanilla JavaScript
- Audio Synthesis: Web Speech API for audible canonical answer readout
- Cryptographic Auditing: SHA-256 document fingerprinting with in-browser hash verification
- Automated Testing: pytest and Python unittest test suites
- Containerization: Docker and Docker Compose

## Quickstart and Installation

1. Clone the Repository
```bash
git clone https://github.com/yasaswivenkat/TruthGuard.git
cd TruthGuard
```

2. Activate the Virtual Environment
On Windows PowerShell:
```powershell
.\activate_venv.ps1
```
On Windows Command Prompt:
```cmd
activate_venv.bat
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Launch the Server and Dashboard
```bash
python server.py
```
Alternatively, double-click run_truthguard.bat on Windows to launch the server and open your browser automatically.

5. Open the Web Interface
Navigate to:
http://localhost:8000/index.html

6. Execute the Test Suite
```bash
pytest tests/ -v
```

## Licenses and Acknowledgement

### License
This project is open-source under the MIT License. See LICENSE for full terms.

### Acknowledgement
- Virtusa Jatayu Season 6 Ideathon Committee for domain guidelines and hackathon orchestration.
- Virtusa TIME Business Unit (Telecom, Information, Media & Entertainment) for real-world enterprise problem statement alignment.
- Team CodeBots (Batch 2027):
  - Yasaswi Venkat (Team Captain & Agentic Architect)
  - Multi-Agent Debate Engineer
  - Vector DB & Ingestion Specialist
  - NLI & Benchmark Evaluator
  - Full-Stack & Deployment Engineer
