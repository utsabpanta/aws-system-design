# Lambda

> **One-line summary.** Run code in response to events without provisioning or managing servers. Pay per millisecond of execution.

## TL;DR
- The serverless compute primitive. Scales 0-to-N automatically; pay only when code is running.
- Right for event-driven, short (< 15 min), stateless work. Wrong for long-running, latency-critical, or steady high-RPS workloads where Fargate/EC2 is cheaper at scale.
- **SnapStart** dramatically reduces Java/Python/.NET cold starts (Node.js is not supported). Use it for any latency-sensitive synchronous Lambda.
- The cost cliff: cheap up to ~1M invocations/day on small functions, increasingly expensive vs. Fargate above ~10M for long-running ones.
- Memory and CPU are coupled — sometimes 2× memory makes the function 3× faster *and* net-cheaper. Use [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) to find the sweet spot.

## When to use it
- HTTP APIs via API Gateway or Lambda Function URLs.
- Reacting to events: S3 uploads, DynamoDB Streams, SQS/SNS messages, EventBridge rules, Kinesis records.
- Cron-style scheduled work (EventBridge Scheduler).
- Step Functions task states for orchestrated workflows.
- Glue logic between AWS services (the most common use).
- Edge logic via Lambda@Edge / CloudFront Functions for latency-sensitive request transformation.

## When NOT to use it
- Long-running jobs (> 15 minutes). Use Fargate, Batch, or Step Functions Distributed Map.
- Sustained high RPS with predictable load — Fargate or EC2 with Savings Plans wins on cost at scale.
- Workloads that need persistent connections (WebSocket servers, gaming relays). Use Fargate or EC2.
- WebSocket-heavy chat apps where you'd hold long connections — use API Gateway WebSocket, AppSync, or a Fargate WebSocket server.
- Compute-heavy ML inference with GPUs (Lambda has no GPU runtime).

## Key concepts

**Function** — a unit of code (Zip up to 250 MB unzipped, or a container image up to 10 GB) with a runtime, handler, memory size (128 MB – 10,240 MB), and timeout (1 s – 15 min).

**Execution model.** Each concurrent invocation runs in its own micro-VM. Inside a single micro-VM, invocations run sequentially — module-level code runs once per cold start; handler code runs once per invocation. Use this fact: open DB connections, load ML models, init SDK clients at module scope (outside the handler) so they're reused.

**Cold start.** When a request needs a new micro-VM, Lambda provisions one — Firecracker boot + runtime init + your initialization code. Sub-100ms for Node.js/Python; 1–10 s for Java without SnapStart. Mitigations: SnapStart, provisioned concurrency, smaller deployment artifact, Graviton runtimes, deferring imports.

**SnapStart** — pre-initializes the function once after deploy, snapshots the micro-VM memory, and restores from the snapshot on each cold start. Supported on **Java 11+, Python 3.12+, and .NET 8+** as of 2026. Not supported on Node.js, Ruby, custom runtimes, or container images. For Python/.NET there's a small per-snapshot-cache and per-restore charge; for Java it's free.

**Provisioned concurrency** — keeps N micro-VMs warm at a fixed cost. Use sparingly; usually a smaller artifact + SnapStart + Graviton is cheaper.

**Concurrency limits.** Account-level concurrent execution quota (default 1,000, raisable). Reserved concurrency caps a single function's concurrency (also acts as a backpressure mechanism). Provisioned concurrency is a separate dial.

**Event sources.** Synchronous (API Gateway, ALB, Function URL, SDK invoke) — caller sees the result. Asynchronous (SNS, EventBridge, S3) — Lambda buffers and retries (twice by default, then DLQ). Poll-based (SQS, Kinesis, DynamoDB Streams, MSK, self-managed Kafka) — Lambda polls and invokes in batches.

