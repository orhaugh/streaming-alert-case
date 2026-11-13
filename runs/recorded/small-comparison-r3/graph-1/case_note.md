# Case note: graph arm, run 1

Agent output, recorded run of 2026-11-13T18:40:30+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: this bounded replay (run run:72cf0e4b91a3; 55 dataset events; 3 of 3 jobs completed; clink exit status 0; not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms window; onward max gap 1,800,000 ms) holds 55 transfers, 48 accounts, 35 devices, 14 onward links and exactly 2 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: c-alerts (supported), c-transfers (supported), c-accounts (supported), c-devices (supported), c-links (supported)
- **F2** Alert 1, fan_in:A-9278:1794301200000: account A-9278, window 1794301200000 to 1794304800000, 6 distinct senders, 6 transfers, total 357000 minor units. The contributing transfers are T0002, T0003, T0006, T0010, T0011 and T0012, between 38000 and 89000 each, every one from a different sender and device.  
  Claims: i-9278 (supported), e-T0002 (supported), e-T0003 (supported), e-T0006 (supported), e-T0010 (supported), e-T0011 (supported), e-T0012 (supported)
- **F3** Alert 2, fan_in:A-9895:1794319200000: account A-9895, window 1794319200000 to 1794322800000, 6 distinct senders, 6 transfers, total 15000 minor units. The contributing transfers are T0035 to T0040, each exactly 2500, every one from a different sender and device.  
  Claims: i-9895 (supported), e-T0035 (supported), e-T0036 (supported), e-T0037 (supported), e-T0038 (supported), e-T0039 (supported), e-T0040 (supported)
- **F4** Alert 1 onward routes: all 6 contributing transfers are passed on. T0002, T0003 and T0006 link to T0007 (A-9278 to A-5092, 138000), then T0008 (A-5092 to A-2897, 135000), then T0009 (A-2897 to A-4989, 132000). T0010, T0011 and T0012 link to T0014 (A-9278 to A-5092, 210000), then T0015 (A-5092 to A-2897, 206000), then T0016 (A-2897 to A-4989, 202000). The longest chain has 3 onward links. T0009 and T0016 are not passed on, so A-4989 is the only resting account. Route accounts: A-9278, A-5092, A-2897, A-4989.  
  Claims: r-9278 (supported), p-9278-a (supported), p-9278-b (supported), p-9278-c (supported), p-9278-d (supported), p-9278-e (supported), p-9278-f (supported), e-T0007 (supported), e-T0008 (supported), e-T0009 (supported), e-T0014 (supported), e-T0015 (supported), e-T0016 (supported), ab-T0009 (supported), ab-T0016 (supported)
- **F5** Alert 2 onward routes: only 3 of the 6 contributing transfers are passed on. T0038, T0039 and T0040 each link to T0041 (A-9895 to A-1415, 14000), and T0041 is not passed on. The longest chain has 1 onward link, and A-1415 is the only resting account. T0035, T0036 and T0037 are not passed on, so they start no chain. Route accounts: A-9895, A-1415.  
  Claims: r-9895 (supported), p-9895-a (supported), p-9895-b (supported), p-9895-c (supported), e-T0041 (supported), ab-T0041 (supported), ab-T0035 (supported), ab-T0036 (supported), ab-T0037 (supported)
- **F6** Alert 1 shared device: route accounts A-9278, A-5092 and A-2897 all sent from device D-568. Every onward transfer on alert 1's routes (T0007, T0008, T0009, T0014, T0015, T0016) was sent from D-568. The resting account A-4989 sent no transfers in this dataset.  
  Claims: sd-568 (supported), e-T0007 (supported), e-T0008 (supported), e-T0009 (supported), e-T0014 (supported), e-T0015 (supported), e-T0016 (supported)
- **F7** Alert 2 shared device: no device was used to send by two or more of its route accounts (A-9895 sent T0041 from D-699). The only other shared device in the dataset, D-619 (A-2952, A-9652), is not on either alert's routes.  
  Claims: ab-route-9895 (supported), sd-619 (supported), e-T0041 (supported)
- **F8** What tells the alerts apart, given that both have 6 senders and 6 transfers inside one event-time hour: (a) Amounts: 357000 in varied amounts for alert 1, against 15000 in six identical 2500 transfers for alert 2. (b) Onward reach: for alert 1 all contributing transfers are passed on through 3 links to one resting account; for alert 2 half are passed on, through 1 link. (c) Devices: for alert 1, one device (D-568) sent every onward hop from three different route accounts; for alert 2 there is no device sharing on the route. (d) Timing: alert 1's onward hops follow each other 140000 to 195000 ms apart. None of the intermediate or resting route accounts (A-5092, A-2897, A-4989, A-1415) has a fan-in alert of its own.  
  Claims: i-9278 (supported), i-9895 (supported), r-9278 (supported), r-9895 (supported), sd-568 (supported), ab-route-9895 (supported), ab-fi-5092 (supported), ab-fi-2897 (supported), ab-fi-4989 (supported), ab-fi-1415 (supported), e-T0007 (supported), e-T0008 (supported), e-T0009 (supported), e-T0015 (supported), e-T0016 (supported)
