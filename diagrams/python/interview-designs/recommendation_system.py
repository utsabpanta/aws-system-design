"""High-level architecture for the recommendation-system design.

Belongs to: docs/03-interview-designs/recommendation-system.md
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
from diagrams.aws.database import Dynamodb, DynamodbDax as DAX, ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Personalize, Sagemaker
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "recommendation_system")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Recommendation system",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Serving (two-stage)"):
        api = APIGateway("Recs API")
        candgen = Lambda("candidate generator")
        ranker = Lambda("ranker")
        ranker_ep = Sagemaker("ranking model\n(real-time endpoint)")
        rec_cache = DAX("recommendation cache")

    with Cluster("Stores"):
        users_t = Dynamodb("users + embeddings")
        items_t = Dynamodb("items + embeddings")
        vecs = OpenSearch("OpenSearch k-NN\n(item vectors)")
        session = ElasticacheForRedis("Valkey\n(session state)")
        excludes = Dynamodb("excludes\n(purchased / disliked)")

    with Cluster("Real-time signals"):
        events = KinesisDataStreams("interaction events")
        flink = ManagedFlink("Managed Flink\n(session aggregator)")

    with Cluster("Offline training"):
        archive = S3("event archive")
        athena = Athena("Athena")
        training = Sagemaker("training jobs\n(embeddings + ranker)")

    with Cluster("Managed alternative"):
        personalize = Personalize("Amazon Personalize\n(opinionated path)")

    cw = Cloudwatch("CloudWatch")

    # Online serving
    users >> Edge(label="GET /recommendations") >> api >> candgen
    candgen >> Edge(label="user emb") >> users_t
    candgen >> Edge(label="k-NN") >> vecs
    candgen >> Edge(label="recent sigs") >> session
    candgen >> Edge(label="~1000 candidates") >> ranker
    ranker >> Edge(label="features") >> items_t
    ranker >> Edge(label="excludes") >> excludes
    ranker >> Edge(label="invoke") >> ranker_ep
    ranker >> Edge(label="cache top-K") >> rec_cache
    ranker >> Edge(label="response") >> api

    # Real-time signals
    users >> Edge(label="POST /events", style="dashed", color="darkgreen") >> events
    events >> flink >> session
    events >> Edge(label="archive", style="dotted") >> archive

    # Offline training loop
    archive >> athena
    athena >> training
    training >> Edge(label="user emb", style="dashed") >> users_t
    training >> Edge(label="item emb", style="dashed") >> items_t
    training >> Edge(label="rebuild index", style="dashed") >> vecs
    training >> Edge(label="deploy", style="dashed") >> ranker_ep

    # Managed path
    events >> Edge(style="dotted", color="purple") >> personalize
    api >> Edge(label="(alt: managed)", style="dotted", color="purple") >> personalize

    candgen >> Edge(style="dotted", color="gray") >> cw
    ranker >> Edge(style="dotted", color="gray") >> cw
