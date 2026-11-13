# Case note: large case, graph arm, run 1

Agent output, recorded run of 2026-11-13T19:28:10+00:00: graph arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in this dataset. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Scope: the run run:5ce89f521e5e is a bounded replay (not cancelled, clink exit status 0, 3 of 3 jobs completed) of 50,000 events. It holds 50,000 transfers, 12,072 accounts, 12,321 devices, 691 onward links and 6 fan-in alerts. Fan-in means at least 5 distinct senders inside one event-time hour. An onward link means a debit within 1,800,000 ms (30 min) after a credit. Everything below holds only for this dataset as this run processed it.  
  Claims: c-alerts (supported), c-transfers (supported), c-links (supported), c-accounts (supported), c-devices (supported)
- **F2** Alert fan_in:A-37573:1794823200000. Window 1794823200000 to 1794826800000; 7 senders, 7 transfers, total 379500. All 7 contributing transfers start onward links. T003057, T003091, T003124 and T003154 link to T003168. T003248, T003287 and T003319 link to T003391. This gives two separate 4-link sequences through the same accounts, A-37573 > A-38045 > A-93288 > A-63022 > A-54215. Both end at A-54215, which sent no transfers in this dataset. Max depth is 4. Path accounts: A-37573, A-38045, A-93288, A-63022, A-54215.  
  Claims: i-37573 (supported), p-37573-a (supported), p-37573-b (supported), r-37573 (supported), e-T003168 (supported), e-T003182 (supported), e-T003201 (supported), e-T003222 (supported), e-T003391 (supported), e-T003416 (supported), e-T003433 (supported), e-T003454 (supported)
- **F3** Alert fan_in:A-37573:1794823200000, devices: all 8 onward transfers on its paths were sent from one device, D-45880. In this dataset D-45880 was used by exactly four accounts, A-37573, A-38045, A-93288 and A-63022, all of them on this alert's paths.  
  Claims: sd-45880 (supported), e-T003168 (supported), e-T003182 (supported), e-T003201 (supported), e-T003222 (supported), e-T003391 (supported), e-T003416 (supported), e-T003433 (supported), e-T003454 (supported)
- **F4** Alert fan_in:A-85921:1794855600000. Window 1794855600000 to 1794859200000; 6 senders, 6 transfers, total 15000. Every contributing transfer is 2500. T005750, T005789, T005830 and T005868 link to T005888 (A-85921 to A-10758, 9500). A-10758 sent nothing in this dataset, so the paths end there. T005934 and T005978 arrived after T005888 and have no onward link. Max depth is 1. Path accounts: A-85921, A-10758. No device was used by two or more of its path accounts.  
  Claims: i-85921 (supported), p-85921 (supported), r-85921 (supported), e-T005888 (supported), e-T005750 (supported), e-T005934 (supported), e-T005978 (supported), ab-T005934 (supported), ab-T005978 (supported), ab-sd-85921 (supported)
- **F5** Alert fan_in:A-10859:1794924000000. Window 1794924000000 to 1794927600000; 6 senders, 6 transfers, total 204000. All 6 contributing transfers start onward links. Paths go from A-10859 to A-78340 (via T011583 or T011670). From A-78340 they either go A-75793 > A-92332 (T011600, T011628; 3 links) or end at A-85287 (T011695; 2 links). Max depth is 3. The paths end at two accounts, A-92332 and A-85287. Path accounts: A-10859, A-78340, A-75793, A-92332, A-85287. Device D-79802 was used by A-10859 and A-78340, the alerted account and the first account after it. It was used by no other account in the dataset.  
  Claims: i-10859 (supported), p-10859-a (supported), p-10859-b (supported), p-10859-c (supported), r-10859 (supported), sd-79802 (supported), e-T011583 (supported), e-T011600 (supported), e-T011628 (supported), e-T011670 (supported), e-T011695 (supported)
