"""High-level architecture for the Google Docs collaborative editing design.

Belongs to: docs/03-interview-designs/google-docs-collab.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Fargate, Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito, KMS
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "google_docs_collab")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Google Docs (collaborative editing)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    editors = Users("Editors\n(multiple per doc)")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(UI)")
        cognito = Cognito("Cognito / SSO")

    with Cluster("Real-time tier"):
        ws = APIGateway("WebSocket API")
        rest = APIGateway("REST API")
        conn_fn = Lambda("connect / route")
        op_fn = Lambda("op router")

    with Cluster("Stateful doc servers"):
        doc_srv = Fargate("doc servers\n(in-memory state per doc;\nOT transform / CRDT merge)")
        sessions = ElasticacheForRedis("Valkey\n(presence + cursors)")

    with Cluster("Durability"):
        ops = Dynamodb("op_log\n(append-only)")
        docs = Dynamodb("documents + ACL")
        snapshots = S3("snapshots\n(periodic + history)")

    with Cluster("Comments / events"):
        comments = Dynamodb("comments")
        bus = Eventbridge("EventBridge")

    kms = KMS("KMS")
    cw = Cloudwatch("CloudWatch")

    # Open doc
    editors >> Edge(label="WS connect") >> cdn >> ws >> conn_fn
    conn_fn >> Edge(label="check ACL") >> docs
    conn_fn >> Edge(label="route to doc server\n(hash doc_id)") >> doc_srv
    conn_fn >> Edge(label="presence", style="dotted") >> sessions

    # Send op
    editors >> Edge(label="sendOp", color="navy") >> ws >> op_fn >> doc_srv
    doc_srv >> Edge(label="transform / merge", color="navy") >> doc_srv
    doc_srv >> Edge(label="append op_seq", color="navy") >> ops
    doc_srv >> Edge(label="broadcast", color="darkgreen") >> ws >> editors

    # Snapshots + history
    doc_srv >> Edge(label="periodic snapshot", style="dashed") >> snapshots
    doc_srv >> Edge(label="cold start: snapshot + tail op log", style="dashed") >> snapshots
    snapshots >> Edge(style="dashed") >> doc_srv

    # Cursors / presence
    editors >> Edge(label="cursor", style="dotted") >> ws >> doc_srv >> sessions

    # Comments
    editors >> Edge(label="comment") >> rest >> comments >> bus

    # Security
    kms >> Edge(style="dotted", color="gray") >> ops
    kms >> Edge(style="dotted", color="gray") >> snapshots

    # Observability
    doc_srv >> Edge(style="dotted", color="gray") >> cw
    op_fn >> Edge(style="dotted", color="gray") >> cw
