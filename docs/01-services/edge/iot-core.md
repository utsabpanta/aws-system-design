# IoT Core

> **One-line summary.** Managed MQTT / HTTPS / WebSockets broker for IoT devices. Device registry, certificate-based auth, fleet provisioning, message routing, device shadows (last-known + desired state), and rules engine for cloud integration.

## TL;DR
- The right entry point for connecting IoT devices (sensors, embedded systems, smart-home gadgets) to AWS at scale.
- **MQTT 3.1.1 / MQTT 5** and HTTPS / WebSockets supported. mTLS auth per device with X.509 certificates from AWS-managed CAs (or your own).
- **Device shadows** persist last-reported and desired state per device — bridges intermittently-connected devices and cloud applications.
- **Rules engine** routes incoming messages to AWS services (Lambda, S3, DynamoDB, Kinesis, SNS, SQS, OpenSearch, Timestream, EventBridge, Step Functions, Kinesis Firehose).
- **Fleet Provisioning** automates onboarding millions of devices.
- For local-edge compute paired with IoT Core, use **IoT Greengrass**.

## When to use it
- Connecting fleets of IoT devices (industrial, consumer, automotive, healthcare) to AWS.
- Real-time telemetry ingestion at IoT scale (millions of devices, billions of messages).
- Per-device certificate-based authentication and authorization.
- Cloud-side processing of device messages via rules / Lambda.
- Device-shadow state synchronization (mobile app sets desired temperature; device reads it when online; reports back).

## When NOT to use it
- Generic messaging not from IoT devices — use **SNS / SQS / EventBridge**.
- Device fleets with custom protocols not supported by IoT Core — use **MQ** with MQTT or a custom broker.
- Workloads where the devices speak HTTP REST only — sometimes API Gateway is enough; IoT Core adds value mostly when MQTT, shadows, fleet provisioning, or device certs matter.

## Key concepts

### Things and the Device Registry
- **Thing** — a logical representation of a device. Has attributes, certificates, policies, group memberships, and an optional **Thing Type** schema.
- **Thing Group** — organize things hierarchically; policies and OTA jobs apply by group.

### Authentication
- **X.509 certificates** — primary auth mechanism. Issued by AWS-managed CAs or your own CA.
- **AWS IAM** — for services and human callers (not typical for devices).
- **Custom authorizers** — Lambda-backed for JWT or bespoke schemes.

### Authorization
- **IoT policies** attached to certificates (or Cognito identities); specify which topics the device can publish / subscribe to, which shadows it can read / update.
- Policy variables (`${iot:Connection.Thing.ThingName}`) let one policy serve many devices.

### MQTT topics
Hierarchical topic strings. Devices publish / subscribe. AWS reserves the `$aws/...` prefix for managed shadows, jobs, fleet provisioning.

### Device shadows
- **Classic shadow** — one per thing.
- **Named shadows** — multiple per thing (e.g., separate shadows for different sub-systems).
- **Shadow document** holds `reported`, `desired`, and `delta` (the diff). Apps update desired; devices reconcile and update reported.

### Rules engine
SQL-like rules over incoming messages route to actions:
- **Lambda**, **S3 PutObject**, **DynamoDB PutItem**, **SNS / SQS publish**, **Kinesis Data Streams / Firehose**, **EventBridge event**, **Step Functions execution**, **Timestream**, **OpenSearch**, **Republish to another MQTT topic**, **HTTPS endpoint**, **AWS IoT Analytics** (legacy), **AWS IoT Events** (legacy).

### Jobs
Deploy commands / OTA firmware updates to fleets of devices. Job lifecycle, rollouts, abort criteria.

### Fleet Provisioning
Automate device onboarding at scale. **Provisioning by claim** (factory-installed claim cert → exchange for unique cert on first connect) or **trusted user** flows.

### Device Defender
Continuous security monitoring of device behavior (cert / policy hygiene; anomalous behavior detection).

