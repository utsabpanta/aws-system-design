# Sustainability

> **One-line summary.** Minimize the environmental impact of running cloud workloads — the same engineering moves that make systems efficient generally make them greener.

## TL;DR

- Cloud sustainability is the only pillar where doing nothing genuinely makes you worse over time. Idle and overprovisioned resources keep emitting whether they do work or not.
- The shared-responsibility split: AWS optimizes the data center (PPA renewables, custom silicon, efficient cooling); you optimize the workload (right-sizing, scheduling, efficient code).
- Region choice matters. Some Regions run on a much greener grid mix than others. The carbon footprint difference between two Regions can rival the impact of weeks of right-sizing work.
- Serverless is almost always the lower-carbon choice — capacity matches demand by design, so there's no idle to amortize.
- The sustainability pillar is mostly the cost pillar in a different vocabulary. If you've done the cost work, you've done most of the sustainability work — but the framing helps prioritize the remaining wins.

## What the pillar is about

Sustainability is the youngest pillar (added in 2021). It asks "what's the carbon, energy, and resource cost of running this workload, and how do you reduce it over time?"

It splits along the shared-responsibility line the same way security does:

- **AWS is responsible for the sustainability *of* the cloud** — data center efficiency, renewable energy procurement, hardware lifecycle, water use, custom silicon (Graviton, Trainium, Inferentia) that's more efficient per watt than commodity hardware.
- **You are responsible for sustainability *in* the cloud** — workload efficiency, Region selection, capacity matching, data lifecycle, choice of services.

The cloud's structural advantage: it's the most efficient compute available. Hyperscale data centers run at PUEs (Power Usage Effectiveness) around 1.1; the average on-prem corporate data center is closer to 1.8 — so the same workload is dramatically more efficient on AWS just from a building physics standpoint. But that's a one-time win; ongoing improvement requires deliberate engineering choices.

## AWS's six design principles

1. **Understand your impact.** AWS publishes the **Customer Carbon Footprint Tool** in Billing — gives per-Region, per-service emissions estimates. Use it as a baseline.
2. **Establish sustainability goals.** "Reduce kgCO2e per million requests by 30% by Q4." Targets per workload, owned by the team that operates it.
3. **Maximize utilization.** Idle resources are wasted resources. Right-size, autoscale, consolidate.
4. **Anticipate and adopt new, more efficient hardware and software offerings.** Graviton, newer instance families, more efficient runtimes (Lambda Snapstart, Java 21, Rust). Each generation is meaningfully more efficient per unit of work.
5. **Use managed services.** AWS amortizes the operational and capacity overhead across many customers — more efficient than per-customer self-managed clusters.
6. **Reduce the downstream impact of your cloud workloads.** Customer devices, network paths, third-party services. Optimize images for mobile, use CDNs to shorten network paths, avoid polling APIs that could be webhooks.

## Key practices

### Region selection

Not all AWS Regions have the same carbon intensity. The grid mix where the data center plugs in determines a meaningful portion of the workload's emissions. AWS publishes Region-by-Region renewable-energy data, and the differences are non-trivial — some Regions are essentially 100% renewable-matched on an annual basis, others have a heavier fossil-fuel mix.

When latency and data-residency allow, pick a low-carbon Region. For a US workload, that often means `us-west-2` (Oregon — grid is heavily hydro) or `us-east-2` (Ohio); in Europe, `eu-north-1` (Stockholm — hydro/nuclear/wind dominant) and `eu-west-1` (Ireland) tend to be greener than continental Regions.

### Capacity matching

Idle is the carbon enemy. An EC2 instance at 5% utilization still draws meaningful power.

- **Auto-scale aggressively.** Target tracking on CPU or queue depth scales in during low traffic.
- **Schedule non-production environments off.** Dev and staging at 8 AM – 8 PM weekdays = 75%+ savings (carbon and cost).
- **Serverless when load is spiky or unknown.** Lambda's "0 instances when idle" model is the cleanest sustainability story.
- **Bin-packing on shared compute.** ECS/EKS with bin-packing scheduling avoids the "two instances at 30% each instead of one at 60%" anti-pattern.

### Right-sizing

The same play as cost optimization, with the same tools (Compute Optimizer, Trusted Advisor, CloudWatch metrics):

- Resize over-provisioned EC2, RDS, Lambda memory.
- Move from older instance families to newer (M5 → M7g) — typically 20%+ better efficiency.
- Move from x86 to Graviton where the workload supports it.

### Storage lifecycle

