# Case note: fan-in alerts in a bounded replay (large case)

Agent output, live run of 2026-11-13T19:15:22+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: one bounded replay (run:5ce89f521e5e, 50,000 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 3,600,000 ms event-time window; onward links require a gap of at most 1,800,000 ms). The graph holds 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F1** Alert fan_in:A-10859:1794924000000: A-10859 received 6 transfers from 6 distinct senders between 1794924000000 and 1794927600000, totalling 204,000 minor units (T011431, T011465, T011494, T011536, T011572, T011610).  
  Claims: I1 (supported)
- **F2** Alert fan_in:A-20636:1795190400000: A-20636 received 6 transfers from 6 distinct senders between 1795190400000 and 1795194000000, totalling 36,000 (T033316, T033368, T033403, T033439, T033474, T033495).  
  Claims: I2 (supported)
- **F3** Alert fan_in:A-28137:1795003200000: A-28137 received 7 transfers from 7 distinct senders between 1795003200000 and 1795006800000, totalling 29,500 (T018004, T018035, T018065, T018090, T018160, T018198, T018248).  
  Claims: I3 (supported)
- **F4** Alert fan_in:A-37573:1794823200000: A-37573 received 7 transfers from 7 distinct senders between 1794823200000 and 1794826800000, totalling 379,500 (T003057, T003091, T003124, T003154, T003248, T003287, T003319).  
  Claims: I4 (supported)
- **F5** Alert fan_in:A-83577:1795057200000: A-83577 received 8 transfers from 8 distinct senders between 1795057200000 and 1795060800000, totalling 174,500 (T022417, T022437, T022451, T022478, T022495, T022519, T022542, T022561).  
  Claims: I5 (supported)
- **F6** Alert fan_in:A-85921:1794855600000: A-85921 received 6 transfers from 6 distinct senders between 1794855600000 and 1794859200000, totalling 15,000 (T005750, T005789, T005830, T005868, T005934, T005978).  
  Claims: I6 (supported)
- **F7** A-10859 onward routes: at most 3 onward links. All six contributing transfers are linked onward to A-10859's debits T011583 (150,000) and/or T011670 (95,000), both paid to A-78340. A-78340 then sent T011600 (120,000) to A-75793, which sent T011628 (117,500) to A-92332, and T011695 (118,000) to A-85287. The money comes to rest at two accounts, A-92332 and A-85287. Route accounts: A-10859, A-78340, A-75793, A-92332, A-85287.  
  Claims: R1 (supported), P1 (supported), P2 (supported), P3 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported)
- **F8** A-20636 onward route: at most 1 onward link. Five of the six contributing transfers are linked to T033506 (30,000), which A-20636 paid to A-36729, and it was not passed on. T033316 (the earliest contribution, at 1795190580000) has no onward link. The money comes to rest at A-36729.  
  Claims: R2 (supported), P4 (supported), E6 (supported), E23 (supported), N4 (supported)
- **F9** A-28137 onward route: no onward links at all. None of its seven contributing transfers was passed on, so it has no chain and no resting account beyond A-28137. A-28137's only recorded outgoing transfer, T018852 (21,000 to A-87539 at 1795013700000), is not an onward link from any contribution and was not itself passed on.  
  Claims: R3 (supported), N5 (supported), N6 (supported), N7 (supported), N8 (supported), N9 (supported), N10 (supported), N11 (supported), E21 (supported), E24 (supported), N20 (supported)
- **F10** A-37573 onward routes: at most 4 onward links, along two parallel sequences through the same accounts. T003057, T003091, T003124 and T003154 link to T003168, which runs A-37573 -> A-38045 -> A-93288 -> A-63022 -> A-54215 (T003168, T003182, T003201, T003222). T003248, T003287 and T003319 link to T003391, which follows the same account sequence (T003391, T003416, T003433, T003454). Both end at A-54215 (184,000 + 166,000). Every contributing transfer is passed on.  
  Claims: R4 (supported), P5 (supported), P6 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), E14 (supported)
