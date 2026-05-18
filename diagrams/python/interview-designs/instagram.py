"""High-level architecture for the Instagram design.

Belongs to: docs/03-interview-designs/instagram.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import AmazonOpensearchService as OpenSearch, KinesisDataStreams
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, DynamodbDax as DAX, ElasticacheForRedis
from diagrams.aws.integration import SimpleNotificationServiceSns as SNS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.media import ElementalMediaconvert as MediaConvert
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "instagram")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Instagram",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(media + pages)")
        cognito = Cognito("Cognito")

    with Cluster("API tier"):
        api = APIGateway("API Gateway")
        post_fn = Lambda("post handler")
        feed_fn = Lambda("feed read")
        media_fn = Lambda("media handler")

    with Cluster("Media pipeline"):
        s3_orig = S3("originals")
        mc = MediaConvert("MediaConvert\n(transcode)")
        s3_var = S3("variants")

    with Cluster("Core data"):
        users_t = Dynamodb("users")
        posts_t = Dynamodb("posts")
        feed_t = Dynamodb("feed\n(precomputed)")
        follow_t = Dynamodb("follow graph")
        dax = DAX("DAX (hot tables)")

    with Cluster("Fan-out"):
        post_sns = SNS("post_published")
        fanout = Lambda("fan-out worker")
        fanout_stream = KinesisDataStreams("Kinesis\n(buffer)")

    with Cluster("Search + cache"):
        opensearch = OpenSearch("OpenSearch\n(users/hashtags)")
        cache = ElasticacheForRedis("Valkey\n(celebrity posts)")

    cw = Cloudwatch("CloudWatch")

    # Post flow
    users >> Edge(label="POST /posts", color="navy") >> cdn >> api >> post_fn
    post_fn >> posts_t
    post_fn >> Edge(label="get presigned URL", color="navy") >> media_fn
    media_fn >> Edge(label="PUT original", color="navy") >> s3_orig
    s3_orig >> Edge(label="S3 event") >> mc >> s3_var
    post_fn >> Edge(label="published") >> post_sns

    # Fan-out
    post_sns >> fanout_stream >> fanout
    fanout >> Edge(label="for each follower\n(if not celebrity)", style="dashed") >> feed_t
    fanout >> Edge(label="follower lookup") >> follow_t

    # Read flow
    users >> Edge(label="GET /feed") >> cdn
    cdn >> Edge(style="dashed", label="miss") >> api >> feed_fn
    feed_fn >> Edge(label="precomputed feed") >> dax >> feed_t
    feed_fn >> Edge(label="celebrity merge") >> cache
    feed_fn >> Edge(label="media URLs") >> cdn

    # Search
    posts_t >> Edge(label="DDB Streams", style="dotted") >> opensearch
    users_t >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Observability
    post_fn >> Edge(style="dotted", color="gray") >> cw
    feed_fn >> Edge(style="dotted", color="gray") >> cw
    fanout >> Edge(style="dotted", color="gray") >> cw
