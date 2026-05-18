"""High-level architecture for the rate limiter.

Belongs to: docs/03-interview-designs/rate-limiter.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import KinesisDataFirehose
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb, ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import WAF
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "rate_limiter")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Rate limiter",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Clients")

    with Cluster("Edge (layered limits)"):
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF rate-based\n(volumetric)")
        api = APIGateway("API Gateway\n(per-key throttle)")

    with Cluster("App tier"):
        app = Lambda("App handler")

    with Cluster("Rate-limiter service"):
        limiter = Lambda("Limiter\n(Lua check)")
        valkey = ElasticacheForRedis("Valkey cluster\n(token buckets)")
        config = Dynamodb("config\n(per-key rules)")

    with Cluster("Observability"):
        firehose = KinesisDataFirehose("Firehose")
        denials_bucket = S3("denial events")
        cw = Cloudwatch("metrics + alarms")

    users >> cdn >> Edge(label="WAF rules") >> waf >> api >> app
    app >> Edge(label="check(key, n)") >> limiter
    limiter >> Edge(label="EVAL Lua\n(atomic)") >> valkey
    limiter >> Edge(label="load rules\n(cached 5s)", style="dotted") >> config

    limiter >> Edge(label="deny events", style="dashed", color="darkred") >> firehose >> denials_bucket
    limiter >> Edge(style="dotted", color="gray") >> cw
    valkey >> Edge(style="dotted", color="gray") >> cw
