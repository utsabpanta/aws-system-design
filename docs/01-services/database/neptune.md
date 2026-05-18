# Neptune

> **One-line summary.** Managed graph database. Supports the property graph model (Gremlin / openCypher) and the RDF/SPARQL model. Two flavors: **Neptune** (OLTP-style graph queries) and **Neptune Analytics** (in-memory analytics + vector search for GraphRAG).

## TL;DR
- The right answer for workloads that are graph-shaped: relationships matter as much as the entities. Fraud detection, recommendation, knowledge graphs, social graphs, identity graphs.
- **Neptune** is the long-running, transactional cluster — like RDS, but for graphs. Up to 15 read replicas, multi-AZ storage, point-in-time recovery.
- **Neptune Analytics** is the newer in-memory sibling, optimized for graph algorithms and **vector similarity search**. The standard primitive for **GraphRAG** in 2026.
- Don't reach for a graph DB because relational JOINs are slow — most JOINs are still better in PostgreSQL with indexes. Use Neptune when the queries are fundamentally graph traversals (variable-depth paths, transitive closure, pattern matching).

## When to use it
- **Fraud / risk** — entity-resolution patterns ("does this transaction connect to a known bad actor through k hops?").
- **Recommendations / personalization** — collaborative filtering over user-item graphs, "users who bought X also bought Y" with constraints.
- **Knowledge graphs** for search, customer 360, drug discovery.
- **Identity graphs** — stitching device, customer, and account identifiers across sources.
- **GraphRAG** — combining graph structure with LLM retrieval (Neptune Analytics with vector indexes).
- **Network / IT topology** modeling and queries.

## When NOT to use it
- Tabular / aggregational workloads — use SQL (RDS / Aurora / Redshift) or DynamoDB.
- Workloads where "graphs" is being overfit to relational data — most "we have relationships" data is fine in PostgreSQL with foreign keys and recursive CTEs.
- Search workloads — OpenSearch.
- Workloads needing horizontal write scale across many writers — Neptune is single-writer (like Aurora).

## Key concepts

### Neptune
**Cluster.** One writer + up to 15 readers, sharing a distributed storage layer (similar architecture to Aurora). Multi-AZ by default for storage; provision readers in multiple AZs for compute HA.

**Query languages.**
- **Property graph:** **Gremlin** (Apache TinkerPop) and **openCypher** (the Neo4j-originated standard).
- **RDF:** **SPARQL** (W3C standard).

The same cluster supports all three — you store data once and query in either model that fits the question (with the catch that the data models aren't fully interchangeable).

**Loader.** Bulk loader pulls CSV / RDF data from S3 into the cluster at high speed — the right way to seed large graphs.

**Backups.** Continuous backups to S3, PITR within retention. AWS Backup integration for cross-Region / cross-account / vault-locked retention.

**Notebooks.** Managed Jupyter integration for exploring graphs.

**Streams.** Change-log of vertex and edge changes for downstream sync (analytics, search).

### Neptune Analytics
A separate service, not a Neptune cluster mode. Loads graph data into memory for fast analytics: graph algorithms (PageRank, community detection, shortest path) and **vector similarity search** (HNSW index on node embeddings).

**One vector index per graph**, dimension 1–65,535, set at graph creation.

The primary 2026 use case is **GraphRAG**: store a knowledge graph in Neptune Analytics, embed entities with an LLM, and query "find entities semantically similar to X *and* within 2 hops of Y." Used heavily for enterprise search, recommendation, and LLM-augmented retrieval.

## Pricing model

### Neptune (OLTP)
- **Instance** — per second by class. RIs available.
- **Storage** — per GB-month of actual graph storage.
- **I/O** — per million requests against storage.
- **Backup storage** — included up to 100% of cluster size.
- **Data transfer** — same AWS rules.

### Neptune Analytics
- **m-NCU (memory Neptune Capacity Unit)** — per hour, sized for the in-memory graph.
- **Storage** — per GB-month of persisted graph snapshots.
- **Vector index** — pricing differs; vector search adds memory pressure.

Neptune Analytics is meaningfully more expensive per GB than Neptune for steady workloads — it's an analytics tier, not a primary database.

## Quotas & limits

- **Neptune readers per cluster**: 15.
- **Max cluster storage**: 128 TiB.
- **Neptune Analytics graph**: one vector index per graph, dimension up to 65,535; can only create the vector index at graph creation time.
- **Concurrent queries**: instance-class dependent.
- **Loader job concurrency**: bounded; queue up jobs for very large loads.

## Common pitfalls

- **Reaching for Neptune for "relational data with relationships."** Foreign keys in PostgreSQL handle most "relationships" just fine. Use Neptune when the queries are graph traversals (variable-depth, pattern-matching, transitive).
- **Loading data via single-row writes.** Use the Bulk Loader from S3 for anything > a few MB — orders of magnitude faster than streaming inserts.
- **Single-AZ cluster compute.** Provision at least one reader in another AZ for compute HA; storage is already multi-AZ.
- **Gremlin in production without query timeouts.** Unbounded variable-depth traversals can spend minutes burning CPU. Always cap depth and set query timeouts.
- **No back-of-the-envelope graph size estimation.** A "small graph" with hundreds of millions of edges quickly exceeds the smallest Neptune instance memory; choose instance class with the working set in mind.
- **Vector index on Neptune Analytics added later.** The vector index can only be created at graph creation — plan for it upfront if you need it.
- **Treating Neptune Analytics as a replacement for Neptune.** It's for read-heavy analytics; data still typically originates in Neptune (or an ETL pipeline) and gets loaded into Neptune Analytics for queries.

## Pairs well with
- **Amazon Bedrock + Neptune Analytics vector search** — the GraphRAG pattern.
- **AWS DMS** — bulk load from other databases.
- **S3 + Neptune Loader** — bulk import.
- **Neptune Streams** — change-log to downstream OpenSearch, analytics, or sync.
- **Notebooks (Jupyter)** — managed graph exploration.

## Pairs well with these repo pages
- [DynamoDB](dynamodb.md) — when the access pattern is "key lookup" not "traversal."
- [OpenSearch] (in [`analytics/`](../analytics/), forthcoming) — for full-text and document search.
- `docs/04-reference-architectures/genai-rag-bedrock.md` (forthcoming) — GraphRAG with Neptune Analytics.

## Further reading
- [Amazon Neptune documentation](https://docs.aws.amazon.com/neptune/).
- [Neptune Analytics documentation](https://docs.aws.amazon.com/neptune-analytics/).
- [Vector indexing in Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/vector-index.html).
- [GraphRAG with Neptune Analytics](https://aws.amazon.com/blogs/database/the-role-of-vector-datastores-in-generative-ai-applications/).
- [Property graphs vs RDF on Neptune](https://docs.aws.amazon.com/neptune/latest/userguide/feature-overview-data-model.html).
