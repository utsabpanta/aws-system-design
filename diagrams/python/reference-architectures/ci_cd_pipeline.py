"""Reference architecture: CI/CD pipeline.

Belongs to: docs/04-reference-architectures/ci-cd-pipeline.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS, Lambda
from diagrams.aws.devtools import (
    Codebuild,
    Codecommit,
    Codedeploy,
    Codepipeline,
)
from diagrams.aws.integration import Eventbridge, SimpleNotificationServiceSns as SNS
from diagrams.aws.management import Cloudformation, Cloudwatch
from diagrams.aws.security import IAM, SecretsManager
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2ContainerRegistry as ECR
from diagrams.generic.blank import Blank
from diagrams.onprem.client import Users
from diagrams.onprem.vcs import Github

OUT = os.environ.get("DIAGRAM_OUT_NAME", "ci_cd_pipeline")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "CI/CD pipeline (CodePipeline V2 + cross-account deploy)",
    filename=OUT,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    devs = Users("Developers")

    with Cluster("Source"):
        gh = Github("GitHub\n(CodeStar Connection)")
        cc = Codecommit("CodeCommit\n(AWS-native)")

    with Cluster("Tooling account"):
        pipeline = Codepipeline("CodePipeline V2")
        build = Codebuild("CodeBuild\n(build / test / scan)")
        artifacts = S3("artifacts bucket")
        ecr = ECR("ECR")
        approval = Blank("Manual approval\n(SNS notify)")
        secrets = SecretsManager("Secrets Manager")
        role = IAM("Cross-account\nrole")

    with Cluster("Staging account"):
        cfn_stg = Cloudformation("CloudFormation\n(staging stack)")
        deploy_stg = Codedeploy("CodeDeploy\n(blue/green)")
        ecs_stg = ECS("ECS / Lambda\n(staging)")
        alarm_stg = Cloudwatch("alarms\n(staging)")

    with Cluster("Production account"):
        cfn_prod = Cloudformation("CloudFormation\n(prod stack)")
        deploy_prod = Codedeploy("CodeDeploy\n(blue/green)")
        ecs_prod = ECS("ECS / Lambda\n(prod)")
        alarm_prod = Cloudwatch("alarms\n(prod)")

    with Cluster("Notifications"):
        events = Eventbridge("EventBridge\n(stage events)")
        sns = SNS("SNS")
        slack = Blank("Slack / Teams\n(external)")

    # Source -> pipeline
    devs >> Edge(label="git push") >> gh
    gh >> Edge(label="webhook") >> pipeline
    cc >> Edge(style="dotted") >> pipeline

    # Build
    pipeline >> build
    build >> Edge(label="image") >> ecr
    build >> Edge(label="artifact") >> artifacts
    build >> Edge(style="dotted", label="creds") >> secrets

    # Deploy to staging
    pipeline >> Edge(label="assume role", style="dashed") >> role
    role >> cfn_stg
    cfn_stg >> deploy_stg >> ecs_stg
    alarm_stg >> Edge(label="rollback trigger", style="dashed", color="darkred") >> deploy_stg

    # Approval -> prod
    pipeline >> approval >> Edge(label="approved") >> cfn_prod
    cfn_prod >> deploy_prod >> ecs_prod
    alarm_prod >> Edge(label="rollback trigger", style="dashed", color="darkred") >> deploy_prod

    # Notifications
    pipeline >> Edge(style="dotted") >> events
    deploy_stg >> Edge(style="dotted") >> events
    deploy_prod >> Edge(style="dotted") >> events
    events >> sns >> slack
