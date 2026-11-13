"""Read-only access to the published Relate store.

Everything here reads the graph through Cypher on a connection opened
read-only. It imports Relate and nothing from clink.
"""

from __future__ import annotations

from pathlib import Path

import relate

STORE = Path("store/case.rl")

# The investigation's relationship questions. p covers the onward links only,
# so length(p) counts them.
ONWARD_REACH = """
MATCH (i:Indicator {kind: 'fan_in'})-[:CONTRIBUTING]->(c:Transfer)
MATCH p = (c)-[:PASSED_ON*1..20]->(t:Transfer)
MATCH (t)-[:TO]->(reached:Account)
RETURN i.id AS indicator, max(length(p)) AS onward_depth, collect(DISTINCT reached.id) AS reached
"""
CAME_TO_REST = """
MATCH (i:Indicator {kind: 'fan_in'})-[:CONTRIBUTING]->(:Transfer)-[:PASSED_ON*1..20]->(t:Transfer)-[:TO]->(rest:Account)
WHERE NOT (t)-[:PASSED_ON]->()
RETURN i.id AS indicator, collect(DISTINCT rest.id) AS terminal
"""
SHARED_DEVICES = """
MATCH (i:Indicator {kind: 'fan_in'})-[:CONTRIBUTING]->(:Transfer)-[:PASSED_ON*0..20]->(:Transfer)-[:TO]->(on_route:Account)
WITH DISTINCT i, on_route
MATCH (on_route)-[:SENT]->(:Transfer)-[:FROM_DEVICE]->(d:Device)
WITH i, d, collect(DISTINCT on_route.id) AS accounts
WHERE size(accounts) >= 2
RETURN i.id AS indicator, d.id AS device, accounts
"""
LONGEST_ROUTES = """
MATCH (i:Indicator {id: $indicator})-[:CONTRIBUTING]->(c:Transfer)
MATCH p = (c)-[:PASSED_ON*1..20]->(t:Transfer)
WHERE NOT (t)-[:PASSED_ON]->()
RETURN [n IN nodes(p) | n.id] AS transfers, [r IN relationships(p) | r.id] AS links
ORDER BY length(p) DESC, transfers
"""


class Graph:
    """One read-only handle on a store. Relate allows one handle per store
    per process, so open it once and close it when done."""

    def __init__(self, path: str | Path = STORE) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"no Relate store at {self.path}")
        self.conn = relate.connect(str(self.path), read_only=True)

    def __enter__(self) -> "Graph":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def rows(self, cypher: str, **params) -> list[dict]:
        return [dict(r) for r in self.conn.execute(cypher, params)]

    def run_records(self) -> list[dict]:
        return self.rows("MATCH (r:Run) RETURN properties(r) AS run")

    def transfers(self) -> list[dict]:
        return self.rows("""
            MATCH (s:Account)-[:SENT]->(t:Transfer)-[:TO]->(d:Account)
            MATCH (t)-[:FROM_DEVICE]->(v:Device)
            RETURN t.id AS transfer_id, s.id AS src, d.id AS dst, t.amount_minor AS amount_minor,
                   t.ts AS ts, v.id AS device""")

    def indicators(self) -> list[dict]:
        found = self.rows("""
            MATCH (i:Indicator {kind: 'fan_in'})-[:ABOUT]->(a:Account)
            MATCH (i)-[:CONTRIBUTING]->(t:Transfer)
            RETURN i.id AS id, a.id AS account, i.window_start AS window_start, i.window_end AS window_end,
                   i.senders AS senders, i.transfers AS transfers, i.total_minor AS total_minor,
                   collect(t.id) AS transfer_ids""")
        for i in found:
            i["transfer_ids"] = sorted(i["transfer_ids"])
        return sorted(found, key=lambda i: i["id"])

    def onward_links(self) -> list[dict]:
        found = self.rows("""
            MATCH (c:Transfer)-[p:PASSED_ON]->(d:Transfer)
            MATCH (c)-[:TO]->(a:Account)-[:SENT]->(d)
            RETURN p.id AS id, c.id AS in_id, d.id AS out_id, a.id AS account, p.gap_ms AS gap_ms""")
        return sorted(found, key=lambda p: p["id"])

    def investigation(self) -> list[dict]:
        """Per fan-in indicator: onward depth, the accounts where its candidate paths end, path accounts
        and the devices two or more route accounts sent from, all by Cypher."""
        result = {i["id"]: {"indicator": i["id"], "account": i["account"], "onward_depth": 0,
                            "terminal_accounts": [], "route_accounts": [i["account"]], "shared_devices": {}}
                  for i in self.indicators()}
        for r in self.rows(ONWARD_REACH):
            entry = result[r["indicator"]]
            entry["onward_depth"] = r["onward_depth"]
            entry["route_accounts"] = sorted(set(r["reached"]) | {entry["account"]})
        for r in self.rows(CAME_TO_REST):
            result[r["indicator"]]["terminal_accounts"] = sorted(r["terminal"])
        for r in self.rows(SHARED_DEVICES):
            result[r["indicator"]]["shared_devices"][r["device"]] = sorted(r["accounts"])
        for entry in result.values():
            entry["shared_devices"] = dict(sorted(entry["shared_devices"].items()))
        return sorted(result.values(), key=lambda r: r["indicator"])

    def routes(self, indicator: str) -> list[dict]:
        """Every onward route from the indicator's contributing transfers to a
        transfer with no onward link, longest first."""
        return self.rows(LONGEST_ROUTES, indicator=indicator)