- **F9** Traceable provenance: every figure above can be traced to the dataset's transfer ids (T0002 to T0041 as cited), the recorded onward link ids (for example onward:T0002:T0007, onward:T0038:T0041) and the run record holding dataset_sha256 72cf0e4b91a346f7a20187386d5b65f4821abf759b2752e13bee3a488efac880.  
  Claims: i-9278 (supported), i-9895 (supported), p-9278-a (supported), p-9895-a (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** Alert 1 matches a collection-and-layering pattern: funds gathered at A-9278, then moved quickly through A-5092 and A-2897 to A-4989, with every hop sent from one device. That could mean one party controls A-9278, A-5092 and A-2897. A shared device does not prove common ownership, identity or fraud.  
  References: sd-568, r-9278, p-9278-a, p-9278-d
- **H2** Alert 2 may be benign or low risk, for example identical small payments such as a split bill, subscription or collection, followed by one outgoing payment. It may also be a smaller mule pattern. The data does not decide between these.  
  References: i-9895, r-9895, ab-route-9895, ab-T0035, ab-T0036, ab-T0037
- **H3** In alert 1, each onward hop is slightly smaller than the one before (138000, 135000, 132000; 210000, 206000, 202000). One reading is that a fee or skim is kept at each hop. This is an interpretation only.  
  References: e-T0007, e-T0008, e-T0009, e-T0014, e-T0015, e-T0016

## Unresolved questions

- **U1** Who owns or controls the accounts using D-568 (A-9278, A-5092, A-2897), and how does A-4989 relate to them? The dataset records device use, not ownership.  
  References: sd-568, r-9278
- **U2** What happens to the funds at A-4989 and A-1415 after this replay? A-4989 sends nothing here. A-1415 later sends T0055 (from D-785), but no onward link was recorded for it. Events outside this bounded dataset cannot be assessed.  
  References: ab-T0009, ab-T0016, ab-T0041
- **U3** The onward transfers do not equal the linked credits: T0007 is 138000 against 141500 in linked credits, T0014 is 210000 against 215500, and T0041 is 14000 against 7500. What explains the gaps, such as other balances or credits outside the links, or fees? The recorded links do not account for the balances.  
  References: e-T0007, e-T0014, e-T0041, i-9278, i-9895
- **U4** How do the fan-in senders relate to each other or to the alerted accounts? Is there a victim or payer relationship? The dataset records only the transfers.  
  References: i-9278, i-9895

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e-T0002 | event | transfer="T0002", sender="A-4452", receiver="A-9278", amount_minor=42000, event_time_ms=1794301510000, device="D-940" | supported |
| e-T0003 | event | transfer="T0003", sender="A-4366", receiver="A-9278", amount_minor=61500, event_time_ms=1794301840000, device="D-479" | supported |
| e-T0006 | event | transfer="T0006", sender="A-7266", receiver="A-9278", amount_minor=38000, event_time_ms=1794302285000, device="D-307" | supported |
| e-T0010 | event | transfer="T0010", sender="A-8133", receiver="A-9278", amount_minor=89000, event_time_ms=1794303450000, device="D-587" | supported |
| e-T0011 | event | transfer="T0011", sender="A-6801", receiver="A-9278", amount_minor=50500, event_time_ms=1794303855000, device="D-850" | supported |
| e-T0012 | event | transfer="T0012", sender="A-3881", receiver="A-9278", amount_minor=76000, event_time_ms=1794304720000, device="D-530" | supported |
| e-T0007 | event | transfer="T0007", sender="A-9278", receiver="A-5092", amount_minor=138000, event_time_ms=1794302640000, device="D-568" | supported |
| e-T0008 | event | transfer="T0008", sender="A-5092", receiver="A-2897", amount_minor=135000, event_time_ms=1794302790000, device="D-568" | supported |
| e-T0009 | event | transfer="T0009", sender="A-2897", receiver="A-4989", amount_minor=132000, event_time_ms=1794302985000, device="D-568" | supported |
| e-T0014 | event | transfer="T0014", sender="A-9278", receiver="A-5092", amount_minor=210000, event_time_ms=1794305000000, device="D-568" | supported |
| e-T0015 | event | transfer="T0015", sender="A-5092", receiver="A-2897", amount_minor=206000, event_time_ms=1794305150000, device="D-568" | supported |
| e-T0016 | event | transfer="T0016", sender="A-2897", receiver="A-4989", amount_minor=202000, event_time_ms=1794305290000, device="D-568" | supported |
| e-T0035 | event | transfer="T0035", sender="A-8770", receiver="A-9895", amount_minor=2500, event_time_ms=1794319340000, device="D-535" | supported |
| e-T0036 | event | transfer="T0036", sender="A-4399", receiver="A-9895", amount_minor=2500, event_time_ms=1794319745000, device="D-450" | supported |
| e-T0037 | event | transfer="T0037", sender="A-4792", receiver="A-9895", amount_minor=2500, event_time_ms=1794320140000, device="D-887" | supported |
| e-T0038 | event | transfer="T0038", sender="A-9088", receiver="A-9895", amount_minor=2500, event_time_ms=1794320530000, device="D-443" | supported |
| e-T0039 | event | transfer="T0039", sender="A-8060", receiver="A-9895", amount_minor=2500, event_time_ms=1794321030000, device="D-832" | supported |
| e-T0040 | event | transfer="T0040", sender="A-8166", receiver="A-9895", amount_minor=2500, event_time_ms=1794321660000, device="D-413" | supported |
| e-T0041 | event | transfer="T0041", sender="A-9895", receiver="A-1415", amount_minor=14000, event_time_ms=1794322200000, device="D-699" | supported |
| i-9278 | indicator | indicator="fan_in:A-9278:1794301200000", account="A-9278", window_start_ms=1794301200000, window_end_ms=1794304800000, senders=6, transfers=6, total_minor=357000, contributing=["T0002", "T0003", "T0006", "T0010", "T0011", "T0012"] | supported |
| i-9895 | indicator | indicator="fan_in:A-9895:1794319200000", account="A-9895", window_start_ms=1794319200000, window_end_ms=1794322800000, senders=6, transfers=6, total_minor=15000, contributing=["T0035", "T0036", "T0037", "T0038", "T0039", "T0040"] | supported |
| p-9278-a | onward_path | transfers=["T0002", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9278-b | onward_path | transfers=["T0003", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9278-c | onward_path | transfers=["T0006", "T0007", "T0008", "T0009"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9278-d | onward_path | transfers=["T0010", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9278-e | onward_path | transfers=["T0011", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9278-f | onward_path | transfers=["T0012", "T0014", "T0015", "T0016"], from_indicator="fan_in:A-9278:1794301200000", comes_to_rest_at="A-4989" | supported |
| p-9895-a | onward_path | transfers=["T0038", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p-9895-b | onward_path | transfers=["T0039", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| p-9895-c | onward_path | transfers=["T0040", "T0041"], from_indicator="fan_in:A-9895:1794319200000", comes_to_rest_at="A-1415" | supported |
| r-9278 | onward_reach | indicator="fan_in:A-9278:1794301200000", max_depth=3, terminal_accounts=["A-4989"], route_accounts=["A-9278", "A-5092", "A-2897", "A-4989"] | supported |
| r-9895 | onward_reach | indicator="fan_in:A-9895:1794319200000", max_depth=1, terminal_accounts=["A-1415"], route_accounts=["A-9895", "A-1415"] | supported |
| sd-568 | shared_device | device="D-568", accounts=["A-9278", "A-5092", "A-2897"], on_route_of="fan_in:A-9278:1794301200000" | supported |
| sd-619 | shared_device | device="D-619", accounts=["A-2952", "A-9652"] | supported |
| ab-route-9895 | absence | kind="no_shared_device_on_route", subject="fan_in:A-9895:1794319200000" | supported |
| ab-T0035 | absence | kind="no_onward_link_from_transfer", subject="T0035" | supported |
| ab-T0036 | absence | kind="no_onward_link_from_transfer", subject="T0036" | supported |
| ab-T0037 | absence | kind="no_onward_link_from_transfer", subject="T0037" | supported |
| ab-T0009 | absence | kind="no_onward_link_from_transfer", subject="T0009" | supported |
| ab-T0016 | absence | kind="no_onward_link_from_transfer", subject="T0016" | supported |
| ab-T0041 | absence | kind="no_onward_link_from_transfer", subject="T0041" | supported |
| ab-fi-5092 | absence | kind="no_fan_in_alert_for_account", subject="A-5092" | supported |
| ab-fi-2897 | absence | kind="no_fan_in_alert_for_account", subject="A-2897" | supported |
| ab-fi-4989 | absence | kind="no_fan_in_alert_for_account", subject="A-4989" | supported |
| ab-fi-1415 | absence | kind="no_fan_in_alert_for_account", subject="A-1415" | supported |
| c-alerts | count | pattern="fan_in_alerts", value=2 | supported |
| c-transfers | count | pattern="transfers", value=55 | supported |
| c-links | count | pattern="onward_links", value=14 | supported |
| c-accounts | count | pattern="accounts", value=48 | supported |
| c-devices | count | pattern="devices", value=35 | supported |

## Score

Correctness 1.00 (7 of 7 required facts covered by supported claims); 50 of 50 claims supported; reference validity 1.0 (61 of 61 distinct ids resolve); 9 queries (0 failed), 4 model requests, 29976 input tokens (cache included) and 8719 output tokens, 100.8 s.
