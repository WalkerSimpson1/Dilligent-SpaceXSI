"""Check Step 2 (customer resolution) against the practice labels.

    python tools/check_customers.py [data folder]

Standard library only. For each practice label: the expected customer record(s), or
AMBIGUOUS, against what system/steps/customer.py resolves.
"""
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "system"))

from steps import customer  # noqa: E402
from steps.data import load  # noqa: E402


def main(folder):
    t0 = time.time()
    data = load(folder)
    t1 = time.time()
    resolved = {a["alert_id"]: customer.resolve(a, data) for a in data.alerts}
    t2 = time.time()
    ok, misses = 0, []
    for lab in data.tables["practice_labels"]:
        pics = resolved[lab["alert_id"]]
        exp = lab["customer_record_ids"]
        if exp == "AMBIGUOUS":
            good = len(pics) > 1
        else:
            want = {x.strip() for x in exp.split(";")}
            good = len(pics) == 1 and set(pics[0].record_ids) == want
        ok += good
        if not good:
            misses.append((lab["hit_id"], exp, [p.record_ids for p in pics]))
    n = len(data.tables["practice_labels"])
    print(f"practice labels: {ok}/{n} customer resolutions right")
    for m in misses:
        print("  MISS", *m)
    print(f"alerts: {len(resolved)}  people per alert: {dict(sorted(Counter(len(p) for p in resolved.values()).items()))}")
    print(f"links: {dict(Counter((p[0].link if p else 'none') for p in resolved.values()))}")
    print(f"time: load {t1 - t0:.1f}s, resolve all {t2 - t1:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datasets")
