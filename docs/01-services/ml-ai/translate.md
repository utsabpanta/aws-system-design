# Translate

> **One-line summary.** Managed neural machine translation. ~75 languages, real-time and batch, with custom terminology and Active Custom Translation for domain adaptation.

## TL;DR
- Sync `TranslateText` for one-string-at-a-time; async batch jobs for large document sets (S3-in / S3-out).
- **Custom terminology** — force specific translations for terms (your product names, brand terms, legal phrasing). The single highest-value feature for production use.
- **Active Custom Translation (parallel data)** — fine-tune translation behavior with your own bilingual parallel corpus.
- Supports document translation that preserves layout (DOCX / XLSX / PPTX / HTML).
- Pairs naturally with **Transcribe → Translate → Polly** for full voice translation pipelines.

## When to use it
- Multilingual customer support (translate incoming tickets, generate localized replies).
- Localization of UI strings / product content at scale.
- Real-time chat translation.
- Document translation for compliance / legal review.
- E-commerce product description localization.

## When NOT to use it
- High-stakes legal / medical translation where human review is non-negotiable — Translate is a first pass.
- Tasks requiring nuanced cultural / creative writing — translation of marketing copy still benefits from human review.
- Translation entwined with reasoning / summarization — sometimes a Bedrock LLM does both more naturally.

## Key concepts

### APIs
- `TranslateText` — real-time, one or more strings.
- `StartTextTranslationJob` — async batch on S3 input/output.
- `TranslateDocument` — sync document translation (DOCX, XLSX, PPTX, HTML) preserving formatting.

### Languages
~75 source / target languages with most pairs supported directly. Some pairs route through English (pivot translation); accuracy slightly lower on those.

### Custom Terminology
- Upload a CSV mapping source-term → target-term per language pair.
- Translate respects these terms regardless of context.
- Mandatory for brand consistency in production.

### Active Custom Translation (parallel data)
- Provide your own parallel corpus (source + target documents).
- Translate fine-tunes its model for your domain (legal, medical, technical, e-commerce).
- Improves accuracy on terms and patterns that don't appear in general-purpose training data.

### Profanity masking
Option to mask profanity in the output (replaces with `?` or similar).

### Formality
Some target languages (German, Italian, Hindi, Japanese, French, Spanish) support a formality preference (formal / informal).

## Pricing model

- **Per character translated** (real-time and batch the same per-character rate).
- **Active Custom Translation** — additional per-character rate.
- **Custom terminology** — free to use; no extra fee.
- **Document translation** — per character in the document.

For high-volume workloads, batch is operationally simpler but the same per-unit cost.

## Quotas & limits

- **Real-time request**: up to 10,000 bytes per call.
- **Async batch**: large; up to many GB per job.
- **Concurrent batch jobs**: bounded; raisable.
- **Custom terminology size**: 256 KB CSV.
- **Parallel data per account**: bounded; check current docs.

## Common pitfalls

- **No custom terminology.** Brand and product names get translated literally; "Apple" becomes the fruit.
- **Active Custom Translation without enough parallel data.** Quality only improves meaningfully with hundreds-thousands of paired examples; tiny corpora don't move the needle.
- **Real-time translation per request at high RPS without caching.** Memoize common short strings (UI labels) instead of paying per call.
- **Document translation that loses formatting.** Use `TranslateDocument` for structured documents (DOCX / XLSX / PPTX / HTML) instead of extracting text and translating — preserves the formatting.
- **Translation in a vacuum.** For chat / voice apps, pair with Transcribe (audio in) and Polly (audio out) for round-trip.
- **Skipping post-edit review for high-stakes content.** Translate is a first pass; human review still needed for legal / safety / marketing.

## Pairs well with
- [Transcribe](transcribe.md) → Translate → [Polly](polly.md) — full voice-translation pipelines.
- [Comprehend](comprehend.md) — language detection ahead of Translate.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — batch / orchestrated workflows.
- [S3](../storage/s3.md) — batch input / output.
- [Bedrock](bedrock.md) — for translation entwined with reasoning / formatting / summarization.

## Pairs well with these repo pages
- [Transcribe](transcribe.md), [Polly](polly.md), [Comprehend](comprehend.md), [Bedrock](bedrock.md).

## Further reading
- [Amazon Translate documentation](https://docs.aws.amazon.com/translate/).
- [Supported language pairs](https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html).
- [Custom terminology](https://docs.aws.amazon.com/translate/latest/dg/how-custom-terminology.html).
- [Active Custom Translation](https://docs.aws.amazon.com/translate/latest/dg/customizing-translations-parallel-data.html).
- [TranslateDocument](https://docs.aws.amazon.com/translate/latest/dg/document-translation.html).
