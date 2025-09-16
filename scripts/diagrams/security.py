from diagrams import Diagram, Cluster
from diagrams.azure.security import SecurityCenter, KeyVaults as KeyVault, Sentinel
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.network import Firewall, ApplicationGateway
from diagrams.azure.monitor import Monitor
from scripts.diagrams.style import GRAPH_ATTR, NODE_ATTR, FILL_SECURITY, step, ctrl, primary

with Diagram("Azure - Security", show=False, outformat="png", filename="docs/diagrams/security", graph_attr=GRAPH_ATTR, node_attr=NODE_ATTR):
    with Cluster("Identity & Access", graph_attr={"bgcolor": FILL_SECURITY}):
        aad = ActiveDirectory("Microsoft Entra ID")
        kv = KeyVault("Key Vault")

    with Cluster("Perimeter"):
        waf = ApplicationGateway("WAF (App GW)")
        afw = Firewall("Azure Firewall")

    with Cluster("Posture / SIEM"):
        asc = SecurityCenter("Defender for Cloud")
        sent = Sentinel("Microsoft Sentinel")
        mon = Monitor("Azure Monitor")

    # Control flows with labels to show onboarding steps
    aad >> step("1 (auth)") >> waf
    waf >> step("2 (rules)") >> afw
    asc >> ctrl() >> afw
    sent >> ctrl() >> afw
    kv >> primary() >> waf
    mon >> ctrl() >> sent