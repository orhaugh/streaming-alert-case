# Case note: table arm, run 2

Agent output, recorded run of 2026-11-13T18:25:38+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: the bounded replay run:72cf0e4b91a3 (3 of 3 jobs completed, clink exit status 0, not cancelled) covers 55 transfers between 48 accounts, sent from 35 devices. It produced 2 fan-in alerts and 14 onward links. Thresholds: at least 5 distinct senders within a 3,600,000 ms window; onward gap of at most 1,800,000 ms. Everything below holds only for this dataset as this run processed it.  
  Claims: C-cnt-alerts (supported), C-cnt-transfers (supported), C-cnt-links (supported), C-cnt-accounts (supported), C-cnt-devices (supported)
- **F2** Alert fan_in:A-9278:1794301200000: account A-9278, window 1794301200000 to 1794304800000. It counts 6 distinct senders and 6 transfers totalling 357000 minor units. The contributing transfers are T0002, T0003, T0006, T0010, T0011 and T0012, with amounts from 38000 to 89000, each from a different sender and device.  
  Claims: I1 (supported), E-T0002 (supported), E-T0003 (supported), E-T0006 (supported), E-T0010 (supported), E-T0011 (supported), E-T0012 (supported)
- **F3** Alert fan_in:A-9895:1794319200000: account A-9895, window 1794319200000 to 1794322800000. It counts 6 distinct senders and 6 transfers totalling 15000 minor units. The contributing transfers are T0035 to T0040, each exactly 2500 and each from a different sender and device.  
  Claims: I2 (supported), E-T0035 (supported), E-T0036 (supported), E-T0037 (supported), E-T0038 (supported), E-T0039 (supported), E-T0040 (supported)
- **F4** Onward links from A-9278: all 6 contributing transfers are passed on, in two batches. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), then T0008 (A-5092 to A-2897, 135000), then T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (to A-2897, 206000), then T0016 (to A-4989, 202000). The longest chain has 3 onward links. The route accounts are A-9278, A-5092, A-2897 and A-4989. Both chains stop at A-4989: T0009 and T0016 are not passed on.  
  Claims: P1 (supported), P2 (supported), R1 (supported), E-T0007 (supported), E-T0008 (supported), E-T0009 (supported), E-T0014 (supported), E-T0015 (supported), E-T0016 (supported), AB-T0009 (supported), AB-T0016 (supported)
- **F5** Onward links from A-9895: only T0038, T0039 and T0040 link onward, all to T0041 (A-9895 to A-1415, 14000), which is not passed on. The longest chain has 1 onward link, and the route accounts are A-9895 and A-1415. T0035, T0036 and T0037 have no onward link, so under the run's rules their funds are recorded as stopping at A-9895. The terminal accounts are therefore A-1415 and A-9895. A-1415 does send T0055 (90000 to A-9514) later, but no onward link connects T0041 to T0055 (the gap is about 11,700,000 ms, above the 1,800,000 ms maximum).  
  Claims: P3 (supported), R2 (unsupported), E-T0041 (supported), E-T0055 (supported), AB-T0041 (supported), AB-T0035 (supported), AB-T0036 (supported), AB-T0037 (supported)
- **F6** Shared devices on the routes: for the A-9278 alert, device D-568 sent all six onward transfers (T0007, T0008, T0009, T0014, T0015, T0016) from three different route accounts: A-9278, A-5092 and A-2897. A-4989 sends nothing in the dataset. For the A-9895 alert, no device is shared among its route accounts: A-9895 sent from D-699 and A-1415 from D-785, and no other account used either device.  
  Claims: SD1 (supported), AB-SD2 (supported), E-T0007 (supported), E-T0008 (supported), E-T0009 (supported), E-T0041 (supported), E-T0055 (supported)
- **F7** Only one other device in the dataset was used by more than one sender: D-619, by A-9652 (T0019) and A-2952 (T0027), both paying A-5093. Neither account is on either alert's routes.  
  Claims: SD3 (supported), E-T0019 (supported), E-T0027 (supported)
- **F8** What tells the alerts apart: as indicators they look alike (6 senders and 6 transfers in one hour each). The recorded relationships differ in three ways. (a) Pass-through: A-9278 passed on all of its contributions, each batch within 1,800,000 ms, through a fixed 3-hop route (A-5092, A-2897, A-4989) with small drops in amount at each hop. A-9895 passed on only 3 of its 6 contributions, over 1 hop. (b) Shared device: A-9278's route shares D-568 across three sending accounts; A-9895's route shares no device. (c) Amounts: A-9278 received varied amounts totalling 357000; A-9895 received six identical 2500 transfers totalling 15000. So A-9278's alert sits inside a recorded multi-hop, single-device relay pattern, while A-9895's alert is a small, uniform fan-in with limited recorded onward movement.  
  Claims: I1 (supported), I2 (supported), R1 (supported), R2 (unsupported), SD1 (supported), AB-SD2 (supported), P1 (supported), P2 (supported), P3 (supported)
