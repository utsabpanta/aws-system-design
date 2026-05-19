"""High-level architecture for the Airbnb booking design.

Belongs to: docs/03-interview-designs/airbnb-booking.md
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
from diagrams.aws.integration import Eventbridge, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "airbnb_booking")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Airbnb booking",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    guests = Users("Guests")
    hosts = Users("Hosts")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(photos + search cache)")
        api = APIGateway("API Gateway")

    with Cluster("Search + browse"):
        search_fn = Lambda("search")
        opensearch = OpenSearch("listings + facets + geo\n+ rollup")
        listing_fn = Lambda("listing detail")
        listing_cache = ElasticacheForRedis("Valkey\n(hot listings)")
        ranker = Sagemaker("search ranker")

    with Cluster("Booking"):
        book_fn = Lambda("booking handler\n(TransactWriteItems)")
        saga = StepFunctions("booking saga")

    with Cluster("Storage"):
        listings = Dynamodb("listings")
        availability = Dynamodb("availability\n(per date)")
        rollup = Dynamodb("availability_rollup")
        bookings = Dynamodb("bookings")
        reviews = Dynamodb("reviews")
        photos = S3("photos")

    with Cluster("Host tools"):
        host_fn = Lambda("host portal")
        avail_stream = KinesisDataStreams("availability changes")
        rollup_fn = Lambda("rollup updater")
        ical = Lambda("iCal sync")

    with Cluster("Comms"):
        bus = Eventbridge("EventBridge")
        ses = SES("SES")

    cw = Cloudwatch("CloudWatch")

    # Search path
    guests >> Edge(label="search") >> cdn >> api >> search_fn
    search_fn >> Edge(label="text + facets + geo + rollup") >> opensearch
    search_fn >> ranker

    # Listing detail
    guests >> Edge(label="listing page") >> cdn >> api >> listing_fn
    listing_fn >> listing_cache
    listing_fn >> listings
    listing_fn >> availability
    guests >> Edge(label="photos") >> cdn >> photos

    # Booking
    guests >> Edge(label="POST /bookings", color="navy") >> api >> book_fn
    book_fn >> Edge(label="TransactWriteItems\n(per night)") >> availability
    book_fn >> bookings
    book_fn >> saga
    saga >> Edge(label="payment + confirm") >> bus

    # Host updates
    hosts >> Edge(label="manage listings") >> api >> host_fn
    host_fn >> listings
    host_fn >> availability
    availability >> Edge(label="DDB Streams") >> avail_stream
    avail_stream >> rollup_fn >> rollup
    avail_stream >> Edge(label="reindex") >> opensearch
    hosts >> ical
    ical >> availability

    # Notifications
    bus >> ses

    # Observability
    search_fn >> Edge(style="dotted", color="gray") >> cw
    book_fn >> Edge(style="dotted", color="gray") >> cw
    saga >> Edge(style="dotted", color="gray") >> cw
