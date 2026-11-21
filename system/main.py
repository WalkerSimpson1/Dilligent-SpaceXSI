"""Pipeline: load data, resolve each side, decide each hit, write one line per hit."""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # run with -I

import customer  # noqa: E402
import decide  # noqa: E402
import hit as hitmod  # noqa: E402
from data import load  # noqa: E402
from model import REVIEW, Decision  # noqa: E402


def safe_review(hit: dict, err: Exception) -> Decision:
    """If anything crashes on a hit, never clear it: send it to review."""
    return Decision(
        hit_id=hit["hit_id"], alert_id=hit["alert_id"], decision=REVIEW,
        reason_code="INSUFFICIENT_DATA", customer_record_id=None,
        reason="The system could not evaluate this hit, so it is left for review.",
        evidence=[], missing=[f"ERROR: {type(err).__name__}: {err}"],
    )


def run(folder: str, out_path: str) -> None:
    t0 = time.time()
    data = load(folder)
    resolved: dict[str, list] = {}  # alert_id -> candidates (resolve each alert once)
    decisions: list[Decision] = []
    errors = 0
    for h in data.hits:
        try:
            alert = data.alerts_by_id.get(h["alert_id"], {})
            if h["alert_id"] not in resolved:
                resolved[h["alert_id"]] = customer.resolve(alert, data)
            d = decide.decide(alert, hitmod.profile(h, data), resolved[h["alert_id"]])
            d.check()
        except Exception as e:  # noqa: BLE001
            errors += 1
            if os.environ.get("DEBUG"):
                traceback.print_exc()
            d = safe_review(h, e)
        decisions.append(d)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for d in decisions:
            f.write(json.dumps(d.to_output(), ensure_ascii=False) + "\n")

    counts = Counter(d.decision for d in decisions)
    print(f"{len(decisions)} hits -> {out_path} in {time.time() - t0:.1f}s; "
          f"{dict(sorted(counts.items()))}; errors={errors}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: main.py <data folder> <output file>")
    run(sys.argv[1], sys.argv[2])
