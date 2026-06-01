# MQ

> **One-line summary.** Managed **ActiveMQ** and **RabbitMQ** brokers. Lift-and-shift target for workloads that depend on AMQP, MQTT, STOMP, OpenWire, or JMS protocols — without operating broker clusters yourself.

## TL;DR

- The right service when you're migrating an existing app that uses ActiveMQ or RabbitMQ and you don't want to refactor onto SQS / SNS / Kafka.
- Two engines: **ActiveMQ** (AMQP, MQTT, OpenWire, STOMP, JMS, WebSockets) and **RabbitMQ** (AMQP 0-9-1, MQTT, STOMP, RabbitMQ Streams).
- Supports **single-instance** (dev/test) and **cluster** (production HA) deployments. Cross-AZ active/standby for ActiveMQ; multi-node cluster for RabbitMQ.
- For new AWS-native workloads, **SQS / SNS / EventBridge / MSK** are usually cheaper and more deeply integrated. MQ shines for the "we already speak AMQP" case.
- Patching, version upgrades, and broker config managed by AWS; you're still responsible for queue / exchange / topic configuration and message-level concerns.

## When to use it

- Lifting and shifting apps that already use ActiveMQ or RabbitMQ to AWS.
- Workloads that depend on broker features SQS / SNS lack: JMS, AMQP routing, transactional queues, complex exchange topologies, MQTT for IoT.
- IoT scenarios where MQTT-on-AWS via **AWS IoT Core** doesn't fit (e.g., custom broker / client topology).
- Integrations with third-party systems that speak STOMP / OpenWire.

## When NOT to use it

- Greenfield event-driven on AWS — **SQS + SNS + EventBridge** is cheaper, more scalable, and more integrated.
- High-volume Kafka-style streaming — use **MSK** or **MSK Serverless**.
- MQTT for IoT at scale — use **AWS IoT Core**, which has device-management and policy features MQ lacks.

## Key concepts

### ActiveMQ flavors

- **Single-instance** — one broker; outage on AZ failure. Dev/test only.
- **Active/standby (multi-AZ)** — synchronous replication to a standby in another AZ; automatic failover. Production-grade ActiveMQ pattern.

### RabbitMQ

- **Cluster mode** — multi-node RabbitMQ cluster, with quorum queues for HA. AWS-managed cluster sizing and failover.

### Protocols

**ActiveMQ:** AMQP 1.0, MQTT, OpenWire (Java-native), STOMP, WebSockets.

**RabbitMQ:** AMQP 0-9-1 (the primary RabbitMQ protocol), MQTT, STOMP, RabbitMQ Streams.

### Networking

Brokers live in your VPC; reach them via standard NLB / endpoint discovery. Optional public accessibility (rarely the right choice for production).

### Encryption and auth

TLS in transit (mandatory). LDAP or LDAP-via-AD for auth (ActiveMQ); native users + virtual hosts (RabbitMQ). KMS encryption at rest.

### CloudWatch integration

Broker metrics (queue depth, connection count, consumer lag) published to CloudWatch. Logs to CloudWatch Logs.

### Maintenance windows

AWS applies minor version patches during a configured weekly window. Major version upgrades require explicit action (blue/green clone, replay, cut over).

## Pricing model

- **Per broker-hour** by instance class (`mq.t3.micro`, `mq.m5.large`, …).
- **Storage** for messages — per GB-month.
- **Data transfer** at standard AWS rates.
- **Cluster sizes** multiply broker-hour costs.

MQ broker hours are real money — at production HA scale, comparable to running RDS-class infrastructure. New workloads should evaluate whether SQS / SNS / EventBridge meets the need before committing.

## Quotas & limits

- **Brokers per Region per account**: 50 (raisable).
- **Connections per broker**: thousands; instance-class dependent.
- **Throughput**: instance-class dependent (modest compared to MSK / Kinesis).
- **Max message size**: 100 MB+ (ActiveMQ); RabbitMQ recommended < 100 MB per message.
- **Maintenance window**: one per week, two-hour minimum.

## Common pitfalls

- **Single-instance for production.** AZ failure = outage. Always Multi-AZ (ActiveMQ) or cluster (RabbitMQ).
- **MQ for greenfield AWS-native systems.** Operationally heavier and more expensive than SQS / SNS at most scales. Use it when the protocol or broker semantics genuinely require it.
- **No CloudWatch alarms on queue depth.** Consumer lag → backlog → memory pressure → broker degradation. Alarm on queue depth and connection count.
- **Skipping version upgrades.** Older broker versions accumulate CVEs and lose AWS support. Schedule version upgrades; test in non-production first.
- **MQTT for IoT instead of AWS IoT Core.** IoT Core has device registry, fleet management, OTA updates, and per-device policies that MQ lacks. Use MQ only when something specific keeps you off IoT Core.
- **Encryption-at-rest assumed but disabled.** Verify the broker config — AWS provides KMS encryption, but you must enable it at broker creation.
- **No DR plan.** Multi-Region MQ requires app-level replication (republish messages to a broker in the secondary Region) — there's no managed cross-Region replication for MQ.

## Pairs well with

- **AWS Backup** — broker backups.
- **Secrets Manager** — broker credentials.
- **CloudWatch Logs / Metrics** — observability.
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md), [EKS](../compute/eks.md) — broker consumers (often via AMQP/MQTT client libraries).
- [EventBridge Pipes](pipes.md) — MQ is a supported source; bridge MQ-bound apps to AWS-native targets.

## Pairs well with these repo pages

- [SQS](sqs.md), [SNS](sns.md), [EventBridge](eventbridge.md) — the AWS-native alternatives for new workloads.
- **AWS IoT Core** (forthcoming) — for MQTT at IoT scale.

## Further reading

- [Amazon MQ documentation](https://docs.aws.amazon.com/amazon-mq/).
- [Amazon MQ for ActiveMQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/activemq.html).
- [Amazon MQ for RabbitMQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/rabbitmq.html).
- [Choosing between Amazon MQ, SQS, and SNS](https://docs.aws.amazon.com/decision-guides/latest/messaging-services-on-aws-how-to-choose/messaging-services-on-aws-how-to-choose.html).
