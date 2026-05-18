"""High-level architecture for the WhatsApp chat design.

Belongs to: docs/03-interview-designs/whatsapp-chat.md
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
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito, KMS
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "whatsapp_chat")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "WhatsApp chat",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    devices = Users("Devices\n(phone / web / tablet)")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(media)")
        cognito = Cognito("Cognito")

    with Cluster("Real-time tier"):
        ws = APIGateway("API Gateway\nWebSocket")
        conn_fn = Lambda("$connect /\n$disconnect")
        msg_fn = Lambda("sendMessage")
        rcpt_fn = Lambda("sendReceipt")

    with Cluster("Storage"):
        connections = Dynamodb("connections\n(user -> conn_id)")
        messages = Dynamodb("messages")
        conv = Dynamodb("conversations")
        conn_cache = ElasticacheForRedis("Valkey\n(hot conn cache)")

    with Cluster("Fan-out + offline"):
        fanout_stream = KinesisDataStreams("Kinesis\n(group fan-out)")
        fanout_fn = Lambda("fan-out worker")
        offline = SQS("offline queues\n(per user)")

    with Cluster("Media"):
        media_fn = Lambda("media handler")
        blobs = S3("blobs\n(SSE-KMS)")
        kms = KMS("KMS")

    with Cluster("Search"):
        opensearch = OpenSearch("OpenSearch\n(message history)")

    cw = Cloudwatch("CloudWatch")

    # Connection lifecycle
    devices >> Edge(label="WS connect") >> ws >> conn_fn >> connections
    conn_fn >> Edge(label="cache", style="dotted") >> conn_cache

    # Send message
    devices >> Edge(label="sendMessage", color="navy") >> ws >> msg_fn
    msg_fn >> Edge(label="lookup recipient", color="navy") >> conn_cache
    msg_fn >> Edge(color="navy") >> messages
    msg_fn >> Edge(label="online -> PostToConnection", color="darkgreen") >> ws
    msg_fn >> Edge(label="offline -> queue", style="dashed") >> offline
    msg_fn >> Edge(label="group -> stream", style="dashed") >> fanout_stream
    fanout_stream >> fanout_fn >> ws

    # Receipts
    devices >> Edge(label="sendReceipt") >> ws >> rcpt_fn >> messages

    # Media
    devices >> Edge(label="GET /media/upload") >> ws >> media_fn >> blobs
    devices >> Edge(label="download via signed URL") >> cdn >> blobs
    kms >> Edge(style="dotted", color="gray") >> blobs

    # Search index
    messages >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Observability
    msg_fn >> Edge(style="dotted", color="gray") >> cw
    fanout_fn >> Edge(style="dotted", color="gray") >> cw