- **F11** A-83577 onward route: at most 5 onward links, the longest of the six alerts. All eight contributing transfers link to T022572 (172,000), and the money then runs A-83577 -> A-56768 -> A-83094 -> A-43725 -> A-14799 -> A-39382 (T022572, T022592, T022609, T022629, T022649). It comes to rest at A-39382 (161,500).  
  Claims: R5 (supported), P7 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported), E19 (supported)
- **F12** A-85921 onward route: at most 1 onward link. T005750, T005789, T005830 and T005868 link to T005888 (9,500), which A-85921 paid to A-10758, and it was not passed on. T005934 and T005978 have no onward link. The money comes to rest at A-10758.  
  Claims: R6 (supported), P8 (supported), E20 (supported), N12 (supported), N13 (supported)
- **F13** Shared devices on routes (question 3): on A-10859's route, device D-79802 sent transfers from A-10859 and A-78340. On A-37573's route, device D-45880 sent transfers from A-37573, A-38045, A-93288 and A-63022, and it sent all eight onward transfers. On A-83577's route, device D-40018 sent transfers from A-83094 (T022609) and A-14799 (T022649). The same device also sent T038409 from A-34114, an account that is not on the route. The routes of A-20636, A-28137 and A-85921 have no device used by two or more route accounts.  
  Claims: S1 (supported), S2 (supported), S3 (supported), S4 (supported), E17 (supported), E19 (supported), E22 (supported), N1 (supported), N2 (supported), N3 (supported)
- **F14** What distinguishes the alerts (question 4): as indicators they look alike (6 to 8 distinct senders, one transfer per sender, one hour). The recorded relationships separate them into three groups. (a) A-28137 has no onward links. (b) A-20636 and A-85921 each have a single 1-link hop to one resting account, some contributions not passed on, and no shared device on the route. (c) A-10859, A-37573 and A-83577 have multi-hop chains (3, 4 and 5 links) that pass on every contribution, and each route has a device shared by route accounts. Within (c), A-37573 is the strongest: one device (D-40018) covers the alerted account and all three intermediaries. A-10859 shares a device between the alerted account and its first hop, and it splits to two resting accounts. In A-83577, two non-adjacent intermediaries share a device. None of the resting accounts (A-92332, A-85287, A-36729, A-54215, A-39382, A-10758) has a fan-in alert of its own.  
  Claims: R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), N1 (supported), N2 (supported), N3 (supported), N14 (supported), N15 (supported), N16 (supported), N17 (supported), N18 (supported), N19 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** On the A-37573 route, one device sent from four accounts and the money passed through the same four-hop sequence twice. This pattern fits a single party controlling the alerted account and its intermediaries, i.e. layering towards A-54215. Device sharing does not establish ownership or identity.  
  References: S2, P5, P6, R4
- **H2** The A-10859 and A-83577 routes, with multi-hop pass-through and partial device sharing, may be rapid pass-through (mule-style) activity. This is an interpretation only.  
  References: S1, S3, R1, R5
- **H3** A-28137 received many small payments and passed none of them on within the onward window. That fits ordinary collection activity (for example a merchant or a shared expense), so its alert may be of lower priority. A-20636 and A-85921, which have one hop and no device overlap, are intermediate cases.  
  References: R3, I3, R2, R6, N1, N3

## Unresolved questions

- **U1** What happens to the money after the resting accounts (A-92332, A-85287, A-36729, A-54215, A-39382, A-10758)? Within this dataset none of their resting transfers was passed on. Any later movement outside the bounded dataset cannot be observed.  
  References: R1, R2, R4, R5, R6
- **U2** Do the shared devices (D-79802, D-45880, D-40018) reflect common control, a shared or public device, or device-ID collisions? Is A-34114, which also used D-40018, related to the A-83577 route? The data records only device usage.  
  References: S1, S2, S3, S4, E22
- **U3** A-10859's two onward debits (245,000 in total) exceed its alerted inflow (204,000). Does that reflect other credits or an earlier balance? The source of the difference was not established here.  
  References: I1, E1, E4
