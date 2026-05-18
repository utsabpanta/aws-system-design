# Parameter Store

> **One-line summary.** Managed configuration and (optionally KMS-encrypted) secret store inside AWS Systems Manager. Free for the **Standard** tier; cheap and convenient for plain configuration.

## TL;DR
- The right place for **config** that doesn't need rotation — environment-style settings, feature flags, third-party-service URLs, IDs of dependent resources.
- **SecureString** parameters are KMS-encrypted; cheap-and-cheerful secret storage when rotation isn't needed.
- **Standard tier is free** (up to 10,000 parameters per account per Region, 4 KB each); **Advanced tier** raises limits to 100,000 parameters, 8 KB each, and adds parameter policies (TTL, notifications).
- **Hierarchical paths** (`/app/prod/db/host`) + **path-based access policies** scale better than flat names.
- For secrets that need rotation, cross-account / cross-Region replication, or fine-grained per-access audit, use **Secrets Manager**.

## When to use it
- Configuration (URLs, flags, IDs, region-specific values) shared across services.
- Non-rotated secrets where Secrets Manager pricing is overkill.
- Bootstrapping containers / Lambdas with config at startup.
- Resolving cross-stack references (a CDK output landed in Parameter Store for another stack to read).

## When NOT to use it
- Secrets requiring rotation, cross-account / cross-Region replication, or per-call audit — use **Secrets Manager**.
- Very large configuration blobs > 8 KB — store in **S3** with a Parameter Store entry pointing to it.
- Anything that needs strong consistency across concurrent writers — Parameter Store is eventually-consistent across the rare same-name same-second writes.

## Key concepts

**Parameter.** A named value with optional description, tier (Standard / Advanced), and type (`String`, `StringList`, `SecureString`).

**Hierarchy.** Names are paths (`/app/prod/db/host`, `/app/prod/db/password`). The `/`-separated structure enables:
- **Get-by-path** (`GetParametersByPath('/app/prod/', recursive=true)`) — fetch a whole subtree.
- **Path-based IAM** (`Resource: arn:aws:ssm:*:*:parameter/app/prod/*`).

**Tiers:**
- **Standard** — free, 4 KB value, 10,000 parameters per account per Region.
- **Advanced** — per-parameter monthly fee, 8 KB value, 100,000 parameters, supports parameter policies (expiration, notification of upcoming expiration, no-change notification).

**SecureString.** KMS-encrypted parameter. Default `aws/ssm` key (free) or customer-managed CMK. Decryption is opt-in on `GetParameter` (`WithDecryption=true`); IAM can authorize `ssm:GetParameter` without `kms:Decrypt` to give "is the key here" access without exposing the value.

**Cross-account.** Not supported natively. Workaround: each account has its own parameter, populated by a cross-account replication mechanism (Lambda, CloudFormation StackSets).

**Cross-Region.** Not built-in. Replicate at the application / IaC layer.

**Versioning.** Every update creates a new version; you can reference a specific version (`/app/prod/db/host:5`) or the latest.

**Parameter policies (Advanced tier only).**
- **Expiration** — auto-delete after a timestamp.
- **ExpirationNotification** — EventBridge event before expiration.
- **NoChangeNotification** — alert if parameter hasn't changed in N days.

**Lambda Parameters & Secrets extension.** Same managed Lambda layer as Secrets Manager — caches Parameter Store reads in the function's local memory.

**Integration.** Used as integration points by ECS task definitions (`secrets` field), CodeBuild, CloudFormation (`{{resolve:ssm:...}}`), CDK, almost every IaC tool.

## Pricing model

- **Standard tier**: free for storage; standard / advanced API throughput tier pricing applies above the included free request rate.
- **Advanced tier**: per parameter per month + slightly more per request.
- **Higher Throughput** mode (opt-in): higher transaction-per-second limits, billed per-request.
- **KMS calls** for SecureString — usually within the KMS 20K monthly free tier unless used at high frequency.

Parameter Store is almost free for typical use. Standard tier is the default starting point.

## Quotas & limits

- **Parameters per account per Region**: 10,000 (Standard) / 100,000 (Advanced).
- **Parameter size**: 4 KB (Standard) / 8 KB (Advanced).
- **API rate** (Standard throughput): 40 TPS per account; Higher Throughput mode raises to 1,000 TPS.
- **Versions per parameter**: 100.

## Common pitfalls

- **Using Parameter Store as a high-rate runtime data store.** Default 40 TPS will throttle a serverless fleet on cold start. Enable Higher Throughput, use the Lambda extension to cache, or just put high-rate data in DynamoDB.
- **Flat parameter names.** `db_host_prod`, `db_host_staging` — doesn't scale and prevents path-based IAM. Use `/<app>/<env>/<service>/<key>` paths.
- **SecureString without IAM on KMS.** Authorizing `ssm:GetParameter WithDecryption=true` also requires `kms:Decrypt` on the encryption key. Misalignment shows up as opaque permission errors.
- **Storing large config blobs.** > 8 KB doesn't fit; chunking is awkward. Store the blob in S3 and put the S3 key in Parameter Store.
- **Treating Parameter Store as cross-account.** It isn't. Plan to replicate per-account or use a higher-level mechanism.
- **No client-side caching.** Hitting Parameter Store on every request burns API quota and adds latency. Use the Parameters & Secrets extension (Lambda) or cache in your container's memory with a TTL.
- **Versioning ignored.** New parameter values land as a new version, but consumers still resolve `latest` — a typo / bad update propagates immediately. Pin versions in deployment manifests when you need strict change control.

## Pairs well with
- [Secrets Manager](secrets-manager.md) — for secrets that need rotation / cross-account / cross-Region.
- [KMS](kms.md) — encryption for SecureString.
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md) — workload consumers.
- **Systems Manager Run Command / Automation** — consume parameters in operational workflows.
- **AppConfig** — for feature flags and runtime config with safer rollout (validation, gradual deployment).

## Pairs well with these repo pages
- [Secrets Manager](secrets-manager.md), [KMS](kms.md).

## Further reading
- [Parameter Store documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).
- [Standard vs Advanced parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html).
- [Parameter policies](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-policies.html).
- [Lambda Parameters & Secrets extension](https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html).
- [Parameter Store pricing](https://aws.amazon.com/systems-manager/pricing/) (under Systems Manager).
