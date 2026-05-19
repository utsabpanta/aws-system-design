"""High-level architecture for the Uber ride-sharing design.

Belongs to: docs/03-interview-designs/uber-ride-sharing.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataStreams,
)
from diagrams.aws.compute import Fargate, Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.integration import SimpleNotificationServiceSns as SNS, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Sagemaker
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "uber_ride_sharing")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Uber ride-sharing",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    drivers = Users("Drivers")
    riders = Users("Riders")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        rest = APIGateway("REST API")
        ws = APIGateway("WebSocket API")

    with Cluster("Location pipeline"):
        loc_fn = Fargate("location handler")
        loc_stream = KinesisDataStreams("location stream")
        geo_updater = Lambda("geo index updater")
        geo_cache = ElasticacheForRedis("Valkey\n(geohash -> drivers)")

    with Cluster("Matching + dispatch"):
        match_fn = Lambda("matcher")
        dispatch_fn = Lambda("dispatcher")
        sns = SNS("driver push")

    with Cluster("Trip lifecycle"):
        sm = StepFunctions("trip state machine")
        trips = Dynamodb("trips")
        bus = Dynamodb("trip_events")

    with Cluster("Pricing + ETA"):
        surge_stream = KinesisDataStreams("demand stream")
        flink = ManagedFlink("Managed Flink\n(surge per geohash)")
        surge = Dynamodb("surge multipliers")
        eta = Sagemaker("ETA model")

    with Cluster("Master data"):
        drv_t = Dynamodb("drivers")
        rdr_t = Dynamodb("riders")
        history = S3("trip history")

    cw = Cloudwatch("CloudWatch")

    # Location stream
    drivers >> Edge(label="location every 4s", color="navy") >> rest >> loc_fn
    loc_fn >> Edge(color="navy") >> loc_stream
    loc_stream >> geo_updater >> geo_cache
    geo_updater >> Edge(label="durable", style="dotted") >> drv_t

    # Rider request -> match -> dispatch
    riders >> Edge(label="POST /request", color="darkgreen") >> rest >> match_fn
    match_fn >> Edge(label="query geohash") >> geo_cache
    match_fn >> Edge(label="surge lookup") >> surge
    match_fn >> Edge(label="ETA") >> eta
    match_fn >> dispatch_fn
    dispatch_fn >> Edge(label="assign (conditional)") >> drv_t
    dispatch_fn >> Edge(label="push to driver") >> sns >> drivers
    dispatch_fn >> sm

    # Trip lifecycle
    sm >> trips
    sm >> bus
    drivers >> Edge(label="state updates", style="dashed") >> ws >> sm
    sm >> Edge(label="live updates") >> ws >> riders

    # Surge pipeline
    riders >> Edge(label="request event", style="dashed", color="purple") >> surge_stream
    surge_stream >> flink >> surge

    # History
    bus >> Edge(label="archive", style="dotted") >> history

    # Observability
    loc_fn >> Edge(style="dotted", color="gray") >> cw
    match_fn >> Edge(style="dotted", color="gray") >> cw
    sm >> Edge(style="dotted", color="gray") >> cw
