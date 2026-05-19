"""Reference architecture: event-driven architecture on AWS.

Belongs to: docs/04-reference-architectures/event-driven-architecture.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS, Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import (
    Eventbridge,
    SNS,
    SQS,
    StepFunctions,
)
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank

OUT = os.environ.get("DIAGRAM_OUT_NAME", "event_driven_architecture")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Event-driven architecture (EventBridge + SQS + SNS)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    with Cluster("Producers"):
        api = APIGateway("API Gateway\n(synchronous edge)")
        ingest_fn = Lambda("ingest handler")
        service = ECS("internal service\n(ECS / Fargate)")
        saas = Blank("SaaS partner\n(Stripe, Zendesk, ...)")

    with Cluster("Event bus"):
        bus = Eventbridge("EventBridge\ncustom bus + rules")
        archive = S3("Event archive\n(replay)")

    with Cluster("Fan-out + buffering"):
        notify_topic = SNS("SNS topic\n(fan-out)")
        work_q = SQS("SQS standard\n(durable buffer)")
        fifo_q = SQS("SQS FIFO\n(ordered, dedupe)")
        dlq = SQS("DLQ")

    with Cluster("Consumers (decoupled)"):
        projector = Lambda("read-model\nprojector")
        notifier = Lambda("notifications")
        billing = Lambda("billing\nupdater")
        workflow = StepFunctions("Step Functions\n(saga / multi-step)")
        worker = ECS("long-running\nworker (ECS)")

    with Cluster("State"):
        ddb = Dynamodb("DynamoDB\n(read models + idempotency)")

    cw = Cloudwatch("CloudWatch\n(metrics + alarms)")

    # Producers publish events
    api >> ingest_fn >> Edge(label="PutEvents", color="navy") >> bus
    service >> Edge(label="PutEvents", color="navy") >> bus
    saas >> Edge(label="SaaS partner event source", style="dashed") >> bus

    # EventBridge rules route events
    bus >> Edge(label="rule: payment.*") >> notify_topic
    bus >> Edge(label="rule: order.placed") >> work_q
    bus >> Edge(label="rule: account.*") >> fifo_q
    bus >> Edge(label="rule: order.*") >> workflow
    bus >> Edge(label="archive", style="dotted") >> archive

    # Fan-out + buffer
    notify_topic >> notifier
    notify_topic >> billing
    work_q >> projector >> ddb
    fifo_q >> worker
    worker >> ddb

    # DLQ
    work_q >> Edge(label="poison", style="dashed", color="red") >> dlq
    fifo_q >> Edge(style="dashed", color="red") >> dlq

    # Observability
    bus >> Edge(style="dotted", color="gray") >> cw
    projector >> Edge(style="dotted", color="gray") >> cw
    workflow >> Edge(style="dotted", color="gray") >> cw
