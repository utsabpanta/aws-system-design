"""High-level architecture for the URL shortener.

Belongs to: docs/03-interview-designs/url-shortener.md
Shows the redirect (read) path and the click-analytics (write) path.
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import Athena, KinesisDataFirehose, Quicksight
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront, Route53
from diagrams.aws.security import ACM
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "url_shortener")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "URL shortener",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        dns = Route53("Route 53")
        tls = ACM("ACM")
        cdn = CloudFront("CloudFront\n(cache redirects)")

    with Cluster("API tier"):
        api = APIGateway("API Gateway\n(HTTP API)")
        redirect_fn = Lambda("redirect")
        shorten_fn = Lambda("shorten")

    with Cluster("Storage"):
        links = Dynamodb("links\n(short_code PK)")

    with Cluster("Analytics pipeline"):
        firehose = KinesisDataFirehose("Firehose")
        bucket = S3("click logs\n(Parquet)")
        athena = Athena("Athena")
        qs = Quicksight("QuickSight")

    cw = Cloudwatch("CloudWatch\nmetrics + alarms")

    # Read path (dominant traffic)
    users >> Edge(label="GET /:code") >> dns >> cdn
    cdn >> Edge(label="cache miss", style="dashed") >> api >> redirect_fn >> links
    redirect_fn >> Edge(label="click event (async)", style="dotted", color="darkgreen") >> firehose

    # Write path
    users >> Edge(label="POST /shorten", color="navy") >> dns
    dns >> Edge(color="navy") >> api
    api >> Edge(color="navy") >> shorten_fn >> Edge(color="navy") >> links

    # Analytics fan-out
    firehose >> bucket >> athena >> qs

    # Observability (kept light — every box reports here)
    redirect_fn >> Edge(style="dotted", color="gray") >> cw
    shorten_fn >> Edge(style="dotted", color="gray") >> cw

    # Visually anchor TLS to the CDN
    tls >> Edge(style="dotted", color="gray") >> cdn
