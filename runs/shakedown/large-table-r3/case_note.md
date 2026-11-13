# Case note: fan-in alerts in a bounded replay (large case)

Agent output, live run of 2026-11-13T19:18:13+00:00: table arm, model claude-opus-5-5 (requested global.anthropic.claude-opus-5-5, effort high), status completed.

Scope: one bounded replay of a synthetic event file, as processed by the run its evidence records. Nothing here is a conclusion about data outside it. Recorded relationships are not proof of fraud, ownership, identity or causation. The checker validates the structured claims below against the original events and the graph; it does not validate the wording of findings.

## Findings

- **F1** Bounded replay run:5ce89f521e5e (50,000 events, 3/3 jobs completed, clink exit status 0, not cancelled; parameters: fan-in needs at least 5 distinct senders inside a 3,600,000 ms window, onward max gap 1,800,000 ms). It holds 50,000 transfers, 691 onward links, 12,072 accounts, 12,321 devices and 6 fan-in alerts. Everything below holds only for this dataset as this run processed it.  
  Claims: C-cnt-alerts (supported), C-cnt-transfers (supported), C-cnt-links (supported), C-cnt-accounts (supported), C-cnt-devices (supported)
- **F2** fan_in:A-37573:1794823200000: 7 senders, 7 transfers, 379,500 total. All 7 contributing transfers were passed on. Chains run up to 4 onward links, A-37573 -> A-38045 -> A-93288 -> A-63022 -> A-54215, in two waves (T003168/T003182/T003201/T003222 and T003391/T003416/T003433/T003454). The money comes to rest only at A-54215. Device D-45880 sent from all four sending accounts on the route (A-37573, A-38045, A-93288, A-63022), and the dataset records no other sender using it.  
  Claims: C-ind-37573 (supported), C-path-37573a (supported), C-path-37573b (supported), C-reach-37573 (supported), C-dev-45880 (supported), C-ev-T003168 (supported), C-ev-T003222 (supported)
- **F3** fan_in:A-83577:1795057200000: 8 senders, 8 transfers, 174,500 total. All 8 contributing transfers feed T022572. The single chain has 5 onward links, the deepest of any alert: A-83577 -> A-56768 -> A-83094 -> A-43725 -> A-14799 -> A-39382. Money comes to rest at A-39382. Device D-40018 sent from two route accounts that are not adjacent on the route, A-83094 (T022609) and A-14799 (T022649). It was also used by A-34114, which is not on the route (T038409).  
  Claims: C-ind-83577 (supported), C-path-83577 (supported), C-reach-83577 (supported), C-dev-40018-route (supported), C-dev-40018-all (supported), C-ev-T022609 (supported), C-ev-T022649 (supported), C-ev-T038409 (supported)
- **F4** fan_in:A-10859:1794924000000: 6 senders, 6 transfers, 204,000 total. All 6 contributing transfers were passed on to A-78340 (T011583, T011670). The route then splits. At most 3 onward links lead to A-92332 via A-75793 (T011600, T011628). A 2-link branch leads to A-85287 (T011695). There are two resting accounts, A-92332 and A-85287. Device D-79802 sent from both A-10859 and A-78340, the first two accounts on the route. No other account in the dataset used it.  
  Claims: C-ind-10859 (supported), C-path-10859a (supported), C-path-10859b (supported), C-reach-10859 (supported), C-dev-79802 (supported), C-ev-T011583 (supported), C-ev-T011600 (supported)
- **F5** fan_in:A-20636:1795190400000: 6 senders, 6 transfers, 36,000 total. 5 of the 6 contributing transfers feed one 1-link hop, T033506 (30,000 to A-36729), where the money comes to rest. T033316 was not passed on. No device was used by two route accounts. A-36729's device D-30793 was also used by A-69026, which is not on the route.  
  Claims: C-ind-20636 (supported), C-path-20636 (supported), C-reach-20636 (supported), C-abs-T033316 (supported), C-abs-dev-20636 (supported), C-dev-30793 (supported)
- **F6** fan_in:A-85921:1794855600000: 6 senders, 6 transfers of exactly 2,500 each, 15,000 total. 4 of the contributing transfers feed one 1-link hop, T005888 (9,500 to A-10758), where the money comes to rest. T005934 and T005978 were not passed on. No device was used by two route accounts.  
  Claims: C-ind-85921 (supported), C-path-85921 (supported), C-reach-85921 (supported), C-abs-T005934 (supported), C-abs-T005978 (supported), C-abs-dev-85921 (supported)
