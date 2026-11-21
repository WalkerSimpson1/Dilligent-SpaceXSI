<div align="center">
<img alt="Vera" src="../assets/brand/vera-logo.svg" width="220">

# How Vera works: a plain-language guide

*About a 7-minute read. No technical background needed.*
</div>

---

## 1. The problem

Banks may not do business with certain people, and must take extra care with others. Those people appear on **watchlists**: **sanctions lists**, lists of **politically exposed persons** (officials and their families) and **adverse media** (people named in news or court records for crimes such as fraud).

Every customer's name is checked against these lists. To be safe, the check is loose: "Mohamed" also catches "Muhammad", and "Li Wei" also catches "Wei Li". Each possible match is a **hit**. A customer's hits are grouped into an **alert**.

Because the check is loose, **most hits are just different people who share a name**. Today an analyst must look at each one. That is slow, and it buries the few real matches among hundreds of false alarms.

**Vera's job is to decide, for each hit: is this listed person really our customer?**

## 2. What Vera gives back

| Answer | What it means | What happens next |
|---|---|---|
| **Different person** | A fact proves it is someone else | The hit is cleared |
| **Same person** | The facts show it is the customer | It goes to the compliance team |
| **Needs review** | The facts can't settle it | An analyst decides |

Every answer comes with a short code (such as *"dates of birth don't match"*), a few sentences naming the deciding facts, and the ID numbers of the records they came from. An analyst can check any decision in seconds. An alert closes only when **every** hit in it is cleared.

## 3. Why mistakes are not equal

| Mistake | Cost |
|---|---|
| Clearing someone who really **is** on the list | **60** |
| Sending a different person to review | 3 |
| Sending a real match to review | 2 |

Letting a sanctioned person stay a customer is twenty times worse than one extra file for an analyst. So every choice follows one rule: **when in doubt, don't clear.** But sending everything to review resolves nothing and scores zero. The skill is clearing as many false alarms as possible **without ever clearing a real one**.

## 4. How Vera decides, step by step

Think of Vera as a careful detective who builds two case files and then compares them.

**Step 1: Read and check the files.** Vera reads the bank's records and the watchlist data, and checks that nothing is missing or duplicated. If the files don't add up, it stops and says so rather than guessing.

**Step 2: Work out who the customer really is.** The alert shows the customer only as screened, perhaps with a nickname or typo. The real details are spread across bank systems that share no common ID: the customer database (one person may have two records), accounts and logins, **identity checks** (an outside company verifying a passport), and support notes ("customer used to live in Ghana"). Vera follows the links between them like a paper trail. When sources disagree, **a passed identity check beats what the customer typed in**. Rejected or expired checks are ignored.

**Step 3: Work out who the listed person really is.** The most useful fact, the date of birth, is often missing from its proper field and hidden in the text, such as *"charged in November 1998, aged 30"*. From that, Vera works out a birth year of 1967 or 1968, and keeps both, because it can't know whether the birthday had passed. When there's no date at all, it looks at **web search results** for the name. It also notes every country linked to the listed person, any date of death, and the dates of reports about them.

**Step 4: Compare and decide.** Vera clears a hit **only if a fact contradicts it**:

| Contradiction | Example |
|---|---|
| **Too young** | The customer was 7 when the fraud was reported |
| **Birth dates clash** | Customer born 1994; listed person born 1961 |
| **No shared country** | The customer only ever lived in Germany; the listed person only in Peru |
| **Verified name differs** | The customer's passport name matches none of the listed names |
| **Person vs. company** | One is a person, the other a business |
| **Died earlier** | The listed person died before the customer was screened |

It says "same person" **only when name and date of birth agree** (name and country, for a company) and nothing contradicts them. Anything else goes to review.

**Step 5: Double-check before saving.** One answer per hit, a valid code for each, and every cited record exists. If anything is off, Vera writes nothing rather than a half-finished file.

