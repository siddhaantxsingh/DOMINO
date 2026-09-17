"""
Where should a fixed resilience budget go?

This is the question a city actually asks, and it is the one thing a cascade map
cannot answer. The planner runs the whole failure sweep, measures how much
service the corridor loses in expectation, then greedily buys the hardening that
buys back the most service per rupee.

It is scored head to head against the conventional method: rank assets by
network centrality and harden the most central ones first. Both plans are
computed by the same code on the same budget, so the comparison is fair.
"""
from __future__ import annotations
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from domino_engine import (load_corridor, run_cascade, accessibility, betweenness,
                           Network)

TOWER_OUT   = "T1"
HARDEN_MULT = 1.75            # same "reinforce and widen" action the engine tests
COST_ROAD   = 1.2             # crore per km, indicative
COST_BRIDGE = 6.0             # crore per km, indicative


def harden_cost(e):
    rate = COST_BRIDGE if e.kind == "bridge" else COST_ROAD
    return round(rate * e.length_km, 1)


def seeds(net):
    return [eid for eid, e in net.edges.items() if e.kind != "service"]


def expected_loss(hardened: set):
    """
    People who lose access to a critical service, averaged over every plausible
    single-asset failure. Lower is better.
    """
    ref = load_corridor()
    for h in hardened:
        ref.edges[h].cap_multiplier = HARDEN_MULT
    base, _ = accessibility(ref)
    total = sum(n.population for n in ref.nodes.values())

    losses, detail = [], {}
    for eid in seeds(ref):
        net = load_corridor()
        for h in hardened:
            net.edges[h].cap_multiplier = HARDEN_MULT
        tr = run_cascade(net, eid, TOWER_OUT)
        lost = total * max(0.0, base - tr["accessibility"][-1]) / 100.0
        losses.append(lost)
        detail[eid] = dict(lost=round(lost), horizon=tr["containment_horizon"],
                           final=tr["accessibility"][-1])
    exp = sum(losses) / len(losses)
    return exp, detail, total, base


def resilience_score(exp_loss, total):
    return round(100.0 * (1 - exp_loss / total), 1)


def greedy_plan(budget, ranked_by=None):
    """
    ranked_by=None  -> DOMINO: buy the biggest reduction in expected loss per crore
    ranked_by=list  -> conventional: buy in the given order while the budget lasts
    """
    ref = load_corridor()
    costs = {eid: harden_cost(ref.edges[eid]) for eid in seeds(ref)}
    chosen, spent = set(), 0.0
    base_exp, _, total, _ = expected_loss(set())
    cur = base_exp
    steps = []

    if ranked_by is not None:
        for eid in ranked_by:
            if eid in chosen or costs[eid] > budget - spent:
                continue
            chosen.add(eid); spent += costs[eid]
            new, _, _, _ = expected_loss(chosen)
            steps.append(dict(asset=eid, label=ref.edges[eid].label,
                              cost=costs[eid], exp_loss=round(new),
                              saved=round(cur - new)))
            cur = new
        return chosen, spent, cur, steps

    while True:
        best = None
        for eid in seeds(ref):
            if eid in chosen or costs[eid] > budget - spent:
                continue
            new, _, _, _ = expected_loss(chosen | {eid})
            gain = cur - new
            if gain <= 0:
                continue
            per = gain / costs[eid]
            if best is None or per > best[0]:
                best = (per, eid, new, gain)
        if best is None:
            break
        _, eid, new, gain = best
        chosen.add(eid); spent += costs[eid]
        steps.append(dict(asset=eid, label=ref.edges[eid].label, cost=costs[eid],
                          exp_loss=round(new), saved=round(gain)))
        cur = new
    return chosen, spent, cur, steps


def main(budget=30.0):
    ref = load_corridor()
    base_exp, base_detail, total, base_acc = expected_loss(set())
    print(f"\n  corridor of {total:,} people · baseline access {base_acc:.1f}%")
    print(f"  with no hardening, an average single failure costs "
          f"{base_exp:,.0f} people their access to a critical service")
    print(f"  resilience score {resilience_score(base_exp, total)} / 100\n")
    print(f"  budget: Rs {budget:.0f} crore\n")

    betw = betweenness(ref)
    conv_order = sorted(seeds(ref), key=lambda e: -betw[e])

    d_set, d_spent, d_exp, d_steps = greedy_plan(budget)
    c_set, c_spent, c_exp, c_steps = greedy_plan(budget, ranked_by=conv_order)

    def show(name, st, spent, exp):
        print(f"  {name}")
        for s in st:
            print(f"      buy  {s['label']:<24} Rs {s['cost']:>5.1f} cr"
                  f"   protects {s['saved']:>6,} more people")
        if not st:
            print("      (nothing affordable reduces expected loss)")
        print(f"      spent Rs {spent:.1f} cr · expected loss now {exp:,.0f} people"
              f" · resilience {resilience_score(exp, total)}/100\n")

    show("CONVENTIONAL — harden the most central assets first", c_steps, c_spent, c_exp)
    show("DOMINO — harden where it buys back the most service", d_steps, d_spent, d_exp)

    saved_d, saved_c = base_exp - d_exp, base_exp - c_exp
    ratio = (saved_d / saved_c) if saved_c > 0 else float("inf")
    print(f"  SAME BUDGET, TWO PLANS")
    print(f"      conventional protects {saved_c:,.0f} people")
    print(f"      DOMINO protects       {saved_d:,.0f} people", end="")
    print(f"   ({ratio:.1f}x more)\n" if saved_c > 0 else "\n")

    out = dict(
        budget_cr=budget, population=total, baseline_access=round(base_acc, 1),
        baseline_expected_loss=round(base_exp),
        baseline_resilience=resilience_score(base_exp, total),
        costs={eid: harden_cost(ref.edges[eid]) for eid in seeds(ref)},
        labels={eid: ref.edges[eid].label for eid in seeds(ref)},
        domino=dict(assets=sorted(d_set), spent=round(d_spent, 1),
                    expected_loss=round(d_exp), steps=d_steps,
                    protected=round(saved_d),
                    resilience=resilience_score(d_exp, total)),
        conventional=dict(assets=sorted(c_set), spent=round(c_spent, 1),
                          expected_loss=round(c_exp), steps=c_steps,
                          protected=round(saved_c),
                          resilience=resilience_score(c_exp, total)),
        advantage=round(ratio, 2) if saved_c > 0 else None)
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"  wrote {p}\n")
    return out


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 30.0)
