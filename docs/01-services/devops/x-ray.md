# X-Ray

> **One-line summary.** Managed distributed tracing. Instruments apps to emit trace segments; X-Ray assembles them into request traces showing latency / errors across services. Often paired with (or partially superseded by) **CloudWatch Application Signals** and **OpenTelemetry**.

## TL;DR

- The original AWS tracing service. SDK instruments your code; X-Ray daemon (or OpenTelemetry collector) ships segments; X-Ray builds traces and a service map.
- In 2026, AWS pushes **CloudWatch Application Signals** for auto-instrumented USE/RED metrics + traces — sits on top of X-Ray under the hood but is the simpler starting point.
- **OpenTelemetry** is the recommended instrumentation standard; export to X-Ray via the **AWS Distro for OpenTelemetry (ADOT)** collector.
- X-Ray works across Lambda, ECS, EKS, EC2, API Gateway, ELB, SNS, SQS, Step Functions, DynamoDB, RDS — most AWS services support trace context propagation.
- **Service maps** and **trace timelines** are the load-bearing UI features for "where is the latency / error?" questions.

## When to use it

- Distributed apps where understanding latency and error attribution across services matters.
- Production troubleshooting of slow endpoints / dependent service problems.
- Microservice / serverless architectures with many service hops per request.
- Pairing with Application Signals for the "auto-instrument + dashboard + alarm" workflow.

## When NOT to use it

- Single-service apps where simple logs + metrics suffice.
- Workloads already standardized on Datadog / Honeycomb / Lightstep / New Relic — those vendors have richer trace exploration; you can still ship to X-Ray in parallel if needed.
- Workloads with extremely high trace volume where 100% sampling is unaffordable — use intelligent sampling.

## Key concepts

### Segments and subsegments

- **Segment** — work done by one service for a single request (a Lambda invocation, an HTTP server handling a request).
- **Subsegment** — child work inside a segment (a DynamoDB query, an outbound HTTP call).
- **Annotations and metadata** — key-value pairs you attach to segments; annotations are indexed (queryable), metadata isn't.

### Trace and trace ID

A **trace** is the full set of segments / subsegments tied to one request, identified by an **AWS X-Ray trace ID** (`Root=1-...`). The trace ID propagates across service hops via HTTP headers (`X-Amzn-Trace-Id`).

### Sampling

- **Default sampling rule** — first request per second per service traced, plus 5% of additional requests. Tunable.
- **Sampling rules** in the X-Ray console: per-service, per-HTTP-method, per-URL pattern — adjust the rate.
- **Reservoir + fixed-rate** — preserve traces of rare events (like errors) while capping volume.

### Service map

Visual graph of services and their dependencies, with latency / error rate annotations. The fastest way to find "which service is slow / erroring."

### Trace explorer

Query traces by attributes (service, URL, response code, custom annotation). Drill into individual trace timelines.

### Insights

X-Ray Insights flags anomalies in service latency / error rate and links to traces that exhibit them.

### Instrumentation

- **AWS X-Ray SDK** — native SDKs for Python, Java, Node, Go, .NET, Ruby.
- **OpenTelemetry (recommended)** — vendor-neutral standard; export to X-Ray via **AWS Distro for OpenTelemetry (ADOT)**.
- **Auto-instrumentation** — Lambda's auto X-Ray integration (enable on the function); ECS / EKS via OpenTelemetry sidecar / ADOT collector.

### Application Signals (newer)

**CloudWatch Application Signals** provides auto-instrumented USE/RED metrics + traces with minimal setup; uses X-Ray for the trace backend. For new workloads, start with Application Signals; drop to X-Ray-native instrumentation when you need more control.

### Trace summary and CloudWatch ServiceLens

Integrated view combining metrics, logs, and traces.

## Pricing model

- **Per million traces recorded** (1 trace = 1 segment).
- **Per million traces retrieved** (queried in the console / API).
- **Per million Insights events** generated.
- **Application Signals** has its own pricing (per metric / per million spans), additive.

X-Ray itself is generally cheap; sampling controls keep volume manageable. The cost growth scenario is high-RPS services with high sampling rates.

## Quotas & limits

- **Trace ingestion**: high; raisable.
- **Trace retention**: 30 days.
- **Segment size**: 64 KB (compressed).
- **Annotations per segment**: 50.
- **Metadata per segment**: 32 KB.
- **Sampling rules per account per Region**: 1,000.
- **Trace query result count**: 1,000 per query (page through more).

## Common pitfalls

- **100% sampling in production.** Expensive and noisy. Use sampling rules; preserve errors and slow traces.
- **No trace-ID propagation in custom services.** A custom HTTP client that doesn't forward `X-Amzn-Trace-Id` breaks the trace. Use the AWS SDK / OTel-instrumented HTTP client.
- **Annotations vs metadata confusion.** Only annotations are indexed / queryable. Use annotations for things you'll search on (`customer_id`, `feature_flag`); metadata for everything else.
- **X-Ray instead of Application Signals for new workloads.** Application Signals is simpler to get started with and uses X-Ray under the hood.
- **OpenTelemetry instrumentation pointed at a non-AWS backend only.** You can export to both X-Ray and Datadog / Honeycomb via OTel multi-export.
- **Lambda X-Ray off.** Enable Active Tracing on Lambda functions you care about; cost is small, value during incidents is large.
- **No service-map review.** Service map shows the topology; review it periodically — drift from architecture diagrams is common.

## Pairs well with

- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md), [API Gateway](../networking/api-gateway.md) — all support X-Ray traces.
- **CloudWatch Application Signals** — auto-instrumented USE/RED on top of X-Ray.
- **AWS Distro for OpenTelemetry (ADOT)** — recommended instrumentation pipeline.
- [Step Functions](../integration-messaging/step-functions.md) — native trace propagation across states.
- [CloudWatch Logs / Metrics](../observability/) (forthcoming) — full observability picture.

## Pairs well with these repo pages

- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md), [API Gateway](../networking/api-gateway.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading

- [AWS X-Ray documentation](https://docs.aws.amazon.com/xray/).
- [CloudWatch Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals.html).
- [AWS Distro for OpenTelemetry](https://aws-otel.github.io/).
- [X-Ray sampling rules](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-sampling.html).
- [X-Ray Insights](https://docs.aws.amazon.com/xray/latest/devguide/xray-console-insights.html).
