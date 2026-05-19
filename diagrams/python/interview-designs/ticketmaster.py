"""High-level architecture for the Ticketmaster (ticket booking) design.

Belongs to: docs/03-interview-designs/ticketmaster.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import AmazonOpensearchService as OpenSearch
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.engagement import SimpleEmailServiceSes as SES
from diagrams.aws.integration import SimpleNotificationServiceSns as SNS, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Shield, WAF
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "ticketmaster")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Ticketmaster",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Buyers\n(spike: 1M concurrent)")

    with Cluster("Edge defense"):
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF\n(CAPTCHA, rate-based)")
        shield = Shield("Shield Advanced")

    with Cluster("Virtual waiting room"):
        wr_api = APIGateway("WR API")
        wr_fn = Lambda("WR controller")
        wr_cache = ElasticacheForRedis("Valkey\n(sorted set per event)")

    with Cluster("Reservation"):
        rsv_api = APIGateway("Reserve API")
        rsv_fn = Lambda("reserve handler\n(TransactWriteItems)")
        rsv_sm = StepFunctions("reservation\nstate machine")
        sweeper = Lambda("expiry sweeper")

    with Cluster("Storage"):
        seats = Dynamodb("seats\n(strong consistency)")
        rsvs = Dynamodb("reservations (TTL)")
        orders = Dynamodb("orders")
        catalog = OpenSearch("event catalog")

    with Cluster("Payment + delivery"):
        pay = Blank("Stripe / Adyen\n(external)")
        pdf = Lambda("ticket render")
        s3 = S3("tickets (PDF)")
        ses = SES("SES (email)")
        sns = SNS("SNS (SMS)")

    cw = Cloudwatch("CloudWatch")

    # Waiting room gating
    users >> cdn >> waf >> Edge(label="join queue") >> wr_api >> wr_fn >> wr_cache
    wr_fn >> Edge(label="admit (token)", color="darkgreen") >> users
    shield >> Edge(style="dotted", color="gray") >> cdn

    # Reservation
    users >> Edge(label="reserve (with token)") >> cdn >> rsv_api >> rsv_fn
    rsv_fn >> Edge(label="TransactWriteItems\n(seat status)") >> seats
    rsv_fn >> Edge(label="create hold") >> rsvs
    rsv_fn >> rsv_sm

    sweeper >> Edge(label="release expired", style="dashed") >> seats
    sweeper >> rsvs

    # Payment + confirmation
    rsv_sm >> Edge(label="call payment") >> pay
    pay >> Edge(label="webhook", style="dashed") >> rsv_sm
    rsv_sm >> Edge(label="confirm") >> orders
    rsv_sm >> pdf >> s3
    rsv_sm >> Edge(label="ticket email") >> ses
    rsv_sm >> sns

    # Catalog
    users >> Edge(label="browse events") >> cdn >> catalog

    # Observability
    rsv_fn >> Edge(style="dotted", color="gray") >> cw
    rsv_sm >> Edge(style="dotted", color="gray") >> cw
