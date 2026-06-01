# System design primer

> **One-line summary.** The vocabulary you need to read every other page in this repo without bouncing off.

## TL;DR

- Latency is *time per request*; throughput is *requests per unit time*. They trade off against each other.
- Availability and durability both come in "nines" but mean different things — availability is "is it up," durability is "did we lose your data."
- The CAP theorem forces a choice between consistency and availability during a network partition; PACELC tells you the latency-vs-consistency choice when there *isn't* a partition.
- Caches don't make a system faster — they make it slower most of the time and dramatically faster on the hot path. The whole game is keeping that hot path correct.
- Capacity estimates aren't supposed to be right. They're supposed to tell you which dimension blows up first.

## Latency and throughput

**Latency** is how long a single request takes, end to end. Usually measured as a distribution — p50 (median), p95, p99, p99.9. The tail matters: a service with a 10 ms p50 and a 2-second p99 will feel broken under load, because most pages need 20+ backend calls and the slowest one dominates user-visible latency. Always think percentiles, never averages.

**Throughput** is how many requests per second (RPS) you can serve. Throughput and latency are linked by **Little's Law**: `concurrent requests = throughput × latency`. If your service handles 100 RPS at 200 ms p99, you have ~20 in-flight requests at any moment — so you need at least 20 worker threads or async slots to sustain it.

You can almost always trade one for the other:

- Batching increases throughput at the cost of per-request latency.
- Sharding decreases per-shard latency at the cost of operational complexity.
- Adding a queue smooths bursts but adds a hop.

A useful rule: optimize for throughput at the system level, and for tail latency at the request level. The two failure modes are very different — running out of capacity (throughput) and an angry user staring at a spinner (latency).

## Availability and durability

Both are quoted in "nines":

| Nines | Annual downtime |
|---|---|
| 99% (two nines) | ~3.65 days |
| 99.9% | ~8.77 hours |
| 99.99% | ~52.6 minutes |
| 99.999% | ~5.26 minutes |
| 99.9999999% (eleven nines, S3) | ~30 ms over a year |

**Availability** is "is the service responding correctly?" You buy it with redundancy: multiple instances, multiple AZs, health checks, retries, failover. Each nine roughly 10× the cost of the previous one. Most systems don't need more than four; the four-to-five jump usually means going multi-Region.

**Durability** is "is the data still there?" You buy it with replication (across disks, across AZs, across Regions) and checksums. S3 quotes eleven nines of durability because objects are replicated and checksummed across at least three AZs; you'd lose roughly one object per 10,000 if you stored 10 million for 10,000 years.

A system can be highly durable but not highly available (Glacier — your data is safe, but retrieval takes hours) or highly available but not durable (an in-memory cache — fast to hit, but a reboot loses everything).

## Scaling

Two axes:

- **Vertical (scale up)** — bigger instance, more CPU/RAM/disk. Simple, no code changes, hits a ceiling (the biggest instance), and a single failure takes everything down.
- **Horizontal (scale out)** — more instances behind a load balancer. No ceiling, fault-tolerant, but forces you to deal with statelessness, session affinity, and consistency.

Almost every modern AWS-native design is horizontal. Vertical scaling is reasonable for a primary database before you shard it, or for a workload that fundamentally needs shared memory.

**Read scaling** is usually easier than write scaling because reads can be served from replicas or caches. Write scaling means sharding (partition the data by key) or eventual consistency (accept writes everywhere, reconcile later). Both are expensive — postpone them until the math says you have to.

## Caching

A cache is a *lookaside* (your code checks the cache, then the database) or *read-through/write-through* (the cache sits in front of the database). Either way, the contract is the same: trade strict consistency for latency and load reduction.

The three eternal questions:

1. **When do you populate it?** Lazy (on miss) is simplest; warm-loading or write-through is faster but adds coupling.
2. **When do you invalidate it?** TTL is the only invalidation strategy that's actually simple. Event-driven invalidation is correct but easy to get wrong; if you delete-on-write you'd better make sure the delete actually wins races against in-flight reads.
3. **What do you do on a miss-storm?** When the cache is cold (after a deploy, after an eviction), the database eats all the load at once. Mitigations: request coalescing (only one request per key goes to the DB), staggered TTLs (jitter), and warming during deploy.

The "cache stampede" problem is the single most common production caching incident. Solve it before you ship the cache.

## Consistency models

When you replicate data, you have to decide what "current" means.

- **Strong / linearizable** — every read returns the most recent write. Expensive: requires coordination (quorum, leader writes). DynamoDB strongly consistent reads, RDS reads from the primary, single-region Aurora.
- **Sequential / serializable** — operations appear in some total order that all clients agree on. Common for SQL transactions.
- **Causal** — if A happens before B, every observer sees A first. Looser than strong, useful for chat/feed apps.
- **Read-your-writes** — a client always sees its own writes (even if other clients see a stale version). Often implemented with sticky sessions.
- **Monotonic reads** — once you've seen version V, you'll never see anything older. Critical for UI sanity (no "the post disappeared, came back, disappeared again").
- **Eventual** — given enough time, all replicas converge. The fastest, the cheapest, the most common, and the one users hate when they hit it (the "I just posted that, where did it go" problem).

