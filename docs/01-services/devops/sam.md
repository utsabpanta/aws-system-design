# SAM (Serverless Application Model)

> **One-line summary.** Open-source CloudFormation extension and CLI specifically for serverless apps (Lambda, API Gateway, DynamoDB, EventBridge, Step Functions). Concise YAML + local-test tooling.

## TL;DR

- **SAM templates** are CloudFormation with a `Transform: AWS::Serverless-2016-10-31` directive — succinct resource shapes for Lambda functions, HTTP/REST APIs, DynamoDB tables, EventBridge rules, Step Functions.
- **SAM CLI** wraps the build / package / deploy / local-test loop with one command. `sam local invoke` runs Lambda functions in a local Docker container; `sam local start-api` runs API Gateway locally.
- For **serverless-only** apps, SAM is the most concise IaC option. For broader / mixed workloads, **CDK** is usually a better fit.
- Compiles to CloudFormation; deploys via CloudFormation; coexists with CDK and direct CloudFormation in the same account.
- **SAM Accelerate** (sync mode) deploys Lambda function code changes in seconds without a full CloudFormation update.

## When to use it

- Serverless apps where the resource set is Lambda + API Gateway + DynamoDB + EventBridge + a few other primitives.
- Teams who want concise YAML over CDK's TypeScript / Python.
- Workloads where local testing of Lambda + API Gateway matters (SAM CLI's `sam local` is the best AWS-native local-test loop).
- Quick prototypes and hackathon-shaped apps.

## When NOT to use it

- Non-serverless workloads (large ECS / EKS / EC2 fleets) — SAM is serverless-shaped; CDK or CloudFormation directly is better.
- Multi-stack / multi-environment deployments with rich orchestration — CDK Pipelines fits better.
- Teams already standardized on CDK or Terraform — switching adds friction.

## Key concepts

### Template

A YAML / JSON CloudFormation template with `Transform: AWS::Serverless-2016-10-31`. Uses simplified resource types:

- **AWS::Serverless::Function** — Lambda with built-in defaults for IAM, environment, layers, events.
- **AWS::Serverless::Api** / **AWS::Serverless::HttpApi** — API Gateway (REST / HTTP).
- **AWS::Serverless::SimpleTable** — DynamoDB.
- **AWS::Serverless::StateMachine** — Step Functions.
- **AWS::Serverless::Application** — nested apps from SAR.
- **AWS::Serverless::LayerVersion** — Lambda layers.

Each compiles to one or more CloudFormation resources.

### SAM CLI

- **`sam init`** — bootstrap a project from a template.
- **`sam build`** — install dependencies, package Lambda code.
- **`sam local invoke <FunctionName>`** — invoke a Lambda function locally in Docker.
- **`sam local start-api`** — run API Gateway locally; useful for end-to-end iteration.
- **`sam local start-lambda`** — local Lambda endpoint for tests / Step Functions Local.
- **`sam deploy`** — package and deploy via CloudFormation.
- **`sam sync`** — fast deploy: detect function code changes and push them directly without CloudFormation update.
- **`sam logs`** — tail CloudWatch Logs for a deployed function.
- **`sam delete`** — tear down.

### SAM Accelerate (`sam sync`)

Skips full CloudFormation updates for code-only changes. Updates Lambda function code (or other supported resources) directly via service APIs. Seconds vs minutes for the iteration loop.

### Lambda layers and runtimes

SAM has first-class support for Lambda layers, runtimes (Node, Python, Java, Go, .NET, Ruby, custom runtimes via container images), and architectures (x86_64, ARM64).

### Events

`Events:` section on a `Function` declares triggers — API Gateway routes, EventBridge rules, S3 buckets, SQS queues, DynamoDB Streams, Kinesis, Schedule, IoT, Cognito, ALB — all expressed as nested mini-templates that SAM expands into the actual CloudFormation.

### SAM Pipelines

Generated CI/CD templates for SAM apps (`sam pipeline init` creates a CodePipeline / GitHub Actions / GitLab CI / Jenkins / Bitbucket Pipelines starter).

### Serverless Application Repository (SAR)

Marketplace of reusable SAM apps. Discover and deploy partner / community serverless apps via `AWS::Serverless::Application`.

## Pricing model

- **SAM itself is free.**
- **CloudFormation** under SAM is free.
- **AWS resources** (Lambda, API Gateway, DynamoDB, etc.) billed normally.
- **SAR apps** may have per-publish or per-instance fees from the author.

## Quotas & limits

- Inherited from **CloudFormation** (stack count, resources per stack, template size).
- Inherited from underlying services (Lambda concurrency, API Gateway throttling, DynamoDB capacity).
- **SAM CLI Docker layer cache** lives locally; clean periodically.

## Common pitfalls

- **SAM for non-serverless workloads.** Forcing ECS / EC2 / EKS through SAM is awkward. Use CDK / CloudFormation directly.
- **Skipping `sam local` for iteration.** Local testing is the SAM ergonomic win; deploying for every change is much slower.
- **`sam build` cache missed.** Rebuild from scratch every CI run = slow. Use SAM's `--cached` flag or Docker layer caching.
- **`sam sync` in production.** Sync skips CloudFormation tracking; great for dev/personal iteration, dangerous in shared environments where state should be tracked.
- **Layer sprawl.** Each layer adds Lambda cold-start time. Consolidate dependencies into the function package or fewer layers.
- **Environment variables for secrets.** Use Secrets Manager / Parameter Store + the Parameters & Secrets Lambda extension; env vars are visible in console / CFN.
- **SAR apps without security review.** Anyone can publish to SAR; review IAM permissions before deploying a SAR app.
- **No CodePipeline / CI integration.** Manual `sam deploy` from a laptop doesn't audit-trail. Use `sam pipeline init` to bootstrap CI.

## Pairs well with

- [Lambda](../compute/lambda.md), [API Gateway](../networking/api-gateway.md), [DynamoDB](../database/dynamodb.md), [Step Functions](../integration-messaging/step-functions.md), [EventBridge](../integration-messaging/eventbridge.md) — serverless primitives.
- [CloudFormation](cloudformation.md), [CDK](cdk.md) — SAM compiles to CloudFormation; coexists with CDK.
- [CodePipeline](codepipeline.md), GitHub Actions, GitLab CI — CI/CD.
- **Serverless Framework** — adjacent third-party tool with similar shape.

## Pairs well with these repo pages

- [CloudFormation](cloudformation.md), [CDK](cdk.md), [Lambda](../compute/lambda.md), [API Gateway](../networking/api-gateway.md), [Step Functions](../integration-messaging/step-functions.md).

## Further reading

- [AWS SAM documentation](https://docs.aws.amazon.com/serverless-application-model/).
- [SAM CLI reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using.html).
- [`sam local`](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-local.html).
- [SAM Accelerate (`sam sync`)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/accelerate.html).
- [Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/).
