# Case note: large case, graph arm, run 2

Agent output, recorded run of 2026-11-13T19:35:59+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F0** Scope: one bounded replay (run:5ce89f521e5e), with 50,000 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled. Parameters: at least 5 distinct senders per event-time hour, onward gap at most 1,800,000 ms. The graph holds 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F1** Alert A-10859 (window 1794924000000–1794927600000): 6 senders, 6 transfers, total 204,000. Every contributing transfer starts a candidate onward-transfer path. The paths branch through A-78340 (T011583, T011670). Up to 3 onward links lead to two end accounts: A-92332 (via T011600 to A-75793, then T011628) and A-85287 (via T011695). Path accounts: A-10859, A-78340, A-75793, A-92332, A-85287.  
  Claims: I1 (supported), R1 (supported), P1 (supported), P2 (supported), P3 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), E5 (supported)
- **F2** Alert A-37573 (window 1794823200000–1794826800000): 7 senders, 7 transfers, total 379,500, the largest of the six. All 7 contributing transfers start paths, and every path has exactly 4 onward links. The paths follow the same account sequence twice at different times: A-37573 → A-38045 → A-93288 → A-63022 → A-54215, first via T003168/T003182/T003201/T003222, then via T003391/T003416/T003433/T003454. All paths end at A-54215.  
  Claims: I4 (supported), R4 (supported), P5 (supported), P6 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), E14 (supported)
- **F3** Alert A-83577 (window 1795057200000–1795060800000): 8 senders, 8 transfers, total 174,500. All 8 contributing transfers lead into one linear sequence of 5 onward links (T022572, T022592, T022609, T022629, T022649) through A-56768, A-83094, A-43725 and A-14799. It ends at A-39382. This is the deepest reach of the six alerts.  
  Claims: I5 (supported), R5 (supported), P7 (supported), E15 (supported), E16 (supported), E17 (supported), E18 (supported), E19 (supported)
- **F4** Alert A-20636 (window 1795190400000–1795194000000): 6 senders, 6 transfers, total 36,000. Five contributing transfers lead by one onward link (T033506, 30,000) to A-36729, where the paths end. T033316 has no onward link.  
  Claims: I2 (supported), R2 (supported), P4 (supported), E6 (supported), X11 (supported)
- **F5** Alert A-85921 (window 1794855600000–1794859200000): 6 senders, 6 transfers, total 15,000. Every contributing transfer is exactly 2,500, for example T005750 and T005978. Four contributing transfers lead by one onward link (T005888, 9,500) to A-10758, where the paths end. T005934 and T005978 have no onward link.  
  Claims: I6 (supported), R6 (supported), P8 (supported), E20 (supported), E24 (supported), E25 (supported), X12 (supported), X13 (supported)
- **F6** Alert A-28137 (window 1795003200000–1795006800000): 7 senders, 7 transfers, total 29,500. None of its 7 contributing transfers has an onward link, so it has no candidate onward-transfer paths. A-28137's only recorded outgoing transfer is T018852 (21,000 to A-87539 at 1795013700000). That is 7,440,000 ms after its last contributing credit (T018248), outside the 30-minute onward window, and T018852 has no onward link itself.  
  Claims: I3 (supported), R3 (supported), X4 (supported), X5 (supported), X6 (supported), X7 (supported), X8 (supported), X9 (supported), X10 (supported), E21 (supported), E23 (supported), X14 (supported)
- **F7** Shared devices on routes: (a) A-37573: device D-45880 sent all 8 of its onward transfers, from four path accounts (A-37573, A-38045, A-93288, A-63022). (b) A-10859: device D-79802 was used by A-10859 and A-78340. (c) A-83577: device D-40018 was used by the non-adjacent path accounts A-83094 and A-14799. The same device was also used, much later, by off-route account A-34114 for T038409, which has no onward link. Every other path account sent from a separate device.  
  Claims: S1 (supported), S2 (supported), S3 (supported), S4 (supported), E7 (supported), E8 (supported), E9 (supported), E10 (supported), E11 (supported), E12 (supported), E13 (supported), E14 (supported), E1 (supported), E2 (supported), E4 (supported), E5 (supported), E17 (supported), E19 (supported), E22 (supported), X15 (supported)
