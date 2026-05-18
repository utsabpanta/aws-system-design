# CloudHSM

> **One-line summary.** Dedicated, single-tenant **FIPS 140-2 Level 3** HSMs in your VPC. You hold the keys; AWS holds the rack.

## TL;DR
- For workloads where regulatory or contractual rules require **single-tenant HSMs you control**, with key material that *never* leaves the HSM under any circumstance.
- Standard interfaces (PKCS#11, OpenSSL engine, JCE, KMIP) — your existing on-prem HSM integrations mostly port directly.
- Significantly more expensive and more operationally complex than **KMS**. Use it only when the compliance requirement explicitly calls for "customer-managed HSM" (e.g., specific HIPAA / PCI / payment-processing scenarios, certain governmental rules).
- KMS can be configured to **use a CloudHSM cluster as its key store** — gives you the KMS API surface (so AWS services that "encrypt with KMS" transparently use your HSM) while you retain hardware key material control.
- Two big "no" defaults: don't reach for CloudHSM as the default; don't use it when KMS satisfies the same compliance bar.

## When to use it
- Compliance regimes that explicitly require single-tenant HSMs you fully control.
- Payment HSM workloads (issuer / acquirer card workloads) where standard CloudHSM mode is used alongside specialized PCI HSM products.
- Code-signing or document-signing keys where you need a verifiable hardware boundary independent of AWS staff access.
- Hybrid scenarios where you already operate Thales / nCipher / SafeNet HSMs on-prem and want a consistent operating model in AWS.

## When NOT to use it
- "We want encryption" — that's **KMS**.
- "We want our application secrets safer" — that's **Secrets Manager** / **Parameter Store** (which use KMS).
- Workloads with low key usage and modest compliance asks — KMS is cheaper and far simpler.
- Customer-facing TLS termination — use **ACM** (with private keys held by AWS) or, if you must use your own HSM, do so on a small, scoped EC2 fleet rather than asking CloudHSM to terminate the connection directly.

## Key concepts

**Cluster.** A logical group of HSMs spread across AZs. Members of the cluster auto-sync key material. Right shape: 2+ HSMs across 2+ AZs.

**HSM (instance).** A physical FIPS 140-2 Level 3 device. Lives in an AWS data center; the network interface lands in your VPC.

**Cluster certificate and Customer Trust Anchor.** When you initialize a cluster, you sign the cluster certificate with your own CA. AWS can't read or extract the key material — and the trust chain is rooted in you, not AWS.

**Crypto Officer (CO), Crypto User (CU), Appliance User (AU).** Role-based access on the HSM itself. Different from IAM — these are HSM-local credentials managed via the CloudHSM CLI / SDK.

**Client SDK / PKCS#11 / OpenSSL engine / JCE / KMIP.** Standard interfaces; applications use them like any other on-prem HSM.

**Backups.** Automatic, encrypted with a key tied to your cluster. Restorable only into your cluster (AWS staff can't restore them elsewhere).

**Cross-Region.** Not built-in; you back up and restore into a new cluster in another Region for DR.

**KMS Custom Key Store on CloudHSM.** You can create a KMS key whose material lives in your CloudHSM cluster. AWS services that "encrypt with KMS" (S3, EBS, RDS, etc.) transparently use the HSM. Combines KMS's developer experience with HSM key custody.

## Pricing model

- **Per-HSM-hour** — flat hourly fee per active HSM in the cluster. **Multiple HSMs for HA** multiply this directly. The fees are significant — usually multiple thousands of dollars/month for an HA cluster.
- **Backups** — included.
- **Data transfer** — same AWS rules.

There is no "free tier" or "scale to zero" mode. A CloudHSM cluster is always-on infrastructure.

## Quotas & limits

- **HSMs per cluster**: up to 28.
- **Clusters per account per Region**: 4 default (raisable).
- **Throughput** — varies with operation; payment / signing workloads especially throttle on asymmetric ops.
- **Key storage per HSM** — bounded; check current spec.

## Common pitfalls

- **Picking CloudHSM as the default.** Almost no workload genuinely needs it. KMS satisfies most compliance regimes. Only adopt CloudHSM after a compliance / legal review concludes it's required.
- **One HSM in one AZ.** No HA. The right starting point is 2 HSMs in 2 AZs at minimum.
- **No backup-restore drill.** Restoring a CloudHSM cluster from backups in a new Region is a non-trivial procedure. Run a DR drill; don't discover the gaps during an incident.
- **No HSM-local credential management plan.** Crypto Officer credentials lost = cluster reset = key material lost forever. Treat them like break-glass: hardware tokens, sealed envelopes, multi-person.
- **Treating CloudHSM as KMS.** Most AWS services don't speak PKCS#11 directly. To get them to use your HSM transparently, use the **KMS Custom Key Store on CloudHSM** integration.
- **No connection-pooling in the client SDK.** Per-request HSM session setup is expensive. Use connection pooling.
- **Ignoring throughput limits for HSM-bound workloads.** Some workloads (payment authorization) burn HSM throughput quickly. Size the cluster for peak, not average.

## Pairs well with
- [KMS](kms.md) — KMS Custom Key Store can layer KMS API onto your HSM.
- **PKCS#11 / JCE / OpenSSL engine** — standard library integrations.
- **CloudWatch** — HSM health and throughput metrics.
- **AWS Direct Connect** — predictable network path to the HSM cluster for hybrid scenarios.

## Pairs well with these repo pages
- [KMS](kms.md) — the cheaper, simpler default for almost all encryption needs.
- [Security pillar](../../05-well-architected/security.md).

## Further reading
- [AWS CloudHSM documentation](https://docs.aws.amazon.com/cloudhsm/).
- [CloudHSM cluster overview](https://docs.aws.amazon.com/cloudhsm/latest/userguide/clusters.html).
- [KMS Custom Key Store with CloudHSM](https://docs.aws.amazon.com/kms/latest/developerguide/keystore-cloudhsm.html).
- [CloudHSM SDK and client tools](https://docs.aws.amazon.com/cloudhsm/latest/userguide/sdks.html).
