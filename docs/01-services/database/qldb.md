# QLDB (Quantum Ledger Database)

> **One-line summary.** AWS's purpose-built immutable, cryptographically verifiable ledger database. **Retired by AWS as of July 31, 2025.**

## Status

> 🛑 **Amazon QLDB was retired on July 31, 2025.** No new clusters can be created; existing clusters are no longer supported. AWS published migration guidance pointing to **Amazon Aurora PostgreSQL** (using extensions to recreate the ledger semantics) as the recommended successor on AWS. Third-party alternatives include **Azure SQL ledger** and **ScalarDL**.
>
> This page exists for historical / migration reference. If you're starting a new ledger workload, do not pick QLDB — jump to [`aurora.md`](aurora.md) and read the migration notes below.

## TL;DR

- QLDB was a managed, immutable, append-only, cryptographically verifiable ledger database — a journal of every change, hashed into a Merkle tree the application could verify.
- AWS retired the service in July 2025 with relatively short notice; the recommended migration target is Aurora PostgreSQL with extensions that emulate ledger behavior.
- For new workloads, evaluate Aurora PostgreSQL with journal/history extensions, **DynamoDB with Streams + an append-only audit table**, or third-party ledger products.
- The lesson: AWS-specific specialty services can retire on short notice. Prefer broader primitives (relational, KV, object) for long-term workloads unless the specialty really is required.

## What it was

QLDB stored data as a series of **immutable** revisions in a verifiable journal. Each transaction was hashed and chained, producing a digest you could publish or verify against — useful when you needed to prove "this record was not tampered with between time T1 and T2."

Used cases included:

- Financial ledgers and reconciliations.
- Supply chain provenance.
- Cryptographically verifiable audit logs.
- Healthcare and HR data with strong tamper-evidence requirements.

QLDB used a SQL-like query language called **PartiQL**.

## Migration path

AWS's recommended migration target is **Amazon Aurora PostgreSQL**, using:

- A schema that captures the journal pattern (per-record history table, version column, append-only inserts).
- A trigger or extension to compute the hash chain on each insert.
- An export pipeline (the AWS-published migration tooling: QLDB → S3 → DMS → Aurora PostgreSQL).

This gets you "a ledger-like store" on a supported, mainstream database, but you lose the QLDB-managed cryptographic verification primitive — your application becomes responsible for computing and publishing digests, and for verifying them on read.

For workloads where the cryptographic verification was the load-bearing feature, evaluate:

- **Aurora PostgreSQL** with `pgcrypto` and an app-level digest publication scheme.
- **DynamoDB Streams** to an append-only audit table with KMS-signed hash chains.
- Third-party / open-source ledger products (Azure SQL ledger, ScalarDL, blockchain primitives if the verification has to involve external parties).

## Lessons for future workloads on AWS

QLDB's retirement is the highest-profile AWS service shutdown in recent memory. A few principles that came out of it:

- **Be careful about building on specialty AWS services with no obvious replacement.** Ledger semantics on top of QLDB had no first-party alternative; teams had to roll their own.
- **Prefer broad primitives (relational, KV, object) for long-term workloads.** They aren't going anywhere; they may not be the cheapest at a given scale, but they're the safest bet for multi-year systems.
- **Maintain an exit plan for every specialty service.** "How would we migrate off of X in six months if we had to?" — answer it before you commit.
- **Watch for AWS service deprecation announcements.** Subscribe to AWS service blogs / [the unofficial AWS breaking-changes tracker](https://github.com/SummitRoute/aws_breaking_changes); track the retirement page in service documentation.

## Pairs well with these repo pages

- [Aurora](aurora.md) — the AWS-recommended migration target.
- [DynamoDB](dynamodb.md) — if rebuilding the audit primitive from scratch, often the right substrate.
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md) — service-deprecation watching is an operations practice.

## Further reading

- AWS service documentation (legacy): historical QLDB docs may still be online for migration reference.
- [AWS migration guidance: QLDB → Aurora PostgreSQL](https://aws.amazon.com/blogs/database/migrate-an-amazon-qldb-ledger-to-amazon-aurora-postgresql/).
- ["AWS Discontinues Amazon Quantum Ledger Database (QLDB)" — InfoQ](https://www.infoq.com/news/2024/07/aws-kill-qldb/).
- [Hacker News discussion of the announcement](https://news.ycombinator.com/item?id=41085736) — community reaction and migration discussions.
