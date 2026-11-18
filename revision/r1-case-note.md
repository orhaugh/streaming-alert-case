# Case note, evidence revision r1

Evidence revision r1, the initial bounded replay: `data/events.ndjson` (55 transfers), dataset sha256 d6d8131b8934..., through `pipeline/revision.sql`. clink exited 0 with 3 of 3 jobs completed; 55 of 55 records reconciled, and the derived indicators and onward links equal the independent reference.

Written by `revise.py` from the evidence in Relate, with no model. Each claim was checked against the original events and the graph of this revision.

Scope: bounded replays of a synthetic event file and what arrived after it, each conclusion relative to the evidence revision it names. Nothing here is a conclusion about data outside those revisions, and recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in that revision. A shared device is context, not proof of ownership or fraud. The checker validates the structured claims against the original events and the graph of each revision; it does not validate the wording of findings.

## Findings

- **F1** fan_in:A-9278:1794301200000: 6 distinct senders paid A-9278 3,570.00 in 6 transfers between 09:00:00 and 10:00:00 UTC on 10 November 2026, by event time, in evidence revision r1.  
  Claims: C1 (supported at r1)
- **F2** From fan_in:A-9278:1794301200000 the candidate onward-transfer paths run at most 3 onward links and end at A-4989: in evidence revision r1 there is no qualifying onward transfer from A-4989 between 09:29:45 and 09:59:45, the 30 minutes after T0009 paid it; or from A-4989 between 10:08:10 and 10:38:10, the 30 minutes after T0016 paid it (UTC, 10 November 2026).  
  Claims: C2 (supported at r1), C3 (supported at r1), C4 (supported at r1)
- **F3** fan_in:A-9895:1794319200000: 6 distinct senders paid A-9895 150.00 in 6 transfers between 14:00:00 and 15:00:00 UTC on 10 November 2026, by event time, in evidence revision r1.  
  Claims: C5 (supported at r1)
- **F4** From fan_in:A-9895:1794319200000 the candidate onward-transfer paths run at most 1 onward link and end at A-1415: in evidence revision r1 there is no qualifying onward transfer from A-1415 between 14:50:00 and 15:20:00, the 30 minutes after T0041 paid it (UTC, 10 November 2026).  
  Claims: C6 (supported at r1), C7 (supported at r1)

## Claims, as checked at r1

| Claim | Type | Asserts | Depends on | Checker |
|---|---|---|---|---|
| C1 | indicator | fan_in:A-9278:1794301200000: 6 senders, 6 transfers, total 3,570.00, contributing T0002, T0003, T0006, T0010, T0011, T0012 | credits to A-9278 09:00:00-10:00:00 | supported |
| C2 | onward_reach | fan_in:A-9278:1794301200000: at most 3 onward links, paths end at A-4989, path accounts A-2897, A-4989, A-5092, A-9278 | credits to A-9278 09:00:00-10:00:00; debits from A-9278 09:05:10-09:35:10; debits from A-9278 09:10:40-09:40:40; debits from A-9278 09:18:05-09:48:05; debits from A-5092 09:24:00-09:54:00; debits from A-2897 09:26:30-09:56:30; debits from A-4989 09:29:45-09:59:45; debits from A-9278 09:37:30-10:07:30; debits from A-9278 09:44:15-10:14:15; debits from A-9278 09:58:40-10:28:40; debits from A-5092 10:03:20-10:33:20; debits from A-2897 10:05:50-10:35:50; debits from A-4989 10:08:10-10:38:10 | supported |
| C3 | no_onward_transfer | no qualifying onward transfer from A-4989 between 09:29:45 and 09:59:45 UTC, 10 November 2026 (the 30 minutes after T0009 paid A-4989); searched: onward links into a debit sent by A-4989 inside the interval, both ends included, over revision r1 (55 transfers) | credits to A-4989 08:59:45-09:59:45; debits from A-4989 09:29:45-09:59:45 | supported |
| C4 | no_onward_transfer | no qualifying onward transfer from A-4989 between 10:08:10 and 10:38:10 UTC, 10 November 2026 (the 30 minutes after T0016 paid A-4989); searched: onward links into a debit sent by A-4989 inside the interval, both ends included, over revision r1 (55 transfers) | credits to A-4989 09:38:10-10:38:10; debits from A-4989 10:08:10-10:38:10 | supported |
| C5 | indicator | fan_in:A-9895:1794319200000: 6 senders, 6 transfers, total 150.00, contributing T0035, T0036, T0037, T0038, T0039, T0040 | credits to A-9895 14:00:00-15:00:00 | supported |
| C6 | onward_reach | fan_in:A-9895:1794319200000: at most 1 onward link, paths end at A-1415, path accounts A-1415, A-9895 | credits to A-9895 14:00:00-15:00:00; debits from A-9895 14:02:20-14:32:20; debits from A-9895 14:09:05-14:39:05; debits from A-9895 14:15:40-14:45:40; debits from A-9895 14:22:10-14:52:10; debits from A-9895 14:30:30-15:00:30; debits from A-9895 14:41:00-15:11:00; debits from A-1415 14:50:00-15:20:00 | supported |
| C7 | no_onward_transfer | no qualifying onward transfer from A-1415 between 14:50:00 and 15:20:00 UTC, 10 November 2026 (the 30 minutes after T0041 paid A-1415); searched: onward links into a debit sent by A-1415 inside the interval, both ends included, over revision r1 (55 transfers) | credits to A-1415 14:20:00-15:20:00; debits from A-1415 14:50:00-15:20:00 | supported |
