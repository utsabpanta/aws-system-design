"""Reference architecture: containerized microservices on ECS.

Belongs to: docs/04-reference-architectures/containerized-microservices-ecs.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, ECS, Fargate
from diagrams.aws.database import Dynamodb, RDS, ElasticacheForRedis
from diagrams.aws.devtools import Codebuild, Codedeploy, Codepipeline
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ELB, CloudFront, Route53
from diagrams.aws.security import ACM, SecretsManager, WAF
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github

OUT = os.environ.get("DIAGRAM_OUT_NAME", "containerized_microservices_ecs")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Containerized microservices on ECS",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users")

    with Cluster("Edge"):
        dns = Route53("Route 53")
        cdn = CloudFront("CloudFront")
        waf = WAF("WAF")
        tls = ACM("ACM")

    with Cluster("Ingress"):
        alb = ELB("ALB\n(shared, host-based routing)")

    with Cluster("ECS cluster (3 AZs, Fargate)"):
        cluster = ECS("ECS cluster")
        orders = Fargate("orders-svc\n(2-10 tasks)")
        payments = Fargate("payments-svc")
        users_svc = Fargate("users-svc")
        notif = Fargate("notif-svc")

    with Cluster("Service-to-service"):
        sc = ECS("Service Connect\n(managed Envoy)")

    with Cluster("State (per service)"):
        orders_db = RDS("orders DB\n(Aurora)")
        users_db = Dynamodb("users DDB")
        cache = ElasticacheForRedis("Valkey cache")

    with Cluster("Container supply chain"):
        repo = Github("git push")
        pipeline = Codepipeline("CodePipeline")
        build = Codebuild("CodeBuild\n(image build + scan)")
        ecr = ECR("ECR")
        deploy = Codedeploy("CodeDeploy\n(blue/green)")

    with Cluster("Config"):
        secrets = SecretsManager("Secrets Manager")

    cw = Cloudwatch("Container Insights\n+ App Signals + X-Ray")

    # Request path
    users >> Edge(label="HTTPS") >> dns >> cdn >> waf >> alb
    tls >> Edge(style="dotted", color="gray") >> alb
    alb >> Edge(label="orders.example.com") >> orders
    alb >> Edge(label="payments.example.com") >> payments

    # Service connect
    orders >> Edge(label="discover + LB") >> sc
    sc >> Edge(label="call users-svc") >> users_svc
    sc >> Edge(label="call payments-svc") >> payments
    sc >> Edge(label="call notif-svc") >> notif

    # State
    orders >> orders_db
    users_svc >> users_db
    payments >> cache

    # Secrets
    secrets >> Edge(style="dotted", color="gray") >> orders
    secrets >> Edge(style="dotted", color="gray") >> payments

    # CI/CD
    repo >> pipeline >> build >> ecr
    pipeline >> deploy >> cluster

    # Observability
    orders >> Edge(style="dotted", color="gray") >> cw
    payments >> Edge(style="dotted", color="gray") >> cw
    users_svc >> Edge(style="dotted", color="gray") >> cw
