"""Precompute budget plans at several levels so the dashboard works offline."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from domino_engine import load_corridor, betweenness
from planner import (expected_loss, greedy_plan, harden_cost, seeds,
                     resilience_score, HARDEN_MULT)

BUDGETS = [5, 10, 20, 30, 50]

def main():
    ref = load_corridor()
    base_exp, _, total, base_acc = expected_loss(set())
    betw = betweenness(ref)
    conv_order = sorted(seeds(ref), key=lambda e: -betw[e])
    out = dict(population=total, baseline_access=round(base_acc, 1),
               baseline_expected_loss=round(base_exp),
               baseline_resilience=resilience_score(base_exp, total),
               harden_multiplier=HARDEN_MULT,
               costs={e: harden_cost(ref.edges[e]) for e in seeds(ref)},
               labels={e: ref.edges[e].label for e in seeds(ref)},
               budgets={})
    for b in BUDGETS:
        ds, dsp, dexp, dst = greedy_plan(b)
        cs, csp, cexp, cst = greedy_plan(b, ranked_by=conv_order)
        sd, sc = base_exp - dexp, base_exp - cexp
        out["budgets"][str(b)] = dict(
            domino=dict(assets=sorted(ds), spent=round(dsp, 1), steps=dst,
                        protected=round(sd), expected_loss=round(dexp),
                        resilience=resilience_score(dexp, total)),
            conventional=dict(assets=sorted(cs), spent=round(csp, 1), steps=cst,
                              protected=round(sc), expected_loss=round(cexp),
                              resilience=resilience_score(cexp, total)),
            advantage=round(sd / sc, 2) if sc > 0 else None)
        print(f"  Rs {b:>3} cr   DOMINO protects {sd:>6,.0f} (Rs {dsp:>5.1f} cr)"
              f"   conventional {sc:>6,.0f} (Rs {csp:>5.1f} cr)"
              f"   {('%.1fx' % (sd/sc)) if sc > 0 else '—'}")
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plans.json")
    json.dump(out, open(p, "w"))
    print(f"\n  wrote {p}")
    return out

if __name__ == "__main__":
    main()
