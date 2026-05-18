"""High-level architecture for the distributed-counter design.

Belongs to: docs/03-interview-designs/distributed-counter.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import Athena, KinesisDataFirehose
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamodbDax as DAX, Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "distributed_counter")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Distributed counter",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    writers = Users("Writers\n(huge volume)")
    readers = Users("Readers")

    with Cluster("API"):
        api = APIGateway("API Gateway")
        inc_fn = Lambda("increment\n(pick random shard)")
        read_fn = Lambda("read\n(sum shards)")

    with Cluster("Storage"):
        ddb = Dynamodb("counters\n(counter_id, shard_id)")
        meta = Dynamodb("counter_meta")
        dax = DAX("DAX\n(sub-ms cache)")

    with Cluster("Historical analytics"):
        firehose = KinesisDataFirehose("Firehose")
        bucket = S3("events / Parquet")
        athena = Athena("Athena")

    cw = Cloudwatch("CloudWatch\n(throttle metrics)")

    writers >> Edge(label="POST /increment", color="navy") >> api >> inc_fn
    inc_fn >> Edge(label="UpdateItem ADD count\n(random shard)", color="navy") >> ddb
    inc_fn >> Edge(label="event log", style="dashed", color="darkgreen") >> firehose

    readers >> Edge(label="GET /counter") >> api >> read_fn
    read_fn >> Edge(label="check cache") >> dax
    dax >> Edge(label="cache miss\nQuery shards", style="dashed") >> ddb
    read_fn >> Edge(label="shard count", style="dotted") >> meta

    firehose >> bucket >> athena

    ddb >> Edge(style="dotted", color="gray") >> cw
    inc_fn >> Edge(style="dotted", color="gray") >> cw
