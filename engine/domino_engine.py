"""
DOMINO — Explainable Infrastructure Cascade & Intervention Engine
Working prototype.

What is real here
-----------------
* A real weighted road graph with capacities and travel times.
* Real shortest-path accessibility (Dijkstra) against a 5 km service threshold.
* Real all-or-nothing traffic assignment, recomputed after every failure.
* A real four-component domino score, each component computed from the graph.
* Real counterfactual intervention testing: apply an action, re-run, compare.
* A real containment horizon, found by running the loop to exhaustion.
* Real dark-zone detection as (physical AND communication) isolation,
  with T_dark = max(T_phys, T_comm).

What is synthetic here
----------------------
The corridor itself. The sandbox this was built in cannot reach the Overpass
API, so `load_corridor()` generates a network shaped like the Udupi-Manipal
corridor instead of downloading one. Swapping in a real extract means replacing
that one function; nothing downstream changes. See `load_osm()` for the shape
of that call.
"""
from __future__ import annotations
import json, math, heapq
from dataclasses import dataclass, field, asdict

SERVICE_THRESHOLD_KM = 5.0      # same accessibility proxy the study used
TOWER_RADIUS_KM      = 2.6
MINUTES_PER_STEP     = 25       # stated assumption: how long one domino takes to fall
OVERLOAD_RATIO       = 1.00     # flow / capacity above which an edge fails

SCORE_WEIGHTS = dict(load_stress=0.35, network_dependency=0.25,
                     emergency_impact=0.25, population_exposure=0.15)


# ────────────────────────────────────────────────────────────── data model
@dataclass
class Node:
    id: str
    x: float
    y: float
    kind: str = "junction"        # junction | hospital | fire | tower
    population: int = 0
    label: str = ""

@dataclass
class Edge:
    id: str
    u: str
    v: str
    length_km: float
    capacity: int
    kind: str = "road"            # road | bridge
    label: str = ""
    alive: bool = True
    cap_multiplier: float = 1.0
    baseline_flow: float = 0.0

    @property
    def effective_capacity(self) -> float:
        return self.capacity * self.cap_multiplier

@dataclass
class Network:
    nodes: dict = field(default_factory=dict)
    edges: dict = field(default_factory=dict)
    dead_towers: set = field(default_factory=set)

    def adj(self):
        a = {n: [] for n in self.nodes}
        for e in self.edges.values():
            if not e.alive:
                continue
            a[e.u].append((e.v, e.length_km, e.id))
            a[e.v].append((e.u, e.length_km, e.id))
        return a

    def services(self):
        return [n.id for n in self.nodes.values() if n.kind in ("hospital", "fire")]

    def populated(self):
        return [n.id for n in self.nodes.values() if n.population > 0]

    def live_towers(self):
        return [n.id for n in self.nodes.values()
                if n.kind == "tower" and n.id not in self.dead_towers]

    def clone_state(self):
        return ({eid: (e.alive, e.cap_multiplier) for eid, e in self.edges.items()},
                set(self.dead_towers))

    def restore_state(self, st):
        edges, towers = st
        for eid, (alive, mult) in edges.items():
            self.edges[eid].alive = alive
            self.edges[eid].cap_multiplier = mult
        self.dead_towers = set(towers)


# ────────────────────────────────────────────────────────────── routing
def dijkstra(adj, source):
    """returns (dist_km, prev_edge) from source over live edges"""
    dist = {source: 0.0}
    prev = {}
    pq = [(0.0, source)]
    seen = set()
    while pq:
        d, n = heapq.heappop(pq)
        if n in seen:
            continue
        seen.add(n)
        for m, w, eid in adj.get(n, []):
            nd = d + w
            if nd < dist.get(m, math.inf):
                dist[m] = nd
                prev[m] = (n, eid)
                heapq.heappush(pq, (nd, m))
    return dist, prev


def path_edges(prev, target):
    out, cur = [], target
    while cur in prev:
        p, eid = prev[cur]
        out.append(eid)
        cur = p
    return out[::-1]


_CACHE = {}

def _state_key(net):
    return (tuple(sorted((eid, e.alive, round(e.cap_multiplier, 3))
                         for eid, e in net.edges.items())),
            tuple(sorted(net.dead_towers)))

