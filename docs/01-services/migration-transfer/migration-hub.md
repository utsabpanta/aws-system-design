# Migration Hub

> **One-line summary.** Central console for planning and tracking AWS migrations across DMS, MGN, Application Discovery Service, and partner tools. Inventory of sources, server-by-server tracking, and (via AWS Transform) AI-driven recommendations.

## TL;DR

- The "where am I in the migration?" view. Aggregates status from MGN (servers), DMS (databases), and other migration tools (CloudEndure legacy, partner products).
- **Strategy Recommendations** analyzes your environment and suggests modernization paths (lift-and-shift vs replatform vs refactor).
- **EC2 Instance Recommendations** sizes target EC2 instances based on observed source utilization.
- **Migration Hub Orchestrator** automates multi-step migration workflows.
- **AWS Transform** (launched May 2025) is the newer AI-driven evolution — all Migration Hub capabilities are now also available in AWS Transform with enhanced AI features.
- ⚠️ **Migration Hub Refactor Spaces** (the multi-account routing layer for Strangler Fig modernization) is **closed to new customers since November 7, 2025**.

## TL;DR — what's where in 2026

| Feature | Service / Location |
|---|---|
| Server migration | **MGN** (Application Migration Service) |
| Database migration | **DMS** |
| Discovery (inventory) | **Application Discovery Service** |
| Files / objects | **DataSync** |
| Central dashboard | **Migration Hub** (or **AWS Transform**) |
| Strategy recommendations | **Migration Hub** → migrating to **AWS Transform** |
| Multi-account routing for Strangler Fig | **Migration Hub Refactor Spaces** (closed to new customers) |
| AI-driven migration / modernization | **AWS Transform** (newer) |

## When to use it

- Any multi-server / multi-database AWS migration where status across workstreams matters.
- Strategy / planning phase — get recommendations on modernization paths.
- EC2 right-sizing for migration targets.
- Programs with multiple parallel migration waves needing a central view.

## When NOT to use it

- Single-server / single-DB one-off migrations — too much overhead.
- If you've already adopted **AWS Transform**, work in Transform; Migration Hub will route you there.

## Key concepts

### Sources of migration data

- **AWS Application Discovery Service** — on-prem inventory.
- **MGN** — server-migration progress.
- **DMS** — database-migration progress.
- **CloudEndure Migration** (legacy; replaced by MGN).
- **Partner tools** integrated via the Migration Hub API.

### Home Region

Migration Hub aggregates data to a "home Region" — pick one Region as the migration command center; data from migrations in any other Region rolls up there.

### Applications

- Group source servers / databases logically into **applications**.
- Track migration status per application.

### Strategy Recommendations

- Analyzes your environment (via Application Discovery Service data).
- Recommends per-application strategy:
  - **Rehost** (MGN lift-and-shift).
  - **Replatform** (small modifications, e.g., move to managed RDS).
  - **Refactor / re-architect**.
  - **Repurchase** (move to SaaS).
  - **Retain** (no migration).
  - **Retire** (decommission).

### EC2 Instance Recommendations

- Uses observed CPU / memory / network usage to recommend EC2 instance types for migrated servers.
- Generates a sized cost estimate per server.

### Migration Hub Orchestrator

- Pre-built workflow templates for common migrations (SAP, server migrations, database migrations).
- Custom workflows for org-specific patterns.

### AWS Transform (newer, recommended evolution)

- Launched May 2025.
- AI-driven assessment + recommendations + automation.
- Includes Migration Hub features (Strategy Recommendations, EC2 Instance Recommendations, Journeys, Orchestrator) with enhanced AI capabilities.
- Pairs with Q Developer for code-modernization workflows.

### Migration Hub Refactor Spaces (closed to new customers)
>
> ⚠️ **Closed to new customers since November 7, 2025.** Existing customers continue. AWS Transform / native Strangler Fig with API Gateway + Lambda is the modern path.

Refactor Spaces was the multi-account routing service for the **Strangler Fig** modernization pattern — wraps a monolith with an API Gateway + NLB + IAM, then routes specific paths to new microservices in separate accounts. AWS Transform now provides the equivalent capability with better AI integration.

## Pricing model

- **Migration Hub dashboard and tracking**: free.
- **Strategy Recommendations**: free.
- **EC2 Instance Recommendations**: free (uses Application Discovery Service data).
- **Migration Hub Orchestrator**: free for the orchestrator itself; you pay for the underlying services.
- **Refactor Spaces** (legacy): per-environment hourly + per-service-endpoint fees.
- **AWS Transform**: separate pricing; some features tied to Q Developer Pro tiers.

## Quotas & limits

- **Migration Hub aggregations**: bounded by source-service limits.
- **Applications tracked**: thousands.
- **Strategy Recommendations**: bounded by source environment scope.

## Common pitfalls

- **No home Region set.** Aggregation doesn't happen without it. Choose early.
- **Migration Hub without Application Discovery Service.** Strategy Recommendations need ADS data to be useful.
- **Manual application grouping for hundreds of servers.** Use ADS auto-grouping; iterate.
- **Strategy Recommendations treated as gospel.** They're suggestions based on observed data; validate per workload before committing.
- **Refactor Spaces planned for new projects.** Closed to new customers — use AWS Transform or build Strangler Fig directly with API Gateway + Lambda + IAM.
- **Treating Migration Hub as the only source of truth.** It aggregates; the underlying migration services (MGN, DMS) are authoritative for their specifics.
- **Not evaluating AWS Transform.** If you're starting a new migration in 2026, look at AWS Transform first.

## Pairs well with

- [MGN](mgn.md), [DMS](dms.md), [DataSync](datasync.md), [Application Discovery Service](application-discovery-service.md) — all feed Migration Hub.
- **AWS Transform** — newer evolution.
- [Q Developer](../ml-ai/q.md) — AI-assisted code modernization in conjunction with Transform.
- [Organizations](../observability/organizations.md), [Control Tower](../observability/control-tower.md) — target account / landing zone for migrations.

## Pairs well with these repo pages

- [MGN](mgn.md), [DMS](dms.md), [DataSync](datasync.md), [Application Discovery Service](application-discovery-service.md).

## Further reading

- [AWS Migration Hub documentation](https://docs.aws.amazon.com/migrationhub/).
- [Strategy Recommendations](https://docs.aws.amazon.com/migrationhub-strategy/).
- [EC2 Instance Recommendations](https://docs.aws.amazon.com/migrationhub/latest/ug/ec2-recommendations.html).
- [Migration Hub Orchestrator](https://docs.aws.amazon.com/migrationhub-orchestrator/).
- [Migration Hub Refactor Spaces availability change](https://docs.aws.amazon.com/migrationhub-refactor-spaces/latest/userguide/migrationhub-availability-change.html).
- [AWS Transform](https://aws.amazon.com/migration-hub/features/).
