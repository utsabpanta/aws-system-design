"""High-level architecture for the YouTube / Netflix streaming design.

Belongs to: docs/03-interview-designs/youtube-netflix-streaming.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import (
    AmazonOpensearchService as OpenSearch,
    Athena,
    KinesisDataAnalytics as ManagedFlink,
    KinesisDataStreams,
)
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.management import Cloudwatch
from diagrams.aws.media import (
    ElementalMediaconvert as MediaConvert,
    ElementalMedialive as MediaLive,
    ElementalMediapackage as MediaPackage,
)
from diagrams.aws.network import APIGateway, CloudFront
from diagrams.aws.security import Shield, WAF
from diagrams.aws.storage import S3, S3Glacier
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "youtube_netflix_streaming")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "YouTube / Netflix streaming",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    uploaders = Users("Creators\n(upload)")
    viewers = Users("Viewers\n(playback)")

    with Cluster("Edge"):
        cdn = CloudFront("CloudFront\n(manifests + segments)")
        waf = WAF("WAF")
        shield = Shield("Shield")

    with Cluster("Upload + transcoding (VOD)"):
        api = APIGateway("Upload API")
        upload_fn = Lambda("upload handler")
        originals = S3("originals")
        mc = MediaConvert("MediaConvert\n(HLS / DASH ladder)")
        variants = S3("variants + manifests")

    with Cluster("Live variant"):
        ml = MediaLive("MediaLive\n(real-time encode)")
        mp = MediaPackage("MediaPackage\n(LL-HLS + DRM)")

    with Cluster("Catalog + stats"):
        videos = Dynamodb("videos")
        stats = Dynamodb("video_stats")
        opensearch = OpenSearch("search")

    with Cluster("Watch events"):
        events_stream = KinesisDataStreams("watch events")
        flink = ManagedFlink("Managed Flink\n(realtime stats)")
        events_archive = S3("event archive")
        athena = Athena("Athena (offline)")

    with Cluster("Cold storage"):
        cold = S3Glacier("Glacier\n(unpopular)")

    cw = Cloudwatch("CloudWatch")

    # Upload + transcode
    uploaders >> Edge(label="presigned upload", color="navy") >> api >> upload_fn
    uploaders >> Edge(label="PUT parts") >> originals
    originals >> Edge(label="S3 event") >> mc >> variants
    upload_fn >> videos

    # Live
    uploaders >> Edge(label="RTMP / SRT", color="purple") >> ml >> mp >> Edge(color="purple") >> cdn

    # Playback
    viewers >> Edge(label="GET manifest") >> cdn
    cdn >> Edge(label="origin pull") >> variants
    viewers >> Edge(label="GET segments") >> cdn

    # Catalog / search
    viewers >> Edge(label="browse / search") >> api
    api >> opensearch
    videos >> Edge(label="DDB Streams", style="dotted") >> opensearch

    # Watch events + stats
    viewers >> Edge(label="play / pause / etc.", style="dashed", color="darkgreen") >> events_stream
    events_stream >> flink >> stats
    events_stream >> events_archive >> athena

    # Cold tiering
    variants >> Edge(label="lifecycle", style="dotted") >> cold

    # Edge security
    shield >> Edge(style="dotted", color="gray") >> cdn
    waf >> Edge(style="dotted", color="gray") >> cdn
    mc >> Edge(style="dotted", color="gray") >> cw
    flink >> Edge(style="dotted", color="gray") >> cw
