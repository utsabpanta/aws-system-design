# Contributing to aws-system-design

Thanks for wanting to add a page. The goal of this repo is a consistent, opinionated, GitHub-renderable reference. The conventions below exist to keep new pages indistinguishable from the ones already here.

## Table of contents
- [Ground rules](#ground-rules)
- [Page template](#page-template)
- [Service page template (condensed)](#service-page-template-condensed)
- [Diagram conventions](#diagram-conventions)
- [Adding a new page](#adding-a-new-page)
- [Local checks before opening a PR](#local-checks-before-opening-a-pr)
- [Commit sign-off (DCO)](#commit-sign-off-dco)

---

## Ground rules

- **Tone:** technical, neutral, opinionated where it matters. No marketing language.
- **Accuracy:** any quantitative claim (latency, throughput, quota, price) must be verified against current AWS docs or omitted with a link out.
- **Length budgets:** service pages 600–1200 words; interview designs 1500–3500 words; reference architectures 1000–2500 words. Avoid filler.
- **No reproduced AWS docs.** Paraphrase. Link out for canonical reference.
- **No console screenshots.** Diagrams are code-rendered.
- **No real customer data** in examples (no real names, account IDs, customer identifiers).
- **One concept per file.** New service? New file. New design? New file.
- **Spelling locale:** US English.

---

## Page template

Every page under `docs/01-services/`, `docs/03-interview-designs/`, and `docs/04-reference-architectures/` follows this template. Sections marked *(interview/ref-arch only)* are skipped on service pages — see the [condensed template](#service-page-template-condensed) below for those.

```markdown
# <Title>

> **One-line summary.** What this is, in plain language.

## TL;DR
3–5 bullets. Senior engineer scanning before a meeting should be unblocked.

## When to use it / When NOT to use it
Two short lists. Be opinionated.

## Functional Requirements
*(Interview designs and reference architectures only.)*

## Non-Functional Requirements
Latency, throughput, availability targets, consistency, durability, cost ceiling.

## Capacity Estimates
*(Interview designs only.)* DAU, QPS, storage growth, bandwidth.

## High-Level Architecture
Diagram here. Either Mermaid inline, or `![](../../images/.../foo.png)` for `diagrams` output.
Below the diagram: 4–8 sentences walking through the flow.

## Data Model
ERD (Mermaid `erDiagram`) plus table-by-table notes. Call out partition keys, sort keys, GSIs for DynamoDB.

## API Design
HTTP verbs, paths, request/response shapes. Or event schemas for async.

## Deep Dives
### <Hard Part #1>
### <Hard Part #2>
### <Hard Part #3>
Each deep dive: state the problem, two or three candidate solutions, the trade-offs, and what you'd pick and why.

## AWS Services Used
Bulleted list with one-line justification per service.

## Cost Notes
Order-of-magnitude cost shape, the big drivers, the levers to pull.

## Failure Modes & DR
What breaks first under load. What an AZ failure looks like. What a Region failure looks like.

## Trade-offs & Alternatives
Honest about what this design gives up. Mention non-AWS alternatives at the component level (e.g., Kafka instead of Kinesis) where relevant.

## Further Reading
Official AWS docs, AWS Architecture Center, re:Invent talks, papers.
```

## Service page template (condensed)

Pages under `docs/01-services/` use a smaller template — you're documenting a service, not a system.

```markdown
# <Service Name>

> **One-line summary.**

## Status
Active / Closed to new customers / Deprecated (with a link to the AWS announcement). Skip the section if active.

## TL;DR
3–5 bullets.

## When to use it / When NOT to use it
Two short opinionated lists.

## Key concepts
The vocabulary you need to read the AWS docs without bouncing off.

## Pricing model
The dimensions you actually pay for. Order of magnitude, not exact prices.

## Quotas & limits
Hard limits that bite at scale. Link to the official quotas page.

## Common pitfalls
Things that surprise people in production.

## Pairs well with
Other AWS services this is typically deployed alongside, and why.

## Further reading
```

---

## Diagram conventions

The diagram tool selection rule:
- **Mermaid** for flows, sequence, state machines, ERDs, simple block diagrams. Inline in the markdown — GitHub renders it natively.
- **Python `diagrams`** (mingrammer/diagrams) for AWS architecture diagrams that need the official AWS icons. Commit both the `.py` source and the rendered `.png`.

### Mermaid
- Use ```` ```mermaid ```` fenced blocks.
- Prefer `flowchart LR` for request flows, `sequenceDiagram` for interactions, `stateDiagram-v2` for state machines, `erDiagram` for data models.
- Label nodes with the AWS service name in brackets: `APIGW[API Gateway]`.
- Solid arrows for synchronous calls; dashed arrows for async / fire-and-forget.
- Cap at ~25 nodes per diagram. Split larger ones.

### Python `diagrams`
- Source lives in `diagrams/python/<category>/<slug>.py`, mirroring the markdown path.
  Example: `docs/03-interview-designs/url-shortener.md` → `diagrams/python/interview-designs/url_shortener.py`.
- Rendered output lives in `images/<category>/<slug>.png`.
- Use the official AWS provider imports: `from diagrams.aws.compute import Lambda`, etc.
- File header docstring should name the page the diagram belongs to and give a one-line description.
- Default direction: `LR` for request flows, `TB` for layered architectures.
- Run `./scripts/render_diagrams.sh` to regenerate all diagrams. Commit both source and output.

### Diagram self-review checklist
Before committing a diagram, confirm:
1. Every box has a service name (no orphan labels).
2. Arrow direction conveys data flow, not just dependency.
3. Sync vs async paths are visually distinguished (solid vs dashed in Mermaid; comment in `diagrams` Python).
4. Multi-AZ / multi-Region is shown explicitly when it matters.
5. External clients and internal services are visually separated (use clusters / subgraphs).

---

## Adding a new page

The easiest path:

```sh
./scripts/new_page.sh <kind> <slug>
# examples:
./scripts/new_page.sh service compute/app-runner
./scripts/new_page.sh design real-time-leaderboard
./scripts/new_page.sh refarch streaming-etl-kinesis
./scripts/new_page.sh pattern outbox
```

`new_page.sh` drops a templated markdown file at the right path. Fill it in, add diagrams, then open a PR.

If the page needs a `diagrams` Python rendering, also create the matching `.py` file under `diagrams/python/` and run `./scripts/render_diagrams.sh`.

After adding, renaming, or removing a page, regenerate the README table of contents:

```sh
./scripts/build_toc.sh
```

CI runs `scripts/build_toc.py --check` and fails if the README is out of sync.

---

## Local checks before opening a PR

```sh
pre-commit run --all-files
```

That runs (per `.pre-commit-config.yaml`):
- `markdownlint` over all `.md` files
- `cspell` over all `.md` files (project dictionary is `.cspell.json`)
- `lychee` link check
- Mermaid syntax validation on every ```` ```mermaid ```` block

CI will run the same checks plus a `README.md` TOC sync check, and a diagram-sync check on PRs that touch `diagrams/python/`.

If your PR introduces a new word that trips cspell (an acronym, a service name, a person's name), add it to `.cspell.json` rather than ignoring the check.

---

## Commit sign-off (DCO)

Every commit must be signed off under the [Developer Certificate of Origin](https://developercertificate.org/). Add a `Signed-off-by` trailer:

```sh
git commit -s -m "Add Aurora Serverless v2 page"
```

The trailer reads:

```
Signed-off-by: Your Name <your.email@example.com>
```

By signing off you're asserting you wrote the change (or have the right to submit it) and agree it can be distributed under the project's [MIT license](LICENSE).
