"""High-level architecture for the ad-click aggregator design.

Belongs to: docs/03-interview-designs/ad-click-aggregator.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    Athena,
    EMR,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataFirehose,
    KinesisDataStreams,
    Redshift,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "ad_click_aggregator")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Ad click aggregator (Lambda architecture)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    ad_servers = Users("Ad servers\n(produce events)")
    advertisers = Users("Advertisers\n(dashboards + billing)")

    with Cluster("Ingest"):
        stream = KinesisDataStreams("event stream\n(sharded by ad_id)")
        firehose = KinesisDataFirehose("Firehose")

    with Cluster("Real-time pipeline"):
        flink = ManagedFlink("Managed Flink\n(rolling windows)")
        fraud_ml = Sagemaker("fraud model")
        rt_agg = Dynamodb("realtime_agg")
        opensearch = OpenSearch("OpenSearch\n(slice + dice)")

    with Cluster("Batch pipeline (exact)"):
        archive = S3("events.parquet\n(partitioned)")
        emr = EMR("EMR / Glue\n(daily)")
        athena = Athena("Athena\n(ad-hoc)")
        redshift = Redshift("Redshift\n(billing)")

    with Cluster("Serving"):
        api = APIGateway("Dashboard + billing API")
        api_fn = Lambda("handlers")

    cw = Cloudwatch("CloudWatch (lag)")

    # Ingest
    ad_servers >> Edge(label="POST event", color="navy") >> stream
    stream >> firehose >> archive

    # Real-time
    stream >> flink
    flink >> Edge(label="fraud filter") >> fraud_ml
    flink >> rt_agg
    flink >> opensearch

    # Batch
    archive >> emr >> redshift
    archive >> athena

    # Serving
    advertisers >> api >> api_fn
    api_fn >> rt_agg
    api_fn >> redshift
    api_fn >> opensearch

    # Observability
    flink >> Edge(style="dotted", color="gray") >> cw
    emr >> Edge(style="dotted", color="gray") >> cw
