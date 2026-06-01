# Amazon Q (family)

> **One-line summary.** AWS's generative-AI assistant brand — multiple distinct products under the Q umbrella, each tailored to a use case (developer coding, enterprise knowledge, contact-center agent assist, BI, AWS console help).

## TL;DR

- **Amazon Q** is a *family of products*, not a single service. The shared idea: an LLM-powered assistant grounded in specific data sources for specific roles. The pricing, integration, and surface differ per product.
- The big five:
  - **Amazon Q Developer** — coding assistant in IDEs, CLI, and as a CI/CD agent.
  - **Amazon Q Business** — enterprise chat over your company's data (Slack, SharePoint, Confluence, S3, Salesforce, etc.).
  - **Amazon Q in Connect** — real-time agent assist for Amazon Connect contact centers.
  - **Amazon Q in QuickSight** — natural-language analytics + generative BI authoring (covered in [`../analytics/quicksight.md`](../analytics/quicksight.md)).
  - **Amazon Q in AWS Console** — chat-based help and operations guidance inside the AWS console.
- For developer-facing AI in your own apps, use **Bedrock** directly. The Q family is for ready-to-use, opinionated AI products inside specific AWS-owned surfaces.

## When to use which

| You want… | Use |
|---|---|
| Coding assistant in IDE / CLI / agentic code changes | **Q Developer** |
| Enterprise chatbot grounded in company knowledge | **Q Business** |
| Real-time agent assist in Amazon Connect | **Q in Connect** |
| Natural-language Q&A on top of QuickSight dashboards | **Q in QuickSight** |
| Chat help inside the AWS console | **Q in AWS Console** |
| Custom LLM-powered app in your codebase | [**Bedrock**](bedrock.md) (not Q) |

## When NOT to use it

- LLM features you'd build into your own product — use **Bedrock** directly; Q is for ready-made AWS-surface assistants.
- Multi-cloud / multi-vendor LLM strategies — Q is AWS-specific.

## Key concepts

### Amazon Q Developer

- **IDE plugins** (VS Code, JetBrains, Visual Studio, etc.) — inline code suggestions, chat, refactoring, test generation.
- **CLI** — `q chat` / `q translate` for shell tasks.
- **Agentic coding** — natural-language prompt → multi-file production-ready feature. Generates code, tests, and integration glue.
- **Code transformation** — Java upgrades, .NET porting, Oracle → PostgreSQL SQL conversion.
- **Security scanning** — flags vulnerabilities in suggested and existing code.
- **GitHub / GitLab integration** — Q Developer agents that operate on PRs.
- **Languages** — 25+ programming languages.
- **Pricing tiers** — Free (limited), Pro (per user/month for unlimited suggestions and advanced features).

### Amazon Q Business

- **Enterprise chatbot** grounded in your data sources: Slack, Teams, SharePoint, Confluence, Salesforce, ServiceNow, Jira, S3, Box, OneDrive, Google Drive, custom connectors.
- **Plugins / actions** — let the chatbot take actions in connected systems (create a Jira ticket, query Salesforce).
- **Apps** — custom mini-applications built on top of your Q Business assistant.
- **Identity** — integrates with **IAM Identity Center** for SSO + user-scoped data access.
- **Pricing** — per-user-per-month subscription (Lite, Pro tiers).
- **Q Apps** — turn natural-language prompts into reusable internal mini-apps.

### Amazon Q in Connect

- Real-time assistant for contact-center agents during voice/chat interactions.
- **Recommendations** — pulls from connected knowledge sources (S3 docs, Salesforce, ServiceNow, custom) as the conversation unfolds.
- **Generative responses** — drafts agent reply text grounded in policies / KB.
- **Step-by-step guides** — walks agents through troubleshooting workflows.
- Replaces the older "Amazon Connect Wisdom" branding.

### Amazon Q in QuickSight

See [`../analytics/quicksight.md`](../analytics/quicksight.md). Natural-language Q&A on top of QuickSight datasets; generative BI authoring (describe a dashboard in plain language, Q generates a starting point).

### Amazon Q in AWS Console

- In-console chat for "how do I do X in AWS?"
- Resource-aware (knows about resources in your account).
- Helps with troubleshooting, generating CLI / SDK code, explaining errors.
- Generally free; some advanced operations may have integration limits.

### Q Developer Agent for code review

Recent feature: an agent that reviews PRs against your codebase, flags issues, and proposes fixes. Often paired with GitHub / GitLab via webhooks.

## Pricing model (per Q product)

- **Q Developer** — Free tier (limited monthly chats / suggestions); Pro per user/month for unlimited usage and advanced features (Code Transformation, agentic features).
- **Q Business** — per user/month, with tiered features (Lite, Pro). Connector / data-source usage may be additional.
- **Q in Connect** — usage-based, tied to Amazon Connect agent / minute pricing.
- **Q in QuickSight** — see QuickSight pricing (per Author / Reader add-on).
- **Q in AWS Console** — generally free, included with AWS account.

## Quotas & limits

- **Q Developer**: per-month chat / suggestion limits in the free tier; unlimited on Pro.
- **Q Business**: per-account user counts, data source counts, document counts — generous, raisable.
- **Q in Connect**: integrates with Connect agent counts.
- **Q in QuickSight**: see QuickSight quotas.

## Common pitfalls

- **Treating Q as a single product.** It's a family; pick the right one for the surface and use case. Confusion is common.
- **Q Business without data-source planning.** Connecting every internal tool without thinking about access scope leaks confidential data across user boundaries. Map Identity Center groups → data-source permissions explicitly.
- **Q Developer Pro skipped for paid teams.** The free tier's monthly cap is restrictive for active development; the Pro tier is usually well worth it.
- **Q in Connect without curated knowledge sources.** Generic responses without grounding in your contact-center playbooks help no one. Curate sources first.
- **Building custom LLM apps on top of Q Business.** Q Business is an end-user product; for custom LLM features in your own app, go to **Bedrock**.
- **Expecting Q to do anything Bedrock can.** Q is an opinionated wrapper for specific roles. If your use case doesn't fit one of those roles, Bedrock + your own UI is the right path.

## Pairs well with

- [Bedrock](bedrock.md) — Q products use Bedrock-hosted models under the hood; you'd build a custom alternative on Bedrock if Q doesn't fit.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — auth for Q Business and others.
- **Amazon Connect** — host for Q in Connect.
- **QuickSight** — host for Q in QuickSight.
- **GitHub / GitLab / Bitbucket** — Q Developer integrations.
- **SharePoint / Confluence / Slack / Salesforce / ServiceNow / S3 / Jira / Teams** — Q Business connectors.

## Pairs well with these repo pages

- [Bedrock](bedrock.md), [QuickSight](../analytics/quicksight.md), [IAM Identity Center](../security-identity/iam-identity-center.md).

## Further reading

- [Amazon Q documentation hub](https://docs.aws.amazon.com/amazonq/).
- [Amazon Q Developer](https://aws.amazon.com/q/developer/).
- [Amazon Q Business](https://aws.amazon.com/q/business/).
- [Amazon Q in Connect](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-q-connect.html).
- [Amazon Q in QuickSight](https://docs.aws.amazon.com/quicksight/latest/user/quicksight-q.html).
- [Amazon Q in AWS Console](https://docs.aws.amazon.com/awsconsole/latest/userguide/amazon-q.html).
