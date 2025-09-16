#!/usr/bin/env python3
"""
Enhanced HA Azure App Service + Functions with Standby Region.
Demonstrates complete multi-region architecture with standby failover capability.

This version includes:
- Active-Active regions (East US 2, West US 2)  
- Standby region (Central US)
- Complete swimlane organization as requested
"""

from diagrams import Diagram, Cluster
from diagrams.azure.network import FrontDoors, ApplicationGateway, LoadBalancers, VirtualNetworks
from diagrams.azure.web import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.storage import StorageAccounts, QueuesStorage as QueueStorage, TableStorage
from diagrams.azure.database import CacheForRedis
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.security import KeyVaults
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams import Edge

# Enhanced styling for clear visual hierarchy
GRAPH_ATTR = {
    "pad": "0.5",
    "nodesep": "0.8",
    "ranksep": "1.3",
    "splines": "ortho",
    "rankdir": "TB",  # Top to bottom for layered architecture
    "fontname": "Inter",
    "fontsize": "11",
    "labelloc": "t",
    "concentrate": "true",  # Reduce edge crossings
    "compound": "true",     # Allow cluster-to-cluster edges
}

NODE_ATTR = {
    "fontsize": "9",
    "width": "2.0",
    "height": "1.4", 
    "fontname": "Inter",
    "shape": "box",
    "style": "rounded,filled",
    "margin": "0.1,0.05",
}

# Color palette for clear distinction
COLOR_PRIMARY = "#2E86C1"
COLOR_REPL    = "#7D3C98"
COLOR_CTRL    = "#566573"
COLOR_DATA    = "#FF8C00"
COLOR_STANDBY = "#FFB366"

def step(label: str, color: str = COLOR_PRIMARY, style: str = "solid", penwidth: str = "1.6"):
    return Edge(label=label, color=color, style=style, penwidth=penwidth, fontsize="9")

def primary():
    return Edge(color=COLOR_PRIMARY, penwidth="1.6")

def repl():
    return Edge(color=COLOR_REPL, style="dashed", penwidth="1.4")

def ctrl():
    return Edge(color=COLOR_CTRL, style="dotted", penwidth="1.2")

def data():
    return Edge(color=COLOR_DATA, penwidth="1.4")

def standby():
    return Edge(color=COLOR_STANDBY, style="dashed", penwidth="1.4")

