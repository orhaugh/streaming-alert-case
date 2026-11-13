# Case note: large case, table arm, run 2

Agent output, recorded run of 2026-11-13T19:33:33+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: one bounded replay (run:5ce89f521e5e, 50,000 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled). Parameters: fan-in needs at least 5 distinct senders within a 3,600,000 ms event-time window, and an onward link needs a debit within 1,800,000 ms of a credit. The dataset contains 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset as processed by this run.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F1** fan_in:A-10859:1794924000000: account A-10859, window 1794924000000–1794927600000, 6 senders, 6 transfers, total 204000. Contributing transfers: T011431, T011465, T011494, T011536, T011572, T011610.  
  Claims: I1 (supported), E11 (supported), E12 (supported)
- **F2** fan_in:A-20636:1795190400000: account A-20636, window 1795190400000–1795194000000, 6 senders, 6 transfers, total 36000. Contributing transfers: T033316, T033368, T033403, T033439, T033474, T033495.  
  Claims: I2 (supported), E21 (supported), E22 (supported)
- **F3** fan_in:A-28137:1795003200000: account A-28137, window 1795003200000–1795006800000, 7 senders, 7 transfers, total 29500. Contributing transfers: T018004, T018035, T018065, T018090, T018160, T018198, T018248.  
  Claims: I3 (supported), E31 (supported)
- **F4** fan_in:A-37573:1794823200000: account A-37573, window 1794823200000–1794826800000, 7 senders, 7 transfers, total 379500. Contributing transfers: T003057, T003091, T003124, T003154, T003248, T003287, T003319.  
  Claims: I4 (supported), E41 (supported), E42 (supported)
- **F5** fan_in:A-83577:1795057200000: account A-83577, window 1795057200000–1795060800000, 8 senders, 8 transfers, total 174500. Contributing transfers: T022417, T022437, T022451, T022478, T022495, T022519, T022542, T022561.  
  Claims: I5 (supported), E51 (supported)
- **F6** fan_in:A-85921:1794855600000: account A-85921, window 1794855600000–1794859200000, 6 senders, 6 transfers, total 15000. Contributing transfers: T005750, T005789, T005830, T005868, T005934, T005978. Each of the six contributing transfers is for 2500.  
  Claims: I6 (supported), E61 (supported), E62 (supported), E63 (supported)
- **F7** A-10859 alert, candidate onward-transfer paths: the longest has 3 onward links. Path accounts are A-10859, A-78340, A-75793, A-85287 and A-92332. The paths branch at A-78340 and end at two accounts, A-92332 (via T011628) and A-85287 (via T011695). Neither has a further qualifying transfer in this dataset, and neither has a fan-in alert. Every contributing transfer starts at least one path, through T011583 and/or T011670 (A-10859 to A-78340).  
  Claims: R1 (supported), P11 (supported), P12 (supported), P13 (supported), E13 (supported), E14 (supported), E15 (supported), E16 (supported), E17 (supported), N11 (supported), N12 (supported), X11 (supported), X12 (supported)
- **F8** A-20636 alert: the longest path has 1 onward link. Path accounts are A-20636 and A-36729. Five contributing transfers link to T033506 (A-20636 to A-36729), and all paths end at A-36729. Contributing transfer T033316 has no onward link, and T033506 has no further one.  
  Claims: R2 (supported), P21 (supported), E23 (supported), N21 (supported), N22 (supported), X21 (supported)
- **F9** A-28137 alert: none of its 7 contributing transfers has an onward link in this dataset. So it has no candidate onward-transfer paths (max depth 0), no end accounts, and A-28137 is its only path account.  
  Claims: R3 (supported), N31 (supported), N32 (supported), N33 (supported), N34 (supported), N35 (supported), N36 (supported), N37 (supported)
- **F10** A-37573 alert: the longest path has 4 onward links. Path accounts are A-37573, A-38045, A-93288, A-63022 and A-54215. There are two parallel candidate sequences over the same accounts: T003168>T003182>T003201>T003222 (linked from T003057, T003091, T003124, T003154) and T003391>T003416>T003433>T003454 (linked from T003248, T003287, T003319). Both end at A-54215, which has no further qualifying transfer in this dataset and no fan-in alert.  
  Claims: R4 (supported), P41 (supported), P42 (supported), E43 (supported), E44 (supported), E45 (supported), E46 (supported), E47 (supported), E48 (supported), E49 (supported), E40 (supported), N41 (supported), N42 (supported), X41 (supported)
- **F11** A-83577 alert: the longest path has 5 onward links, the most of any alert. Path accounts are A-83577, A-56768, A-83094, A-43725, A-14799 and A-39382. All 8 contributing transfers link to the single sequence T022572>T022592>T022609>T022629>T022649, which ends at A-39382. A-39382 has no further qualifying transfer in this dataset and no fan-in alert.  
  Claims: R5 (supported), P51 (supported), E52 (supported), E53 (supported), E54 (supported), E55 (supported), E56 (supported), N51 (supported), X51 (supported)
