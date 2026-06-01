# SNS (Simple Notification Service)

> **One-line summary.** Fully managed pub/sub messaging — fan-out one message to many subscribers (SQS queues, Lambda, HTTP endpoints, email, SMS, mobile push, Kinesis Data Firehose).

## TL;DR

- The "fanout" primitive on AWS. Publishers send messages to a **topic**; subscribers (zero, one, or many) get a copy. Default delivery is one-to-many at-least-once.
- Two topic types: **Standard** (high throughput, best-effort ordering, at-least-once) and **FIFO** (strict ordering and exactly-once delivery within a message group, lower throughput).
- **Message filtering** lets each subscriber receive only the messages matching a JSON filter policy — replaces N topics with one + per-subscriber filters.
- For point-to-point queueing, use **SQS** directly. For event-bus routing with content-based rules + many AWS-service targets, use **EventBridge**. SNS is best at "topic-style fanout to a known set of consumers."
- Pairs naturally with **SQS** (the "SNS-to-SQS-to-consumer" pattern is the canonical AWS fanout architecture) — SNS for fanout, SQS for buffering / decoupling each consumer.

## When to use it

- Fan-out a single event to multiple SQS queues, Lambda functions, or HTTP endpoints.
- Mobile push notifications (iOS APNs, Android FCM, Amazon Device Messaging).
- SMS / email alerts (e.g., CloudWatch alarm notifications).
- Cross-account / cross-Region fanout.
- Delivering events to Kinesis Data Firehose for streaming pipelines.

## When NOT to use it

- Point-to-point queueing — use **SQS** directly.
- Event-bus routing with complex rule patterns and many AWS service targets — **EventBridge** is purpose-built for that.
- Long-lived persistent storage — SNS has retention windows (in the tens of seconds for stored undelivered messages); use SQS / DynamoDB Streams for durable buffering.
- Workflows with state — use **Step Functions**.

## Key concepts

**Topic.** Named entity that publishers publish to and subscribers subscribe to. Standard or FIFO.

**Subscription.** Per-subscriber binding to a topic. Subscriber types:

- **SQS queue.**
- **Lambda function.**
- **HTTP / HTTPS endpoint.**
- **Email / email-JSON / SMS.**
- **Mobile push** (APNs, FCM, ADM).
- **Kinesis Data Firehose** (for streaming into S3 / Redshift / OpenSearch).
- **Cross-account / cross-Region** subscriptions allowed with appropriate policies.

**Message attributes.** Key-value metadata attached to a message. Used by **message filtering** so each subscriber can express a JSON filter policy ("only deliver messages where `event_type = order_paid`").

**FIFO topics.** Guarantee per-`MessageGroupId` ordering and deduplication via `MessageDeduplicationId`. Throughput is significantly lower than Standard (3,000 messages/sec per topic by default, raisable). FIFO topics can only fan out to FIFO SQS queues.

**Message Data Protection.** Inspect and redact PII in messages on the publish side (optional add-on for sensitive data).

**Server-side encryption.** KMS-encrypted at rest (default `aws/sns` key or CMK).

**Dead-letter queues.** Per-subscription DLQ (an SQS queue) catches messages that fail delivery after retries.

**Delivery retries.** Customizable retry policies for HTTP/HTTPS subscriptions (other types use AWS-managed retries).

**FIFO ordering & deduplication.** FIFO topics dedupe by `MessageDeduplicationId` over a 5-minute window; the same ID within the window collapses to one delivered message.

## Pricing model

- **Per million publishes** to Standard topics; FIFO has a higher rate.
- **Per million deliveries** by subscription type. SMS / mobile push / HTTP cost more than SQS / Lambda / Firehose.
- **Data transfer** for outbound HTTP / SMS.
- **Message Data Protection** is an add-on per million scanned.

SQS-subscribed deliveries are inexpensive; SMS deliveries are the line item that surprises teams (rate per message varies by destination country).

## Quotas & limits

- **Topics per account per Region**: 100,000.
- **Subscriptions per topic**: 12.5 million.
- **Message size**: 256 KB (256 KB extended payload via SNS Extended Client library + S3 for the body).
- **Throughput (Standard)**: very high; soft limits raisable.
- **Throughput (FIFO)**: 3,000 messages/sec per topic default.
- **Filter policy size**: 256 KB max per subscription.
- **Filter policy complexity**: 100 filter values per attribute name.

## Common pitfalls

- **One topic per consumer.** Use one topic + per-subscription filtering instead.
- **No DLQ.** Failed deliveries vanish into retries and eventually silently drop. Always wire a DLQ.
- **HTTP subscriber that returns 200 too fast.** Subscriber must process before returning 200; otherwise message is acknowledged but unprocessed. Better: SNS → SQS → consumer.
- **FIFO topic with too many MessageGroupIds and a few hot groups.** Throughput is shared. Spread evenly.
- **Sending sensitive data unencrypted.** Use KMS server-side encryption. For PII, evaluate Message Data Protection.
- **Mobile push as a primary notification path without engagement tracking.** Use Pinpoint (or a third-party MAP) for delivery tracking, A/B test bucketing, opt-out compliance.
- **Cross-account subscription without correctly scoped resource policies.** Both topic policy *and* subscriber resource policy must allow.
- **SMS at scale without budget controls.** SMS pricing varies widely by destination country; one bug can ring up a four-figure bill in a day.

## Pairs well with

- [SQS](sqs.md) — the canonical SNS→SQS→consumer fanout pattern.
- [Lambda](../compute/lambda.md) — function subscription for serverless processing.
- [Kinesis Data Firehose](../analytics/) (forthcoming) — stream events to S3 / Redshift / OpenSearch.
- [EventBridge](eventbridge.md) — the richer event-bus alternative.
- **Mobile Hub / Pinpoint** — for mobile push at scale.

## Pairs well with these repo pages

- [SQS](sqs.md), [EventBridge](eventbridge.md), [Step Functions](step-functions.md).
- `docs/02-patterns/pub-sub.md` (forthcoming).

## Further reading

- [Amazon SNS documentation](https://docs.aws.amazon.com/sns/).
- [SNS message filtering](https://docs.aws.amazon.com/sns/latest/dg/sns-message-filtering.html).
- [FIFO topics](https://docs.aws.amazon.com/sns/latest/dg/sns-fifo-topics.html).
- [SNS DLQs](https://docs.aws.amazon.com/sns/latest/dg/sns-dead-letter-queues.html).
- ["Avoiding fallback in distributed systems", Amazon Builders' Library](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/).
