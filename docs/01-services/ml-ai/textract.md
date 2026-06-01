# Textract

> **One-line summary.** Managed document understanding — extract text, tables, forms (key-value pairs), signatures, and structured query results from PDFs and images.

## TL;DR

- For **structured** document processing — forms, invoices, receipts, IDs, lending documents, healthcare forms. Returns text *and* the spatial structure (tables, key-value pairs, layout).
- Pre-built **AnalyzeExpense** and **AnalyzeID** APIs handle invoices / receipts and government-issued IDs out of the box.
- **AnalyzeLending** for the loan-document workflow.
- **Queries** (ask questions of a document: "What's the invoice total?") return targeted answers without writing extraction rules.
- For ad-hoc text in images (signs, screenshots), **Rekognition DetectText** is fine. For documents with structure, Textract is the right tool.

## When to use it

- Invoice / receipt processing pipelines.
- Healthcare form digitization.
- ID verification (driver's licenses, passports).
- Loan / mortgage document processing.
- KYC document extraction.
- Any "PDF in, structured JSON out" workflow.

## When NOT to use it

- Plain text extraction with no structure needed — Rekognition `DetectText` is cheaper.
- Free-form documents where you want LLM-style understanding ("summarize this contract") — pair Textract for OCR with **Bedrock** for the reasoning, or use a Bedrock vision-capable model directly.
- Real-time / sub-second document processing — Textract is asynchronous for multi-page docs.

## Key concepts

### APIs

**Sync (single page):**

- `DetectDocumentText` — raw text with bounding boxes.
- `AnalyzeDocument` — text + tables + forms + signatures + layout + queries.

**Async (multi-page PDFs, S3-based):**

- `StartDocumentTextDetection` / `GetDocumentTextDetection`.
- `StartDocumentAnalysis` / `GetDocumentAnalysis`.

**Specialty:**

- `AnalyzeExpense` — invoices, receipts (line items, totals, vendor, dates).
- `AnalyzeID` — passports, driver's licenses (issuer-specific field extraction).
- `AnalyzeLending` — loan-package workflow (orchestrates many document classifications and extractions).

### Features

- **Tables** — preserves row/column structure; rebuild the table in your downstream system.
- **Forms** — `KEY_VALUE_SET` blocks tying labels to values ("Name: John Smith" → `KEY = Name, VALUE = John Smith`).
- **Layout** — paragraphs, titles, footers, page numbers, headers — useful for converting docs to structured Markdown.
- **Signatures** — detect signature regions.
- **Queries** — ask "What's the total amount?" / "Who is the borrower?" and get a targeted answer.
- **Adapters** — train a custom adapter on a small sample of your documents to improve accuracy on domain-specific layouts.

### Output format

Textract returns a graph of blocks (PAGE, LINE, WORD, TABLE, CELL, KEY_VALUE_SET, QUERY_RESULT, SIGNATURE, LAYOUT_*) with bounding boxes and relationships. Most teams use the `amazon-textract-textractor` Python helper to parse this into easier shapes.

## Pricing model

- **Per page** processed, with different rates for `DetectDocumentText`, `AnalyzeDocument` (with features: forms / tables / queries / signatures / layout — each feature adds cost), `AnalyzeExpense`, `AnalyzeID`, `AnalyzeLending`.
- **Adapters** — per-adapter-monthly fee + per-page for adapter inference.
- **No charge for the async start/get** (only for the underlying processing).

The per-feature-per-page model means turning on every feature for every document is expensive. Be selective.

## Quotas & limits

- **Sync request size**: 10 MB (PDF / image).
- **Async request size**: 500 MB / 3,000-page PDF.
- **Page concurrency**: bounded; raisable.
- **Adapter training**: small dataset (10s-100s of pages).

## Common pitfalls

- **Enabling all features for every doc.** Pay for what you use. Don't request tables + forms + signatures + queries + layout if you only need text + key-value pairs.
- **Skipping the adapter for high-volume domain-specific documents.** A small trained adapter can dramatically improve accuracy on consistent layouts (your invoice format, your specific KYC form).
- **Treating Textract output as flat text.** The whole point is the structure — use it.
- **Document quality ignored.** Poor scans (low DPI, skewed, photographed at angles) hurt accuracy. Pre-process if your pipeline can.
- **Textract for handwritten signatures-verification.** Textract detects *where* a signature is; it doesn't verify identity. For verification, use a forensic tool.
- **Skipping Queries for targeted extraction.** Writing rules to find "the invoice total" can be replaced with a Query. Easier, more robust to layout changes.
- **No retry policy on async jobs.** Async jobs can fail transiently; configure SNS notification + retry logic.

## Pairs well with

- [S3](../storage/s3.md) — input / output.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — pipeline orchestration.
- [Comprehend](comprehend.md) — analyze extracted text (sentiment, entities, classification).
- [Bedrock](bedrock.md) — LLM-based reasoning over extracted text (summarize, Q&A).
- [Macie](../security-identity/macie.md) — PII discovery on extracted documents.

## Pairs well with these repo pages

- [Comprehend](comprehend.md), [Bedrock](bedrock.md), [Rekognition](rekognition.md).

## Further reading

- [Amazon Textract documentation](https://docs.aws.amazon.com/textract/).
- [AnalyzeDocument features](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-analyzing.html).
- [AnalyzeExpense](https://docs.aws.amazon.com/textract/latest/dg/expensedocuments.html).
- [Textract Queries](https://docs.aws.amazon.com/textract/latest/dg/queryresponse.html).
- [Textract adapters](https://docs.aws.amazon.com/textract/latest/dg/adapters.html).
