# Operational Excellence

> **One-line summary.** Run, monitor, and continuously improve workloads — and make the system tell you when something is wrong before a customer does.

## TL;DR

- Operations is code. Runbooks, deployments, infra, and dashboards all live in a repo.
- You can't operate what you can't observe. Logs, metrics, traces, and events are first-class system inputs, not afterthoughts.
- Small, frequent, reversible changes beat big infrequent ones. The unit of progress is "the next safe deploy," not "the next release."
- Every incident leaves the system better than it found it — through a blameless postmortem and at least one mechanical fix (alarm, runbook, guardrail).
- The default failure mode of "operational excellence" is performative dashboards no one reads. Build the dashboards humans actually look at when paged.

## What the pillar is about

Operational Excellence is the pillar that says "you'll be running this thing in production, not just shipping it." It covers how teams organize work, codify operations, deploy safely, observe what's running, and learn from incidents.

It's the easiest pillar to fake and the hardest to actually do. Every team claims good operations; very few teams can answer "show me the runbook for the last alarm that fired" without flinching.

## AWS's six design principles

Per the AWS Well-Architected Framework, the Operational Excellence pillar rests on six principles:

1. **Perform operations as code.** Infrastructure (CloudFormation/CDK/Terraform), policies (SCPs, OPA), runbooks (SSM documents, Lambda), and dashboards (CloudWatch JSON) all live in version control.
2. **Make frequent, small, reversible changes.** Smaller blast radius, easier rollback, faster feedback. Deploy daily, not monthly.
3. **Refine operations procedures frequently.** Game-day failures, chaos experiments, regular runbook drills.
4. **Anticipate failure.** Pre-mortems, dependency mapping, blast-radius budgets. Build the system assuming each component will eventually fail.
5. **Learn from all operational events and failures.** Blameless postmortems with action items that actually ship.
6. **Use managed services to reduce operational burden.** RDS over self-managed Postgres, Lambda over EC2, Fargate over ECS-on-EC2. Pay AWS to be on call for the layers below your code.

## Key practices

### Deployment safety

- **CI/CD on a trunk-based branch model.** Pull request → CI → auto-deploy to staging → gated promotion to prod. CodePipeline, CodeBuild, CodeDeploy are the AWS-native answer; GitHub Actions + a cloud runner is equally common.
- **Progressive delivery** (canary, blue/green, linear). Route a small slice of traffic to the new version; promote only if metrics hold. CodeDeploy supports this for ECS, Lambda, and EC2; for stricter SLOs, App Mesh or service mesh handles weighted routing.
- **Automatic rollback** on regression. Define the alarm that defines "broken" (error rate, p99 latency, custom KPI). The deploy system rolls back automatically when the alarm fires.

### Observability

Three pillars (overloaded word):

- **Logs** — high-cardinality, lossless, human-readable. CloudWatch Logs, OpenSearch, or a third-party (Datadog, Honeycomb).
- **Metrics** — low-cardinality, aggregated, cheap. CloudWatch Metrics, Managed Prometheus.
- **Traces** — request-scoped, sampled, show end-to-end flow across services. X-Ray, OpenTelemetry into X-Ray or third-party.

Add the fourth, increasingly first-class:

- **Events** — discrete, business-relevant things that happened (order placed, deploy started). EventBridge or a Kafka/Kinesis topic. The audit log your CFO will eventually need.

Use **CloudWatch Application Signals** to get USE/RED metrics auto-instrumented without writing manual code. Use **synthetics** (CloudWatch Synthetics) for "is the user flow working" checks separate from infrastructure health.

### Alerting

The rule: **page on user-visible symptoms, not on causes.** "p99 latency over 1s for 5 minutes" pages someone. "CPU at 80%" might be normal; suppress it unless it correlates to a symptom.

Two on-call habits that compound:

- Every alarm has a runbook link in the description. If you can't write the runbook, the alarm probably shouldn't page.
- Every alarm has an owner. CloudWatch alarm tags (`Service`, `OncallTeam`) make this enforceable.

### Runbooks as code

SSM **Automation documents** and SSM **Run Command** let you codify ops procedures (restart a service, rotate a key, drain a node) so anyone on call can execute them safely. The doc is reviewed, tested, audited — none of that is true of a text doc in Confluence titled "How to restart the worker."

### Postmortems

Blameless, mechanical, written. The format that survives organizational change:

1. Timeline (UTC, second-level precision where possible).
2. Customer impact.
3. Contributing factors (plural — there's never just one).
4. Action items (each with an owner, a due date, and a Jira/Linear ticket).
5. What went well.

The action items are the only part that matters. A postmortem that doesn't produce shipped changes is a writing exercise.

## AWS services that support this pillar

- **CloudFormation, CDK** — infrastructure as code, drift detection.
- **Systems Manager** — Run Command, Automation, Parameter Store, Patch Manager, Session Manager.
- **CodePipeline, CodeBuild, CodeDeploy** — CI/CD with built-in canary/blue-green.
- **CloudWatch** (Logs, Metrics, Alarms, Dashboards, Synthetics, RUM, Application Signals) — the observability spine.
- **X-Ray** — distributed tracing.
- **EventBridge** — event bus for ops events, scheduled tasks, cross-account fan-out.
- **AppConfig** — runtime feature flags and config with safe deployment.
- **Trusted Advisor, Health, Config** — proactive checks against best practice and resource compliance drift.
- **Resilience Hub** — assess and track recovery objectives against your defined RTO/RPO.

## Common anti-patterns

- **"We'll add monitoring later."** It will be after the first outage, and that outage will be debugged by tailing logs.
- **Dashboards no one looks at.** A dashboard with 80 widgets is a dashboard no one looks at. Maintain a "first 5 minutes of an incident" dashboard with ≤6 panels, separately from the deep-dive dashboards.
- **Alarms that page on causes.** "Lambda errors > 0" pages you for every transient blip. Page on "5xx rate > 1% for 5 minutes" instead.
- **Manual deploys.** Anything that can be done from a terminal can be done from CI; if it can't be done from CI, it's a security and reproducibility risk.
- **Postmortems that don't produce shipped changes.** A document is not a fix.
- **Tribal runbooks.** "Ask Sarah" doesn't survive Sarah's vacation.
- **Single-account everything.** AWS Organizations + multi-account (per `multi-account-organization` reference architecture) is operational hygiene, not a maturity goal.

## Pairs well with

- [Reliability](reliability.md) — the operations practices here are what make reliability targets achievable.
- [Security](security.md) — operations as code is the only credible audit trail.
- `docs/04-reference-architectures/ci-cd-pipeline.md` — concrete CI/CD blueprint.
- `docs/04-reference-architectures/log-aggregation.md` — observability at scale.

## Further reading

- AWS Well-Architected Framework — Operational Excellence pillar whitepaper.
- *Site Reliability Engineering*, Google — the SLO/SLI vocabulary and on-call practices.
- *The DevOps Handbook* (Kim, Humble, Debois, Willis) — flow, feedback, and continuous learning.
- *Accelerate* (Forsgren, Humble, Kim) — the four DORA metrics (lead time, deploy frequency, MTTR, change fail rate).