> **A fictional example.** Customer **Alex Morgan** is flagged against a listing for **Alex Morgan**. An approved passport check says Alex was born in **1994**; the listing gives **1961**. Answer: *different person*. Had the listing said 12 July 1994, with both linked to the UK, the answer would be *same person*. Had the only birth year come from an unrelated-looking search result, it would be *needs review*, with a note to check the original listing.

## 5. Vera, the analyst app

The same engine powers **Vera**, an app for the analyst, and gives exactly the same decisions. It offers:

- a **review queue**, showing each hit side by side with the customer;
- a **decision tree** for every hit: each check, and whether it passed;
- a **yes/no guide** through the bank's identity rules;
- **draft emails** for hits that need more information. The customer version never mentions screening or watchlists, because warning a customer ("tipping off") can be illegal. Nothing is sent automatically.

## 6. The main decisions and their trade-offs

Each of these was a deliberate choice. Most trade some extra reviews for safety.

| # | Decision | What we gain | What it costs |
|---|---|---|---|
| 1 | **Fixed written rules, not an AI model** | The same answer on every run (the hackathon checks five runs), and every decision explainable | Wording the rules don't recognise is missed. Missing facts lead to review, so the cost is analyst time, not safety |
| 2 | **Clear only on proof; missing information is never a mismatch** | No clearance on a guess. A customer with no birth date can't be cleared on birth date | About 3 in 10 hits still go to a person |
| 3 | **A fact that can be read two ways keeps both readings.** *03/04/1988* is both 3 April and 4 March; *"Congo"* is both Congos | A misreading can never clear a hit | A few clearable hits go to review |
| 4 | **Join two customer records only on strong evidence**: same phone **and** same full birth date, or same passport | Family members who share a phone and address aren't merged | Some records of the same person stay apart |
| 5 | **Search results are ignored unless proven relevant**: same kind of listing, in a linked country, about that person and nobody else | A namesake's birth date can't clear a real match | Many results go unused |
| 6 | **Person names are hidden before reading countries from text** | "Jordan Ellis" isn't read as the country Jordan | None found so far |
| 7 | **Strict name matching.** The team built two matchers; a generous one (accepting "Jonny" for "John": nickname plus typo) produced doubtful matches, like two banks with similar names | Fewer false "same name" agreements | Strict matching finds a name mismatch slightly more often, the riskier direction. It scored perfectly in practice; we keep watching it |
| 8 | **Other alphabets.** Cyrillic, Greek, Armenian, Georgian and Japanese names are converted with fixed tables. Arabic, Chinese, Hebrew and others are kept and flagged | Names can be compared across scripts without guessing | Unconvertible names never help a match; a human sees them |
| 9 | **Standard tools only, every fact sourced** | Runs anywhere with nothing to install; every answer traceable to its records | We wrote our own name, date and country tools instead of using ready-made ones |

The full log of these decisions is in [`plan/DECISIONS.md`](plan/DECISIONS.md), and the name, date and country choices are explained in [`plan/STEP1_METHODOLOGY.md`](plan/STEP1_METHODOLOGY.md).

## 7. Results so far

On the 819 practice hits (440 alerts), in about 72 seconds:

| Answer | Hits | Share |
|---|---:|---:|
| Different person | 457 | 56% |
| Same person | 121 | 15% |
| Needs review | 241 | 29% |

**174 of 440 alerts (40%) close completely** with no human needed. On the 50 cases with known answers, Vera got **50 right, with 0 unsafe clearances**. The most common grounds for clearing were *no shared country* (226), *verified name differs* (122) and *birth dates clash* (83).

## 8. What is still open

- **Crash safety.** Today, if one unusual record makes the program fail, the whole run produces no file, which would score zero. The fix (turning that one hit into "needs review") is assigned and in progress.
- **The real test is unseen.** The final score comes from about 550 new hits with differently worded text. Practice results are encouraging, not a guarantee.
- **Before submission,** the competition data must be removed from the public repository.

---

<sub>Glossary: **alert**, a customer flagged by screening · **hit**, one possible watchlist match · **identity check**, a passport or ID verification by an outside company · **tipping off**, illegally warning someone that they are under investigation.</sub>
