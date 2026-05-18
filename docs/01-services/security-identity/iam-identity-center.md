# IAM Identity Center

> **One-line summary.** AWS's SSO and centralized human-identity service. Federate from your IdP (Okta, Azure AD/Entra, Google Workspace, JumpCloud) or use the built-in directory; map identities to permission sets that map to roles in each AWS account.

## TL;DR
- The right way to give humans access to AWS. Replaces long-lived **IAM Users** entirely for workforce access.
- Formerly "AWS Single Sign-On (SSO)" — renamed to **IAM Identity Center**.
- Identity source: built-in directory, Active Directory (Managed AD or AD Connector), or external SAML / OIDC IdP (Okta, Entra, Google Workspace, JumpCloud, OneLogin).
- **Permission sets** are reusable bundles of IAM policies; you map (Group, AWS Account, Permission Set) → access.
- Users get a personal **start page URL**, see all accounts they can access, and pick a permission set per session. Short-lived STS credentials, optional MFA, CLI helper for the terminal.

## When to use it
- Any AWS Organization with more than one person needing AWS access. Mandatory at production scale.
- Replacing legacy "shared IAM User with everyone has the password" patterns.
- Multi-account access (the common AWS Organizations pattern) — Identity Center is the access control plane.
- Federating from corporate IdP so workforce joiners/leavers flow through standard HR processes.

## When NOT to use it
- Customer / end-user authentication — use **Cognito** instead.
- Pure machine-to-machine — use **IAM roles** and STS, not Identity Center.
- Tiny single-account / single-engineer accounts — IAM Users with MFA can be acceptable (though Identity Center is still preferred).

## Key concepts

**Identity source.**
- **Identity Center directory** — built-in, AWS-managed. Easy starting point.
- **Active Directory** — AWS Managed Microsoft AD or AD Connector to on-prem.
- **External IdP** — SAML 2.0 (Okta, Entra ID, Google Workspace, JumpCloud, etc.). The most common choice in enterprises.

Only one identity source per Identity Center instance.

**Permission set.** A reusable bundle of:
- Inline policies and/or managed policies.
- A permissions boundary.
- A session duration (1 h – 12 h).
- A relay state (where to land after login).

Behind the scenes, when you assign a permission set to an account, Identity Center creates an IAM role named `AWSReservedSSO_<permission-set-name>_<hash>` in that account.

**Assignment.** `(group or user) × (AWS account or OU) × (permission set)`. Group-based assignments scale far better than user-based.

**Account assignments via IaC.** Define permission sets and assignments in CloudFormation / CDK / Terraform. Manual assignments drift; codified ones don't.

**Application access.** Identity Center can also broker SSO into SaaS apps (the AWS-published catalog of pre-integrated apps, custom SAML/OIDC apps, and AWS-managed apps like QuickSight or Amazon Q).

**Multi-account access in the console.** Users land on `https://<your-prefix>.awsapps.com/start`, see all accessible accounts + permission sets, and pick one to enter the AWS console session for that account/role.

**CLI access.** `aws sso login` opens a browser to authenticate; `aws sso configure` sets up profiles. AWS SDKs natively understand SSO profiles since 2022.

**Trusted token issuers.** Identity Center can vend short-lived JWTs that downstream apps trust — useful for app-level SSO from the same identity.

**Auto-provisioning (SCIM).** Workforce changes (joiner / mover / leaver) sync from the IdP via SCIM. Groups and group memberships propagate automatically.

## Pricing model

- **IAM Identity Center is free.**
- AWS Managed Microsoft AD (if used as the identity source) has its own per-hour fee.
- External IdP — pay whatever your IdP charges.
- No per-user-per-month fee for Identity Center itself.

## Quotas & limits

- **Permission sets per Identity Center instance**: 500.
- **Permissions per permission set**: 10 managed policies + 1 inline (with size limits).
- **Maximum assignment combinations**: scales with org size; high.
- **Session duration**: 1 h – 12 h per permission set.
- **Group members and groups**: large (high thousands) — limits effectively determined by your IdP.

## Common pitfalls

- **User-based assignments instead of group-based.** Every joiner/leaver needs manual changes. Use groups; provision through SCIM.
- **One mega-permission-set "Admin" for everyone.** Real teams need scoped permission sets per role (developer, read-only, billing, etc.). Use job-function-aligned permission sets.
- **Long session durations on admin permission sets.** Default 1 h is fine; 12 h on a `AdministratorAccess` set is a credential-theft surface. Keep admin sessions short.
- **Identity Center in `us-east-1` "because that's where everything is" without considering recovery.** Identity Center is regional — losing the chosen Region affects access. Some teams place Identity Center in a non-`us-east-1` Region to decorrelate from `us-east-1` events.
- **Account assignments managed in the console.** Drift, no audit trail. Codify in IaC.
- **Forgetting to set the permissions boundary on permission sets.** Without it, an admin assigned to a permission set can create roles outside the scope. Apply boundaries where it matters.
- **Two parallel identity sources (e.g., legacy IAM Users + Identity Center).** Confusing, harder to audit. Migrate cleanly.
- **No break-glass plan.** Identity Center / external IdP failures lock you out. Keep a small set of root or break-glass IAM roles with hardware-MFA credentials in a sealed envelope.

## Pairs well with
- [IAM](iam.md) — Identity Center provisions IAM roles per account.
- **AWS Organizations** — multi-account boundary.
- **AWS Managed Microsoft AD / AD Connector** — directory backend.
- **External IdP** (Okta, Entra ID, Google Workspace) — source of identity.
- **AWS CLI v2** — built-in SSO support.

## Pairs well with these repo pages
- [Security pillar](../../05-well-architected/security.md) — the "centralize identity" principle.
- `docs/04-reference-architectures/multi-account-organization.md` (forthcoming).

## Further reading
- [IAM Identity Center documentation](https://docs.aws.amazon.com/singlesignon/).
- [Identity sources overview](https://docs.aws.amazon.com/singlesignon/latest/userguide/manage-your-identity-source-sso.html).
- [Permission sets](https://docs.aws.amazon.com/singlesignon/latest/userguide/permissionsetsconcept.html).
- [Best practices for IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/security-best-practices.html).
