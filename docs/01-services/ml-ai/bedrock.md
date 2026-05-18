# Bedrock

> **One-line summary.** AWS's managed foundation-model platform. Access Anthropic Claude, Meta Llama, Mistral, Cohere, AI21, Amazon Titan, Amazon Nova, and others through one API; fine-tune, ground on your data via Knowledge Bases, orchestrate as Agents, evaluate, and gate with Guardrails.

## TL;DR
- The right service for **LLM and foundation-model workloads on AWS**. One API, multiple model providers, no per-vendor SDKs to manage.
- **Knowledge Bases** is the managed RAG primitive (S3 / Confluence / Salesforce / SharePoint as sources; OpenSearch / Pinecone / Aurora pgvector / Kendra as the retriever). **Agents** orchestrate multi-step tasks with tool use.
- **Guardrails** enforce content policies (denied topics, PII redaction, prompt-injection filters, harmful-content classifiers) at the API boundary — applies to any model on the platform.
- **Model evaluation** lets you compare models against your own dataset before committing to one.
- For custom models, fine-tuning is supported on many models; **Provisioned Throughput** reserves capacity for predictable production load.

## When to use it
- Building LLM-powered features (chat, summarization, classification, code generation, content generation).
- Retrieval-augmented generation (RAG) over enterprise data using Knowledge Bases.
- Multi-step agent workflows with tool use (DB query, API call, file operation).
- Migrating off OpenAI / Anthropic direct APIs to a single AWS-managed surface.
- Enforcing content policies / safety controls at the LLM API boundary.

## When NOT to use it
- Workloads that need a specific open-source model not on Bedrock — host on **SageMaker** (or **SageMaker JumpStart**) directly.
- Classical ML (regression, classification on tabular data, time-series) — **SageMaker**.
- Specific AI tasks where AWS has a dedicated API (OCR → Textract, transcription → Transcribe, image labeling → Rekognition) — usually cheaper than running them through an LLM.

## Key concepts

### Foundation models
Bedrock hosts models from multiple providers:
- **Anthropic Claude** (Claude 3.x / 4.x family) — large reasoning / chat / vision models.
- **Meta Llama** — open Llama models.
- **Mistral / Mixtral**.
- **Cohere Command** — chat / RAG-optimized.
- **AI21 Jurassic / Jamba**.
- **Amazon Nova** (text, image, video) and **Amazon Titan** (text, image, embeddings) — AWS's own model family.
- **Stable Diffusion / Stability AI** — image generation.

Models are versioned; new versions land regularly. Each model has on-demand and (for many) Provisioned Throughput pricing.

### Invocation modes
- **InvokeModel** / **Converse** — single request/response.
- **InvokeModelWithResponseStream** / **ConverseStream** — streaming output for chat UX.
- **Batch inference** — long-running offline scoring of large datasets.

The **Converse API** is the unified, model-agnostic shape — same code works across Claude, Llama, Mistral, etc.

### Knowledge Bases
Managed RAG:
- **Data sources** — S3, Confluence, Salesforce, SharePoint, web crawl, custom.
- **Chunking** — fixed-size, semantic, or hierarchical.
- **Embeddings** — Titan Embeddings, Cohere Embed, or others.
- **Vector stores** — OpenSearch Serverless, Pinecone, Aurora PostgreSQL (pgvector), MongoDB Atlas, Neptune Analytics, **Kendra GenAI Index** (for higher-accuracy hybrid retrieval).
- **Retrieve** API returns relevant chunks; **RetrieveAndGenerate** also generates a grounded answer with citations.

### Agents
Multi-step LLM workflows:
- **Action groups** — Lambda functions the agent can call as tools.
- **Knowledge Bases** integration — retrieve from RAG sources mid-conversation.
- **Memory** — preserve context across sessions.
- **Multi-agent collaboration** — supervisor + sub-agent patterns.

### Guardrails
Policy enforcement at the API:
- **Denied topics** — block specific topics ("don't discuss competitor X").
- **Content filters** — harmful content categories (hate, violence, sexual, misconduct).
- **Word filters** — block specific words / regex.
- **PII redaction** — detect and mask PII in inputs and outputs.
- **Prompt-injection filters** — detect and block attempts to subvert the system prompt.
- **Contextual grounding checks** — verify the model's output is grounded in retrieved sources.

