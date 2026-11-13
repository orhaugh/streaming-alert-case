# Case note: fan-in alerts in a bounded replay

Agent output, recorded run of 2026-11-13T18:38:36+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f0** Scope: one bounded replay (run run:72cf0e4b91a3, 55 dataset events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms event-time window; onward links require a gap of at most 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f1** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000, 6 distinct senders, 6 transfers, total 357000 minor units (3,570.00). Contributing transfers: T0002, T0003, T0006, T0010, T0011, T0012, each from a different sender and device, amounts from 38000 to 89000.  
  Claims: i1 (supported), e02 (supported), e03 (supported), e06 (supported), e10 (supported), e11 (supported), e12 (supported)
- **f2** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000, 6 distinct senders, 6 transfers, total 15000 minor units (150.00). Contributing transfers: T0035, T0036, T0037, T0038, T0039, T0040, each exactly 2500, each from a different sender and device.  
  Claims: i2 (supported), e35 (supported), e36 (supported), e37 (supported), e38 (supported), e39 (supported), e40 (supported)
- **f3** Onward links for A-9278: all six contributing transfers are passed on. T0002, T0003 and T0006 link into T0007 (A-9278→A-5092, 138000), then T0008 (A-5092→A-2897, 135000), then T0009 (A-2897→A-4989, 132000). T0010, T0011 and T0012 link into T0014 (A-9278→A-5092, 210000), then T0015 (A-5092→A-2897, 206000), then T0016 (A-2897→A-4989, 202000). Each chain has at most 3 onward links. Route accounts: A-9278, A-5092, A-2897, A-4989. The money comes to rest only at A-4989: T0009 and T0016 are not passed on.  
  Claims: r1 (supported), p1a (supported), p1b (supported), p1c (supported), p1d (supported), p1e (supported), p1f (supported), e07 (supported), e08 (supported), e09 (supported), e14 (supported), e15 (supported), e16 (supported), x09 (supported), x16 (supported)
- **f4** Onward links for A-9895: only three of the six contributing transfers (T0038, T0039, T0040) are passed on, all into the single transfer T0041 (A-9895→A-1415, 14000), which is not passed on. T0035, T0036 and T0037 are not passed on. Chains have at most 1 onward link. Route accounts: A-9895, A-1415. Resting account: A-1415.  
  Claims: r2 (supported), p2a (supported), p2b (supported), p2c (supported), e41 (supported), x35 (supported), x36 (supported), x37 (supported), x41 (supported)
- **f5** Shared devices on routes: for the A-9278 alert, device D-568 was used to send by three of its route accounts, A-9278, A-5092 and A-2897. It sent all six onward transfers (T0007, T0008, T0009, T0014, T0015, T0016). The resting account A-4989 sent no transfers in this dataset. For the A-9895 alert, no device was used by two or more of its route accounts: A-9895 sent from D-699 and A-1415 sent from D-785.  
  Claims: s1 (supported), e07 (supported), e08 (supported), e09 (supported), e14 (supported), e15 (supported), e16 (supported), x1 (supported), e41 (supported), e55 (supported)
- **f6** The only other device used by more than one account in the dataset is D-619 (A-2952, A-9652). Neither account is on either alert's route.  
  Claims: s2 (supported)
- **f7** A-1415 later sent T0055 (90000 to A-9514, device D-785) at 1794333900000. That is 11,700,000 ms after T0041, well over the 1,800,000 ms onward gap, so it is not recorded as an onward link. None of the downstream accounts (A-5092, A-2897, A-4989, A-1415) has a fan-in alert of its own.  
  Claims: e55 (supported), e41 (supported), x41 (supported), xa1 (supported), xa2 (supported), xa3 (supported), xa4 (supported)
- **f8** What distinguishes the alerts: both have 6 senders and 6 transfers inside one hour, but the recorded relationships differ. (a) A-9278: all contributing credits are passed on within the gap, in two batches of three, through three hops to one resting account. Each hop takes slightly less than the one before (for example 138000 → 135000 → 132000), with gaps of 140,000–195,000 ms after the first hop. All three hops were sent from one device, D-568, by three different accounts. (b) A-9895: identical small credits; only half are linked onward, through a single hop of 14000. No device is shared on the route, and the resting account's later outflow falls outside the onward window. So the A-9278 alert is a fan-in followed by fast, layered, device-linked onward movement. The A-9895 alert is, as recorded, a fan-in with partial single-hop forwarding and no device linkage.  
  Claims: r1 (supported), r2 (supported), s1 (supported), x1 (supported), i1 (supported), i2 (supported), x35 (supported), x36 (supported), x37 (supported), e07 (supported), e08 (supported), e09 (supported), e14 (supported), e15 (supported), e16 (supported), e41 (supported)
- **f9** Traceable provenance: every value here is tied to dataset ids (transfers, onward links onward:Txxxx:Tyyyy, indicators fan_in:<account>:<window start>) in the run's graph store, which records dataset sha256 72cf0e4b91a3… and pipeline pipeline/case.sql.  
  Claims: i1 (supported), i2 (supported), c1 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** Because one device, D-568, sent every onward hop from A-9278 through A-5092 and A-2897 within minutes, a single operator may control those three accounts. That would fit a collection-and-layering (mule) pattern ending at A-4989. A shared device does not prove common ownership or fraud.  
  References: s1, r1, f3, f5
- **h2** The A-9895 alert (six identical 2500 credits, partial forwarding, no device linkage) may be benign collective payments such as a shared bill or group collection, and possibly a false positive of the fan-in rule. The data does not establish this.  
  References: i2, r2, x1, f4
- **h3** The small shortfall at each hop on the A-9278 route (about 3000–4000 per hop) could be fees or skimmed amounts kept by intermediaries. This is an interpretation only.  
  References: e07, e08, e09, e14, e15, e16

## Unresolved questions

- **u1** Where does money go after A-4989? It sent no transfers in this bounded dataset, so later movement, if any, is outside the data.  
  References: x09, x16, xa1
- **u2** A-9895 sent 14000 in T0041, while the three linked credits total 7500. Was T0041 funded partly by the unlinked credits T0035–T0037, or by a balance not visible here? The onward-link rule cannot say which credits funded a debit.  
  References: e41, x35, x36, x37
- **u3** A-1415 sent 90000 (T0055) after receiving only 14000 in this dataset. Its funding source and any connection to the alert are not recorded.  
  References: e55, e41
- **u4** Who are the people behind accounts and devices (for example D-568), and are the senders to A-9278 victims, complicit, or unrelated? The data holds no identity or ownership information.  
  References: s1, i1
- **u5** Did any activity before or after the replayed event file affect these accounts? Completeness beyond the 55 recorded events is not established.  
  References: c2

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e02 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| e03 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| e06 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| e10 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| e11 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| e12 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| e07 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| e08 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| e09 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| e14 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| e15 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| e16 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| e35 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| e36 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| e37 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| e38 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| e39 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| e40 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| e41 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| e55 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| i1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| i2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| p1a | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p1b | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p1c | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p1d | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p1e | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p1f | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p2a | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p2b | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p2c | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| r1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| r2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| s1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| s2 | shared_device | device="D-619", accounts=["A-2952", "A-9652"] | supported |
| x1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| x35 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| x36 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| x37 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| x41 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| x09 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| x16 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| xa1 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| xa2 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| xa3 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| xa4 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 51 of 51 claims supported; reference validity 1.0 (60 of 60 distinct ids resolve); 9 queries (0 failed), 5 model requests, 39971 input tokens (cache included) and 9292 output tokens, 112.7 s.
