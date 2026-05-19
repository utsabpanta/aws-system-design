"""Reference architecture: data lake on S3.

Belongs to: docs/04-reference-architectures/data-lake-on-s3.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    Athena,
    EMR,
    Glue,
    GlueDataCatalog,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataFirehose,
    LakeFormation,
    Quicksight,
    Redshift,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DatabaseMigrationService as DMS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.storage import S3, S3Glacier
from diagrams.generic.blank import Blank

OUT = os.environ.get("DIAGRAM_OUT_NAME", "data_lake_on_s3")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Data lake on S3 (medallion + Iceberg)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    sources = Blank("Operational sources\n(DB, SaaS, files, IoT)")

    with Cluster("Ingestion"):
        dms = DMS("DMS / Aurora ZeroETL\n(CDC)")
        firehose = KinesisDataFirehose("Firehose\n(streams)")
        flink = ManagedFlink("Managed Flink")
        appflow = Lambda("AppFlow / Lambda\n(SaaS pulls)")

    with Cluster("Lake (S3 medallion zones)"):
        raw = S3("raw/\n(original format)")
        silver = S3("silver/\n(cleansed Parquet)")
        gold = S3("gold/ (Iceberg /\nS3 Tables)")
        cold = S3Glacier("Glacier\n(retention)")

    with Cluster("Catalog + governance"):
        glue = Glue("Glue jobs\n(transform)")
        catalog = GlueDataCatalog("Glue Data Catalog")
        lf = LakeFormation("Lake Formation\n(column / row ACLs)")

    with Cluster("Query engines"):
        athena = Athena("Athena\n(ad-hoc SQL)")
        spec = Redshift("Redshift Spectrum")
        emr = EMR("EMR / EMR Serverless\n(Spark, Trino)")
        sm = Sagemaker("SageMaker\n(ML training)")

    with Cluster("BI"):
        qs = Quicksight("QuickSight")

    cw = Cloudwatch("CloudWatch")

    # Ingestion
    sources >> dms >> raw
    sources >> firehose >> raw
    sources >> flink >> raw
    sources >> appflow >> raw

    # Transform (raw -> silver -> gold)
    raw >> glue >> silver >> glue >> gold

    # Catalog + governance over all zones
    raw >> Edge(style="dotted") >> catalog
    silver >> Edge(style="dotted") >> catalog
    gold >> Edge(style="dotted") >> catalog
    lf >> Edge(label="permission overlay", style="dotted") >> catalog

    # Tiering
    raw >> Edge(label="lifecycle", style="dotted") >> cold

    # Consumption
    catalog >> athena
    catalog >> spec
    catalog >> emr
    silver >> sm
    gold >> sm
    athena >> qs
    spec >> qs

    # Observability
    glue >> Edge(style="dotted", color="gray") >> cw
    emr >> Edge(style="dotted", color="gray") >> cw
