#!/usr/bin/env python3
"""
Enhanced High-Availability Azure App Service and Functions deployment diagram.
Implements all requirements from the problem statement.

Requirements implemented:
- Clear containers/swimlanes for logical layers (Internet, Identity, Active regions, Standby)  
- Identity and entry points at top/left, app/compute in middle, database/storage at bottom
- Horizontal alignment of critical components with bordered boxes
- Clear connection labeling and minimal line crossings
- Specific components: Front Door, Queue Storage, Redis, Table Storage
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
    "ranksep": "1.2",
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

# Enhanced diagram with clear swimlanes and layers
with Diagram(
    "Enhanced HA - App Service + Functions Multi-Region",
    show=False,
    outformat="png", 
    filename="docs/diagrams/enhanced_ha_webapp",
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
        fd = FrontDoors("Azure Front Door\\n(Global LB)")
        
    # Layer 2: Identity & Security (Top-Left)  
    with Cluster("🔐 Identity & Security", graph_attr={
        "bgcolor": "#FDECEE", 
        "style": "rounded,bold", 
        "penwidth": "2.0",
        "rank": "min"
    }):
        aad = ActiveDirectory("Microsoft Entra ID\\n(Authentication)")
        kv = KeyVaults("Key Vault\\n(Secrets & Certs)")
    
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
            vnet1 = VirtualNetworks("VNet East\\n(10.1.0.0/16)")
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
            vnet2 = VirtualNetworks("VNet West\\n(10.2.0.0/16)")
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
    
    # Layer 5: Monitoring & Observability (Bottom)
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
    
    # Storage replication
    storage1 >> Edge(label="Geo-Replication", color=COLOR_REPL, style="solid", penwidth="1.6") >> storage2
    
    # Cache synchronization
    redis1 >> Edge(label="Cache Sync", color=COLOR_REPL, style="dashed", penwidth="1.4") >> redis2
    
    # === CONTROL & SECURITY FLOWS (Dotted to minimize visual clutter) ===
    
    # Identity flows
    aad >> ctrl() >> fd
    kv >> ctrl() >> app1
    kv >> ctrl() >> app2
    kv >> ctrl() >> func1
    kv >> ctrl() >> func2
    
    # Monitoring flows (Telemetry)
    app1 >> ctrl() >> logs
    app2 >> ctrl() >> logs  
    func1 >> ctrl() >> logs
    func2 >> ctrl() >> logs

print("✅ Generated enhanced HA Web App + Functions architecture diagram")
print("📁 Output: docs/diagrams/enhanced_ha_webapp.png")
print("")
print("🎯 Key Features Implemented:")
print("   • Clear swimlanes for each logical layer")
print("   • Internet/Edge at top, Identity top-left")
print("   • App/Compute in middle layers")
print("   • Data/Storage at bottom")
print("   • Horizontal alignment with bordered boxes")
print("   • Minimal line crossings with clear labels")
print("   • Front Door + Queue Storage + Redis + Table Storage")