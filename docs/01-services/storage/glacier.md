# S3 Glacier tiers

> **One-line summary.** The archive end of the S3 storage class spectrum — three tiers trading retrieval latency and price for the cheapest durable storage AWS sells.

## TL;DR

- "Glacier" today is not a separate service; it's three S3 storage classes — **Instant Retrieval**, **Flexible Retrieval**, and **Deep Archive** — managed through normal S3 APIs and lifecycle policies.
- Same eleven-nines durability as S3 Standard. The difference is retrieval latency (ms → minutes → hours) and per-GB cost (~$0.004 → ~$0.00099 per GB-month at the Deep Archive end).
- Minimum storage durations and per-retrieval fees mean Glacier classes only make sense for **truly cold** data. Misuse can cost *more* than just leaving objects in Standard.
- The legacy "Amazon S3 Glacier" service (with vaults and the original Glacier API) still exists but is in maintenance — new workloads should use the S3 storage classes via the standard S3 API.
- For compliance / regulatory holds, combine with **S3 Object Lock** (Compliance mode) for true WORM that even the root account can't delete until the retention period expires.

## When to use it

- Long-term backups (RDS exports, application backups, on-prem tape replacements).
- Compliance and audit logs that must be kept for years but rarely read.
- Old log files that should outlive the warm-tier retention but might need to be queried under subpoena or investigation.
- Media archives, historical datasets, post-pipeline ML training data.
- Anywhere "we'll need it once a year, if that, but we have to keep it for seven years."

## When NOT to use it

- Data accessed more than ~once per quarter — Standard-IA or Intelligent-Tiering's automatic archive tier is usually cheaper.
- Small objects (< 128 KB minimum billable size) at scale — the per-object overhead dominates the storage cost.
- Workloads that need a guaranteed retrieval SLA in minutes — Flexible Retrieval is usually fast but not contractually guaranteed. Use Instant Retrieval if you need ms-scale.
- Data you might rewrite or version frequently — minimum storage duration penalties bite hard.

## Key concepts

The three tiers:

| Class | Retrieval latency | Min storage duration | Use case |
|---|---|---|---|
| **Glacier Instant Retrieval** | milliseconds | 90 days | Archive data needing immediate access. Cheaper than Standard-IA when access is < monthly. |
| **Glacier Flexible Retrieval** | Expedited (1–5 min), Standard (3–5 h), Bulk (5–12 h) | 90 days | Most cold archives. Three retrieval speed tiers with different prices. |
| **Glacier Deep Archive** | Standard (within 12 h), Bulk (within 48 h) | 180 days | Cheapest tier. The "tape replacement" tier — disaster archives, long-term compliance. |

**Retrieval modes (Flexible Retrieval and Deep Archive).** You initiate a restore job; AWS makes a temporary copy in S3 Standard for the duration you specify. Tier choices trade retrieval cost for retrieval time. **Provisioned capacity** for Expedited retrievals reserves capacity at additional cost — niche, used for predictable high-volume retrieval needs.

**Lifecycle transitions.** The normal way to land data in Glacier is a lifecycle policy on a regular S3 bucket: `Standard → Standard-IA after 30 days → Glacier Flexible Retrieval after 90 days → Glacier Deep Archive after 365 days → expire after 7 years`. Don't manually `PUT` objects to a Glacier class for typical workloads — let lifecycle do it.

**S3 Object Lock.** WORM retention. Two modes:

- **Governance** — admins with `s3:BypassGovernanceRetention` can override.
- **Compliance** — *no one*, including the root account, can delete until retention expires. Required for regulatory immutability (SEC 17a-4(f), FINRA, CFTC).

**Minimum billable size.** All Glacier tiers (and Standard-IA / One Zone-IA) bill at minimum **128 KB** per object regardless of actual size. A bucket of millions of tiny objects in Glacier is expensive *and* slow to retrieve.

**Retrieval fees.** All three Glacier classes charge per GB retrieved and per restore request. Deep Archive is the cheapest to store and the most expensive per retrieval — which is exactly why you put data there: you trust you'll rarely need it back.

