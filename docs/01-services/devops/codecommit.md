# CodeCommit

> **One-line summary.** AWS-managed private Git repositories. **Reopened to new customers on November 24, 2025** after a 16-month closure — back to general availability with new feature investment.

## Status

> 🟢 **CodeCommit is back to GA.** AWS reopened CodeCommit to new customers on **November 24, 2025**, reversing the July 2024 closure. New customers can create repositories again. AWS announced **Git LFS support planned for Q1 2026** and **regional expansion to `eu-south-2` and `ca-west-1` planned for Q3 2026**.
>
> Between July 25, 2024 and November 24, 2025, only existing customers could create new repositories. That period is over — the service is fully back.

## TL;DR

- Managed private Git on AWS. IAM-controlled access, SSH or HTTPS, no infrastructure to operate.
- After a 16-month closure to new customers (June 2024 – November 2025), CodeCommit is back to GA with new investment.
- Reasonable choice when you want Git inside AWS without GitHub / GitLab / Bitbucket and you prefer to keep code, IAM, KMS, and CI all in one cloud.
- Most teams in 2026 use **GitHub** or **GitLab** for source control, with AWS CI/CD services (CodeBuild, CodeDeploy, CodePipeline) plugged in via webhooks or OIDC. CodeCommit remains a valid alternative for AWS-native teams.
- Standard Git semantics — `git clone`, `git push`, branch protection (via IAM policies), pull requests via the AWS console.

## When to use it

- Teams that want a single-cloud setup with AWS-controlled source code, IAM-aligned access, and KMS encryption.
- Regulated workloads where keeping source on AWS infrastructure is required.
- Workloads with tight integration to other AWS services (CodeBuild, CodePipeline, CodeArtifact, CodeGuru) where the AWS-native source store is convenient.

## When NOT to use it

- Teams already deeply invested in GitHub / GitLab / Bitbucket ecosystems (PR workflows, marketplace integrations, community).
- Workloads where open-source collaboration matters — public GitHub is the de facto standard.
- Teams using GitHub Copilot / GitHub Actions / GitHub Advanced Security where reproducing the experience on CodeCommit isn't feasible.

## Key concepts

**Repository.** Standard Git repo. Created per AWS account, in a specific Region.

**Access:**

- **HTTPS** with Git credentials generated for an IAM user (legacy pattern).
- **HTTPS-GRC** (git-remote-codecommit) — STS-based authentication, recommended for federated identities / SSO users.
- **SSH** with public-key auth on an IAM user (legacy).
- **AWS SDK** — list / clone / push programmatically with IAM credentials.

For modern setups with **IAM Identity Center** federation, HTTPS-GRC is the right default.

**Branches and PRs.** Standard Git branches; AWS console (and SDK / CLI) supports pull requests with approval rules, approval rule templates, and approval requirements.

**Triggers.**

- **CloudWatch / EventBridge events** on repo activity (push, PR creation, comment).
- **SNS notifications** on events.
- **CodePipeline** can use CodeCommit as a source.

**Branch protection.** Enforced via IAM resource policies — restrict who can push to specific branches.

**Encryption.** KMS at rest (default `aws/codecommit` key or CMK); TLS in transit.

**Cross-account / cross-Region.** Cross-account via IAM role assumption; cross-Region via your own replication (Git mirroring) — no built-in cross-Region replication.

**Mirroring.** Many teams mirror CodeCommit ↔ GitHub for hybrid setups during migration / experimentation.

## Pricing model

- **Free tier**: 5 active users per month, 50 GB storage, 10,000 Git requests/month.
- **Beyond free**: $1.00 / additional active user / month.
- **Storage**: free in the active-user fee; large repos can negotiate.
- **Git requests**: included up to a per-user threshold.

Genuinely cheap for most teams. The 5-user free tier is generous for small teams or open-source workflows.

## Quotas & limits

- **Repositories per account per Region**: 1,000 default (raisable).
- **Repository size**: 4-byte files default; effectively unlimited storage for code (large binaries → Git LFS once supported, planned Q1 2026).
- **Files per repo**: very high.
- **Branches per repo**: very high.
- **Concurrent users / requests**: high; AWS-managed scaling.
- **Approval rules** per PR: bounded; check current docs.

## Common pitfalls

- **Long-lived Git credentials.** Per-IAM-user HTTPS credentials persist; rotate or use HTTPS-GRC.
- **Manual access management.** Use IAM Identity Center + HTTPS-GRC; manual IAM-user creation doesn't scale.
- **No branch protection.** Default IAM policies often allow push to `main`. Enforce via IAM resource policies on the repo + approval rules.
- **CodeCommit as the team's only copy.** Cross-Region replication isn't built in. For DR, mirror to a second Region or to GitHub / GitLab.
- **Skipping pull-request workflows.** AWS Console PRs work; train the team on them rather than letting people push directly to `main`.
- **Large binaries before Git LFS.** Until LFS support lands (planned Q1 2026), large binaries bloat the repo. Use S3 for binary assets.
- **Forgetting that public-facing collaboration is awkward.** CodeCommit isn't designed for external contributors; for open-source / community, GitHub is the right tool.

## Pairs well with

- [CodeBuild](codebuild.md), [CodePipeline](codepipeline.md), [CodeDeploy](codedeploy.md) — native source for AWS CI/CD.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — federated access with HTTPS-GRC.
- [KMS](../security-identity/kms.md) — encryption at rest with customer-managed keys.
- [EventBridge](../integration-messaging/eventbridge.md) — react to repo events.
- [Q Developer](../ml-ai/q.md) — code review via Q Developer agent on the repo.

## Pairs well with these repo pages

- [CodePipeline](codepipeline.md), [CodeBuild](codebuild.md), [CodeDeploy](codedeploy.md), [CodeArtifact](codeartifact.md).

## Further reading

- [AWS CodeCommit documentation](https://docs.aws.amazon.com/codecommit/).
- [The Future of AWS CodeCommit (return to GA)](https://aws.amazon.com/blogs/devops/aws-codecommit-returns-to-general-availability/).
- [HTTPS-GRC (git-remote-codecommit)](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-git-remote-codecommit.html).
- [Pull requests and approval rules](https://docs.aws.amazon.com/codecommit/latest/userguide/pull-requests.html).
- [CodeCommit pricing](https://aws.amazon.com/codecommit/pricing/).
