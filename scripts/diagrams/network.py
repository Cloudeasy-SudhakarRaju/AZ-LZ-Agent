from diagrams import Diagram, Cluster
from diagrams.generic.place import Datacenter as Bus
from diagrams.azure.network import (ApplicationGateway, FrontDoors, Firewall, VirtualNetworks, 
                                   DNSPrivateZones, LoadBalancers, ExpressrouteCircuits, VirtualNetworkGateways)
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.security import SecurityCenter, KeyVaults, Sentinel
from diagrams.azure.web import AppServices
from diagrams.azure.general import Managementgroups
from diagrams.azure.storage import StorageAccounts, QueuesStorage, TableStorage
from diagrams.azure.database import CacheForRedis
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights
from style import (GRAPH_ATTR, NODE_ATTR, FILL_INTERNET_EDGE, FILL_IDENTITY_SECURITY, 
                   FILL_NETWORK, FILL_MONITORING, step, primary, ctrl, data_flow, monitoring)

# Enhanced network topology implementing all 16 requirements
with Diagram(
    "Azure - Enhanced Network Architecture",
    show=False,
    outformat="png",
    filename="docs/diagrams/network",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    # Internet Edge Zone (DMZ) - Requirement 1, 12
    with Cluster("🌐 Internet Edge (DMZ)", graph_attr={"bgcolor": FILL_INTERNET_EDGE}):
        fd = FrontDoors("Azure Front Door")
        
    # Identity & Security Zone - Requirement 1, 12
    with Cluster("🔐 Identity & Security", graph_attr={"bgcolor": FILL_IDENTITY_SECURITY}):
        aad = ActiveDirectory("Microsoft Entra ID")
        kv = KeyVaults("Key Vault")
        sentinel = Sentinel("Sentinel SIEM")
        mg = Managementgroups("Mgmt Group")

    # Active Region 1 (Primary) - Requirement 6, 13, 14
    with Cluster("🏢 East US 2 (Active-Primary) [PROD]", graph_attr={"bgcolor": "#EBF5FB"}):
        
        # Network Layer - Requirement 3, 16
        with Cluster("🌐 Network & Connectivity", graph_attr={"bgcolor": FILL_NETWORK}):
            appgw = ApplicationGateway("App Gateway (WAF)")
            azfw = Firewall("Azure Firewall")
            vnet = VirtualNetworks("Hub VNet")
            lb = LoadBalancers("Internal LB")
            er = ExpressrouteCircuits("ExpressRoute")
            vpn = VirtualNetworkGateways("VPN Gateway")
            privdns = DNSPrivateZones("Private DNS")
        
        # Application Layer - Requirement 3
        with Cluster("⚙️ Application & Compute", graph_attr={"bgcolor": "#FFFFFF"}):
            appsvc = AppServices("App Service")
        
        # Data Layer - Requirement 3, 4
        with Cluster("💾 Data & Storage", graph_attr={"bgcolor": "#F3E8FF"}):
            storage = StorageAccounts("Storage Account")
            queue = QueuesStorage("Queue Storage")
            table = TableStorage("Table Storage")
            redis = CacheForRedis("Redis Cache")

    # Active Region 2 (Secondary) - Requirement 6, 13
    with Cluster("🏢 West US 2 (Active-Secondary) [PROD]", graph_attr={"bgcolor": "#F0F8FF"}):
        
        # Network Layer
        with Cluster("🌐 Network & Connectivity", graph_attr={"bgcolor": FILL_NETWORK}):
            appgw2 = ApplicationGateway("App Gateway (WAF)")
            azfw2 = Firewall("Azure Firewall")
            vnet2 = VirtualNetworks("Hub VNet")
            lb2 = LoadBalancers("Internal LB")
        
        # Application Layer
        with Cluster("⚙️ Application & Compute", graph_attr={"bgcolor": "#FFFFFF"}):
            appsvc2 = AppServices("App Service")
        
        # Data Layer
        with Cluster("💾 Data & Storage", graph_attr={"bgcolor": "#F3E8FF"}):
            storage2 = StorageAccounts("Storage Account")
            redis2 = CacheForRedis("Redis Cache")

    # Monitoring & Observability - Requirement 11
    with Cluster("📊 Monitoring & Observability", graph_attr={"bgcolor": FILL_MONITORING}):
        logs = LogAnalyticsWorkspaces("Log Analytics")
        app_insights = ApplicationInsights("Application Insights")
        mdef = SecurityCenter("Defender for Cloud")

    # Primary Traffic Flow - Requirement 8 (Workflow Numbering)
    fd >> step("1") >> appgw >> step("2") >> azfw >> step("3") >> vnet >> step("4") >> lb >> step("5") >> appsvc
    
    # Data Flow - Requirement 8 
    appsvc >> step("6") >> redis
    appsvc >> step("7") >> queue  
    appsvc >> step("8") >> table
    appsvc >> step("9") >> storage

    # Security Connections - Requirement 14, 15
    aad >> ctrl("Auth") >> fd
    aad >> ctrl("Auth") >> appgw
    kv >> ctrl("Secrets") >> appsvc
    mg >> ctrl("Policy") >> azfw

    # Monitoring Connections - Requirement 11, 14
    appsvc >> monitoring("Logs") >> logs
    azfw >> monitoring("Security Events") >> sentinel
    fd >> monitoring("Metrics") >> app_insights
    
    # Network Core Connectivity - Requirement 16
    er >> primary("Private Peering") >> vnet
    vpn >> primary("Site-to-Site") >> vnet
    vnet >> primary("Peering") >> vnet2
    
    # Active-Active Replication - Requirement 13
    storage >> data_flow("Geo-Replication") >> storage2
    redis >> data_flow("Active Replication") >> redis2
    
    # Secondary Region Flow
    fd >> primary("Global Load Balance") >> appgw2
    appgw2 >> primary() >> azfw2 >> primary() >> vnet2 >> primary() >> lb2 >> primary() >> appsvc2

    # Cross-region monitoring
    appsvc2 >> monitoring("Logs") >> logs
    azfw2 >> monitoring("Security Events") >> sentinel