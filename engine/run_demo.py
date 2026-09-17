"""Run the DOMINO scenario and print the trace. Writes output.json for the dashboard."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from domino_engine import (load_corridor, run_cascade, accessibility, assign,
                           SERVICE_THRESHOLD_KM, MINUTES_PER_STEP, SCORE_WEIGHTS)

BOLD = "\033[1m"; DIM = "\033[2m"; R = "\033[0m"
RED = "\033[31m"; AMB = "\033[33m"; GRN = "\033[32m"; VIO = "\033[35m"

def bar(v, w=18):
    f = int(round(v * w))
    return "█" * f + "·" * (w - f)

def main(seed="B1", tower="T2"):
    net = load_corridor()
    base, _ = accessibility(net)
    pop = sum(n.population for n in net.nodes.values())

    print(f"\n{BOLD}DOMINO — cascade and intervention engine{R}")
    print(f"{DIM}corridor: {len(net.nodes)} nodes, {len(net.edges)} edges · "
          f"population {pop:,} · service threshold {SERVICE_THRESHOLD_KM} km{R}\n")
    print(f"  baseline accessibility        {BOLD}{base:5.1f}%{R}")

    seed_label = net.edges[seed].label
    print(f"\n{RED}  ▸ FAILURE INJECTED{R}  {seed_label}"
          f"{('  +  ' + net.nodes[tower].label + ' down') if tower else ''}\n")

    net2 = load_corridor()
    trace = run_cascade(net2, seed, tower)

    after_inject = trace["accessibility"][0]
    print(f"  accessibility after failure   {RED}{after_inject:5.1f}%{R}\n")

    for st in trace["steps"]:
        if st.get("status") == "settled":
            print(f"  {DIM}no edge is overloaded — the chain settles on its own{R}")
            continue
        d = st["domino"]
        col = GRN if st["status"] == "CASCADE STOPPED" else AMB
        print(f"{BOLD}  DOMINO {st['step']}{R}  {d['label']}"
              f"   score {BOLD}{d['score']:.3f}{R}   load {d['load_ratio']}×capacity")
        for k, v in d["components"].items():
            print(f"      {DIM}{k:<22}{R} {bar(v)} {v:.2f}  {DIM}× {SCORE_WEIGHTS[k]}{R}")
        print(f"      {DIM}interventions tested:{R}")
        for o in st["interventions"]:
            mark = f"{GRN}HOLDS{R}" if o["holds"] else f"{DIM}fails{R}"
            win = f"{o['window_min']} min" if o["window_min"] else "capital"
            print(f"        [{o['clock']:<7} {win:>8}]  {o['label']:<38} "
                  f"acc {o['accessibility']:5.1f}%   {mark}")
        print(f"      {col}{st['status']}{R}"
              f"   accessibility {st.get('accessibility_after', '—')}%\n")

    h = trace["containment_horizon"]
    print(f"{BOLD}  CONTAINMENT HORIZON  {h} step{'s' if h != 1 else ''}{R}"
          f"   {DIM}(the last step at which an available action still held the chain){R}\n")

    if trace["dark_zones"]:
        print(f"{VIO}{BOLD}  DARK ZONES{R} {DIM}(physical AND communication isolation){R}")
        print(f"      {DIM}{'zone':<20}{'pop':>7}  {'T_phys':>7}{'T_comm':>8}{'T_dark':>8}{R}")
        for z in trace["dark_zones"]:
            print(f"      {z['label']:<20}{z['population']:>7,}  "
                  f"{z['t_phys_min']:>5} m{z['t_comm_min']:>6} m{VIO}{z['t_dark_min']:>6} m{R}")
        first = trace["dark_zones"][0]
        print(f"\n      {BOLD}dispatch first: {first['label']} in {first['t_dark_min']} minutes{R}\n")
    else:
        print(f"  {DIM}no dark zones under this scenario{R}\n")

    # ---- machine-readable output for the dashboard
    out = dict(
        meta=dict(nodes=len(net.nodes), edges=len(net.edges), population=pop,
                  threshold_km=SERVICE_THRESHOLD_KM, minutes_per_step=MINUTES_PER_STEP,
                  weights=SCORE_WEIGHTS, seed=seed, seed_label=seed_label,
                  tower=tower, tower_label=net.nodes[tower].label if tower else None),
        graph=dict(
            nodes=[dict(id=n.id, x=n.x, y=n.y, kind=n.kind, population=n.population,
                        label=n.label) for n in net.nodes.values()],
            edges=[dict(id=e.id, u=e.u, v=e.v, km=e.length_km, capacity=e.capacity,
                        kind=e.kind, label=e.label, alive=e.alive)
                   for e in net.edges.values()]),
        trace=trace)
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{DIM}  wrote {p}{R}\n")
    return out


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
