"""Reference architecture: data warehouse on Redshift.

Belongs to: docs/04-reference-architectures/data-warehouse-redshift.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    Athena,
    Glue,
    KinesisDataFirehose,
    KinesisDataStreams,
    Quicksight,
    Redshift,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Aurora, DatabaseMigrationService as DMS, Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank

OUT = os.environ.get("DIAGRAM_OUT_NAME", "data_warehouse_redshift")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Data warehouse on Redshift",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    saas = Blank("SaaS sources\n(Salesforce, etc.)")

    with Cluster("Sources"):
        aurora = Aurora("Aurora (OLTP)")
        ddb = Dynamodb("DynamoDB")
        onprem = Blank("On-prem DBs")

    with Cluster("Ingestion"):
        zerotl = Lambda("Zero-ETL\n(managed)")
        appflow = Blank("AppFlow")
        firehose = KinesisDataFirehose("Firehose")
        streams = KinesisDataStreams("Kinesis Streams")
        dms = DMS("DMS")
        glue = Glue("Glue jobs\n(batch ETL)")

    with Cluster("Lake (cold tier)"):
        s3 = S3("S3 (Parquet,\npartitioned)")

    with Cluster("Warehouse"):
        rs = Redshift("Redshift\n(Serverless or ra3 RIs)")
        athena = Athena("Athena\n(lake fallback)")

    with Cluster("Consumption"):
        qs = Quicksight("QuickSight")
        bi = Blank("Tableau / Looker /\nPower BI (JDBC)")
        ml = Sagemaker("SageMaker (ML)")

    cw = Cloudwatch("CloudWatch")

    # Zero-ETL direct paths
    aurora >> Edge(label="Zero-ETL", color="darkgreen") >> rs
    ddb >> Edge(label="Zero-ETL", color="darkgreen") >> rs
    saas >> Edge(label="Zero-ETL / AppFlow") >> appflow >> rs

    # Streaming
    streams >> Edge(label="Streaming Ingestion") >> rs
    firehose >> s3
    firehose >> rs

    # Batch + lake
    onprem >> dms >> s3
    s3 >> glue >> s3
    s3 >> Edge(label="Spectrum external table") >> rs
    s3 >> athena

    # Consumption
    rs >> qs
    rs >> bi
    rs >> ml
    athena >> qs

    # Observability
    rs >> Edge(style="dotted", color="gray") >> cw
    glue >> Edge(style="dotted", color="gray") >> cw

    # Zero-ETL note (visual link)
    zerotl >> Edge(style="dotted", color="darkgreen") >> rs
