# SQS (Simple Queue Service)

> **One-line summary.** Fully managed message queue. Decouples producers from consumers; absorbs traffic bursts; provides at-least-once (Standard) or exactly-once / strict-order (FIFO) delivery.

## TL;DR
- The default messaging primitive on AWS. Every event-driven system uses SQS somewhere.
- Two queue types: **Standard** (very high throughput, at-least-once delivery, best-effort ordering) and **FIFO** (300 messages/sec by default per group, exactly-once, strict order).
- **Visibility timeout** is the most-misconfigured setting — make it longer than your worker's processing time + safety margin; otherwise messages re-deliver and you double-process.
- **Dead-letter queues (DLQs)** are mandatory for production. Poison-pill messages will eventually appear; without a DLQ they retry forever.
- Pair with **SNS** (fanout) or **EventBridge Pipes** (filter+enrich) for event distribution; pair with **Lambda** (event source mapping) or **ECS / EC2** for consumption.

## When to use it
- Decouple any two services where one can run faster or slower than the other.
- Absorb traffic bursts so downstream services don't have to scale instantly.
- Async work — order processing, image / video transcoding, ML inference jobs.
- Background notifications and retries.
- Dead-letter handling for failed messages from SNS / Step Functions / Lambda async.

## When NOT to use it
- Strict pub/sub fanout to multiple consumers — use **SNS** (or SNS → multiple SQS queues).
- Event-bus routing with content-based rules to many AWS service targets — use **EventBridge**.
- Streaming, time-ordered, replayable event logs — use **Kinesis Data Streams** or **MSK** (Kafka).
- Workflow orchestration with state and conditionals — use **Step Functions**.

## Key concepts

**Queue types:**
- **Standard** — at-least-once, best-effort ordering, very high throughput (thousands per second per queue, more via partitioning).
- **FIFO** — exactly-once delivery, strict per-`MessageGroupId` ordering. Default throughput 300 messages/sec per group, raisable to 3,000+ with high-throughput mode.

**Visibility timeout.** When a consumer receives a message, it becomes invisible to other consumers for the visibility-timeout window. If the consumer doesn't delete the message within that window, the message reappears for re-delivery. Set this *longer* than your processing time + safety; otherwise duplicates.

**Long polling.** `WaitTimeSeconds` up to 20s on `ReceiveMessage` — the SQS server holds the call open until messages arrive or the timeout expires. Reduces empty-poll cost dramatically.

**Dead-letter queue (DLQ).** A separate queue for messages that have been received but never successfully deleted after N retries. The standard pattern: a Standard or FIFO queue with `RedrivePolicy → DLQ`. The DLQ is the canonical "broken message" alarm point.

**Redrive (DLQ replay).** Move messages from DLQ back to the source queue for re-processing after the underlying bug is fixed.

**Message attributes.** Up to 10 key-value pairs of metadata. Filterable on the consumer side (but unlike SNS, SQS itself doesn't filter — filtering is the consumer's job).

**Encryption.** KMS server-side encryption at rest (default `aws/sqs` key or CMK).

**Cross-account / cross-Region.** Queues support cross-account access via queue policy + IAM. Cross-Region is via app-level replication or via SNS / EventBridge.

**Lambda event source mapping.** Built-in poller pulls from SQS and invokes Lambda. Batch size up to 10 (Standard, 10,000 with batching window) or 10,000 (FIFO). Scales Lambda concurrency with queue depth.

**FIFO specifics.**
- **`MessageGroupId`** orders messages within the group (parallel groups process in parallel).
- **`MessageDeduplicationId`** dedupes over 5 minutes.
- **High-throughput FIFO** — per-MessageGroupId throughput, not per-queue.

## Pricing model

- **Per million API requests** — `SendMessage`, `ReceiveMessage`, `DeleteMessage`, `ChangeMessageVisibility`, etc. Standard and FIFO have different rates (FIFO is more expensive).
- **Data transfer** — same AWS rules.
- **Long polling** reduces the empty-poll API call count, so it actively saves money at scale.
- **Server-side encryption** with the default key is free; CMK incurs KMS calls.

## Quotas & limits

- **Queues per account per Region**: 1 million.
- **Message size**: 256 KB (extended payload via S3 + the Extended Client library up to 2 GB).
- **Message retention**: 60 seconds to 14 days (default 4 days).
- **Visibility timeout**: up to 12 hours.
- **Throughput (Standard)**: very high, effectively unlimited via partitioning.
- **Throughput (FIFO)**: 300 messages/sec per MessageGroupId default; 3,000+ in high-throughput mode.
- **Batch size**: 10 for `SendMessageBatch` / `DeleteMessageBatch` / `ReceiveMessage`.

## Common pitfalls

- **Visibility timeout too short.** Worker takes 60s, visibility 30s → message re-delivered while worker is still processing → double-processing. Set visibility ≥ max processing time × safety factor; extend with `ChangeMessageVisibility` if the worker needs longer.
- **No DLQ.** Eventually a bad message will fail forever. Always set `maxReceiveCount` and route to a DLQ.
- **No CloudWatch alarm on DLQ depth.** A growing DLQ that nobody sees is a silent outage.
- **Short polling in production.** Empty polls = API requests = cost without value. Enable long polling.
- **Lambda concurrency unbounded against a queue.** Lambda scales Lambdas faster than the downstream can handle; downstream collapses. Set `MaximumConcurrency` on the event source mapping.
- **FIFO with one MessageGroupId for everything.** Serializes all processing. Choose group IDs that match the actual ordering requirement.
- **Idempotency assumed but not implemented.** Standard queues guarantee at-least-once — consumers MUST be idempotent. FIFO guarantees exactly-once within the dedup window only, not across windows.
- **Cross-account access via IAM only.** Queue policy is also required for cross-account. Easy to miss.
- **Large payloads inline.** > 256 KB doesn't fit. Use Extended Client (transparent S3-offload) or send a reference and have the consumer fetch the body.

## Pairs well with
- [SNS](sns.md) — SNS → SQS fanout is the canonical event distribution pattern.
- [EventBridge Pipes](pipes.md) — filter and enrich SQS messages before delivering.
- [Lambda](../compute/lambda.md) — event source mapping for serverless consumers.
- [Step Functions](step-functions.md) — orchestrate flows that pull from SQS.
- [DynamoDB Streams](../database/dynamodb.md), [Kinesis Data Streams](../analytics/) (forthcoming) — alternative event sources.

## Pairs well with these repo pages
- [SNS](sns.md), [Lambda](../compute/lambda.md), [Step Functions](step-functions.md).
- `docs/02-patterns/idempotency.md` (forthcoming).

## Further reading
- [Amazon SQS documentation](https://docs.aws.amazon.com/sqs/).
- [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html).
- [SQS DLQs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html).
- [FIFO queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html).
- ["Avoiding insurmountable queue backlogs", Amazon Builders' Library](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/).