**Legacy "S3 Glacier" service.** A separate, older API surface with vaults instead of buckets. Still works; not where new workloads should go. AWS recommends the S3 storage classes for everything new. Tape Gateway uses the legacy vault API under the hood for VTL volumes.

## Pricing model

- **Storage** — per GB-month. Roughly an order of magnitude cheaper from Standard → Standard-IA → Glacier Instant → Glacier Flexible → Glacier Deep Archive. Deep Archive sits in the single-digit $/TB/month range.
- **Retrieval requests** — per 1,000 (Glacier Instant) or per GB + per request (Flexible / Deep Archive). Expedited > Standard > Bulk in price.
- **Restore window** — when you restore from Flexible / Deep Archive, you specify how many days to keep the temporary copy in Standard. You pay Standard storage for that copy during the window.
- **Lifecycle transitions** — per 1,000 objects. Tiny-object workloads can pay more in transition fees than in storage savings.
- **Minimum storage duration** — early deletion (or transition out) charges the full duration's storage.

The whole-archive cost calculation:

```
total = (GB stored × $/GB-month × months) +
        (retrieval frequency × GB retrieved × $/GB) +
        (request count × $/1000 requests) +
        (lifecycle transition count × $/1000 transitions)
```

If retrieval is the dominant term, you've put the data in the wrong tier.

## Quotas & limits

- **Object size** — same as standard S3 (5 TB max).
- **Minimum billable size** — 128 KB per object across IA / Glacier classes.
- **Minimum storage duration** — 30 days (IA), 90 days (Glacier Instant / Flexible), 180 days (Deep Archive).
- **Provisioned retrieval capacity** — purchase in units; quota varies.
- **Restore concurrency** — high, but billing scales with the number of restore jobs.

## Common pitfalls

- **Tiny objects archived to Glacier.** A bucket of 1 KB objects pays the 128 KB minimum each *and* per-request retrieval fees. Aggregate first (`tar` / Parquet / zip) before lifecycle-transitioning.
- **Lifecycle-transitioning before the source class's minimum duration.** Standard-IA charges for 30 days minimum; moving objects to Glacier on day 5 still pays Standard-IA for 30 days *and* the transition. Use `min(NoncurrentDays, ObjectAge)` carefully.
- **Forgetting the restore window.** Restored copies in Standard auto-delete after the requested window. Re-restoring repeatedly is wasteful; size the window for your actual workflow.
- **Treating Glacier as a backup tool.** It's a storage class. You still need to engineer the backup (snapshot, dump, replicate) and the lifecycle policy that lands it in Glacier.
- **Deep Archive for data you'll need quickly.** "Within 12 h" is not "in 12 h" — restores complete asynchronously, and an incident at 2 AM can mean morning before you have the file.
- **Object Lock in Compliance mode by accident.** Compliance retention can't be removed by anyone for the retention duration. Test Governance mode first; only flip to Compliance for genuinely regulated data.
- **Skipping Object Lock for "important" archives.** Without it, a compromised root account can delete the archive. With Compliance mode, ransomware and rogue insiders can't.

## Pairs well with

- [S3](s3.md) — Glacier classes are part of the S3 storage class spectrum.
- **S3 lifecycle policies** — the right way to land data here.
- **S3 Object Lock** — WORM retention.
- **AWS Backup** — lands backups in cold storage with vault-level policies.
- **S3 Storage Lens** — visibility into how much storage sits in each class.
- **Athena** — queries archived data once restored, or directly on Glacier Instant Retrieval objects.

## Pairs well with these repo pages

- [Backup](backup.md) — managed backups that often land in cold storage.

## Further reading

- [S3 Storage Classes](https://aws.amazon.com/s3/storage-classes/).
- [S3 Glacier classes for archival](https://aws.amazon.com/s3/storage-classes/glacier/).
- [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html).
- [Lifecycle transition rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html).
- [Restoring archived objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects.html).
