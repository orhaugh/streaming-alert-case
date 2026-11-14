# Case note: fan-in alerts in a bounded replay (large case)

Agent output, recorded run of 2026-11-14T07:50:34+00:00: graph arm through Relate's MCP server (relate-mcp 1.0.1, stdio), model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Run run:5ce89f521e5e is a bounded replay of 50,000 events (dataset sha256 5ce89f52…). All 3 of 3 jobs completed, clink exited with status 0, and the run was not cancelled. Parameters: fan-in needs at least 5 distinct senders within a 3,600,000 ms event-time window, and the onward-link gap limit is 1,800,000 ms. The graph holds 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** There are six fan-in alerts. Each one's contributing transfers come from distinct senders, one transfer per sender. (a) A-37573: window 1794823200000–1794826800000, 7 senders, 7 transfers, total 379,500. (b) A-85921: window 1794855600000–1794859200000, 6 senders, 6 transfers, total 15,000; every contributing transfer is 2,500. (c) A-10859: window 1794924000000–1794927600000, 6 senders, 6 transfers, total 204,000. (d) A-28137: window 1795003200000–1795006800000, 7 senders, 7 transfers, total 29,500. (e) A-83577: window 1795057200000–1795060800000, 8 senders, 8 transfers, total 174,500. (f) A-20636: window 1795190400000–1795194000000, 6 senders, 6 transfers, total 36,000. No sender contributes to more than one alert. No device was used by two or more of the contributing senders within any one alert.  
  Claims: I1 (supported), I2 (supported), I3 (supported), I4 (supported), I5 (supported), I6 (supported), E21 (supported), E22 (supported), E23 (supported)
- **F3** A-37573 (fan_in:A-37573:1794823200000): every contributing transfer starts a candidate onward path. The longest path has 4 onward links. There are two parallel branches. T003057, T003091, T003124 and T003154 link to T003168, then T003182, T003201, T003222. T003248, T003287 and T003319 link to T003391, then T003416, T003433, T003454. Both branches pass through the same accounts in the same order: A-37573 → A-38045 → A-93288 → A-63022 → A-54215. Both end at A-54215, where no further qualifying transfer exists in this dataset. Route accounts: A-37573, A-38045, A-93288, A-63022, A-54215.  
  Claims: I1 (supported), P1 (supported), P2 (supported), R1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported), E7 (supported), E8 (supported), N6 (supported)
- **F4** A-37573 route: device D-45880 sent all eight onward transfers on both branches (T003168, T003182, T003201, T003222, T003391, T003416, T003433, T003454). It was used by four route accounts: A-37573, A-38045, A-93288 and A-63022. The terminal account A-54215 is not recorded as sending from it.  
  Claims: S1 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported), E6 (supported), E7 (supported), E8 (supported)
- **F5** A-83577 (fan_in:A-83577:1795057200000): all 8 contributing transfers have an onward link to the same transfer, T022572 (A-83577 → A-56768, 172,000). From there one path of 5 onward links follows: T022572 → T022592 → T022609 → T022629 → T022649. Its accounts are A-83577 → A-56768 → A-83094 → A-43725 → A-14799 → A-39382, and it ends at A-39382 with no further qualifying transfer in this dataset. The five onward transfers fall between 1795059000000 and 1795059900000, and the gaps after the first link are 180,000–300,000 ms.  
  Claims: I5 (supported), P3 (supported), R2 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), N7 (supported)
- **F6** A-83577 route: device D-40018 was used by route accounts A-83094 (T022609) and A-14799 (T022649), which are not adjacent on the path. D-40018 was also used by A-34114, which is not on this route (T038409). The other onward transfers came from different devices.  
  Claims: S2 (supported), E11 (supported), E13 (supported), E24 (supported), E9 (supported), E10 (supported), E12 (supported)
