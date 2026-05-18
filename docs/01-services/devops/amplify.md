# Amplify

> **One-line summary.** End-to-end framework for building and hosting web and mobile apps on AWS — Gen 2 unifies the front-end framework, backend provisioning (in TypeScript), and **Amplify Hosting** for static / SSR / SPA deployment.

## TL;DR
- Two-ish products under one name:
  - **Amplify Hosting** — Vercel / Netlify-style static / SSR / SPA hosting on AWS. Push to Git; Amplify builds and deploys.
  - **Amplify Gen 2** (replacing Gen 1) — TypeScript-first backend builder. Define auth (Cognito), data (AppSync + DynamoDB), storage (S3), functions (Lambda), real-time (AppSync subscriptions). One repo, full-stack, branch-based environments.
- For greenfield React / Next.js / Vue / Angular apps that want auth + API + DB + hosting end-to-end, Amplify Gen 2 is the most opinionated path.
- For just-hosting (no AWS-managed backend), **Amplify Hosting** alone competes with Vercel / Netlify / Cloudflare Pages.
- Compared to building each piece yourself (Cognito + AppSync + DynamoDB + Lambda + S3 + CloudFront): Amplify's value is the integration story and code generation; the cost is opinion / lock-in.

## When to use it
- Greenfield React / Next.js / Vue / Angular / Svelte apps on AWS.
- Teams that want full-stack scaffolding (auth + data + storage + hosting) in one repo.
- Mobile apps (iOS / Android / Flutter / React Native) consuming AWS services.
- Static-site hosting with branch-based preview environments.
- Server-side rendered Next.js apps that want AWS-native hosting (instead of Vercel).

## When NOT to use it
- Teams already standardized on Vercel / Netlify / Cloudflare for hosting and AWS for backend.
- Backends that don't fit the Amplify Gen 2 model (large microservice meshes, EKS-resident apps, complex EventBridge flows).
- Workloads where the team wants to write CDK / Terraform directly without an Amplify abstraction layer.

## Key concepts

### Amplify Hosting
- **Git-connected** — connect a GitHub / GitLab / Bitbucket / CodeCommit repo.
- **Branch-based environments** — `main` → prod, `staging` → staging, every feature branch → preview URL.
- **Build settings** — YAML in `amplify.yml` for the build commands and output directory.
- **Frameworks** — first-class support for Next.js (SSR + ISR), React, Vue, Angular, Svelte, Nuxt, Gatsby, Hugo, plus static sites.
- **Custom domains** with ACM certs + Route 53 integration.
- **Edge functions** — small JS functions at CloudFront edge (Amplify-managed).
- **Atomic deploys + rollback** to any previous build.
- **Password protection** for non-prod environments.
- **Monorepo support** — multiple apps from one repo.

### Amplify Gen 2 (backend builder)
- **TypeScript-first** — define backend as TypeScript code (`amplify/backend.ts`).
- **Auth** — Cognito User Pool / Identity Pool, social federation, email/password, magic links.
- **Data** — AppSync GraphQL API (or REST), DynamoDB / Aurora / OpenSearch backing, fine-grained authorization rules in TypeScript.
- **Storage** — S3 buckets with per-user / per-group access patterns.
- **Functions** — Lambda functions with environment, IAM, schedule, event triggers.
- **AI** — pre-built components for Bedrock + AppSync (chatbot, generation).
- **Auth + data + storage authorization rules** defined inline; Amplify generates the correct IAM + Cognito + GraphQL policies.
- **Branch-based backends** — every Git branch gets its own backend environment.

### Amplify Gen 1 (legacy)
The previous Amplify CLI + JSON config approach. Still supported but Gen 2 is the recommended new-project path.

### Amplify libraries (client)
- **`amplify/auth`**, **`amplify/data`**, **`amplify/storage`**, **`amplify/predictions`** — TypeScript / Swift / Kotlin / Dart / Flutter SDKs that wrap Cognito / AppSync / S3 / Lex / Polly / Transcribe with conventional APIs.
- Auto-configured from the deployed backend.

### Hosting features
- **Build-time SSR / ISR support** for Next.js.
- **Image optimization** at edge.
- **Headers, redirects, rewrites** declared in config.

## Pricing model

### Amplify Hosting
- **Build minutes** — per build-minute.
- **Storage** — per GB-month for hosted artifacts.
- **Data transfer** — per GB served.
- **SSR compute** — for Next.js SSR / ISR: per request + per million function invocations (similar shape to Lambda).

### Amplify Gen 2 backend
- The Amplify backend service is **free**.
- You pay for the underlying AWS resources (Cognito MAUs, AppSync requests, DynamoDB capacity, Lambda invocations, S3 storage).

## Quotas & limits

- **Apps per account per Region** (Hosting): 100s, raisable.
- **Branches per app**: 50.
- **Backend environments per branch**: typically 1.
- **Build timeout**: 30 min default.
- **Resource limits inherited** from the underlying services (Cognito, AppSync, DynamoDB, etc.).

## Common pitfalls

- **Amplify Gen 1 for new projects.** Gen 2 is the recommended path; Gen 1 is in legacy support.
- **Amplify Gen 2 backend for use cases it doesn't fit.** It's opinionated; complex microservice meshes or EKS workloads belong in CDK / direct services.
- **Hosting cost surprise.** SSR Next.js apps with high traffic can ring up real bills; understand the per-invocation + data-transfer model before committing.
- **Branch-based backend sprawl.** Every dev branch = a full backend environment. Lifecycle / clean up.
- **Cross-environment data assumption.** Each branch has its own DynamoDB / S3; "I'll just copy data between environments" needs explicit tooling.
- **Auto-generated IAM not reviewed.** Amplify generates IAM; review for over-permissive rules before production.
- **Auth state across mobile + web inconsistent.** Same Cognito User Pool across platforms works, but UX details (refresh, session expiry) need explicit handling.

## Pairs well with
- [Cognito](../security-identity/cognito.md), **AppSync** (GraphQL), [DynamoDB](../database/dynamodb.md), [S3](../storage/s3.md), [Lambda](../compute/lambda.md) — backing services.
- [Bedrock](../ml-ai/bedrock.md) — AI components inside Amplify Gen 2.
- [Route 53](../networking/route53.md), [ACM](../security-identity/acm.md) — custom domains and TLS.
- [CloudFront](../networking/cloudfront.md) — sits under Amplify Hosting for delivery.
- [CDK](cdk.md) — Amplify Gen 2 compiles to CDK; you can drop into CDK for what Amplify abstracts away.

## Pairs well with these repo pages
- [Cognito](../security-identity/cognito.md), [DynamoDB](../database/dynamodb.md), [Lambda](../compute/lambda.md), [CDK](cdk.md).
- `docs/04-reference-architectures/static-website-s3-cloudfront.md` (forthcoming).

## Further reading
- [AWS Amplify documentation](https://docs.amplify.aws/).
- [Amplify Gen 2 (TypeScript-first)](https://docs.amplify.aws/react/build-a-backend/).
- [Amplify Hosting](https://docs.aws.amazon.com/amplify/).
- [Migrating from Gen 1 to Gen 2](https://docs.amplify.aws/react/start/migrate-from-gen1/).
- [Amplify libraries](https://docs.amplify.aws/react/build-a-backend/).
