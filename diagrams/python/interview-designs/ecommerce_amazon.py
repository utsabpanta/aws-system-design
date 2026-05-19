"""High-level architecture for the e-commerce / Amazon design.

Belongs to: docs/03-interview-designs/ecommerce-amazon.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import AmazonOpensearchService as OpenSearch
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Aurora, Dynamodb, DynamodbDax as DAX, ElasticacheForRedis
from diagrams.aws.integration import Eventbridge, SQS, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Personalize
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import WAF, Shield, Cognito
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "ecommerce_amazon")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "E-commerce / Amazon",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    customers = Users("Customers")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF")
        shield = Shield("Shield Adv.")
        cognito = Cognito("Cognito")

    with Cluster("API tier"):
        api = APIGateway("API Gateway")
        catalog_fn = Lambda("catalog svc")
        search_fn = Lambda("search svc")
        cart_fn = Lambda("cart svc")
        order_fn = Lambda("order svc")
        review_fn = Lambda("review svc")

    with Cluster("Data stores"):
        catalog = Dynamodb("products")
        cart = Dynamodb("carts")
        inv = Dynamodb("inventory")
        orders = Aurora("orders + ledger")
        reviews = Dynamodb("reviews")
        opensearch = OpenSearch("product + review search")
        hot_cache = ElasticacheForRedis("Valkey\n(hot products)")
        dax = DAX("DAX")

    with Cluster("Order saga"):
        saga = StepFunctions("place-order saga")
        bus = Eventbridge("EventBridge")
        async_q = SQS("async queues")

    with Cluster("Recommendations + media"):
        recs = Personalize("recommendations")
        images = S3("product images")

    cw = Cloudwatch("CloudWatch")

    # Browse / search / product detail
    customers >> Edge(label="GET /products/...") >> cdn
    cdn >> Edge(label="image cache") >> images
    cdn >> Edge(label="API miss", style="dashed") >> waf >> api
    api >> catalog_fn >> dax >> catalog
    catalog_fn >> Edge(label="hot cache", style="dotted") >> hot_cache
    catalog_fn >> Edge(label="recs") >> recs

    api >> search_fn >> opensearch
    catalog >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Cart
    customers >> Edge(label="cart ops") >> api >> cart_fn >> cart

    # Reviews
    customers >> Edge(label="reviews") >> api >> review_fn >> reviews
    reviews >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Place-order saga
    customers >> Edge(label="POST /orders", color="navy") >> api >> order_fn
    order_fn >> saga
    saga >> Edge(label="pay (call payment-system)") >> bus
    saga >> Edge(label="reserve inv\n(conditional decrement)") >> inv
    saga >> Edge(label="commit order") >> orders
    saga >> Edge(label="OrderPlaced event") >> bus
    bus >> async_q

    # Edge defense
    shield >> Edge(style="dotted", color="gray") >> cdn

    # Observability
    order_fn >> Edge(style="dotted", color="gray") >> cw
    saga >> Edge(style="dotted", color="gray") >> cw