- **F7** A-10859 (fan_in:A-10859:1794924000000): every contributing transfer has an onward link, and the paths branch. T011431, T011465, T011494, T011536 and T011572 link to T011583 (A-10859 → A-78340). From T011583, one path goes T011600 (→ A-75793), then T011628 (→ A-92332): 3 links, the longest, ending at A-92332. T011583 also links to T011695 (A-78340 → A-85287). T011536, T011572 and T011610 also link to T011670 (A-10859 → A-78340), which links to T011695. Paths end at two accounts, A-92332 and A-85287, with no further qualifying transfer in this dataset. Route accounts: A-10859, A-78340, A-75793, A-92332, A-85287.  
  Claims: I3 (supported), P4 (supported), P5 (supported), P6 (supported), R3 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported), N8 (supported), N9 (supported)
- **F8** A-10859 route: device D-79802 was used by A-10859 (T011583, T011670) and A-78340 (T011600, T011695). The last link, T011628 from A-75793, came from a different device, D-10265.  
  Claims: S3 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported)
- **F9** A-20636 (fan_in:A-20636:1795190400000): five of its six contributing transfers link to one transfer, T033506 (A-20636 → A-36729, 30,000, device D-52544). That gives one path of 1 link, ending at A-36729. T033316 has no onward link. A-36729's only recorded send, T034128, falls 7,800,000 ms after T033506, which is beyond the gap limit, so it is not linked. Route accounts A-20636 and A-36729 share no device.  
  Claims: I6 (supported), P7 (supported), R4 (supported), E19 (supported), E25 (supported), N1 (supported), N10 (supported), A1 (supported)
- **F10** A-85921 (fan_in:A-85921:1794855600000): four contributing transfers (T005750, T005789, T005830, T005868) link to T005888 (A-85921 → A-10758, 9,500, device D-97117). That gives one path of 1 link, ending at A-10758. T005934 and T005978 come after T005888 and have no onward link. Route accounts A-85921 and A-10758 share no device.  
  Claims: I2 (supported), P8 (supported), R5 (supported), E20 (supported), N2 (supported), N3 (supported), N11 (supported), A2 (supported)
- **F11** A-28137 (fan_in:A-28137:1795003200000): none of its seven contributing transfers has an onward link, so the alert starts no candidate onward path. Its route is the alerted account alone, so there is no shared device on the route. A-28137's only recorded send, T018852 (21,000 to A-87539), comes after the window, with no onward link.  
  Claims: I4 (supported), R6 (supported), N4 (supported), N5 (supported), A3 (supported), E21 (supported), E26 (supported)
- **F12** None of the path-end accounts (A-54215, A-39382, A-92332, A-85287, A-36729, A-10758) has a fan-in alert of its own.  
  Claims: X1 (supported), X2 (supported), X3 (supported), X4 (supported), X5 (supported), X6 (supported)
- **F13** What distinguishes the alerts. As fan-in indicators they look alike: 6–8 distinct senders in one event-time hour, one transfer per sender, no sender overlap and no shared sender devices. The recorded relationships beyond the indicator split them into three groups. (1) A-37573, A-83577 and A-10859 each have multi-link candidate onward paths (4, 5 and 3 links), whose first onward transfer comes soon after the credits. Each also has a device used by two or more accounts on its own route: D-45880 by four accounts, D-40018 by two non-adjacent accounts, D-79802 by two. (2) A-20636 and A-85921 each have a single 1-link path to one account, some contributing transfers with no link, and no shared device on the route. (3) A-28137 has no onward links and no route device sharing. This makes group (1) the clearest candidates for review; groups (2) and (3) show only the fan-in and timing. These relationships record timing and device use only. They do not show that the same funds moved, or establish fraud or common control.  
  Claims: R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), A1 (supported), A2 (supported), A3 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** For A-37573, a single device sending every onward transfer across four accounts, in two identical account sequences, could mean one party operates those accounts (a possible mule chain). This is an interpretation; a shared device can also come from a shared or managed terminal.  
  References: S1, P1, P2
