# Lex

> **One-line summary.** Managed conversational AI service — build chatbots and IVR bots (voice and text). Same underlying tech that powers Alexa, exposed for your apps.

## TL;DR

- For **rule-and-intent-based chatbots and IVR** — the "user asks for X; bot collects slots; bot calls a Lambda; bot replies" pattern. Strong in contact-center IVR (with Amazon Connect) and bounded customer-service flows.
- **Intent + slot** model with built-in dialog management, multi-turn slot elicitation, confirmation, and fallback handling.
- **Lex V2** is the current generation. Lex V1 is legacy; new bots should be V2.
- In 2026, **open-ended conversational AI** (long context, free-form reasoning) usually lives on **Bedrock Agents** instead — Lex is best when you have a known set of intents with structured slot collection and want a bounded, predictable, low-latency bot.
- Native integrations: **Amazon Connect** (IVR), **chat channels** (Slack, Twilio, Facebook Messenger via direct connectors), web SDKs.

## When to use it

- Contact-center IVR (Amazon Connect).
- Customer service chatbots for FAQs / order status / scheduling / refunds.
- Voice-enabled IoT or in-app voice commands.
- Internal employee chatbots for HR / IT tasks.
- Use cases where the bot has a *small set of well-defined intents* and structured data to collect.

## When NOT to use it

- Open-ended, free-form chat that requires reasoning over arbitrary topics — **Bedrock Agents** (or Q Business for the enterprise-knowledge case).
- Mostly-Q&A over a corpus of documents — **Bedrock Knowledge Bases** or Q Business.
- Chat experiences that need long-context multi-turn reasoning (write code, summarize a paper) — LLM on Bedrock.

## Key concepts

### Bots, intents, slots, utterances

- **Bot** — the top-level resource.
- **Intent** — a user goal ("BookAppointment", "GetOrderStatus"). Each intent has sample utterances.
- **Slot** — a piece of data the bot collects ("date", "time", "service-type"). Slot types are built-in (`AMAZON.Date`, `AMAZON.Number`, `AMAZON.City`) or custom.
- **Sample utterances** — example user phrases that map to the intent. Lex generalizes from these.

### Dialog management

- **Slot elicitation** — bot asks for slots one by one until all required slots are filled.
- **Confirmation** — confirm before fulfilling.
- **Fallback intent** — default handler when nothing matched.
- **Session state** — preserved across turns; carry context.

### Fulfillment

- **Lambda hook** at fulfillment — your Lambda receives the filled slots, does the work (database lookup, API call, ticket creation), returns a response.
- **Code hooks** at multiple lifecycle points (dialog code hook, initialization hook, validation hook).

### Channels

- **Amazon Connect** — IVR for voice bots.
- **Chat platforms** — Slack, Twilio SMS, Facebook Messenger via built-in connectors.
- **Web SDKs / custom integrations** via the runtime API.

### Voice

- Lex uses **Transcribe** for ASR and **Polly** for TTS internally for voice channels.

### Bot versioning and aliases

- **Versions** snapshot the bot configuration.
- **Aliases** point to versions; production / staging / dev aliases let you safely promote changes.

### Generative AI features (Lex V2)

Lex has been adding generative features:

- **Descriptive bot building** — describe a bot in plain language; Lex generates intents and slots.
- **Sample utterance generation** — given an intent, generate variant utterances.
- **Conversational FAQ** — answer questions from a knowledge source (often paired with a Bedrock Knowledge Base) when no intent matches.

These narrow the gap with LLM-based bots; for fully open-ended chat, Bedrock Agents is still the better starting point.

### Lex V1 (legacy)

Earlier API surface. New bots should be V2. Migration tools available.

## Pricing model

- **Per text request** — small per-1,000 fee.
- **Per voice request (audio input)** — separate rate.
- **Per voice second processed** — for streaming voice channels.
- **No charge for the bot itself**; you pay only per interaction.

For voice channels, the per-second cost adds up; budget for IVR traffic.

## Quotas & limits

- **Intents per bot**: 250+ (raisable).
- **Slots per intent**: 100.
- **Sample utterances per intent**: 1,500.
- **Bot versions per account per Region**: 100+.
- **Concurrent voice sessions**: bounded; raisable.

## Common pitfalls

- **Lex for open-ended chat.** It's intent-and-slot oriented. For free-form conversation, Bedrock Agents fits better.
- **Few sample utterances per intent.** Lex generalizes from examples; sparse training = brittle intent matching. Aim for 10+ varied utterances per intent.
- **No fallback intent.** Out-of-scope input silently fails. Define `FallbackIntent` explicitly.
- **Slot validation only in Lambda.** Use built-in slot types where possible; faster and cleaner than custom validation Lambdas.
- **Direct deploy to prod without aliases.** A bad bot change breaks every conversation. Test on staging alias first.
- **Voice channels without rate planning.** Voice-per-second pricing adds up faster than text-per-request; model expected concurrent voice sessions.
- **Lex V1 for new bots.** Use V2; V1 is legacy.

## Pairs well with

- **Amazon Connect** — IVR voice front-end.
- [Transcribe](transcribe.md), [Polly](polly.md) — internal voice plumbing (Lex uses them).
- [Lambda](../compute/lambda.md) — fulfillment hooks.
- [Bedrock](bedrock.md) Knowledge Bases — for FAQ-style answers when no intent matches.
- [Comprehend](comprehend.md) — sentiment / entity enrichment on transcripts.
- [DynamoDB](../database/dynamodb.md), [RDS](../database/rds.md) — backing data for fulfillment.

## Pairs well with these repo pages

- [Bedrock](bedrock.md), [Transcribe](transcribe.md), [Polly](polly.md), [Q](q.md).

## Further reading

- [Amazon Lex documentation](https://docs.aws.amazon.com/lex/).
- [Lex V2 developer guide](https://docs.aws.amazon.com/lexv2/latest/dg/).
- [Bot lifecycle and versioning](https://docs.aws.amazon.com/lexv2/latest/dg/versioning-aliases.html).
- [Lex generative features](https://docs.aws.amazon.com/lexv2/latest/dg/generative-ai.html).
- [Lex with Amazon Connect](https://docs.aws.amazon.com/lexv2/latest/dg/contact-center-connect.html).