- **F6** Alert fan_in:A-28137:1795003200000. Window 1795003200000 to 1795006800000; 7 senders, 7 transfers, total 29500. None of its 7 contributing transfers has an onward link, so it has no onward paths: max depth 0, no end accounts, and its only path account is A-28137. A-28137's only debit in the dataset is T018852 (21000, to A-87539, at 1795013700000). That is 7,440,000 ms after its last contributing credit (T018248), beyond the 30-minute onward window, and no onward link points to it. No shared device on its path.  
  Claims: i-28137 (supported), r-28137 (supported), ab-T018004 (supported), ab-T018035 (supported), ab-T018065 (supported), ab-T018090 (supported), ab-T018160 (supported), ab-T018198 (supported), ab-T018248 (supported), e-T018852 (supported), ab-sd-28137 (supported)
- **F7** Alert fan_in:A-83577:1795057200000. Window 1795057200000 to 1795060800000; 8 senders, 8 transfers, total 174500. All 8 contributing transfers link to T022572. From there one 5-link sequence runs A-83577 > A-56768 > A-83094 > A-43725 > A-14799 > A-39382, the deepest path of any alert. It ends at A-39382, which sent nothing in this dataset. Path accounts: A-83577, A-56768, A-83094, A-43725, A-14799, A-39382.  
  Claims: i-83577 (supported), p-83577 (supported), r-83577 (supported), e-T022572 (supported), e-T022592 (supported), e-T022609 (supported), e-T022629 (supported), e-T022649 (supported)
- **F8** Alert fan_in:A-83577:1795057200000, devices: D-40018 was used by two of its path accounts, A-83094 (T022609) and A-14799 (T022649). These are not adjacent on the path. D-40018 was also used by A-34114, which is not on any alert path, for T038409 (12000 to A-39862 at 1795252440000). T038409 has no onward links. The other path transfers each used a device that only that account used among those listed.  
  Claims: sd-40018-route (supported), sd-40018-all (supported), e-T022609 (supported), e-T022649 (supported), e-T038409 (supported)
- **F9** Alert fan_in:A-20636:1795190400000. Window 1795190400000 to 1795194000000; 6 senders, 6 transfers, total 36000. T033368, T033403, T033439, T033474 and T033495 link to T033506 (A-20636 to A-36729, 30000). T033316 has no onward link. Max depth is 1 and the paths end at A-36729. A-36729's only later debit, T034128 at 1795200600000, is 7,800,000 ms after T033506 and is not linked. Path accounts: A-20636, A-36729. No shared device on its path.  
  Claims: i-20636 (supported), p-20636 (supported), r-20636 (supported), e-T033506 (supported), e-T034128 (supported), ab-T033316 (supported), ab-sd-20636 (supported)
- **F10** None of the accounts on the alert paths other than the six alerted accounts has a fan-in alert. Within the dataset, no device used to send a contributing transfer was used by any other account.  
  Claims: ab-fa-54215 (supported), ab-fa-10758 (supported), ab-fa-92332 (supported), ab-fa-85287 (supported), ab-fa-39382 (supported), ab-fa-36729 (supported), ab-fa-78340 (supported), ab-fa-38045 (supported), c-alerts (supported)
