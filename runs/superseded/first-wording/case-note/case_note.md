# Case note: fan-in alerts in a bounded replay

Agent output, recorded run of 2026-11-13T18:20:09+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: the run record (run:72cf0e4b91a3) is a bounded replay of 55 events. clink exited with status 0, 3 of 3 jobs completed, and the run was not cancelled. Parameters: fan_in_min_senders=5, fan_in_window_ms=3600000, onward_max_gap_ms=1800000. The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as processed by this run.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000. 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002 (A-4452, 42000), T0003 (A-4366, 61500), T0006 (A-7266, 38000), T0010 (A-8133, 89000), T0011 (A-6801, 50500) and T0012 (A-3881, 76000). Each was sent from a different device.  
  Claims: I1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000. 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035 to T0040, each exactly 2500, from A-8770, A-4399, A-4792, A-9088, A-8060 and A-8166. Each was sent from a different device.  
  Claims: I2 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F4** Onward links for A-9278: all 6 contributing transfers are passed on, at most 3 links deep, along A-9278 -> A-5092 -> A-2897 -> A-4989, in two waves. Wave 1: T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), then T0008 (A-5092 to A-2897, 135000), then T0009 (A-2897 to A-4989, 132000). Wave 2: T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (A-5092 to A-2897, 206000), then T0016 (A-2897 to A-4989, 202000). Neither T0009 nor T0016 is passed on, so the money comes to rest at A-4989 only. Each hop pays out a little less than it received.  
  Claims: P1 (supported), P2 (supported), P3 (supported), P4 (supported), P5 (supported), P6 (supported), R1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), X3 (supported), X4 (supported)
- **F5** Onward links for A-9895: only 3 of the 6 contributing transfers (T0038, T0039, T0040) are passed on, each by one link to T0041 (A-9895 to A-1415, 14000). T0035, T0036 and T0037 are not passed on; their credit-to-debit gaps to T0041 exceed the 1800000 ms limit. T0041 is not passed on either, so the most links in any chain is 1 and the money comes to rest at A-1415. A-1415's later send T0055 is not recorded as an onward link of T0041.  
  Claims: P7 (supported), P8 (supported), P9 (supported), R2 (supported), E19 (supported), X5 (supported), X6 (supported), X7 (supported), X8 (supported)
- **F6** Shared devices on A-9278's routes: device D-568 sent every route transfer from A-9278 (T0007, T0014), A-5092 (T0008, T0015) and A-2897 (T0009, T0016). Those are exactly the three route accounts that sent from D-568; A-4989 sent nothing in the dataset. None of the six senders of the contributing transfers uses a shared device.  
  Claims: S1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F7** Shared devices on A-9895's routes: no device was used by two or more of its route accounts (A-9895, A-1415). A-9895 sent T0041 from D-699 and A-1415 sent T0055 from D-785. The only other shared device in the dataset, D-619 (A-2952, A-9652), is not on either alert's routes.  
  Claims: X1 (supported), S2 (supported), E19 (supported)
- **F8** What tells the alerts apart: as indicators they match (6 senders, 6 transfers, one hour each). The recorded relationships differ. (a) A-9278's chains are 3 links deep and pass through two intermediate accounts to one resting account; A-9895's chains are 1 link deep and go straight to A-1415. (b) All of A-9278's contributing transfers are passed on, but only half of A-9895's are. (c) The three accounts moving money along A-9278's route all sent from one device, D-568; A-9895's route has no shared device. (d) A-9278 received 357000 in varied amounts; A-9895 received 15000 in identical 2500 amounts. Only A-9278's alert combines layered onward movement with a common device across the route, so it calls for closer review. A-9895's alert, seen through these relationships alone, shows a shallow single pass-on.  
  Claims: R1 (supported), R2 (supported), S1 (supported), X1 (supported), I1 (supported), I2 (supported), X5 (supported), X6 (supported), X7 (supported)
- **F9** The accounts where money comes to rest (A-4989, A-1415) and the intermediaries A-5092 and A-2897 have no fan-in alert of their own.  
  Claims: X9 (supported), X10 (supported), X11 (supported), X12 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** D-568 being used to send from A-9278, A-5092 and A-2897 may mean one party controls all three accounts, moving pooled funds through them to A-4989 (layering). The data records only device use, not ownership or identity.  
  References: S1, R1
- **H2** The six identical 2500 credits to A-9895 from six senders on six devices may be a benign collection (for example a shared bill or group payment) rather than mule activity. They may also be a low-value test. Nothing in the data settles which.  
  References: I2, R2, X1
- **H3** The small amount kept back at each hop on A-9278's route (for example 138000 -> 135000 -> 132000) may be fees or cuts taken by intermediaries. That reading is not established.  
  References: E7, E8, E9, E10, E11, E12

## Unresolved questions

- **U1** Who controls device D-568? Do A-9278, A-5092 and A-2897 belong to the same person? The dataset records device use only.  
  References: S1
- **U2** What happens to funds at A-4989 and A-1415 after this replay? Is A-1415's later T0055 (90000) funded by T0041 or by other money? The data has no onward link, and no events outside the bounded replay are available.  
  References: X4, X6, R1, R2
- **U3** Do the senders to A-9278 (A-4452, A-4366, A-7266, A-8133, A-6801, A-3881) know each other, or are they victims? The data shows no shared device among them and no further relationship.  
  References: I1
- **U4** Was the 2500 still held at A-9895 (15000 received, 14000 passed on in T0041) spent later, outside this dataset?  
  References: I2, E19

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E1 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| E2 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| E3 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| E4 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| E5 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| E6 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| E7 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| E8 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| E9 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| E10 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| E11 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| E12 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| E13 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| E14 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| E15 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| E16 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| E17 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| E18 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| E19 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P4 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P5 | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P6 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P7 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| P8 | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| P9 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| S2 | shared_device | device="D-619", accounts=["A-2952", "A-9652"] | supported |
| X1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| X3 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| X4 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| X5 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| X8 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| X9 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| X10 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| X11 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| X12 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 50 of 50 claims supported; reference validity 1.0 (59 of 59 distinct ids resolve); 9 queries (0 failed), 5 model requests, 43695 input tokens (cache included) and 8964 output tokens, 107.6 s.
