# Next steps

Six features we plan to build **separately and at the same time**, each in its own worktree and branch. Each one merges into `main` on its own once its checks pass.

## Ground rules for every feature

These come from the brief (`docs/brief/Track2_Description.txt`) and the decisions so far (`DECISIONS.md`):

- **The graded run must not change unless the feature is meant to change it.** After each merge, `system/run datasets output/dev.jsonl` must still give 50/50 practice labels with 0 unsafe clearances. Every run must give byte-identical output.
- **A language model may be called only through OpenRouter, with the key in `OPENROUTER_API_KEY`.** This is the brief's rule for the graded system. A direct Grok (xAI) key can't be used on the graded path, but Grok models are on OpenRouter (for example `x-ai/grok-…`).
- **Model output never clears a hit by itself.** A model can add facts that send a hit to review, or help explain a decision. A clearance still needs a contradiction the rules can replay from records. That is the 60-point risk.
- **Reproducibility.** The unseen set is run five times, and 10% of the score is for identical decisions and reason codes. Model calls must be cached, or kept off the decision path.
- **No keys, no dev data, no real people in commits.** Keys stay in `.env` (gitignored).
- **Each feature has one owner.** Each feature edits only its own files. Shared files (`system/engine/*`, `system/vera/engine_bridge.py`) are changed in a single, announced merge.

## The six features

| # | Feature | Branch / worktree | Owner | Touches the graded output? |
|---|---|---|---|---|
| 1 | Data enrichment via a language model | `feat/llm-enrich` → `../dsx-enrich` | _tbd_ | Yes, if its facts feed decisions |
| 2 | Emails for missing or needed data | `feat/emails` → `../dsx-emails` | _tbd_ | No (Vera only) |
| 3 | Social-media screening for extremist views via Grok and X | `feat/grok-social` → `../dsx-social` | _tbd_ | Should not (see the risks) |
| 4 | Grok explanation of why it was / was not a hit | `feat/grok-explain` → `../dsx-explain` | _tbd_ | Only the `reason` text, if at all |
| 5 | Finalised command-line tool for real use | `feat/cli-final` → `../dsx-cli` | _tbd_ | No |
| 6 | Website to showcase and download the tool | `feat/website` → `../dsx-site` | _tbd_ | No |

Start each from an up-to-date `main`: `git worktree add ../dsx-<name> -b feat/<name> origin/main`.

---

### 1. Data enrichment via a language model

**Goal:** use a language model (through OpenRouter) to pull facts the fixed rules miss out of free text: dates of birth, countries and identity details worded in unexpected ways. *Data source still to be confirmed; the plan says "from … via llm api key".*

- **Where it fits:** step 3 (hit facts) and step 2 (support notes), as a fallback when the rules find nothing.
- **Safety:** an extracted fact must quote the exact text it came from, and the code checks that the quote really appears in the record. Model facts may only *block* a clearance or send a hit to review. They are never the sole reason to clear.
- **Determinism:** temperature 0, a fixed model version, and a cache keyed on the input text. The cache is filled once, so the five graded runs read the same answers. If the key is missing or a call fails, the run continues without enrichment.
- **Budget:** about 550 unseen hits in under 30 minutes, so calls run in parallel with a timeout.
- **Done when:** practice labels are still 50/50 with 0 unsafe clearances, the number of reviews goes down, and five runs are byte-identical.

### 2. Emails for missing or needed data

**Goal:** for every hit left for review, draft the request that would settle it: an internal note to the analyst, and a neutral note to the customer where they can supply the missing fact (such as a date of birth or proof of address).

- **Builds on:** `system/vera/emails.py` and the missing-fact codes from `engine_bridge.py` (decision R9).
- **Safety:** customer drafts must pass `tipping_off_check()`, so they never mention screening, watchlists or sanctions. Drafts are never sent automatically.
- **Optional:** model-written wording, run through the same tipping-off check and a fallback to the fixed template.
- **Done when:** every review hit with a missing-fact code gets a draft, every customer draft passes the check, and none is sent.

### 3. Social-media screening for extremist views via Grok and X

**Goal:** use Grok's access to X to find public posts showing support for extremism or violence, as extra context for analysts.

- **Risks to settle before building:**
  - **Legal:** in the EU and UK, political and religious beliefs are special-category personal data (GDPR article 9), and profiling customers by belief needs a clear lawful basis.
  - **Rules:** X's terms forbid scraping, and the brief allows a model only through OpenRouter.
  - **Identity:** an X account with the customer's name is rarely provably the customer. That is the same namesake problem this whole system solves.
- **Safer scope:** look up the **listed person** only (not customers), and only for public **violent-extremism or terrorism** links, not beliefs. Analysts see the result in Vera as unverified context, with links. It never changes a decision.
- **Done when:** the team signs off the scope above (or a better one), the graded output is unchanged, and every result shows its source link and is marked unverified.

### 4. Grok explanation of why it was / was not a hit

**Goal:** a short, plain-English explanation of each decision, built from the facts the engine actually used.

- **Input:** the engine's findings and source IDs, not the raw records, so the model can't add facts.
- **Safety:** the explanation may only cite record IDs that are in the decision's evidence. If it names any other fact, it is thrown away and the fixed template is used.
- **Graded `reason` field:** the brief scores reasons at 25% of the unseen score. Keep the rule-based reason in the graded file unless model reasons are cached, checked and proven better. Otherwise show model explanations only in Vera.
- **Done when:** every explanation passes the evidence check, and the graded output is unchanged or deliberately improved and reproducible.

### 5. Finalised command-line tool for real use

**Goal:** make Vera ready for analysts beyond the hackathon.

- **Install:** one command, no extra packages, on Windows, macOS and Linux.
- **Usage:** a `--help` page and clear errors for a wrong data folder or a missing key.
- **Records:** analyst decisions are saved and can be exported, with an audit trail of who decided what and when.
- **Settings:** OpenRouter key and model, and turning features 1, 3 and 4 on and off.
- **Speed:** the run takes about 72 seconds today; show progress, and cache results between sessions.
- **Depends on:** crash safety (R10, `error_sam.md`), so one bad record can't stop the tool.
- **Done when:** a new user can install it, run it on the dev folder and review a hit by following only the README.

### 6. Website to showcase and download the tool

**Goal:** a simple public page that explains Vera and lets people download it.

- **Content:** the story from [`docs/HOW_IT_WORKS.md`](../HOW_IT_WORKS.md), screenshots or a recording of Vera on **fictional** data, the results, and a download link (a GitHub release zip).
- **Brand:** the logos in `assets/brand/` (navy `#0A1A3A`, teal `#19C3A6`).
- **Hosting:** GitHub Pages from a `site/` folder or a `gh-pages` branch.
- **Safety:** no dev data, customer names or keys on the page.
- **Done when:** the page is live, the download runs, and it shows no real data.

---

## Order and dependencies

- **Can start now, in parallel:** 2, 5 and 6. They don't touch the graded output.
- **Start now, merge carefully:** 1 and 4 change shared engine code. They need the OpenRouter caching agreed first, so both use **one shared helper**, `system/llm.py`: one cache, one key, one fallback.
- **Agree the scope first:** 3.
- **Before submission:** crash safety (R10) and removing the dev data from the repo (R11, step 6.3).
