# Case note: table arm, run 1

Agent output, recorded run of 2026-11-13T18:42:11+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f1** Bounded replay run:72cf0e4b91a3 (3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 1-hour event-time window; onward max gap 30 min) holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f2** Alert fan_in:A-9278:1794301200000: account A-9278 received 6 transfers from 6 distinct senders between 1794301200000 and 1794304800000, 357000 minor units in total (T0002, T0003, T0006, T0010, T0011, T0012).  
  Claims: i1 (supported)
- **f3** Alert fan_in:A-9895:1794319200000: account A-9895 received 6 transfers from 6 distinct senders between 1794319200000 and 1794322800000, 15000 minor units in total (T0035 to T0040, each 2500).  
  Claims: i2 (supported), e35 (supported), e40 (supported)
- **f4** All six contributions to A-9278 are passed on. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092), then T0008 (A-5092 to A-2897), then T0009 (A-2897 to A-4989). T0010, T0011 and T0012 link to T0014, then T0015, then T0016 along the same accounts. Chains reach 3 onward links at most. The route is A-9278, A-5092, A-2897, A-4989, and the money comes to rest only at A-4989 (T0009 and T0016 are not passed on). Each hop is a little smaller than the one before: 138000, 135000, 132000 and 210000, 206000, 202000.  
  Claims: p1 (supported), p2 (supported), r1 (supported), e7 (supported), e8 (supported), e9 (supported), e14 (supported), e15 (supported), e16 (supported), a6 (supported), a7 (supported)
- **f5** Only three of the six contributions to A-9895 are passed on. T0038, T0039 and T0040 link to T0041 (A-9895 to A-1415, 14000), which has no onward link. T0035, T0036 and T0037 have no onward link. Chains reach 1 onward link at most, the route accounts are A-9895 and A-1415, and the money comes to rest at A-1415. A-1415's later transfer T0055 (90000 to A-9514) is not recorded as an onward link, and T0055 itself is not passed on.  
  Claims: p3 (supported), r2 (supported), e41 (supported), e55 (supported), a2 (supported), a3 (supported), a4 (supported), a5 (supported), a8 (supported)
- **f6** Shared devices on routes: for the A-9278 alert, device D-568 sent every recorded transfer from route accounts A-9278, A-5092 and A-2897 (T0007, T0008, T0009, T0014, T0015, T0016). The resting account A-4989 sent nothing. For the A-9895 alert, no device was used by two or more route accounts: A-9895 sent from D-699 and A-1415 from D-785.  
  Claims: s1 (supported), e7 (supported), e8 (supported), e9 (supported), e14 (supported), e15 (supported), e16 (supported), a1 (supported), e41 (supported), e55 (supported)
- **f7** Both indicators have the same shape: 6 senders and 6 transfers in one hour. What sets them apart is the recorded relationships. A-9278 passes on every contribution through a 3-hop chain that ends at one account, and all three sending accounts on that route used one device (D-568). A-9895 passes on half its contributions in a single hop, no device is shared on its route, and its 6 contributions are small and identical (2500 each, 15000 in total, compared with 357000). So the A-9278 alert comes with corroborating relationships that go beyond the fan-in. The A-9895 alert rests mostly on the fan-in count alone.  
  Claims: i1 (supported), i2 (supported), r1 (supported), r2 (supported), s1 (supported), a1 (supported), a2 (supported), a3 (supported), a4 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** A-9278, A-5092 and A-2897 might be run by one party or through one device, which would make the chain to A-4989 look like layering (pass-through accounts) of collected funds. Sharing a device does not prove ownership or identity, and the onward links are based on timing, not proof that the same money moved.  
  References: s1, r1, p1, p2
- **h2** The A-9895 fan-in (six identical 2500 payments) could be ordinary collection activity, such as a shared bill or a pool, rather than mule activity. Its one-hop forwarding to A-1415 is weaker evidence than the A-9278 pattern.  
  References: i2, r2, a1
- **h3** A-1415's 90000 payment to A-9514 (T0055) is larger than anything A-1415 received in this dataset. That could point to funds from outside the dataset, or to a later stage of movement the 30-minute onward rule does not capture.  
  References: e55, a8, e41

## Unresolved questions

- **u1** Who controls A-4989, and what happened to the funds after they arrived there? The dataset records no outgoing transfer from A-4989.  
  References: r1, a6, a7
- **u2** Do D-568 sessions belong to one person or to a shared or aggregator device? The data records only device ids.  
  References: s1
- **u3** Where did the money A-1415 sent in T0055 come from, and was it connected to the A-9895 funds at all? It falls outside the onward gap, and its amount is more than A-1415 is recorded as receiving.  
  References: e55, e41
- **u4** What happened to the A-9895 contributions that were not passed on (T0035, T0036, T0037)? The data cannot say whether they stayed in the account or left later through a payment the 30-minute onward rule does not link.  
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
| e35 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| e40 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
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
| a8 | absence | kind="no_onward_link_from_transfer", subject="T0055" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 31 of 31 claims supported; reference validity 1.0 (37 of 37 distinct ids resolve); 5 queries (0 failed), 3 model requests, 19277 input tokens (cache included) and 5514 output tokens, 66.9 s.