### Sidecar services
- **AWS IoT Greengrass** — edge runtime for local processing (see [`iot-greengrass.md`](iot-greengrass.md)).
- **AWS IoT SiteWise** — industrial telemetry collection (see [`iot-sitewise.md`](iot-sitewise.md)).
- **AWS IoT TwinMaker** — digital twins (see [`iot-twinmaker.md`](iot-twinmaker.md)).
- **AWS IoT FleetWise** — vehicle telemetry (closing to new customers; see [`iot-fleetwise.md`](iot-fleetwise.md)).

### Legacy / sunsetting components
**AWS IoT Analytics** and **AWS IoT Events** have been on AWS's "less recommended" list for some time. For analytics, route IoT data to S3 / Athena / Redshift; for event detection, use EventBridge + Lambda.

## Pricing model

- **Connectivity** — per million minutes a device is connected.
- **Messaging** — per million messages exchanged.
- **Device Shadow** — per million operations.
- **Registry** — per million operations.
- **Rules** — per million rules triggered + per million actions executed.
- **Jobs**, **Device Defender** — separate per-million pricing.
- **Fleet Provisioning** — per million provisioning events.

Scales linearly with device count and message rate; per-unit prices are small.

## Quotas & limits

- **Messages per device per second**: 100 default (raisable).
- **Things per account per Region**: 500,000 default (raisable significantly).
- **MQTT message size**: 128 KB.
- **Shadow document size**: 8 KB per shadow.
- **Rules per account per Region**: 1,000 default.
- **Connection lifespan**: bounded by keep-alive.

## Common pitfalls

- **Per-device IAM users instead of certificates.** Doesn't scale; rotation is painful. Always certs.
- **One IoT policy with `*` topics.** A compromised device gets every other device's topics. Scope per-device with policy variables.
- **Shadow as durable storage.** It's a sync mechanism, not a database. For history, route messages to DynamoDB / Timestream / S3.
- **Skipping Device Defender.** Anomalous device behavior (a compromised device spamming) silently affects the cluster.
- **No Fleet Provisioning plan for new devices.** Manually creating certs and things for each device doesn't scale past hundreds.
- **Connecting devices to IoT Core directly when Greengrass would help.** For batteries-of-sensors at a site, a Greengrass core aggregating and pre-processing reduces per-device cost and improves resilience.
- **Using IoT Analytics / IoT Events for new pipelines.** They're legacy; route through Kinesis / EventBridge / Lambda instead.
- **MQTT 3.1.1 only when MQTT 5 features fit.** MQTT 5 adds shared subscriptions, message expiry, user properties — worth using for new fleets.

## Pairs well with
- [IoT Greengrass](iot-greengrass.md) — local edge runtime.
- [IoT SiteWise](iot-sitewise.md), [IoT TwinMaker](iot-twinmaker.md), [IoT FleetWise](iot-fleetwise.md) — verticals.
- [Lambda](../compute/lambda.md), [DynamoDB](../database/dynamodb.md), [Timestream](../database/timestream.md), [Kinesis](../analytics/kinesis.md), [S3](../storage/s3.md) — common rule action targets.
- [Cognito](../security-identity/cognito.md) — end-user mobile-app identity paired with IoT Core.
- [Bedrock](../ml-ai/bedrock.md), [SageMaker](../ml-ai/sagemaker.md) — ML on IoT telemetry.
- [EventBridge](../integration-messaging/eventbridge.md) — event-driven downstream processing.

## Pairs well with these repo pages
- [IoT Greengrass](iot-greengrass.md), [IoT SiteWise](iot-sitewise.md), [Timestream](../database/timestream.md).
- `docs/04-reference-architectures/iot-ingestion.md` (forthcoming).

## Further reading
- [AWS IoT Core documentation](https://docs.aws.amazon.com/iot/).
- [Device certificates and policies](https://docs.aws.amazon.com/iot/latest/developerguide/iot-policies.html).
- [Device Shadows](https://docs.aws.amazon.com/iot/latest/developerguide/iot-device-shadows.html).
- [Rules engine](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html).
- [Fleet Provisioning](https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html).
- [Device Defender](https://docs.aws.amazon.com/iot-device-defender/).
