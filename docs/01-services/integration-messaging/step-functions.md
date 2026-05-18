# Step Functions

> **One-line summary.** Managed workflow orchestration. Defines a state machine in JSON / YAML / Workflow Studio; integrates natively with 220+ AWS services. Two flavors: **Standard** (long-running, exactly-once) and **Express** (high-throughput, at-least-once).

## TL;DR
- The right answer for any workflow with state, retries, parallel branches, error handling, or human-in-the-loop steps that you'd otherwise glue together with Lambda+SQS+DynamoDB by hand.
- **Standard workflows** run up to a year, billed per state transition, exactly-once execution semantics. Right for human approvals, long-running orchestration, business workflows.
- **Express workflows** run up to 5 minutes, billed per million transitions + duration, at-least-once semantics, much higher throughput. Right for high-RPS event processing, IoT data flows, microservice orchestration.
- **Distributed Map** runs up to 10,000 parallel child executions per Map state — competes with AWS Batch for fan-out workloads, with the integration richness of Step Functions.
- Native AWS service integrations (`arn:aws:states:::aws-sdk:<service>:<action>` — every AWS SDK action available without a Lambda wrapper).

## When to use it
- Multi-step business workflows: order processing, KYC, content moderation pipelines.
- Distributed transactions / **sagas** with compensating actions on failure.
- ETL orchestration (Glue jobs, Athena queries, EMR steps).
- ML training pipelines (SageMaker steps, training, evaluation, deployment).
- Coordinating microservices without each service having to know about the next.
- Long-running approvals (human-in-the-loop via callback tokens).
- Fan-out with **Distributed Map** for large-scale parallel processing.

## When NOT to use it
- Single-Lambda, single-purpose work — overkill.
- Pure pub/sub fanout — EventBridge / SNS.
- Streaming with offsets — Kinesis / MSK.
- Workflows that don't have state or branching — SQS + Lambda is simpler.

## Key concepts

### Workflow types
- **Standard** — durable, audit-logged, executions retained for 90 days. Billed per state transition (~$0.025 per 1,000 transitions). Up to 1-year execution duration. **Exactly-once** state transitions. Right for business workflows, sagas, human-in-the-loop.
- **Express** — in-memory, no per-execution audit trail in the Step Functions console (logs go to CloudWatch). Billed per million invocations + duration (much cheaper per execution at high RPS). Up to 5-minute execution. **At-least-once** semantics — design for idempotency. Two sub-flavors:
  - **Synchronous** — caller waits for the response (API-style).
  - **Asynchronous** — fire-and-forget.

### States
The building blocks (in Amazon States Language, ASL):
- **Task** — invokes a Lambda, an AWS service, an HTTP endpoint, or an Activity worker.
- **Pass** — passes input to output, optionally transformed.
- **Choice** — branching on input.
- **Wait** — pause for N seconds or until a timestamp.
- **Parallel** — run multiple branches concurrently, wait for all.
- **Map** — apply a workflow to each item in an array (inline or Distributed).
- **Succeed / Fail** — terminal states.

### Distributed Map
A Map state that processes thousands-to-millions of items by spawning **child executions** in parallel (up to 10,000 concurrent). Reads from S3 (CSV / JSON / Parquet objects) or from an in-memory array. Useful for:
- Processing millions of S3 objects (ML preprocessing, data conversion, batch validation).
- Per-customer fanout in multi-tenant batch jobs.
- A serverless alternative to AWS Batch for embarrassingly parallel work.

### Service integrations
- **Lambda invocation** (synchronous, asynchronous, callback).
- **AWS SDK integrations** — directly call any AWS SDK action without a Lambda wrapper using `arn:aws:states:::aws-sdk:<service>:<action>` (e.g., `aws-sdk:dynamodb:putItem`, `aws-sdk:s3:getObject`).
- **Optimized integrations** — purpose-built for common patterns (ECS RunTask with wait-for-completion, EMR add-step with wait, SageMaker train with wait, etc.).
- **HTTP Task** — call any HTTPS endpoint with managed authentication (EventBridge connection).

