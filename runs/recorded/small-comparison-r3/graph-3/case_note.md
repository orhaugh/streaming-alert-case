# Case note: graph arm, run 3

Agent output, recorded run of 2026-11-13T18:46:32+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f1** Scope: this bounded replay (run run:72cf0e4b91a3; 55 dataset events; 3 of 3 jobs completed; clink exit status 0; not cancelled; at least 5 distinct senders per 1-hour window for fan-in; onward gap of at most 1,800,000 ms) contains 55 transfers, 48 accounts, 35 devices, 14 onward links and exactly 2 fan-in alerts.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000 to 1794304800000 ms, 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002, T0003, T0006, T0010, T0011, T0012.  
  Claims: i1 (supported), e12 (supported), e13 (supported)
- **f3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000 to 1794322800000 ms, 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035 to T0040, each 2500.  
  Claims: i2 (supported), e9 (supported), e10 (supported), e11 (supported)
- **f4** Onward reach of the A-9278 alert: all 6 contributing transfers are passed on. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), which links to T0008 (A-5092 to A-2897) and then to T0009 (A-2897 to A-4989). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 and T0016 along the same accounts. The longest chain has 3 onward links. The route accounts are A-9278, A-5092, A-2897 and A-4989. The money comes to rest only at A-4989: T0009 and T0016 are not passed on.  
  Claims: r1 (supported), p1 (supported), p2 (supported), p3 (supported), p4 (supported), p5 (supported), p6 (supported), e1 (supported), e2 (supported), e3 (supported), e4 (supported), e5 (supported), e6 (supported), x6 (supported), x7 (supported)
- **f5** Onward reach of the A-9895 alert: only T0038, T0039 and T0040 are passed on, all three into T0041 (A-9895 to A-1415, 14000). T0035, T0036 and T0037 are not passed on. The longest chain has 1 onward link. The route accounts are A-9895 and A-1415, and the money comes to rest at A-1415 because T0041 is not passed on.  
  Claims: r2 (supported), p7 (supported), p8 (supported), p9 (supported), e7 (supported), x2 (supported), x3 (supported), x4 (supported), x5 (supported)
- **f6** Shared devices on routes: for the A-9278 alert, device D-568 sent every onward transfer (T0007, T0008, T0009, T0014, T0015, T0016) from three route accounts: A-9278, A-5092 and A-2897. For the A-9895 alert, no device was used by two or more of its route accounts (T0041 came from D-699; A-1415's only sent transfer, T0055, came from D-785).  
  Claims: s1 (supported), e1 (supported), e2 (supported), e3 (supported), e4 (supported), e5 (supported), e6 (supported), x1 (supported), e7 (supported), e8 (supported)
- **f7** What sets the alerts apart: both have 6 senders and 6 transfers inside one event-time hour, but they differ in the recorded relationships. The A-9278 alert passes on every contributing transfer through 3 onward links to one resting account, A-4989, and all of that is sent from one device shared by three route accounts. The A-9895 alert has small equal credits totalling 15000, half of them not passed on, a single onward hop to A-1415, and no shared device on its route. A-1415 later sent T0055 (90000) to A-9514, but no onward link from T0041 was recorded. Neither resting account has a fan-in alert of its own.  
  Claims: i1 (supported), i2 (supported), r1 (supported), r2 (supported), s1 (supported), x1 (supported), x2 (supported), x3 (supported), x4 (supported), x5 (supported), e8 (supported), x8 (supported), x9 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** In the A-9278 alert, quick pass-through over A-9278, A-5092 and A-2897, all sent from device D-568, could mean one party controls those accounts and is layering funds toward A-4989. The data records only that one device was shared. It does not establish ownership, identity, control or fraud.  
  References: s1, r1, p1, p4
- **h2** The A-9895 alert could be harmless collection of many small equal payments (for example a shared bill or group contribution), with one later payment out. The lack of a shared device and the shallow onward reach fit that reading but do not prove it.  
  References: i2, r2, x1

## Unresolved questions

- **u1** Who controls or owns accounts A-9278, A-5092, A-2897 and device D-568? The dataset records device use, not identity.  
  References: s1
- **u2** What happens to the funds at A-4989 and A-1415 after this bounded replay? No later events are in the dataset, and A-4989 sends nothing here.  
  References: x6, x7, x5
- **u3** Is A-1415's T0055 (90000 to A-9514, about 3.25 h after T0041) related to the funds it received? It falls outside the onward gap, so no link is recorded, and the amount is larger than T0041.  
  References: e7, e8, x5
- **u4** Where did the 2500 credits T0035 to T0037 go? They were not passed on within the onward gap, and the dataset does not tie them to any later debit.  
  References: x2, x3, x4

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e1 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| e2 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| e3 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| e4 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| e5 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| e6 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| e7 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| e8 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| e9 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| e10 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| e11 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| e12 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| e13 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| i1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| i2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| p1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p2 | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p3 | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p4 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p5 | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p6 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p7 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p8 | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p9 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| r1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| r2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| s1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| x1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| x2 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| x3 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| x4 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| x5 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| x6 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| x7 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| x8 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| x9 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 41 of 41 claims supported; reference validity 1.0 (43 of 43 distinct ids resolve); 10 queries (0 failed), 5 model requests, 41650 input tokens (cache included) and 7194 output tokens, 87.4 s.
