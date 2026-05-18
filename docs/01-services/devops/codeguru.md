# CodeGuru

> **One-line summary.** Two ML-powered developer tools — **CodeGuru Profiler** (continuous performance profiling for JVM and Python apps) and **CodeGuru Reviewer** (automated code review against best-practice rules; **closed to new repository associations as of November 7, 2025** — superseded by Q Developer).

## Status

> ⚠️ **CodeGuru is split into two products with different statuses:**
>
> - **CodeGuru Profiler** — **active**, fully supported. JVM and Python production profiling.
> - **CodeGuru Reviewer** — **closed to new repository associations as of November 7, 2025**. Existing associations continue. AWS recommends migrating to **[Amazon Q Developer](../ml-ai/q.md)**, which includes static analysis (SAST), secrets detection, dependency vulnerability scanning, and code-quality issue detection.

## TL;DR
- **Profiler**: production-grade profiling agent for JVM (Java, Scala, Kotlin) and Python apps. Continuously samples CPU and latency; surfaces flame graphs and recommendations.
- **Reviewer**: was an ML-powered code-review tool that commented on PRs with security and best-practice findings. **Now closed for new repos**; Q Developer is the replacement.
- For new projects in 2026, use **Q Developer** for code review and **Profiler** for production performance analysis.

## When to use it

### CodeGuru Profiler
- Production JVM / Python services with performance bottlenecks to investigate.
- Identify hot methods, GC pressure, deserialization overhead, hot paths in libraries.
- Reduce compute cost by surfacing inefficient code.
- Profile in production with low overhead (≤ 1% typically).

### CodeGuru Reviewer (existing users only)
- Existing associations: keep using until you migrate.
- New projects: use **Q Developer** instead.

## When NOT to use it
- Profiling languages CodeGuru Profiler doesn't support (Go, Rust, Node, .NET) — use language-native profilers (pprof, `perf`, OpenTelemetry, Datadog, etc.).
- Code review on new projects — use **Q Developer**.

## Key concepts

### CodeGuru Profiler
- **Agent** — small library you add to your application; samples stack traces periodically (default ~1% CPU overhead).
- **Profiling group** — logical group for a service across hosts / Lambdas / containers.
- **Flame graph** — visualization of where CPU time is spent; the standard tool for spotting hot methods.
- **Recommendations** — ML-suggested improvements ("this serialization library is a known bottleneck; try X").
- **Anomaly detection** — flags unusual CPU patterns vs the baseline.
- **Lambda support** — automatic profiling for Lambda functions (no agent install for some runtimes).
- **Cost estimation** — translates "this hot method costs ~$X / month" for prioritization.

### CodeGuru Reviewer (existing users)
- **Repository association** — connect a repo (CodeCommit / GitHub / GitHub Enterprise / Bitbucket / S3 archive).
- **Pull request reviews** — Reviewer comments on PRs with detected issues.
- **Code reviews on demand** — analyze a full branch / commit on demand.
- **Categories** — security issues, best practices, AWS-API best practices, language-specific issues, secrets in code.
- **Severity levels** — Critical, High, Medium, Low.

## Migration from CodeGuru Reviewer to Q Developer

Q Developer offers a superset of Reviewer's capabilities:
- **Static analysis (SAST)** for security vulnerabilities.
- **Secrets detection** (credentials in code).
- **Dependency vulnerability detection (SCA)**.
- **Code-quality issues**.
- **Integrated in IDE plugins and GitHub / GitLab**.
- **Agentic code-review on PRs** — comment with suggested fixes, not just findings.

Practical migration:
1. Install Q Developer plugins in the team's IDEs.
2. Wire Q Developer's GitHub / GitLab integration for repo-level PR review.
3. Decommission CodeGuru Reviewer repo associations after parity is validated.

## Pricing model

### Profiler
- **Per profiling-group per active hour** (small flat fee per agent-hour).
- Lambda profiling included in the agent fee.

### Reviewer (existing)
- **Per 100 lines of code** scanned per month, with monthly free tier.
- No new repos can be associated; existing ones bill as before.

### Q Developer
- See [`../ml-ai/q.md`](../ml-ai/q.md) — Free tier + per-user-per-month Pro tier.

## Quotas & limits

- **Profiling groups per account per Region**: bounded; raisable.
- **Profiling agent overhead**: tunable; default ~1% CPU.
- **Profiler retention**: configurable; historical profiles persist for analysis.

## Common pitfalls

- **Reviewer for new repos.** Won't work; new associations are blocked since Nov 7, 2025. Use Q Developer.
- **Profiler agent in dev environments only.** The point is *production* profiling; sampling overhead is low enough for prod.
- **Skipping Profiler for "we have CloudWatch metrics."** CloudWatch shows what's slow; Profiler shows *why* (the hot method). Different problems.
- **Profiler results ignored.** Recommendations only matter if someone acts. Add a recurring "look at top recommendation" rotation.
- **Treating CodeGuru as the only code-review.** Whether you're on Reviewer (existing) or Q Developer, human review still matters. ML augments, doesn't replace.
- **Forgetting Q Developer covers more than Reviewer did.** Q Developer's agentic features (auto-fix suggestions, code transformation) are a real upgrade.

## Pairs well with
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EC2](../compute/ec2.md) — Profiler runs in any of these.
- [X-Ray](x-ray.md) — distributed tracing pairs with method-level profiling.
- [CloudWatch](../observability/) (forthcoming) — alarms and dashboards alongside Profiler insights.
- [Q Developer](../ml-ai/q.md) — the replacement for Reviewer.
- [CodePipeline](codepipeline.md), [CodeCommit](codecommit.md), GitHub / GitLab — source for legacy Reviewer associations.

## Pairs well with these repo pages
- [Q Developer](../ml-ai/q.md), [X-Ray](x-ray.md), [Inspector](../security-identity/inspector.md).

## Further reading
- [Amazon CodeGuru Profiler documentation](https://docs.aws.amazon.com/codeguru/latest/profiler-ug/).
- [Amazon CodeGuru Reviewer availability change](https://docs.aws.amazon.com/codeguru/latest/reviewer-ug/codeguru-reviewer-availability-change.html).
- [Migrate from CodeGuru Reviewer to Amazon Q Developer](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/code-review.html).
- [Profiler supported runtimes](https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up.html).