### Patterns
- **Request/Response** — invoke and return immediately.
- **Run a Job (.sync)** — invoke and wait for completion (works for many services).
- **Wait for Callback (.waitForTaskToken)** — invoke, get a callback token, pause until your worker / human sends back the token. The primitive for human-in-the-loop.

### Error handling
Per-state `Retry` (with backoff and jitter) and `Catch` (route to a recovery branch on specific errors). The error-handling primitive that replaces hand-rolled try/catch loops in Lambda functions.

### Observability
- **Execution history** with input/output per state.
- **CloudWatch Logs** for Express workflows.
- **X-Ray tracing** end-to-end.
- **EventBridge events** for execution lifecycle.

## Pricing model

- **Standard** — per state transition (~$0.025 per 1,000). Express workflows are usually much cheaper per execution at high RPS.
- **Express** — per million workflow executions + per GB-second of memory-time.
- **Distributed Map** — per million child workflow executions and state transitions; you also pay for the underlying invocations (Lambda, ECS, etc.).
- **Data transfer** — same AWS rules.

For high-volume event-driven workloads (10s of thousands of executions/day), Express is typically much cheaper than Standard.

## Quotas & limits

- **Standard execution duration**: 1 year.
- **Express execution duration**: 5 minutes.
- **Max state transitions per execution**: 25,000 (Standard).
- **Distributed Map concurrency**: 10,000 child executions.
- **State machine size**: 1 MB.
- **Input / output size per state**: 256 KB (S3 paging supported for larger).
- **Concurrent executions per account per Region**: high (thousands), raisable.

## Common pitfalls

- **Standard when Express would do.** For high-RPS workflows that don't need exactly-once or 1-year durations, Express is significantly cheaper.
- **Lambda for every step.** Use AWS SDK integrations to call AWS APIs directly — no Lambda needed, no cold start, no per-invocation cost.
- **No retry config.** Default is no retry. Configure per-state Retry policies for transient errors.
- **Single huge state machine for unrelated workflows.** Decompose; one state machine per workflow.
- **Distributed Map without thinking about downstream rate.** Spawning 10,000 child executions that all hit the same DynamoDB partition or external API will throttle. Use Map's concurrency limit + downstream rate-limiting.
- **State machine JSON edited by hand.** Workflow Studio is the visual editor; CDK / Step Functions Toolkit makes type-checked authoring possible.
- **Callback tokens that never come back.** Human-approval workflows need timeout + escalation paths.
- **Synchronous Express for long-running tasks.** Express maxes at 5 minutes; longer needs Standard or async patterns.

## Pairs well with
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [Batch](../compute/batch.md) — common task targets.
- [EventBridge](eventbridge.md), [SQS](sqs.md), [SNS](sns.md) — triggers and async coupling.
- [DynamoDB](../database/dynamodb.md), [S3](../storage/s3.md) — state persistence and Distributed Map input.
- **SageMaker, Glue, EMR, Athena** — analytics / ML orchestration.
- **CloudWatch + X-Ray** — observability.

## Pairs well with these repo pages
- [Lambda](../compute/lambda.md), [EventBridge](eventbridge.md), [SQS](sqs.md).
- `docs/02-patterns/saga.md`, `docs/02-patterns/outbox.md` (forthcoming).

## Further reading
- [AWS Step Functions documentation](https://docs.aws.amazon.com/step-functions/).
- [Standard vs Express workflows](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html).
- [Distributed Map](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-asl-use-map-state-distributed.html).
- [AWS SDK integrations](https://docs.aws.amazon.com/step-functions/latest/dg/supported-services-awssdk.html).
- [Workflow Studio](https://docs.aws.amazon.com/step-functions/latest/dg/workflow-studio.html).
