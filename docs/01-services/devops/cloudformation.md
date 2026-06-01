# CloudFormation

> **One-line summary.** AWS's native infrastructure-as-code service. Define resources in YAML / JSON / Cfn-Guard; AWS creates, updates, and deletes them as one transactional unit.

## TL;DR

- The original AWS IaC. Templates describe the desired state of resources; CloudFormation reconciles by creating / updating / deleting.
- **Stacks** are the deployable unit; **StackSets** deploy the same stack across many accounts / Regions; **Change Sets** preview what an update will do before applying.
- **Drift detection** finds out-of-band changes (someone clicked in the console); **Resource Import** brings existing resources under CFN control.
- Most teams today use **CDK** (programming languages → generates CloudFormation) or **Terraform** instead of writing CloudFormation directly, but the underlying CloudFormation engine still does the work.
- **AWS::Serverless** transform powers **SAM** (Serverless Application Model). Other transforms include **AWS::LanguageExtensions** and **AWS::Include**.

## When to use it

- Direct CloudFormation when you want the AWS-native, no-extra-tool option.
- Multi-account / multi-Region deploys via StackSets.
- Workloads using CDK or SAM — both compile to CloudFormation.
- Resources / features that CloudFormation supports but Terraform doesn't (sometimes new AWS services land in CFN first).
- Compliance-driven IaC where AWS-native tooling is preferred.

## When NOT to use it

- Multi-cloud — Terraform / Pulumi is the cross-cloud choice.
- Teams already invested in Terraform — switching for marginal benefit isn't worth it.
- Tiny one-off deployments where a shell script or manual console action is simpler (though those don't reproduce).

## Key concepts

### Templates

YAML or JSON files. Sections:

- **Parameters** — inputs.
- **Mappings** — static lookups.
- **Conditions** — control which resources to create.
- **Resources** — the AWS resources to create / update / delete.
- **Outputs** — values to export to other stacks or display.
- **Metadata, Transform, Rules, AWSTemplateFormatVersion**.

### Stacks

A deployable instance of a template. Stack operations: create, update, delete, rollback. CloudFormation tracks the resources created and ties them to the stack.

### Change Sets

Preview what an update will do (create / update / delete which resources, which require replacement) before executing. The safe deployment primitive.

### StackSets

Deploy the same stack to many AWS accounts and Regions. Used heavily for org-wide guardrails (security baseline, logging, IAM roles) via **AWS Organizations** integration.

### Drift detection

Identify resources that have been changed outside CloudFormation. Schedule drift checks periodically; alert on drift.

### Resource Import

Bring existing resources into a stack without recreating them. Useful for migrating console-clicked resources to IaC.

### Transforms

**AWS::Serverless** (SAM), **AWS::LanguageExtensions** (loops, intrinsic functions for collections), **AWS::Include** (compose templates from S3 fragments).

### Custom resources

Resources implemented as Lambda functions that CloudFormation invokes during stack lifecycle — for things CFN doesn't natively support (third-party SaaS provisioning, special workflows).

### CloudFormation Hooks

Pre-create / pre-update validation that can block stack operations failing policy checks (FedRAMP / CIS / org-specific rules). Hook providers in CloudFormation registry — third-party and your own.

### Cfn-Guard

Open-source policy-as-code DSL for validating templates against your rules at PR time.

### CloudFormation Registry

Discover and use community-published resource types (Datadog, Splunk, MongoDB Atlas, etc.) alongside AWS-native ones.

### Drift handling and AWS::Config

Use **AWS Config** rules to detect drift continuously, not just on demand.

## Pricing model

- **CloudFormation itself is free** for AWS native resources.
- **Third-party / public registry resources** — some have small per-operation fees.
- **Hooks** — per-evaluation fee.
- **Underlying resources** billed normally.
- **Drift detection** — per-resource-checked fee.

## Quotas & limits

- **Stacks per account per Region**: 2,000 default (raisable).
- **Resources per stack**: 500 default (raisable to thousands).
- **Template size**: 1 MB (inline) or 460 KB compressed; larger templates use S3-staged uploads.
- **Parameters / Outputs / Mappings per template**: 200 each.
- **StackSets stack instances per StackSet**: high; check current docs.

## Common pitfalls

- **Manual console changes after the stack is up.** Drift; the next stack update may revert or error. Detect drift; enforce IaC discipline.
- **No Change Sets in production.** A destructive update without preview is a self-inflicted incident. Always preview.
- **One mega-stack with everything.** Slow updates, big blast radius, hard to reason about. Split by lifecycle (data tier, app tier) and by ownership.
- **Hardcoded values instead of parameters.** Template doesn't compose / reuse.
- **No StackSets for org-wide baselines.** Manual per-account deploys don't scale across an Organization.
- **Cyclic dependencies between stacks.** Use SSM Parameter Store / outputs intentionally to decouple.
- **`Retain` policies missing on stateful resources.** A stack-delete that destroys an RDS / DynamoDB / S3 bucket is unrecoverable. Set `DeletionPolicy: Retain` on critical state.
- **Updates that require replacement of stateful resources.** A schema change marked "requires replacement" on RDS = new instance, data loss. Always Change Set + review.
- **Cfn-Guard skipped at PR time.** Bad templates land before review catches them.

## Pairs well with

- [CDK](cdk.md), [SAM](sam.md) — higher-level IaC that compiles to CloudFormation.
- [AWS Config](../security-identity/config.md) — drift detection at scale.
- [CodePipeline](codepipeline.md) — deploy stacks via pipelines.
- **AWS Organizations** — StackSets across accounts.
- [Systems Manager Parameter Store](../security-identity/parameter-store.md) — cross-stack references via SSM parameters.

## Pairs well with these repo pages

- [CDK](cdk.md), [SAM](sam.md), [CodePipeline](codepipeline.md), [Config](../security-identity/config.md).

## Further reading

- [AWS CloudFormation documentation](https://docs.aws.amazon.com/cloudformation/).
- [Change Sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html).
- [StackSets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html).
- [Drift detection](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html).
- [Cfn-Guard](https://github.com/aws-cloudformation/cloudformation-guard).
- [CloudFormation Hooks](https://docs.aws.amazon.com/cloudformation-cli/latest/hooks-userguide/what-is-cloudformation-hooks.html).
