# Case note: graph arm, run 3

Agent output, recorded run of 2026-11-13T18:28:58+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: one bounded replay (run run:72cf0e4b91a3, 55 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms window, onward gap up to 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000. It has 6 distinct senders and 6 transfers totalling 357,000 minor units (3,570.00). The contributing transfers are T0002, T0003, T0006, T0010, T0011 and T0012. Their amounts vary from 38,000 to 89,000, and each came from a different sender and device.  
  Claims: I1 (supported), E01 (supported), E02 (supported), E03 (supported), E04 (supported), E05 (supported), E06 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000. It has 6 distinct senders and 6 transfers totalling 15,000 minor units (150.00). The contributing transfers are T0035 to T0040, each exactly 2,500, each from a different sender and device.  
  Claims: I2 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F4** Onward links for A-9278: every contributing transfer is passed on, and the longest chain has 3 onward links. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138,000), then T0008 (A-5092 to A-2897, 135,000), then T0009 (A-2897 to A-4989, 132,000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210,000), then T0015 (A-5092 to A-2897, 206,000), then T0016 (A-2897 to A-4989, 202,000). Neither T0009 nor T0016 is passed on, so both chains come to rest at A-4989. The route accounts are A-9278, A-5092, A-2897 and A-4989.  
  Claims: R1 (supported), P1 (supported), P2 (supported), E07 (supported), E08 (supported), E09 (supported), E10 (supported), E11 (supported), E12 (supported), X2 (supported), X3 (supported)
- **F5** Onward links for A-9895: the longest chain has 1 onward link. T0038, T0039 and T0040 link to T0041 (A-9895 to A-1415, 14,000, device D-699), which is not passed on, so that chain comes to rest at A-1415. T0035, T0036 and T0037 have no onward link: they remain at A-9895 as recorded. A-1415 later sends T0055 (90,000 to A-9514 at 1794333900000), but no onward link from T0041 to T0055 was recorded. The gap is 11,700,000 ms, well over the 1,800,000 ms limit. The route accounts are A-9895 and A-1415.  
  Claims: R2 (unsupported), P3 (supported), E19 (supported), E20 (supported), X4 (supported), X5 (supported), X6 (supported), X7 (supported)
- **F6** Shared devices on the A-9278 routes: three route accounts, A-9278, A-5092 and A-2897, all sent transfers from device D-568. All six onward transfers (T0007, T0008, T0009, T0014, T0015, T0016) came from D-568. A-4989 sent no transfers in this dataset.  
  Claims: S1 (supported), E07 (supported), E08 (supported), E09 (supported), E10 (supported), E11 (supported), E12 (supported)
- **F7** Shared devices on the A-9895 routes: none. A-9895 sent from D-699 and A-1415 from D-785, and no device was used by both route accounts.  
  Claims: X1 (supported), E19 (supported), E20 (supported)
- **F8** What tells the alerts apart: as indicators they look alike (6 senders, 6 transfers, one-hour window). The recorded relationships differ. (a) A-9278 forwards all six credits in two 3-link chains through A-5092 and A-2897 to a single resting account, A-4989. A-9895 forwards only via one 1-link transfer, and half its credits are not passed on. (b) The A-9278 route accounts share one device, D-568, used for every onward hop. The A-9895 route has no shared device. (c) The A-9278 amounts vary and are large (total 357,000). The A-9895 amounts are six identical 2,500 payments (total 15,000). (d) None of the downstream accounts A-5092, A-2897, A-4989 or A-1415 has a fan-in alert of its own. So the A-9278 alert is joined to a multi-hop, single-device onward structure, while the A-9895 alert is a shallow fan-in with limited onward movement. The fan-in indicator alone does not separate them.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (unsupported), S1 (supported), X1 (supported), X8 (supported), X9 (supported), X10 (supported), X11 (supported)
- **F9** Interpretation caution: an onward link records only timing (a credit followed within 1,800,000 ms by a debit from the same account), not that the same money moved. For example, T0041 (14,000) is more than the three linked credits it follows (3 × 2,500 = 7,500), and T0007 (138,000) is less than the three credits linked to it (141,500). The conclusions here are traceable provenance back to the listed transfer ids, not proof of fund flow.  
  Claims: P1 (supported), P3 (supported), E01 (supported), E02 (supported), E03 (supported), E07 (supported), E16 (supported), E17 (supported), E18 (supported), E19 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-9278, A-5092 and A-2897 may be controlled by one party or operated together, because they share device D-568 and passed balances along in quick succession (150–195 s between hops). This could be consistent with a collection-and-layering pattern ending at A-4989. The data does not establish ownership, identity or intent.  
  References: S1, R1, P1, P2
- **H2** The A-9895 alert may be benign collective payments (for example, six people each paying an equal 25.00 share), with a later partial payout to A-1415. It could also be low-value testing. The data does not tell these apart.  
  References: I2, R2, X1
- **H3** A-4989 may be a collection or exit account, because both A-9278 chains end there and it sends nothing in this dataset.  
  References: R1, X2, X3, X10

## Unresolved questions

- **U1** What happens to funds at A-4989 and A-1415 after this replay? The dataset is bounded, and no onward activity from A-4989 is recorded within it.  
  References: R1, R2, X2, X3, X4
- **U2** Who holds device D-568, and is the sharing legitimate (for example, a household, a business, or a shared terminal)? The graph records device use, not ownership.  
  References: S1
- **U3** Do the contributing senders of either alert have links outside this dataset, or relationships the graph does not record?  
  References: I1, I2
- **U4** Device D-619 is also shared, by A-2952 and A-9652 (both paid A-5093), but it is not on either alert's route. Is it relevant? It falls outside these alerts and was not investigated further.  
  References: C5

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
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415", "A-9895"], route_accounts=["A-9895", "A-1415"] | unsupported: terminal_accounts are ['A-1415'], not ['A-1415', 'A-9895'] |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| X1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| X2 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| X3 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| X4 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| X5 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| X8 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| X9 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| X10 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| X11 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C1 | count | pattern="fan_in_alerts", value=2 | supported |
| C2 | count | pattern="transfers", value=55 | supported |
| C3 | count | pattern="onward_links", value=14 | supported |
| C4 | count | pattern="accounts", value=48 | supported |
| C5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 43 of 44 claims supported; reference validity 1.0 (61 of 61 distinct ids resolve); 10 queries (0 failed), 5 model requests, 42431 input tokens (cache included) and 9286 output tokens, 111.1 s.
