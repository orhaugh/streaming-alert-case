# Case note: graph arm, run 2

Agent output, recorded run of 2026-11-13T18:44:42+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: one bounded replay (run run:72cf0e4b91a3, 55 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders in a 3,600,000 ms window; onward links within 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000 to 1794304800000, 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002, T0003, T0006, T0010, T0011, T0012 (from A-4452, A-4366, A-7266, A-8133, A-6801, A-3881, each on a different device, amounts from 38000 to 89000).  
  Claims: I1 (supported), E01 (supported), E02 (supported), E03 (supported), E04 (supported), E05 (supported), E06 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000 to 1794322800000, 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035, T0036, T0037, T0038, T0039, T0040, each exactly 2500, from A-8770, A-4399, A-4792, A-9088, A-8060, A-8166, each on a different device.  
  Claims: I2 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F4** Onward links for A-9278: all six contributing transfers are passed on. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), then T0008 (A-5092 to A-2897, 135000), then T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (A-5092 to A-2897, 206000), then T0016 (A-2897 to A-4989, 202000). The longest chain has 3 onward links. T0009 and T0016 are not passed on, so both chains end at A-4989. The route accounts are A-9278, A-5092, A-2897 and A-4989.  
  Claims: R1 (supported), P1 (supported), P2 (supported), P3 (supported), P4 (supported), P5 (supported), P6 (supported), E07 (supported), E08 (supported), E09 (supported), E10 (supported), E11 (supported), E12 (supported), N5 (supported), N6 (supported)
- **F5** Onward links for A-9895: only T0038, T0039 and T0040 are passed on. All three link to T0041 (A-9895 to A-1415, 14000), and T0041 is not passed on. The longest chain has 1 onward link, and the money comes to rest at A-1415. T0035, T0036 and T0037 are not passed on, so they start no chain. The route accounts are A-9895 and A-1415.  
  Claims: R2 (supported), P7 (supported), P8 (supported), P9 (supported), E19 (supported), N2 (supported), N3 (supported), N4 (supported), N7 (supported)
- **F6** Shared devices on the A-9278 routes: A-9278, A-5092 and A-2897 each sent from device D-568. All six onward transfers T0007, T0008, T0009, T0014, T0015 and T0016 were sent from D-568. The resting account A-4989 sent no transfers in the dataset.  
  Claims: S1 (supported), E07 (supported), E08 (supported), E09 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F7** Shared devices on the A-9895 route: none. No device was used to send by two or more of its route accounts. A-9895 sent T0041 from D-699. A-1415 sent T0055 (to A-9514, 90000, at 1794333900000) from D-785. T0055 is not an onward link of T0041: it came 11,700,000 ms later, beyond the 1,800,000 ms onward gap.  
  Claims: N1 (supported), E19 (supported), E20 (supported), N7 (supported)
- **F8** The only other device in the dataset used by two or more sending accounts is D-619, used by A-2952 (T0027) and A-9652 (T0019), both paying A-5093. It is not on either alert's routes. Note that A-5093 is a different account from route account A-5092.  
  Claims: S2 (supported), E21 (supported), E22 (supported)
- **F9** What distinguishes the two alerts, which look alike as indicators (6 senders and 6 transfers each, within one hour): (a) totals of 357000 against 15000, with uniform 2500 credits for A-9895; (b) all six A-9278 credits are passed on through chains 3 links deep, against three of six A-9895 credits passed on 1 link deep; (c) the A-9278 onward route, three distinct accounts, was sent entirely from one device, D-568, while the A-9895 route shares no device. None of the downstream accounts A-5092, A-2897, A-4989 or A-1415 has its own fan-in alert. The A-9278 alert therefore comes with a recorded multi-hop, single-device onward structure. The A-9895 alert is a fan-in with a short, partial onward link and no device overlap.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (supported), S1 (supported), N1 (supported), N2 (supported), N3 (supported), N4 (supported), N8 (supported), N9 (supported), N10 (supported), N11 (supported)
- **F10** Traceable provenance: every statement above comes from transfers, onward links and indicators in this graph, identified by their dataset ids, under the run record's parameters and the dataset sha256 72cf0e4b91a3...  
  Claims: C1 (supported), C2 (supported), I1 (supported), I2 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** Because one device, D-568, sent every hop from A-9278 through A-5092 and A-2897 to A-4989, with small amount reductions at each hop (138000 to 135000 to 132000; 210000 to 206000 to 202000), these accounts may be controlled by one party moving collected funds in layers. The data records only device use and transfers; it does not establish common control, ownership or fraud.  
  References: S1, R1, E07, E08, E09, E10, E11, E12
- **H2** The A-9895 alert, with uniform 2500 credits and only part of them passed on in a single hop, may be benign collection activity (for example, a shared bill or a group payment) rather than mule activity. That is an interpretation; the data does not establish the purpose.  
  References: I2, R2, N1, N2, N3, N4
- **H3** A-9278 forwarded 348000 of the 357000 it received. The 3000 to 4000 shortfall at each later hop could be fees or retained amounts. That is not recorded.  
  References: E07, E08, E09, E10, E11, E12, I1

## Unresolved questions

- **U1** What happens to the funds at A-4989 after T0009 and T0016? A-4989 sends nothing in this bounded dataset, and later activity, if there is any, lies outside it.  
  References: N5, N6, R1
- **U2** Is A-1415's later transfer T0055 (90000 to A-9514, from D-585... D-785) related to the 14000 it received in T0041? It falls outside the onward gap and its amount exceeds the credit, so the data does not link them.  
  References: E19, E20, N7
- **U3** Who uses device D-568, and does using one device mean one person or entity across A-9278, A-5092 and A-2897? The data cannot say.  
  References: S1
- **U4** Is there any relationship between D-619's users (A-2952, A-9652) paying A-5093 and route account A-5092, beyond the similar ids? Nothing recorded connects them.  
  References: S2, R1

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E01 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| E02 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| E03 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| E04 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| E05 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| E06 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| E07 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| E08 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| E09 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
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
| E20 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| E21 | event | transfer="T0019", sender="A-9652", receiver="A-5093", amount_minor=2350, event_time_ms=1794305700000, device="D-619" | supported |
| E22 | event | transfer="T0027", sender="A-2952", receiver="A-5093", amount_minor=4120, event_time_ms=1794310800000, device="D-619" | supported |
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
| N1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| N2 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| N3 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| N4 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| N5 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| N6 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| N7 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| N8 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| N9 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| N10 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| N11 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 53 of 53 claims supported; reference validity 0.9844 (63 of 64 distinct ids resolve); 10 queries (0 failed), 5 model requests, 43445 input tokens (cache included) and 9384 output tokens, 109.4 s.
