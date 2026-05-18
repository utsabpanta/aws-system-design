# Comprehend

> **One-line summary.** Managed natural-language processing API. Entities, key phrases, sentiment, language detection, syntax, topic modeling, PII detection, document classification — pre-trained plus custom models.

## TL;DR
- Pre-trained NLP API for the "I have a corpus of text and I need to extract structured signals" use cases.
- Standard analyses: **entities** (people, places, orgs, dates), **key phrases**, **sentiment** (positive / negative / neutral / mixed), **language detection**, **PII detection / redaction**, **syntax** (POS tags), **events** (financial / clinical event extraction).
- **Custom classification** and **custom entity recognition** for domain-specific tasks (label your own dataset, get a managed model).
- **Comprehend Medical** is a separate offshoot for clinical text (medical entities, ICD-10, RxNorm, PHI).
- For more open-ended language understanding (Q&A, summarization, complex reasoning), an LLM on **Bedrock** is usually the better choice in 2026. Comprehend remains useful for high-volume structured extraction where per-LLM-token pricing would be expensive.

## When to use it
- Sentiment analysis on customer reviews / support tickets.
- PII detection / redaction in document pipelines.
- Topic modeling on large text corpora.
- Custom classifiers for support-ticket routing, content moderation.
- Custom entity recognizers for domain-specific terms (drug names, product SKUs, parts).
- Clinical text extraction (Comprehend Medical).

## When NOT to use it
- Workloads where you want generative outputs (summaries, paraphrasing, Q&A) — **Bedrock** is the right tool.
- Tasks where a small fine-tuned LLM clearly beats per-task classification accuracy — Bedrock with fine-tuning.
- Tiny one-off tasks where managing a Comprehend job is heavier than the work — sometimes a Lambda + small library is enough.

## Key concepts

### Pre-trained APIs
**Single-document (real-time):**
- `DetectDominantLanguage`
- `DetectEntities` (people, places, orgs, dates, quantities, titles, events, locations)
- `DetectKeyPhrases`
- `DetectSentiment`
- `DetectSyntax`
- `DetectPiiEntities` / `RedactPiiEntities`
- `DetectTargetedSentiment` (sentiment toward specific entities in the text)

**Batch (async, S3 input/output):** the same analyses on large document sets.

### Custom models
- **Custom Classification** — train a multi-class or multi-label classifier on your labeled documents.
- **Custom Entity Recognition** — train an NER model on your annotated entities.
- **Topic Modeling** — unsupervised topic discovery over a document corpus (Latent Dirichlet Allocation under the hood).

Custom models can be **endpoint-hosted** (low-latency real-time) or **async batch** (cheaper, no endpoint).

### Comprehend Medical
- Separate API surface for medical text.
- **Entities**: medications, conditions, anatomy, tests.
- **ICD-10-CM** and **RxNorm** code linking.
- **PHI detection** — HIPAA-relevant identifier extraction.

### Flywheels
A managed mechanism to continuously retrain custom models as new data arrives — keeps the model fresh without you running pipelines yourself.

## Pricing model

- **Pre-trained APIs** — per unit (100 characters per unit).
- **Custom classification / entity recognition** — per inference unit (per document) + per training-hour + per endpoint-hour (if endpoint-hosted).
- **Topic modeling** — per 100 KB of text + per modeling job.
- **Comprehend Medical** — per unit (slightly different units than core Comprehend).
- **Flywheels** — included in custom-model pricing.

For high-volume PII detection or sentiment analysis, Comprehend at per-unit pricing is often cheaper than running an LLM per request.

## Quotas & limits

- **Real-time API**: per-request character limit (5,000 characters for most analyses, 5 MB for batch / async).
- **Concurrent batch jobs**: bounded; raisable.
- **Endpoint inference units**: configurable per endpoint.
- **Custom model document limits**: per training-job document count limits; check current docs.

## Common pitfalls

- **Comprehend for tasks an LLM does dramatically better.** Open-ended summarization, contextual Q&A, multi-document reasoning — Bedrock wins.
- **Per-document real-time API at high RPS.** Batch jobs are dramatically cheaper for large corpora.
- **PII redaction without a downstream review.** Comprehend catches most PII; manual review for critical workflows is still required.
- **Custom model without enough labeled data.** Domain-specific NER and classification need thousands of labeled examples for good accuracy.
- **Endpoints kept up at full capacity for occasional use.** Async batch fits sporadic workloads better than always-on endpoints.
- **Mixing Comprehend Medical with non-medical text.** It's tuned for clinical language; bad results on general text.

## Pairs well with
- [S3](../storage/s3.md) — async batch input / output.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — pipeline orchestration.
- [Kinesis Data Streams / Firehose](../analytics/kinesis.md) — stream into Comprehend.
- [Bedrock](bedrock.md) — when generative or richer reasoning is needed.
- [Macie](../security-identity/macie.md) — adjacent PII discovery for S3-stored data.

## Pairs well with these repo pages
- [Bedrock](bedrock.md), [Textract](textract.md), [Translate](translate.md).

## Further reading
- [Amazon Comprehend documentation](https://docs.aws.amazon.com/comprehend/).
- [Custom classification](https://docs.aws.amazon.com/comprehend/latest/dg/how-document-classification.html).
- [Custom entity recognition](https://docs.aws.amazon.com/comprehend/latest/dg/custom-entity-recognition.html).
- [Comprehend Medical](https://docs.aws.amazon.com/comprehend-medical/).
- [Flywheels](https://docs.aws.amazon.com/comprehend/latest/dg/flywheels-about.html).
