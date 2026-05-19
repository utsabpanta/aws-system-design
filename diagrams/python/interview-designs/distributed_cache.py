"""High-level architecture for the distributed-cache design.

Belongs to: docs/03-interview-designs/distributed-cache.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import ElasticacheForRedis
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3
from diagrams.onprem.client import Client

OUT = os.environ.get("DIAGRAM_OUT_NAME", "distributed_cache")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Distributed cache",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    clients = Client("Smart clients\n(local topology)")

    with Cluster("Cluster (shard A: primary + replicas)"):
        prim_a = ElasticacheForRedis("Primary A\n(slots 0-5460)")
        rep_a1 = ElasticacheForRedis("Replica A-1\n(other AZ)")
        rep_a2 = ElasticacheForRedis("Replica A-2")

    with Cluster("Cluster (shard B)"):
        prim_b = ElasticacheForRedis("Primary B\n(slots 5461-10922)")
        rep_b1 = ElasticacheForRedis("Replica B-1")

    with Cluster("Cluster (shard C)"):
        prim_c = ElasticacheForRedis("Primary C\n(slots 10923-16383)")
        rep_c1 = ElasticacheForRedis("Replica C-1")

    with Cluster("Coordination + persistence"):
        gossip = EC2("Gossip / cluster bus\n(or coordinator)")
        snapshots = S3("RDB snapshots\n+ AOF backup")

    cw = Cloudwatch("CloudWatch\n(per-node metrics)")

    # Client routing: hash(key) -> slot -> primary
    clients >> Edge(label="hash(key) -> slot 1234") >> prim_a
    clients >> Edge(label="slot 6789") >> prim_b
    clients >> Edge(label="slot 12345") >> prim_c

    # Replication
    prim_a >> Edge(label="async replication", style="dashed", color="darkgreen") >> rep_a1
    prim_a >> Edge(style="dashed", color="darkgreen") >> rep_a2
    prim_b >> Edge(style="dashed", color="darkgreen") >> rep_b1
    prim_c >> Edge(style="dashed", color="darkgreen") >> rep_c1

    # Coordination
    prim_a >> Edge(label="gossip", style="dotted") >> gossip
    prim_b >> Edge(style="dotted") >> gossip
    prim_c >> Edge(style="dotted") >> gossip
    gossip >> Edge(label="topology update\n(MOVED)", style="dashed") >> clients

    # Persistence
    prim_a >> Edge(label="snapshot", style="dotted") >> snapshots
    prim_b >> Edge(style="dotted") >> snapshots
    prim_c >> Edge(style="dotted") >> snapshots

    # Observability
    prim_a >> Edge(style="dotted", color="gray") >> cw
    prim_b >> Edge(style="dotted", color="gray") >> cw
    prim_c >> Edge(style="dotted", color="gray") >> cw
