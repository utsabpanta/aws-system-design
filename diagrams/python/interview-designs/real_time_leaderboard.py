"""High-level architecture for the real-time leaderboard design.

Belongs to: docs/03-interview-designs/real-time-leaderboard.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Shield, WAF
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "real_time_leaderboard")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Real-time leaderboard",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    players = Users("Players / game servers")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF (anti-cheat rate)")
        shield = Shield("Shield")

    with Cluster("Write path"):
        api = APIGateway("API Gateway")
        score_fn = Lambda("score submit")
        ddb = Dynamodb("scores\n(source of truth)")
        stream = KinesisDataStreams("score events")
        sync_fn = Lambda("zset sync")

    with Cluster("Serving"):
        read_fn = Lambda("read handlers\n(top-K / around-me / rank)")
        valkey = ElasticacheForRedis("Valkey\n(ZSET per scope)")
        rebuild_fn = Lambda("cold-start rebuild")

    cw = Cloudwatch("CloudWatch")

    # Score write path: durable first, then to Valkey
    players >> Edge(label="POST /scores", color="navy") >> cdn >> waf >> api >> score_fn
    score_fn >> Edge(label="durable write", color="navy") >> ddb
    score_fn >> Edge(label="publish", color="navy") >> stream
    stream >> sync_fn >> Edge(label="ZADD per scope") >> valkey

    # Reads
    players >> Edge(label="GET top / rank / around-me") >> cdn >> api >> read_fn >> valkey

    # Rebuild on cold start
    ddb >> Edge(label="scan + ZADD", style="dashed") >> rebuild_fn >> valkey

    shield >> Edge(style="dotted", color="gray") >> cdn
    score_fn >> Edge(style="dotted", color="gray") >> cw
    read_fn >> Edge(style="dotted", color="gray") >> cw
