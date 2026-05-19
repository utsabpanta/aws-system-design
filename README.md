# aws-system-design

An open-source, version-controlled reference for **learning AWS services and system design**. Every page is markdown, every diagram is generated from source code, and the whole thing renders directly on GitHub — no build step, no hosted site, no signup.

**Who it's for**
- Engineers and students who want to learn AWS services in depth — what each service does, when to reach for it, and the trade-offs that come with the choice.
- Anyone studying for system design interviews who wants concrete AWS-mapped answers backed by reasoning, not memorization.
- Self-taught learners building intuition for how real systems are designed: the patterns that show up everywhere, the failure modes that matter, and the AWS primitives that implement them.

**What it is not**
- An AWS certification cram sheet — explanations go deeper than exam dumps and don't optimize for question banks.
- A code-tutorial repo — minimal CDK/Terraform/CLI snippets only, as illustration. The repo is design-first.
- A vendor comparison — this is AWS-focused; "AWS vs GCP" pages are out of scope.

---

## How to navigate

New here? Read the three short pages in [`docs/00-getting-started/`](docs/00-getting-started/) first — in any order, but ideally:

1. **[How to read this repo](docs/00-getting-started/how-to-read-this-repo.md)** — the directory map and how each page is structured.
2. **[AWS mental model](docs/00-getting-started/aws-mental-model.md)** — Regions, AZs, IAM, VPCs, shared responsibility. The load-bearing concepts every other page assumes.
3. **[System design primer](docs/00-getting-started/system-design-primer.md)** — the vocabulary (latency, throughput, CAP, PACELC, caches) you need for the rest of the repo.

Then jump into whichever section answers your question:

| You want to… | Go to |
|---|---|
| Learn a single AWS service in depth | [`docs/01-services/`](docs/01-services/) |
| Understand a reusable building block (caching, sharding, sagas…) | [`docs/02-patterns/`](docs/02-patterns/) |
| Walk through a classic system design problem on AWS | [`docs/03-interview-designs/`](docs/03-interview-designs/) |
| Study a full architecture end-to-end | [`docs/04-reference-architectures/`](docs/04-reference-architectures/) |
| Review a Well-Architected pillar | [`docs/05-well-architected/`](docs/05-well-architected/) |

Every page has the same shape: **TL;DR → when to use / when NOT to use → details → trade-offs**. If you only read the first two sections, you're already 80% of the way there.

---

## Table of contents

> Auto-generated from the `docs/` tree by [`scripts/build_toc.py`](scripts/build_toc.py). Do not edit between the markers below — regenerate with `scripts/build_toc.sh`.

<!-- TOC START -->

### 00 — Getting started

- [AWS mental model](docs/00-getting-started/aws-mental-model.md)
- [How to read this repo](docs/00-getting-started/how-to-read-this-repo.md)
- [System design primer](docs/00-getting-started/system-design-primer.md)

### 01 — Services

#### Analytics

- [Athena](docs/01-services/analytics/athena.md)
- [Clean Rooms](docs/01-services/analytics/clean-rooms.md)
- [Data Exchange](docs/01-services/analytics/data-exchange.md)
- [EMR (Elastic MapReduce)](docs/01-services/analytics/emr.md)
- [FinSpace](docs/01-services/analytics/finspace.md)
- [Glue](docs/01-services/analytics/glue.md)
- [Kinesis (family)](docs/01-services/analytics/kinesis.md)
- [Lake Formation](docs/01-services/analytics/lake-formation.md)
- [MSK (Managed Streaming for Apache Kafka)](docs/01-services/analytics/msk.md)
- [OpenSearch Service](docs/01-services/analytics/opensearch.md)
- [QuickSight](docs/01-services/analytics/quicksight.md)

#### Compute

- [App Runner](docs/01-services/compute/app-runner.md)
- [Batch](docs/01-services/compute/batch.md)
- [EC2 (Elastic Compute Cloud)](docs/01-services/compute/ec2.md)
- [ECS (Elastic Container Service)](docs/01-services/compute/ecs.md)
- [EKS (Elastic Kubernetes Service)](docs/01-services/compute/eks.md)
- [Elastic Beanstalk](docs/01-services/compute/elastic-beanstalk.md)
- [Fargate](docs/01-services/compute/fargate.md)
- [Lambda](docs/01-services/compute/lambda.md)
- [Lightsail](docs/01-services/compute/lightsail.md)

#### Database