- **F12** A-85921 alert: the longest path has 1 onward link. Path accounts are A-85921 and A-10758. Four contributing transfers link to T005888 (A-85921 to A-10758, 9500), and the paths end at A-10758. Contributing transfers T005934 and T005978 have no onward link.  
  Claims: R6 (supported), P61 (supported), E64 (supported), N61 (supported), N62 (supported), N63 (supported), X61 (supported)
- **F13** Shared devices on paths. A-10859: device D-79802 was used to send by A-10859 and A-78340, which are the alerted account and its first onward account. A-37573: device D-45880 was used to send by A-37573, A-38045, A-93288 and A-63022, which are every path account that sent anything; all 8 onward transfers on its paths came from D-45880. A-83577: device D-40018 was used to send by A-83094 and A-14799, which are not adjacent on the path; account A-34114, which is not on the path, also sent from D-40018. The A-20636, A-28137 and A-85921 alerts have no device used by two or more of their path accounts. A-36729 (on the A-20636 path) shares device D-30793 with A-69026, which is not on that path.  
  Claims: S1 (supported), S2 (supported), S3 (supported), S4 (supported), S5 (supported), B1 (supported), B2 (supported), B3 (supported), E13 (supported), E14 (supported), E15 (supported), E43 (supported), E44 (supported), E45 (supported), E46 (supported), E54 (supported), E56 (supported)
- **F14** What tells the alerts apart. As indicators they are alike: 6–8 distinct senders within one hour. The recorded relationships beyond the indicator differ. (a) Onward links: A-28137 has none. A-20636 and A-85921 have single-step paths to one account each, and some of their contributions have no onward link. A-10859 (3 links, branching to 2 end accounts), A-37573 (4 links) and A-83577 (5 links) have multi-step paths that every contribution feeds into. (b) Shared devices: only A-10859, A-37573 and A-83577 have a device shared by accounts on their paths. In the A-37573 case the alerted account and every intermediate account sent from one device, D-45880. (c) Amounts: in the recorded transfers, each onward transfer on the multi-step paths is slightly smaller than the one before it (for example 196000, 191000, 187500, 184000 on A-37573's first sequence, and 172000 down to 161500 on A-83577's). For interpretation: A-28137, and to a lesser degree A-20636 and A-85921, show nothing beyond the fan-in itself. A-37573, A-83577 and A-10859 combine fan-in with multi-step timing links and shared devices, which makes them the stronger candidates for review. These remain recorded relationships, not proof of fraud or common control.  
  Claims: R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), B1 (supported), B2 (supported), B3 (supported), E43 (supported), E44 (supported), E45 (supported), E46 (supported), E52 (supported), E56 (supported)
- **F15** Traceable provenance: each finding traces back to the transfer ids listed in its claims. Those ids come from the alert_contributions and onward_links tables of run run:5ce89f521e5e.  
  Claims: C1 (supported), I1 (supported), I2 (supported), I3 (supported), I4 (supported), I5 (supported), I6 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-37573's path accounts (A-37573, A-38045, A-93288, A-63022) may be operated by a single party: they all sent from D-45880, in quick succession, with slightly decreasing amounts. This would fit a layering pattern, but the data shows only device use and timing, not who controls the accounts or whether the same funds moved.  
  References: S2, R4, P41, P42
- **H2** A-83577's sequence may be a relay pattern. D-40018 is shared by non-adjacent accounts A-83094 and A-14799, and also by off-path A-34114, which raises the possibility of a wider linked set. This is not established.  
  References: S3, R5, P51
- **H3** A-10859 and A-78340 may be controlled together, since both sent from D-79802. Not established.  
  References: S1, R1
- **H4** A-28137's fan-in (small amounts, no onward links) and A-85921's (six identical 2500 transfers) could be ordinary collection activity, such as shared bills or a small merchant. The data cannot tell this apart from other explanations.  
  References: R3, I3, I6

## Unresolved questions

- **U1** What happened at the end accounts (A-92332, A-85287, A-36729, A-54215, A-39382, A-10758) after this dataset? The paths end only because there is no further qualifying transfer in this bounded replay.  
  References: R1, R2, R4, R5, R6
- **U2** Who controls or uses devices D-45880, D-79802 and D-40018? And what, if anything, connects A-34114 (D-40018) and A-69026 (D-30793) to the alerted paths?  
  References: S1, S2, S3, S5
- **U3** Did the same funds actually move along these paths? Onward links record timing within 30 minutes, not where funds came from.  
  References: P11, P41, P51
