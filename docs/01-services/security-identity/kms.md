# KMS (Key Management Service)

> **One-line summary.** Managed key storage and cryptographic operations. The encryption-at-rest substrate for nearly every other AWS service that encrypts your data.

## TL;DR
- Store and use cryptographic keys without ever handling raw key material. Almost every other AWS service ("encrypt with KMS") uses KMS under the hood.
- Three key types: **AWS-owned** (free, AWS-managed, you don't see them), **AWS-managed** (per-service `aws/<service>` keys, free), and **customer-managed (CMK)** (you control policy, rotation, grants — billed monthly + per use).
- The big architectural lever: **one CMK per data classification / domain, not one per resource.** A KMS key sprawl problem destroys grant management and observability.
- Cross-account encryption via key policies + IAM. **Multi-Region keys** replicate the same key material across Regions for transparent cross-Region access (KMS does the replication for you).
- KMS calls have per-request charges and modest rate limits (in the low thousands per second per key); high-volume workloads should use **envelope encryption** with KMS-generated data keys rather than calling `Encrypt` / `Decrypt` per request.

## When to use it
- Almost every AWS workload — every "encrypt with KMS" toggle on every service.
- Application-level encryption (envelope-encrypted data, JWE, signed JWTs with KMS-asymmetric keys).
- Cross-account key sharing for data shared across an Organization.
- HMAC, sign/verify, and (since the last few years) **asymmetric keys** (RSA, ECC) for digital signatures and key wrapping.

## When NOT to use it
- Storage of long secrets like API keys, passwords — those go in **Secrets Manager** (or Parameter Store SecureString). KMS encrypts *for* those services.
- TLS private keys for ALB / CloudFront — use **ACM**.
- Hardware-tied keys for FIPS 140-2 Level 3 compliance scenarios that require single-tenant HSMs — use **CloudHSM**.

## Key concepts

**KMS key (KMS-CMK).** A logical key with a key ID, ARN, alias (optional, recommended), description, key policy, and grants. Material lives on FIPS 140-2 Level 3 HSMs in the Region.

**Key types:**
- **Symmetric** (AES-256-GCM under the hood) — the default; used for envelope encryption and most `Encrypt`/`Decrypt` flows.
- **Asymmetric RSA / ECC** — sign/verify, encrypt/decrypt (RSA), key agreement (ECC).
- **HMAC** — generate/verify HMAC tags.

**Symmetric key usage modes:**
- **Encrypt / Decrypt** — direct, for small payloads (< 4 KB).
- **Generate Data Key** — KMS returns a plaintext data key + an encrypted-by-KMS-CMK copy. App encrypts data with the plaintext key, stores the encrypted-key alongside, discards the plaintext key. **The right pattern for any meaningful data volume — KMS isn't called per object decrypt for years of stored data.**

**Key origin:**
- **AWS_KMS** — KMS generates and holds the material.
- **EXTERNAL** — you import material (e.g., HSM-generated externally). Imported keys expire; you must re-import.
- **AWS_CLOUDHSM** — material lives in a CloudHSM cluster you own.
- **EXTERNAL_KEY_STORE (XKS)** — material in an HSM outside AWS, KMS proxies requests to it. For sovereignty / data-residency mandates.

**Key policies.** Resource-based JSON on the key. Must grant `kms:*` to your account root for emergency recovery; otherwise scope per-IAM-principal.

**Grants.** Lightweight, programmatic permissions on a key, often issued by an AWS service on your behalf (RDS, Lambda) — narrow scope, automatic expiration.

**Aliases.** `alias/payments-prod` instead of a UUID ARN. Aliases can be re-pointed to a different key as part of rotation or migration without changing app code.

**Rotation.** Toggle automatic yearly rotation on symmetric KMS-managed CMKs. The alias keeps pointing to the same logical key; KMS retains old key material for decrypting old ciphertexts. Manual rotation requires app-level re-encryption.

**Multi-Region keys.** Replicate the same KMS-CMK across Regions (each replica has its own ARN but shares material). Ciphertext encrypted in one Region decrypts in another without re-encryption.

**CloudTrail integration.** Every KMS operation logged. Essential for any incident response on encrypted data.

## Pricing model

- **Per CMK per month** — ~$1 / key / month for KMS-managed CMKs. Multi-Region replicas billed per replica.
- **Per API request** — ~$0.03 per 10,000 requests (symmetric); asymmetric ops are more expensive.
- **Free tier** — first 20,000 requests / month free.
- **AWS-managed keys** (`aws/<service>`) — free, no monthly fee.
- **External key store (XKS)** — additional per-request fee.

The economic reason envelope encryption matters: a high-volume workload that calls `Decrypt` per request can pay thousands per month for KMS calls. Generating one data key and encrypting many objects with it brings that to single-digit dollars.

## Quotas & limits

- **CMKs per account per Region**: 100,000.
- **Aliases per account per Region**: 10,000.
- **Symmetric cryptographic operations per second** (per CMK): 5,500 – 50,000 depending on the operation and Region; raisable for some classes.
- **Asymmetric operations** are lower; verify per Region.
- **`Decrypt` is the most-throttled** — envelope encryption avoids per-decrypt calls.
- **Cross-Region replica creation**: small per-request fee.

## Common pitfalls

- **One CMK per resource.** Hundreds of keys, impossible-to-audit grants. Use one CMK per data classification or per domain.
- **`Decrypt` per request without envelope encryption.** Hits KMS rate limits and runs up the bill. Envelope encryption is the right pattern at any meaningful scale.
- **Cross-account sharing without key-policy access.** Identity-based policy in account B isn't enough; the key policy in account A must allow account B (or B's roles).
- **`kms:*` to everyone "for compatibility."** Equivalent to giving them encrypt-anything access. Scope per action and per principal.
- **No alias.** Keys identified by UUID ARN in code makes rotation / replacement painful. Always use aliases.
- **Rotation off on long-lived keys.** Enable automatic annual rotation on symmetric CMKs; KMS handles old-ciphertext decryption transparently.
- **Multi-Region key for everything.** They cost more than single-Region; only use for data that's actually accessed cross-Region or for DR scenarios.
- **Leaving the default AWS-managed key for sensitive data.** AWS-managed keys (`aws/s3`, etc.) can't be customized; you can't audit specific access narrowly. Move to a CMK when control matters.
- **Forgetting that KMS calls show up in CloudTrail.** That's a feature, not a bug — investigate suspicious `Decrypt` calls on sensitive keys.

## Pairs well with
- [S3](../storage/s3.md), [EBS](../storage/ebs.md), [RDS](../database/rds.md), [DynamoDB](../database/dynamodb.md) — all use KMS for at-rest encryption.
- [Secrets Manager](secrets-manager.md), [Parameter Store](parameter-store.md) — encrypted with KMS.
- [CloudHSM](cloudhsm.md) — KMS XKS or `AWS_CLOUDHSM` origin can use HSMs you operate.
- **AWS CloudTrail** — KMS calls are logged for audit.
- **IAM Access Analyzer** — surfaces cross-account access through key policies.

## Pairs well with these repo pages
- [Security pillar](../../05-well-architected/security.md) — "encrypt everything in transit and at rest."

## Further reading
- [AWS KMS documentation](https://docs.aws.amazon.com/kms/).
- [KMS concepts: keys, aliases, grants, key policies](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html).
- [Envelope encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping).
- [Multi-Region keys](https://docs.aws.amazon.com/kms/latest/developerguide/multi-region-keys-overview.html).
- [External key stores (XKS)](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-external.html).
