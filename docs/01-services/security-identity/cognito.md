# Cognito

> **One-line summary.** Managed customer / end-user identity service. **User Pools** for signup/sign-in (your own user database, or federated via social/SAML/OIDC); **Identity Pools** for AWS-credential issuance to end users.

## TL;DR

- Use Cognito **User Pools** for "I have customers; they need to sign in and get a JWT to call my APIs." Federation, MFA, password policies, customizable flows, hosted UI, OAuth 2.0 / OIDC.
- Use **Identity Pools** to swap a Cognito (or third-party IdP) token for **AWS credentials** so end users can call AWS APIs directly (typical: an S3 upload from the browser without a server-side relay).
- **Big 2024 pricing change (effective Dec 1, 2024):** new **Lite / Essentials / Plus** tiers; **new user pools get 10K MAU free**; **pools created before Nov 22, 2024 keep the legacy 50K MAU free tier** unless you switch tiers. Picking a tier upgrade *or* migrating provider settings drops you into the new tiering.
- For workforce / employee access to AWS, use **IAM Identity Center**, not Cognito.
- Most teams use a User Pool and (optionally) an Identity Pool — the two play together but solve different problems.

## When to use it

- Customer-facing apps that need sign-up, sign-in, password management, MFA.
- Mobile / web SPAs that need to call API Gateway with a JWT.
- Apps that need to federate end users from Google / Facebook / Apple / SAML / OIDC.
- Browser / mobile clients that need temporary AWS credentials to call S3 / DynamoDB / etc. directly.

## When NOT to use it

- Workforce / employee access — use **IAM Identity Center**.
- B2B-only with one or two enterprise IdPs and no AWS-credential issuance — sometimes integrating directly with the IdP via your own JWT validation in API Gateway HTTP API authorizers is simpler and cheaper.
- Workloads where you want full identity ownership (custom DB, full UX control) and the Cognito limits are a constraint — pure self-built with libraries like NextAuth.js / Authlib may be more flexible.

## Key concepts

### User Pools

A managed user directory:

- **Sign-up / sign-in** with username, email, or phone. Custom attributes.
- **MFA** (SMS, TOTP, hardware FIDO2 / passkeys via the newer tiers).
- **Password policies** (length, character classes, history).
- **Hosted UI** — AWS-hosted sign-up/sign-in pages with customization.
- **OAuth 2.0 / OIDC** — User Pool acts as an OIDC provider; issues ID tokens, access tokens, refresh tokens.
- **Federation** — social (Google, Facebook, Apple), SAML, OIDC IdPs as identity sources.
- **Triggers (Lambda hooks)** — pre/post sign-up, pre/post auth, pre token generation, etc. The customization surface for adding business logic to auth flows.
- **Advanced security features (ASF)** — adaptive auth, risk-based scoring, compromised-credential checks. Available in the **Plus** tier (formerly billed separately).

### Identity Pools

- Take a token (Cognito ID token, social IdP token, SAML assertion, OIDC token) and exchange it for **AWS STS credentials** scoped to an IAM role.
- **Authenticated** and **unauthenticated** roles per pool.
- Common pattern: User Pool token → Identity Pool → STS credentials → call S3 / DynamoDB with the user's role.

### Pricing tiers (effective Dec 1, 2024)

- **Lite** — basic sign-up / sign-in, social federation. Cheapest per MAU, 10K MAU free tier.
- **Essentials** — adds passwordless sign-in, custom email/SMS senders, broader auth flows. 10K MAU free tier.
- **Plus** — adds ASF (adaptive auth, threat detection, compromised credentials). Replaces the previously separate ASF pricing.
- **Federated** — SAML / OIDC federation has its own tier with **50 MAU free per month regardless of pool tier**.
- **Pools created before Nov 22, 2024** keep the **legacy 50K MAU free tier**. **Changing tiers drops a legacy pool to 10K free** — verify carefully before flipping a setting.

