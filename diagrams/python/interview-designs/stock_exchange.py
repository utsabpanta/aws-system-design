"""High-level architecture for the stock exchange / matching engine design.

Belongs to: docs/03-interview-designs/stock-exchange.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    Athena,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataStreams,
    Redshift,
)
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import Aurora
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Shield, WAF
from diagrams.aws.storage import S3, S3Glacier
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "stock_exchange")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Stock exchange (matching engine)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    brokers = Blank("Brokers\n(FIX over leased line / colo)")
    retail = Users("Retail consumers\n(market data)")

    with Cluster("Low-latency tier (colo / EC2 cluster PG)"):
        gateway = EC2("FIX gateway\n(validate + risk pre-check)")
        matcher = EC2("matching engine\n(per-symbol, single-thread)")
        md_pub = EC2("market data publisher")

    with Cluster("Durability + audit"):
        wal = Aurora("event log\n(WAL, semi-sync)")
        archive = S3("event archive\n(years)")
        cold = S3Glacier("regulatory cold storage\n(7+ years)")

    with Cluster("Market data fan-out (retail)"):
        cdn = CloudFront("CloudFront\n(snapshots / delayed)")
        ws = APIGateway("WebSocket API\n(live)")
        md_stream = KinesisDataStreams("market data stream")

    with Cluster("Surveillance + analytics"):
        flink = ManagedFlink("Managed Flink\n(spoofing / wash trade)")
        redshift = Redshift("Redshift\n(historical)")
        athena = Athena("Athena (ad-hoc)")

    with Cluster("Settlement (downstream)"):
        settle = Lambda("settlement service")
        clearinghouse = Blank("DTCC / clearinghouse")

    with Cluster("Edge security"):
        waf = WAF("WAF (retail)")
        shield = Shield("Shield")

    cw = Cloudwatch("CloudWatch")

    # Order flow
    brokers >> Edge(label="FIX NewOrder", color="navy") >> gateway
    gateway >> Edge(label="sequence + ack", color="navy") >> matcher
    matcher >> Edge(label="WAL write (quorum)", color="navy") >> wal
    matcher >> Edge(label="ExecutionReport", color="darkgreen") >> gateway >> brokers

    # Market data
    matcher >> md_pub >> md_stream
    md_pub >> Edge(label="multicast in colo", style="dashed") >> brokers
    md_stream >> ws
    ws >> retail
    cdn >> retail
    shield >> Edge(style="dotted", color="gray") >> cdn
    waf >> Edge(style="dotted", color="gray") >> ws

    # Audit + archive
    wal >> archive
    archive >> Edge(label="lifecycle", style="dotted") >> cold

    # Surveillance
    md_stream >> flink
    flink >> Edge(label="alerts", style="dashed", color="darkred") >> cw

    # Analytics
    archive >> athena
    archive >> redshift

    # Settlement (T+1 / T+2)
    matcher >> Edge(label="end-of-day trades", style="dashed") >> settle >> clearinghouse

    # Observability
    matcher >> Edge(style="dotted", color="gray") >> cw
    gateway >> Edge(style="dotted", color="gray") >> cw
