# Amendment A1: evidence revision r1 to r2

This amends the investigation published at r1 (`r1-case-note.md`, sha256 0437d93ab98c...), which stays as it was written. A claim supported at r1 remains supported relative to r1; this records whether it still applies at r2.

Evidence revision r2, a bounded recomputation following r1: `data/events.ndjson` (55 transfers) and `arrivals/r2.ndjson` (1 transfer), 56 transfers in all, dataset sha256 e7dca2014eef..., through `pipeline/revision.sql`. clink exited 0 with 3 of 3 jobs completed; 56 of 56 records reconciled, and the derived indicators and onward links equal the independent reference.

Scope: bounded replays of a synthetic event file and what arrived after it, each conclusion relative to the evidence revision it names. Nothing here is a conclusion about data outside those revisions, and recorded relationships are not proof of fraud, ownership, identity or causation. An onward link records timing: a debit within 30 minutes after a credit to the same account. It is a candidate onward-transfer relationship, not evidence that the same funds moved, and a path ends where no further qualifying transfer exists in that revision. A shared device is context, not proof of ownership or fraud. The checker validates the structured claims against the original events and the graph of each revision; it does not validate the wording of findings.

## What arrived

| Transfer | From | To | Amount | Event time (UTC) | Device |
|---|---|---|---|---|---|
| T0056 | A-1415 | A-6630 | 130.00 | 15:01:00, 10 November 2026 | D-785 |

## Event time, and how the revision was made

- T0056 has event time 15:01:00. The last transfer revision r1's replay read, at 18:05:00, put the watermark at 18:00:00 (the pipeline allows 5 minutes). Appended to that stream, T0056 would be 2 h 59 min behind the watermark, far beyond that allowance, and T0041's 30-minute onward interval, which it falls in, ended at 15:20:00, also behind it. A transfer that late has no guarantee of being paired.
- r1's jobs have completed in any case: a bounded replay ends with its input, and its state with it, so nothing can be appended to it.
- So r2 is a bounded recomputation: clink replayed `data/events.ndjson` and every transfer that arrived since as two inputs and merged them by event time, so the arrival is judged by the same five-minute allowance as every other transfer.

## What changed in the evidence

- New onward link `onward:T0041:T0056`, derived by clink in r2: a candidate onward-transfer relationship, timing only.

## Claims selected for revalidation

- C6: T0056 is a debit from A-1415 inside 14:50:00-15:20:00, the 30 minutes after T0041
- C7: T0056 is a debit from A-1415 inside 14:50:00-15:20:00, C7's search scope
- Not selected: C1, C2, C3, C4, C5. Revalidating only the selected claims gave the same verdicts as checking all 7 again.

## F4, superseded at r2

As written at r1: From fan_in:A-9895:1794319200000 the candidate onward-transfer paths run at most 1 onward link and end at A-1415: in evidence revision r1 there is no qualifying onward transfer from A-1415 between 14:50:00 and 15:20:00, the 30 minutes after T0041 paid it (UTC, 10 November 2026).

| Claim | Asserts | At r1 | At r2 |
|---|---|---|---|
| C6 | fan_in:A-9895:1794319200000: at most 1 onward link, paths end at A-1415, path accounts A-1415, A-9895 | supported | unsupported: the longest chain is 2 onward link(s), not 1; terminal_accounts are ['A-6630'], not ['A-1415']; route_accounts are ['A-1415', 'A-6630', 'A-9895'], not ['A-1415', 'A-9895'] |
| C7 | no qualifying onward transfer from A-1415 between 14:50:00 and 15:20:00 UTC, 10 November 2026 (the 30 minutes after T0041 paid A-1415); searched: onward links into a debit sent by A-1415 inside the interval, both ends included, over revision r1 (55 transfers) | supported | unsupported: qualifying onward transfer(s) from A-1415: onward:T0041:T0056 (T0056 at 15:01:00) |

Replacement, **F5**, asserted at r2: From fan_in:A-9895:1794319200000 the candidate onward-transfer paths run at most 2 onward links and end at A-6630: in evidence revision r2 there is no qualifying onward transfer from A-6630 between 15:01:00 and 15:31:00, the 30 minutes after T0056 paid it (UTC, 10 November 2026). New in r2: onward:T0041:T0056, from T0041 (paid A-1415 at 14:50:00) to T0056 (A-1415 to A-6630, 130.00, at 15:01:00), 11 min apart; one candidate path through it runs T0038, T0041, T0056.

| Claim | Type | Asserts | At r2 |
|---|---|---|---|
| C8 | onward_reach | fan_in:A-9895:1794319200000: at most 2 onward links, paths end at A-6630, path accounts A-1415, A-6630, A-9895 | supported |
| C9 | no_onward_transfer | no qualifying onward transfer from A-6630 between 15:01:00 and 15:31:00 UTC, 10 November 2026 (the 30 minutes after T0056 paid A-6630); searched: onward links into a debit sent by A-6630 inside the interval, both ends included, over revision r2 (56 transfers) | supported |
| C10 | onward_path | path T0038 > T0041 > T0056 from fan_in:A-9895:1794319200000, ends at A-6630 | supported |
| C11 | event | T0056: A-1415 to A-6630, 130.00 at 15:01:00 UTC, device D-785 | supported |

## Unchanged at r2

- **F1** fan_in:A-9278:1794301200000: 6 distinct senders paid A-9278 3,570.00 in 6 transfers between 09:00:00 and 10:00:00 UTC on 10 November 2026, by event time, in evidence revision r1.  
  C1 supported at r2 (not selected, so carried; a full recheck agrees)
- **F2** From fan_in:A-9278:1794301200000 the candidate onward-transfer paths run at most 3 onward links and end at A-4989: in evidence revision r1 there is no qualifying onward transfer from A-4989 between 09:29:45 and 09:59:45, the 30 minutes after T0009 paid it; or from A-4989 between 10:08:10 and 10:38:10, the 30 minutes after T0016 paid it (UTC, 10 November 2026).  
  C2 supported at r2 (not selected, so carried; a full recheck agrees), C3 supported at r2 (not selected, so carried; a full recheck agrees), C4 supported at r2 (not selected, so carried; a full recheck agrees)
- **F3** fan_in:A-9895:1794319200000: 6 distinct senders paid A-9895 150.00 in 6 transfers between 14:00:00 and 15:00:00 UTC on 10 November 2026, by event time, in evidence revision r1.  
  C5 supported at r2 (not selected, so carried; a full recheck agrees)