Cold data sitting on hot storage burns disk-spin energy for no benefit:

- **S3 lifecycle policies** to move data to Infrequent Access → Glacier → Deep Archive. Or use **S3 Intelligent-Tiering** for automatic transitions.
- **Delete what's not needed.** Old logs, snapshots, dev backups. Set retention policies, don't keep "just in case."
- **Compress.** Logs, exports, archives in gzip/zstd/snappy. CPU is cheaper and more efficient than spinning disk.

### Code and runtime efficiency

The biggest individual-engineer carbon lever:

- **Choose efficient runtimes.** Rust, Go, Java 21 with SnapStart, Python 3.12 — each generation is meaningfully more efficient.
- **Eliminate redundant work.** Cache, batch, deduplicate. Every request that doesn't run is the greenest request.
- **Profile and remove hot loops.** A CPU profile pointing at a hot path is also pointing at avoidable emissions.
- **Async + batch over per-item sync.** Fewer wakeups, more work per cycle.

### Data efficiency

- **Pick the right format.** Parquet/ORC over JSON/CSV for analytics — orders of magnitude smaller and faster to query.
- **Sample, don't store all.** For analytics, often a sampled dataset answers the same questions at 1% of the storage.
- **Use the lowest-precision type that works.** Int8 over Int64 where the range fits; float16 over float32 for many ML workloads.

### Network efficiency

- **CloudFront in front of public origins.** Reduces both data transfer volume and the network hops the request travels.
- **HTTP/2, HTTP/3.** Multiplexed connections beat 1990s-style multiple TCP connections.
- **Compress responses.** gzip/brotli on text payloads — saves bytes on the wire, energy in routers and client modems.
- **Right-size media.** Image and video transcoding to the device's actual resolution. CloudFront Functions + Lambda@Edge for per-request transformations.

### ML and AI workload specifics

ML is currently the fastest-growing source of cloud carbon:

- **Inferentia / Trainium** are AWS's purpose-built ML silicon — substantially more efficient per inference / per training step than GPUs.
- **Right-size models.** A smaller fine-tuned model often beats a giant general-purpose one for a specific task, at a fraction of the energy per inference.
- **Batch inference** where latency allows. Per-request inference overhead dominates small requests.
- **Cache and reuse embeddings, completions, training results.**

## AWS services that support this pillar

- **Customer Carbon Footprint Tool** (in Billing) — per-Region, per-service emissions data.
- **AWS Compute Optimizer** — right-sizing.
- **AWS Trusted Advisor** — idle resource detection.
- **AWS Graviton (M7g, C7g, R7g, …), Inferentia, Trainium** — efficient custom silicon.
- **Lambda, Fargate, App Runner** — capacity-matched serverless compute.
- **S3 Intelligent-Tiering, Glacier** — storage lifecycle.
- **AWS Auto Scaling** — demand-matched capacity.
- **CloudFront** — network efficiency and edge caching.
- **EventBridge Scheduler, Instance Scheduler** — automated shutdown of non-production.

## Common anti-patterns

- **24/7 dev/staging environments.** A Lambda + EventBridge schedule turns this off for 75% of the week.
- **Over-provisioning "for safety."** Capacity headroom is fine; 5× headroom forever is waste.
- **Default Region forever** without checking carbon intensity. Switching from a coal-heavy Region to a hydro/wind Region can dwarf months of right-sizing work.
- **Keeping every log forever.** Define retention, enforce it, transition to Glacier and then delete.
- **Always-on data pipelines** for data no one queries. Move to on-demand (Athena over Glue jobs) where the access pattern is sparse.
- **Self-managed Kubernetes clusters running at 20% utilization** instead of Fargate / serverless equivalents.
- **Ignoring downstream impact.** A polling client costs the same to your AWS bill regardless, but every poll burns battery on the user's phone. Webhooks beat polling.

## Pairs well with

- [Cost Optimization](cost-optimization.md) — almost identical toolkit, different framing.
- [Performance Efficiency](performance-efficiency.md) — efficient code is greener code.
- [Operational Excellence](operational-excellence.md) — sustainability dashboards live alongside operational ones.

## Further reading

- AWS Well-Architected Framework — Sustainability pillar whitepaper.
- AWS Customer Carbon Footprint Tool documentation.
- AWS Sustainability — public commitments and Region-level renewable energy data.
- Green Software Foundation — vendor-neutral practices and the SCI (Software Carbon Intensity) specification.
- *Building Green Software* (Anne Currie, Sarah Hsu, Sara Bergman).