**Runtimes (2026).** Managed: Node.js 22 (latest), Python 3.13, Python 3.12, Java 21/17/11, .NET 8, Ruby 3.3, Go via `provided.al2023`. Node 18/16 and most Amazon Linux 2 runtimes are deprecated or on a deprecation schedule; new functions can't use the retired ones. Always pick the newest LTS runtime your code supports.

**VPC mode.** Putting a Lambda in a VPC attaches a Hyperplane ENI on first invoke (fast, but adds cold-start cost the first time). Use it only when the function actually needs to reach VPC-private resources (RDS, ElastiCache, internal services); a Lambda that only talks to AWS service APIs has no security benefit from being in a VPC.

## Pricing model

Three components, billed per invocation:
1. **Requests** — $0.20 per 1M (Standard); free tier covers first 1M/month per account.
2. **Compute** — GB-seconds (memory × duration). $0.0000166667 per GB-second on x86 (Graviton ~20% cheaper). Per-millisecond billing.
3. **Optional**: provisioned concurrency (charged per GB-second the warm pool is active), SnapStart cache/restore (Python/.NET only), data transfer.

The breakeven vs Fargate: at ~70%+ utilization on long-running workloads, Fargate or EC2 is cheaper. For bursty traffic with idle time, Lambda wins easily. Use the [AWS Pricing Calculator](https://calculator.aws/) for any function spending >$500/month — there's usually a 30%+ optimization in there.

## Quotas & limits

- **Concurrency**: 1,000 per account per Region default (raise via Service Quotas; many production accounts run >10k).
- **Timeout**: 15 minutes max.
- **Memory**: 128 MB – 10,240 MB (CPU scales linearly with memory).
- **Deployment package**: 250 MB unzipped (Zip), 10 GB (container image).
- **`/tmp` storage**: 512 MB default, configurable up to 10 GB.
- **Concurrent ENIs** when in VPC: limited per Region (typically 250); usually not the bottleneck thanks to Hyperplane.
- **Event source batch size**: SQS up to 10,000 (10 by default); Kinesis up to 10,000.
- **Payload size**: 6 MB synchronous, 256 KB asynchronous.

## Common pitfalls

- **Hot-loading at request time.** Loading an ML model in the handler runs it every invocation. Move it to module scope.
- **Forgetting timeouts on downstream calls.** A Lambda whose downstream hangs will burn through its 15-minute budget at full rate. Set HTTP/DB timeouts explicitly.
- **Re-creating SDK clients per invocation.** Module-scope them.
- **VPC for no reason.** Adds ENI overhead and complicates cold starts with no security benefit if the function doesn't need VPC resources.
- **Synchronous chains of Lambdas.** Lambda calling Lambda synchronously pays double, doubles latency, and burns concurrency. Use Step Functions or async patterns.
- **No DLQ on async/SQS sources.** Bad payloads will retry forever or be silently dropped after retries.
- **Ignoring [Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning).** The default memory choice is usually wrong for cost.
- **No SnapStart on Java/Python/.NET latency-sensitive functions.** Free (for Java) or cheap (for Python/.NET) and dramatically reduces cold-start tail.

## Pairs well with
- **API Gateway / ALB / Function URLs** — HTTP-facing functions.
- **SQS / SNS / EventBridge / Kinesis** — async event sources with retries and DLQs built in.
- **Step Functions** — orchestrate multiple Lambdas with retries, parallelism, and human-in-the-loop.
- **DynamoDB Streams** — react to table changes.
- **Powertools for AWS Lambda** ([Python](https://docs.powertools.aws.dev/lambda/python/), Node, Java, .NET) — observability, idempotency, parameter handling primitives.

## Further reading
- [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/).
- [Lambda runtime support policy](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html).
- [SnapStart](https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html).
- Amazon Builders' Library — "Reliability, constant work, and a good cup of coffee", "Reducing Amazon SQS poll wait times to milliseconds with Amazon Kinesis Client Library".
- "Serverless Patterns Collection" (serverlessland.com) — community-maintained reference patterns.
