# Cloud9

> **One-line summary.** Browser-based IDE for AWS workloads. **Closed to new customers as of July 25, 2024.** Existing customers continue; AWS recommends migrating to **AWS IDE Toolkits** (VS Code / JetBrains plugins) + **AWS CloudShell**.

## Status

> ⚠️ **AWS Cloud9 is closed to new customers (since July 25, 2024).**
>
> - Existing customers can continue using the service.
> - AWS continues to invest in security, availability, and performance improvements.
> - **No new features.**
>
> **AWS-recommended migration:**
>
> - **AWS IDE Toolkits** — open-source plugins for VS Code, JetBrains (IntelliJ, PyCharm, etc.), Visual Studio. Manage AWS resources, deploy applications, and debug from a local IDE.
> - **AWS CloudShell** — browser-based bash/PowerShell shell with AWS CLI pre-configured, 1 GB persistent home directory, no IDE features.
> - **GitHub Codespaces / GitPod / Coder** — cloud-hosted VS Code workspaces for full IDE-in-browser; pair with the AWS Toolkit.
>
> Many former Cloud9 use cases (collaborative coding, quick AWS-aware shell access, environment-as-code) are better served by these alternatives in 2026.

## TL;DR

- Cloud9 was AWS's browser-hosted IDE — a VS-Code-style editor on an EC2 instance, with terminal, Git integration, debugging, and AWS SDK pre-configured.
- Useful for "give me an AWS-aware browser IDE for training / collaboration / quick changes from any device."
- **Closed to new customers since July 25, 2024.** New users should use AWS IDE Toolkits in a local IDE or GitHub Codespaces.
- Existing customers can keep using it indefinitely (as of 2026), but features are frozen.

## When to use it

- **Existing customers only.** Continue using or migrate.
- **For new use cases: use the alternatives above.** No new Cloud9 environments can be created.

## When NOT to use it

- Any new project. New Cloud9 environment creation is blocked.

## Key concepts (for existing users)

**Environment.** A Cloud9 dev environment — either an **EC2 environment** (Cloud9 provisions an EC2 instance) or **SSH environment** (connect to an existing EC2 / on-prem machine).

**Shared environments.** Multiple users can collaborate in the same environment — pair programming, code review, instructor-led training.

**Pre-configured tools.** AWS CLI, Git, language runtimes (Node, Python, Ruby, Go, Java, .NET, C++), Docker. Updated periodically by AWS.

**AWS-managed credentials.** Cloud9 environments use AWS-managed temporary credentials that match the IAM user / role of the Cloud9 user — no need to configure access keys.

**Auto-hibernate.** EC2 environments hibernate after configurable idle time to save cost.

**Environment SSH.** SSH from Cloud9 to other EC2 / on-prem hosts; preserve session state.

## Migration paths

### To AWS IDE Toolkits + local VS Code / JetBrains

1. Install [AWS Toolkit for VS Code](https://aws.amazon.com/visualstudiocode/) (or [JetBrains](https://aws.amazon.com/intellij/)).
2. Sign in via IAM Identity Center / IAM.
3. Get the same AWS resource management, deployment, and debugging features locally.
4. For the "browser IDE from any device" use case: pair with **GitHub Codespaces** or **GitPod** for cloud-hosted VS Code.

### To AWS CloudShell

1. Open CloudShell from the AWS console (browser-based bash / PowerShell with AWS CLI).
2. 1 GB persistent home directory across sessions.
3. Good for quick CLI / scripts; not a full IDE.

### To a self-hosted IDE on EC2

For teams that genuinely need a browser-accessible IDE on an EC2 instance and Cloud9 was the only one in their toolkit: self-host **code-server** (VS Code in browser) or run **GitHub Codespaces** on a dedicated machine.

## Pricing model (legacy)

- **Cloud9 the service is free.**
- You pay for the underlying EC2 + EBS the environment runs on.
- SSH-only environments (connecting to your own machines) have no Cloud9-related compute charge.

## Common pitfalls (for existing users)

- **Treating Cloud9 as "future-safe."** It isn't. Plan migration; new features won't land.
- **Sharing environments without authorization controls.** Shared environments grant collaborators access to anything the environment's IAM role allows.
- **Big EC2 instances kept warm.** Use auto-hibernate to limit cost.
- **EBS / snapshot sprawl.** Snapshots accumulate; lifecycle them.
- **Cloud9 as the team's only dev environment.** Single-vendor lock-in to a closed-to-new-customers product. Diversify to IDE Toolkits + Codespaces / GitPod / Coder for resilience.

## Pairs well with these repo pages

- [CodeCommit](codecommit.md) (just reopened to new customers!) — source.
- [CodeBuild](codebuild.md), [CodePipeline](codepipeline.md) — CI/CD downstream of Cloud9-edited code.
- **AWS CloudShell**, **AWS IDE Toolkits** (in VS Code / JetBrains) — the migration targets.

## Further reading

- [AWS Cloud9 documentation](https://docs.aws.amazon.com/cloud9/).
- [Migrate from Cloud9 to IDE Toolkits or CloudShell](https://aws.amazon.com/blogs/devops/how-to-migrate-from-aws-cloud9-to-aws-ide-toolkits-or-aws-cloudshell/).
- [AWS Toolkit for VS Code](https://aws.amazon.com/visualstudiocode/).
- [AWS Toolkit for JetBrains](https://aws.amazon.com/intellij/).
- [AWS CloudShell](https://docs.aws.amazon.com/cloudshell/).
