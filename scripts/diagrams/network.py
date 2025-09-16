from diagrams import Diagram, Cluster
from diagrams.generic.place import Datacenter as Bus
from diagrams.azure.network import ApplicationGateway, FrontDoors, Firewall, VirtualNetworks, DNSPrivateZones, LoadBalancers
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.security import SecurityCenter
from diagrams.azure.web import AppServices
from diagrams.azure.general import Managementgroups
from scripts.diagrams.style import GRAPH_ATTR, NODE_ATTR, FILL_NETWORK, step, primary, ctrl

# Network topology with LR flow and a central "Transit/Ingress" swimlane
with Diagram(
    "Azure - Network",
    show=False,
    outformat="png",
    filename="docs/diagrams/network",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    with Cluster("Ingress"):
        fd = FrontDoors("Azure Front Door")
        appgw = ApplicationGateway("App Gateway (WAF)")
        azfw = Firewall("Azure Firewall")

    with Cluster("Core Network", graph_attr={"bgcolor": FILL_NETWORK}):
        vnet = VirtualNetworks("Hub VNet")
        privdns = DNSPrivateZones("Private DNS")
        lb = LoadBalancers("Internal LB")
        bus = Bus("Network Bus")

    with Cluster("Identity / Control"):
        aad = ActiveDirectory("Microsoft Entra ID")
        mg = Managementgroups("Mgmt Group")
        mdef = SecurityCenter("Defender for Cloud")

    with Cluster("App Tier"):
        appsvc = AppServices("App Service")

    # Flow: Internet -> AFD -> AppGW -> Firewall -> VNet/LB -> App
    fd >> step("1") >> appgw >> step("2") >> azfw >> step("3") >> vnet >> step("4") >> lb >> step("5") >> appsvc

    # Bus to reduce crossings: shared services attach to the bus, then bus to DNS/App
    vnet >> primary() >> bus
    bus >> primary() >> privdns
    bus >> primary() >> appsvc

    # Control/management links (dotted)
    aad >> ctrl() >> fd
    mg >> ctrl() >> azfw
    mdef >> ctrl() >> azfw