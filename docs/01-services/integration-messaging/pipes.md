# EventBridge Pipes

> **One-line summary.** Managed point-to-point integrations between an event source and a target, with optional **filter** and **enrichment** stages in between. Replaces hand-written Lambda glue for "consume from X, transform, send to Y."

## TL;DR

- Four stages: **Source → Filter → Enrichment → Target.** Source and Target are required; Filter and Enrichment optional.
- Sources include **SQS, DynamoDB Streams, Kinesis Data Streams, MSK / self-managed Kafka, MQ.** Targets include almost any AWS service (Lambda, Step Functions, SNS, SQS, ECS, Kinesis, HTTPS API destinations, …).
- **Filter** uses JSON pattern matching to drop events you don't want — saves enrichment/target cost.
- **Enrichment** can call Lambda, Step Functions, API Gateway / API destination synchronously to augment the event before delivery.
- Maintains source ordering through the pipeline when the source guarantees it. Different from EventBridge **Rules** (which is bus-fanout with simple targets) — Pipes is single-source-to-single-target with filter+enrich.

## When to use it

- You'd otherwise write a Lambda function that polls SQS / DynamoDB Streams / Kinesis and forwards to another service.
- Need cross-service piping with content-based filtering (drop messages that don't match `event_type = X`).
- Need to enrich events with extra data from a lookup (call an API, query DynamoDB) before sending to the target.
- DynamoDB Streams → Step Functions / Kinesis / Lambda without writing the polling+invocation code.
- Kafka / MSK → Lambda / Step Functions with managed offset and DLQ handling.

## When NOT to use it

- Pure pub/sub fanout to many subscribers — use **EventBridge bus** (custom bus + rules + multiple targets).
- Single-producer single-Lambda direct event-source-mapping is fine and simpler — no need for Pipes if you don't need filter/enrich.
- Stateful orchestration across many steps — that's **Step Functions**.

## Key concepts

### Pipe stages

1. **Source.** Polls the source for new events.
2. **Filter (optional).** JSON pattern; events that don't match are dropped (and you don't pay for enrichment / target on them).
3. **Enrichment (optional).** Synchronously invokes a Lambda / Step Function / API destination / API Gateway with the filtered event; the response replaces the event for the target stage.
4. **Target.** Sends to a destination.

### Sources

- **Amazon SQS** (Standard and FIFO).
- **DynamoDB Streams.**
- **Kinesis Data Streams.**
- **Amazon MSK** (managed Kafka).
- **Self-managed Kafka.**
- **Amazon MQ** (ActiveMQ, RabbitMQ).

### Targets

Almost any AWS service: Lambda, Step Functions (Standard or Express), SNS, SQS, EventBridge bus, Kinesis Streams, Kinesis Firehose, ECS task, Batch job, API Gateway (REST or HTTP), API destinations (arbitrary HTTPS), CloudWatch Logs, SageMaker pipeline, EventBridge Pipes (chaining), and more.

### Filtering

JSON pattern matching, same syntax as EventBridge rules. Filters apply to the event payload from the source. Events that don't match are dropped — and Pipes doesn't charge for them downstream.

### Enrichment

The enrichment step is **synchronous**. The pipe invokes the enrichment Lambda / Step Functions / API and waits for a response that becomes the event handed to the target. Use cases:

- Look up additional data (the source message has only an ID; enrichment fetches the full record).
- Reshape the payload into the target's expected format.
- Apply business logic that's too complex for a JSON pattern.

### Ordering

If the source guarantees ordering (FIFO SQS, single-shard Kinesis, per-key DynamoDB stream), Pipes preserves that order end-to-end.

### Batching

Per-source batching is supported (e.g., SQS messages batched into one Lambda invocation). Configure batch size and window.

### Error handling

Failed invocations follow source-type semantics (SQS visibility timeout reappearance, Kinesis retry-on-error). DLQ supported for unrecoverable failures.

## Pricing model

- **Per million events processed** through the pipe.
- **Enrichment Lambda invocations / API destination calls** billed separately at the underlying service rate.
- **Source / target service costs** (SQS reads, target Lambda invocations, etc.) are still your bill.

The "filter early to save downstream cost" pattern is the key economic lever — drop unwanted events before enrichment / target invocation.

## Quotas & limits

- **Pipes per account per Region**: 1,000 default (raisable).
- **Event size**: 256 KB (source-dependent).
- **Batch size**: up to 10 per invocation (source-dependent).
- **Enrichment timeout**: synchronous, bounded by target service limits.
- **Filter pattern complexity**: same as EventBridge rules.

## Common pitfalls

- **Hand-rolled Lambda pollers when Pipes would do.** A poll-SQS-and-forward Lambda is the canonical case Pipes was built to replace.
- **Filtering at the target instead of the pipe.** Filter at the pipe — you don't pay for enrichment / target invocations on dropped events.
- **Enrichment Lambda timeouts.** The pipe waits synchronously; long enrichment latency blocks the pipeline. Keep enrichment fast.
- **No DLQ on the source's failure path.** Failed events disappear into source semantics; configure DLQ.
- **Using Pipes for fanout.** Pipes is one source → one target. For fanout, send to an EventBridge bus and use rules to fan out.
- **Pipes between two AWS-native services when EventBridge Rules would do.** If the source is "AWS service event" and the target is "AWS service," EventBridge bus + rule is usually cleaner.
- **Forgetting that Pipes preserves source ordering.** If the source is FIFO and the target needs to handle in-order, the rest of the pipeline (especially batching) must not reorder.

## Pairs well with

- [SQS](sqs.md), [DynamoDB](../database/dynamodb.md) (Streams), [Kinesis](../analytics/) (forthcoming), [MSK / Kafka](../analytics/) (forthcoming), [MQ](mq.md) — source services.
- [Lambda](../compute/lambda.md), [Step Functions](step-functions.md), [SNS](sns.md), [SQS](sqs.md), [EventBridge](eventbridge.md) — common targets.
- **API destinations** — for HTTPS targets outside AWS.

## Pairs well with these repo pages

- [EventBridge](eventbridge.md), [Step Functions](step-functions.md), [Lambda](../compute/lambda.md).
- [SQS](sqs.md), [DynamoDB](../database/dynamodb.md).

## Further reading

- [Amazon EventBridge Pipes documentation](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html).
- [Pipes concepts](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-concepts.html).
- [Pipes sources](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-source.html).
- [Pipes targets](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-event-target.html).
- [Event enrichment](https://docs.aws.amazon.com/eventbridge/latest/userguide/pipes-enrichment.html).