### Tokens and validation

- **ID token** — proves identity (claims about the user).
- **Access token** — used to call protected APIs; contains scopes.
- **Refresh token** — used to get new ID/access tokens.

API Gateway **HTTP API JWT authorizers** validate Cognito tokens natively — no Lambda authorizer needed for the common case.

### Hosted UI vs custom UI

- **Hosted UI** — AWS-hosted pages; quickest to ship; customization is CSS-level.
- **Custom UI** — build your own using `amplify-js` / `cognito-identity-provider` SDKs; full control.

## Pricing model

- **Per MAU per month** in each tier (Lite cheapest, Plus most expensive).
- **Federated MAU** billed separately.
- **SMS messages for MFA** at standard SNS SMS rates.
- **No charge** for tokens issued, hosted UI usage, or trigger Lambda invocations beyond standard Lambda billing.

The pricing tier change in 2024 was significant — re-evaluate cost if you have a moderately-sized pool that crossed the 10K-vs-50K free-tier line.

## Quotas & limits

- **User pools per account per Region**: 1,000.
- **Identity pools per Region**: 1,000.
- **Apps per user pool**: 1,000.
- **Federated IdPs per user pool**: 33 (1 SAML + 32 OIDC + social).
- **Triggers** — bounded; per-flow Lambda invocations count toward Lambda concurrency.
- **Rate limits** — per-action throttle on most APIs (e.g., sign-ups per second per pool).

## Common pitfalls

- **Switching a legacy pool to a new tier without re-running the cost math.** Pre-Nov-2024 pools have a 5× more generous free tier; flipping tiers drops you to 10K MAU free, which for a 40K-MAU app can mean a multi-hundred-dollar/month bump.
- **Using Cognito for workforce SSO.** Identity Center is the right answer for employees accessing AWS. Cognito is for *your* customers.
- **Unauthenticated Identity Pool with overly broad IAM role.** Anyone hitting your site gets temporary AWS credentials with that role's permissions. Scope tightly; usually a small `s3:GetObject` for a specific prefix is the most you want.
- **Building your own UI without using the SDKs.** Implementing the OAuth flows by hand is error-prone. Use the AWS Amplify SDKs or a well-maintained OIDC client library.
- **No Lambda trigger for atomic side effects.** Post-confirmation triggers run *after* the user is confirmed; failures don't roll the sign-up back. Make trigger logic idempotent and retry-safe; consider compensating logic on failure.
- **Lite tier when you need ASF.** Adaptive auth and risk scoring are Plus-tier features now; if your threat model needs them, budget for Plus from day one.
- **Per-Region pools for global apps without a strategy.** Cognito User Pools are Region-scoped; there's no managed multi-Region replication. Cross-Region failover for identity needs application-level coordination.
- **Forgetting to validate JWTs server-side.** Even with API Gateway JWT authorizers, custom backends accepting Cognito tokens directly must validate signature, issuer, audience, expiration.

## Pairs well with

- [API Gateway](../networking/api-gateway.md) — JWT authorizer validates Cognito tokens.
- **Lambda** — trigger-based custom flows.
- **S3 / DynamoDB / AppSync** — direct end-user access via Identity Pool credentials.
- **Amplify** — the SDK / UI library most teams reach for.
- **External IdPs** — federate from Google / Facebook / Apple / SAML / OIDC.

## Pairs well with these repo pages

- [IAM Identity Center](iam-identity-center.md) — the workforce-identity counterpart.
- [API Gateway](../networking/api-gateway.md), [Verified Permissions](verified-permissions.md).

## Further reading

- [Amazon Cognito documentation](https://docs.aws.amazon.com/cognito/).
- [Cognito User Pool feature plans (Lite / Essentials / Plus)](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html).
- [Cognito pricing](https://aws.amazon.com/cognito/pricing/).
- [User Pool triggers](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools-working-with-aws-lambda-triggers.html).
- [Identity Pools overview](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html).
