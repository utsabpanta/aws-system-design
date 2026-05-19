"""High-level architecture for the search-autocomplete design.

Belongs to: docs/03-interview-designs/search-autocomplete.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    Athena,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataStreams,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "search_autocomplete")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Search autocomplete",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Serving path (every keystroke)"):
        cdn = CloudFront("CloudFront\n(cache short prefixes)")
        api = APIGateway("HTTP API")
        serve_fn = Lambda("autocomplete")
        opensearch = OpenSearch("OpenSearch\n(suggester)")
        valkey = ElasticacheForRedis("Valkey\n(trending + personal)")
        personal = Dynamodb("personal history")

    with Cluster("Build path (offline / streaming)"):
        stream = KinesisDataStreams("search events")
        flink = ManagedFlink("Managed Flink\n(rolling counts)")
        rebuild_fn = Lambda("hourly rebuild")
        index = Dynamodb("prefix_index")
        archive = S3("event archive")
        athena = Athena("Athena")

    cw = Cloudwatch("CloudWatch\n(latency / hit rate)")

    # Serving
    users >> Edge(label="GET /autocomplete?q=wea", color="navy") >> cdn
    cdn >> Edge(label="long prefix - miss", style="dashed") >> api >> serve_fn
    serve_fn >> Edge(label="base top-K") >> opensearch
    serve_fn >> Edge(label="trending merge") >> valkey
    serve_fn >> Edge(label="personal merge") >> personal

    # Build
    users >> Edge(label="search query logged", style="dashed", color="darkgreen") >> stream
    stream >> flink >> valkey
    stream >> Edge(label="archive", style="dotted") >> archive >> athena
    athena >> Edge(label="hourly counts") >> rebuild_fn
    rebuild_fn >> Edge(label="rebuild") >> opensearch
    rebuild_fn >> index

    # Observability
    serve_fn >> Edge(style="dotted", color="gray") >> cw
    flink >> Edge(style="dotted", color="gray") >> cw
