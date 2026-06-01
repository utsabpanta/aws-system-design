# Transcribe

> **One-line summary.** Managed automatic speech recognition (ASR). Convert audio / video to text — real-time streaming or async batch — across dozens of languages.

## TL;DR

- The right service for speech-to-text on AWS. Real-time `StartStreamTranscription` (WebSocket / HTTP/2) and async S3-based `StartTranscriptionJob`.
- **Custom vocabulary** + **custom language models** improve recognition for domain-specific terms (drug names, product names, jargon).
- **Speaker diarization** (who said what), **channel identification**, **automatic language identification**, **PII redaction**, **toxicity detection**, **content filtering** — all built in.
- **Transcribe Medical** for clinical conversation transcription (HIPAA-aligned).
- **Transcribe Call Analytics** packages contact-center-specific features (sentiment, talk-time, categorization, summarization).

## When to use it

- Meeting / call recording transcription.
- Real-time captions for live streams.
- Contact-center analytics (Call Analytics).
- Voice-driven applications (transcribe to feed downstream NLU).
- Subtitles / closed captions for video content.
- Medical conversation transcription.
- Voice search / commands.

## When NOT to use it

- Music or non-speech audio (Transcribe is tuned for speech).
- Extremely noisy / low-quality audio without preprocessing.
- Workloads where you want full-stack voice AI (transcription + understanding + response) — sometimes a single voice-aware LLM agent fits better.

## Key concepts

### Modes

- **Streaming (real-time)** — `StartStreamTranscription` via WebSocket or HTTP/2. Sub-second-to-second latency. Use for live captions / voice apps / real-time agent assist.
- **Batch** — `StartTranscriptionJob` on S3 audio file. Higher accuracy in some configurations; async results.

### Features

- **Speaker diarization** — labels speakers (`spk_0`, `spk_1`) when there are multiple voices.
- **Channel identification** — for stereo recordings (one party per channel), associate text with channel.
- **Automatic language identification** — Transcribe detects the language from the audio.
- **Custom vocabulary** — small list of domain terms with optional pronunciation hints.
- **Custom language models (CLMs)** — train on your text corpus for vocabulary AND phrasing adaptation.
- **PII redaction** — mask credit cards, SSNs, addresses, names in the transcript.
- **Toxicity detection** — flag harmful content in the audio.
- **Content filtering / vocabulary filtering** — block or mask specified words.
- **Subtitle output** — VTT / SRT for video captions.

### Transcribe Call Analytics

Contact-center-specific:

- **Sentiment** per speaker over time.
- **Talk-time / interruption metrics**.
- **Categorization** — apply rules ("escalation requested", "refund mentioned").
- **Conversation summaries** — generative summary at end of call.
- **Real-time analytics** — same features in real time for agent assist.

### Transcribe Medical

- Optimized for clinical dialogue (doctor-patient).
- HIPAA-eligible.
- Includes medical-specific vocabulary out of the box.

### Output format

JSON with words, timestamps, confidence per word, speakers / channels, and optional alternative transcriptions.

## Pricing model

- **Per audio-second** transcribed (rounded up per call). Different tiers:
  - **Standard** — base transcription.
  - **Medical** — higher per-second rate.
  - **Call Analytics** (batch and real-time) — higher rates that include the analytics features.
- **Custom Language Models** — per-hour training fee; inference at standard per-second rate.
- **PII redaction / toxicity / content filtering** — add-on per-second fees on top of the base rate.

For high-volume meeting / call workloads, tiered volume discounts apply.

## Quotas & limits

- **Real-time stream session length**: 4 hours per session.
- **Batch audio file size**: 2 GB.
- **Batch job duration**: up to 4 hours of audio per job.
- **Custom vocabulary size**: 50 KB.
- **Custom language model training data**: GB-scale per model.
- **Concurrent batch jobs**: bounded; raisable.

## Common pitfalls

- **No custom vocabulary on a domain workload.** Generic ASR mis-recognizes brand / drug / product names. A vocabulary list is the first improvement.
- **Streaming when batch would do.** Batch transcription is cheaper per second and often higher accuracy. Use streaming only when you need real-time output.
- **Speaker diarization assumed accurate.** Diarization quality degrades with overlapping speech, poor mic separation, and short utterances. Validate on your audio.
- **PII redaction without verification.** Catches most; treat as "first pass" for highly regulated workloads.
- **No language identification for multilingual audio.** Languages don't auto-detect mid-clip; one language per job by default. For mixed-language audio, segment first.
- **Audio quality ignored.** A bad mic / noisy environment dominates accuracy more than any feature tweak. Quality matters most.
- **Call Analytics for non-call workloads.** It's tuned for two-party conversations; multi-speaker meetings work better with standard Transcribe + diarization.

## Pairs well with

- [Polly](polly.md) — round-trip voice apps.
- [Translate](translate.md) — translate transcripts to other languages.
- [Comprehend](comprehend.md) — sentiment / entities / classification on transcripts.
- [Bedrock](bedrock.md) — summarize / answer questions on transcripts.
- **Amazon Connect** — Call Analytics is the canonical contact-center pairing.
- [S3](../storage/s3.md) — audio input.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — pipeline orchestration.

## Pairs well with these repo pages

- [Polly](polly.md), [Translate](translate.md), [Comprehend](comprehend.md), [Bedrock](bedrock.md), [Lex](lex.md).

## Further reading

- [Amazon Transcribe documentation](https://docs.aws.amazon.com/transcribe/).
- [Streaming transcription](https://docs.aws.amazon.com/transcribe/latest/dg/streaming.html).
- [Custom Language Models](https://docs.aws.amazon.com/transcribe/latest/dg/custom-language-models.html).
- [Transcribe Call Analytics](https://docs.aws.amazon.com/transcribe/latest/dg/call-analytics.html).
- [Transcribe Medical](https://docs.aws.amazon.com/transcribe/latest/dg/transcribe-medical.html).
