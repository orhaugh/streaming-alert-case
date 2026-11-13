# Case note: table arm, run 3

Agent output, recorded run of 2026-11-13T18:47:59+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f0** Scope: one bounded replay (run:72cf0e4b91a3; 55 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders in a 3,600,000 ms window; onward max gap 1,800,000 ms). The dataset has 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f1** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000 ms, 6 distinct senders, 6 transfers, total 357000 minor units. The contributing transfers are T0002, T0003, T0006, T0010, T0011 and T0012.  
  Claims: i1 (supported)
- **f2** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000 ms, 6 distinct senders, 6 transfers, total 15000 minor units. The contributing transfers are T0035 to T0040.  
  Claims: i2 (supported)
- **f3** Onward links from the A-9278 alert: chains go at most 3 links deep. T0002, T0003 and T0006 each link to T0007 (A-9278 to A-5092, 138000), then to T0008 (A-5092 to A-2897, 135000), then to T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 each link to T0014 (A-9278 to A-5092, 210000), then to T0015 (to A-2897, 206000), then to T0016 (to A-4989, 202000). Every contributing transfer is passed on. The only account where the money comes to rest is A-4989: T0009 and T0016 are not passed on. The route accounts are A-9278, A-5092, A-2897 and A-4989. A-4989 has no fan-in alert.  
  Claims: r1 (supported), p1 (supported), p2 (supported), e7 (supported), e8 (supported), e9 (supported), e14 (supported), e15 (supported), e16 (supported), a6 (supported), a7 (supported), a8 (supported)
- **f4** Onward links from the A-9895 alert: chains go at most 1 link deep. T0038, T0039 and T0040 each link to T0041 (A-9895 to A-1415, 14000). T0041 is not passed on, so the money comes to rest at A-1415. The other three contributing transfers (T0035, T0036, T0037) are not passed on and start no chain. The route accounts are A-9895 and A-1415.  
  Claims: r2 (supported), p3 (supported), e41 (supported), a2 (supported), a3 (supported), a4 (supported), a5 (supported)
- **f5** Shared devices on the routes: for the A-9278 alert, device D-568 sent transfers from three route accounts: A-9278, A-5092 and A-2897. All six onward transfers (T0007, T0008, T0009, T0014, T0015, T0016) were sent from D-568. The resting account A-4989 sent no transfers. For the A-9895 alert, no device was used by two or more of its route accounts (A-9895 sent from D-699, A-1415 from D-785).  
  Claims: s1 (supported), e7 (supported), e8 (supported), e9 (supported), e14 (supported), e15 (supported), e16 (supported), a1 (supported), e41 (supported), e55 (supported)
- **f6** What distinguishes the two alerts: both have 6 senders and 6 transfers, but they differ in four recorded ways. (a) Total: 357000 against 15000. (b) Pass-on: all 6 credits to A-9278 are passed on, against 3 of 6 for A-9895. (c) Depth: chains of 3 hops through A-5092 and A-2897 to A-4989, against 1 hop to A-1415. (d) Devices: one device, D-568, sends from every forwarding account on the A-9278 route, while no device is shared on the A-9895 route. The A-9278 indicator therefore comes with a recorded multi-hop, single-device forwarding structure. The A-9895 indicator has only a single partial forward and no shared device on its route.  
  Claims: i1 (supported), i2 (supported), r1 (supported), r2 (supported), s1 (supported), a1 (supported), a2 (supported), a3 (supported), a4 (supported)
- **f7** A-1415 later sends T0055 (90000 to A-9514, device D-785) at 1794333900000. That is 11,700,000 ms after T0041, beyond the 1,800,000 ms onward gap, so the run recorded no onward link and T0041 counts as not passed on. A-1415 has no fan-in alert.  
  Claims: e55 (supported), e41 (supported), a5 (supported), a9 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** One device (D-568) sending from A-9278, A-5092 and A-2897, with each hop forwarding slightly less than it received within minutes, fits these accounts being controlled by one operator and used as pass-through (layering) accounts toward A-4989. The data does not establish control, ownership or intent.  
  References: s1, r1, p1, p2, f3, f5
- **h2** The A-9895 alert (six identical 2500 credits, half of them forwarded in one 14000 debit, no shared device on the route) may be benign collection, such as a shared bill or group payment. Or it may be a low-value mule test. The recorded relationships are weaker than for A-9278 and do not decide between these readings.  
  References: i2, r2, a1, f4

## Unresolved questions

- **u1** What happens to funds at A-4989 after T0009 and T0016? A-4989 sends nothing in this bounded dataset, and activity outside the replay cannot be seen.  
  References: a6, a7, r1
- **u2** Is T0055 (A-1415 to A-9514, 90000), sent outside the onward gap and for more than A-1415 received through T0041, related to the A-9895 alert at all? Where did the rest of the 90000 come from? The dataset records no link.  
  References: e55, e41, a5
- **u3** Who uses device D-568, and what is the relationship between the accounts that share it? The data records only that transfers were sent from it.  
  References: s1
- **u4** Where did the 7500 minor units credited to A-9895 by T0035–T0037 go? They are not passed on within the gap, and the data does not show where they ended up.  
  References: a2, a3, a4

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e7 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| e8 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| e9 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| e14 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| e15 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| e16 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| e41 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| e55 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| i1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| i2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| p1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p2 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p3 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| r1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| r2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| s1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| a1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| a2 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| a3 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| a4 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| a5 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| a6 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| a7 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| a8 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| a9 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 30 of 30 claims supported; reference validity 1.0 (33 of 33 distinct ids resolve); 5 queries (0 failed), 3 model requests, 19277 input tokens (cache included) and 5303 output tokens, 62.9 s.
