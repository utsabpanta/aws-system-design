"""High-level architecture for the notification system design.

Belongs to: docs/03-interview-designs/notification-system.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import Athena, KinesisDataFirehose
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.engagement import Pinpoint, SimpleEmailServiceSes as SES
from diagrams.aws.integration import Eventbridge, SimpleNotificationServiceSns as SNS, SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "notification_system")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Notification system",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    callers = Users("Caller services")

    with Cluster("Ingest"):
        events = Eventbridge("EventBridge\n(send events)")
        send_api = APIGateway("Send API")

    with Cluster("Dispatcher"):
        dispatcher = Lambda("dispatcher\n(prefs + dedup + template)")
        prefs = Dynamodb("preferences")
        templates = Dynamodb("templates")
        idem = Dynamodb("idempotency")

    with Cluster("Per-channel queues"):
        q_email = SQS("email q")
        q_sms = SQS("sms q")
        q_push = SQS("push q")
        q_inapp = SQS("in-app q")

    with Cluster("Channel workers + providers"):
        w_email = Lambda("email worker")
        w_sms = Lambda("sms / push worker")
        w_inapp = Lambda("in-app worker")
        ses = SES("SES")
        sns = SNS("SNS")
        pinpoint = Pinpoint("Pinpoint")
        ws_api = APIGateway("WS API\n(in-app)")

    with Cluster("Delivery state + analytics"):
        notif = Dynamodb("notifications\n(status)")
        firehose = KinesisDataFirehose("Firehose")
        bucket = S3("event lake")
        athena = Athena("Athena")

    cw = Cloudwatch("CloudWatch")

    # Ingest
    callers >> Edge(label="event") >> events >> dispatcher
    callers >> Edge(label="POST /notifications") >> send_api >> dispatcher

    # Dispatcher lookups
    dispatcher >> Edge(style="dotted") >> prefs
    dispatcher >> Edge(style="dotted") >> templates
    dispatcher >> Edge(style="dotted", label="dedup") >> idem

    # Fanout to per-channel queues
    dispatcher >> q_email >> w_email >> ses
    dispatcher >> q_sms >> w_sms >> sns
    dispatcher >> q_push >> w_sms >> pinpoint
    dispatcher >> q_inapp >> w_inapp >> ws_api

    # Provider callbacks + status
    ses >> Edge(label="bounce / complaint", style="dashed", color="darkred") >> events
    sns >> Edge(style="dashed", color="darkred") >> events
    events >> Edge(label="status update", color="darkgreen") >> notif
    events >> Edge(label="event archive", style="dotted") >> firehose >> bucket >> athena

    dispatcher >> Edge(style="dotted", color="gray") >> cw
    w_email >> Edge(style="dotted", color="gray") >> cw
