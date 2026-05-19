"""Reference architecture: serverless REST API.

Belongs to: docs/04-reference-architectures/serverless-rest-api.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SQS, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront, Route53
from diagrams.aws.security import ACM, Cognito
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "serverless_rest_api")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Serverless REST API",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Clients\n(SPA / mobile)")

    with Cluster("Edge"):
        dns = Route53("Route 53")
        cdn = CloudFront("CloudFront")
        tls = ACM("ACM")
        cognito = Cognito("Cognito User Pool\n(JWT issuer)")

    with Cluster("API"):
        api = APIGateway("API Gateway HTTP API\n(JWT authorizer)")

    with Cluster("Compute (per-route Lambda)"):
        create_fn = Lambda("create")
        read_fn = Lambda("read / list")
        update_fn = Lambda("update")
        delete_fn = Lambda("delete")
        upload_fn = Lambda("presign upload URL")

    with Cluster("Data"):
        ddb = Dynamodb("single-table\n(on-demand or provisioned)")
        blobs = S3("user uploads\n(presigned URLs)")

    with Cluster("Async / events"):
        bus = Eventbridge("EventBridge\n(domain events)")
        q = SQS("SQS\n(backpressure)")
        sm = StepFunctions("Step Functions\n(multi-step flows)")
        worker = Lambda("background worker")

    cw = Cloudwatch("CloudWatch + X-Ray\n(logs, metrics, traces)")

    # Auth + routing
    users >> Edge(label="login") >> cognito
    users >> Edge(label="API + JWT", color="navy") >> dns >> cdn >> api
    tls >> Edge(style="dotted", color="gray") >> cdn

    # Handlers
    api >> create_fn >> ddb
    api >> read_fn >> ddb
    api >> update_fn >> ddb
    api >> delete_fn >> ddb
    api >> upload_fn
    upload_fn >> Edge(label="presigned URL") >> users
    users >> Edge(label="PUT object") >> blobs

    # Async
    create_fn >> Edge(label="event") >> bus
    bus >> q >> worker
    bus >> sm

    # Observability
    create_fn >> Edge(style="dotted", color="gray") >> cw
    read_fn >> Edge(style="dotted", color="gray") >> cw
    update_fn >> Edge(style="dotted", color="gray") >> cw
