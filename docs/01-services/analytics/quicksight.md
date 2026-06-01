# QuickSight

> **One-line summary.** AWS's managed BI service. Dashboards, embedded analytics, paginated reports, and **Q** (natural-language Q&A and Amazon-Q-powered conversational analytics).

## TL;DR

- The right managed BI tool when you want dashboards consumed inside AWS-aware orgs without standing up Tableau / Looker / Power BI infrastructure.
- **SPICE** (Super-fast, Parallel, In-memory Calculation Engine) caches datasets in memory for sub-second dashboard queries — the difference between a slow dashboard and a snappy one.
- **Q** adds natural-language queries ("show me revenue by region last quarter"), automated insights, and Amazon-Q-style narrative generation.
- **Embedded analytics** is first-class — embed dashboards into your own SaaS app with row-level security and per-tenant data isolation.
- Pricing is **per user** (Authors create, Readers view), with separate SPICE-capacity and Q-feature fees. Plan the user model before deploying.

## When to use it

- Internal BI dashboards over AWS data (Redshift, Athena, RDS, Aurora, S3, OpenSearch, Snowflake).
- Embedded analytics in customer-facing SaaS apps.
- ML-augmented narratives and natural-language Q&A on top of your data.
- Reports and dashboards distributed to non-technical stakeholders.

## When NOT to use it

- Highly customized data viz (D3-style bespoke charts) — use a custom front-end on your own analytics API.
- Real-time streaming dashboards with sub-second refresh — QuickSight refreshes via SPICE or direct query; not designed for second-by-second updates.
- Workloads where the team's already deeply invested in Tableau / Looker / Power BI — switching tools has real cost.

## Key concepts

### Editions

- **Standard** — single-user, no SPICE-shared, limited features. (Used mostly historically; most teams use Enterprise.)
- **Enterprise** — multi-user, IAM Identity Center / AD federation, SPICE, embedded analytics, fine-grained security, Q. The current default.
- **Enterprise + Q** — Enterprise plus the Q (natural-language) features.

### Authors and Readers

- **Author** — creates datasets, analyses, dashboards. Per-user monthly subscription.
- **Reader** — views dashboards and paginated reports. Per-session pricing (a Reader pays per dashboard session, bounded monthly).

The Reader-session pricing model means thousands of occasional viewers cost less than they would per-seat.

### Datasets and SPICE

A **dataset** is a definition of data source + filters + joins + calculated fields. Two materialization modes:

- **SPICE** — load the dataset into the in-memory engine; dashboards query SPICE. Sub-second. Refresh on schedule or via incremental refresh.
- **Direct query** — pass-through to the source on every query. Right for very fresh data or for sources too large to fit in SPICE.

SPICE capacity is purchased separately (per GB-month).

### Analyses and dashboards

- **Analysis** — the editing surface where authors build visuals.
- **Dashboard** — the published, read-only artifact viewers consume.

### Visuals

Standard chart types (bar, line, pie, KPI, table, heatmap, sankey, geospatial, treemap, custom URL), plus ML-powered visuals (forecast, anomaly detection, key-driver narratives).

### Q (natural-language)

- **Q&A** — type / speak a question in natural language; Q generates the visual.
- **Q Topics** — curated subject areas Q uses to interpret questions.
- **Generative BI authoring** — describe a dashboard in plain language; Q generates a starting point.
- Amazon Q in QuickSight underlies many of these features.

### Embedded analytics

- Embed dashboards in your app via signed URLs.
- **Anonymous embedding** for public dashboards.
- **Namespaces** — isolated user pools for multi-tenant SaaS.
- **Row-level security (RLS)** — per-user / per-tenant data isolation enforced at query time.

### Paginated reports

Pixel-perfect, multi-page reports (the use case formerly served by Crystal Reports / SSRS). Useful for compliance / regulatory reporting.

### ML integrations

SageMaker integration for custom ML models scoring datasets; built-in forecast / anomaly detection without external infrastructure.

### Identity and access

IAM Identity Center, SAML, Active Directory, and IAM-federated user provisioning. RLS for per-user data scope.

## Pricing model

- **Author subscription** — per-user monthly.
- **Reader sessions** — per 30-minute session, capped per Reader per month.
- **SPICE capacity** — per GB-month.
- **Q** — per Author + per Reader add-on.
- **Embedded sessions** — per-session pricing similar to Reader.
- **Paginated reports** — separate per-user pricing tier.

The economic story: thousands of casual Readers via session-based pricing is much cheaper than per-seat tools. Heavy Author and Q users add up faster.

## Quotas & limits

- **SPICE capacity per account**: configurable; large datasets in the TB range supported.
- **Datasets per analysis**: many.
- **Visuals per analysis / dashboard**: high (30+).
- **Dashboards per account**: thousands.
- **Concurrent users**: scales with the QuickSight service.
- **Embedded user namespaces**: bounded; check current docs for very-large SaaS embeds.

## Common pitfalls

- **All Readers, no SPICE.** Direct queries on every dashboard view = slow dashboards + expensive source costs. Use SPICE for any dashboard with non-trivial traffic.
- **Per-seat Author pricing for ad-hoc explorers.** If explorers don't need to publish, give them Reader access to a sandbox dashboard.
- **No RLS for multi-tenant embeds.** All tenants see all data; data leak. Always RLS for SaaS embedding.
- **Q without curated Topics.** Q's answers are only as good as the data model it's pointed at. Curate Topics for the questions users ask.
- **Refreshing huge SPICE datasets on a tight schedule.** Wastes capacity. Use incremental refresh.
- **Storing PII in QuickSight datasets.** SPICE persists data; treat SPICE as a data store with the same security expectations as a database.
- **Skipping versioning.** QuickSight supports versioning analyses / dashboards via export / CFN; without it, "who changed this dashboard" is a hard question.

## Pairs well with

- [Athena](athena.md), [Redshift](../database/redshift.md), [RDS / Aurora](../database/rds.md), [OpenSearch](opensearch.md), [S3](../storage/s3.md) — data sources.
- [Lake Formation](lake-formation.md) — fine-grained perms upstream.
- [Cognito / IAM Identity Center](../security-identity/) — auth.
- **Amazon Q in QuickSight** — natural-language and gen-AI features.
- **SageMaker** — custom ML model scoring.

## Pairs well with these repo pages

- [Athena](athena.md), [Redshift](../database/redshift.md), [Lake Formation](lake-formation.md), [OpenSearch](opensearch.md).

## Further reading

- [Amazon QuickSight documentation](https://docs.aws.amazon.com/quicksight/).
- [SPICE](https://docs.aws.amazon.com/quicksight/latest/user/spice.html).
- [Embedded analytics](https://docs.aws.amazon.com/quicksight/latest/user/embedded-analytics.html).
- [Q in QuickSight](https://docs.aws.amazon.com/quicksight/latest/user/quicksight-q.html).
- [Row-level security](https://docs.aws.amazon.com/quicksight/latest/user/restrict-access-to-a-data-set-using-row-level-security.html).
