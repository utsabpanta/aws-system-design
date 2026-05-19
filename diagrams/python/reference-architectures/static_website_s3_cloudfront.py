"""Reference architecture: static website on S3 + CloudFront.

Belongs to: docs/04-reference-architectures/static-website-s3-cloudfront.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.devtools import Codepipeline
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import CloudFront, Route53
from diagrams.aws.security import ACM, WAF
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github

OUT = os.environ.get("DIAGRAM_OUT_NAME", "static_website_s3_cloudfront")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Static website (S3 + CloudFront)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Visitors")

    with Cluster("Edge"):
        dns = Route53("Route 53\n(custom domain)")
        cdn = CloudFront("CloudFront\n(OAC, HTTPS, WAF, HSTS)")
        tls = ACM("ACM cert\n(us-east-1)")
        waf = WAF("WAF (optional)")

    with Cluster("Origin (private)"):
        bucket = S3("site bucket\n(versioned, BPA on)")

    with Cluster("Deploy pipeline"):
        repo = Github("git push main")
        ci = Codepipeline("CodePipeline /\nGitHub Actions")
        edge_fn = Lambda("(opt) CloudFront\nFunction / Lambda@Edge")

    cw = Cloudwatch("CloudWatch\n(logs + alarms)")

    # Read path
    users >> Edge(label="GET https://www.example.com") >> dns >> cdn
    cdn >> Edge(label="OAC SigV4", style="dashed") >> bucket

    # TLS + security
    tls >> Edge(style="dotted", color="gray") >> cdn
    waf >> Edge(style="dotted", color="gray") >> cdn

    # Optional edge customization
    edge_fn >> Edge(label="header rewrite /\nroute normalize", style="dotted") >> cdn

    # Deploy
    repo >> ci
    ci >> Edge(label="aws s3 sync --delete", color="navy") >> bucket
    ci >> Edge(label="cloudfront create-invalidation\n(/index.html)", color="navy") >> cdn

    cdn >> Edge(style="dotted", color="gray") >> cw
