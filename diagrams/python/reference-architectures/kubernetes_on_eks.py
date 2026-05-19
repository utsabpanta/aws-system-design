"""Reference architecture: Kubernetes on EKS.

Belongs to: docs/04-reference-architectures/kubernetes-on-eks.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2, EKS
from diagrams.aws.database import RDS
from diagrams.aws.management import (
    AmazonManagedGrafana as ManagedGrafana,
    Cloudwatch,
    SystemsManagerParameterStore as ParameterStore,
)
from diagrams.aws.network import ELB, CloudFront, Route53
from diagrams.aws.security import IAMRole, SecretsManager, WAF
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users
from diagrams.onprem.gitops import ArgoCD
from diagrams.onprem.monitoring import Prometheus
from diagrams.onprem.vcs import Github

OUT = os.environ.get("DIAGRAM_OUT_NAME", "kubernetes_on_eks")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Kubernetes on EKS",
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

    with Cluster("EKS cluster (3 AZs)"):
        ctrl = EKS("EKS control plane\n(AWS-managed)")

        with Cluster("Data plane (Auto Mode / Karpenter)"):
            nodes = EC2("Nodes\n(Karpenter-provisioned,\nSpot + on-demand)")

        with Cluster("Workloads"):
            ingress_alb = ELB("AWS LB Controller\n-> ALB / NLB")
            api_pods = EKS("api pods")
            worker_pods = EKS("worker pods")

    with Cluster("Per-pod IAM"):
        pi = IAMRole("Pod Identity\nservice account -> IAM role")

    with Cluster("State"):
        ddb = RDS("Aurora / RDS")
        s3 = S3("S3 (mountpoint CSI)")

    with Cluster("Config + secrets"):
        secrets = SecretsManager("Secrets Manager")
        ssm = ParameterStore("Parameter Store")

    with Cluster("GitOps"):
        repo = Github("manifests / Helm")
        argo = ArgoCD("Argo CD")

    with Cluster("Observability"):
        ci = Cloudwatch("Container Insights\n+ App Signals")
        prom = Prometheus("Managed Prometheus")
        grafana = ManagedGrafana("Managed Grafana")

    # Request path
    users >> Edge(label="HTTPS") >> dns >> cdn >> waf >> ingress_alb >> api_pods
    api_pods >> Edge(label="internal call") >> worker_pods

    # Pod IAM
    pi >> Edge(style="dotted", color="gray") >> api_pods
    pi >> Edge(style="dotted", color="gray") >> worker_pods

    # State
    api_pods >> ddb
    worker_pods >> s3

    # Config
    secrets >> Edge(style="dotted", color="gray") >> api_pods
    ssm >> Edge(style="dotted", color="gray") >> api_pods

    # GitOps
    repo >> argo
    argo >> Edge(label="apply manifests") >> ctrl

    # Cluster runs on nodes
    ctrl >> nodes
    nodes >> api_pods
    nodes >> worker_pods

    # Observability
    api_pods >> Edge(style="dotted", color="gray") >> ci
    api_pods >> Edge(style="dotted", color="gray") >> prom
    prom >> grafana
    ci >> grafana
