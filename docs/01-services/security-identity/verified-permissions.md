# Verified Permissions

> **One-line summary.** Managed authorization service for *your own* applications. Defines and evaluates fine-grained access policies in **Cedar**, the open-source policy language AWS created.

## TL;DR

- The "authorization-as-a-service" piece you'd otherwise build in every app: "can this user perform this action on this resource, given context X?"
- Policies in **Cedar** — declarative, statically analyzable, supports ABAC / RBAC / ReBAC patterns.
- Integrates natively with **Cognito** (User Pool groups, attributes as principal claims) for the common "Cognito + my app" case.
- The right answer when you need expressive permissions in a customer-facing app, multi-tenant SaaS, or document-sharing-style ReBAC — and don't want to build your own permission engine.
- Less essential for apps with simple role-based access (just check a role claim in your code) — Verified Permissions shines when permissions get complex.

## When to use it

- Multi-tenant SaaS with per-tenant, per-resource, per-action authorization.
- Document-sharing / collaboration apps with sharing rules.
- B2B apps with customer-managed roles and policies (delegated admin).
- Apps where the authorization layer needs to be auditable / verifiable separately from the app code.
- Workloads that already use Cedar (Verified Access, IAM) and want consistent policy semantics.

## When NOT to use it

- Simple role-checks in your app — `if user.role == "admin"` doesn't need a service.
- Latency-critical inner-loop checks where the round-trip to Verified Permissions doesn't fit the budget. (Use local Cedar evaluation in your service via the open-source SDK; Verified Permissions caches help, but a service call is a service call.)
- Workloads outside AWS where the network round-trip dominates.

## Key concepts

**Policy store.** A logical container for policies, schemas, and identity sources.

**Schema.** Declares your app's entity types (e.g., `User`, `Document`, `Folder`), their attributes, and the actions that can be performed on them. Cedar uses the schema to type-check policies — catches errors before they fail at runtime.

**Cedar policies.**

```cedar
permit(
  principal in Group::"Engineers",
  action == Action::"EditDocument",
  resource
)
when {
  resource.owner == principal ||
  resource.shared_with.contains(principal)
};
```

Three styles often combined:

- **RBAC** — principal in group.
- **ABAC** — `when { context.region == "us-east-1" }`.
- **ReBAC** — relationship-based: "user is in the group that owns the parent folder of this document."

**Identity source.** Identity Provider that supplies principal claims:

- **Cognito User Pool** — direct integration; user pool groups and attributes become principal claims automatically.
- **OIDC IdP** — generic OIDC connection.

**Templates and template-linked policies.** Reusable policy templates with placeholders. Used heavily for "share this document with this user" patterns where you mint a template-linked policy per share.

**`IsAuthorized` API.** Your app calls Verified Permissions with `(principal, action, resource, context)`; service returns ALLOW or DENY plus the policy that decided. Sub-100ms latency typical.

**`IsAuthorizedWithToken`** — pass the JWT from Cognito / OIDC IdP directly; Verified Permissions extracts claims as principal attributes.

**Local Cedar evaluation.** The Cedar language is open source and embeddable. For latency-critical paths, run Cedar policies in-process; sync them from Verified Permissions.

**Policy auditing.** Every authorization decision can be logged for audit. Useful for proving compliance ("show me all access decisions on this resource last month").

## Pricing model

- **Per million authorization requests.**
- **Per policy stored** — small per-policy-per-month fee.
- Volume-tiered.

For low-call-volume apps, the cost is small. For very high-RPS apps, evaluate local Cedar evaluation as an optimization.

## Quotas & limits

- **Policy stores per account per Region**: 100.
- **Policies per policy store**: 1 million.
- **Templates per policy store**: 50.
- **Schema size**: bounded.
- **Authorization requests per second**: high (auto-scales).

## Common pitfalls

- **Building your own permission engine alongside Verified Permissions.** Pick one — either Cedar everywhere (consistent semantics) or a custom engine. Mixing is the worst of both worlds.
- **Schema as an afterthought.** Without a schema, policy errors are runtime, not compile-time. Define the schema before writing policies.
- **Template-linked policy explosion.** A "share with user" pattern creates a policy per share. Millions of shares = millions of policies = pricing pressure and harder reasoning. Consider whether the share semantics can be expressed as a permission relationship instead.
- **`IsAuthorized` on the hot path without caching.** Sub-100ms is fast, but compounded across many checks per request adds up. Batch with `BatchIsAuthorized` where possible; cache same-result decisions in the calling service.
- **Identity source not configured.** Calling `IsAuthorizedWithToken` without an identity source = errors. Wire Cognito / OIDC IdP up front.
- **Forgetting audit logs.** Authorization decisions are exactly the events compliance auditors want. Log them to CloudWatch / S3.

## Pairs well with

- [Cognito](cognito.md) — native identity source.
- [Verified Access](verified-access.md) — sibling service; also uses Cedar.
- [API Gateway](../networking/api-gateway.md), [Lambda](../compute/lambda.md) — call `IsAuthorized` from request handlers.
- **Cedar SDK** — local evaluation for latency-critical paths.

## Pairs well with these repo pages

- [Cognito](cognito.md), [Verified Access](verified-access.md), [IAM](iam.md).

## Further reading

- [Amazon Verified Permissions documentation](https://docs.aws.amazon.com/verifiedpermissions/).
- [Cedar language reference](https://docs.cedarpolicy.com/).
- [Cedar policy validation against schemas](https://docs.cedarpolicy.com/policies/validation.html).
- [Cognito integration](https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/identity-providers.html).
- [Verified Permissions pricing](https://aws.amazon.com/verified-permissions/pricing/).
