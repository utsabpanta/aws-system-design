"""High-level architecture for the pastebin design.

Belongs to: docs/03-interview-designs/pastebin.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import KMS, WAF
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "pastebin")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Pastebin",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(cache public reads)")
        waf = WAF("WAF\n(rate / bot)")

    with Cluster("API tier"):
        api = APIGateway("API Gateway")
        create_fn = Lambda("create")
        read_fn = Lambda("read / auth")
        unlock_fn = Lambda("unlock\n(password)")

    with Cluster("Storage"):
        meta = Dynamodb("pastes\n(metadata + TTL)")
        blobs = S3("pastes/*\n(blobs + lifecycle)")
        kms = KMS("KMS")

    cw = Cloudwatch("CloudWatch")

    # Create path
    users >> Edge(label="POST /pastes", color="navy") >> waf >> Edge(color="navy") >> cdn
    cdn >> Edge(color="navy", style="dashed", label="miss") >> api >> create_fn
    create_fn >> Edge(label="put blob", color="navy") >> blobs
    create_fn >> Edge(label="put metadata", color="navy") >> meta

    # Read path (public — cached); read path (private — through Lambda)
    users >> Edge(label="GET /:code") >> cdn
    cdn >> Edge(label="public hit", color="darkgreen") >> blobs
    cdn >> Edge(label="private / auth miss", style="dashed") >> api >> read_fn
    read_fn >> meta
    read_fn >> Edge(label="presigned URL") >> blobs

    # Password unlock
    users >> Edge(label="POST /:code/unlock", color="purple") >> api >> unlock_fn >> meta

    # Encryption + observability
    kms >> Edge(style="dotted", color="gray") >> blobs
    kms >> Edge(style="dotted", color="gray") >> meta
    create_fn >> Edge(style="dotted", color="gray") >> cw
    read_fn >> Edge(style="dotted", color="gray") >> cw
