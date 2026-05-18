# Polly

> **One-line summary.** Managed text-to-speech (TTS). Dozens of voices across many languages, with **Neural** and **Generative** voice engines for human-like output.

## TL;DR
- Convert text into natural-sounding speech via API. Returns MP3 / OGG Vorbis / PCM audio (`SynthesizeSpeech`) or **starts an async S3-output job** for long-form text.
- Three engine tiers in 2026:
  - **Standard** — concatenative TTS; cheapest, robotic by modern standards.
  - **Neural** — neural-net voices; near-human; the most common production choice.
  - **Generative / Long-form** — newer engines tuned for expressive and very long-form narration; best for audiobooks / podcasts / IVR.
- **SSML** support (Speech Synthesis Markup Language) for pauses, pronunciation, emphasis, prosody control.
- Pair with **Transcribe** (the inverse — speech-to-text) for full voice-interaction pipelines.

## When to use it
- IVR / contact center prompts (often pairs with Amazon Connect).
- E-learning / accessibility (audio versions of text content).
- Audiobook / podcast generation.
- Notifications / alerts spoken to users.
- Voice in chatbots and assistants.

## When NOT to use it
- Voice cloning of specific people without their consent — restricted by AWS AUP and not the right tool.
- Highly emotional / dramatic performances — current generative voices are good but not full performance acting.
- Real-time conversational AI where extremely low latency and emotional adaptation matter — emerging Bedrock Voice and other AWS conversational primitives may fit better.

## Key concepts

### Engines and voices
- **Standard voices** — concatenative; many languages, low cost; obviously synthetic in modern UX.
- **Neural Text-to-Speech (NTTS)** — neural-net-based; modern default for most apps. Many voices across English, Spanish, French, German, Japanese, Mandarin, Hindi, Arabic, and others.
- **Generative voices / Long-form** — newer, longer-context, more expressive engines. Use for audiobooks, long narration, marketing copy, IVR prompts that need warmth.

Voice catalog includes both gender presentations across many accents (US, UK, AU, IN English; LatAm vs European Spanish; etc.).

### SSML
Mark up the input text:
- `<break time="500ms"/>` for pauses.
- `<phoneme alphabet="ipa" ph="...">word</phoneme>` for custom pronunciation.
- `<emphasis level="strong">word</emphasis>`.
- `<prosody rate="slow">…</prosody>`.
- `<say-as interpret-as="date">2026-05-18</say-as>`.

Critical for production-quality output.

### Lexicons
Per-account pronunciation lexicons override default pronunciation for specific terms (your product names, jargon, abbreviations).

### Async (long-form synthesis)
- Start a synthesis task; Polly writes the result to an S3 bucket; you get an SNS notification on completion.
- Right for podcast-length / book-length content (text up to ~100K characters).

### Speech marks
Optional metadata stream alongside audio: word- / sentence-level timestamps, viseme codes for lip-sync animation. Useful for karaoke-style highlighting and animation.

### Output formats
- **MP3** — most common.
- **OGG Vorbis**.
- **PCM** — raw audio for further processing.
- Sample rates: 8 kHz, 16 kHz, 22.05 kHz, 24 kHz.

## Pricing model

- **Standard voices** — per million characters; cheapest tier.
- **Neural voices** — per million characters; higher rate.
- **Generative / Long-form voices** — per million characters; highest rate; warranted for the quality difference on long content.
- **Async (long-form synthesis tasks)** — same per-character rate as the chosen engine.

## Quotas & limits

- **Real-time `SynthesizeSpeech` request size**: 3,000 characters of billed characters per request.
- **Async long-form synthesis**: up to ~100,000 characters of text per job.
- **Concurrent requests per second**: bounded; raisable.
- **Lexicons per Region**: 5 default.

## Common pitfalls

- **Standard voices in customer-facing apps.** Robotic by 2026 standards. Use Neural or Generative unless cost dominates.
- **No SSML.** Default reading is monotone. Add pauses, emphasis, and prosody for natural pacing.
- **No lexicon for brand / product names.** Mispronunciations of your own brand erode trust. One lexicon entry per problem term.
- **Generating audio per request when caching would do.** Common phrases (IVR prompts, notification templates) should be generated once and cached; don't pay per render.
- **Voice consistency drift.** Different parts of the app using different voices makes the brand feel disjointed. Pick voices per locale and stick.
- **Sample rate mismatches.** Some downstream (Connect IVR, telephony) prefer specific rates. Match the consumer's expectation.
- **Skipping the legal AUP review for voice cloning / impersonation use cases.** Don't.

## Pairs well with
- [Transcribe](transcribe.md) — the speech-to-text counterpart for round-trip voice workflows.
- **Amazon Connect** — IVR prompts and dynamic messages.
- [Lex](lex.md) — conversational bots that speak responses via Polly.
- [Lambda](../compute/lambda.md) — on-demand generation pipelines.
- [S3](../storage/s3.md) — async output destination.
- [Translate](translate.md) — translate text before synthesizing in another language.

## Pairs well with these repo pages
- [Transcribe](transcribe.md), [Lex](lex.md), [Translate](translate.md).

## Further reading
- [Amazon Polly documentation](https://docs.aws.amazon.com/polly/).
- [Polly voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html).
- [SSML reference](https://docs.aws.amazon.com/polly/latest/dg/ssml.html).
- [Long-form synthesis](https://docs.aws.amazon.com/polly/latest/dg/long-form-voice-overview.html).
- [Lexicons](https://docs.aws.amazon.com/polly/latest/dg/managing-lexicons.html).
