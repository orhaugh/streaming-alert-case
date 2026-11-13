# Case note: table arm, run 2

Agent output, recorded run of 2026-11-13T18:43:18+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f1** Scope: the bounded replay run:72cf0e4b91a3 (55 events, 3 of 3 jobs completed, clink exit 0, not cancelled; fan-in threshold 5 distinct senders per 1-hour event-time window, onward gap up to 30 min). It contains 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Nothing here covers events outside this run.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000 to 1794304800000, 6 distinct senders, 6 transfers, total 357000 minor units. Contributing transfers: T0002, T0003, T0006, T0010, T0011, T0012, with amounts from 38000 to 89000.  
  Claims: i1 (supported), e1 (supported), e2 (supported), e3 (supported), e4 (supported), e5 (supported), e6 (supported)
- **f3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000 to 1794322800000, 6 distinct senders, 6 transfers, total 15000 minor units. Contributing transfers: T0035 to T0040, each exactly 2500.  
  Claims: i2 (supported), e13 (supported), e14 (supported), e15 (supported), e16 (supported), e17 (supported), e18 (supported)
- **f4** Onward routes for A-9278: all six contributing transfers have recorded onward links. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), then T0008 (A-5092 to A-2897, 135000), then T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (to A-2897, 206000), then T0016 (to A-4989, 202000). The longest chain has 3 onward links. Money comes to rest at A-4989 only: T0009 and T0016 were not passed on. Route accounts: A-9278, A-5092, A-2897, A-4989.  
  Claims: p1 (supported), p2 (supported), p3 (supported), p4 (supported), p5 (supported), p6 (supported), r1 (supported), e7 (supported), e8 (supported), e9 (supported), e10 (supported), e11 (supported), e12 (supported), a5 (supported), a6 (supported)
- **f5** Onward routes for A-9895: only T0038, T0039 and T0040 have a recorded onward link, each to T0041 (A-9895 to A-1415, 14000). T0035, T0036 and T0037 were not passed on, so they start no chain. The longest chain has 1 onward link. Money comes to rest at A-1415: T0041 was not passed on. Route accounts: A-9895, A-1415.  
  Claims: p7 (supported), p8 (supported), p9 (supported), r2 (supported), e19 (supported), a2 (supported), a3 (supported), a4 (supported), a7 (supported)
- **f6** Shared devices on the routes: for A-9278, device D-568 sent every transfer from route accounts A-9278, A-5092 and A-2897 (T0007, T0008, T0009, T0014, T0015, T0016). A-4989 sent no transfers. For A-9895, no device was used by two or more route accounts.  
  Claims: s1 (supported), e7 (supported), e8 (supported), e9 (supported), e10 (supported), e11 (supported), e12 (supported), a1 (supported)
- **f7** The only other device used by more than one sending account in the dataset is D-619 (A-9652 and A-2952). Neither account is on either alert's routes.  
  Claims: s2 (supported)
- **f8** What distinguishes the alerts: as indicators they look alike (6 senders and 6 transfers each within one hour). The recorded relationships differ. (a) A-9278: all 6 credits are passed on, through a 3-hop chain repeated twice, A-9278 to A-5092 to A-2897 to A-4989. Each hop keeps most of the amount (138000, 135000, 132000 and 210000, 206000, 202000), and the hops come within minutes of each other (gaps of 140000 to 195000 ms after the first hop). All three intermediate senders used the same device, D-568. (b) A-9895: 6 identical 2500 credits; only 3 are linked onward, through a single hop to A-1415; no shared device on the route. So the A-9278 alert is backed by a multi-hop onward structure and device overlap, while the A-9895 alert rests on the fan-in count and one short onward hop.  
  Claims: i1 (supported), i2 (supported), r1 (supported), r2 (supported), s1 (supported), a1 (supported), p1 (supported), p4 (supported), p7 (supported)
- **f9** A-1415 later sent T0055 (90000 to A-9514), 11700000 ms after receiving T0041. That is beyond the onward gap, and no onward link was recorded from T0041.  
  Claims: e20 (supported), a7 (supported)
- **f10** Accounts A-9862 and A-1823 each received repeated small transfers from several senders but have no fan-in alert. In this data they had fewer than 5 distinct senders.  
  Claims: a8 (supported), a9 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** The A-9278 pattern (fan-in, quick pass-through of most of the value over three hops, all hops sent from one device D-568) fits an account chain that one party controls, as in a mule or layering structure, with A-4989 as the collection point. The data records shared device use and onward links only. It does not establish who controls the accounts, or any fraud.  
  References: f4, f6, f8
- **h2** The A-9895 pattern (six identical 2500 payments, a partial single-hop pass-on, no device overlap) may be benign group collection, such as a shared bill or event fee, or a weaker form of the same behaviour. The data does not tell them apart.  
  References: f3, f5, f8
- **h3** The D-568 overlap could reflect one person operating three accounts, a shared or household device, or a device identifier artefact. Which one cannot be decided from the data.  
  References: f6

## Unresolved questions

- **u1** Who owns or controls A-9278, A-5092, A-2897 and A-4989, and what does device D-568 really represent? Transfers and device ids do not establish identity.  
  References: s1, r1
- **u2** What happens to the funds at A-4989 and A-1415 after this bounded replay? Neither shows a recorded onward link within the dataset.  
  References: a5, a6, a7
- **u3** Where did A-1415's 90000 for T0055 come from? It is far more than the 14000 received in T0041, and no other credits to A-1415 are recorded in this dataset.  
  References: e19, e20
- **u4** Why were T0035 to T0037 not passed on? The data does not show whether those funds stayed at A-9895 or left through channels not recorded here.  
  References: a2, a3, a4

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e1 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| e2 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| e3 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| e4 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| e5 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| e6 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| e7 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| e8 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| e9 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| e10 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| e11 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| e12 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| e13 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| e14 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| e15 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| e16 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| e17 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| e18 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| e19 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| e20 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
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
| s2 | shared_device | device="D-619", accounts=["A-9652", "A-2952"] | supported |
| a1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| a2 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| a3 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| a4 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| a5 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| a6 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| a7 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| a8 | absence | kind="no_fan_in_alert_for_account", subject="A-9862" | supported |
| a9 | absence | kind="no_fan_in_alert_for_account", subject="A-1823" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 49 of 49 claims supported; reference validity 1.0 (62 of 62 distinct ids resolve); 6 queries (0 failed), 4 model requests, 30577 input tokens (cache included) and 7157 output tokens, 84.6 s.
