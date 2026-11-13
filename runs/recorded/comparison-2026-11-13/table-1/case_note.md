# Case note: table arm, run 1

Agent output, recorded run of 2026-11-13T18:24:11+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: the bounded replay run:72cf0e4b91a3 (dataset sha256 72cf0e4b…c880, 55 events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms event-time window, onward max gap 1,800,000 ms). It holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000. It counts 6 distinct senders and 6 transfers totalling 357000 minor units: T0002, T0003, T0006, T0010, T0011 and T0012. The amounts differ (38000 to 89000).  
  Claims: I1 (supported), E2 (supported), E3 (supported), E6 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000. It counts 6 distinct senders and 6 transfers totalling 15000 minor units: T0035 to T0040, each exactly 2500.  
  Claims: I2 (supported), E35 (supported), E36 (supported), E37 (supported), E38 (supported), E39 (supported), E40 (supported)
- **F4** Onward links for A-9278: every one of its 6 contributing transfers is linked to an outgoing transfer. T0002, T0003 and T0006 link to T0007 (A-9278→A-5092, 138000), then T0008 (A-5092→A-2897, 135000), then T0009 (A-2897→A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278→A-5092, 210000), then T0015 (A-5092→A-2897, 206000), then T0016 (A-2897→A-4989, 202000). The longest chain has 3 onward links. Both routes end at A-4989: neither T0009 nor T0016 is passed on. The accounts on the routes are A-9278, A-5092, A-2897 and A-4989.  
  Claims: P1 (supported), P2 (supported), R1 (supported), E7 (supported), E8 (supported), E9 (supported), E14 (supported), E15 (supported), E16 (supported), AB1 (supported), AB2 (supported)
- **F5** Onward links for A-9895: only T0038, T0039 and T0040 link onward, all to T0041 (A-9895→A-1415, 14000). T0041 is not passed on. T0035, T0036 and T0037 have no onward link, so for them the record ends at A-9895. The longest chain has 1 onward link. The end points are A-1415, plus A-9895 for the three unlinked transfers. The accounts on the routes are A-9895 and A-1415.  
  Claims: P3 (supported), R2 (unsupported), E41 (supported), AB3 (supported), AB4 (supported)
- **F6** Shared devices, A-9278 routes: device D-568 sent all six outgoing transfers, from three different route accounts: A-9278 (T0007, T0014), A-5092 (T0008, T0015) and A-2897 (T0009, T0016). The fourth route account, A-4989, sends nothing in this dataset.  
  Claims: S1 (supported), E7 (supported), E8 (supported), E9 (supported), E14 (supported), E15 (supported), E16 (supported)
- **F7** Shared devices, A-9895 routes: no device was used by two or more route accounts. A-9895 sent from D-699 (T0041). A-1415 sent from D-785 (T0055, to A-9514, 90000). T0055 is not recorded as an onward link from T0041, since it comes 11,700,000 ms after T0041, well past the 1,800,000 ms limit.  
  Claims: AB5 (supported), E41 (supported), E55 (supported), AB4 (supported)
- **F8** What tells the two alerts apart: both show 6 senders and 6 transfers in one hour. But A-9278 has (a) all of its incoming transfers linked onward, (b) a chain of 3 hops in two separate waves through the same accounts A-9278 → A-5092 → A-2897 → A-4989, (c) each hop forwarding a little less than the amount before it (141500 in, then 138000 → 135000 → 132000; 215500 in, then 210000 → 206000 → 202000), each within 355,000 ms or less of the last inflow of its wave, and (d) one device, D-568, behind every outgoing transfer from three different route accounts. A-9895 instead has six identical small credits, only half of them linked onward, a single 1-hop link to A-1415, and no shared device on its route. The equal indicator values hide these differences in structure.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (unsupported), S1 (supported), AB5 (supported), P1 (supported), P2 (supported), P3 (supported)
- **F9** Other accounts with several incoming senders did not reach the threshold and have no fan-in indicator: A-9862 (4 senders: T0021, T0024, T0025, T0026) and A-1823 (3 senders, 6 transfers). A-4989, where A-9278's routes end, also has no indicator.  
  Claims: AB6 (supported), AB7 (supported), AB8 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** The A-9278 pattern fits a pass-through or layering route under shared control: money from several senders is collected and forwarded in a few minutes, across three hops, from one device, ending at A-4989. The data does not establish control, ownership or fraud. A shared device is only a recorded relationship.  
  References: F4, F6, F8, S1
- **H2** The A-9895 pattern (six identical 2500 payments from different senders, with one 14000 payment out) may be ordinary collection, such as a group payment or a split bill. It is weaker evidence of layering than A-9278. This is an interpretation, not a finding.  
  References: F3, F5, F7
- **H3** The small drop at each A-9278 hop (about 3000–4000 per hop) could be fees or skimming. The data does not record why.  
  References: F4

## Unresolved questions

- **U1** Where did T0041's funding come from? It pays 14000, but its three linked credits (T0038–T0040) total only 7500. Onward links are matched on time only and do not show which money was actually forwarded.  
  References: P3, E41
- **U2** What happens to the money at A-4989 and A-1415 outside this bounded replay? A-4989 sends nothing in the dataset. A-1415's later T0055 (90000 to A-9514) is too late to be linked, and its source is not recorded.  
  References: AB2, AB4, E55
- **U3** Who controls device D-568, and do A-9278, A-5092 and A-2897 share one owner? The data records device use only, not identity.  
  References: S1

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E2 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| E3 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| E6 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| E7 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| E8 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| E9 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| E10 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| E11 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| E12 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| E14 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| E15 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| E16 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| E35 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| E36 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| E37 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| E38 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| E39 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| E40 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| E41 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| E55 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415", "A-9895"], route_accounts=["A-9895", "A-1415"] | unsupported: terminal_accounts are ['A-1415'], not ['A-1415', 'A-9895'] |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| AB1 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| AB2 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| AB3 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| AB4 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| AB5 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| AB6 | absence | kind="no_fan_in_alert_for_account", subject="A-9862" | supported |
| AB7 | absence | kind="no_fan_in_alert_for_account", subject="A-1823" | supported |
| AB8 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 40 of 41 claims supported; reference validity 1.0 (63 of 63 distinct ids resolve); 5 queries (0 failed), 3 model requests, 19051 input tokens (cache included) and 7322 output tokens, 87.4 s.
