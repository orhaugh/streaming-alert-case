"""The bounded dataset's facts, taken from either of two independent sources.

from_events() derives them from the raw event file with the reference rules
(reference.py), reading nothing clink or Relate produced. from_graph() reads
them from the published Relate store with Cypher, computing nothing itself.
The claim checker and the store checks judge the same rules against both, so
a claim is only supported when the original events and the graph agree.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from . import reference
from .events import load_events, sha256_of
from .graph import Graph


@dataclass
class Facts:
    source: str
    transfers: dict[str, dict]                 # transfer id -> src, dst, amount_minor, ts, device
    indicators: dict[str, dict]                # indicator id -> account, window, senders, transfers, total, transfer_ids
    links: dict[str, dict]                     # onward link id -> in_id, out_id, account, gap_ms
    investigation: dict[str, dict]             # indicator id -> onward_depth, terminal/route accounts, shared devices
    device_senders: dict[str, set[str]] = field(default_factory=dict)  # device -> accounts that sent from it
    run: dict | None = None

    @property
    def accounts(self) -> set[str]:
        return {a for t in self.transfers.values() for a in (t["src"], t["dst"])}

    @property
    def devices(self) -> set[str]:
        return {t["device"] for t in self.transfers.values()}

    def links_from(self, transfer_id: str) -> list[dict]:
        return [link for link in self.links.values() if link["in_id"] == transfer_id]


def _device_senders(transfers: dict[str, dict]) -> dict[str, set[str]]:
    senders: dict[str, set[str]] = defaultdict(set)
    for t in transfers.values():
        senders[t["device"]].add(t["src"])
    return dict(senders)


def _strip(record: dict, *names: str) -> dict:
    return {k: v for k, v in record.items() if k not in names}


def from_events(path: str | Path = "data/events.ndjson") -> Facts:
    events = load_events(path)
    indicators = reference.fan_in(events)
    pairs = reference.onward(events)
    transfers = {e["transfer_id"]: _strip(e, "transfer_id") for e in events}
    return Facts(
        source="events",
        transfers=transfers,
        indicators={i["id"]: _strip(i, "id") for i in indicators},
        links={p["id"]: _strip(p, "id") for p in pairs},
        investigation={r["indicator"]: _strip(r, "indicator") for r in reference.investigate(events, indicators, pairs)},
        device_senders=_device_senders(transfers),
        run={"dataset_sha256": sha256_of(path), "dataset_events": len(events)},
    )


def from_graph(graph: Graph) -> Facts:
    transfers = {t["transfer_id"]: _strip(t, "transfer_id") for t in graph.transfers()}
    runs = graph.run_records()
    return Facts(
        source="graph",
        transfers=transfers,
        indicators={i["id"]: _strip(i, "id") for i in graph.indicators()},
        links={p["id"]: _strip(p, "id") for p in graph.onward_links()},
        investigation={r["indicator"]: _strip(r, "indicator") for r in graph.investigation()},
        device_senders=_device_senders(transfers),
        run=runs[0]["run"] if len(runs) == 1 else None,
    )
