# Case note: fan-in alerts in a bounded replay (small case)

Agent output, recorded run of 2026-11-13T19:26:04+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **f0** Scope: this note covers only the bounded replay run:72cf0e4b91a3 (dataset sha256 72cf0e4b…, 55 events; 3 of 3 jobs completed; clink exit status 0; not cancelled; fan-in threshold 5 distinct senders in a 3,600,000 ms window; onward links allowed up to 1,800,000 ms gap). In this dataset there are 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts.  
  Claims: c1 (supported), c2 (supported), c3 (supported), c4 (supported), c5 (supported)
- **f1** Alert fan_in:A-9278:1794301200000: account A-9278, event-time window 1794301200000 to 1794304800000, 6 distinct senders, 6 transfers, total 357,000 minor units. Contributing transfers: T0002 (A-4452, 42,000), T0003 (A-4366, 61,500), T0006 (A-7266, 38,000), T0010 (A-8133, 89,000), T0011 (A-6801, 50,500), T0012 (A-3881, 76,000). Each was sent from a different device.  
  Claims: i1 (supported), e1 (supported), e2 (supported), e3 (supported), e4 (supported), e5 (supported), e6 (supported)
- **f2** Alert fan_in:A-9895:1794319200000: account A-9895, event-time window 1794319200000 to 1794322800000, 6 distinct senders, 6 transfers, total 15,000 minor units. Contributing transfers: T0035, T0036, T0037, T0038, T0039 and T0040, each exactly 2,500 minor units, from six different senders and six different devices.  
  Claims: i2 (supported), e13 (supported), e14 (supported), e15 (supported), e16 (supported), e17 (supported), e18 (supported)
- **f3** Onward paths for A-9278: all six contributing transfers have an onward link. T0002, T0003 and T0006 each link to T0007 (A-9278→A-5092), then T0008 (A-5092→A-2897), then T0009 (A-2897→A-4989). T0010, T0011 and T0012 each link to T0014 (A-9278→A-5092), then T0015 (A-5092→A-2897), then T0016 (A-2897→A-4989). The longest path has 3 onward links. The path accounts are A-9278, A-5092, A-2897 and A-4989. Every path ends at A-4989, because T0009 and T0016 have no further qualifying transfer in this dataset.  
  Claims: r1 (supported), p1 (supported), p2 (supported), p3 (supported), p4 (supported), p5 (supported), p6 (supported), e7 (supported), e8 (supported), e9 (supported), e10 (supported), e11 (supported), e12 (supported), a5 (supported), a6 (supported)
- **f4** Onward paths for A-9895: only T0038, T0039 and T0040 have an onward link, each to T0041 (A-9895→A-1415, 14,000). T0035, T0036 and T0037 have no onward link, so they start no path. The longest path has 1 onward link. The path accounts are A-9895 and A-1415, and every path ends at A-1415 because T0041 has no onward link in this dataset. A-1415's only recorded send, T0055 (90,000 to A-9514), falls at 1794333900000, 11,700,000 ms after T0041. That is outside the 1,800,000 ms onward gap, so no onward link is recorded, and T0055 itself has none.  
  Claims: r2 (supported), p7 (supported), p8 (supported), p9 (supported), e19 (supported), e20 (supported), a2 (supported), a3 (supported), a4 (supported), a7 (supported), a12 (supported)
- **f5** Shared devices on paths: for the A-9278 alert, device D-568 sent transfers from three of its path accounts: A-9278, A-5092 and A-2897. All six onward transfers (T0007, T0008, T0009, T0014, T0015, T0016) came from D-568. A-4989 sent no transfer in this dataset. For the A-9895 alert, no device was used by two or more of its path accounts (A-9895 sent from D-699; A-1415 sent from D-785).  
  Claims: s1 (supported), e7 (supported), e8 (supported), e9 (supported), e10 (supported), e11 (supported), e12 (supported), a1 (supported), e19 (supported), e20 (supported)
- **f6** The only other device in the dataset used by more than one account is D-619 (A-9652 sent T0019, A-2952 sent T0027, both to A-5093). Neither A-9652 nor A-2952 is on either alert's paths.  
  Claims: s2 (supported), e21 (supported), e22 (supported)