- **U4** Are the contributing senders connected to each other in any way not recorded here, such as identity data or out-of-window activity?  
  References: I1, I4, I5

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E11 | event | transfer="T011431", sender="A-57720", receiver="A-10859", amount_minor=28000, event_time_ms=1794924300000, device="D-47930" | supported |
| E12 | event | transfer="T011610", sender="A-67293", receiver="A-10859", amount_minor=39000, event_time_ms=1794926220000, device="D-35545" | supported |
| E13 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| E14 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| E15 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| E16 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| E17 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| E21 | event | transfer="T033316", sender="A-37471", receiver="A-20636", amount_minor=6000, event_time_ms=1795190580000, device="D-49226" | supported |
| E22 | event | transfer="T033368", sender="A-75147", receiver="A-20636", amount_minor=5500, event_time_ms=1795191120000, device="D-67770" | supported |
| E23 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| E31 | event | transfer="T018004", sender="A-42687", receiver="A-28137", amount_minor=4000, event_time_ms=1795003380000, device="D-94992" | supported |
| E41 | event | transfer="T003057", sender="A-76091", receiver="A-37573", amount_minor=61000, event_time_ms=1794823320000, device="D-16311" | supported |
| E42 | event | transfer="T003248", sender="A-11724", receiver="A-37573", amount_minor=66000, event_time_ms=1794825840000, device="D-17121" | supported |
| E43 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| E44 | event | transfer="T003182", sender="A-38045", receiver="A-93288", amount_minor=191000, event_time_ms=1794824940000, device="D-45880" | supported |
| E45 | event | transfer="T003201", sender="A-93288", receiver="A-63022", amount_minor=187500, event_time_ms=1794825180000, device="D-45880" | supported |
| E46 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| E47 | event | transfer="T003391", sender="A-37573", receiver="A-38045", amount_minor=176000, event_time_ms=1794827520000, device="D-45880" | supported |
| E48 | event | transfer="T003416", sender="A-38045", receiver="A-93288", amount_minor=172500, event_time_ms=1794827700000, device="D-45880" | supported |
| E49 | event | transfer="T003433", sender="A-93288", receiver="A-63022", amount_minor=169000, event_time_ms=1794827940000, device="D-45880" | supported |
| E40 | event | transfer="T003454", sender="A-63022", receiver="A-54215", amount_minor=166000, event_time_ms=1794828240000, device="D-45880" | supported |
| E51 | event | transfer="T022417", sender="A-85076", receiver="A-83577", amount_minor=19000, event_time_ms=1795057260000, device="D-78356" | supported |
| E52 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| E53 | event | transfer="T022592", sender="A-56768", receiver="A-83094", amount_minor=169500, event_time_ms=1795059180000, device="D-96125" | supported |
| E54 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| E55 | event | transfer="T022629", sender="A-43725", receiver="A-14799", amount_minor=164000, event_time_ms=1795059600000, device="D-13859" | supported |
| E56 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| E61 | event | transfer="T005750", sender="A-10868", receiver="A-85921", amount_minor=2500, event_time_ms=1794855900000, device="D-61312" | supported |
| E62 | event | transfer="T005934", sender="A-30679", receiver="A-85921", amount_minor=2500, event_time_ms=1794858060000, device="D-11053" | supported |
| E63 | event | transfer="T005978", sender="A-35236", receiver="A-85921", amount_minor=2500, event_time_ms=1794858600000, device="D-25672" | supported |
| E64 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| I1 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| I2 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| I3 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| I4 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| I5 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| I6 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| P11 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| P12 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P13 | onward_path | transfers=["T011431", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P21 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| P41 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P42 | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P51 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| P61 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
| R1 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-85287", "A-92332"] | supported |
| R2 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| R3 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| R4 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| R5 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| R6 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| S1 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| S2 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| S3 | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| S4 | shared_device | device="D-40018", accounts=["A-83094", "A-14799", "A-34114"] | supported |
| S5 | shared_device | device="D-30793", accounts=["A-36729", "A-69026"] | supported |
| B1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| B2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| B3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| N11 | absence | kind="no_onward_link_from_transfer", subject="T011628" | supported |
| N12 | absence | kind="no_onward_link_from_transfer", subject="T011695" | supported |
| N21 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| N22 | absence | kind="no_onward_link_from_transfer", subject="T033506" | supported |
| N31 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| N32 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| N33 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| N34 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| N35 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| N36 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| N37 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| N41 | absence | kind="no_onward_link_from_transfer", subject="T003222" | supported |
| N42 | absence | kind="no_onward_link_from_transfer", subject="T003454" | supported |
| N51 | absence | kind="no_onward_link_from_transfer", subject="T022649" | supported |
| N61 | absence | kind="no_onward_link_from_transfer", subject="T005888" | supported |
| N62 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| N63 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| X11 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| X12 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| X21 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| X41 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| X51 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| X61 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 87 of 87 claims supported; reference validity 1.0 (122 of 122 distinct ids resolve); 7 queries (0 failed), 5 model requests, 75336 input tokens (cache included) and 12535 output tokens, 144.7 s.
