# IAM (Identity and Access Management)

> **One-line summary.** AWS's authorization engine. Decides who (principal) can do what (action) to which resources (ARN), under what conditions.

## TL;DR
- The single most important AWS service to get right. Almost every breach involves IAM misuse.
- Use **IAM Identity Center** for humans (federation, SSO), **IAM roles** for workloads (EC2 instance profiles, ECS task roles, Lambda execution roles, IRSA / Pod Identity for EKS), **STS** for short-lived credentials. **No long-lived access keys** as a default.
- Three policy types matter most: **identity-based** (attached to user/role/group), **resource-based** (attached to a resource like an S3 bucket), and **SCPs** (org-wide guardrails in AWS Organizations).
- Evaluation logic (simplified): **explicit deny > explicit allow > implicit deny**, with SCPs, permission boundaries, session policies, and (for resource-based) cross-account considerations layering on top.
- Use **Access Analyzer** continuously — it surfaces unused permissions, external access, and validates policies before you ship them.

## When to use it
- Always. Every AWS API call is authorized through IAM.

## When NOT to use it
- For end-user / customer-facing authentication, use **Cognito** (or your IdP through Cognito or Identity Center). IAM is for AWS resource access by people and workloads you control.

## Key concepts

**Principal** — the actor making the request. Users, roles, AWS services, federated identities, and the root account.

**IAM User** — a long-lived identity. **Mostly avoid for humans** — use IAM Identity Center federation. IAM Users still appropriate for narrow service-account scenarios (e.g., third-party SaaS that doesn't support OIDC federation), and even then prefer rotating access keys and tight scope.

**IAM Role** — an identity with no long-lived credentials; assumed via STS by principals (humans or workloads) to get short-lived credentials. The right shape for everything workload-related.

**Group** — collection of users with common policies. Useful for organizing IAM Users; less relevant when humans federate via Identity Center.

**Policy** — JSON document declaring `Effect` (`Allow` / `Deny`) for `Action`s on `Resource`s under optional `Condition`s.

**Policy types:**
- **Identity-based** — attached to a user / group / role.
- **Resource-based** — attached to a resource (S3 bucket policy, KMS key policy, SQS queue policy, Lambda function policy). Can grant cross-account access without the consumer changing anything in their own account.
- **Permissions boundaries** — maximum permissions a role/user can have. Doesn't grant anything; only caps. Used to delegate role creation safely.
- **Service Control Policies (SCPs)** — in AWS Organizations, applied to accounts/OUs. Don't grant; only restrict. Org-wide guardrails (e.g., "no one can disable CloudTrail" or "no resources outside approved Regions").
- **Session policies** — passed to `AssumeRole` to further restrict the assumed session.
- **Resource Control Policies (RCPs)** — newer Organizations construct that restricts what *resource-based* policies can grant. Pairs with SCPs (which restrict identity-based).

**Evaluation logic (high level).** Effective permissions = intersection of (SCPs ∧ permissions boundary ∧ identity-based policies ∧ session policies) ∧ (resource-based, if applicable). Any explicit `Deny` at any layer wins. No allow anywhere = denied.

**STS (Security Token Service).** Issues short-lived credentials via `AssumeRole`, `AssumeRoleWithSAML`, `AssumeRoleWithWebIdentity`, `GetSessionToken`. Federated identities and cross-account role assumption all flow through STS.

**Instance profiles, task roles, execution roles, IRSA / Pod Identity** — service-specific ways of attaching a role to a compute identity so the SDK can transparently call `AssumeRole` and get credentials.

**Access Analyzer.** Continuously evaluates policies and surfaces:
- **External access** — resources reachable from outside your account / org.
- **Unused access** — IAM roles and permissions not used in N days.
- **Policy validation** — policy linting before you save.
- **Custom policy checks** — fail PRs that would grant overly broad permissions.

**Identity-Aware Sessions, Source Identity, MFA conditions.** Mechanisms for layering additional context on access — `aws:MultiFactorAuthPresent`, `sts:SourceIdentity`, IP restrictions, time restrictions.

## Pricing model

- **IAM itself is free.**
- **STS** is free for most operations.
- **Access Analyzer** has a small per-analyzed-resource fee for the unused-access analyzer; external-access analyzer is free.
- **IAM Identity Center** is free for the SSO service; you pay only for any underlying directory storage.

## Quotas & limits

- **Users per account**: 5,000 default.
- **Roles per account**: 1,000 default (raisable to ~5,000+).
- **Groups per account**: 300.
- **Inline policy size**: 2,048 chars (user/group), 10,240 (role).
- **Managed policy size**: 6,144 chars.
- **Policies attached to a role/user/group**: 10 managed + inline.
- **SCPs per OU**: 5 (raisable to 10).
- **Permissions boundaries**: one per user / role.

## Common pitfalls

- **Long-lived access keys for humans.** Federate humans via IAM Identity Center; the only "user" should be break-glass.
- **`*` in IAM policies.** `s3:*` on `*` is a backdoor. Use the smallest action set on the smallest resource set that works; iterate with Access Analyzer.
- **Granting the deploy role admin "for convenience."** Now the CI / CD role is a god account. Scope to what's actually deployed.
- **No permissions boundaries on developer-created roles.** Devs creating roles can escalate privileges accidentally. Apply a permissions boundary to all dev roles to cap the maximum scope.
- **SCPs that only `Deny`, never tested.** A new SCP can silently break workloads. Test in a dev OU first; use `Condition`s for narrow scope.
- **Forgetting resource-based policies in cross-account designs.** Identity-based policy must allow; resource-based must also allow (or be unset in same-account). Cross-account = both ends must allow.
- **`Resource: "*"` for `iam:PassRole`.** Lets a principal hand any role to any service — privilege escalation primitive. Scope `iam:PassRole` with `Resource:` to specific roles and `Condition` on the service.
- **Root account for daily ops.** Lock root (MFA, no access keys, credentials offline) and federate.
- **No `Condition`s on dangerous actions.** Add `aws:MultiFactorAuthPresent`, source IP, `aws:PrincipalOrgID` for cross-account boundaries.
- **Skipping Access Analyzer.** It's free for external access; the unused-access analyzer is the cleanest way to spot drift.

## Pairs well with
- [IAM Identity Center](iam-identity-center.md) — human access.
- **AWS Organizations + SCPs / RCPs** — org-wide guardrails.
- **AWS Access Analyzer** — continuous policy hygiene.
- **AWS CloudTrail** — record every IAM-evaluated call.
- **AWS Config + AWS Audit Manager** — compliance over IAM state.
- **AWS Secrets Manager / Parameter Store** — for any secrets that *do* need to exist (rather than IAM-roleable workloads).

## Pairs well with these repo pages
- [Security pillar](../../05-well-architected/security.md) — the principles IAM enforces.
- All compute pages — workloads consume IAM via instance profile / task role / execution role / IRSA / Pod Identity.

## Further reading
- [AWS IAM documentation](https://docs.aws.amazon.com/iam/).
- [IAM policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html).
- [IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html).
- [Service Control Policies and Resource Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html).
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).
