# Case note: table arm, run 3

Agent output, recorded run of 2026-11-13T18:30:49+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: the bounded replay run:72cf0e4b91a3 (55 dataset events, 3/3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms window; onward max gap 1,800,000 ms). It holds 55 transfers, 48 accounts, 35 devices, 14 onward links and 2 fan-in alerts. Everything below applies only to this dataset as this run processed it.  
  Claims: C-cnt-alerts (supported), C-cnt-transfers (supported), C-cnt-links (supported), C-cnt-accounts (supported), C-cnt-devices (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278 received 6 transfers from 6 distinct senders in the window [1794301200000, 1794304800000), 357,000 minor units in total. The contributing transfers are T0002, T0003, T0006, T0010, T0011, T0012.  
  Claims: I1 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895 received 6 transfers from 6 distinct senders in the window [1794319200000, 1794322800000), 15,000 minor units in total (6 x 2,500). The contributing transfers are T0035 to T0040.  
  Claims: I2 (supported)
- **F4** Onward links for alert A-9278: all 6 contributing transfers lead into onward chains of 3 links each, so max depth is 3. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138,000), then T0008 (A-5092 to A-2897, 135,000), then T0009 (A-2897 to A-4989, 132,000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210,000), then T0015 (A-5092 to A-2897, 206,000), then T0016 (A-2897 to A-4989, 202,000). Neither T0009 nor T0016 is passed on, so both chains come to rest at A-4989. The route accounts are A-9278, A-5092, A-2897 and A-4989.  
  Claims: P1 (supported), P2 (supported), P3 (supported), R1 (supported), E7 (supported), E8 (supported), E9 (supported), E14 (supported), E15 (supported), E16 (supported), X-T0009 (supported), X-T0016 (supported)
- **F5** Onward links for alert A-9895: only T0038, T0039 and T0040 are linked onward, each to T0041 (A-9895 to A-1415, 14,000, event time 1794322200000). T0035, T0036 and T0037 have no onward link. T0041 is not passed on: A-1415's later transfer T0055 (90,000 to A-9514 at 1794333900000) comes 11,700,000 ms after T0041, beyond the 1,800,000 ms onward gap, and is not a recorded onward link. Max depth is 1, the money comes to rest at A-1415, and the route accounts are A-9895 and A-1415.  
  Claims: P4 (supported), R2 (supported), E41 (supported), E55 (supported), X-T0041 (supported), X-T0035 (supported), X-T0036 (supported), X-T0037 (supported)
- **F6** Shared devices on routes: for alert A-9278, device D-568 sent all six onward transfers (T0007, T0014 from A-9278; T0008, T0015 from A-5092; T0009, T0016 from A-2897). So three of its route accounts, A-9278, A-5092 and A-2897, sent from the same device. The terminal account A-4989 sends nothing in this dataset. For alert A-9895, no device was used by two or more of its route accounts: A-9895 sent from D-699 and A-1415 sent from D-785.  
  Claims: S1 (supported), E7 (supported), E8 (supported), E9 (supported), E14 (supported), E15 (supported), E16 (supported), X-dev-A9895 (supported), E41 (supported), E55 (supported)
- **F7** What sets the alerts apart: as fan-in indicators they look alike (6 senders, 6 transfers, one hour each). They differ in three recorded relationships. (a) Depth: A-9278 has 3-hop chains through two intermediate accounts to a single resting account, A-4989. A-9895 has a single hop to A-1415. (b) Coverage: every A-9278 contributing transfer is linked onward, and each onward debit is only slightly smaller than the linked credits (141,500 in, 138,000 out; 215,500 in, 210,000 out), shrinking by 3,000 to 4,000 per hop. Only 3 of the 6 A-9895 credits are linked, and the one onward debit (14,000) is larger than its linked credits (7,500). (c) Devices: A-9278's route accounts share device D-568, and the A-9895 route has no shared device. So A-9278 is a fan-in followed by quick multi-hop pass-through sent from one device. A-9895 is a fan-in of identical small amounts with one onward transfer.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (supported), S1 (supported), X-dev-A9895 (supported), E7 (supported), E14 (supported), E41 (supported)
- **F8** The resting accounts A-4989 and A-1415 have no fan-in indicator of their own in this dataset.  
  Claims: X-alert-A4989 (supported), X-alert-A1415 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** The A-9278 pattern (pooling from 6 senders, rapid 3-hop pass-through to A-4989, and all hops sent from device D-568) is consistent with a layering or mule chain where one operator controls A-9278, A-5092 and A-2897. A shared device does not prove common ownership or control.  
  References: F4, F6, S1, R1
- **H2** The A-9895 pattern (six identical 2,500 credits, then one 14,000 debit and no shared device on the route) could equally fit a benign collection, such as a group payment or a split bill, followed by one payout. It could also fit an early-stage collection account. The data does not tell these apart.  
  References: F3, F5, I2
- **H3** T0035 to T0037 fall outside the 1,800,000 ms onward gap, so they are not linked. The 14,000 in T0041 is close to the 15,000 total received, so all six credits may have funded it economically. The link rule records only timing, not where the money came from.  
  References: F5, P4

## Unresolved questions

- **U1** What happens to funds at A-4989 and A-1415 beyond this bounded replay? A-4989 sends nothing here, and A-1415's T0055 (90,000) is larger than anything it received in the dataset.  
  References: R1, R2, E55
- **U2** Who holds or uses device D-568, and are A-9278, A-5092 and A-2897 controlled by the same party? The dataset records only the device on each transfer.  
  References: S1
- **U3** Are the six senders to each alerted account linked in any way outside this dataset, such as victims, customers or coordinated accounts? None of them shares a device with the route accounts here.  
  References: I1, I2

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E7 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| E8 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| E9 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| E14 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| E15 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| E16 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| E41 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| E55 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P4 | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| S1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| X-dev-A9895 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| X-T0009 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| X-T0016 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| X-T0041 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| X-T0035 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| X-T0036 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| X-T0037 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| X-alert-A4989 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| X-alert-A1415 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C-cnt-alerts | count | pattern="fan_in_alerts", value=2 | supported |
| C-cnt-transfers | count | pattern="transfers", value=55 | supported |
| C-cnt-links | count | pattern="onward_links", value=14 | supported |
| C-cnt-accounts | count | pattern="accounts", value=48 | supported |
| C-cnt-devices | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 31 of 31 claims supported; reference validity 1.0 (33 of 33 distinct ids resolve); 5 queries (0 failed), 3 model requests, 19046 input tokens (cache included) and 6086 output tokens, 73.2 s.
