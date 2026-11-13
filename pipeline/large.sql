-- The large case: the same three clink jobs over the 50,000-transfer file, each writing straight
-- into one Relate store through connector='relate'. No program sits between
-- the engine and the graph.
--
-- Run from the repository root with a clink that carries the Relate connector
-- (rebuild.sh runs it from the runtime image):
--
--   clink run pipeline/large.sql
--
-- Each sink's statement finds its nodes by a stable id under a uniqueness
-- constraint and MERGEs everything it writes. The three jobs write one store
-- at the same time and in no fixed order (an indicator can arrive before the
-- transfers it points at), and a batch can be replayed: either way the graph
-- comes out the same.

CREATE TABLE transfers (
    transfer_id  VARCHAR,
    src          VARCHAR,
    dst          VARCHAR,
    amount_minor BIGINT,
    ts           BIGINT,
    device       VARCHAR
) WITH (
    connector         = 'file',
    format            = 'json',
    path              = 'data/large/events.ndjson',
    event_time_column = 'ts',
    watermark_lag_ms  = '300000',
    batch_size        = '1',
    on_decode_error   = 'fail'
);

-- 1. Every transfer, with its sender, receiver and device.
CREATE TABLE graph_transfers (
    transfer_id  VARCHAR,
    src          VARCHAR,
    dst          VARCHAR,
    amount_minor BIGINT,
    ts           BIGINT,
    device       VARCHAR
) WITH (
    connector = 'relate',
    path      = 'store/large.building.rl',
    schema    = 'CREATE CONSTRAINT account_id IF NOT EXISTS FOR (n:Account) REQUIRE n.id IS UNIQUE;
                 CREATE CONSTRAINT device_id IF NOT EXISTS FOR (n:Device) REQUIRE n.id IS UNIQUE;
                 CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (n:Transfer) REQUIRE n.id IS UNIQUE',
    statement = 'UNWIND $rows AS row
                 MERGE (s:Account {id: row.src})
                 MERGE (d:Account {id: row.dst})
                 MERGE (v:Device {id: row.device})
                 MERGE (t:Transfer {id: row.transfer_id})
                 SET t.ts = row.ts, t.amount_minor = row.amount_minor
                 MERGE (s)-[:SENT]->(t)
                 MERGE (t)-[:TO]->(d)
                 MERGE (t)-[:FROM_DEVICE]->(v)'
);

INSERT INTO graph_transfers
SELECT transfer_id, src, dst, amount_minor, ts, device
FROM transfers;

-- 2. Fan-in: at least five distinct senders into one account inside a
--    one-hour event-time window, linked to the transfers that make it up.
CREATE TABLE graph_fan_in (
    indicator_id VARCHAR,
    account      VARCHAR,
    window_start BIGINT,
    window_end   BIGINT,
    senders      BIGINT,
    transfers    BIGINT,
    total_minor  BIGINT,
    transfer_ids VARCHAR
) WITH (
    connector = 'relate',
    path      = 'store/large.building.rl',
    schema    = 'CREATE CONSTRAINT account_id IF NOT EXISTS FOR (n:Account) REQUIRE n.id IS UNIQUE;
                 CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (n:Transfer) REQUIRE n.id IS UNIQUE;
                 CREATE CONSTRAINT indicator_id IF NOT EXISTS FOR (n:Indicator) REQUIRE n.id IS UNIQUE',
    statement = 'UNWIND $rows AS row
                 MERGE (a:Account {id: row.account})
                 MERGE (i:Indicator {id: row.indicator_id})
                 SET i.kind = "fan_in", i.window_start = row.window_start,
                     i.window_end = row.window_end, i.senders = row.senders,
                     i.transfers = row.transfers, i.total_minor = row.total_minor
                 MERGE (i)-[:ABOUT]->(a)
                 WITH i, row
                 UNWIND split(row.transfer_ids, ",") AS tid
                 MERGE (t:Transfer {id: tid})
                 MERGE (i)-[:CONTRIBUTING]->(t)'
);

INSERT INTO graph_fan_in
SELECT 'fan_in:' || dst || ':' || CAST(window_start AS VARCHAR) AS indicator_id,
       dst AS account,
       window_start,
       window_end,
       COUNT(DISTINCT src) AS senders,
       COUNT(*) AS transfers,
       SUM(amount_minor) AS total_minor,
       STRING_AGG(transfer_id, ',') AS transfer_ids
FROM transfers
GROUP BY dst, TUMBLE(ts, INTERVAL '1' HOUR)
HAVING COUNT(DISTINCT src) >= 5;

-- 3. Onward transfer: a credit to an account and a debit from that account
--    no more than 30 minutes later, by event time. This is the relationship
--    the investigation follows.
CREATE TABLE graph_onward (
    in_id  VARCHAR,
    out_id VARCHAR,
    in_ts  BIGINT,
    out_ts BIGINT
) WITH (
    connector = 'relate',
    path      = 'store/large.building.rl',
    schema    = 'CREATE CONSTRAINT transfer_id IF NOT EXISTS FOR (n:Transfer) REQUIRE n.id IS UNIQUE',
    statement = 'UNWIND $rows AS row
                 MERGE (c:Transfer {id: row.in_id})
                 MERGE (d:Transfer {id: row.out_id})
                 MERGE (c)-[p:PASSED_ON]->(d)
                 SET p.id = "onward:" + row.in_id + ":" + row.out_id,
                     p.gap_ms = row.out_ts - row.in_ts'
);

INSERT INTO graph_onward
SELECT c.transfer_id AS in_id,
       d.transfer_id AS out_id,
       c.ts AS in_ts,
       d.ts AS out_ts
FROM transfers d
JOIN transfers c
  ON d.src = c.dst
 AND d.ts BETWEEN c.ts + INTERVAL '0' SECOND AND c.ts + INTERVAL '30' MINUTE;
