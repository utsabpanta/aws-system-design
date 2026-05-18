# Secrets Manager

> **One-line summary.** Managed storage and rotation of secrets — database passwords, API keys, OAuth tokens, third-party credentials. KMS-encrypted, IAM-controlled, optionally rotated by Lambda.

## TL;DR
- The right place for secrets that need **rotation** or that are **sensitive enough to want explicit IAM-controlled access and audit per access**.
- For mere config that *happens* to be sensitive (a non-rotated API key, an env-style value), **Parameter Store SecureString** is usually cheaper and sufficient.
- Built-in rotation for RDS / Aurora / RDS Proxy / DocumentDB / Redshift / ElastiCache; custom rotation via Lambda for anything else.
- Cross-account / cross-Region replication is first-class — share secrets across accounts via resource policy, replicate to other Regions for DR.
- Costs more than Parameter Store per secret per month, but the rotation, audit, and cross-account / cross-Region features justify it for the secrets that matter.

## When to use it
- Database credentials (especially with managed rotation via RDS / Aurora).
- API keys / tokens for third-party services where rotation is a real requirement.
- OAuth client secrets.
- TLS private keys that aren't fronted by ACM.
- Any secret you want CloudTrail-logged on every access.

## When NOT to use it
- Plain configuration that isn't sensitive — Parameter Store String (free).
- Sensitive config with no rotation need — Parameter Store SecureString (cheaper).
- TLS certs for ALB / CloudFront — use ACM.
- Long-lived AWS access keys — workloads should use **IAM roles + STS**, not a secret.

## Key concepts

**Secret.** Versioned. Each `PutSecretValue` creates a new version. Stages (`AWSCURRENT`, `AWSPENDING`, `AWSPREVIOUS`) point to specific versions; the rotation Lambda manipulates stage labels.

**Encryption.** KMS-encrypted at rest. Default `aws/secretsmanager` key (free) or a customer-managed CMK.

**Resource policy.** Resource-based policy on the secret. The mechanism for cross-account access (account B can read the secret created in account A if both the secret's resource policy *and* B's IAM policy allow it).

**Rotation.**
- **Managed rotation** for supported AWS databases (RDS PostgreSQL/MySQL/SQL Server/Oracle/MariaDB/Db2, Aurora, DocumentDB, Redshift, ElastiCache). No Lambda for you to write.
- **Custom rotation** via a Lambda function with four steps (`createSecret`, `setSecret`, `testSecret`, `finishSecret`).
- Rotation can be scheduled (every N days / hours) or triggered manually.

**Replication.** Cross-Region replication of a secret to other Regions. Updates propagate. Useful for multi-Region apps and DR.

**Caching.** AWS SDKs include client-side caching (the Secrets Manager Caching Client) to avoid re-fetching the same secret on every call. Combined with Lambda extensions / sidecars for serverless caching.

**Lambda extension (Parameters and Secrets).** A managed Lambda layer that caches Secrets Manager / Parameter Store reads in the function's local memory, reducing per-invocation latency and cost.

**Hierarchical access via tags / paths.** Tag-based access policies (`secret:resource-tag/Env: prod`) let you scope access broadly without enumerating every secret.

## Pricing model

- **Per secret per month** — flat fee per stored secret.
- **Per API request** — small per-10,000 fee.
- **KMS calls** — usually free under the 20k-monthly-free-tier; custom CMKs charge per use.
- **Cross-Region replicas** — billed per replica per month.

Compared to Parameter Store SecureString, Secrets Manager is much more expensive per secret. Use it where the rotation / cross-account / cross-Region / audit features earn the premium.

## Quotas & limits

- **Secrets per account per Region**: 500,000 default.
- **Secret value size**: 64 KB.
- **API rate**: high (thousands per second per account).
- **Rotation Lambda timeout**: 15 min (standard Lambda max).

## Common pitfalls

- **Secrets Manager for plain config.** Parameter Store String is free; SecureString is cheap. Don't pay for what you don't use.
- **Hardcoding the latest version.** Always fetch `AWSCURRENT` unless you specifically need a version-pinned read; the rotation system manages stages for you.
- **No client-side caching.** Fetching on every request is slow and expensive. Use the SDK caching client or the Lambda Parameters & Secrets extension.
- **Rotation enabled without testing.** A broken rotation can leave you with a stale `AWSCURRENT` and clients failing to authenticate. Test in dev; monitor rotation success metric.
- **Cross-account access only via IAM, not resource policy.** Both ends must allow; missing the resource policy is the common failure mode.
- **Storing AWS access keys.** Workloads should use IAM roles + STS. The exception is third-party SaaS that needs a long-lived AWS key — even then, rotate aggressively.
- **Secret name reuse after deletion.** Deleted secrets enter a 7–30 day recovery window. Trying to create one with the same name during that window fails.
- **Multi-Region replication off for production secrets.** Region-outage scenarios leave the secret unreachable. Replicate critical secrets.

## Pairs well with
- [KMS](kms.md) — encryption layer.
- [RDS](../database/rds.md) / [Aurora](../database/aurora.md) — managed rotation.
- [Lambda](../compute/lambda.md) — custom rotation handlers; Parameters & Secrets extension for caching.
- **AWS Backup** — vault-locked retention for compliance.
- **IAM Access Analyzer** — surface cross-account access through secret resource policies.
- **CloudTrail** — every access logged.

## Pairs well with these repo pages
- [Parameter Store](parameter-store.md) — the cheaper alternative for non-rotated config.
- [Security pillar](../../05-well-architected/security.md).

## Further reading
- [AWS Secrets Manager documentation](https://docs.aws.amazon.com/secretsmanager/).
- [Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html).
- [Cross-account access to secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples_cross.html).
- [Lambda Parameters & Secrets extension](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html).
- [Secrets Manager pricing](https://aws.amazon.com/secrets-manager/pricing/).