Guardrails apply to any model on Bedrock and to your own models (via ApplyGuardrail).

### Fine-tuning
Supported for many models — provide a labeled dataset; Bedrock produces a custom model artifact. **Continued Pre-training** is also available for some models (domain adaptation).

### Model Evaluation
Compare models on your own dataset with automatic metrics, LLM-as-judge evaluation, or human evaluation workflows.

### Provisioned Throughput
Reserve dedicated capacity (in **Model Units**) for predictable latency and throughput. Hourly billing for the reservation. Required for fine-tuned models in some cases; optional for base models for production SLOs.

### Bedrock Marketplace
Discover and deploy partner models (Cohere, Mistral premium, others) with managed billing.

## Pricing model

- **On-demand inference** — per million input + output tokens, by model.
- **Provisioned Throughput** — hourly per Model Unit; cheaper at high sustained throughput.
- **Batch inference** — typically discounted vs on-demand.
- **Fine-tuning** — per million tokens trained + storage for the custom model.
- **Knowledge Bases** — per-source ingestion + vector store cost (vector store is your S3 / Aurora / OpenSearch / Pinecone bill).
- **Agents** — token cost for the LLM + Lambda invocation cost for action groups.
- **Guardrails** — per million text units evaluated.

The dominant cost on most workloads is **per-token inference** — design for prompt brevity, retrieval-augmented context (don't dump full docs), and caching.

## Quotas & limits

- **Concurrent requests per model**: model- and Region-dependent; raisable.
- **Tokens per request**: model-dependent (latest large Claude / Nova / Llama models support very long context windows — 200K+ tokens).
- **Knowledge Bases per account per Region**: 100s.
- **Agents per account per Region**: 100s.
- **Provisioned Throughput Model Units**: bounded; raisable.

## Common pitfalls

- **Picking a model based on benchmarks instead of your task.** Run **Model Evaluation** on a representative dataset before committing.
- **Long prompts with full documents.** RAG with Knowledge Bases is dramatically cheaper than stuffing context.
- **No Guardrails.** A production LLM API without content filtering, PII redaction, and prompt-injection defense is an incident waiting to happen.
- **Direct prompt manipulation instead of Agents.** When the workflow has multiple steps and tool use, Agents handle the orchestration; rolling your own is error-prone.
- **On-demand for steady production load.** Provisioned Throughput is often cheaper at sustained traffic; predictable latency too.
- **Fine-tuning the largest model when a smaller fine-tuned model would do.** Fine-tuned smaller models often beat larger base models on narrow tasks at a fraction of the inference cost.
- **No evaluation metrics post-deploy.** LLM outputs drift; without evaluation in production, regressions go unnoticed.
- **Region availability mismatch.** Specific models are launched per-Region; verify your target Region supports the model before architecting around it.

## Pairs well with
- [Lambda](../compute/lambda.md) — Action Groups in Agents.
- [OpenSearch](../analytics/opensearch.md), **Aurora pgvector**, [Neptune Analytics](../database/neptune.md), [Kendra](kendra.md), **Pinecone, MongoDB Atlas** — Knowledge Bases vector stores.
- [S3](../storage/s3.md), **Confluence / Salesforce / SharePoint connectors** — Knowledge Bases data sources.
- [SageMaker](sagemaker.md) — JumpStart for custom open-source models; Bedrock for managed-model API.
- [Step Functions](../integration-messaging/step-functions.md) — multi-step LLM workflows beyond what Agents handle.
- [CloudTrail](../observability/) (forthcoming) — Bedrock API logs.

## Pairs well with these repo pages
- [SageMaker](sagemaker.md), [Kendra](kendra.md), [OpenSearch](../analytics/opensearch.md), [Neptune](../database/neptune.md).
- `docs/04-reference-architectures/genai-rag-bedrock.md` (forthcoming).

## Further reading
- [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/).
- [Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/).
- [Bedrock Agents](https://aws.amazon.com/bedrock/agents/).
- [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/).
- [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html).
- [Model Evaluation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html).
