# aws-system-design

A version-controlled reference for AWS services and system design patterns. Every page is markdown, every diagram is generated from source code, and the whole thing renders directly on GitHub — no build step, no hosted site.

**Who it's for**
- Engineers preparing for system design interviews who want concrete AWS-mapped answers.
- Practitioners looking for reference architectures to copy from on Monday morning.

**What it is not**
- An AWS certification cram sheet.
- A code-tutorial repo — minimal CDK/Terraform/CLI snippets only, as illustration.
- A vendor comparison ("AWS vs GCP").

---

## How to navigate

Start with [`docs/00-getting-started/how-to-read-this-repo.md`](docs/00-getting-started/how-to-read-this-repo.md), then jump into whichever section answers your question:

| You want to… | Go to |
|---|---|
| Understand a single AWS service | [`docs/01-services/`](docs/01-services/) |
| Look up a reusable building block (caching, sharding, sagas…) | [`docs/02-patterns/`](docs/02-patterns/) |
| Whiteboard a classic interview problem on AWS | [`docs/03-interview-designs/`](docs/03-interview-designs/) |
| Find a production-ready blueprint | [`docs/04-reference-architectures/`](docs/04-reference-architectures/) |
| Re-read a Well-Architected pillar | [`docs/05-well-architected/`](docs/05-well-architected/) |

---

## Table of contents

### 00 — Getting started
- [How to read this repo](docs/00-getting-started/how-to-read-this-repo.md)
- [System design primer](docs/00-getting-started/system-design-primer.md)
- [AWS mental model](docs/00-getting-started/aws-mental-model.md)

### 01 — Services
One folder per AWS service category. Each service gets its own page.
- [Compute](docs/01-services/compute/) — EC2, Lambda, ECS, EKS, Fargate, Batch, Lightsail, …
- [Storage](docs/01-services/storage/) — S3, EBS, EFS, FSx, Backup, …
- [Database](docs/01-services/database/) — RDS, Aurora, DynamoDB, ElastiCache, Redshift, …
- [Networking](docs/01-services/networking/) — VPC, Route 53, CloudFront, ELB, API Gateway, …
- [Security & Identity](docs/01-services/security-identity/) — IAM, KMS, Cognito, WAF, GuardDuty, …
- [Integration & Messaging](docs/01-services/integration-messaging/) — SNS, SQS, EventBridge, Step Functions, …
- [Analytics](docs/01-services/analytics/) — Athena, Glue, EMR, Kinesis, MSK, OpenSearch, …
- [ML / AI](docs/01-services/ml-ai/) — SageMaker, Bedrock, Rekognition, Comprehend, …
- [DevOps](docs/01-services/devops/) — CodeBuild, CodeDeploy, CodePipeline, CloudFormation, CDK, …
- [Observability](docs/01-services/observability/) — CloudWatch, CloudTrail, Systems Manager, X-Ray, …
- [Edge](docs/01-services/edge/) — CloudFront, Global Accelerator, Outposts, Wavelength, IoT, …
- [Migration & Transfer](docs/01-services/migration-transfer/) — DMS, MGN, DataSync, Transfer Family, …

### 02 — Patterns
Reusable building blocks that show up in every system.
See [`docs/02-patterns/`](docs/02-patterns/).

### 03 — Interview designs
Classic whiteboard problems with AWS-mapped solutions, 25+ pages.
See [`docs/03-interview-designs/`](docs/03-interview-designs/).

### 04 — Reference architectures
"How would I actually build this on Monday" blueprints.
See [`docs/04-reference-architectures/`](docs/04-reference-architectures/).

### 05 — Well-Architected
A deep-dive per pillar.
See [`docs/05-well-architected/`](docs/05-well-architected/).

---

## Conventions

- **One file per concept.** Every service, every pattern, every design has its own markdown file.
- **Same template everywhere.** See [CONTRIBUTING.md](CONTRIBUTING.md#page-template).
- **Diagrams are code.** Mermaid for flows/sequences/ERDs (renders inline on GitHub). Python [`diagrams`](https://github.com/mingrammer/diagrams) for AWS architecture diagrams (committed as both `.py` source and rendered `.png`).
- **Cite, don't copy.** Paraphrase AWS docs; link out for canonical reference.

---

## Contributing

Pull requests welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the page template, style guide, diagram conventions, and the DCO sign-off requirement.

## License

[MIT](LICENSE).
