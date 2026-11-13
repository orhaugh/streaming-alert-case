# Case note: large case, graph arm, run 3

Agent output, recorded run of 2026-11-13T19:38:48+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: run run:5ce89f521e5e was a bounded replay of 50,000 events (dataset sha256 5ce89f52…). All 3 jobs completed, clink exited with status 0 and the run was not cancelled. Parameters: fan-in needs at least 5 distinct senders in a 3,600,000 ms event-time window, and onward links need a gap of at most 1,800,000 ms. The graph holds 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F1** Alert fan_in:A-37573:1794823200000: A-37573 received 7 transfers from 7 distinct senders in window 1794823200000–1794826800000, total 379,500 minor units (T003057, T003091, T003124, T003154, T003248, T003287, T003319). Every contributing transfer starts a path of 4 onward links. The paths form two parallel sequences. T003057/T003091/T003124/T003154 link to T003168→T003182→T003201→T003222, and T003248/T003287/T003319 link to T003391→T003416→T003433→T003454. Both sequences run through the same accounts, A-37573→A-38045→A-93288→A-63022→A-54215, and every path ends at A-54215 with no further qualifying transfer in this dataset. Max depth is 4. Path accounts: A-37573, A-38045, A-93288, A-63022, A-54215.  
  Claims: I1 (supported), P1 (supported), P2 (supported), R1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported), E7 (supported), E8 (supported), N14 (supported), N15 (supported)
- **F2** On the A-37573 alert's paths, device D-45880 was used to send by four path accounts: A-37573, A-38045, A-93288 and A-63022. All eight onward transfers (T003168, T003182, T003201, T003222, T003391, T003416, T003433, T003454) were sent from D-45880.  
  Claims: S1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported), E7 (supported), E8 (supported)
- **F3** Alert fan_in:A-85921:1794855600000: A-85921 received 6 transfers from 6 distinct senders in window 1794855600000–1794859200000, total 15,000. Each contributing transfer was 2,500. Four of them (T005750, T005789, T005830, T005868) link to one onward transfer, T005888 (9,500 to A-10758), and the paths end at A-10758. The later two (T005934, T005978) have no onward link. Max depth is 1. Path accounts: A-85921, A-10758. No device was used to send by two or more of these path accounts.  
  Claims: I2 (supported), P3 (supported), R2 (supported), E9 (supported), E24 (supported), E25 (supported), N11 (supported), N12 (supported), N16 (supported), N1 (supported)
- **F4** Alert fan_in:A-10859:1794924000000: A-10859 received 6 transfers from 6 distinct senders in window 1794924000000–1794927600000, total 204,000. The paths branch. A-10859 sent T011583 and T011670 to A-78340. From A-78340, T011695 ends at A-85287, and T011600 continues to A-75793, then T011628 ends at A-92332. Max depth is 3. Path accounts: A-10859, A-78340, A-75793, A-85287, A-92332. The paths end at A-85287 and A-92332.  
  Claims: I3 (supported), P4 (supported), P5 (supported), P6 (supported), R3 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), E14 (supported), N17 (supported), N18 (supported)
- **F5** On the A-10859 alert's paths, device D-79802 was used to send by A-10859 (T011583, T011670) and by A-78340 (T011600, T011695). The third-hop transfer T011628 from A-75793 used a different device, D-10265.  
  Claims: S2 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), E14 (supported)
- **F6** Alert fan_in:A-28137:1795003200000: A-28137 received 7 transfers from 7 distinct senders in window 1795003200000–1795006800000, total 29,500. None of its 7 contributing transfers has an onward link, so the alert has no onward paths. Max depth is 0 and the only path account is A-28137. A-28137's only outgoing transfer in the dataset, T018852 (21,000 to A-87539, at 1795013700000), came 7,440,000 ms after the last contributing credit T018248. That is outside the 1,800,000 ms onward window.  
  Claims: I4 (supported), R4 (supported), N2 (supported), N4 (supported), N5 (supported), N6 (supported), N7 (supported), N8 (supported), N9 (supported), N10 (supported), E21 (supported), E23 (supported)
