# Case note: large case, table arm, run 1

Agent output, recorded run of 2026-11-13T19:31:13+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: one bounded replay (run:5ce89f521e5e, 50000 dataset events, 3 of 3 jobs completed, clink exit status 0, not cancelled; fan-in threshold 5 distinct senders per 1-hour event-time window; onward gap of up to 30 minutes). The dataset holds 50000 transfers, 12072 accounts, 12321 devices, 691 onward links and 6 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C1 (supported), C2 (supported), C3 (supported), C4 (supported), C5 (supported)
- **F2** Alert fan_in:A-10859:1794924000000: account A-10859, window 1794924000000 to 1794927600000, 6 senders, 6 transfers, total 204000 (T011431, T011465, T011494, T011536, T011572, T011610). Every contributing transfer has an onward link. The candidate onward-transfer paths are up to 3 onward links long and split in two. One path goes A-10859 > A-78340 > A-75793 > A-92332 (T011583, T011600, T011628). The other goes A-10859 > A-78340 > A-85287 (T011670 or T011583, then T011695). The paths end at A-92332 and A-85287, where this dataset has no further qualifying transfer. Path accounts: A-10859, A-78340, A-75793, A-92332, A-85287. Shared device: D-79802 sent transfers from both A-10859 and A-78340, the alerted account and the next account on the paths. It sent T011583, T011670, T011600 and T011695.  
  Claims: I1 (supported), R1 (supported), P4 (supported), P5 (supported), S1 (supported), E5 (supported), E6 (supported), E7 (supported), E8 (supported), E9 (supported), N12 (no such claim), N14 (no such claim)
- **F3** Alert fan_in:A-37573:1794823200000: account A-37573, window 1794823200000 to 1794826800000, 7 senders, 7 transfers, total 379500 (T003057, T003091, T003124, T003154, T003248, T003287, T003319). All 7 have onward links. There are two parallel candidate paths, each 4 onward links long, over the same accounts A-37573 > A-38045 > A-93288 > A-63022 > A-54215. The first runs T003168, T003182, T003201, T003222. The second runs T003391, T003416, T003433, T003454. Both end at A-54215, where this dataset has no further qualifying transfer. Shared device: D-45880 sent all 8 onward transfers, covering 4 of the 5 path accounts (A-37573, A-38045, A-93288, A-63022). A-54215 sent no transfers in this dataset.  
  Claims: I2 (supported), R2 (supported), P2 (supported), P3 (supported), S2 (supported), E1 (supported), E2 (supported), E3 (supported), E4 (supported), N13 (no such claim)
- **F4** Alert fan_in:A-83577:1795057200000: account A-83577, window 1795057200000 to 1795060800000, 8 senders, 8 transfers, total 174500 (T022417 to T022561). All 8 have onward links. One candidate path follows, 5 onward links long: A-83577 > A-56768 > A-83094 > A-43725 > A-14799 > A-39382 (T022572, T022592, T022609, T022629, T022649). It ends at A-39382, where this dataset has no further qualifying transfer. Shared device: D-40018 sent from both A-83094 (T022609) and A-14799 (T022649). These two accounts are not next to each other on the path. D-40018 also sent T038409 from A-34114, an account that is not on this alert's paths. The other onward transfers on the path came from distinct devices.  
  Claims: I3 (supported), R3 (supported), P1 (supported), S3 (supported), E10 (supported), E11 (supported), E12 (supported), E17 (supported), N15 (no such claim)
- **F5** Alert fan_in:A-20636:1795190400000: account A-20636, window 1795190400000 to 1795194000000, 6 senders, 6 transfers, total 36000. Five contributing transfers each have an onward link to the same debit, T033506 (A-20636 to A-36729, 30000). T033316 has no onward link. The longest path is 1 onward link, ending at A-36729. Path accounts: A-20636, A-36729. No device was shared between them. A-36729's only outgoing transfer, T034128, came 7800000 ms (about 2.2 h) after T033506, beyond the 30-minute gap.  
  Claims: I4 (supported), R4 (supported), P6 (supported), X1 (supported), X4 (supported), E13 (supported), E15 (supported)
- **F6** Alert fan_in:A-85921:1794855600000: account A-85921, window 1794855600000 to 1794859200000, 6 senders, 6 transfers, each 2500, total 15000. Four contributing transfers each have an onward link to T005888 (A-85921 to A-10758, 9500). T005934 and T005978 have no onward link. The longest path is 1 onward link, ending at A-10758. Path accounts: A-85921, A-10758. No device was shared between them.  
  Claims: I5 (supported), R5 (supported), P7 (supported), X2 (supported), X5 (supported), X6 (supported), E14 (supported)
- **F7** Alert fan_in:A-28137:1795003200000: account A-28137, window 1795003200000 to 1795006800000, 7 senders, 7 transfers, total 29500. None of the 7 contributing transfers has an onward link, so the alert starts no candidate path (max depth 0, no end accounts, and A-28137 is the only path account). A-28137's only outgoing transfer in the dataset, T018852 at 1795013700000, is more than 30 minutes after its last contributing credit (T018248 at 1795006260000).  
  Claims: I6 (supported), R6 (supported), X3 (supported), X7 (supported), X8 (supported), X9 (supported), X10 (supported), X11 (supported), X12 (supported), X13 (supported), E16 (supported)
