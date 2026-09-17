"""
Precompute the response playbook: run every plausible seed failure offline and
store the trace, the containment horizon, the action that holds (if any) and the
dark zones. This is what a city would run overnight and hand out as cards.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from domino_engine import (load_corridor, run_cascade, accessibility,
                           SERVICE_THRESHOLD_KM, MINUTES_PER_STEP, SCORE_WEIGHTS,
                           TOWER_RADIUS_KM)

TOWER_OUT = "T1"

def main():
    ref = load_corridor()
    base, _ = accessibility(ref)
    scenarios, cards = {}, []

    for eid, e in ref.edges.items():
        if e.kind == "service":
            continue
        net = load_corridor()
        tr = run_cascade(net, eid, TOWER_OUT)
        scenarios[eid] = tr
        act = next((st["action"] for st in tr["steps"]
                    if st.get("status") == "CASCADE STOPPED"), None)
        first = tr["dark_zones"][0] if tr["dark_zones"] else None
        dominoes = [st["domino"]["label"] for st in tr["steps"] if st.get("domino")]
        if not dominoes:
            outcome = "no cascade"
        elif tr["containment_horizon"] > 0:
            outcome = "contained"
        else:
            outcome = "uncontained"
        cards.append(dict(
            seed=eid, seed_label=e.label, kind=e.kind, outcome=outcome,
            horizon=tr["containment_horizon"],
            dominoes=dominoes,
            action=act["label"] if act else None,
            clock=act["clock"] if act else None,
            window_min=act["window_min"] if act else None,
            final_accessibility=tr["accessibility"][-1],
            dark_zones=len(tr["dark_zones"]),
            first_dark=(f"{first['label']} at T+{first['t_dark_min']} min" if first else None),
            population_at_risk=sum(z["population"] for z in tr["dark_zones"])))

    order = {"uncontained": 0, "contained": 1, "no cascade": 2}
    cards.sort(key=lambda c: (order[c["outcome"]], c["final_accessibility"]))
    out = dict(
        meta=dict(baseline_accessibility=round(base, 1),
                  population=sum(n.population for n in ref.nodes.values()),
                  threshold_km=SERVICE_THRESHOLD_KM, tower_radius_km=TOWER_RADIUS_KM,
                  minutes_per_step=MINUTES_PER_STEP, weights=SCORE_WEIGHTS,
                  tower_out=TOWER_OUT, tower_out_label=ref.nodes[TOWER_OUT].label,
                  scenario_count=len(cards)),
        graph=dict(
            nodes=[dict(id=n.id, x=n.x, y=n.y, kind=n.kind, population=n.population,
                        label=n.label) for n in ref.nodes.values()],
            edges=[dict(id=e.id, u=e.u, v=e.v, km=e.length_km, capacity=e.capacity,
                        kind=e.kind, label=e.label, alive=e.alive)
                   for e in ref.edges.values()]),
        playbook=cards, scenarios=scenarios)

    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_data.json")
    json.dump(out, open(p, "w"))

    print(f"\n  precomputed {len(cards)} seed failures over a "
          f"{len(ref.nodes)}-node corridor\n")
    print(f"  {'asset':<26}{'horizon':>8}{'final acc':>11}{'at risk':>10}  recommended action")
    print("  " + "-" * 94)
    for c in cards:
        h = {"no cascade": "n/a", "uncontained": "0"}.get(c["outcome"],
             str(c["horizon"]))
        act = (c["action"] or ("the corridor absorbs it" if c["outcome"] == "no cascade"
                               else "nothing holds it: harden before it fails"))
        print(f"  {c['seed_label']:<26}{h:>8}{c['final_accessibility']:>10.1f}%"
              f"{c['population_at_risk']:>10,}  {act[:46]}")
    print(f"\n  wrote {p}\n")
    return out

if __name__ == "__main__":
    main()