- **U4** What is the relationship between the contributing senders and the alerted accounts? Is the fan-in coordinated or coincidental? Nothing recorded answers this.  
  References: I1, I2, I3, I4, I5, I6

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E1 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| E2 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| E3 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| E4 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| E5 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| E6 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| E7 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| E8 | event | transfer="T003182", sender="A-38045", receiver="A-93288", amount_minor=191000, event_time_ms=1794824940000, device="D-45880" | supported |
| E9 | event | transfer="T003201", sender="A-93288", receiver="A-63022", amount_minor=187500, event_time_ms=1794825180000, device="D-45880" | supported |
| E10 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| E11 | event | transfer="T003391", sender="A-37573", receiver="A-38045", amount_minor=176000, event_time_ms=1794827520000, device="D-45880" | supported |
| E12 | event | transfer="T003416", sender="A-38045", receiver="A-93288", amount_minor=172500, event_time_ms=1794827700000, device="D-45880" | supported |
| E13 | event | transfer="T003433", sender="A-93288", receiver="A-63022", amount_minor=169000, event_time_ms=1794827940000, device="D-45880" | supported |
| E14 | event | transfer="T003454", sender="A-63022", receiver="A-54215", amount_minor=166000, event_time_ms=1794828240000, device="D-45880" | supported |
| E15 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| E16 | event | transfer="T022592", sender="A-56768", receiver="A-83094", amount_minor=169500, event_time_ms=1795059180000, device="D-96125" | supported |
| E17 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| E18 | event | transfer="T022629", sender="A-43725", receiver="A-14799", amount_minor=164000, event_time_ms=1795059600000, device="D-13859" | supported |
| E19 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| E20 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| E21 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| E22 | event | transfer="T038409", sender="A-34114", receiver="A-39862", amount_minor=12000, event_time_ms=1795252440000, device="D-40018" | supported |
| E23 | event | transfer="T033316", sender="A-37471", receiver="A-20636", amount_minor=6000, event_time_ms=1795190580000, device="D-49226" | supported |
| E24 | event | transfer="T018248", sender="A-31752", receiver="A-28137", amount_minor=5500, event_time_ms=1795006260000, device="D-83530" | supported |
| I1 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011610", "T011572", "T011536", "T011494", "T011465", "T011431"] | supported |
| I2 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033495", "T033474", "T033439", "T033403", "T033368", "T033316"] | supported |
| I3 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018248", "T018198", "T018160", "T018090", "T018065", "T018035", "T018004"] | supported |
| I4 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003319", "T003287", "T003248", "T003154", "T003124", "T003091", "T003057"] | supported |
| I5 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022561", "T022542", "T022519", "T022495", "T022478", "T022451", "T022437", "T022417"] | supported |
| I6 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005978", "T005934", "T005868", "T005830", "T005789", "T005750"] | supported |
| P1 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", comes_to_rest_at="A-92332" | supported |
| P2 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", comes_to_rest_at="A-85287" | supported |
| P3 | onward_path | transfers=["T011431", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", comes_to_rest_at="A-85287" | supported |
| P4 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", comes_to_rest_at="A-36729" | supported |
| P5 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", comes_to_rest_at="A-54215" | supported |
| P6 | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", comes_to_rest_at="A-54215" | supported |
| P7 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", comes_to_rest_at="A-39382" | supported |
| P8 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", comes_to_rest_at="A-10758" | supported |
| R1 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-92332", "A-85287"] | supported |
| R2 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| R3 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| R4 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| R5 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| R6 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| S1 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| S2 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| S3 | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| S4 | shared_device | device="D-40018", accounts=["A-83094", "A-14799", "A-34114"] | supported |
| N1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| N2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| N3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| N4 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| N5 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| N6 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| N7 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| N8 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| N9 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| N10 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| N11 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| N12 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| N13 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| N14 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| N15 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| N16 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| N17 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| N18 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| N19 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| N20 | absence | kind="no_onward_link_from_transfer", subject="T018852" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 73 of 73 claims supported; reference validity 1.0 (107 of 107 distinct ids resolve); 11 queries (0 failed), 8 model requests, 106972 input tokens (cache included) and 13835 output tokens, 168.5 s.
