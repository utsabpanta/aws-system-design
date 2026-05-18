# IoT SiteWise

> **One-line summary.** Managed industrial IoT data platform. Collects, stores, organizes, and analyzes time-series data from industrial equipment (PLCs, SCADA, OPC UA) using a hierarchical asset model.

## TL;DR
- For **industrial / OT (operational technology) data** — manufacturing, energy, mining, oil & gas, utilities. The substrate for "we have a factory of sensors and equipment and want a unified data layer."
- **Asset models + assets** describe the equipment hierarchy (`Factory > Production Line > Press`); **measurements**, **transforms**, **metrics** are the data points on each asset.
- **SiteWise Edge** (deployed via IoT Greengrass) runs locally at the factory — collects from OPC UA / Modbus servers, pre-processes, ships to the cloud.
- **SiteWise Monitor** is a no-code dashboard tool for plant operators.
- Pairs naturally with **IoT TwinMaker** (3D digital twins) and **QuickSight** (BI).

## When to use it
- Industrial / manufacturing data ingestion and analysis.
- Replacing OT historians (OSIsoft PI, GE Proficy, Wonderware) with a cloud-managed alternative — or augmenting them.
- Sites with OPC UA / Modbus / EtherNet/IP equipment.
- Multi-site fleets of equipment needing centralized visibility.
- Predictive maintenance pipelines (SiteWise data → SageMaker / Bedrock).

## When NOT to use it
- General-purpose time-series — use **Timestream for InfluxDB**.
- Non-industrial IoT — IoT Core + DynamoDB / Timestream is often a better fit.
- Workloads where you need a full DCS / SCADA control system — SiteWise observes; it doesn't control.

## Key concepts

### Asset model and assets
- **Asset model** — schema for a type of equipment (a `Press` model with attributes like model number, location, properties like `temperature`, `pressure`, `state`).
- **Asset** — an instance of a model (Press #14, Press #15).
- **Hierarchy** — assets can have child assets (`Factory > Production Line > Press > Sub-component`).

### Properties
- **Attribute** — static metadata.
- **Measurement** — time-series data from a sensor.
- **Transform** — derived value computed from measurements (e.g., `pressure * 1.5`).
- **Metric** — aggregated value over a window (`sum / avg / min / max / count` over the last hour).

### SiteWise Edge
- Deployed via **IoT Greengrass** at the site.
- **OPC UA collector** reads from on-prem OPC UA servers.
- **Modbus / EtherNet/IP** collectors for other industrial protocols.
- Buffers data locally for intermittent connectivity.
- Optional local processing (transforms, metrics) at the edge.
- Optional **SiteWise Monitor** dashboards at the site for plant operators (works offline).

### SiteWise Monitor
- No-code dashboard tool aimed at plant operators (not data scientists).
- Web-based; per-project access control.

### Storage tiers
- **Hot tier** — recent data, queryable with low latency.
- **Cold tier** — older data, cheaper, slightly higher query latency.

### Data export
Export to **S3** for analytics (Athena, Glue, SageMaker, QuickSight). Optional **Iceberg format** for modern lakehouse setups.

### Integration with TwinMaker
SiteWise feeds **IoT TwinMaker** with the data layer; TwinMaker provides the 3D / scene model.

### Alarms
Define **alarms** on properties; route notifications through SNS / EventBridge.

## Pricing model

- **Per million messages ingested**.
- **Per million property data points stored**.
- **Per million property queries**.
- **SiteWise Monitor** — per portal-hour + per active user.
- **Storage** — per GB-month hot / cold.
- **SiteWise Edge** — per edge connector hour + Greengrass core costs.

Industrial scale (factories with thousands of tags) generates real volume; budget accordingly.

## Quotas & limits

- **Asset models per account per Region**: 4,000.
- **Assets per account per Region**: 100,000 default (raisable).
- **Properties per asset**: 200.
- **Hierarchy depth**: 10 levels.
- **Edge connectors / OPC UA sources per gateway**: bounded; check current docs.

## Common pitfalls

- **No site / asset hierarchy plan up front.** Asset models are foundational; restructuring later is painful. Design the hierarchy early.
- **Direct cloud ingestion from on-prem without SiteWise Edge.** Connectivity gaps lose data. Edge handles buffering and resilience.
- **OPC UA exposed to the cloud directly.** Industrial protocols belong on the factory floor; SiteWise Edge brokers the cloud connection.
- **Skipping hot/cold tiering plan.** Long retention without lifecycle = expensive hot tier forever.
- **One project for everyone in SiteWise Monitor.** Per-team / per-line projects scope dashboards and access; flat-everyone projects are a security risk.
- **Treating SiteWise as control / DCS.** It's observe and analyze, not control. Industrial control systems remain on-prem.
- **No export to S3 / Iceberg.** SiteWise's native query is OK for dashboards but limited for advanced analytics. Export to S3 + Athena for the heavy lifting.

## Pairs well with
- [IoT Greengrass](iot-greengrass.md) — runs SiteWise Edge.
- [IoT TwinMaker](iot-twinmaker.md) — 3D digital twins on top of SiteWise data.
- [QuickSight](../analytics/quicksight.md) — BI dashboards.
- [SageMaker](../ml-ai/sagemaker.md), [Bedrock](../ml-ai/bedrock.md) — predictive maintenance, anomaly detection.
- [S3](../storage/s3.md), [Athena](../analytics/athena.md), [Glue](../analytics/glue.md) — analytics on exported data.
- [Timestream for InfluxDB](../database/timestream.md) — alternative time-series store when SiteWise's industrial-asset model doesn't fit.

## Pairs well with these repo pages
- [IoT Core](iot-core.md), [IoT Greengrass](iot-greengrass.md), [IoT TwinMaker](iot-twinmaker.md), [QuickSight](../analytics/quicksight.md).
- `docs/04-reference-architectures/iot-ingestion.md` (forthcoming).

## Further reading
- [AWS IoT SiteWise documentation](https://docs.aws.amazon.com/iot-sitewise/).
- [SiteWise Edge](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/sw-gateways.html).
- [Asset models](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/industrial-asset-models.html).
- [SiteWise Monitor](https://docs.aws.amazon.com/iot-sitewise/latest/appguide/monitor-getting-started.html).
- [Cold tier storage](https://docs.aws.amazon.com/iot-sitewise/latest/userguide/cold-tier.html).