- **F7** Alert fan_in:A-83577:1795057200000: A-83577 received 8 transfers from 8 distinct senders in window 1795057200000–1795060800000, total 174,500. All 8 contributing transfers link to T022572, which starts one path of 5 onward links: A-83577→A-56768→A-83094→A-43725→A-14799→A-39382 (T022572, T022592, T022609, T022629, T022649). The path ends at A-39382. Max depth is 5, the longest of the six alerts.  
  Claims: I5 (supported), P7 (supported), R5 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported), E19 (supported), N19 (supported)
- **F8** On the A-83577 alert's paths, device D-40018 was used to send by A-83094 (T022609) and A-14799 (T022649), which are not adjacent on the path. D-40018 was also used by A-34114, which is not one of this alert's path accounts. Each of the other three onward transfers used its own device (D-73452, D-96125, D-13859).  
  Claims: S3 (supported), S4 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported), E19 (supported)
- **F9** Alert fan_in:A-20636:1795190400000: A-20636 received 6 transfers from 6 distinct senders in window 1795190400000–1795194000000, total 36,000. Five contributing transfers link to T033506 (30,000 to A-36729), and the paths end at A-36729. The first, T033316, has no onward link. Max depth is 1. Path accounts: A-20636, A-36729. No device was shared among them. A-36729's only outgoing transfer, T034128, came 7,800,000 ms after T033506, outside the onward window.  
  Claims: I6 (supported), P8 (supported), R6 (supported), E20 (supported), E22 (supported), E26 (supported), N13 (supported), N20 (supported), N3 (supported)
- **F10** None of the accounts where paths end (A-54215, A-10758, A-85287, A-92332, A-39382, A-36729) has a fan-in alert of its own.  
  Claims: N21 (supported), N22 (supported), N23 (supported), N24 (supported), N25 (supported), N26 (supported), C1 (supported)
- **F11** What sets the alerts apart, given that all six are fan-in alerts with 6–8 distinct senders and one transfer per sender: the recorded relationships after the fan-in differ. (a) A-28137 has no onward links at all. (b) A-85921 and A-20636 each have one onward hop to an account that ends the path, and no shared device. (c) A-37573, A-10859 and A-83577 have multi-hop paths (depth 4, 3 and 5), and in each, two or more path accounts sent from a common device. The overlap is strongest for A-37573: one device, D-45880, sent every onward transfer from four accounts. A-10859 shares D-79802 across its first two hops. A-83577 shares D-40018 between two non-adjacent accounts, and that device was also used off-route by A-34114.  
  Claims: R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), S4 (supported), N1 (supported), N2 (supported), N3 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** In the A-37573 alert, four path accounts sent from the single device D-45880. Two short bursts of onward transfers followed each group of credits, with slightly declining amounts per hop. This could mean the accounts are controlled together, but the data does not show ownership, identity or that the same funds moved. It is an interpretation to check first.  
  References: S1, P1, P2, R1
- **H2** The A-10859 and A-83577 alerts show a partial device overlap along multi-hop paths. That might reflect related operators on parts of the route, or simply shared or public devices. The data cannot tell these apart. A-34114's off-route use of D-40018 makes the shared-device case for A-83577 weaker.  
  References: S2, S3, S4, R3, R5
- **H3** The A-28137 alert (no onward links), and to a lesser degree the A-85921 and A-20636 alerts (one hop, no shared device), fit benign collection activity, such as small uniform payments to one recipient, as well as they fit mule activity. As indicators they are weaker than the multi-hop, device-sharing alerts.  
  References: R4, R2, R6, N1, N2, N3

## Unresolved questions

- **U1** Do the onward transfers carry the same funds as the contributing credits? Onward links record only timing (a debit within 30 minutes of a credit), so this dataset cannot answer it.  
  References: P1, P7, R3
- **U2** Where did anything go after the path ends (A-54215, A-10758, A-85287, A-92332, A-39382, A-36729)? A path ending means only that there is no further qualifying transfer in this bounded dataset. Activity outside the replay is unknown.  
  References: R1, R2, R3, R5, R6
- **U3** Who owns or uses devices D-45880, D-79802 and D-40018? Is D-40018's use by A-34114 related to the A-83577 route? The graph records device use, not identity.  
  References: S1, S2, S3, S4