- **f7** What distinguishes the alerts: both have 6 senders and 6 transfers, so they look alike at the indicator level. The recorded relationships differ. (a) Amounts: A-9278 received varied amounts totalling 357,000; A-9895 received six identical 2,500 amounts totalling 15,000. (b) Onward coverage: every A-9278 contributing transfer has an onward link, but only 3 of 6 for A-9895. (c) Depth: A-9278's paths run 3 links through two intermediate accounts to A-4989, in two separate sequences; A-9895's paths stop after 1 link at A-1415. (d) Devices: A-9278's path accounts A-9278, A-5092 and A-2897 all sent from the same device D-568, while no device is shared on A-9895's paths. (e) Timing: on the A-9278 paths, the gaps between the onward transfers themselves are 140,000–195,000 ms. None of the downstream path accounts (A-5092, A-2897, A-4989, A-1415) has a fan-in alert.  
  Claims: i1 (supported), i2 (supported), r1 (supported), r2 (supported), s1 (supported), a1 (supported), a2 (supported), a3 (supported), a4 (supported), a8 (supported), a9 (supported), a10 (supported), a11 (supported), p1 (supported), p4 (supported), p7 (supported)

## Hypotheses

Interpretations the data does not establish.

- **h1** The A-9278 alert may reflect a coordinated pattern: several inbound credits, followed within minutes by repeated 3-step sequences of debits all sent from the single device D-568, with each step slightly smaller (138,000→135,000→132,000; 210,000→206,000→202,000). This is consistent with, but does not establish, one operator controlling A-9278, A-5092 and A-2897. The onward links record timing only; they do not show that the same funds moved, and a shared device does not show shared ownership or identity.  
  References: s1, r1, p1, p4, e7, e8, e9, e10, e11, e12
- **h2** The A-9895 alert may be a more benign collection pattern, for example six people each paying an identical 2,500 contribution, followed by one later debit. Only half the credits have an onward link, there is a single shallow link and no device is shared, so the indicator alone is weak. This interpretation is not established by the data.  
  References: i2, r2, a1, a2, a3, a4, e19
- **h3** In arithmetic, T0007 (138,000) is close to the sum of T0002+T0003+T0006 (141,500), and T0014 (210,000) is close to T0010+T0011+T0012 (215,500). This could suggest aggregation at A-9278, but the dataset records only timing links, not the movement of funds.  
  References: e1, e2, e3, e4, e5, e6, e7, e10

## Unresolved questions

- **u1** Who owns or operates device D-568, and are A-9278, A-5092 and A-2897 controlled by the same party? The dataset records device use only, not ownership or identity.  
  References: s1
- **u2** What happens at A-4989 and A-1415 after the paths end? The paths end only because no qualifying transfer exists in this bounded dataset; activity outside it is unknown.  
  References: r1, r2, a5, a6, a7
- **u3** Did A-9278 or A-9895 have credits or debits outside this replay that would change the alert windows or the onward links? The run record covers only the 55 events processed.  
  References: i1, i2
- **u4** What was the purpose of the six identical 2,500 payments to A-9895, and of the debits from A-9278? The dataset has no transaction descriptions or counterparty relationships.  
  References: i2, e7, e10, e19

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
| e21 | event | transfer="T0019", sender="A-9652", receiver="A-5093", amount_minor=2350, event_time_ms=1794305700000, device="D-619" | supported |
| e22 | event | transfer="T0027", sender="A-2952", receiver="A-5093", amount_minor=4120, event_time_ms=1794310800000, device="D-619" | supported |
| i1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| i2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| p1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p2 | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p3 | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p4 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p5 | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p6 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", ends_at="A-4989" | supported |
| p7 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", ends_at="A-1415" | supported |
| p8 | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", ends_at="A-1415" | supported |
| p9 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", ends_at="A-1415" | supported |
| r1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| r2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| s1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| s2 | shared_device | device="D-619", accounts=["A-2952", "A-9652"] | supported |
| a1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| a2 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| a3 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| a4 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| a5 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| a6 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| a7 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| a8 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| a9 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| a10 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| a11 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| a12 | absence | kind="no_onward_link_from_transfer", subject="T0055" | supported |
| c1 | count | pattern="fan_in_alerts", value=2 | supported |
| c2 | count | pattern="transfers", value=55 | supported |
| c3 | count | pattern="onward_links", value=14 | supported |
| c4 | count | pattern="accounts", value=48 | supported |
| c5 | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 54 of 54 claims supported; reference validity 1.0 (63 of 63 distinct ids resolve); 13 queries (0 failed), 7 model requests, 73880 input tokens (cache included) and 9976 output tokens, 122.5 s.
