"""Reference architecture: hub-and-spoke multi-account network on AWS.

Belongs to: docs/04-reference-architectures/hub-and-spoke-network.md
"""
from __future__ import annotations

import os

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.management import ControlTower, Organizations
from diagrams.aws.network import (
    CloudFront,
    DirectConnect,
    NATGateway,
    NetworkFirewall,
    PrivateSubnet,
    PublicSubnet,
    Route53,
    SiteToSiteVpn,
    TransitGateway,
    VPC,
    VPCCustomerGateway,
)
from diagrams.aws.security import RAM
from diagrams.generic.blank import Blank

OUT = os.environ.get("DIAGRAM_OUT_NAME", "hub_and_spoke_network")

graph_attr = {"pad": "0.4", "fontname": "Helvetica", "fontsize": "11"}

with Diagram(
    "Hub-and-spoke multi-account network",
    filename=OUT,
    show=False,
    direction="TB",
    graph_attr=graph_attr,
):
    with Cluster("Organization"):
        org = Organizations("AWS Organizations")
        ct = ControlTower("Control Tower\n(landing zone)")
        ram = RAM("RAM\n(share TGW + subnets)")

    with Cluster("Network account (hub)"):
        tgw = TransitGateway("Transit Gateway\n(routing core)")
        with Cluster("Inspection VPC"):
            fw = NetworkFirewall("Network Firewall\n(stateful inspection)")
            insp_subnet = PrivateSubnet("inspection subnets")
        with Cluster("Egress VPC"):
            nat = NATGateway("centralized NAT\n(one per AZ)")
            pub = PublicSubnet("public subnets")
        with Cluster("Ingress / shared services VPC"):
            r53 = Route53("Route 53 Resolver\n(inbound + outbound endpoints)")
            cdn = CloudFront("CloudFront\n(global ingress)")

    with Cluster("On-prem"):
        cgw = VPCCustomerGateway("Customer Gateway")
        vpn = SiteToSiteVpn("Site-to-Site VPN")
        dx = DirectConnect("Direct Connect\n(dedicated / hosted)")
        onprem = Blank("Corporate DC")

    with Cluster("Workload accounts (spokes)"):
        prod_vpc = VPC("Prod VPC")
        stg_vpc = VPC("Staging VPC")
        sandbox_vpc = VPC("Sandbox VPC")

    # Governance fanout
    org >> ct
    org >> Edge(label="share", style="dashed") >> ram
    ram >> Edge(label="TGW attachments", style="dashed") >> tgw

    # Spoke attachments
    prod_vpc >> Edge(label="TGW attachment") >> tgw
    stg_vpc >> Edge(label="TGW attachment") >> tgw
    sandbox_vpc >> Edge(label="TGW attachment") >> tgw

    # Centralized egress: spoke -> TGW -> inspection -> egress -> Internet
    tgw >> Edge(label="route table:\nspoke->inspection",
                color="navy") >> insp_subnet >> fw
    fw >> Edge(label="allowed traffic", color="navy") >> nat >> pub
    pub >> Edge(label="Internet egress") >> Blank("Internet")

    # On-prem connectivity
    onprem >> cgw >> vpn >> tgw
    onprem >> dx >> tgw

    # Shared services
    tgw >> Edge(label="DNS / endpoints") >> r53
    cdn >> Edge(label="origin", style="dashed") >> prod_vpc