- [Aurora Serverless](docs/01-services/database/aurora-serverless.md)
- [Aurora](docs/01-services/database/aurora.md)
- [DocumentDB](docs/01-services/database/documentdb.md)
- [DynamoDB](docs/01-services/database/dynamodb.md)
- [ElastiCache](docs/01-services/database/elasticache.md)
- [Keyspaces (for Apache Cassandra)](docs/01-services/database/keyspaces.md)
- [MemoryDB](docs/01-services/database/memorydb.md)
- [Neptune](docs/01-services/database/neptune.md)
- [QLDB (Quantum Ledger Database)](docs/01-services/database/qldb.md)
- [RDS (Relational Database Service)](docs/01-services/database/rds.md)
- [Redshift](docs/01-services/database/redshift.md)
- [Timestream](docs/01-services/database/timestream.md)

#### DevOps

- [Amplify](docs/01-services/devops/amplify.md)
- [CDK (Cloud Development Kit)](docs/01-services/devops/cdk.md)
- [Cloud9](docs/01-services/devops/cloud9.md)
- [CloudFormation](docs/01-services/devops/cloudformation.md)
- [CodeArtifact](docs/01-services/devops/codeartifact.md)
- [CodeBuild](docs/01-services/devops/codebuild.md)
- [CodeCommit](docs/01-services/devops/codecommit.md)
- [CodeDeploy](docs/01-services/devops/codedeploy.md)
- [CodeGuru](docs/01-services/devops/codeguru.md)
- [CodePipeline](docs/01-services/devops/codepipeline.md)
- [SAM (Serverless Application Model)](docs/01-services/devops/sam.md)
- [X-Ray](docs/01-services/devops/x-ray.md)

#### Edge

- [IoT Core](docs/01-services/edge/iot-core.md)
- [IoT FleetWise](docs/01-services/edge/iot-fleetwise.md)
- [IoT Greengrass](docs/01-services/edge/iot-greengrass.md)
- [IoT SiteWise](docs/01-services/edge/iot-sitewise.md)
- [IoT TwinMaker](docs/01-services/edge/iot-twinmaker.md)
- [Local Zones](docs/01-services/edge/local-zones.md)
- [Outposts](docs/01-services/edge/outposts.md)
- [Snow Family](docs/01-services/edge/snow-family.md)
- [Wavelength](docs/01-services/edge/wavelength.md)

#### Integration & Messaging

- [AppFlow](docs/01-services/integration-messaging/appflow.md)
- [EventBridge](docs/01-services/integration-messaging/eventbridge.md)
- [MQ](docs/01-services/integration-messaging/mq.md)
- [MWAA (Managed Workflows for Apache Airflow)](docs/01-services/integration-messaging/mwaa.md)
- [EventBridge Pipes](docs/01-services/integration-messaging/pipes.md)
- [SNS (Simple Notification Service)](docs/01-services/integration-messaging/sns.md)
- [SQS (Simple Queue Service)](docs/01-services/integration-messaging/sqs.md)
- [Step Functions](docs/01-services/integration-messaging/step-functions.md)
- [SWF (Simple Workflow Service)](docs/01-services/integration-messaging/swf.md)

#### Migration & Transfer

- [Application Discovery Service (ADS)](docs/01-services/migration-transfer/application-discovery-service.md)
- [DataSync](docs/01-services/migration-transfer/datasync.md)
- [DMS (Database Migration Service)](docs/01-services/migration-transfer/dms.md)
- [MGN (Application Migration Service)](docs/01-services/migration-transfer/mgn.md)
- [Migration Hub](docs/01-services/migration-transfer/migration-hub.md)
- [Transfer Family](docs/01-services/migration-transfer/transfer-family.md)

#### ML / AI

- [Bedrock](docs/01-services/ml-ai/bedrock.md)
- [Comprehend](docs/01-services/ml-ai/comprehend.md)
- [Forecast](docs/01-services/ml-ai/forecast.md)
- [Kendra](docs/01-services/ml-ai/kendra.md)
- [Lex](docs/01-services/ml-ai/lex.md)
- [Personalize](docs/01-services/ml-ai/personalize.md)
- [Polly](docs/01-services/ml-ai/polly.md)
- [Amazon Q (family)](docs/01-services/ml-ai/q.md)
- [Rekognition](docs/01-services/ml-ai/rekognition.md)
- [SageMaker](docs/01-services/ml-ai/sagemaker.md)
- [Textract](docs/01-services/ml-ai/textract.md)
- [Transcribe](docs/01-services/ml-ai/transcribe.md)
- [Translate](docs/01-services/ml-ai/translate.md)

