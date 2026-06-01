# IoT FleetWise

> **One-line summary.** Managed service for collecting, organizing, and transferring **vehicle telemetry data** to the cloud — supports the major automotive data protocols, including vision-system (camera / radar / lidar) data. **Closing to new customers on April 30, 2026.**

## Status

> ⚠️ **AWS IoT FleetWise is closing to new customers on April 30, 2026.**
>
> - Existing customers can continue using the service after the closure date.
> - **No new feature development** is planned by AWS.
> - For new automotive telemetry projects, evaluate alternatives: a custom pipeline built on **IoT Core + Greengrass + Kinesis + Timestream/InfluxDB**, third-party vehicle telemetry platforms (Tesla-style data-platform vendors, OpenADx, Cosmos / Foxglove), or wait to see what AWS positions next in the connected-vehicle space.
>
> This page documents FleetWise for existing customers and for understanding what it offered.

## TL;DR

- Built for the automotive use case — connected vehicles, fleet telemetry, autonomous-driving data collection.
- Supports CAN (Controller Area Network), DBC files, OBD-II, and vision-system data (cameras, radar, lidar).
- **Campaigns** define what data to collect, from which vehicles, under what conditions (event-triggered, time-windowed, on demand).
- Standardizes data into a **Signal Catalog** (a shared schema across vehicle models) so analytics doesn't deal with per-OEM idiosyncrasies.
- Output to S3 / Timestream — analytics happens downstream.
- Closing to new customers; existing customers continue.

## When to use it

- **Existing FleetWise customers** continuing operations.
- Migration assessment for moving off FleetWise to alternative pipelines.

## When NOT to use it

- New automotive telemetry projects — won't be accepted as a new customer. Plan an alternative.
- Non-vehicle IoT workloads — IoT Core + Greengrass + Kinesis is the path.

## Key concepts (for existing users)

### Signal Catalog

A schema of standardized vehicle signals (engine RPM, brake pressure, GPS, accelerometer, camera frames). Mapped to per-vehicle-model signal representations (DBC files for CAN-bus signals).

### Vehicles and fleets

Each vehicle is registered to FleetWise with its model + signal mapping. Vehicles group into fleets.

### Campaigns

- **Data collection schemes** defining what data to collect from which vehicles.
- **Triggers** — time-based, condition-based (e.g., "collect when brake pressure exceeds X"), event-based.
- **Destinations** — Amazon S3 or Timestream.

### Edge agent

Software on the vehicle that subscribes to CAN-bus / OBD-II / camera / radar / lidar signals and ships per the campaign config. Optional Greengrass-hosted.

### Vision system data

- Camera frames, radar / lidar point clouds.
- Synchronization across sensors (timestamps align across cameras / radar / lidar).

### Intelligent data collection

Only ship signals you need; downsample, filter, aggregate at the edge to reduce bandwidth.

## Pricing model (legacy)

- **Per vehicle per month**.
- **Per million data points ingested**.
- **Storage** at S3 / Timestream rates.

## Migration considerations (for existing users)

- **AWS recommends staying** on FleetWise through the existing-customer period if your workload is stable.
- For new vehicles / new fleets, evaluate building on IoT Core + Greengrass + Kinesis / MSK + Timestream for InfluxDB / S3 + custom catalog management.
- Third-party automotive platforms (Foxglove for visualization, Cosmos for messaging-style, OEM-specific platforms) may fit your use case.
- Start the migration assessment early — automotive telemetry pipelines are non-trivial to rebuild.

## Pairs well with these repo pages

- [IoT Core](iot-core.md), [IoT Greengrass](iot-greengrass.md), [Kinesis](../analytics/kinesis.md), [Timestream](../database/timestream.md), [S3](../storage/s3.md) — the components of an alternative custom telemetry pipeline.

## Further reading

- [AWS IoT FleetWise documentation](https://docs.aws.amazon.com/iot-fleetwise/).
- [AWS IoT FleetWise availability change](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/iotfleetwise-availability-change.html).
- [Campaigns and intelligent data collection](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/intelligent-data-collection.html).
- [Vision system data](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/vision-system-data.html).