- **F8** None of the accounts where paths end (A-92332, A-85287, A-54215, A-39382, A-36729, A-10758) has a fan-in indicator of its own.  
  Claims: X14 (supported), X15 (supported), X16 (supported), X17 (supported), X18 (supported), X19 (supported)
- **F9** What separates the six alerts, which look similar as indicators (6 to 8 senders, one hour each): (a) onward-link depth runs 0 (A-28137), 1 (A-20636, A-85921), 3 (A-10859), 4 (A-37573) and 5 (A-83577). (b) The shape differs: one branch in A-10859 ends at two accounts, two parallel paths over the same accounts in A-37573 end at one account, and A-83577 has a single linear path. (c) Devices: the deeper three each have a device that sent from two or more of their path accounts (D-79802, D-45880, D-40018). The shallow or empty three have none. D-45880 is the strongest case, with one device behind every onward transfer from 4 path accounts. (d) A-28137 has no onward links at all, so for it there is no recorded relationship beyond the fan-in itself. All of this traces back to recorded transfers, links and device fields (traceable provenance), but none of it establishes fraud, common control or the movement of the same funds.  
  Claims: R1 (supported), R2 (supported), R3 (supported), R4 (supported), R5 (supported), R6 (supported), S1 (supported), S2 (supported), S3 (supported), X4 (supported), X5 (supported), X6 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** In alert A-37573, one device (D-45880) sends a quick series of onward transfers through four accounts, each a few minutes after the credit before it and slightly smaller. This could fit the four accounts being operated together, as in a layering pattern. The data records only the device field and the timing. It does not establish who controlled the accounts or that the same funds moved.  
  References: S2, P2, P3, R2
- **H2** In alerts A-10859 and A-83577, a device is shared by path accounts (D-79802 and D-40018). This could point to a common operator on parts of those paths. D-40018 is also used by an off-path account (A-34114), which may instead suggest a shared or public device.  
  References: S1, S3, E17
- **H3** Alert A-28137 has no onward links and no shared device on its route. It may be benign collection activity, such as small payments from many senders. A-20636 and A-85921, each with a single onward hop, may be similar. The data does not establish this either way.  
  References: R6, R4, R5, X3, X4, X5

## Unresolved questions

- **U1** Who owns or controls the path accounts and the shared devices D-45880, D-79802 and D-40018? The data records device use only, not identity.  
  References: S1, S2, S3
- **U2** What happens at the end accounts (A-92332, A-85287, A-54215, A-39382, A-36729, A-10758) outside this bounded dataset? A path ending here only means this dataset has no further qualifying transfer.  
  References: R1, R2, R3, R4, R5
- **U3** Do the onward transfers carry the same funds as the contributing credits? Onward links record timing only.  
  References: P1, P2, P4
- **U4** Would activity outside the replay change the picture for A-28137, or for transfers whose debits may fall more than 30 minutes after the credit, such as T018852 and T034128?  
  References: E16, E15, R6

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| E1 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| E2 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| E3 | event | transfer="T003391", sender="A-37573", receiver="A-38045", amount_minor=176000, event_time_ms=1794827520000, device="D-45880" | supported |
| E4 | event | transfer="T003454", sender="A-63022", receiver="A-54215", amount_minor=166000, event_time_ms=1794828240000, device="D-45880" | supported |
| E5 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| E6 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| E7 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| E8 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| E9 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| E10 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| E11 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| E12 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| E13 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| E14 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| E15 | event | transfer="T034128", sender="A-36729", receiver="A-34558", amount_minor=28000, event_time_ms=1795200600000, device="D-30793" | supported |
| E16 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| E17 | event | transfer="T038409", sender="A-34114", receiver="A-39862", amount_minor=12000, event_time_ms=1795252440000, device="D-40018" | supported |
| I1 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| I2 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| I3 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| I4 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| I5 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| I6 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| P1 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| P2 | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P3 | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| P4 | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| P5 | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| P6 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| P7 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
| R1 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-92332", "A-85287"] | supported |
| R2 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| R3 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| R4 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| R5 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| R6 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| S1 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| S2 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| S3 | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| X1 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| X2 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| X3 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| X4 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| X5 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| X6 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| X7 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| X8 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| X9 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| X10 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| X11 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| X12 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| X13 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| X14 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| X15 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| X16 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| X17 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| X18 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| X19 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| C1 | count | pattern="fan_in_alerts", value=6 | supported |
| C2 | count | pattern="transfers", value=50000 | supported |
| C3 | count | pattern="onward_links", value=691 | supported |
| C4 | count | pattern="accounts", value=12072 | supported |
| C5 | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 63 of 63 claims supported; reference validity 1.0 (104 of 104 distinct ids resolve); 11 queries (0 failed), 7 model requests, 113949 input tokens (cache included) and 11570 output tokens, 139.2 s.
