"""Evaluate Step 2 against the 50 practice labels (uses pandas only for loading the xlsx dump)."""
import pickle, sys, time
sys.path.insert(0, '.')
import pandas as pd
from system import customer as CU

def rows(df): return [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in df.to_dict('records')]

def load():
    T = pickle.load(open('T.pkl', 'rb'))
    return {'alerts': rows(T['Alerts']), 'customers': rows(T['Customers']), 'accounts': rows(T['Accounts']),
            'onboarding': rows(T['Onboarding']), 'kyc': rows(T['KYC checks']), 'notes': rows(T['Notes'])}, T['Practice labels']

if __name__ == '__main__':
    t0 = time.time(); tables, pl = load(); print('loaded', round(time.time()-t0,1), 's')
    t0 = time.time(); ix = CU.build_index(tables); print('index', round(time.time()-t0,1), 's')
    alerts = {a['alert_id']: a for a in tables['alerts']}
    ok = 0; bad = []
    seen = {}
    for _, l in pl.iterrows():
        a = alerts[l.alert_id]
        if l.alert_id not in seen: seen[l.alert_id] = CU.resolve(a, ix)
        res = seen[l.alert_id]
        exp = l.customer_record_ids
        if exp == 'AMBIGUOUS': good = res.ambiguous
        else:
            want = set(x.strip() for x in exp.split(';'))
            good = (not res.ambiguous) and bool(res.pictures) and set(res.pictures[0].record_ids) == want
        ok += good
        if not good: bad.append((l.hit_id, l.alert_id, res.link, exp, [p.record_ids for p in res.pictures], res.note))
    print(f'customer resolution matches {ok}/{len(pl)} practice labels')
    for b in bad: print('MISS', b)
