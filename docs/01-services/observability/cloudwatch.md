# CloudWatch

> **One-line summary.** AWS's observability backbone — **Logs, Metrics, Alarms, Dashboards, Synthetics, RUM, Application Signals** — under one service umbrella.

## TL;DR
- The default place AWS services emit telemetry. Logs, metrics, traces (via X-Ray), alarms, and synthetic checks all live here.
- **Logs** — structured / unstructured log storage, queried with **Logs Insights** (CWLI) SQL-like language; subscriptions ship to Lambda / Firehose / OpenSearch.
- **Metrics** — time-series; standard (15-month retention, 60s-1m granularity by default) and **high-resolution** (1-second resolution). **Custom metrics** via `PutMetricData`, **EMF (Embedded Metric Format)** for log-derived metrics.
- **Alarms** drive paging, auto-scaling, and remediation. Composite alarms combine conditions; metric math computes derived signals.
- **Application Signals** is the modern auto-instrumented APM layer — SLOs, USE/RED, service maps with no manual instrumentation. **New 2026 features:** SLO Recommendations, Service-Level SLOs, SLO Performance Reports.
- **Synthetics** (Canary scripts) + **RUM** (real user monitoring) close the user-facing-experience side.

## When to use it
- Always. CloudWatch is the AWS-native default for logs, metrics, and alarms.
- APM-style application monitoring (Application Signals).
- Synthetic monitoring of user journeys (Canaries).
- Real-user monitoring of web apps (RUM).
- Log-driven incident response (Logs Insights queries during outages).
- Auto-scaling and remediation triggered by alarms.

## When NOT to use it
- Workloads where you already pay for Datadog / Grafana Cloud / New Relic / Honeycomb — CloudWatch overlap is mostly redundant, though many teams keep CloudWatch as the AWS-side aggregation point with downstream forwarding.
- Workloads with extremely high cardinality (millions of distinct metric dimensions) — CloudWatch isn't optimized for that; Managed Prometheus or specialized tools fit better.

## Key sub-features

### Logs
- **Log groups** + **log streams** (one stream per producer-instance / per container / per Lambda invocation source).
- **Retention**: configurable per log group (1 day – 10 years – never expire).
- **Logs Insights** — interactive SQL-like queries (`stats count() by bin(5m)`, `parse @message ...`).
- **Subscription filters** — stream logs to Lambda / Firehose / Kinesis / OpenSearch for further processing.
- **Live Tail** — real-time log streaming in the console (millisecond delay).
- **Anomaly detection** — auto-learn log patterns and flag deviations.
- **Account-level subscription filters** — apply to all log groups in an account.

### Metrics
- **Standard metrics** — 1-minute resolution by default; some AWS services emit at 5-min.
- **Detailed monitoring** — 1-minute resolution for services that default to 5-min.
- **High-resolution custom metrics** — 1-second resolution.
- **PutMetricData** — direct API.
- **EMF (Embedded Metric Format)** — log JSON that CloudWatch parses into metrics. The cheapest way to emit lots of metrics at high cardinality.
- **Metric Math** — compute derived metrics (`error_rate = errors / requests`).
- **Cross-account metric sharing** for the centralized-observability account pattern.

### Alarms
- **Standard alarms** — threshold over N data points in M minutes.
- **Composite alarms** — boolean expression over multiple alarms (`alarm1 AND (alarm2 OR alarm3)`).
- **Anomaly-detection alarms** — alarm when a metric deviates from its learned baseline.
- Actions: **SNS notification**, **EC2 Auto Scaling**, **EC2 actions** (reboot, stop, terminate), **OpsItem creation**, **Systems Manager Automation**, **Lambda**.

### Dashboards
- JSON-defined; widgets for line / stacked / number / text / log / explorer / alarm-status.
- **Cross-account / cross-Region** dashboards via account sharing.
- Snapshots for sharing-as-link.

### Synthetics (Canaries)
- Scheduled scripts (Node.js / Python via Puppeteer / Playwright / Selenium) that hit your service.
- Detect customer-facing failures before users do.
- Outputs: success/failure metric + screenshots / HAR for debugging.

### RUM (Real User Monitoring)
- JavaScript snippet on your web app collects performance, errors, user journeys.
- Sample data; aggregate views into Apdex, error pages, slow URLs.