#### Networking

- [API Gateway](docs/01-services/networking/api-gateway.md)
- [App Mesh](docs/01-services/networking/app-mesh.md)
- [Cloud Map](docs/01-services/networking/cloud-map.md)
- [CloudFront](docs/01-services/networking/cloudfront.md)
- [Direct Connect](docs/01-services/networking/direct-connect.md)
- [ELB (Elastic Load Balancing)](docs/01-services/networking/elb.md)
- [Global Accelerator](docs/01-services/networking/global-accelerator.md)
- [NAT Gateway](docs/01-services/networking/nat.md)
- [Route 53](docs/01-services/networking/route53.md)
- [Transit Gateway](docs/01-services/networking/transit-gateway.md)
- [VPC Endpoints & PrivateLink](docs/01-services/networking/vpc-endpoints.md)
- [VPC (Virtual Private Cloud)](docs/01-services/networking/vpc.md)
- [VPN (Site-to-Site & Client)](docs/01-services/networking/vpn.md)

#### Observability

- [AppConfig](docs/01-services/observability/appconfig.md)
- [CloudTrail](docs/01-services/observability/cloudtrail.md)
- [CloudWatch](docs/01-services/observability/cloudwatch.md)
- [Control Tower](docs/01-services/observability/control-tower.md)
- [AWS Health](docs/01-services/observability/health.md)
- [Organizations](docs/01-services/observability/organizations.md)
- [Resource Explorer](docs/01-services/observability/resource-explorer.md)
- [Service Catalog](docs/01-services/observability/service-catalog.md)
- [Systems Manager (SSM)](docs/01-services/observability/systems-manager.md)
- [Trusted Advisor](docs/01-services/observability/trusted-advisor.md)

#### Security & Identity

- [ACM (AWS Certificate Manager)](docs/01-services/security-identity/acm.md)
- [Artifact](docs/01-services/security-identity/artifact.md)
- [Audit Manager](docs/01-services/security-identity/audit-manager.md)
- [CloudHSM](docs/01-services/security-identity/cloudhsm.md)
- [Cognito](docs/01-services/security-identity/cognito.md)
- [Config](docs/01-services/security-identity/config.md)
- [Detective](docs/01-services/security-identity/detective.md)
- [GuardDuty](docs/01-services/security-identity/guardduty.md)
- [IAM Identity Center](docs/01-services/security-identity/iam-identity-center.md)
- [IAM (Identity and Access Management)](docs/01-services/security-identity/iam.md)
- [Inspector](docs/01-services/security-identity/inspector.md)
- [KMS (Key Management Service)](docs/01-services/security-identity/kms.md)
- [Macie](docs/01-services/security-identity/macie.md)
- [Network Firewall](docs/01-services/security-identity/network-firewall.md)
- [Parameter Store](docs/01-services/security-identity/parameter-store.md)
- [Secrets Manager](docs/01-services/security-identity/secrets-manager.md)
- [Security Hub (CSPM)](docs/01-services/security-identity/security-hub.md)
- [Shield](docs/01-services/security-identity/shield.md)
- [Verified Access](docs/01-services/security-identity/verified-access.md)
- [Verified Permissions](docs/01-services/security-identity/verified-permissions.md)
- [WAF (Web Application Firewall)](docs/01-services/security-identity/waf.md)

#### Storage

- [AWS Backup](docs/01-services/storage/backup.md)
- [EBS (Elastic Block Store)](docs/01-services/storage/ebs.md)
- [EFS (Elastic File System)](docs/01-services/storage/efs.md)
- [FSx](docs/01-services/storage/fsx.md)
- [S3 Glacier tiers](docs/01-services/storage/glacier.md)
- [S3 (Simple Storage Service)](docs/01-services/storage/s3.md)
- [Storage Gateway](docs/01-services/storage/storage-gateway.md)

### 02 — Patterns