def assign(net: Network):
    k = _state_key(net)
    hit = _CACHE.get(k)
    if hit is not None:
        return hit
    out = _assign(net)
    if len(_CACHE) > 60000:
        _CACHE.clear()
    _CACHE[k] = out
    return out


def _assign(net: Network):
    """
    All-or-nothing assignment over two trip purposes, because a fire station is
    not a substitute for a hospital:

      * medical trips  (70%) must reach a hospital
      * rescue trips   (30%) reach the nearest fire station

    Both are routed on the shortest surviving path, so a failure anywhere on the
    corridor redistributes real load onto the alternatives. Returns per-edge
    flow, per-node distance to the nearest critical service, the edges each
    ward depends on, and each edge's share of emergency routing.
    """
    adj = net.adj()
    flow = {eid: 0.0 for eid in net.edges}
    emergency_edges = {eid: 0.0 for eid in net.edges}
    node_dist, node_route = {}, {}

    hospitals = [n.id for n in net.nodes.values() if n.kind == "hospital"]
    stations  = [n.id for n in net.nodes.values() if n.kind == "fire"]
    trees = {s: dijkstra(adj, s) for s in hospitals + stations}

    total_pop = sum(net.nodes[n].population for n in net.populated()) or 1

    def nearest(n, group):
        best, who = math.inf, None
        for s in group:
            d = trees[s][0].get(n, math.inf)
            if d < best:
                best, who = d, s
        return best, who

    for n in net.populated():
        pop = net.nodes[n].population
        share = pop / total_pop
        routes = []

        dh, h = nearest(n, hospitals)
        if h is not None and dh < math.inf:
            eids = path_edges(trees[h][1], n)
            routes.append(eids)
            for eid in eids:
                flow[eid] += pop * 0.12 * 0.70
                emergency_edges[eid] += share

        df, f = nearest(n, stations)
        if f is not None and df < math.inf:
            eids = path_edges(trees[f][1], n)
            routes.append(eids)
            for eid in eids:
                flow[eid] += pop * 0.12 * 0.30
                emergency_edges[eid] += share * 0.5

        node_dist[n] = min(dh, df)
        node_route[n] = sorted({e for r in routes for e in r})
    return flow, node_dist, node_route, emergency_edges


def accessibility(net: Network):
    """share of population within the service threshold"""
    _, node_dist, _, _ = assign(net)
    tot = cov = 0
    for n in net.populated():
        p = net.nodes[n].population
        tot += p
        if node_dist.get(n, math.inf) <= SERVICE_THRESHOLD_KM:
            cov += p
    return (cov / tot * 100.0) if tot else 0.0, node_dist


def betweenness(net: Network):
    """edge betweenness over service-to-population routes, normalised 0..1"""
    _, _, node_route, _ = assign(net)
    cnt = {eid: 0 for eid in net.edges}
    for eids in node_route.values():
        for eid in eids:
            cnt[eid] += 1
    mx = max(cnt.values()) or 1
    return {k: v / mx for k, v in cnt.items()}


# ────────────────────────────────────────────────────────────── scoring
def score_edge(net, eid, flow, base_flow, betw, emergency_edges, node_route):
    e = net.edges[eid]
    cap = e.effective_capacity or 1.0
    ratio = flow.get(eid, 0.0) / cap
    load_stress = min(1.0, max(0.0, (ratio - 0.55) / 0.85))

    dep = betw.get(eid, 0.0)
    emerg = min(1.0, emergency_edges.get(eid, 0.0) * 3.0)

    total_pop = sum(net.nodes[n].population for n in net.populated()) or 1
    exposed = sum(net.nodes[n].population for n, eids in node_route.items() if eid in eids)
    pop_exposure = exposed / total_pop

    parts = dict(load_stress=load_stress, network_dependency=dep,
                 emergency_impact=emerg, population_exposure=pop_exposure)
    total = sum(SCORE_WEIGHTS[k] * v for k, v in parts.items())
    return round(total, 3), {k: round(v, 3) for k, v in parts.items()}, round(ratio, 2)


