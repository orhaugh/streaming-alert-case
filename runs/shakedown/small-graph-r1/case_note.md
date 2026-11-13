# Case note: fan-in alerts in a bounded replay

Agent output, live run of 2026-11-13T18:16:58+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: one bounded replay (run:72cf0e4b91a3, dataset sha256 72cf0e4b…c880, 55 events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms event-time window, onward max gap 1,800,000 ms). The graph holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **F1** Alert 1, fan_in:A-9278:1794301200000: account A-9278, window 1794301200000–1794304800000, 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002 (A-4452, 42000), T0003 (A-4366, 61500), T0006 (A-7266, 38000), T0010 (A-8133, 89000), T0011 (A-6801, 50500), T0012 (A-3881, 76000). Amounts vary, and each was sent from a different device.  
  Claims: i1 (supported), e02 (supported), e03 (supported), e06 (supported), e10 (supported), e11 (supported), e12 (supported)
- **F2** Alert 2, fan_in:A-9895:1794319200000: account A-9895, window 1794319200000–1794322800000, 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035 (A-8770), T0036 (A-4399), T0037 (A-4792), T0038 (A-9088), T0039 (A-8060), T0040 (A-8166), each exactly 2500, each from a different device.  
  Claims: i2 (supported), e35 (supported), e36 (supported), e37 (supported), e38 (supported), e39 (supported), e40 (supported)
- **F3** Alert 1 onward routes: all six contributing transfers have onward links. T0002, T0003 and T0006 link to T0007 (A-9278→A-5092, 138000), then T0008 (A-5092→A-2897, 135000), then T0009 (A-2897→A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278→A-5092, 210000), then T0015 (A-5092→A-2897, 206000), then T0016 (A-2897→A-4989, 202000). The longest chain is 3 onward links. Both routes come to rest at A-4989: T0009 and T0016 are not passed on.  
  Claims: r1 (unsupported), p1 (supported), p2 (supported), p3 (supported), p4 (supported), p5 (supported), p6 (supported), e07 (supported), e08 (supported), e09 (supported), e14 (supported), e15 (supported), e16 (supported), a6 (supported), a7 (supported)
- **F4** Alert 2 onward routes: only T0038, T0039 and T0040 have onward links, each a single link to T0041 (A-9895→A-1415, 14000). T0041 is not passed on, so these routes come to rest at A-1415 after at most 1 onward link. T0035, T0036 and T0037 have no onward link, so in this data their credits stop at A-9895. A-1415 does later send T0055 (90000 to A-9514, 1794333900000), but that is 11,700,000 ms after T0041, beyond the 1,800,000 ms onward gap, and is not a recorded onward link.  
  Claims: p7 (supported), p8 (supported), p9 (supported), e41 (supported), a2 (supported), a3 (supported), a4 (supported), a5 (supported), e55 (supported)
- **F5** Shared devices on routes. Alert 1: device D-568 sent all six onward transfers on its routes (T0007, T0014 from A-9278; T0008, T0015 from A-5092; T0009, T0016 from A-2897). So A-9278, A-5092 and A-2897 are the route accounts that sent from a device another route account also used. Alert 2: no device was used by two or more accounts on its routes. The only other device in the dataset used by more than one account, D-619 (A-2952, A-9652), is on neither alert's routes.  
  Claims: s1 (supported), a1 (supported)