- [Bulkhead](docs/02-patterns/bulkhead.md)
- [Caching strategies](docs/02-patterns/caching-strategies.md)
- [Circuit breaker](docs/02-patterns/circuit-breaker.md)
- [CQRS (Command Query Responsibility Segregation)](docs/02-patterns/cqrs.md)
- [Data partitioning / sharding](docs/02-patterns/data-partitioning-sharding.md)
- [Disaster recovery strategies](docs/02-patterns/disaster-recovery-strategies.md)
- [Event sourcing](docs/02-patterns/event-sourcing.md)
- [Idempotency](docs/02-patterns/idempotency.md)
- [Leader election](docs/02-patterns/leader-election.md)
- [Multi-region active-active](docs/02-patterns/multi-region-active-active.md)
- [Multi-region active-passive](docs/02-patterns/multi-region-active-passive.md)
- [Transactional outbox](docs/02-patterns/outbox.md)
- [Pub/Sub](docs/02-patterns/pub-sub.md)
- [Rate limiting](docs/02-patterns/rate-limiting.md)
- [Read replicas vs caching](docs/02-patterns/read-replicas-vs-caching.md)
- [Saga](docs/02-patterns/saga.md)

### 03 — Interview designs

- [Ad click aggregator](docs/03-interview-designs/ad-click-aggregator.md)
- [Airbnb (booking / availability)](docs/03-interview-designs/airbnb-booking.md)
- [Distributed cache](docs/03-interview-designs/distributed-cache.md)
- [Distributed counter](docs/03-interview-designs/distributed-counter.md)
- [Dropbox / file storage and sync](docs/03-interview-designs/dropbox-file-storage.md)
- [E-commerce (Amazon-style)](docs/03-interview-designs/ecommerce-amazon.md)
- [Google Docs (collaborative editing)](docs/03-interview-designs/google-docs-collab.md)
- [Instagram](docs/03-interview-designs/instagram.md)
- [Notification system](docs/03-interview-designs/notification-system.md)
- [Pastebin](docs/03-interview-designs/pastebin.md)
- [Payment system](docs/03-interview-designs/payment-system.md)
- [Rate limiter](docs/03-interview-designs/rate-limiter.md)
- [Real-time leaderboard](docs/03-interview-designs/real-time-leaderboard.md)
- [Recommendation system](docs/03-interview-designs/recommendation-system.md)
- [Search autocomplete (typeahead)](docs/03-interview-designs/search-autocomplete.md)
- [Slack messaging (workplace chat)](docs/03-interview-designs/slack-messaging.md)
- [Stock exchange (matching engine)](docs/03-interview-designs/stock-exchange.md)
- [Ticketmaster (event ticket booking)](docs/03-interview-designs/ticketmaster.md)
- [TinyURL](docs/03-interview-designs/tinyurl.md)
- [Twitter feed (X timeline)](docs/03-interview-designs/twitter-feed.md)
- [Uber (ride-sharing / dispatch)](docs/03-interview-designs/uber-ride-sharing.md)
- [URL shortener (TinyURL / bit.ly)](docs/03-interview-designs/url-shortener.md)
- [Web crawler](docs/03-interview-designs/web-crawler.md)
- [WhatsApp chat (real-time messaging)](docs/03-interview-designs/whatsapp-chat.md)
- [YouTube / Netflix (video streaming)](docs/03-interview-designs/youtube-netflix-streaming.md)

### 04 — Reference architectures

- [CI/CD pipeline](docs/04-reference-architectures/ci-cd-pipeline.md)
- [Containerized microservices on ECS](docs/04-reference-architectures/containerized-microservices-ecs.md)
- [Data lake on S3](docs/04-reference-architectures/data-lake-on-s3.md)
- [Data warehouse on Redshift](docs/04-reference-architectures/data-warehouse-redshift.md)
- [Event-driven architecture](docs/04-reference-architectures/event-driven-architecture.md)
- [Hub-and-spoke multi-account network](docs/04-reference-architectures/hub-and-spoke-network.md)
- [Kubernetes on EKS](docs/04-reference-architectures/kubernetes-on-eks.md)
- [Multi-Region active-active](docs/04-reference-architectures/multi-region-active-active.md)
- [Serverless REST API](docs/04-reference-architectures/serverless-rest-api.md)
- [Static website: S3 + CloudFront](docs/04-reference-architectures/static-website-s3-cloudfront.md)
- [Streaming data pipeline](docs/04-reference-architectures/streaming-data-pipeline.md)
- [Three-tier web app](docs/04-reference-architectures/three-tier-web-app.md)

### 05 — Well-Architected

- [Cost Optimization](docs/05-well-architected/cost-optimization.md)
- [Operational Excellence](docs/05-well-architected/operational-excellence.md)
- [Performance Efficiency](docs/05-well-architected/performance-efficiency.md)
- [Reliability](docs/05-well-architected/reliability.md)
- [Security](docs/05-well-architected/security.md)
- [Sustainability](docs/05-well-architected/sustainability.md)

<!-- TOC END -->

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