- **F9** Other accounts that received several transfers did not raise alerts. A-1823 received 6 transfers from only 3 senders (T0042 to T0048) and has no fan-in alert. The terminal account A-4989 and the account A-1415 also have no fan-in alert.  
  Claims: AB-A1823 (supported), AB-A4989 (supported), AB-A1415 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** The A-9278 pattern (fan-in, then fast forwarding through A-5092 and A-2897 to A-4989, with every hop sent from the single device D-568) could fit a mule or layering chain run by one operator. The data does not establish that: a shared device does not prove shared control or ownership.  
  References: F4, F6, SD1, R1
- **H2** The uniform 2500 contributions to A-9895 could fit a collection, split-bill, or small-payment pattern as easily as a fraud pattern. The data cannot tell these apart.  
  References: F3, I2
- **H3** A-1415's later 90000 transfer (T0055) might be partly funded by T0041 even though the run recorded no onward link. Its amount far exceeds T0041 (14000), so other funding sources outside the recorded links would be needed.  
  References: F5, E-T0055, AB-T0041

## Unresolved questions

- **U1** Who controls device D-568, and do A-9278, A-5092 and A-2897 share an owner? The dataset records only that the device was used to send.  
  References: SD1
- **U2** What happened to funds at A-4989 and A-1415 after this replay? There are no recorded debits from A-4989, and no recorded onward link from T0041; events outside the bounded dataset are not visible.  
  References: AB-T0009, AB-T0016, AB-T0041
- **U3** Where did the funds from T0035, T0036 and T0037 (7500 in total) go after reaching A-9895? T0041 (14000) is linked only to T0038, T0039 and T0040, and the dataset does not record account balances.  
  References: AB-T0035, AB-T0036, AB-T0037, P3
- **U4** Why do the forwarded amounts decrease slightly at each hop on the A-9278 route (for example 141500 in, then 138000, 135000 and 132000 out)? The data records no fees or other purpose.  
  References: P1, P2

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E-T0002 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| E-T0003 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| E-T0006 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| E-T0007 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| E-T0008 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| E-T0009 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| E-T0010 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| E-T0011 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| E-T0012 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| E-T0014 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| E-T0015 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| E-T0016 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| E-T0019 | event | transfer="T0019", sender="A-9652", receiver="A-5093", amount_minor=2350, event_time_ms=1794305700000, device="D-619" | supported |
| E-T0027 | event | transfer="T0027", sender="A-2952", receiver="A-5093", amount_minor=4120, event_time_ms=1794310800000, device="D-619" | supported |
| E-T0035 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| E-T0036 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| E-T0037 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| E-T0038 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| E-T0039 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| E-T0040 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| E-T0041 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| E-T0055 | event | transfer="T0055", sender="A-1415", receiver="A-9514", amount_minor=90000, event_time_ms=1794333900000, device="D-785" | supported |
| I1 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| I2 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| P1 | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P2 | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| P3 | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| R1 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| R2 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415", "A-9895"], route_accounts=["A-9895", "A-1415"] | unsupported: terminal_accounts are ['A-1415'], not ['A-1415', 'A-9895'] |
| SD1 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| SD3 | shared_device | device="D-619", accounts=["A-9652", "A-2952"] | supported |
| AB-SD2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| AB-T0009 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| AB-T0016 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| AB-T0041 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| AB-T0035 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| AB-T0036 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| AB-T0037 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| AB-A1823 | absence | kind="no_fan_in_alert_for_account", subject="A-1823" | supported |
| AB-A4989 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| AB-A1415 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| C-cnt-alerts | count | pattern="fan_in_alerts", value=2 | supported |
| C-cnt-transfers | count | pattern="transfers", value=55 | supported |
| C-cnt-links | count | pattern="onward_links", value=14 | supported |
| C-cnt-accounts | count | pattern="accounts", value=48 | supported |
| C-cnt-devices | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 45 of 46 claims supported; reference validity 1.0 (66 of 66 distinct ids resolve); 6 queries (0 failed), 4 model requests, 30924 input tokens (cache included) and 7901 output tokens, 96.3 s.
