"""High-level architecture for the Slack messaging design.

Belongs to: docs/03-interview-designs/slack-messaging.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    KinesisDataStreams,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.engagement import SimpleEmailServiceSes as SES
from diagrams.aws.integration import SQS, SimpleNotificationServiceSns as SNS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito, KMS
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "slack_messaging")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Slack messaging",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users\n(multiple workspaces)")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        cognito = Cognito("Cognito / SAML")

    with Cluster("Real-time tier"):
        ws = APIGateway("WebSocket API")
        rest = APIGateway("REST API")
        conn_fn = Lambda("connect / sub")
        send_fn = Lambda("sendMessage")

    with Cluster("Storage"):
        msgs = Dynamodb("messages\n(channel_id, ts)")
        channels = Dynamodb("channels + members")
        conns = Dynamodb("connections")
        read_state = Dynamodb("read_state")
        conn_cache = ElasticacheForRedis("Valkey\n(hot conn cache)")

    with Cluster("Fan-out"):
        stream = KinesisDataStreams("message stream")
        fanout = Lambda("fan-out workers\n(by channel)")
        offline_q = SQS("offline push")

    with Cluster("Search (per-workspace)"):
        opensearch = OpenSearch("workspace indices\n(hot + UltraWarm + Cold)")

    with Cluster("Notifications + files"):
        ses = SES("SES")
        sns = SNS("SNS / mobile push")
        files = S3("file attachments")
        kms = KMS("KMS (per workspace)")

    cw = Cloudwatch("CloudWatch")

    # Connections
    users >> Edge(label="WS connect") >> ws >> conn_fn >> conns
    conn_fn >> Edge(label="cache", style="dotted") >> conn_cache

    # Send message
    users >> Edge(label="sendMessage", color="navy") >> ws >> send_fn
    send_fn >> Edge(color="navy") >> msgs
    send_fn >> Edge(label="lookup members") >> channels
    send_fn >> Edge(label="publish") >> stream

    # Fan-out
    stream >> fanout
    fanout >> Edge(label="online -> PostToConnection", color="darkgreen") >> ws
    fanout >> Edge(label="offline -> push", style="dashed") >> offline_q
    offline_q >> ses
    offline_q >> sns

    # Read state
    users >> Edge(label="markRead") >> rest >> read_state

    # Search
    msgs >> Edge(label="DDB Streams", style="dotted") >> opensearch
    users >> Edge(label="GET /search") >> rest >> opensearch

    # Files
    users >> Edge(label="upload") >> rest >> files
    users >> Edge(label="download") >> cdn >> files
    kms >> Edge(style="dotted", color="gray") >> files
    kms >> Edge(style="dotted", color="gray") >> msgs

    # Observability
    send_fn >> Edge(style="dotted", color="gray") >> cw
    fanout >> Edge(style="dotted", color="gray") >> cw
