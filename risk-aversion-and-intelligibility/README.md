# Risk aversion and intelligibility

This is a standalone Track 2 design for cautious, explainable clearances. A clearance needs a contradiction allowed by the screening policy and a trace showing that the deciding facts belong to the two entities being compared. A review should tell the analyst which fact needs checking and what the answer could change.

The evaluator and reviewer demo now live in the graded [`../system/`](../system/README.md) (merged with Steps 1-3, see DECISIONS.md R1-R7). From the repository root, use `system/run --format csv datasets output/dev.jsonl` to reproduce the local predictions or `system/review --demo` to inspect a fictional review and its conditional outcomes.

| Start here | What it covers |
|---|---|
| [Intent](spec/intent.md) | The goal, the cost of mistakes, and what a useful review looks like |
| [Requirements](spec/requirements.md) | Testable rules for input, identity, evidence, decisions, and explanations |
| [Design](spec/design.md) | How to implement the checks, preserve the source trail, and show conditional outcomes |
| [Failure modes and acceptance cases](spec/failure-modes.md) | How false clearances happen and concrete cases that should catch them |
| [Implementation sequence](spec/tasks.md) | Build order, checks, and criteria for comparing changes |
| [Engineering conventions](steering/coding-standards.md) | Shared implementation and data-handling decisions for this approach |

The examples are fictional. The specification uses the organizer’s v3 brief and the local policy export. Confirm rule interpretations and input parity against the original delivery when it is available. [Organizer’s brief](<../Screening — Brief v3 (same person or not).docx>) · [Local policy export](<../datasets/Screening Dev Set - browse - Policy.csv>)