- **U4** Are the contributing senders related to each other or to the path accounts? Senders were not examined beyond their contributing transfers, and they are by definition not part of the path accounts.  
  References: I1, I2, I3, I4, I5, I6

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E1 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| E2 | event | transfer="T003182", sender="A-38045", receiver="A-93288", amount_minor=191000, event_time_ms=1794824940000, device="D-45880" | supported |
| E3 | event | transfer="T003201", sender="A-93288", receiver="A-63022", amount_minor=187500, event_time_ms=1794825180000, device="D-45880" | supported |
| E4 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| E5 | event | transfer="T003391", sender="A-37573", receiver="A-38045", amount_minor=176000, event_time_ms=1794827520000, device="D-45880" | supported |
| E6 | event | transfer="T003416", sender="A-38045", receiver="A-93288", amount_minor=172500, event_time_ms=1794827700000, device="D-45880" | supported |
| E7 | event | transfer="T003433", sender="A-93288", receiver="A-63022", amount_minor=169000, event_time_ms=1794827940000, device="D-45880" | supported |
| E8 | event | transfer="T003454", sender="A-63022", receiver="A-54215", amount_minor=166000, event_time_ms=1794828240000, device="D-45880" | supported |
| E9 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| E10 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| E11 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| E12 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| E13 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| E14 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| E15 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| E16 | event | transfer="T022592", sender="A-56768", receiver="A-83094", amount_minor=169500, event_time_ms=1795059180000, device="D-96125" | supported |
| E17 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| E18 | event | transfer="T022629", sender="A-43725", receiver="A-14799", amount_minor=164000, event_time_ms=1795059600000, device="D-13859" | supported |
| E19 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| E20 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| E21 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| E22 | event | transfer="T034128", sender="A-36729", receiver="A-34558", amount_minor=28000, event_time_ms=1795200600000, device="D-30793" | supported |
| E23 | event | transfer="T018248", sender="A-31752", receiver="A-28137", amount_minor=5500, event_time_ms=1795006260000, device="D-83530" | supported |
| E24 | event | transfer="T005978", sender="A-35236", receiver="A-85921", amount_minor=2500, event_time_ms=1794858600000, device="D-25672" | supported |
| E25 | event | transfer="T005934", sender="A-30679", receiver="A-85921", amount_minor=2500, event_time_ms=1794858060000, device="D-11053" | supported |
| E26 | event | transfer="T033316", sender="A-37471", receiver="A-20636", amount_minor=6000, event_time_ms=1795190580000, device="D-49226" | supported |
| I1 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| I2 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| I3 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| I4 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| I5 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| I6 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| P1 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P2 | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P3 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
| P4 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| P5 | onward_path | transfers=["T011431", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P6 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P7 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| P8 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| R1 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| R2 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| R3 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-85287", "A-92332"], route_accounts=["A-10859", "A-78340", "A-75793", "A-85287", "A-92332"] | supported |
| R4 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| R5 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| R6 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| S1 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| S2 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| S3 | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| S4 | shared_device | device="D-40018", accounts=["A-83094", "A-14799", "A-34114"] | supported |
| N1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| N2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| N3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| N4 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| N5 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| N6 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| N7 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| N8 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| N9 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| N10 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| N11 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| N12 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| N13 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| N14 | absence | kind="no_onward_link_from_transfer", subject="T003222" | supported |
| N15 | absence | kind="no_onward_link_from_transfer", subject="T003454" | supported |
| N16 | absence | kind="no_onward_link_from_transfer", subject="T005888" | supported |
| N17 | absence | kind="no_onward_link_from_transfer", subject="T011628" | supported |
| N18 | absence | kind="no_onward_link_from_transfer", subject="T011695" | supported |
| N19 | absence | kind="no_onward_link_from_transfer", subject="T022649" | supported |
| N20 | absence | kind="no_onward_link_from_transfer", subject="T033506" | supported |
| N21 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| N22 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| N23 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| N24 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| N25 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| N26 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 81 of 81 claims supported; reference validity 1.0 (112 of 112 distinct ids resolve); 11 queries (0 failed), 8 model requests, 109300 input tokens (cache included) and 13851 output tokens, 165.1 s.
