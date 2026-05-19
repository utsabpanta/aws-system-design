"""Reference architecture: multi-region active-active on AWS.

Belongs to: docs/04-reference-architectures/multi-region-active-active.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Fargate, Lambda
from diagrams.aws.database import Aurora, Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import (
    APIGateway,
    CloudFront,
    GlobalAccelerator,
    Route53,
)
from diagrams.aws.security import ACM, Cognito
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "multi_region_active_active")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Multi-region active-active",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Global users")

    with Cluster("Global edge"):
        dns = Route53("Route 53\n(latency / geo / failover)")
        cdn = CloudFront("CloudFront")
        gax = GlobalAccelerator("Global Accelerator\n(static anycast IPs)")
        tls = ACM("ACM\n(us-east-1 for CloudFront)")
        cognito = Cognito("Cognito\n(per-region pools +\nexternal IdP federation)")

    with Cluster("Region A (us-east-1)"):
        api_a = APIGateway("API Gateway")
        fn_a = Lambda("Lambda")
        svc_a = Fargate("ECS Fargate")
        ddb_a = Dynamodb("DynamoDB\n(global tables replica)")
        aur_a = Aurora("Aurora Global\nprimary writer")
        s3_a = S3("S3 bucket\n(replicated)")

    with Cluster("Region B (eu-west-1)"):
        api_b = APIGateway("API Gateway")
        fn_b = Lambda("Lambda")
        svc_b = Fargate("ECS Fargate")
        ddb_b = Dynamodb("DynamoDB\n(global tables replica)")
        aur_b = Aurora("Aurora Global\nread replicas\n(promote on failover)")
        s3_b = S3("S3 bucket\n(CRR target)")

    cw = Cloudwatch("CloudWatch\n(cross-Region dashboards,\nhealth checks)")

    # User routing
    users >> Edge(label="HTTPS") >> dns
    dns >> cdn
    cdn >> gax
    gax >> Edge(label="closest healthy") >> api_a
    gax >> Edge(label="closest healthy") >> api_b
    tls >> Edge(style="dotted", color="gray") >> cdn
    users >> Edge(label="auth", style="dashed") >> cognito

    # Region A
    api_a >> fn_a >> ddb_a
    api_a >> svc_a >> aur_a
    svc_a >> s3_a

    # Region B
    api_b >> fn_b >> ddb_b
    api_b >> svc_b >> aur_b
    svc_b >> s3_b

    # Cross-region replication
    ddb_a >> Edge(label="Global Tables\n(multi-active, last-writer-wins)",
                  color="navy", style="bold") >> ddb_b
    ddb_b >> Edge(color="navy", style="bold") >> ddb_a
    aur_a >> Edge(label="Aurora Global\n(physical replication, ~1s lag)",
                  color="navy", style="bold") >> aur_b
    s3_a >> Edge(label="S3 Cross-Region Replication",
                 color="navy", style="bold") >> s3_b

    # Observability
    api_a >> Edge(style="dotted", color="gray") >> cw
    api_b >> Edge(style="dotted", color="gray") >> cw
    dns >> Edge(label="health checks", style="dotted", color="gray") >> cw