- **F7** fan_in:A-28137:1795003200000: 7 senders, 7 transfers, 29,500 total. None of its 7 contributing transfers was passed on (max depth 0, no resting account, route is only A-28137). A-28137 does have a later outgoing transfer, T018852 at 1795013700000. That is about 2 h after the last contribution, beyond the 30-min onward gap, so it is not an onward link. No device is shared on the route.  
  Claims: C-ind-28137 (supported), C-reach-28137 (supported), C-abs-T018004 (supported), C-abs-T018035 (supported), C-abs-T018065 (supported), C-abs-T018090 (supported), C-abs-T018160 (supported), C-abs-T018198 (supported), C-abs-T018248 (supported), C-abs-dev-28137 (supported), C-ev-T018852 (supported)
- **F8** As indicators, all six alerts look alike: 6 to 8 distinct senders, one transfer per sender, inside one hour. They differ in the relationships recorded after the fan-in. (a) Onward depth: 4 for A-37573, 5 for A-83577, 3 for A-10859, 1 for A-20636 and A-85921, 0 for A-28137. (b) Pass-through completeness: every contribution was passed on for A-37573, A-83577 and A-10859; only some were for A-20636 and A-85921; none were for A-28137. (c) Device sharing on the route: one device on all four sending route accounts (A-37573); one device on two non-adjacent route accounts (A-83577); one device on the first two route accounts (A-10859); none for the other three. The resting accounts with recorded onward reach (A-54215, A-39382, A-92332, A-85287, A-36729, A-10758) have no fan-in alert of their own.  
  Claims: C-reach-37573 (supported), C-reach-83577 (supported), C-reach-10859 (supported), C-reach-20636 (supported), C-reach-85921 (supported), C-reach-28137 (supported), C-dev-45880 (supported), C-dev-40018-route (supported), C-dev-79802 (supported), C-abs-dev-20636 (supported), C-abs-dev-85921 (supported), C-abs-dev-28137 (supported), C-abs-fan-54215 (supported), C-abs-fan-39382 (supported), C-abs-fan-92332 (supported), C-abs-fan-85287 (supported), C-abs-fan-36729 (supported), C-abs-fan-10758 (supported)

## Hypotheses

Interpretations the data does not establish.

- **H1** A-37573 may be a layering chain controlled from one place: four accounts send from the same device D-45880, and each hop takes roughly 3–5 minutes with small amount decreases. The data does not establish that one party controls these accounts, only that the device was recorded for their transfers.  
  References: F2, C-dev-45880, C-reach-37573
- **H2** A-83577 may be multi-hop layering. Its 5-hop route has one device reused at hops 3 and 5 (D-40018), which could point to a common operator behind A-83094 and A-14799. The device also appears on unrelated account A-34114, so it could instead be a shared or public device.  
  References: F3, C-dev-40018-route, C-dev-40018-all
- **H3** A-10859 and A-78340 may be linked, since both used D-79802, and the money was split across two resting accounts. This could be dispersal, or ordinary business between related accounts.  
  References: F4, C-dev-79802
- **H4** A-20636, A-85921 and A-28137 may be benign aggregation, for example collections or shared bills: small amounts (A-85921 got identical 2,500 payments), shallow or no onward movement, and no device sharing on the route. Under the recorded relationships they are weaker candidates than A-37573, A-83577 and A-10859, but the data does not show any of them to be legitimate.  
  References: F5, F6, F7

## Unresolved questions

- **U1** Who owns or controls the accounts and devices? A shared device record does not establish identity, ownership or common control.  
  References: C-dev-45880, C-dev-40018-route, C-dev-79802, C-dev-30793
- **U2** What happened to funds at the resting accounts (A-54215, A-39382, A-92332, A-85287, A-36729, A-10758) after this bounded replay, or through transfers more than 30 minutes apart, which onward links do not capture?  
  References: C-reach-37573, C-reach-83577, C-reach-10859, C-reach-20636, C-reach-85921
- **U3** Do the onward links mean the same money moved? Onward links only pair a credit with a later debit within 30 minutes. They do not prove that the funds were the same or that one transfer caused the other.  
  References: F8
- **U4** Is A-28137's later transfer T018852 (21,000 to A-87539, about 2 h after the fan-in) related to the incoming funds? The run's link rule does not relate it.  
  References: C-ev-T018852, C-reach-28137

## Claims, as checked