- **F11** What tells the alerts apart: as indicators the six are alike (5 to 8 distinct senders in one hour, one transfer per sender). The recorded relationships differ. (a) Onward links: A-28137 has none. A-85921 and A-20636 have one link each, to a single account, and some of their credits are unlinked. A-10859, A-37573 and A-83577 have multi-link paths of depth 3, 4 and 5, and every one of their contributing transfers starts a path. (b) Shared devices on the paths: A-37573's paths use one device, D-45880, across four of its five path accounts. A-10859's alerted account and first path account share D-79802. A-83577 has two non-adjacent path accounts on D-40018, which one outside account also used. A-85921, A-28137 and A-20636 have no shared device on their paths. (c) Amounts: A-85921 received six transfers of exactly 2500 each. A-37573's two path sequences repeat the same account order.  
  Claims: r-28137 (supported), r-85921 (supported), r-20636 (supported), r-10859 (supported), r-37573 (supported), r-83577 (supported), sd-45880 (supported), sd-79802 (supported), sd-40018-route (supported), ab-sd-85921 (supported), ab-sd-28137 (supported), ab-sd-20636 (supported), i-85921 (supported), p-37573-a (supported), p-37573-b (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-37573 has deep, repeated onward-link sequences, and four of its path accounts sent from one device, D-45880. That fits the hypothesis that one party operates those accounts as a relay. The data does not establish ownership, control, or that the same funds moved. A shared device is consistent with other explanations too, such as a shared or institutional terminal or a data artefact.  
  References: F2, F3, sd-45880
- **H2** A-10859 and A-83577 show the same pattern more weakly: a device shared by two path accounts (D-79802 and D-40018). For D-40018, the presence of the off-route account A-34114 could mean a shared or reused device rather than common control. Both readings are hypotheses only.  
  References: F5, F7, F8
- **H3** A-28137, A-85921 and A-20636 have no or shallow onward links and no shared devices on their paths. They could be benign aggregation, for example collections or a merchant-like receiver. The uniform 2500 amounts into A-85921 could be fixed-price payments or structured payments. The data does not say which, and these alerts should not be ranked as innocuous on that basis alone.  
  References: F4, F6, F9
- **H4** Ranking by recorded relationships alone, A-37573 looks the most worth reviewing, followed by A-83577 and A-10859. This is a triage suggestion, not a finding of fraud.  
  References: F11

## Unresolved questions

- **U1** Did the debits on the onward links actually carry the funds from the fan-in credits? Onward links record timing within 30 minutes only, so the data cannot answer this.  
  References: F2, F5, F7
- **U2** What happened to the accounts where the paths end (A-54215, A-10758, A-92332, A-85287, A-39382, A-36729, and A-28137 itself) outside this bounded dataset? The paths end only because no further qualifying transfer exists here.  
  References: r-37573, r-85921, r-10859, r-83577, r-20636, r-28137
- **U3** Who uses devices D-45880, D-79802 and D-40018, and how is A-34114 related to the A-83577 path accounts, if at all? The data records device use, not identity or ownership.  
  References: sd-45880, sd-79802, sd-40018-all
- **U4** Do the senders into each alerted account have any relationship beyond their single transfers? Nothing recorded here links them, and nothing outside the dataset is available.  
  References: i-37573, i-85921, i-10859, i-28137, i-83577, i-20636

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| e-T003168 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| e-T003182 | event | transfer="T003182", sender="A-38045", receiver="A-93288", amount_minor=191000, event_time_ms=1794824940000, device="D-45880" | supported |
| e-T003201 | event | transfer="T003201", sender="A-93288", receiver="A-63022", amount_minor=187500, event_time_ms=1794825180000, device="D-45880" | supported |
| e-T003222 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| e-T003391 | event | transfer="T003391", sender="A-37573", receiver="A-38045", amount_minor=176000, event_time_ms=1794827520000, device="D-45880" | supported |
| e-T003416 | event | transfer="T003416", sender="A-38045", receiver="A-93288", amount_minor=172500, event_time_ms=1794827700000, device="D-45880" | supported |
| e-T003433 | event | transfer="T003433", sender="A-93288", receiver="A-63022", amount_minor=169000, event_time_ms=1794827940000, device="D-45880" | supported |
| e-T003454 | event | transfer="T003454", sender="A-63022", receiver="A-54215", amount_minor=166000, event_time_ms=1794828240000, device="D-45880" | supported |
| e-T005888 | event | transfer="T005888", sender="A-85921", receiver="A-10758", amount_minor=9500, event_time_ms=1794857400000, device="D-97117" | supported |
| e-T005750 | event | transfer="T005750", sender="A-10868", receiver="A-85921", amount_minor=2500, event_time_ms=1794855900000, device="D-61312" | supported |
| e-T005934 | event | transfer="T005934", sender="A-30679", receiver="A-85921", amount_minor=2500, event_time_ms=1794858060000, device="D-11053" | supported |
| e-T005978 | event | transfer="T005978", sender="A-35236", receiver="A-85921", amount_minor=2500, event_time_ms=1794858600000, device="D-25672" | supported |
| e-T011583 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| e-T011600 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| e-T011628 | event | transfer="T011628", sender="A-75793", receiver="A-92332", amount_minor=117500, event_time_ms=1794926460000, device="D-10265" | supported |
| e-T011670 | event | transfer="T011670", sender="A-10859", receiver="A-78340", amount_minor=95000, event_time_ms=1794927000000, device="D-79802" | supported |
| e-T011695 | event | transfer="T011695", sender="A-78340", receiver="A-85287", amount_minor=118000, event_time_ms=1794927300000, device="D-79802" | supported |
| e-T018852 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| e-T022572 | event | transfer="T022572", sender="A-83577", receiver="A-56768", amount_minor=172000, event_time_ms=1795059000000, device="D-73452" | supported |
| e-T022592 | event | transfer="T022592", sender="A-56768", receiver="A-83094", amount_minor=169500, event_time_ms=1795059180000, device="D-96125" | supported |
| e-T022609 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| e-T022629 | event | transfer="T022629", sender="A-43725", receiver="A-14799", amount_minor=164000, event_time_ms=1795059600000, device="D-13859" | supported |
| e-T022649 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| e-T033506 | event | transfer="T033506", sender="A-20636", receiver="A-36729", amount_minor=30000, event_time_ms=1795192800000, device="D-52544" | supported |
| e-T034128 | event | transfer="T034128", sender="A-36729", receiver="A-34558", amount_minor=28000, event_time_ms=1795200600000, device="D-30793" | supported |
| e-T038409 | event | transfer="T038409", sender="A-34114", receiver="A-39862", amount_minor=12000, event_time_ms=1795252440000, device="D-40018" | supported |
| i-37573 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| i-85921 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| i-10859 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| i-28137 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| i-83577 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| i-20636 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| p-37573-a | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| p-37573-b | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", ends_at="A-54215" | supported |
| p-85921 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", ends_at="A-10758" | supported |
| p-10859-a | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-92332" | supported |
| p-10859-b | onward_path | transfers=["T011431", "T011583", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| p-10859-c | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", ends_at="A-85287" | supported |
| p-83577 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", ends_at="A-39382" | supported |
| p-20636 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", ends_at="A-36729" | supported |
| r-37573 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| r-85921 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| r-10859 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-92332", "A-85287"] | supported |
| r-28137 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| r-83577 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| r-20636 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| sd-45880 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| sd-79802 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| sd-40018-route | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| sd-40018-all | shared_device | device="D-40018", accounts=["A-34114", "A-83094", "A-14799"] | supported |
| ab-T005934 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| ab-T005978 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| ab-T018004 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| ab-T018035 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| ab-T018065 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| ab-T018090 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| ab-T018160 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| ab-T018198 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| ab-T018248 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| ab-T033316 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| ab-sd-85921 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| ab-sd-28137 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| ab-sd-20636 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| ab-fa-54215 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| ab-fa-10758 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| ab-fa-92332 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| ab-fa-85287 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| ab-fa-39382 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| ab-fa-36729 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| ab-fa-78340 | absence | kind="no_fan_in_alert_for_account", subject="A-78340" | supported |
| ab-fa-38045 | absence | kind="no_fan_in_alert_for_account", subject="A-38045" | supported |
| c-alerts | count | pattern="fan_in_alerts", value=6 | supported |
| c-transfers | count | pattern="transfers", value=50000 | supported |
| c-links | count | pattern="onward_links", value=691 | supported |
| c-accounts | count | pattern="accounts", value=12072 | supported |
| c-devices | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 76 of 76 claims supported; reference validity 1.0 (112 of 112 distinct ids resolve); 13 queries (0 failed), 9 model requests, 119818 input tokens (cache included) and 15060 output tokens, 182.8 s.