def find_next_domino(net, base_flow):
    """the overloaded edge with the highest explainable score"""
    flow, _, node_route, emergency_edges = assign(net)
    betw = betweenness(net)
    best = None
    for eid, e in net.edges.items():
        if not e.alive:
            continue
        s, parts, ratio = score_edge(net, eid, flow, base_flow, betw,
                                     emergency_edges, node_route)
        if ratio > OVERLOAD_RATIO:
            cand = dict(edge=eid, label=e.label or eid, score=s,
                        components=parts, load_ratio=ratio)
            if best is None or s > best["score"]:
                best = cand
    return best, flow


# ────────────────────────────────────────────────────────────── interventions
def _contraflow(n, eid, m=1.30):
    n.edges[eid].cap_multiplier = m
def _open(n, oid):
    n.edges[oid].alive = True

def intervention_catalogue(net, eid):
    """
    Actions the engine is allowed to try on this domino. Two clocks: respond
    actions are available in minutes on an operations budget, harden actions
    take months on a capital budget.
    """
    e = net.edges[eid]
    closed = [oid for oid, o in net.edges.items() if o.kind == "service" and not o.alive]
    out = [
        dict(id=f"respond:contraflow:{eid}", clock="respond", window_min=90,
             label=f"Contraflow on {e.label or eid}",
             apply=lambda n, eid=eid: _contraflow(n, eid, 1.30)),
        dict(id=f"harden:reinforce:{eid}", clock="harden", window_min=None,
             label=f"Reinforce and widen {e.label or eid}",
             apply=lambda n, eid=eid: _contraflow(n, eid, 1.75)),
    ]
    for oid in closed:
        o = net.edges[oid]
        out.append(dict(id=f"respond:open:{oid}", clock="respond", window_min=60,
                        label=f"Reopen {o.label or oid}",
                        apply=lambda n, oid=oid: _open(n, oid)))
        out.append(dict(id=f"respond:package:{oid}+{eid}", clock="respond", window_min=90,
                        label=f"Reopen {o.label or oid} + contraflow on {e.label or eid}",
                        apply=lambda n, oid=oid, eid=eid: (_open(n, oid),
                                                           _contraflow(n, eid, 1.30))))
    return out


def test_interventions(net, base_access):
    """
    Counterfactual: apply each candidate action, re-run assignment, and check
    whether the chain is held (nothing still overloaded) without losing
    accessibility. Returns the best action that holds, or None.
    """
    results = []
    held = None
    dom, _ = find_next_domino(net, None)
    if dom is None:
        return None, []
    for act in intervention_catalogue(net, dom["edge"]):
        st = net.clone_state()
        act["apply"](net)
        acc, _ = accessibility(net)
        nxt, _ = find_next_domino(net, None)
        net.restore_state(st)
        holds = nxt is None and acc >= base_access - 2.0
        results.append(dict(id=act["id"], label=act["label"], clock=act["clock"],
                            window_min=act["window_min"],
                            accessibility=round(acc, 1), holds=holds))
        if holds and held is None:
            held = results[-1]
    return held, results


# ────────────────────────────────────────────────────────────── dark zones
def dark_zones(net: Network, step_when_isolated: dict, tower_fail_step: int):
    adj = net.adj()
    _, node_dist, _, _ = assign(net)
    live = net.live_towers()
    zones = []
    for n in net.populated():
        node = net.nodes[n]
        phys = node_dist.get(n, math.inf) > SERVICE_THRESHOLD_KM
        covered = any(math.dist((node.x, node.y),
                                (net.nodes[t].x, net.nodes[t].y)) <= TOWER_RADIUS_KM
                      for t in live)
        comm = not covered
        if phys and comm:                      # AND, never OR
            t_phys = step_when_isolated.get(n, 0) * MINUTES_PER_STEP
            t_comm = tower_fail_step * MINUTES_PER_STEP
            t_dark = max(t_phys, t_comm)       # both must hold
            zones.append(dict(node=n, label=node.label or n,
                              population=node.population,
                              t_phys_min=t_phys, t_comm_min=t_comm,
                              t_dark_min=t_dark,
                              priority=round(node.population * 1.0 / 1000, 2)))
    zones.sort(key=lambda z: (z["t_dark_min"], -z["population"]))
    return zones


