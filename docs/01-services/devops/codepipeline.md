# CodePipeline

> **One-line summary.** Managed CI/CD orchestration. Defines a pipeline (source → build → test → deploy → approve) as stages and actions; AWS executes it on every change.

## TL;DR

- The orchestration glue between source (CodeCommit / GitHub / GitLab / Bitbucket / S3), build (CodeBuild), test, and deploy (CodeDeploy / CloudFormation / CDK / SAM / ECS / Lambda / Elastic Beanstalk).
- **V2 pipelines** (current default) add **triggers** (Git tags, branches), **parameters**, **variables**, **execution-mode** options (QUEUED / SUPERSEDED / PARALLEL), and **detect-source-changes** for monorepos.
- Visual + JSON / YAML / CDK-definable; integrates with **EventBridge** for triggers and notifications.
- Most teams use CodePipeline either as "the AWS-native CI/CD" or as a downstream consumer of GitHub Actions / GitLab CI (build there, deploy via CodePipeline).
- For complex DAG workflows beyond linear stage→stage, **Step Functions** is sometimes the better fit.

## When to use it

- AWS-native CI/CD for application deploys (ECS, Lambda, EC2, EKS, S3 static sites).
- Multi-environment promotion pipelines (dev → staging → prod with manual approvals).
- CloudFormation / CDK stack deployments with change-set review.
- Compliance-driven workflows requiring manual approvals and audited deployment history.

## When NOT to use it

- Teams committed to GitHub Actions / GitLab CI for the whole pipeline — running both adds complexity.
- Pipelines with complex branching / parallel logic that suit Step Functions better.
- Workloads where Argo CD / Flux (GitOps) is the deploy paradigm.

## Key concepts

### Pipelines (V2)

- **V2 pipelines** are the current default; V1 still exists for backwards compatibility.
- V2 adds: **triggers** (Git tags, branches with filters), **parameters** (named inputs per execution), **variables** (across stages), **execution modes** (QUEUED, SUPERSEDED, PARALLEL).

### Structure

- **Pipeline** — top-level resource.
- **Stage** — ordered phase (`Source`, `Build`, `Deploy_Staging`, `Approval`, `Deploy_Prod`).
- **Action** — a specific operation in a stage (run CodeBuild, deploy to ECS, manual approval, invoke Lambda, run Step Function, etc.).
- **Action providers** — broad catalog: AWS-native (CodeBuild, CodeDeploy, CloudFormation, ECS, Lambda, S3, Elastic Beanstalk, AppConfig) and third-party (GitHub, BitBucket, GitLab, Jenkins, Snyk, ThoughtWorks GoCD, etc.).

### Source actions

- **CodeCommit / GitHub / GitHub Enterprise / GitLab / Bitbucket / S3 / ECR / Step Functions output**.
- **CodeStar Connections** — the modern OAuth-based integration to third-party Git providers; doesn't require static tokens.

### Build / test actions

- Most commonly **CodeBuild**.
- **Jenkins**, **TeamCity**, **CircleCI** also supported.

### Deploy actions

- **CodeDeploy**, **CloudFormation** (stack creation / update / change set), **ECS deploy**, **Lambda deploy** (alias updates), **Elastic Beanstalk**, **S3** (static-site sync), **AppConfig**, **Step Functions**.

### Approval actions

Manual approval step that pauses the pipeline pending a human button-click (with optional review URL and comment).

### Triggers

- **CodeCommit / S3 push** events.
- **GitHub / GitLab / Bitbucket webhooks** via CodeStar Connections.
- **EventBridge events** for arbitrary triggering.
- **Schedule** (cron-style).

### Variables and parameters

- **Pipeline variables** — set at execution start; substituted across actions.
- **Action variables** — output from one action consumed by a later one.
- **Pipeline parameters** — declared inputs per pipeline execution (V2).

### Execution modes (V2)

- **QUEUED** — only one execution at a time; subsequent ones queue.
- **SUPERSEDED** (default) — newer execution cancels older.
- **PARALLEL** — multiple executions run concurrently.

### Notifications

**EventBridge events** on stage transitions; route to SNS / Slack / Teams.

### CDK / IaC

Define pipelines in **AWS CDK Pipelines** for self-mutating CI/CD; great for "the pipeline that deploys the pipeline" patterns.

## Pricing model

- **Per active pipeline per month** (a pipeline is "active" if it has at least one execution in the past 30 days).
- **V2 pipelines** have a different pricing tier than V1 — billed per action execution minute.
- **First active pipeline per month free.**
- **Underlying actions** (CodeBuild minutes, S3 storage, etc.) billed separately.

For most teams the cost is small; the bulk is in CodeBuild / CloudFormation downstream.

## Quotas & limits

- **Pipelines per account per Region**: 1,000.
- **Stages per pipeline**: 50.
- **Actions per stage**: 50.
- **Parallel actions per stage**: bounded by region; typically 50.
- **Pipeline execution duration**: up to 30 days.

## Common pitfalls

- **V1 pipelines for new projects.** Use V2 — triggers, parameters, variables, execution modes.
- **No manual approval before prod.** A bad merge goes straight to production. Approval gates are friction worth keeping for high-impact deploys.
- **One mega-pipeline for many services.** Hard to reason about, slow blast radius. One pipeline per logical service.
- **Static tokens for GitHub.** Use CodeStar Connections (OAuth) — no token rotation surface.
- **No notifications.** Pipeline failures go unnoticed. Wire EventBridge → Slack / SNS.
- **CloudFormation rollback assumed.** CFN rolls back on failure for create; deletes can leave orphaned resources. Test rollback scenarios.
- **PARALLEL execution mode without idempotency.** Two concurrent deploys to the same target can race. Most teams want SUPERSEDED or QUEUED unless they specifically want parallelism.
- **Pipeline that deploys to multiple Regions sequentially.** Slow. Use Step Functions or parallel actions for multi-Region fan-out.
- **No "pipeline that deploys the pipeline" pattern.** Manual pipeline edits drift; CDK Pipelines or CloudFormation defining the pipeline keeps it versioned.

## Pairs well with

- [CodeBuild](codebuild.md), [CodeDeploy](codedeploy.md), [CodeCommit](codecommit.md) — the Code* tools.
- [CloudFormation](cloudformation.md), [CDK](cdk.md), [SAM](sam.md) — IaC deploys.
- **GitHub / GitLab / Bitbucket** via CodeStar Connections.
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [S3](../storage/s3.md), [Elastic Beanstalk](../compute/elastic-beanstalk.md) — deploy targets.
- [Step Functions](../integration-messaging/step-functions.md) — for richer-than-linear orchestration.
- [EventBridge](../integration-messaging/eventbridge.md) — notifications.

## Pairs well with these repo pages

- [CodeBuild](codebuild.md), [CodeDeploy](codedeploy.md), [CDK](cdk.md), [CloudFormation](cloudformation.md), [SAM](sam.md).

## Further reading

- [AWS CodePipeline documentation](https://docs.aws.amazon.com/codepipeline/).
- [V2 pipelines](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipeline-types-planning.html).
- [Action providers](https://docs.aws.amazon.com/codepipeline/latest/userguide/integrations-action-type.html).
- [CDK Pipelines](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html).
- [Notifications and triggers](https://docs.aws.amazon.com/codepipeline/latest/userguide/triggers.html).