| Claim | Type | Asserts | Checker |
|---|---|---|---|
| C-ev-T003168 | event | transfer="T003168", sender="A-37573", receiver="A-38045", amount_minor=196000, event_time_ms=1794824760000, device="D-45880" | supported |
| C-ev-T003222 | event | transfer="T003222", sender="A-63022", receiver="A-54215", amount_minor=184000, event_time_ms=1794825480000, device="D-45880" | supported |
| C-ev-T022609 | event | transfer="T022609", sender="A-83094", receiver="A-43725", amount_minor=167000, event_time_ms=1795059360000, device="D-40018" | supported |
| C-ev-T022649 | event | transfer="T022649", sender="A-14799", receiver="A-39382", amount_minor=161500, event_time_ms=1795059900000, device="D-40018" | supported |
| C-ev-T038409 | event | transfer="T038409", sender="A-34114", receiver="A-39862", amount_minor=12000, event_time_ms=1795252440000, device="D-40018" | supported |
| C-ev-T011583 | event | transfer="T011583", sender="A-10859", receiver="A-78340", amount_minor=150000, event_time_ms=1794925980000, device="D-79802" | supported |
| C-ev-T011600 | event | transfer="T011600", sender="A-78340", receiver="A-75793", amount_minor=120000, event_time_ms=1794926160000, device="D-79802" | supported |
| C-ev-T018852 | event | transfer="T018852", sender="A-28137", receiver="A-87539", amount_minor=21000, event_time_ms=1795013700000, device="D-94558" | supported |
| C-ind-10859 | indicator | indicator="fan_in:A-10859:1794924000000", account="A-10859", window_start_ms=1794924000000, window_end_ms=1794927600000, senders=6, transfers=6, total_minor=204000, contributing=["T011431", "T011465", "T011494", "T011536", "T011572", "T011610"] | supported |
| C-ind-20636 | indicator | indicator="fan_in:A-20636:1795190400000", account="A-20636", window_start_ms=1795190400000, window_end_ms=1795194000000, senders=6, transfers=6, total_minor=36000, contributing=["T033316", "T033368", "T033403", "T033439", "T033474", "T033495"] | supported |
| C-ind-28137 | indicator | indicator="fan_in:A-28137:1795003200000", account="A-28137", window_start_ms=1795003200000, window_end_ms=1795006800000, senders=7, transfers=7, total_minor=29500, contributing=["T018004", "T018035", "T018065", "T018090", "T018160", "T018198", "T018248"] | supported |
| C-ind-37573 | indicator | indicator="fan_in:A-37573:1794823200000", account="A-37573", window_start_ms=1794823200000, window_end_ms=1794826800000, senders=7, transfers=7, total_minor=379500, contributing=["T003057", "T003091", "T003124", "T003154", "T003248", "T003287", "T003319"] | supported |
| C-ind-83577 | indicator | indicator="fan_in:A-83577:1795057200000", account="A-83577", window_start_ms=1795057200000, window_end_ms=1795060800000, senders=8, transfers=8, total_minor=174500, contributing=["T022417", "T022437", "T022451", "T022478", "T022495", "T022519", "T022542", "T022561"] | supported |
| C-ind-85921 | indicator | indicator="fan_in:A-85921:1794855600000", account="A-85921", window_start_ms=1794855600000, window_end_ms=1794859200000, senders=6, transfers=6, total_minor=15000, contributing=["T005750", "T005789", "T005830", "T005868", "T005934", "T005978"] | supported |
| C-path-37573a | onward_path | transfers=["T003057", "T003168", "T003182", "T003201", "T003222"], from_indicator="fan_in:A-37573:1794823200000", comes_to_rest_at="A-54215" | supported |
| C-path-37573b | onward_path | transfers=["T003248", "T003391", "T003416", "T003433", "T003454"], from_indicator="fan_in:A-37573:1794823200000", comes_to_rest_at="A-54215" | supported |
| C-path-83577 | onward_path | transfers=["T022417", "T022572", "T022592", "T022609", "T022629", "T022649"], from_indicator="fan_in:A-83577:1795057200000", comes_to_rest_at="A-39382" | supported |
| C-path-10859a | onward_path | transfers=["T011431", "T011583", "T011600", "T011628"], from_indicator="fan_in:A-10859:1794924000000", comes_to_rest_at="A-92332" | supported |
| C-path-10859b | onward_path | transfers=["T011610", "T011670", "T011695"], from_indicator="fan_in:A-10859:1794924000000", comes_to_rest_at="A-85287" | supported |
| C-path-20636 | onward_path | transfers=["T033368", "T033506"], from_indicator="fan_in:A-20636:1795190400000", comes_to_rest_at="A-36729" | supported |
| C-path-85921 | onward_path | transfers=["T005750", "T005888"], from_indicator="fan_in:A-85921:1794855600000", comes_to_rest_at="A-10758" | supported |
| C-reach-37573 | onward_reach | indicator="fan_in:A-37573:1794823200000", max_depth=4, terminal_accounts=["A-54215"], route_accounts=["A-37573", "A-38045", "A-93288", "A-63022", "A-54215"] | supported |
| C-reach-83577 | onward_reach | indicator="fan_in:A-83577:1795057200000", max_depth=5, terminal_accounts=["A-39382"], route_accounts=["A-83577", "A-56768", "A-83094", "A-43725", "A-14799", "A-39382"] | supported |
| C-reach-10859 | onward_reach | indicator="fan_in:A-10859:1794924000000", max_depth=3, terminal_accounts=["A-92332", "A-85287"], route_accounts=["A-10859", "A-78340", "A-75793", "A-92332", "A-85287"] | supported |
| C-reach-20636 | onward_reach | indicator="fan_in:A-20636:1795190400000", max_depth=1, terminal_accounts=["A-36729"], route_accounts=["A-20636", "A-36729"] | supported |
| C-reach-85921 | onward_reach | indicator="fan_in:A-85921:1794855600000", max_depth=1, terminal_accounts=["A-10758"], route_accounts=["A-85921", "A-10758"] | supported |
| C-reach-28137 | onward_reach | indicator="fan_in:A-28137:1795003200000", max_depth=0, terminal_accounts=[], route_accounts=["A-28137"] | supported |
| C-dev-45880 | shared_device | device="D-45880", accounts=["A-37573", "A-38045", "A-93288", "A-63022"], on_route_of="fan_in:A-37573:1794823200000" | supported |
| C-dev-40018-route | shared_device | device="D-40018", accounts=["A-83094", "A-14799"], on_route_of="fan_in:A-83577:1795057200000" | supported |
| C-dev-40018-all | shared_device | device="D-40018", accounts=["A-83094", "A-14799", "A-34114"] | supported |
| C-dev-79802 | shared_device | device="D-79802", accounts=["A-10859", "A-78340"], on_route_of="fan_in:A-10859:1794924000000" | supported |
| C-dev-30793 | shared_device | device="D-30793", accounts=["A-36729", "A-69026"] | supported |
| C-abs-T033316 | absence | kind="no_onward_link_from_transfer", subject="T033316" | supported |
| C-abs-T005934 | absence | kind="no_onward_link_from_transfer", subject="T005934" | supported |
| C-abs-T005978 | absence | kind="no_onward_link_from_transfer", subject="T005978" | supported |
| C-abs-T018004 | absence | kind="no_onward_link_from_transfer", subject="T018004" | supported |
| C-abs-T018035 | absence | kind="no_onward_link_from_transfer", subject="T018035" | supported |
| C-abs-T018065 | absence | kind="no_onward_link_from_transfer", subject="T018065" | supported |
| C-abs-T018090 | absence | kind="no_onward_link_from_transfer", subject="T018090" | supported |
| C-abs-T018160 | absence | kind="no_onward_link_from_transfer", subject="T018160" | supported |
| C-abs-T018198 | absence | kind="no_onward_link_from_transfer", subject="T018198" | supported |
| C-abs-T018248 | absence | kind="no_onward_link_from_transfer", subject="T018248" | supported |
| C-abs-dev-20636 | absence | kind="no_shared_device_on_route", subject="fan_in:A-20636:1795190400000" | supported |
| C-abs-dev-85921 | absence | kind="no_shared_device_on_route", subject="fan_in:A-85921:1794855600000" | supported |
| C-abs-dev-28137 | absence | kind="no_shared_device_on_route", subject="fan_in:A-28137:1795003200000" | supported |
| C-abs-fan-54215 | absence | kind="no_fan_in_alert_for_account", subject="A-54215" | supported |
| C-abs-fan-39382 | absence | kind="no_fan_in_alert_for_account", subject="A-39382" | supported |
| C-abs-fan-92332 | absence | kind="no_fan_in_alert_for_account", subject="A-92332" | supported |
| C-abs-fan-85287 | absence | kind="no_fan_in_alert_for_account", subject="A-85287" | supported |
| C-abs-fan-36729 | absence | kind="no_fan_in_alert_for_account", subject="A-36729" | supported |
| C-abs-fan-10758 | absence | kind="no_fan_in_alert_for_account", subject="A-10758" | supported |
| C-cnt-alerts | count | pattern="fan_in_alerts", value=6 | supported |
| C-cnt-transfers | count | pattern="transfers", value=50000 | supported |
| C-cnt-links | count | pattern="onward_links", value=691 | supported |
| C-cnt-accounts | count | pattern="accounts", value=12072 | supported |
| C-cnt-devices | count | pattern="devices", value=12321 | supported |

## Score

Correctness 1.00 (19 of 19 required facts covered by supported claims); 56 of 56 claims supported; reference validity 1.0 (99 of 99 distinct ids resolve); 8 queries (0 failed), 5 model requests, 84165 input tokens (cache included) and 10840 output tokens, 133.2 s.
