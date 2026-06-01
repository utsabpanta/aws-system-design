# Snow Family

> **One-line summary.** Physical devices shipped to your location for offline data transfer and edge compute. In 2026 this is essentially **Snowball Edge** — Snowmobile and Snowcone have been retired.

## Status

> ⚠️ **Snow Family has been shrinking:**
>
> - **AWS Snowmobile** — the 100-PB shipping-container truck — **retired in April 2024**. No longer offered.
> - **AWS Snowcone** — the smallest device (8 TB) — **discontinued November 12, 2024**. No new orders accepted; both new and existing customers can no longer order Snowcone devices.
> - **AWS Snowball Edge** — **still active**. The remaining Snow Family product, available in storage-optimized and compute-optimized configurations.
>
> **Migration / alternatives:**
>
> - Most online data transfer needs are better served by **AWS DataSync** (which AWS now recommends for the use cases previously served by Snowmobile and Snowcone).
> - Snowball Edge still applies for genuinely offline / bandwidth-constrained scenarios.

## TL;DR

- Ship Snowball Edge devices to remote / disconnected sites; load data locally; ship them back to AWS where the data is ingested into S3.
- Useful for **one-time large data migrations from disconnected environments** (research sites, oil rigs, ships, military, factories with poor internet) and for **edge compute in disconnected scenarios** (run EC2 / Greengrass on the Snowball Edge).
- Two flavors: **Storage Optimized** (high storage, modest compute) and **Compute Optimized** (more compute, less storage; optional GPU for ML inference at the edge).
- For typical "we have a lot of data to move to AWS" scenarios with internet connectivity, **DataSync** is usually faster, cheaper, and operationally simpler.

## When to use it (Snowball Edge)

- One-time large data migrations from sites with poor / no internet (TB to PB range).
- Disaster-recovery scenarios where physical shipping is the only practical path.
- Edge compute in disconnected or intermittent environments (oil rigs, ships, remote research).
- Government / military / regulated environments requiring physical custody of devices.
- Pre-cloud-onboarding of large datasets where shipping disks beats months of internet transfer.

## When NOT to use it

- Sites with reasonable internet — **DataSync** ingests faster and with less operational overhead.
- Continuous data movement between on-prem and AWS — **DataSync** or **Storage Gateway**.
- Tiny migrations — direct upload to S3 is simpler.

## Key concepts

### Snowball Edge Storage Optimized

- High storage (~80 TB usable).
- Limited compute (a few EC2 instances locally).
- For data-heavy migrations.

### Snowball Edge Compute Optimized

- More compute (more vCPU, GPU options).
- Less storage.
- For edge compute scenarios (ML inference, video transcoding, data preprocessing at the edge before transit).

### Local AWS APIs

- **EC2 on Snowball Edge** — run AMIs locally (limited instance types).
- **S3 on Snowball Edge** — S3-compatible API for local data ingestion.
- **AWS IoT Greengrass** can run on the device.

### Workflow

1. Order a Snowball Edge via AWS console.
2. AWS ships the device.
3. Connect at your site, transfer data to it (via S3 API or NFS).
4. Ship back to AWS via prepaid label.
5. AWS ingests into a target S3 bucket in your account.

### Encryption

- All data encrypted at rest (KMS keys you control).
- Tamper-evident enclosures.
- TLS in transit between client and device.

### Service link (for compute scenarios)

Snowball Edge devices can register with AWS for management while at the edge — see EC2 / Greengrass console for status, push updates, etc. Requires connectivity; works in intermittent scenarios.

### Clustering

Multiple Snowball Edge devices can be clustered for higher availability of storage.

### Discontinued members

- **Snowmobile** — 100 PB shipping container truck. Retired April 2024 because smaller devices and improved DataSync covered the use case more practically.
- **Snowcone** — smallest Snow Family device (8 TB). Discontinued November 12, 2024.

## Pricing model

- **Per-device per-shipment** — flat fee per device per use.
- **Per-day fee** while you have the device on-site (after a free-use window).
- **Data transfer to S3 on return** — free.
- **Shipping** — included in pricing.

For large migrations the per-device-shipment cost is low relative to the data moved; for repeated small shipments it adds up.

## Quotas & limits

- **Devices per order**: bounded; large orders coordinate with AWS.
- **Storage per Snowball Edge SO**: ~80 TB usable.
- **Concurrent jobs per account**: bounded.
- **Service availability**: most AWS commercial Regions support shipping.

## Common pitfalls

- **Snowball Edge for use cases DataSync handles better.** If internet is decent and the dataset is bounded, DataSync wins.
- **Underestimating shipping time.** Snowball Edge round-trip is days. For tight deadlines, plan accordingly or use online transfer.
- **No encryption-key plan.** Lost device with unrecoverable key = lost data. Have a key-management policy.
- **Single device for HA edge compute.** Cluster multiple devices.
- **Bringing data back into an unencrypted S3 bucket.** Ingestion lands in S3 with whatever encryption policy the bucket has. Use SSE-KMS by default.
- **Returning the device late.** Per-day fees accumulate after the free window.
- **Assuming Snowmobile / Snowcone are still options.** They're not. Snowball Edge is the only Snow product available for new orders.

## Pairs well with

- [S3](../storage/s3.md) — destination of returned data.
- **AWS DataSync** — the online alternative for the same use cases when internet is sufficient.
- [IoT Greengrass](iot-greengrass.md) — edge runtime that can run on Snowball Edge Compute Optimized.
- [EC2](../compute/ec2.md) — Snowball Edge runs EC2 instances locally.
- [Storage Gateway](../storage/storage-gateway.md) — for ongoing hybrid storage instead of one-off migration.

## Pairs well with these repo pages

- [S3](../storage/s3.md), [Storage Gateway](../storage/storage-gateway.md), [IoT Greengrass](iot-greengrass.md).
- [Migration & Transfer category](../migration-transfer/) — DataSync, MGN, DMS, etc.

## Further reading

- [AWS Snow Family documentation](https://docs.aws.amazon.com/snowball/).
- [AWS Snow device updates (including Snowmobile / Snowcone retirements)](https://aws.amazon.com/blogs/storage/aws-snow-device-updates/).
- [Snowball Edge specs](https://aws.amazon.com/snowball-edge/features/).
- [Snowball Edge vs DataSync](https://aws.amazon.com/datasync/).
- [Snowball Edge pricing](https://aws.amazon.com/snowball/pricing/).
