"""High-level architecture for the Dropbox / file-storage design.

Belongs to: docs/03-interview-designs/dropbox-file-storage.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import AmazonOpensearchService as OpenSearch
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Cognito, KMS
from diagrams.aws.storage import S3, S3Glacier
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "dropbox_file_storage")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Dropbox / file storage",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    devices = Users("Devices")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront")
        cognito = Cognito("Cognito")

    with Cluster("API tier"):
        api = APIGateway("REST API")
        ws = APIGateway("WebSocket")
        check_fn = Lambda("chunk check / upload URL")
        commit_fn = Lambda("commit manifest")
        download_fn = Lambda("download / ACL")
        notif_fn = Lambda("notification dispatcher")

    with Cluster("Metadata"):
        files = Dynamodb("files")
        versions = Dynamodb("file_versions")
        chunks = Dynamodb("chunks\n(hash -> S3 + ref_count)")
        acl = Dynamodb("acl + share_links")

    with Cluster("Object storage"):
        s3 = S3("chunks/<hash>")
        kms = KMS("KMS")
        glacier = S3Glacier("Glacier\n(cold tier)")

    with Cluster("Eventing + search"):
        bus = Eventbridge("EventBridge")
        opensearch = OpenSearch("OpenSearch\n(file search)")

    cw = Cloudwatch("CloudWatch")

    # Upload flow
    devices >> Edge(label="check / upload", color="navy") >> api >> check_fn
    check_fn >> Edge(label="lookup existing", style="dotted") >> chunks
    devices >> Edge(label="PUT chunk (presigned)", color="navy") >> s3
    devices >> Edge(label="commit manifest", color="navy") >> api >> commit_fn
    commit_fn >> files
    commit_fn >> versions
    commit_fn >> Edge(label="ref_count++") >> chunks

    # Change notification
    versions >> Edge(label="DDB Streams", style="dashed") >> bus
    bus >> notif_fn >> ws >> Edge(label="file_changed") >> devices

    # Download
    devices >> Edge(label="GET /files/:id/download") >> api >> download_fn
    download_fn >> Edge(label="check ACL") >> acl
    download_fn >> Edge(label="manifest") >> versions
    download_fn >> Edge(label="presigned chunks") >> devices
    devices >> Edge(label="GET chunks") >> cdn >> s3

    # Tiering
    s3 >> Edge(label="lifecycle", style="dotted") >> glacier
    kms >> Edge(style="dotted", color="gray") >> s3

    # Search index
    files >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Observability
    commit_fn >> Edge(style="dotted", color="gray") >> cw
    download_fn >> Edge(style="dotted", color="gray") >> cw
