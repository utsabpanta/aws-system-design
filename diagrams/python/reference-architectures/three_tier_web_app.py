"""Reference architecture: three-tier web app.

Belongs to: docs/04-reference-architectures/three-tier-web-app.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2, ECS, Fargate
from diagrams.aws.database import RDS, ElasticacheForRedis
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ELB, CloudFront, InternetGateway, NATGateway, Route53
from diagrams.aws.security import ACM, SecretsManager, WAF
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "three_tier_web_app")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Three-tier web app",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        dns = Route53("Route 53")
        cdn = CloudFront("CloudFront\n(optional)")
        waf = WAF("WAF")
        tls = ACM("ACM cert")

    with Cluster("VPC (3 AZs)"):
        igw = InternetGateway("IGW")

        with Cluster("Public subnets (per AZ)"):
            alb = ELB("ALB")
            nat = NATGateway("NAT\n(per AZ)")

        with Cluster("Private app subnets"):
            ecs = ECS("ECS service")
            tasks = Fargate("Fargate tasks\n(auto-scale)")
            workers = EC2("worker ASG\n(SQS consumers)")

        with Cluster("Isolated DB subnets"):
            db = RDS("Aurora / RDS\nMulti-AZ")
            cache = ElasticacheForRedis("ElastiCache\n(Valkey)")

    with Cluster("Async + storage"):
        q = SQS("SQS\n(background jobs)")
        s3 = S3("S3\n(uploads / exports)")

    with Cluster("Config"):
        secrets = SecretsManager("DB creds\n(rotated)")

    cw = Cloudwatch("CloudWatch + X-Ray")

    # Request path
    users >> Edge(label="HTTPS") >> dns >> cdn >> waf >> alb
    tls >> Edge(style="dotted", color="gray") >> alb
    alb >> ecs >> tasks
    tasks >> db
    tasks >> cache
    tasks >> Edge(label="presign upload", style="dashed") >> s3

    # Background work
    tasks >> Edge(label="enqueue job") >> q >> workers
    workers >> db
    workers >> s3

    # Outbound through NAT
    tasks >> Edge(label="outbound (3rd party)", style="dotted") >> nat >> igw

    # Secrets
    secrets >> Edge(style="dotted", color="gray") >> tasks
    secrets >> Edge(style="dotted", color="gray") >> workers

    # Observability
    tasks >> Edge(style="dotted", color="gray") >> cw
    workers >> Edge(style="dotted", color="gray") >> cw
    db >> Edge(style="dotted", color="gray") >> cw
