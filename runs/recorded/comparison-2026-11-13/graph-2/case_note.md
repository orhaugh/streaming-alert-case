# Case note: graph arm, run 2

Agent output, recorded run of 2026-11-13T18:27:14+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: one bounded replay (run:72cf0e4b91a3, 55 dataset events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders within a 3,600,000 ms event-time window; onward links require a gap of at most 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below applies only to this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert 1, fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000. 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002, T0003, T0006, T0010, T0011, T0012, with amounts of 38000 to 89000 that are all different, each sent from a different device.  
  Claims: I1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported)
- **F3** Alert 2, fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000. 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035, T0036, T0037, T0038, T0039, T0040, every one exactly 2500 minor units, each sent from a different device.  
  Claims: I2 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F4** Alert 1 onward route: all six contributing transfers are passed on. T0002, T0003 and T0006 link to T0007 (A-9278→A-5092, 138000), then T0008 (A-5092→A-2897, 135000), then T0009 (A-2897→A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278→A-5092, 210000), then T0015 (A-5092→A-2897, 206000), then T0016 (A-2897→A-4989, 202000). At most 3 onward links. The route accounts are A-9278, A-5092, A-2897 and A-4989. The money comes to rest at A-4989 only: neither T0009 nor T0016 is passed on, and A-4989 sends no transfer in the dataset.  
  Claims: P1 (supported), P2 (supported), R1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), X2 (supported), X3 (supported)
- **F5** Alert 2 onward route: only three of the six contributing transfers are passed on. T0038, T0039 and T0040 link to T0041 (A-9895→A-1415, 14000), which is not passed on. T0035, T0036 and T0037 are not passed on, so their chains end at A-9895. At most 1 onward link. The route accounts are A-9895 and A-1415, and the terminal accounts are A-9895 and A-1415.  
  Claims: P3 (supported), R2 (unsupported), E19 (supported), X4 (supported), X5 (supported), X6 (supported), X7 (supported)
- **F6** Alert 1 devices: A-9278, A-5092 and A-2897, three of its route accounts, all sent their onward transfers (T0007, T0008, T0009, T0014, T0015, T0016) from the same device, D-568. A-4989 sent nothing.  
  Claims: S1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F7** Alert 2 devices: no device was used to send by two or more of its route accounts. A-9895 sent from D-699, and A-1415 sent its only transfer, T0055, from D-785. The only other device in the dataset used by more than one account is D-619 (A-9652, A-2952), which is on neither alert's route.  
  Claims: X1 (supported), E19 (supported), E20 (supported), S2 (supported)
- **F8** What distinguishes the alerts: as indicators they look alike (6 senders, 6 transfers, one-hour window). The recorded relationships differ in four ways. (a) Pass-through: alert 1 passes on all six credits through a 3-link chain, while alert 2 passes on three of six through 1 link. (b) Amounts: alert 1's onward transfers carry most of the money in (348000 of 357000 leaves A-9278, and 334000 reaches A-4989), against 14000 of 15000 for alert 2. Alert 2's inputs are uniform 2500 amounts. (c) Device: alert 1's route accounts all send from D-568, while alert 2's route has no shared device. (d) Timing: alert 1's hops come 140000–195000 ms apart. On the recorded relationships, alert 1 is a multi-hop route with a shared device, and alert 2 is a shallow, partial pass-through with no device link.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (unsupported), S1 (supported), X1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), E19 (supported)
- **F9** Neither alert's terminal account has a fan-in alert of its own (A-4989, A-1415). A-1415 later sent T0055 (90000 to A-9514), but it is not a recorded onward link from T0041: it came about 11,700,000 ms later, beyond the 1,800,000 ms onward gap.  
  Claims: X8 (supported), X9 (supported), E20 (supported), X4 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** Alert 1 may be a collection-and-layering pattern: six unrelated-looking credits are consolidated and then pushed through two intermediate accounts to A-4989 within minutes, all from one device (D-568). That could mean A-9278, A-5092 and A-2897 are controlled by one party. The data records shared device use only, not ownership or intent.  
  References: R1, S1, P1, P2, F8
- **H2** Alert 2 may be benign or low-risk: six identical 2500 payments look like a group collection or split bill, and half of the money stays in A-9895. It could also be a probe or test pattern. The data cannot tell these apart.  
  References: I2, R2, X1, F5
- **H3** The small shortfall at each hop of alert 1 (about 3000–4000 minor units) could be fees or retained cuts. Nothing recorded supports either reading.  
  References: E7, E8, E9, E10, E11, E12

## Unresolved questions

- **U1** What happens to the funds at A-4989 after T0009 and T0016? A-4989 sends nothing in this bounded dataset, and nothing outside it can be assessed.  
  References: R1, X2, X3
- **U2** Is A-1415's later transfer T0055 (90000, larger than the 14000 it received) related to T0041 in any way? No onward link is recorded, and the source of A-1415's other funds is not established here.  
  References: E19, E20, X4
- **U3** Who uses device D-568, and is a single person or a shared or institutional terminal behind the three accounts? Device records do not show identity.  
  References: S1
- **U4** Are the 12 contributing senders connected to each other or to the route accounts in ways not recorded here (for example other channels or identity data)? They share no device in this dataset.  
  References: I1, I2
- **U5** Is D-619's use by A-9652 and A-2952, both paying A-5093, relevant to either alert? It lies outside both alerts' routes.  
  References: S2

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
| E20 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-9895", "A-1415"], route_accounts=["A-9895", "A-1415"] | unsupported: terminal_accounts are ['A-1415'], not ['A-1415', 'A-9895'] |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| S2 | shared_device | device="D-619", accounts=["A-9652", "A-2952"] | supported |
| X1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| X2 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| X3 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| X4 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| X5 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| X8 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| X9 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 42 of 43 claims supported; reference validity 1.0 (61 of 61 distinct ids resolve); 8 queries (0 failed), 5 model requests, 39830 input tokens (cache included) and 8558 output tokens, 103.5 s.
