"""High-level architecture for the Twitter feed design.

Belongs to: docs/03-interview-designs/twitter-feed.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataStreams,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, DynamodbDax as DAX, ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import WAF
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "twitter_feed")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Twitter feed",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF (abuse)")

    with Cluster("API tier"):
        api = APIGateway("API Gateway")
        post_fn = Lambda("post")
        tl_fn = Lambda("timeline read")
        search_fn = Lambda("search")
        rank_fn = Lambda("ranker")

    with Cluster("Storage"):
        tweets = Dynamodb("tweets")
        timeline = Dynamodb("home_timeline\n(precomputed)")
        follow = Dynamodb("follow graph")
        dax = DAX("DAX")

    with Cluster("Fan-out + streaming"):
        stream = KinesisDataStreams("tweet stream")
        fanout = Lambda("fan-out worker")
        flink = ManagedFlink("Managed Flink\n(trends + abuse)")

    with Cluster("Search + cache"):
        opensearch = OpenSearch("OpenSearch")
        cache = ElasticacheForRedis("Valkey\n(celebrity + trends)")
        ml = Sagemaker("SageMaker\n(ranking)")

    cw = Cloudwatch("CloudWatch")

    # Post path
    users >> Edge(label="POST /tweets", color="navy") >> cdn >> waf >> api >> post_fn
    post_fn >> tweets
    post_fn >> Edge(label="publish event", color="navy") >> stream

    # Fan-out
    stream >> fanout
    fanout >> Edge(label="lookup", style="dotted") >> follow
    fanout >> Edge(label="push (regular)", style="dashed") >> timeline
    fanout >> Edge(label="cache (celebrity)", style="dashed") >> cache

    # Streaming for trends / abuse
    stream >> flink >> cache

    # Read path
    users >> Edge(label="GET /home-timeline") >> cdn
    cdn >> Edge(style="dashed", label="miss") >> api >> tl_fn
    tl_fn >> Edge(label="precomputed") >> dax >> timeline
    tl_fn >> Edge(label="merge celeb") >> cache
    tl_fn >> Edge(label="rank") >> rank_fn >> ml

    # Search
    tweets >> Edge(label="DDB Streams", style="dotted") >> opensearch
    users >> Edge(label="GET /search") >> api >> search_fn >> opensearch

    # Observability
    post_fn >> Edge(style="dotted", color="gray") >> cw
    tl_fn >> Edge(style="dotted", color="gray") >> cw