- **H2** For A-83577, the onward transfer of 172,000 against a fan-in total of 174,500, followed by quick successive debits of slightly smaller amounts, could mean collected credits were forwarded along the route. The data records only timing and amounts, not that the same funds moved.  
  References: I5, E9, E10, E11, E12, E13, P3
- **H3** For A-10859, the branching to two end accounts with devices shared between A-10859 and A-78340 could reflect splitting under common control. Unverified.  
  References: R3, S3
- **H4** A-85921 (six equal 2,500 credits) and A-28137 (small credits with no onward link) may be benign collection patterns, such as group payments or merchant-like receipts, that met the fan-in threshold. Not established.  
  References: I2, I4, R6

## Unresolved questions

- **U1** Who owns or controls the accounts that share devices D-45880, D-40018 and D-79802, and why is D-40018 also used by A-34114, which is outside the route?  
  References: S1, S2, S3, E24
- **U2** What happened at or after the path-end accounts (A-54215, A-39382, A-92332, A-85287, A-36729, A-10758)? These paths end only because this bounded dataset has no further qualifying transfer.  
  References: R1, R2, R3, R4, R5
- **U3** Do the onward links reflect the same funds being moved, or only coincidental timing? Onward links record timing alone.  
  References: P1, P3, P4, P7, P8
- **U4** Are the contributing senders connected to each other or to the route accounts in ways not recorded here, such as off-dataset identities?  
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
| E9 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| E10 | event | transfer="T022592", sender="A-56768", receiver="A-83094", amount_minor=169500, event_time_ms=1795059180000, device="D-96125" | supported |
| E11 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| E12 | event | transfer="T022629", sender="A-43725", receiver="A-14799", amount_minor=164000, event_time_ms=1795059600000, device="D-13859" | supported |
| E13 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| E14 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| E15 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| E16 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| E17 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| E18 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| E19 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| E20 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| E21 | event | transfer="T018004", sender="A-42687", receiver="A-28137", amount_minor=4000, event_time_ms=1795003380000, device="D-94992" | supported |
| E22 | event | transfer="T005750", sender="A-10868", receiver="A-85921", amount_minor=2500, event_time_ms=1794855900000, device="D-61312" | supported |
| E23 | event | transfer="T022417", sender="A-85076", receiver="A-83577", amount_minor=19000, event_time_ms=1795057260000, device="D-78356" | supported |
| E24 | event | transfer="T038409", sender="A-34114", receiver="A-39862", amount_minor=12000, event_time_ms=1795252440000, device="D-40018" | supported |
| E25 | event | transfer="T034128", sender="A-36729", receiver="A-34558", amount_minor=28000, event_time_ms=1795200600000, device="D-30793" | supported |
| E26 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| I1 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| I2 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| I3 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| I4 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| I5 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| I6 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| P1 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P2 | onward_path | transfers=["T003319", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P3 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| P4 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| P5 | onward_path | transfers=["T011431", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P6 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P7 | onward_path | transfers=["T033495", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| P8 | onward_path | transfers=["T005868", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
| R1 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| R2 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| R3 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-92332", "A-85287"] | supported |
| R4 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| R5 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| R6 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| S1 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| S2 | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| S3 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| A1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| A2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| A3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| N1 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| N2 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| N3 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| N4 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| N5 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| N6 | absence | kind="no_onward_link_from_transfer", subject="T003454" | supported |
| N7 | absence | kind="no_onward_link_from_transfer", subject="T022649" | supported |
| N8 | absence | kind="no_onward_link_from_transfer", subject="T011628" | supported |
| N9 | absence | kind="no_onward_link_from_transfer", subject="T011695" | supported |
| N10 | absence | kind="no_onward_link_from_transfer", subject="T033506" | supported |
| N11 | absence | kind="no_onward_link_from_transfer", subject="T005888" | supported |
| X1 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| X2 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| X3 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| X4 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| X5 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| X6 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 74 of 74 claims supported; reference validity 1.0 (112 of 112 distinct ids resolve); 16 queries (1 failed), 8 model requests, 118239 input tokens (cache included) and 15092 output tokens, 1989.7 s.