# ────────────────────────────────────────────────────────────── the loop
def snapshot(net: Network):
    """per-edge state and per-ward service distance, for replay"""
    flow, node_dist, _, _ = assign(net)
    return dict(
        edges={eid: dict(alive=e.alive,
                         ratio=round(flow.get(eid, 0.0) / (e.effective_capacity or 1), 2),
                         boosted=round(e.cap_multiplier, 2))
               for eid, e in net.edges.items()},
        wards={n: round(node_dist.get(n, 99.0), 2) for n in net.populated()},
        dead_towers=sorted(net.dead_towers))


def run_cascade(net: Network, seed_edge: str, tower_out: str | None = None,
                max_steps: int = 6):
    trace = {"seed": seed_edge, "steps": [], "accessibility": [], "frames": []}

    base_access, _ = accessibility(net)
    base_flow, base_dist, _, _ = assign(net)
    trace["baseline_accessibility"] = round(base_access, 1)
    trace["frames"].append(dict(phase="baseline", accessibility=round(base_access, 1),
                                **snapshot(net)))

    net.edges[seed_edge].alive = False
    tower_fail_step = 0
    if tower_out:
        net.dead_towers.add(tower_out)

    acc, node_dist = accessibility(net)
    trace["accessibility"].append(round(acc, 1))
    trace["frames"].append(dict(phase="failure", accessibility=round(acc, 1),
                                **snapshot(net)))
    step_when_isolated = {n: 0 for n in net.populated()
                          if node_dist.get(n, math.inf) > SERVICE_THRESHOLD_KM}

    horizon = -1
    stopped = False
    for step in range(1, max_steps + 1):
        dom, flow = find_next_domino(net, base_flow)
        if dom is None:
            trace["steps"].append(dict(step=step, status="settled"))
            stopped = True
            break

        held, options = test_interventions(net, base_access)
        rec = dict(step=step, domino=dom, interventions=options)

        if held:
            horizon = step
            rec["status"] = "CASCADE STOPPED"
            rec["action"] = held
            st = net.clone_state()
            for act in intervention_catalogue(net, dom["edge"]):
                if act["id"] == held["id"]:
                    act["apply"](net)
            acc, _ = accessibility(net)
            rec["accessibility_after"] = round(acc, 1)
            trace["steps"].append(rec)
            trace["accessibility"].append(round(acc, 1))
            trace["frames"].append(dict(phase="stopped", step=step,
                                        accessibility=round(acc, 1), **snapshot(net)))
            net.restore_state(st)
            stopped = True
            break

        rec["status"] = "CASCADE CONTINUES"
        net.edges[dom["edge"]].alive = False      # gridlocked: unusable, not destroyed
        acc, node_dist = accessibility(net)
        rec["accessibility_after"] = round(acc, 1)
        for n in net.populated():
            if node_dist.get(n, math.inf) > SERVICE_THRESHOLD_KM and n not in step_when_isolated:
                step_when_isolated[n] = step
        trace["accessibility"].append(round(acc, 1))
        trace["frames"].append(dict(phase="domino", step=step,
                                    accessibility=round(acc, 1), **snapshot(net)))
        trace["steps"].append(rec)

    trace["containment_horizon"] = horizon if horizon >= 0 else 0
    trace["stopped"] = stopped
    trace["dark_zones"] = dark_zones(net, step_when_isolated, tower_fail_step)
    return trace


