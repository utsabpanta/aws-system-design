# IoT Greengrass

> **One-line summary.** Edge runtime for IoT devices and gateways. Brings AWS Lambda, container components, ML inference, MQTT brokering, and Stream Manager to the device — works offline, syncs to cloud when connected.

## TL;DR

- The right service for IoT scenarios where local processing matters (latency, intermittent connectivity, bandwidth cost, regulatory data locality) — not every sensor needs to round-trip to the cloud for every reading.
- **Greengrass V2** is the current generation (V1 reaches **end of support June 1, 2026**). All new deployments should be V2; existing V1 customers must migrate before EOL.
- **Components** (the deployment unit): AWS-published (Stream Manager, MQTT broker, ML inference runtimes, Secret Manager, CloudWatch Logs / Metrics, Token Exchange) and your own (Lambda functions, Docker containers, Python / Java / C++ apps).
- Runs on Linux (x86 / ARM) — Raspberry Pi to industrial gateways. **2026 features**: non-root install support, lightweight components (Secure Tunneling at 4 MB vs 36 MB), C / C++ / Rust component SDK (sub-MB footprint for resource-constrained devices).
- Pairs natively with **IoT Core** for cloud-side messaging, registry, and OTA jobs.

## When to use it

- Edge processing of sensor data (filter, aggregate, downsample before sending to cloud).
- ML inference at the edge (defect detection, predictive maintenance, image classification).
- Offline-capable IoT — devices keep working through internet outages, sync when reconnected.
- IoT gateways aggregating many local devices over local protocols (Modbus, BACnet, OPC UA) before bridging to the cloud.
- Local control loops where cloud round-trip latency is unacceptable (manufacturing, robotics).

## When NOT to use it

- Devices that only need to send sensor readings to the cloud — IoT Core direct is simpler.
- Workloads where the edge isn't bandwidth- or latency-constrained — keep processing in the cloud.
- Very-resource-constrained microcontrollers (Arduino-class) — Greengrass needs Linux. Use **FreeRTOS** or direct MQTT to IoT Core.

## Key concepts

### Versions

- **Greengrass V2** (current) — component-based deployment model, smaller footprint, fleet-management features.
- **Greengrass V1** — original; **reaches end of support June 1, 2026**. Migrate.

### Greengrass core device

A Linux device running the Greengrass nucleus + deployed components. Manages local Lambda functions, container components, ML, MQTT brokering, secrets, logs.

### Components

The deployment unit. **AWS-public components** include:

- **Nucleus** (the core runtime).
- **MQTT 5 / 3.1.1 broker** for local devices.
- **Stream Manager** for sending high-throughput streams to cloud (Kinesis / S3) with buffering and retry.
- **CloudWatch Logs / Metrics**.
- **Secret Manager** (local secret access).
- **Token Exchange** (for AWS credentials from the core).
- **ML inference runtimes** (PyTorch, TensorFlow, ONNX, DLR).
- **Modbus / OPC UA / BACnet protocol adapters**.
- **Secure Tunneling** for remote troubleshooting.

**Custom components** — your own apps as components (Lambda function, generic Docker / process).

### Deployments

- Deploy to a single core, a thing group, or all cores.
- Per-deployment rollout strategy with metrics-based abort.
- Component versions; deployments are immutable.

### Stream Manager

Reliable, asynchronous data shipping from edge to cloud with local buffering, store-and-forward, batching, and exactly-once-into-Kinesis semantics. The right way to ship telemetry that needs to survive connectivity gaps.

### Local Lambda functions

Run Lambda functions (Python, Node, Java, C++, Go runtimes) on the core. Triggered by local MQTT, IPC, or timer. Useful for local control loops.

### IPC and authorization

Components communicate via the Greengrass IPC (a local SDK). Access controlled by an authorization policy on each component.

### Local secrets

Replicate secrets from AWS Secrets Manager to the core; components access them locally.

### Recent (2026) features

- **V2.17 (April 2026)** — non-root install, lightweight components (Secure Tunneling lite at 4 MB), PKCS#11 / HSM support for cert storage.
- **Component SDK in C / C++ / Rust** (April 2026) — sub-MB component footprints for resource-constrained devices.
- **Nucleus lite** — for even smaller devices.

## Pricing model

- **Per core device per month** (a fixed monthly fee per active core).
- **IoT Core** messaging / shadow / rules costs apply when the core publishes to the cloud.
- **Underlying AWS resources** (Lambda, Kinesis, S3) billed normally.

## Quotas & limits

- **Cores per account per Region**: bounded; raisable.
- **Components per core**: bounded; check current docs.
- **Component size**: bounded (lightweight options under 5 MB; standard up to tens of MB).
- **Local MQTT clients per core**: thousands.
- **Stream Manager streams per core**: bounded; configurable.

## Common pitfalls

- **Still on Greengrass V1.** **June 1, 2026 EOL.** Migrate to V2.
- **One core per device for simple sensors.** Greengrass overhead isn't justified for sensors that just publish — direct IoT Core is simpler.
- **No Stream Manager for high-throughput telemetry.** Sending lots of data via direct MQTT to IoT Core is more expensive and less reliable than Stream Manager → Kinesis.
- **No HSM / secure-element use.** Storing device keys in plaintext on the filesystem of an edge device is a security risk. Use PKCS#11 with an HSM where the hardware supports it.
- **Deploying to all cores at once.** A bad component breaks the whole fleet. Use group-based rolling deployments.
- **Resource-constrained device with the full Nucleus.** Use **Nucleus lite** and lightweight components for sub-100 MB-memory devices.
- **No metrics from the core.** The CloudWatch Logs / Metrics components are not enabled by default. Add them.
- **Trying to run X86 components on ARM (or vice versa).** Components are arch-specific; verify your build.

## Pairs well with

- [IoT Core](iot-core.md) — cloud-side broker.
- **AWS Lambda** — function components running locally on the core.
- [Kinesis](../analytics/kinesis.md) — Stream Manager destination.
- [S3](../storage/s3.md) — file uploads / model artifacts.
- [Secrets Manager](../security-identity/secrets-manager.md) — replicated to the core.
- [SiteWise](iot-sitewise.md), [TwinMaker](iot-twinmaker.md) — industrial pairings.
- [Snowball Edge](snow-family.md) — can host Greengrass for disconnected scenarios.

## Pairs well with these repo pages

- [IoT Core](iot-core.md), [Kinesis](../analytics/kinesis.md), [Lambda](../compute/lambda.md).

## Further reading

- [AWS IoT Greengrass V2 documentation](https://docs.aws.amazon.com/greengrass/v2/developerguide/).
- [V1 to V2 migration](https://docs.aws.amazon.com/greengrass/v2/developerguide/move-from-v1.html).
- [Public components](https://docs.aws.amazon.com/greengrass/v2/developerguide/public-components.html).
- [Stream Manager](https://docs.aws.amazon.com/greengrass/v2/developerguide/stream-manager-component.html).
- [Greengrass v2.17 announcement (Apr 2026)](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-iot-greengrass-v217/).
