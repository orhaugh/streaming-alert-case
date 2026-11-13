# Case note: graph arm, run 1

Agent output, recorded run of 2026-11-13T18:22:15+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: this is one bounded replay (run run:72cf0e4b91a3, 55 dataset events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms event-time window; onward max gap 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and exactly 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F1** Alert 1, fan_in:A-9278:1794301200000: account A-9278 received 6 transfers from 6 distinct senders in window 1794301200000–1794304800000, totalling 357000 minor units. The contributing transfers are T0002, T0003, T0006, T0010, T0011 and T0012. Amounts vary from 38000 to 89000, and each sender used a different device.  
  Claims: I1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported)
- **F2** Alert 2, fan_in:A-9895:1794319200000: account A-9895 received 6 transfers from 6 distinct senders in window 1794319200000–1794322800000, totalling 15000 minor units. The contributing transfers are T0035 to T0040. Each is exactly 2500, and each was sent from a different device.  
  Claims: I2 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F3** Alert 1's onward route: all 6 contributing transfers have onward links. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), which links to T0008 (A-5092 to A-2897, 135000), which links to T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (A-5092 to A-2897, 206000), then T0016 (A-2897 to A-4989, 202000). Chains are at most 3 onward links long. Both final transfers, T0009 and T0016, were not passed on, so the money comes to rest at A-4989. The route accounts are A-9278, A-5092, A-2897 and A-4989.  
  Claims: R1 (supported), P1 (supported), P2 (supported), P3 (supported), P4 (supported), P5 (supported), P6 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), X2 (supported), X3 (supported)
- **F4** Alert 2's onward route: only 3 of the 6 contributing transfers (T0038, T0039, T0040) link onward, all to a single transfer, T0041 (A-9895 to A-1415, 14000). T0041 was not passed on. T0035, T0036 and T0037 were not passed on either, so in the recorded links those credits stay at A-9895. Chains are at most 1 onward link long. The chain ends are A-1415 and A-9895, and the route accounts are A-9895 and A-1415. A-1415 later sent T0055 (90000 to A-9514, at 1794333900000), but no onward link connects it to T0041, because T0055 falls well outside the 1,800,000 ms gap.  
  Claims: R2 (unsupported), P7 (supported), P8 (supported), P9 (supported), E19 (supported), E20 (supported), X4 (supported), X5 (supported), X6 (supported), X7 (supported), X8 (supported)
- **F5** Shared devices on routes, alert 1: device D-568 was used to send every onward transfer on the route, T0007, T0008, T0009, T0014, T0015 and T0016. That means route accounts A-9278, A-5092 and A-2897 all sent from D-568. A-4989 sent no transfers in the dataset.  
  Claims: S1 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F6** Shared devices on routes, alert 2: no device was used by two or more of its route accounts. A-9895 sent from D-699, and A-1415 sent from D-785. The only other shared device in the dataset, D-619 (used by A-2952 and A-9652), is not on either alert's route.  
  Claims: X1 (supported), S2 (supported), E19 (supported), E20 (supported)
- **F7** What separates the alerts: both show 6 senders and 6 transfers in one hour, but the recorded relationships beneath them differ. (a) Onward depth: alert 1 has a 3-hop onward route along A-9278, A-5092, A-2897 and A-4989, and all of its contributing transfers lead onward. Alert 2 has a single 1-hop link, and only half of its contributing transfers lead onward. (b) Amounts: on alert 1's route, two batches of credits (141500 and 215500) move on as 138000 and 210000, and each later hop is a few thousand smaller. Alert 2 has uniform 2500 credits, and only 14000 moves on. (c) Devices: every hop on alert 1's route was sent from one device, D-568, by three different route accounts. Alert 2's route has no shared device. (d) Downstream alerts: no downstream route account of either alert (A-5092, A-2897, A-4989, A-1415) has its own fan-in alert. So the indicator alone would miss the route behind alert 1.  
  Claims: R1 (supported), R2 (unsupported), S1 (supported), X1 (supported), I1 (supported), I2 (supported), X9 (supported), X10 (supported), X11 (supported), X12 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** Alert 1 may be a collection-and-layering pattern: funds gathered at A-9278 and moved quickly through A-5092 and A-2897 to A-4989. If so, the single device D-568 on every hop could mean the three route accounts are operated by one party. The data does not establish this. A shared device is not proof of shared ownership, identity or fraud.  
  References: fan_in:A-9278:1794301200000, D-568, A-9278, A-5092, A-2897, A-4989, T0007, T0014
- **H2** Alert 2 could be benign, for example many small identical payments such as a collection or a split bill, followed by an ordinary later payment. The onward link to T0041 is a timing link only (14000 sent after 7500 of linked credits) and does not show that those specific funds moved on.  
  References: fan_in:A-9895:1794319200000, T0041, A-1415
- **H3** The small amount drops at each hop on alert 1's route (3000–4000 minor units) might be fees or retained cuts. Nothing recorded explains them.  
  References: T0007, T0008, T0009, T0014, T0015, T0016

## Unresolved questions

- **U1** Who controls device D-568, and do A-9278, A-5092 and A-2897 share an owner? The dataset records only device use, not ownership or identity.  
  References: D-568, A-9278, A-5092, A-2897
- **U2** What happens to funds at A-4989 and A-1415 after this dataset ends? A-4989 sends nothing in the bounded replay, and events outside it are not visible.  
  References: A-4989, A-1415
- **U3** Where did the funds for A-1415's T0055 (90000) come from? A-1415 received only 14000 in the dataset, and account balances and earlier history are not recorded.  
  References: A-1415, T0055, T0041
- **U4** Are the onward links value-preserving? The links record only event-time proximity, so it cannot be determined which credits actually funded which debits.  
  References: onward:T0002:T0007, onward:T0038:T0041

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
| P2 | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P4 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P5 | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P6 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P7 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| P8 | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| P9 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415", "A-9895"], route_accounts=["A-9895", "A-1415"] | unsupported: terminal_accounts are ['A-1415'], not ['A-1415', 'A-9895'] |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| S2 | shared_device | device="D-619", accounts=["A-2952", "A-9652"] | supported |
| X1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| X2 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| X3 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| X4 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| X5 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| X8 | absence | kind="no_onward_link_from_transfer", subject="T0055" | supported |
| X9 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| X10 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| X11 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| X12 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 51 of 52 claims supported; reference validity 1.0 (62 of 62 distinct ids resolve); 9 queries (0 failed), 5 model requests, 39627 input tokens (cache included) and 9480 output tokens, 115.4 s.