# ────────────────────────────────────────────────────────────── corridor
def load_corridor() -> Network:
    """
    Synthetic corridor shaped like Udupi-Manipal: a coastal arterial, an inland
    arterial, a river with two crossings, a referral hospital and a fire station
    on the inland side, three towers, and population spread across the wards.
    Coordinates are in kilometres on a local grid.
    """
    N, E = {}, {}
    def n(i, x, y, kind="junction", pop=0, label=""):
        N[i] = Node(i, x, y, kind, pop, label)
    def e(i, u, v, cap, kind="road", label=""):
        d = math.dist((N[u].x, N[u].y), (N[v].x, N[v].y))
        E[i] = Edge(i, u, v, round(d, 2), cap, kind, label or i)

    # coastal arterial, west of the river
    n("C1", 0.0, 0.0, pop=5200, label="Malpe ward")
    n("C2", 0.4, 2.6, pop=7400, label="Kadiyali ward")
    n("C3", 0.9, 5.1, pop=6100, label="Kalsanka ward")
    n("C4", 1.4, 7.6, pop=4300, label="Santhekatte ward")
    # inland arterial, east of the river
    n("I1", 4.6, 0.6, pop=3100, label="Perampalli ward")
    n("I2", 4.9, 3.0, pop=8200, label="Manipal south")
    n("I3", 5.2, 5.4, pop=9100, label="Manipal centre")
    n("I4", 5.6, 7.8, pop=3800, label="Eshwar nagar")
    # the three river crossings meet the arterials here
    n("X1", 2.6, 0.9); n("X2", 2.8, 3.2); n("X3", 3.0, 6.0)
    # critical services
    n("H1", 6.5, 4.2, kind="hospital", label="Referral hospital")
    n("F1", 1.9, 6.2, kind="fire",     label="Fire station")
    # communication towers
    n("T1", 1.2, 2.0, kind="tower", label="Tower T-04")
    n("T2", 4.5, 4.4, kind="tower", label="Tower T-11")
    n("T3", 3.4, 7.7, kind="tower", label="Tower T-19")
    n("T4", 0.6, 6.5, kind="tower", label="Tower T-06")
    n("T5", 3.8, 1.4, kind="tower", label="Tower T-02")

    e("N1",  "C1", "C2", 0, label="Coastal road N1")
    e("N2",  "C2", "C3", 0, label="Coastal road N2")
    e("N3",  "C3", "C4", 0, label="Coastal road N3")
    e("R11", "I1", "I2", 0, label="Inland road R11")
    e("R24", "I2", "I3", 0, label="Inland road R24")
    e("R31", "I3", "I4", 0, label="Inland road R31")
    e("A1",  "C1", "X1", 0, label="Approach A1")
    e("A2",  "C2", "X2", 0, label="Approach A2")
    e("A3",  "C3", "X3", 0, label="Approach A3")
    e("B03", "X1", "I1", 0, kind="bridge", label="Bridge B03")
    e("B07", "X2", "I2", 0, kind="bridge", label="Bridge B07")
    e("B12", "X3", "I3", 0, kind="bridge", label="Bridge B12")
    e("A4",  "C4", "I4", 0, label="North link A4")
    e("HS",  "I3", "H1", 0, label="Hospital approach")
    e("HS2", "I2", "H1", 0, label="Hospital south approach")
    e("FS",  "C3", "F1", 0, label="Fire station approach")
    e("FS2", "X3", "F1", 0, label="Fire east approach")

    net = Network(N, E)
    # a closed service road, available to the engine only as an intervention
    # a decommissioned crossing the city still owns: closed, but openable
    net.edges["SR"] = Edge("SR", "X2", "I3", 3.3, 1800, kind="service",
                           label="Old crossing SR-2", alive=False)
    calibrate_capacity(net)
    return net


def calibrate_capacity(net: Network, target_utilisation: float = 0.55,
                       floor: int = 500):
    """
    Size every road to the demand it actually carries when nothing has failed,
    so that the intact network runs at `target_utilisation` of capacity. This
    replaces an arbitrary capacity guess with one derived from the graph, and it
    means a load ratio above 1.0 during a cascade represents roughly a doubling
    of baseline demand on that road.
    """
    flow, _, _, _ = assign(net)
    for eid, e in net.edges.items():
        if e.kind == "service" or not e.alive:
            e.baseline_flow = 0.0          # mothballed assets keep their design capacity
            continue
        base = flow.get(eid, 0.0)
        e.capacity = max(floor, int(math.ceil(base / target_utilisation)))
        e.baseline_flow = round(base, 1)
    return net


def load_osm(bbox, cache=None):  # pragma: no cover - documented extension point
    """
    Drop-in replacement for load_corridor(). Query Overpass for
    highway=motorway|trunk|primary|secondary|tertiary inside `bbox`, map each
    way to an Edge with capacity from its lane count, snap amenity=hospital,
    amenity=fire_station and man_made=mast to the nearest node, and attach
    population from a WorldPop raster sampled per node catchment.
    Everything downstream of this function is unchanged.
    """
    raise NotImplementedError("network access is disabled in this sandbox")
