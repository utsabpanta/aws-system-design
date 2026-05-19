"""High-level architecture for the payment-system design.

Belongs to: docs/03-interview-designs/payment-system.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import EMR, Glue
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Aurora, Dynamodb
from diagrams.aws.integration import Eventbridge, StepFunctions
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.aws.security import KMS, SecretsManager
from diagrams.aws.storage import S3
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Users

OUT = os.environ.get("DIAGRAM_OUT_NAME", "payment_system")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Payment system",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    customer = Users("Customer\n(tokenizes card via processor JS)")

    with Cluster("API"):
        api = APIGateway("payments API")
        webhook = APIGateway("webhooks")
        pay_fn = Lambda("payment handler")
        wh_fn = Lambda("webhook handler\n(signature verify)")

    with Cluster("Orchestration"):
        sm = StepFunctions("payment state machine\n(auth - capture - settle)")
        bus = Eventbridge("internal events")

    with Cluster("Storage (source of truth)"):
        aurora = Aurora("Aurora PostgreSQL\n(payment_intents, ledger,\naudit_log)")
        idem = Dynamodb("idempotency cache")

    with Cluster("External"):
        processor = Blank("Stripe / Adyen\n(processor)")
        bank = Blank("Bank / network")

    with Cluster("Reconciliation"):
        reports = S3("processor reports\n+ bank statements")
        glue = Glue("Glue / EMR\n(nightly recon)")
        recon = Aurora("reconciliation")

    secrets = SecretsManager("processor API keys")
    kms = KMS("KMS")
    cw = Cloudwatch("CloudWatch")

    # Charge flow
    customer >> Edge(label="POST /payment-intents", color="navy") >> api >> pay_fn
    pay_fn >> Edge(label="dedup", style="dotted") >> idem
    pay_fn >> Edge(label="create intent", color="navy") >> aurora
    pay_fn >> sm
    sm >> Edge(label="auth / capture", color="navy") >> processor
    processor >> Edge(label="auth response", color="darkgreen") >> sm
    sm >> Edge(label="ledger entries\n(double-entry)") >> aurora
    sm >> bus

    # Webhook (async events)
    processor >> Edge(label="webhook", style="dashed") >> webhook >> wh_fn
    wh_fn >> sm
    wh_fn >> aurora

    # Settlement to bank
    processor >> Edge(label="settle", style="dotted") >> bank

    # Reconciliation
    processor >> Edge(label="daily report", style="dotted") >> reports
    bank >> Edge(label="statements", style="dotted") >> reports
    reports >> glue >> recon
    glue >> Edge(label="discrepancies", style="dashed", color="darkred") >> bus

    # Security
    secrets >> Edge(style="dotted", color="gray") >> pay_fn
    secrets >> Edge(style="dotted", color="gray") >> wh_fn
    kms >> Edge(style="dotted", color="gray") >> aurora

    pay_fn >> Edge(style="dotted", color="gray") >> cw
    sm >> Edge(style="dotted", color="gray") >> cw
