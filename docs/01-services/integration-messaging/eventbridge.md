# EventBridge

> **One-line summary.** Serverless event bus. Producers send events; **rules** match them by JSON pattern and route to one or more AWS services (Lambda, Step Functions, SQS, SNS, ECS, Kinesis, API destinations, …) or another bus.

## TL;DR
- The right answer for **event-bus routing** when you have many producers, many consumers, and complex content-based rules. Think "Kafka without partitions; routing without writing code."
- Three bus types: **default bus** (AWS service events automatically; one per account per Region), **custom buses** (yours, for your own events), and **partner event buses** (third-party SaaS — Datadog, Auth0, MongoDB, etc. — publish directly).
- Companion services: **EventBridge Pipes** (point-to-point with filter+enrich, see [`pipes.md`](pipes.md)), **EventBridge Scheduler** (cron-style scheduled invocations at massive scale, replacing CloudWatch Events Rules).
- **Schema Registry** discovers event schemas automatically from the bus and generates SDK code bindings.
- Pairs naturally with **Step Functions** (target for orchestration), **Lambda** (target for arbitrary handlers), **SQS** (target for buffering before processing).

## When to use it
- Many-to-many event distribution with content-based routing.
- Reacting to AWS service events (EC2 state changes, CodePipeline events, GuardDuty findings, etc.).
- SaaS event integration without writing webhook handlers (via partner event buses).
- Scheduled / cron-style invocations at scale (use **EventBridge Scheduler**).
- Cross-account / cross-Region event delivery.
- Replacing per-target Lambda wrappers with declarative routing.

## When NOT to use it
- High-throughput, ordered, replayable event streams — use **Kinesis Data Streams** or **MSK** (Kafka).
- Single producer, single consumer with simple buffering — use **SQS** directly.
- Pure fanout to known consumers — **SNS** is simpler.
- Workflow orchestration with state — **Step Functions**.

## Key concepts

**Event bus.** Logical container for events.
- **Default bus** — AWS service events for the account/Region land here automatically (CloudTrail events, service-emitted notifications).
- **Custom bus** — yours; PutEvents from any source.
- **Partner bus** — SaaS-published events.

**Event.** JSON with structured fields. Standard envelope: `source`, `detail-type`, `detail`, `time`, `region`, `account`.

**Rule.** Pattern + targets. Pattern matches on event content (fields, prefixes, IP ranges, anything-but, numeric ranges, exists). Up to 5 targets per rule.

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped", "terminated"]
  }
}
```

**Targets.** Lambda, Step Functions, SQS, SNS, Kinesis (Streams + Firehose), ECS task, API Gateway, API destinations (arbitrary HTTPS endpoint with managed auth), another event bus, EventBridge Pipes, CloudWatch Logs, AWS Glue, SageMaker, and many more.

**Input transformation.** Reshape the event before sending to the target (extract specific fields, build a custom JSON template).

**API destinations.** Send events to any HTTP endpoint outside AWS, with managed connection credentials (basic auth, API key, OAuth). Replaces custom Lambda integration glue.

**Schema Registry.** Discovers schemas from events on the bus; auto-generates code bindings (Java, Python, TypeScript) for producers and consumers.

**Archive + Replay.** Archive events from a bus and replay them back later — for debugging or recovering from a bad target deployment.

**EventBridge Scheduler.** Separate service for scheduled invocations. Replaces older CloudWatch Events Rules cron / rate expressions with:
- Higher quotas (millions of schedules per account).
- Per-schedule throttling.
- Built-in retries and DLQ.
- One-time schedules (not just recurring).
- Direct integration with hundreds of AWS service APIs.

**Cross-Region / cross-account.** A rule on bus A can target a bus in another account or Region. Standard pattern for centralized event collection.

**EventBridge Pipes.** Point-to-point integrations between source and target with optional filter + enrich steps. See [`pipes.md`](pipes.md). Different from EventBridge Rules — Pipes is single-source-single-target with rich middle steps; Rules is bus-fanout with simple targets.

## Pricing model

- **Custom events published** — per million events to a bus.
- **Cross-account / cross-Region events** — additional per million.
- **AWS service events on the default bus** — free.
- **EventBridge Pipes** — per million events processed; enrichment Lambda invocations billed separately.
- **EventBridge Scheduler** — per million invocations.
- **Schema Registry** — free for AWS-discovered schemas; custom schemas count toward quota.
- **Archive / Replay** — per GB archived + per GB replayed.

## Quotas & limits

- **Buses per account per Region**: 100.
- **Rules per bus**: 300 default (raisable).
- **Targets per rule**: 5.
- **PutEvents throughput**: 10,000 events/sec per account per Region default (raisable).
- **Event size**: 256 KB.
- **Scheduler schedules per account**: 1 million (default), raisable into the tens of millions.

## Common pitfalls

- **EventBridge for stream-style workloads.** Not the right fit; use Kinesis or MSK for ordered, partitioned, replayable streams.
- **Too many targets on one rule.** Cap is 5. Fan to SNS / another bus if you need more.
- **No DLQ on critical rules.** Failed target invocations vanish silently. Configure DLQ on each rule target.
- **Hand-coding cron in Lambda for scheduled work.** Use EventBridge Scheduler — managed retries, DLQ, and pricing is better at scale than running a CloudWatch Events rule with a Lambda target.
- **Mixing event-bus routing (EventBridge Rules) with point-to-point ingest (Pipes).** They're different products; use Pipes when you have one source + one target with filter/enrich.
- **Schema Registry ignored.** When event schemas drift, consumers break opaquely. The registry catches drift early.
- **No archive on important buses.** When a consumer is broken, you can't replay. Archive critical events.
- **Cross-account event posting without IAM + bus policy.** Both ends must allow.

## Pairs well with
- [SNS](sns.md), [SQS](sqs.md), [Lambda](../compute/lambda.md), [Step Functions](step-functions.md) — common targets.
- [EventBridge Pipes](pipes.md) — single-source single-target with filter+enrich.
- **API destinations** — send events to external HTTP endpoints.
- **Kinesis Data Firehose** — stream events to S3 / Redshift / OpenSearch.
- **CloudTrail** — AWS API events flow naturally to the default bus.

## Pairs well with these repo pages
- [Pipes](pipes.md), [Step Functions](step-functions.md), [SNS](sns.md), [SQS](sqs.md).
- `docs/02-patterns/pub-sub.md`, `docs/02-patterns/event-sourcing.md` (forthcoming).

## Further reading
- [Amazon EventBridge documentation](https://docs.aws.amazon.com/eventbridge/).
- [EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html).
- [EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/).
- [Event patterns reference](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html).
- [Schema Registry](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema-registry.html).
