# Engineering conventions

- Use Python 3 standard-library components and the files supplied to the runner. Keep the official JSONL adapter and the development CSV adapter on the same internal representation. The proposed first implementation runs offline.
- Preserve exact source identifiers and distinguish observed values, normalized values, interpretations, and hypotheticals. Record source eligibility and rejected proof attempts separately from facts used in the verdict.
- Keep parsing, identity linking, fact collection, policy predicates, and output formatting independently testable. Use tree-shaped data or small typed records. Use deterministic ordering at joins, candidate evaluation, reason selection, and serialization.
- Put organizer policy rules and constants in named predicates with direct test coverage. Describe uncertain source interpretations in the design and verify them against the original files before submission.
- Restrict stdout and stderr diagnostics to aggregate counts, error classes, and locations useful for repair. Keep private details in authorized local artifacts. Use synthetic fixture records for tests and public examples. Follow the organizer’s instructions for distributing the required prediction file.
- Fit any analysis or implementation work for this approach inside its own folder in shared development. Stage a submission-shaped `system/` and `output/` in a separate workspace or coordinate the final placement with the team.
