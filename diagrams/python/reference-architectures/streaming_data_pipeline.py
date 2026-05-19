"""Reference architecture: real-time streaming data pipeline on AWS.

Belongs to: docs/04-reference-architectures/streaming-data-pipeline.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService,
    Athena,
    GlueDataCatalog,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataFirehose,
    KinesisDataStreams,
    ManagedStreamingForKafka,
    Quicksight,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank

OUT = os.environ.get("DIAGRAM_OUT_NAME", "streaming_data_pipeline")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Streaming data pipeline (Kinesis + Flink + S3)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    sources = Blank("Producers\n(apps, IoT, CDC, clickstream)")

    with Cluster("Ingest"):
        stream = KinesisDataStreams("Kinesis Data Streams\n(N shards / on-demand)")
        msk = ManagedStreamingForKafka("MSK\n(alternative for Kafka)")

    with Cluster("Real-time processing"):
        enrich = Lambda("Lambda\n(per-record enrich)")
        flink = ManagedFlink("Managed Flink\n(windows, joins, dedupe)")

    with Cluster("Operational stores"):
        ddb = Dynamodb("DynamoDB\n(per-key state, alerts)")
        os_idx = AmazonOpensearchService("OpenSearch\n(search + dashboards)")

    with Cluster("Analytics lake"):
        firehose = KinesisDataFirehose("Firehose\n(batches → Parquet)")
        lake = S3("S3 lake\n(Iceberg, partitioned by hour)")
        catalog = GlueDataCatalog("Glue Catalog")
        athena = Athena("Athena")
        qs = Quicksight("QuickSight")

    cw = Cloudwatch("CloudWatch\n(IteratorAge, Flink metrics)")

    # Producers -> ingest
    sources >> Edge(label="PutRecord(s)") >> stream
    sources >> Edge(label="alt: Kafka producer", style="dashed") >> msk

    # Hot path: per-record
    stream >> enrich >> ddb
    enrich >> Edge(label="anomaly", color="red") >> os_idx

    # Hot path: stateful streaming
    stream >> Edge(label="windowed agg") >> flink >> os_idx
    flink >> Edge(label="emits derived events", style="dashed") >> stream

    # Cold path: durable lake
    stream >> Edge(label="tee", color="navy") >> firehose >> lake
    lake >> Edge(style="dotted") >> catalog
    catalog >> athena >> qs

    # Observability
    stream >> Edge(style="dotted", color="gray") >> cw
    flink >> Edge(style="dotted", color="gray") >> cw
