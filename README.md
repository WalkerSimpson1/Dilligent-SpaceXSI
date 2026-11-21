<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/vera-logo-reversed.svg">
  <img alt="Vera" src="assets/brand/vera-logo.svg" width="300">
</picture>

### Same person or not?

**Watchlist screening that clears the obvious false positives, keeps every real or uncertain match for a human, and explains each decision with the records behind it.**

![Python](https://img.shields.io/badge/python-3.10%2B-0A1A3A?style=flat-square)
![Dependencies](https://img.shields.io/badge/dependencies-standard%20library%20only-19C3A6?style=flat-square)
![Deterministic](https://img.shields.io/badge/runs-deterministic-13284F?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-0A1A3A?style=flat-square)

[What it does](#what-it-does) · [How it decides](#how-it-decides) · [Architecture](#architecture) · [Quick start](#quick-start) · [Vera app](#vera-the-analyst-app) · [Status](#project-status) · [Repository map](#repository-map)

</div>

---

## What it does

A bank screens every customer against sanctions lists, lists of politically exposed people (PEPs) and adverse-media records. Names are matched loosely, so most matches, called **hits**, are just namesakes. For every hit, this system answers one question: **is this listed person actually our customer?**

To answer it, the system works out two things and then compares them:

| | Who is the customer? | Who is the listed person? |
|---|---|---|
| **Where the facts live** | CRM records, accounts, onboarding, identity (KYC) checks, support notes | The watchlist profile, its free-text notes, web search results |
| **What makes it hard** | One person can have several records; family members share phones and addresses; nicknames and typos | Dates of birth hidden in prose ("aged 30 in November 1998"); search results mostly about other people with the same name |

Each hit gets one of three decisions:

| Decision | Meaning |
|---|---|
| 🟢 `DIFFERENT_ENTITY` | A fact proves it is someone else. The hit is cleared. |
| 🔴 `SAME_ENTITY` | The facts show it is the customer. The hit goes to compliance. |
| 🟡 `REVIEW` | The facts can't settle it. An analyst decides. |

> Every decision comes with a reason code, two to four sentences naming the deciding facts, and the IDs of the records that decided it. Nothing is cleared without evidence.

## How it decides

### The one rule behind every choice

| Mistake | Cost |
|---|---|
| Clearing a hit that is really the customer | **60** |
| Sending a different person to review | 3 |
| Sending a real match to review | 2 |

Wrongly clearing a sanctioned person is twenty times worse than an unneeded review. So **whenever the data is ambiguous, the system picks the reading that cannot clear a hit**. Anything that makes two people look *more alike* (an extra name match, an extra country) is safe to add. Anything that makes them look *different* must be certain.

### Clear only on a contradiction, confirm only on agreement

A hit is cleared only when a fact **contradicts** it:

| Check | Example |
|---|---|
| ⏳ **Time** | The customer was 7 when the fraud report was written |
| 🎂 **Date of birth** | The customer was born in 1988; the hit in 1952 |
| 🌍 **Location** | Every country tied to the customer differs from every country tied to the hit |
| 🔤 **Verified name** | The customer's passport name doesn't match any of the hit's names |
| 🏢 **Type** | One is a person, the other a company |
| ✝️ **Death** | The listed person died before the customer was screened |

It is confirmed only when **name and date of birth agree** (or name and country, for a company) and nothing contradicts them. **Missing information is never a mismatch**: a birth year alone can still agree with a full date.

## Architecture

```mermaid
flowchart LR
    A[("alerts")] --> L["1 · s1_load.py<br/>read + check tables"] --> C
    subgraph customer["Who is the customer?"]
        C["2 · s2_customers.py<br/>Customer resolution"]
        CRM[("CRM · accounts ·<br/>onboarding · KYC · notes")] --> C
    end
    subgraph listed["Who is the listed person?"]
        H["3 · s3_hit_facts.py<br/>Hit facts"]
        W[("hits · search results")] --> H
    end
    L --> H
    C -- Customer --> D
    H -- HitFacts --> D
    D["4 · s4_decide.py<br/>Decision engine"] --> V["5 · s5_batch.py<br/>verify every row"] --> O[/"output/dev.jsonl<br/>decision · reason code · reason · evidence"/]
    M["match/ + normalize.py<br/>names · dates · countries"] -.-> C
    M -.-> H
    M -.-> D

    classDef step fill:#0A1A3A,stroke:#19C3A6,color:#fff
    classDef data fill:#13284F,stroke:#13284F,color:#fff
    classDef out fill:#19C3A6,stroke:#19C3A6,color:#0A1A3A
    class L,C,H,D,V,M step
    class A,CRM,W data
    class O out
```

- **Every fact carries its source.** A date of birth is stored with the ID of the record it came from (`KYC-…`, `NOTE-…`, `H-…`, `SR-…`), so the decision can cite exactly the records that decided it.
- **Deterministic.** Standard-library Python with fixed rules and fixed tables: the same input gives the same output on every run.
- **Fails loudly, never partially.** Every output row is checked (one row per hit, valid reason code, cited IDs exist) before the file is replaced; a structural problem stops the run with an error instead of writing a partial file.

## Quick start

Python 3.10 or later; nothing to install.

```bash
# decide every hit in a data folder, one JSON line per hit
system/run datasets output/dev.jsonl

# run the unit tests
python -m unittest discover -s tests -t .
```

One output line looks like this:

```json
{"hit_id": "H-…", "alert_id": "A-…", "decision": "DIFFERENT_ENTITY", "reason_code": "DOB_MISMATCH",
 "customer_record_id": "CUS-…", "reason": "The customer was born in 2001 (KYC-…); the hit's search results put its birth year at 1965 or 1966 (SR-…).",
 "evidence": ["KYC-…", "SR-…"]}
```

## Vera: the analyst app

<img align="right" src="assets/brand/vera-icon.svg" width="72" alt="">

Vera is the command-line app on top of the screening system. Launch it from the repo folder:

```
vera            # Windows cmd / PowerShell (vera.cmd)
./vera          # Git Bash, macOS, Linux
vera dev/       # optional: point it at another data folder
```

To type just `vera` from anywhere, add this repo folder to your PATH.

| Menu | What it does |
|---|---|
| **Run Vera** | Decide every hit and see the summary, including the practice-label score and unsafe clearances |
| **Review queue** | Open alerts, then an alert's hits, then a hit side by side with the customer. On a hit, `t` shows the decision tree, `e` drafts emails and `d` records your own decision |
| **Decision guide** | An interactive yes/no walk through the identity SOP |
| **Draft all emails** | For every REVIEW hit, an internal draft and, where the customer can help, a neutral customer draft. Drafts are checked for tipping-off words and are never sent |

**Keys:** `↑` `↓` move · `enter` open · `esc` / `←` back · `q` quit. In terminals that can't read single keys, Vera shows numbered menus instead.

Vera never changes the graded output (`system/run`, `output/dev.jsonl`). Its files go in `.vera/` and `emails/`, both gitignored.

## Project status

The work plan with every step is in [`docs/plan/steps.txt`](docs/plan/steps.txt); how the two codebases were merged is in [`docs/plan/DECISIONS.md`](docs/plan/DECISIONS.md) (R1–R7).

| Step | What | Status |
|---|---|---|
| 0 | Foundation: entry point, data loader, output checks | ✅ `system/run`, `engine/s1_load.py`, `engine/s5_batch.py` |
| 1 | Shared matchers: names, dates, countries | ✅ `system/match/` · transliteration is used by the engine |
| 2 | Customer resolution | ✅ `engine/s2_customers.py` (Nij's Step 2 in `steps/customer.py` feeds Vera) |
| 3 | Hit profile | ✅ `engine/s3_hit_facts.py`, with the Step 3 age reader (`steps/hit.py`) as fallback |
| 4 | Decision engine | ✅ `engine/s4_decide.py` |
| 5 | Evaluation and QA | 🔧 `tools/score` (practice labels, unsafe clearances first) · `tools/check_customers.py` |
| 6 | Documentation and submission | 🔧 In progress |
| 7 | Analyst extras | 🔧 Vera works but still runs on the Step 0–3 pipeline (`steps/`), not the engine |

Dev set: 457 cleared, 121 matched, 241 review out of 819 hits in about 75 seconds; practice labels 50/50 with 0 unsafe clearances; byte-identical reruns.

## Methodology

- [**Step 1 methodology**](docs/plan/STEP1_METHODOLOGY.md): the main name, date and country decisions in plain language.
- [**Step 2 notes**](docs/plan/STEP2.md): customer resolution.
- [**Decision log**](docs/plan/DECISIONS.md): every decision with its reason and status.
- [**Cautious-clearance spec**](docs/spec/README.md): intent, requirements, design and the false-clearance acceptance cases the engine is tested against.

A few highlights:

- **Names in any script.** Cyrillic, Greek, Armenian, Georgian and Japanese names are transliterated with fixed tables before matching.
- **Every clearance is a named contradiction**, replayed from its source records before it is written.
- **Bank slash dates are day-first for linking records only;** a date that could be read two ways never clears a hit on its own.
- **Ambiguous countries count as all of them.** An extra country can only block a clearance.

## Repository map

Folders follow the pipeline. Read `system/engine/` top to bottom: `s1` → `s5` is the order a hit goes through.

```
system/
├── run · run.py          graded entry point: system/run <data folder> <output file>
├── engine/               THE GRADED PIPELINE
│   ├── s1_load.py        1. read the tables, check every alert's hit list
│   ├── s2_customers.py   2. who is the customer? links, merges, approved KYC, notes
│   ├── s3_hit_facts.py   3. what the listing says: birth dates, countries, reports, death
│   ├── s4_decide.py      4. policy rules → decision, reason code, reason, evidence
│   ├── s5_batch.py       5. every hit in order, verify the rows, write the file
│   └── normalize.py      shared name/date/country helpers (+ countries.tsv)
├── match/                Step 1 matchers: names, transliteration, dates, countries
├── steps/                Step 0–3 contract and modules (data, model, customer, hit, decide, main); Vera runs on these
├── vera/ · vera_cli.py   the analyst app
tools/                    score (practice labels) · review (what-if demo) · check_customers.py
tests/                    test_engine/ · test_match/ · test_steps/ (invented data only)
docs/
├── brief/                Track 2 description and the organiser's brief
├── plan/                 steps.txt · DECISIONS.md · STEP1_METHODOLOGY.md · STEP2.md
└── spec/                 cautious-clearance spec: intent, requirements, design, failure modes
assets/brand/             Vera logo files
datasets/                 dev data (must be purged before submission)
```

## Data and safety

- **The data stays out of the submission.** The development data comes from the event's participant data room and is for participants only. Tests use invented names and dates.
- **No secrets in the repo.** A language model, if used, is called only through OpenRouter with the key in `OPENROUTER_API_KEY`; `.env` is gitignored.
- **Drafts are never sent.** Vera's customer emails never mention screening, watchlists or sanctions (that would be tipping off).

---

<div align="center">
<sub>Built for the <b>Same Person or Not?</b> hackathon track · MIT License</sub>
</div>