Most real systems mix models: strong for writes that update the canonical record, eventual for fan-out to read replicas, read-your-writes overlaid on top to hide the gap from the user.

## CAP and PACELC

**CAP** says: during a network partition, a distributed system can guarantee Consistency *or* Availability, not both. In practice no production system gets to choose "no partitions," so every distributed system has a stance: CP (refuse writes when partitioned — banking, leader election) or AP (accept writes everywhere, reconcile later — DNS, shopping carts).

**PACELC** extends this to the no-partition case: *Else, choose between Latency and Consistency.* DynamoDB is PA/EL — picks Availability during partitions, picks Latency the rest of the time (eventual reads are fast). Spanner-class systems are PC/EC — strong consistency always, at the cost of per-write latency.

If you can answer "what's our PACELC stance?" for every datastore in your design, you're 90% ahead of the room.

## Quorums

When you replicate to N nodes, set `W` (writes that must ack) and `R` (reads that must ack). If `W + R > N`, every read overlaps with the latest successful write, so reads see fresh data without a full lock.

- **N=3, W=2, R=2** — typical: tolerate one slow/down node, strong consistency.
- **N=3, W=3, R=1** — fast reads, every write must hit every node.
- **N=3, W=1, R=1** — fastest, weakest consistency. DynamoDB eventual reads are roughly this shape.

DynamoDB and Cassandra both expose this knob explicitly; RDS Multi-AZ hides it (synchronous replication to the standby).

## Backpressure and queueing

When upstream is faster than downstream, three things can happen: the downstream falls behind, the queue grows unboundedly, or upstream gets backpressure and slows down. The third is the only one that doesn't end in a 3 AM page.

In an AWS context that usually means: SQS or Kinesis sits between two services, the consumer scales on queue depth (or lag), and producers either tolerate temporary slowdown or get rejected with a 429. The shape to avoid is an unbounded in-process buffer that swallows OOMs silently.

**Queueing theory pop quiz:** as utilization approaches 100%, queue depth and latency go to infinity. The implication: target around 70–80% utilization on shared resources. The last 20% of capacity is what absorbs bursts; if you "save money" by removing it, your p99 latency explodes long before you notice anywhere else.

## Idempotency

If you can't safely retry, you can't build a reliable distributed system. Idempotency = "doing it twice has the same effect as doing it once."

Common implementations:

- **Idempotency key** — client generates a unique ID per logical operation; server stores `(key, result)` and replays the stored result on duplicate. Stripe-style.
- **Conditional writes** — `if-not-exists` puts, `expected-version` updates. DynamoDB conditional expressions, S3 object versioning + If-Match.
- **At-least-once + dedup** — queue delivers more than once on purpose; consumer tracks processed message IDs in a TTL'd store.

Every payment, every state transition, every webhook handler should be idempotent. Most outages are duplicate-processing bugs you didn't write down.

## Capacity estimation

The estimate isn't the point. The dimensions are.

A reasonable interview-style template:

1. **DAU** → **QPS** (`DAU × actions_per_day / 86400`, then multiply by 5–10 for peak).
2. **Storage per record** × records per day × retention → total bytes.
3. **Bandwidth** = QPS × payload size, in *and* out.
4. **Read/write ratio** — usually 10:1 or 100:1 for social apps, more like 1:1 for transactional systems.

Now sanity-check: does QPS exceed what a single primary database can serve (~10–20k QPS depending on workload)? If yes, you need replicas or sharding. Does storage exceed what a single host can hold (~10–100 TB)? If yes, sharding or object store. Does bandwidth exceed a single host's NIC (~10 Gbps practical)? If yes, multiple ingestion endpoints.

The estimate's job is to tell you which scaling story you're committing to in the rest of the design. Get the scaling story right; the exact numbers don't matter.

## Failure modes to think about explicitly

For every system, ask:

- **What does the failure of one instance look like?** (Should be invisible — that's why you have a load balancer.)
- **What does the failure of one AZ look like?** (Should degrade gracefully — that's why you run multi-AZ.)
- **What does the failure of one Region look like?** (Most systems silently say "we go down" — say it explicitly, then decide if that's OK.)
- **What does a poison-pill message look like?** (One bad payload shouldn't block the queue forever — that's why you have a DLQ.)
- **What does a thundering herd look like?** (After a cache flush, after a deploy, after a network blip clears.)
- **What does a cascading failure look like?** (Service A's slowdown ties up Service B's connection pool, which ties up Service C's…)

If a page in this repo doesn't address those questions for the system it describes, it's incomplete.

## Further reading

- [AWS mental model](aws-mental-model.md) — Regions, AZs, edge, IAM, the geography under everything.
- *Designing Data-Intensive Applications*, Martin Kleppmann — the canonical reference for replication, consistency, and partitioning.
- *Site Reliability Engineering*, Google — the SLO/SLI/SLA vocabulary.
- AWS Well-Architected Framework — six pillars covered under [`docs/05-well-architected/`](../05-well-architected/).