- **F6** What distinguishes the alerts. Both meet the same threshold (6 senders, 6 transfers, one-hour window), but the recorded relationships differ. (a) Alert 1 passes on all its contributing credits; Alert 2 passes on only half. (b) Alert 1 runs 3 links deep through A-5092 and A-2897 to A-4989; Alert 2 is 1 link deep to A-1415. (c) On Alert 1's route each hop follows within 140000–195000 ms, and each forwarded amount is slightly smaller (138000→135000→132000; 210000→206000→202000). (d) All of Alert 1's onward transfers come from one device, D-568, used by three different route accounts; Alert 2's route has no shared device. (e) Alert 1's credits are varied and large (total 357000); Alert 2's are six equal 2500 credits (total 15000). None of the downstream accounts (A-5092, A-2897, A-4989, A-1415) has a fan-in alert of its own. Interpretation: Alert 1 sits on a fast, multi-hop, single-device chain, so it warrants priority review. Alert 2 is, on the recorded evidence, a simple collection with one partial forward, and the fan-in alert alone sets it apart.  
  Claims: i1 (supported), i2 (supported), r1 (unsupported), p1 (supported), p4 (supported), p7 (supported), e07 (supported), e08 (supported), e09 (supported), e14 (supported), e15 (supported), e16 (supported), s1 (supported), a1 (supported), a2 (supported), a3 (supported), a4 (supported), a8 (supported), a9 (supported), a10 (supported), a11 (supported)
- **F7** Onward links match by account and time, not by amount. T0007 (138000) is linked from credits totalling 141500; T0014 (210000) is linked from credits totalling 215500, and it falls 200000 ms after the alert window ends. T0041 (14000) is linked from credits totalling 7500. So the links do not show that particular funds moved; they show only that a debit followed credits within 1,800,000 ms.  
  Claims: e02 (supported), e03 (supported), e06 (supported), e07 (supported), e10 (supported), e11 (supported), e12 (supported), e14 (supported), e38 (supported), e39 (supported), e40 (supported), e41 (supported), p1 (supported), p4 (supported), p7 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-9278, A-5092 and A-2897 may be operated by the same person or group, because one device (D-568) sent every onward transfer among them within minutes. The data records shared device use only; it does not establish ownership or control.  
  References: s1, e07, e08, e09, e14, e15, e16
- **H2** Alert 1's pattern (many senders, consolidation, rapid multi-hop forwarding with small decrements, ending at A-4989) fits collection and layering, e.g. a money-mule chain. It is equally possible it has a legitimate explanation; nothing recorded establishes fraud.  
  References: i1, r1, p1, p4
- **H3** Alert 2's six equal 2500 credits and single partial forward to A-1415 may reflect a benign group collection (e.g. equal shares) rather than laundering. This is not established.  
  References: i2, p7, a1

## Unresolved questions

- **U1** Who uses device D-568, and why do three accounts send from it? The dataset records only device ids.  
  References: s1
- **U2** What happens to funds at A-4989 and A-1415 after this dataset ends? The bounded replay records no onward link from T0009, T0016 or T0041, and the run record does not show that activity outside the dataset is absent.  
  References: a5, a6, a7
- **U3** Is T0055 (A-1415→A-9514, 90000), which falls outside the onward gap and exceeds what A-1415 is recorded receiving here, related to T0041 at all? The data cannot say.  
  References: e55, e41
- **U4** What funded the gaps between linked credits and debits (e.g. T0041 at 14000 against 7500 in linked credits), and where did the unforwarded T0035–T0037 credits go? Account balances are not in the evidence.  
  References: e41, a2, a3, a4

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
| p1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p2 | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p3 | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p4 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p5 | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p6 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p7 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p8 | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p9 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| r1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-4452", "A-4366", "A-7266", "A-8133", "A-6801", "A-3881", "A-9278", "A-5092", "A-2897", "A-4989"] | unsupported: route_accounts are ['A-2897', 'A-4989', 'A-5092', 'A-9278'], not ['A-2897', 'A-3881', 'A-4366', 'A-4452', 'A-4989', 'A-5092', 'A-6801', 'A-7266', 'A-8133', 'A-9278'] |
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
| a10 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| a11 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 48 of 49 claims supported; reference validity 1.0 (60 of 60 distinct ids resolve); 8 queries (0 failed), 4 model requests, 31116 input tokens (cache included) and 10895 output tokens, 131.7 s.