- **F8** No device was used to send by two or more path accounts for alerts A-20636, A-85921 and A-28137.  
  Claims: X1 (supported), X2 (supported), X3 (supported)
- **F9** None of the end accounts (A-92332, A-85287, A-54215, A-39382, A-36729, A-10758) has a fan-in alert of its own.  
  Claims: X16 (supported), X17 (supported), X18 (supported), X19 (supported), X20 (supported), X21 (supported)
- **F10** The six alerts look alike as indicators (6–8 distinct senders, one transfer per sender, inside one hour). The recorded relationships separate them into three groups. (1) A-37573, A-83577 and A-10859: every contributing transfer has an onward link, the paths reach 3–5 links deep, and onward amounts are close to the window total. In these three, path accounts share a device: one device across four accounts for A-37573, two accounts for A-10859, two non-adjacent accounts plus one off-route account for A-83577. (2) A-20636 and A-85921: one onward link to a single account, not all contributions linked, and no shared device. (3) A-28137: no onward links and no shared device. Interpretation follows the timing and device records only. For group 3 the only recorded relationship is the fan-in itself. Groups 1 and 2 also have recorded timing links, and group 1 adds device overlap.  
  Claims: I1 (supported), I2 (supported), I3 (supported), I4 (supported), I5 (supported), I6 (supported), R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), X1 (supported), X2 (supported), X3 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-37573's sequence may be a single-operator layering route. One device sent every onward transfer from four accounts, the same account sequence happened twice, and each step was slightly smaller than the one before. A shared device does not establish common control or identity, and onward links record timing only, not that the same funds moved.  
  References: S2, R4, P5, P6
- **H2** A-10859 and A-78340 may be controlled by the same party, given shared device D-79802. A-83094 and A-14799 may be related through D-40018. This could equally reflect a shared or public device.  
  References: S1, S3, S4
- **H3** A-28137 may be an ordinary collection account, for example many small payments to one payee. A-85921's uniform 2,500 contributions may reflect a fixed-price payment or a scripted pattern. The data does not distinguish these possibilities.  
  References: I3, I6, E21

## Unresolved questions

- **U1** What happens at end accounts A-92332, A-85287, A-54215, A-39382, A-36729 and A-10758 beyond this dataset? A path ending here means only that no further qualifying transfer exists in this bounded replay.  
  References: R1, R2, R4, R5, R6
- **U2** Who owns or uses devices D-45880, D-79802 and D-40018, and how is A-34114 related to A-83094 and A-14799, if at all? The data records only device use per transfer.  
  References: S2, S1, S4
- **U3** Do the onward transfers carry the same funds as the contributing credits? Onward links record timing only, and no balance or fund-tracing data is available.  
  References: P1, P5, P7
- **U4** Is anything known about the contributing senders (customer data, earlier history outside this replay)? None of them shares a device with any other account in this dataset.  
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
| E23 | event | transfer="T018248", sender="A-31752", receiver="A-28137", amount_minor=5500, event_time_ms=1795006260000, device="D-83530" | supported |
| E24 | event | transfer="T005750", sender="A-10868", receiver="A-85921", amount_minor=2500, event_time_ms=1794855900000, device="D-61312" | supported |
| E25 | event | transfer="T005978", sender="A-35236", receiver="A-85921", amount_minor=2500, event_time_ms=1794858600000, device="D-25672" | supported |
| I1 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| I2 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| I3 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| I4 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| I5 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| I6 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| P1 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| P2 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P3 | onward_path | transfers=["T011536", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P4 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| P5 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P6 | onward_path | transfers=["T003319", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P7 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| P8 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
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
| X1 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| X2 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| X3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| X4 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| X5 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| X8 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| X9 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| X10 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| X11 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| X12 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| X13 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| X14 | absence | kind="no_onward_link_from_transfer", subject="T018852" | supported |
| X15 | absence | kind="no_onward_link_from_transfer", subject="T038409" | supported |
| X16 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| X17 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| X18 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| X19 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| X20 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| X21 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 75 of 75 claims supported; reference validity 1.0 (109 of 109 distinct ids resolve); 14 queries (0 failed), 10 model requests, 139958 input tokens (cache included) and 13641 output tokens, 167.6 s.