### Application Signals
- Auto-instrumented APM: USE/RED metrics + traces for EC2 / ECS / EKS / Lambda apps.
- **SLOs** with goal-and-error-budget tracking.
- **2026 additions**: SLO Recommendations (auto-suggest reliability targets from 30 days of P99 / error data), Service-Level SLOs (aggregate across operations), SLO Performance Reports (calendar-aligned historical analysis).
- Uses **X-Ray** under the hood for trace storage.

### ServiceLens
Cross-cutting view tying together metrics, logs, and traces.

### Contributor Insights
Top-N analysis on log fields ("which IPs are hitting `/login` most? which API consumers are erroring?").

### Metric Streams
Stream metrics in near-real-time to Kinesis Data Firehose for third-party consumption (Datadog, Splunk, custom).

### Cross-Account Observability
Designate an **Observability Access Manager** monitoring account; member accounts share Logs / Metrics / Traces / Application Signals data with it. The right pattern for a central SRE / SOC view.

## Pricing model

- **Logs**: per GB ingested + per GB stored + per query data scanned (Logs Insights).
- **Metrics**: per metric per month + per million PutMetricData requests.
- **Alarms**: per alarm per month (standard / high-res / composite different tiers).
- **Dashboards**: per dashboard per month (first 3 free).
- **Synthetics**: per canary run.
- **RUM**: per million events ingested.
- **Application Signals**: per service per month + per million spans.
- **Metric Streams**: per million updates.
- **Data transfer** at standard rates.

The biggest cost surprises: **high-cardinality custom metrics** (each dimension combination is a separate metric) and **Logs ingestion** from chatty services. Use **EMF** for high-cardinality metrics from log data and **log filtering / sampling** to cap volume.

## Quotas & limits

- **Log group retention**: up to 10 years.
- **Metrics**: high cardinality possible but per-metric monthly cost adds up.
- **Alarms per account per Region**: 5,000 default (raisable).
- **Dashboards per account per Region**: 1,000 default.
- **Logs Insights query timeout**: 60 minutes.
- **Synthetics canary count**: bounded; raisable.
- **Cross-Account Observability**: thousands of source accounts per monitoring account.

## Common pitfalls

- **No log retention policy.** Logs accumulate forever at default settings; ingestion is one bill, storage is another.
- **Custom metric per (user, endpoint, region) tuple.** Cardinality explosion. Use EMF or dimension pruning.
- **Alarms on infrastructure causes, not user-visible symptoms.** "CPU > 80%" pages people; "p99 latency > 2s for 5min" pages people about something users care about.
- **No runbook on alarm action.** A page with no playbook at 3 AM is a failure mode.
- **Single account, no Cross-Account Observability.** Multi-account orgs benefit hugely from centralized observability.
- **Skipping Application Signals on services that fit.** It's cheaper than rolling your own instrumentation and gives free SLO + service map.
- **Synthetics canaries that hit production only.** Run them against staging too; catch issues before deploy.
- **No metric filter for log-derived KPIs.** "Number of failed orders" should be a metric, not a Logs Insights query you remember.

## Pairs well with
- [X-Ray](../devops/x-ray.md) — trace backend for Application Signals.
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md), [EC2](../compute/ec2.md) — telemetry producers.
- [Firehose](../analytics/kinesis.md) — log subscription destinations.
- [OpenSearch](../analytics/opensearch.md) — log-heavy analytics.
- [EventBridge](../integration-messaging/eventbridge.md) — alarm and Logs events drive automation.
- **AWS Distro for OpenTelemetry (ADOT)** — recommended instrumentation pipeline.
- **Amazon Managed Grafana / Managed Prometheus** — open-source-style dashboards / metrics.

## Pairs well with these repo pages
- [CloudTrail](cloudtrail.md), [Systems Manager](systems-manager.md), [X-Ray](../devops/x-ray.md), [EventBridge](../integration-messaging/eventbridge.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading
- [Amazon CloudWatch documentation](https://docs.aws.amazon.com/cloudwatch/).
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html).
- [Embedded Metric Format (EMF)](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html).
- [Application Signals](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Signals.html).
- [CloudWatch Synthetics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Synthetics_Canaries.html).
- [Cross-Account Observability](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Unified-Cross-Account.html).