# Complete HA diagram with standby region
with Diagram(
    "Complete HA - App Service + Functions (Active-Active + Standby)",
    show=False,
    outformat="png", 
    filename="docs/diagrams/complete_ha_webapp_standby",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    
    # Layer 1: Internet & Edge (Top)
    with Cluster("🌐 Internet & Edge Services", graph_attr={
        "bgcolor": "#E8F4F8", 
        "style": "rounded,bold", 
        "penwidth": "2.0",
        "rank": "min"
    }):
        fd = FrontDoors("Azure Front Door\\n(Global Load Balancer)")
        
    # Layer 2: Identity & Security (Top-Left)  
    with Cluster("🔐 Identity & Security", graph_attr={
        "bgcolor": "#FDECEE", 
        "style": "rounded,bold", 
        "penwidth": "2.0",
        "rank": "min"
    }):
        aad = ActiveDirectory("Microsoft Entra ID\\n(Global Authentication)")
        kv = KeyVaults("Key Vault\\n(Secrets & Certificates)")
    
    # Layer 3: Active Region 1 (Left side)
    with Cluster("🏗️ Active Region: East US 2", graph_attr={
        "bgcolor": "#F0F8F0", 
        "style": "rounded,bold", 
        "penwidth": "2.5",
        "rank": "same"
    }):
        
        # Network sublayer
        with Cluster("Network Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            appgw1 = ApplicationGateway("App Gateway\\n(WAF + SSL)")
            lb1 = LoadBalancers("Load Balancer\\n(Internal)")
        
        # Compute sublayer  
        with Cluster("App & Compute Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            app1 = AppServices("Web App\\n(East)")
            func1 = FunctionApps("Function App\\n(Background)")
        
        # Data sublayer
        with Cluster("Data & Storage Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            storage1 = StorageAccounts("Storage Account\\n(East)")
            queue1 = QueueStorage("Queue Storage\\n(Messages)")
            redis1 = CacheForRedis("Redis Cache\\n(Session)")
            table1 = TableStorage("Table Storage\\n(NoSQL Data)")
    
    # Layer 4: Active Region 2 (Right side)
    with Cluster("🏗️ Active Region: West US 2", graph_attr={
        "bgcolor": "#F8F0F8", 
        "style": "rounded,bold", 
        "penwidth": "2.5",
        "rank": "same"
    }):
        
        # Network sublayer
        with Cluster("Network Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            appgw2 = ApplicationGateway("App Gateway\\n(WAF + SSL)")
            lb2 = LoadBalancers("Load Balancer\\n(Internal)")
        
        # Compute sublayer
        with Cluster("App & Compute Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            app2 = AppServices("Web App\\n(West)")
            func2 = FunctionApps("Function App\\n(Background)")
        
        # Data sublayer
        with Cluster("Data & Storage Layer", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            storage2 = StorageAccounts("Storage Account\\n(West)")
            queue2 = QueueStorage("Queue Storage\\n(Messages)")
            redis2 = CacheForRedis("Redis Cache\\n(Session)")
            table2 = TableStorage("Table Storage\\n(NoSQL Data)")
    
    # Layer 5: Standby Region (Center bottom)
    with Cluster("🛡️ Standby Region: Central US", graph_attr={
        "bgcolor": "#FFF3E0", 
        "style": "rounded,bold", 
        "penwidth": "2.5",
        "rank": "max"
    }):
        
        # Compute sublayer (minimal for cost optimization)
        with Cluster("Standby Compute", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            app3 = AppServices("Web App\\n(Standby - Scaled Down)")
            func3 = FunctionApps("Function App\\n(Standby)")
        
        # Data sublayer (backup and disaster recovery)
        with Cluster("Standby Data", graph_attr={
            "bgcolor": "#FFFFFF", 
            "style": "dashed", 
            "penwidth": "1.5"
        }):
            storage3 = StorageAccounts("Storage Account\\n(DR Backup)")
            table3 = TableStorage("Table Storage\\n(DR Replica)")
    
    # Layer 6: Monitoring & Observability (Bottom)
    with Cluster("📊 Monitoring & Observability", graph_attr={
        "bgcolor": "#EBF5FB", 
        "style": "rounded,bold", 
        "penwidth": "2.0",
        "rank": "max"
    }):
        logs = LogAnalyticsWorkspaces("Log Analytics\\n(Centralized Logs)")
    
    # === PRIMARY FLOW PATHS (Numbered sequence) ===
    
    # Step 1: Internet traffic to Front Door
    fd >> step("1 (HTTPS)", COLOR_PRIMARY) >> appgw1
    fd >> step("1 (HTTPS)", COLOR_PRIMARY) >> appgw2
    
    # Step 2: App Gateway to Load Balancer  
    appgw1 >> step("2 (HTTP)", COLOR_PRIMARY) >> lb1
    appgw2 >> step("2 (HTTP)", COLOR_PRIMARY) >> lb2
    
    # Step 3: Load Balancer to Web Apps
    lb1 >> step("3 (HTTP)", COLOR_PRIMARY) >> app1
    lb2 >> step("3 (HTTP)", COLOR_PRIMARY) >> app2
    
    # Step 4: Web App to Function App integration
    app1 >> step("4 (API)", COLOR_PRIMARY) >> func1
    app2 >> step("4 (API)", COLOR_PRIMARY) >> func2
    
    # Step 5: Function App to Queue Storage (Async processing)
    func1 >> step("5 (Queue)", COLOR_DATA) >> queue1
    func2 >> step("5 (Queue)", COLOR_DATA) >> queue2
    
    # === DATA LAYER CONNECTIONS ===
    
    # Cache connections (Performance)
    app1 >> Edge(label="Cache", color="#87CEEB", style="dashed", penwidth="1.4") >> redis1
    app2 >> Edge(label="Cache", color="#87CEEB", style="dashed", penwidth="1.4") >> redis2
    
    # Table storage connections (Data persistence)
    app1 >> Edge(label="Data", color=COLOR_DATA, penwidth="1.4") >> table1
    app2 >> Edge(label="Data", color=COLOR_DATA, penwidth="1.4") >> table2
    
    # General storage connections (Files/Blobs)
    app1 >> Edge(label="Files", color=COLOR_DATA, penwidth="1.4") >> storage1
    app2 >> Edge(label="Files", color=COLOR_DATA, penwidth="1.4") >> storage2
    
    # === CROSS-REGION REPLICATION (Minimal crossings) ===
    
    # Active-Active storage replication
    storage1 >> Edge(label="Geo-Replication", color=COLOR_REPL, style="solid", penwidth="1.6") >> storage2
    
    # Cache synchronization
    redis1 >> Edge(label="Cache Sync", color=COLOR_REPL, style="dashed", penwidth="1.4") >> redis2
    
    # === STANDBY REGION CONNECTIONS (Disaster Recovery) ===
    
    # Standby failover connections (orange dashed to indicate DR)
    fd >> standby() >> app3  # Failover path
    
    # Data backup to standby region
    storage1 >> Edge(label="DR Backup", color=COLOR_STANDBY, style="dashed", penwidth="1.4") >> storage3
    storage2 >> Edge(label="DR Backup", color=COLOR_STANDBY, style="dashed", penwidth="1.4") >> storage3
    
    # Table storage backup
    table1 >> Edge(label="DR Replica", color=COLOR_STANDBY, style="dashed", penwidth="1.4") >> table3
    table2 >> Edge(label="DR Replica", color=COLOR_STANDBY, style="dashed", penwidth="1.4") >> table3
    
    # === CONTROL & SECURITY FLOWS (Dotted to minimize visual clutter) ===
    
    # Identity flows
    aad >> ctrl() >> fd
    kv >> ctrl() >> app1
    kv >> ctrl() >> app2
    kv >> ctrl() >> app3  # Standby also needs access to secrets
    kv >> ctrl() >> func1
    kv >> ctrl() >> func2
    kv >> ctrl() >> func3
    
    # Monitoring flows (Telemetry from all regions)
    app1 >> ctrl() >> logs
    app2 >> ctrl() >> logs  
    app3 >> ctrl() >> logs  # Monitor standby region too
    func1 >> ctrl() >> logs
    func2 >> ctrl() >> logs
    func3 >> ctrl() >> logs

print("✅ Generated complete HA Web App + Functions architecture with standby region")
print("📁 Output: docs/diagrams/complete_ha_webapp_standby.png")
print("")
print("🎯 Complete Architecture Features:")
print("   • Active-Active regions (East US 2, West US 2)")
print("   • Standby region (Central US) for disaster recovery")
print("   • Clear swimlanes for each logical layer")
print("   • Internet/Edge at top, Identity top-left")
print("   • App/Compute in middle, Data/Storage at bottom")
print("   • Horizontal alignment with bold bordered boxes")
print("   • Minimal line crossings with clear labels")
print("   • All requested components: Front Door + Queue + Redis + Table Storage")
print("   • DR backup and failover paths clearly marked")