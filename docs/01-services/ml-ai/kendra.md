# Kendra

> **One-line summary.** Managed enterprise search service with **semantic understanding**. Indexes documents from S3, SharePoint, Confluence, Salesforce, ServiceNow, databases, and 40+ other sources; returns high-accuracy ranked passages and direct answers, not just keyword matches.

## TL;DR
- The right service for **enterprise search** with natural-language queries — "How do I file an expense report?" returns the actual policy passage, not 50 keyword hits.
- **Kendra GenAI Enterprise Edition** combines hybrid search (lexical + semantic embeddings) with re-ranking models — currently the highest-accuracy AWS-managed retrieval option for RAG.
- **Connectors** for SharePoint, Confluence, Salesforce, ServiceNow, S3, RDS, Box, OneDrive, Slack, GitHub, Jira, and many more — including custom connectors via SDK.
- For greenfield RAG, **Bedrock Knowledge Bases** is the simpler starting point; **Kendra GenAI Index** is now a supported retriever inside Bedrock Knowledge Bases when you want Kendra's accuracy with Bedrock's orchestration.
- Premium pricing — Kendra is the most expensive AWS retrieval option. For small / cost-sensitive RAG, an OpenSearch / pgvector / Pinecone pairing is often cheaper.

## When to use it
- Internal enterprise search ("our employees can't find anything in our wiki").
- Customer support self-service search.
- High-accuracy RAG retrieval (as a retriever inside Bedrock Knowledge Bases).
- Document search in regulated environments (legal, healthcare, finance).
- Replacing keyword-based search (Elasticsearch / OpenSearch with default tokenizers) with semantic search.

## When NOT to use it
- Tiny content corpora — pricing doesn't amortize.
- Tasks where vector-only retrieval is sufficient — pgvector / OpenSearch k-NN / Pinecone is cheaper.
- Open-data / public-content search — open-source search engines often suffice.
- High-throughput consumer-facing search at very large scale where a custom index is cost-justified.

## Key concepts

### Editions
- **Kendra Developer Edition** — cheaper tier; capped storage / queries; for evaluation / small workloads.
- **Kendra Enterprise Edition** — production-grade; higher capacity, redundancy, higher query throughput.
- **Kendra GenAI Enterprise Edition** — adds hybrid search (lexical + semantic), advanced re-ranking, and the **Kendra GenAI Index** for use as a Bedrock Knowledge Bases retriever.

### Index
The searchable corpus. Documents loaded via **data source connectors** (incremental sync) or direct upload.

### Data sources
40+ connectors: S3, SharePoint Online / On-prem, Confluence, Salesforce, ServiceNow, Box, OneDrive, Google Drive, Jira, GitHub, Slack, RDS, Aurora, Microsoft Teams, Quip, Alfresco, custom connectors via SDK. Connectors sync incrementally on schedule.

### Document attributes / faceted search
Documents carry attributes (author, date, document type, custom tags); facets enable filtering and sorting alongside text matching.

### Query types
- **Natural-language queries** — "How do I request time off?" — returns the passage with the answer.
- **Question-answering** — direct answers extracted from the source content.
- **Keyword search** — traditional inverted-index queries.
- **Faceted filtering** — narrow by attribute.

Response includes both ranked documents AND direct answers (where extractable) with citations.

### Re-ranking
Kendra's GenAI Edition includes neural re-ranking models that score top candidates from initial retrieval — significantly improves accuracy on natural-language queries.

### Access control
**Document-level access control** — each document carries an ACL (user / group IDs); Kendra enforces at query time. The principal making the query supplies their identity (via IAM Identity Center, custom token); Kendra filters results to authorized documents.

### Custom data sources
Bring documents via the SDK when no connector exists.

### Kendra GenAI Index
Specialized index optimized for use as a **Bedrock Knowledge Bases retriever**. Combines Kendra's hybrid search and re-ranking with Bedrock's broader RAG orchestration. The right pattern when you want Kendra accuracy with Bedrock features (Agents, Guardrails, multi-source RAG).

## Pricing model

- **Developer Edition** — flat hourly fee + small per-query cost.
- **Enterprise Edition** — hourly fee per "Storage Capacity Unit" (SCU) and per "Query Capacity Unit" (QCU). Significantly more expensive than Developer.
- **GenAI Enterprise Edition** — additional hourly fee for the GenAI features.
- **Connectors** — included with the index; some connectors have additional connector-specific fees.

Kendra is the most expensive AWS retrieval service per query. For workloads that justify it (high accuracy on enterprise content, regulated / compliance-driven retrieval), the cost is reasonable; for general RAG, evaluate cheaper alternatives.

## Quotas & limits

- **Documents per index**: tens of millions (Developer) to hundreds of millions (Enterprise).
- **Storage per index**: GB to TB scale.
- **Queries per second**: per QCU; raisable.
- **Connector sync frequency**: configurable.
- **Custom data sources**: bounded; raisable.

## Common pitfalls

- **Kendra Enterprise for tiny workloads.** The flat hourly fee dominates at small query volume. Use Developer Edition or a different retriever.
- **No document-level access control.** Returning confidential documents to unauthorized users is the most embarrassing search-system failure. Configure ACLs from day one.
- **No incremental sync configured.** Full-sync every time is slow and expensive. Use incremental sync.
- **Skipping the GenAI Edition for high-stakes RAG.** Re-ranking dramatically improves answer quality on natural-language queries.
- **Kendra and Bedrock Knowledge Bases used in parallel.** Pick one as primary. If Kendra's accuracy is the driver, use it via the GenAI Index inside Bedrock Knowledge Bases.
- **Connector permissions too broad.** Kendra needs to read your source content; scope the IAM role / source credentials minimally.
- **No metrics monitoring.** Query volume, latency, and click-through (if you instrument it) tell you whether Kendra is actually working for users.

## Pairs well with
- [Bedrock](bedrock.md) Knowledge Bases — Kendra GenAI Index as the retriever.
- [Lambda](../compute/lambda.md) — query orchestration, custom processing.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — principal identity for document-level ACL.
- [QuickSight](../analytics/quicksight.md) — search-quality dashboards.
- [Comprehend](comprehend.md) — text enrichment ahead of indexing.

## Pairs well with these repo pages
- [Bedrock](bedrock.md), [OpenSearch](../analytics/opensearch.md), [Q](q.md).

## Further reading
- [Amazon Kendra documentation](https://docs.aws.amazon.com/kendra/).
- [Kendra GenAI Index](https://docs.aws.amazon.com/kendra/latest/dg/gen-ai.html).
- [Building Bedrock Knowledge Base with Kendra GenAI index](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-kendra-genai-index.html).
- [Kendra data source connectors](https://docs.aws.amazon.com/kendra/latest/dg/hiw-data-source.html).
- [Document-level access control](https://docs.aws.amazon.com/kendra/latest/dg/user-acls.html).
