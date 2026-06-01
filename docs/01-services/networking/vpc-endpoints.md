# VPC Endpoints & PrivateLink

> **One-line summary.** Private connectivity from your VPC to AWS services (and to third-party SaaS) without traversing the public internet, without NAT, and without a gateway hop.

## TL;DR

- Two endpoint types: **Gateway** (free, for S3 and DynamoDB only) and **Interface** (per-hour + per-GB, for almost everything else, powered by **AWS PrivateLink**).
- **Gateway endpoints save real money** by keeping S3 and DynamoDB traffic off NAT — turn them on in every VPC that has private subnets.
- **Interface endpoints** make sense when (a) you want traffic off the public internet for security/compliance or (b) the volume to a specific service exceeds the cost of running the endpoint.
- **PrivateLink** is the underlying mechanism — exposes a service over an ENI in the consumer's VPC. Used by AWS services, AWS Marketplace SaaS partners, and you can publish your own service this way too.
- The biggest mistake: thinking VPC Endpoints are an optional optimization. For production VPCs, S3 and DynamoDB Gateway endpoints are table stakes.

## When to use it

**Gateway endpoint (S3 / DynamoDB):**

- Always turn it on for any VPC with private subnets that talks to S3 or DynamoDB. Free, no excuse not to.

**Interface endpoint (Interface VPC Endpoint, IVE):**

- Compliance / security needs traffic to stay off the public internet (HIPAA, FedRAMP).
- High-volume traffic to a specific AWS service where the NAT-processed-bytes fee exceeds the endpoint hourly + per-GB cost (ECR image pulls in container fleets, Secrets Manager / Parameter Store at scale, CloudWatch Logs ingestion).
- Cross-account access to a service published as a PrivateLink service.
- Workloads in fully isolated subnets (no NAT, no IGW) that still need AWS API access.

## When NOT to use it

- Tiny VPCs with negligible AWS-service traffic — the Interface endpoint per-hour cost dominates.
- Workloads that mostly talk to one another within a VPC — no AWS service traffic to begin with.
- Services that already have a Gateway endpoint (S3, DynamoDB) — don't add an Interface endpoint, the Gateway is free.

## Key concepts

### Gateway Endpoints

- **Only for S3 and DynamoDB.**
- Implemented as a route table entry: traffic to the service's prefix list is sent over an AWS-internal path, no extra hop.
- **Free.** No hourly charge, no per-GB charge.
- Restricted by **endpoint policy** (resource-style IAM document) — `s3:Get*` on `arn:aws:s3:::approved-bucket/*` only, etc.

### Interface Endpoints (powered by PrivateLink)

- An **ENI** in each chosen subnet, with a DNS name that resolves to that ENI's private IP.
- **Private DNS** (enabled by default for most AWS service endpoints) overrides the public DNS for the service so existing SDK calls resolve to the endpoint without code changes.
- Hundreds of AWS services have Interface endpoints — CloudWatch Logs, Secrets Manager, SSM, ECR, Kinesis, SQS, SNS, STS, KMS, and many more.
- **Cross-account / cross-VPC.** PrivateLink lets a service owner publish their service; consumers create endpoints into the service.

### PrivateLink for third-party SaaS

- Many SaaS providers (Snowflake, Datadog, MongoDB Atlas, Splunk, etc.) publish their service via PrivateLink. Customer creates an Interface endpoint into the provider's service — traffic stays on the AWS network.
- Inverse: you can publish your own service via PrivateLink as a "VPC Endpoint Service," allowing other AWS accounts to consume it via Interface endpoints in their own VPCs.

### Resource Endpoints (newer)

- Newer PrivateLink primitive that exposes specific resources (an RDS endpoint, a domain) rather than a full service. Simpler for cross-VPC database access patterns.

### DNS behavior

- **Private DNS enabled** (default for AWS service endpoints): `s3.us-east-1.amazonaws.com` resolves to the endpoint's private IP from inside the VPC. Existing SDK code uses the endpoint transparently.
- **Disable private DNS** to force callers to explicitly use the endpoint's DNS name; useful when you want both public and endpoint paths available.

### Endpoint policies

Both Gateway and Interface endpoints support endpoint policies — resource-style IAM that limits *what* the endpoint can do, regardless of the caller's IAM. Useful for "only let this VPC talk to *this* set of S3 buckets."

## Pricing model

- **Gateway endpoints** — free.
- **Interface endpoints** — per-AZ-hour per endpoint + per-GB processed. The per-hour adds up across many services and many AZs; consolidate to the AZs you actually use.
- **PrivateLink Service** (publisher) — per-hour per AZ the service is offered + per-GB processed.
- **Data transfer** — traffic through Interface endpoints to the same Region's AWS service is included in the per-GB processed fee; no separate cross-AZ charge for traffic *between* a subnet and an endpoint in the same AZ.

The economics of Interface vs NAT for a given service is roughly:

```
NAT-cost per GB processed > Interface endpoint per-GB + amortized hourly
```

For most services that workloads talk to a lot (ECR, Logs, Secrets Manager, Kinesis), Interface endpoints win as soon as the workload has meaningful traffic.

## Quotas & limits

- **Interface endpoints per VPC**: 50 default (raisable to 255).
- **Gateway endpoints per VPC**: per service, no real quota.
- **Endpoint services published per account**: 50 (raisable).
- **Allowed principals per endpoint service**: 8,000.
- **DNS resolution**: endpoint DNS is resolved by Route 53 Resolver inside the VPC.

## Common pitfalls

- **No Gateway endpoints for S3 / DynamoDB.** Pure waste — every S3 PUT and DynamoDB call traverses NAT. Add the Gateway endpoint and update the route table; the change is online and free.
- **One Interface endpoint in one AZ.** Traffic from other AZs to that endpoint pays cross-AZ data transfer. Either spread the endpoint across the AZs you use or accept the cost trade.
- **Forgetting endpoint policies.** Default endpoint policy is `*` — anyone in the VPC can use it for anything. Tighten policies, especially for shared environments.
- **Endpoint pollution.** Provisioning endpoints for services no one uses adds hourly cost. Audit unused endpoints periodically.
- **Endpoint + IAM mismatch.** Endpoint allows the action, but caller's IAM doesn't (or vice-versa). Both must allow.
- **Cross-Region calls through Interface endpoint.** Interface endpoints are Regional — calls to a service in another Region won't traverse a same-Region endpoint.
- **Private DNS conflicts.** Some setups (split-horizon DNS, on-prem AD-integrated resolvers) need careful Route 53 Resolver configuration to avoid surprising name resolution.

## Pairs well with

- [VPC](vpc.md) and [NAT Gateway](nat.md) — the alternative path for AWS-service traffic.
- **AWS Network Firewall** — inspect traffic to/from endpoints.
- **Resource Access Manager (RAM)** — share endpoints / endpoint services across accounts.
- **AWS PrivateLink Marketplace partners** — discoverable SaaS that publishes via PrivateLink.

## Further reading

- [VPC Endpoints documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html).
- [Gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html).
- [Interface endpoints (PrivateLink)](https://docs.aws.amazon.com/vpc/latest/privatelink/create-interface-endpoint.html).
- [PrivateLink-ready partners (Marketplace)](https://aws.amazon.com/privatelink/partners/).
- [Endpoint policies](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-access.html).
