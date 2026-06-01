# IoT TwinMaker

> **One-line summary.** Service for building **digital twins** of real-world systems — 3D scenes + workflow + time-series + alarm data layered together into an interactive view of physical equipment / facilities.

## TL;DR

- The right service for "we want a 3D / interactive operational view of our factory / building / wind farm grounded in real-time telemetry."
- **Entities** model real-world things (a pump, a HVAC unit, a building); **components** attach data sources (SiteWise properties, S3 documents, Kinesis streams, custom).
- **Scenes** are 3D environments — upload glTF / GLB / FBX, place entity tags onto the model, navigate in a browser.
- **TwinMaker integrates with Grafana** (Managed Grafana plugin) for the operational dashboard view + 3D scene.
- Pairs naturally with **SiteWise** for industrial telemetry and **AppSync / GraphQL** for the data API.
- A niche product — most teams use SiteWise + a 2D dashboard. TwinMaker is for situations where 3D / spatial context genuinely matters (large facilities, complex equipment, immersive operator UX).

## When to use it

- Industrial facilities where 3D spatial context aids operations (plant tour, drill-down by pointing at equipment).
- Building management — large campuses or multi-floor facilities.
- Wind farms / solar fields where physical layout matters for operational decisions.
- AR / VR operator training built on real-time data.
- Customer-facing 3D dashboards for connected products.

## When NOT to use it

- 2D dashboards suffice (most cases) — SiteWise Monitor or QuickSight is cheaper and faster to build.
- Tiny equipment fleets — the 3D modeling effort isn't justified.
- Workloads where you don't have 3D models or aren't willing to invest in creating them.

## Key concepts

### Workspaces

Top-level resource. Contains entities, components, scenes, dashboards.

### Entities and components

- **Entity** — a logical real-world thing (pump, HVAC unit, building zone). Hierarchical (an entity can have child entities).
- **Component** — attaches data behavior to an entity. Types:
  - **SiteWise component** — bind to SiteWise asset properties.
  - **Kinesis Video Streams component** — live video feeds attached to an entity.
  - **S3 component** — documents / manuals / spec sheets attached to an entity.
  - **Custom component** — your Lambda function as a data connector.

### Scenes

- 3D scene files (glTF / GLB / FBX) uploaded to S3.
- **Tags** placed on the scene mark where entities are physically (e.g., a tag on the 3D model of the pump in the factory).
- Navigable in browser-based scene viewer.
- Tag visualizations can show real-time data (gauge overlay on the 3D model showing pump pressure).

### Data API

TwinMaker exposes a GraphQL-ish data API for downstream apps to query entities + their data.

### Managed Grafana plugin

- Official TwinMaker plugin for **Amazon Managed Grafana**.
- Displays 3D scenes alongside time-series panels.
- Operators get a "scene + charts" unified view.

### Custom-component connectors

- Bring data from any source (your own time-series DB, ERP, MES) by writing a Lambda-backed component.
- TwinMaker treats it like any other property source.

## Pricing model

- **Per million API calls**.
- **Per workspace per month** (small flat fee).
- **Per data point ingested / queried** (similar shape to SiteWise).
- **Storage** for scenes / models.
- **Managed Grafana** separately.

## Quotas & limits

- **Workspaces per account per Region**: bounded.
- **Entities per workspace**: high (tens of thousands).
- **Components per entity**: bounded; check current docs.
- **Scene file size**: bounded by S3 / glTF practical limits.

## Common pitfalls

- **TwinMaker without a clear 3D use case.** A 2D dashboard would have worked. Use TwinMaker when spatial context genuinely matters.
- **No data connectors planned.** Empty scenes look pretty but tell you nothing. Wire SiteWise / Kinesis / custom components from day one.
- **One huge scene for everything.** Slow load times, hard to navigate. Split per area / per zone.
- **glTF / GLB files too large.** Optimize 3D models for web performance (decimation, compression, texture optimization).
- **Skipping Grafana integration.** The Managed Grafana plugin is the typical operational UI; building your own viewer is much more work.
- **Custom Lambda components without caching.** Per-data-point Lambda calls add up; cache where possible.
- **Treating TwinMaker as the system of record.** It's a view layer; SiteWise / Timestream / DynamoDB hold the actual data.

## Pairs well with

- [IoT SiteWise](iot-sitewise.md) — primary telemetry source.
- **Amazon Managed Grafana** — operational dashboards with TwinMaker scenes.
- [Kinesis Video Streams](../analytics/kinesis.md) — live camera feeds.
- [S3](../storage/s3.md) — scene model storage.
- [Lambda](../compute/lambda.md) — custom component connectors.
- [Bedrock](../ml-ai/bedrock.md) — generative descriptions / chatbots over the digital twin (emerging pattern).

## Pairs well with these repo pages

- [IoT SiteWise](iot-sitewise.md), [IoT Core](iot-core.md), [IoT Greengrass](iot-greengrass.md).

## Further reading

- [AWS IoT TwinMaker documentation](https://docs.aws.amazon.com/iot-twinmaker/).
- [Scenes and 3D models](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/twinmaker-gs-scene.html).
- [TwinMaker for Managed Grafana](https://docs.aws.amazon.com/grafana/latest/userguide/AWS-IoT-TwinMaker-data-source.html).
- [Components and connectors](https://docs.aws.amazon.com/iot-twinmaker/latest/guide/component-types.html).
