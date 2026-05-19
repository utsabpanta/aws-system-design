"""High-level architecture for the web-crawler design.

Belongs to: docs/03-interview-designs/web-crawler.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    KinesisDataFirehose,
    KinesisDataStreams,
)
from diagrams.aws.compute import Fargate, Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3, S3Glacier
from diagrams.onprem.network import Internet

OUT = os.environ.get("DIAGRAM_OUT_NAME", "web_crawler")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Web crawler",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    web = Internet("Public web")

    with Cluster("Frontier"):
        frontier = SQS("URL frontier\n(FIFO, MessageGroupId=domain)")
        rate_limit = ElasticacheForRedis("Valkey\n(per-domain rate)")

    with Cluster("Fetch + parse"):
        fetcher = Fargate("fetcher workers")
        parser = Lambda("parser")
        fetch_stream = KinesisDataStreams("fetch events")

    with Cluster("State"):
        url_state = Dynamodb("url_state")
        content = Dynamodb("content (hash dedup)")
        domain_policy = Dynamodb("domain_policy\n(robots.txt)")

    with Cluster("Storage + index"):
        raw = S3("raw HTML\n(gzip)")
        cold = S3Glacier("cold tier")
        firehose = KinesisDataFirehose("Firehose")
        opensearch = OpenSearch("OpenSearch")

    cw = Cloudwatch("CloudWatch")

    # Fetch loop
    frontier >> fetcher
    fetcher >> Edge(label="check / update", style="dotted") >> url_state
    fetcher >> Edge(label="rate check", style="dotted") >> rate_limit
    fetcher >> Edge(label="robots.txt") >> domain_policy
    fetcher >> Edge(label="HTTP fetch", color="navy") >> web
    fetcher >> Edge(label="put HTML", color="navy") >> raw
    fetcher >> Edge(label="event") >> fetch_stream

    # Parse + dedup + enqueue
    fetch_stream >> parser
    parser >> Edge(label="content dedup") >> content
    parser >> Edge(label="extracted text") >> firehose >> opensearch
    parser >> Edge(label="new URLs") >> frontier

    # Tiering
    raw >> Edge(label="lifecycle", style="dotted") >> cold

    # Observability
    fetcher >> Edge(style="dotted", color="gray") >> cw
    parser >> Edge(style="dotted", color="gray") >> cw
