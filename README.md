# Dilligent-SpaceXSI
Hackathon

## Vera: the analyst app

Vera is the command-line app on top of the screening system. Launch it from the repo folder:

```
vera            # Windows cmd / PowerShell (vera.cmd)
./vera          # Git Bash, macOS, Linux
vera dev/       # optional: point it at another data folder
```

To type just `vera` from anywhere, add this repo folder to your PATH.

- **Run Vera:** decide every hit and see the summary, including the practice-label score and unsafe clearances.
- **Review queue:** open alerts, then an alert's hits, then a hit side by side with the customer. On a hit, `t` shows the decision tree, `e` drafts emails and `d` records your own decision.
- **Decision guide:** an interactive yes/no walk through the identity SOP.
- **Draft all emails:** for every REVIEW hit, an internal draft and, where the customer can help, a neutral customer draft. Drafts are checked for tipping-off words and are never sent.

Keys: ↑↓ move, enter open, esc/← back, q quit. In terminals that can't read single keys, Vera shows numbered menus instead.

Vera never changes the graded output (`system/run`, `output/dev.jsonl`). Its files go in `.vera/` and `emails/`, both gitignored.
