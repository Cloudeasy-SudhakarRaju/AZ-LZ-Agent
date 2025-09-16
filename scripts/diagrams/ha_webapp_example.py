#!/usr/bin/env python3
"""
High-Availability Azure App Service and Functions deployment diagram.
Demonstrates clear swimlanes, proper layering, and minimal line crossings.

Based on requirements:
- Clear containers/swimlanes for logical layers
- Identity and entry points at top/left
- App/compute in middle layers  
- Database/storage at bottom
- Horizontal alignment of critical components
- Bordered boxes for regions
- Clear connection labeling
"""

from diagrams import Diagram, Cluster
from diagrams.azure.network import FrontDoors, ApplicationGateway, LoadBalancers, VirtualNetworks
from diagrams.azure.web import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import CacheForRedis
from diagrams.azure.storage import StorageAccounts, QueuesStorage as QueueStorage, TableStorage
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.security import KeyVaults
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams import Edge

# Copy style definitions directly to avoid import issues
GRAPH_ATTR = {
    "pad": "0.5",
    "nodesep": "0.6",
    "ranksep": "0.8",
    "splines": "ortho",
    "rankdir": "LR",
    "fontname": "Inter",
    "fontsize": "11",
    "labelloc": "t",
}

NODE_ATTR = {
    "fontsize": "10",
    "width": "1.6",
    "height": "1.2",
    "fontname": "Inter",
}

# Palette
COLOR_PRIMARY = "#2E86C1"
COLOR_REPL    = "#7D3C98"
COLOR_CTRL    = "#566573"

def step(label: str, color: str = COLOR_PRIMARY, style: str = "solid", penwidth: str = "1.4"):
    return Edge(label=label, color=color, style=style, penwidth=penwidth)

def primary():
    return Edge(color=COLOR_PRIMARY, penwidth="1.4")

def repl():
    return Edge(color=COLOR_REPL, style="dashed", penwidth="1.2")

def ctrl():
    return Edge(color=COLOR_CTRL, style="dotted", penwidth="1.0")

# Enhanced graph attributes for clear layout
custom_graph_attr = GRAPH_ATTR.copy()
custom_graph_attr.update({
    "rankdir": "TB",  # Top-to-bottom for better layering
    "splines": "ortho",  # Orthogonal edges
    "nodesep": "1.2",
    "ranksep": "1.8",
    "compound": "true",
    "concentrate": "true",  # Merge parallel edges
    "newrank": "true",  # Better ranking algorithm
})

with Diagram(
    "Azure HA - App Service + Functions Multi-Region",
    show=False,
    outformat="png", 
    filename="docs/diagrams/ha_webapp_example",
    graph_attr=custom_graph_attr,
    node_attr=NODE_ATTR,
):
    # Internet/Edge Layer (Top)
    with Cluster("Internet & Edge Services", graph_attr={"bgcolor": "#E8F4F8", "style": "rounded"}):
        fd = FrontDoors("Azure Front Door")
        
    # Identity Layer (Top-Left)
    with Cluster("Identity & Security", graph_attr={"bgcolor": "#FDECEE", "style": "rounded"}):
        aad = ActiveDirectory("Microsoft Entra ID")
        kv = KeyVaults("Key Vault")
    
    # Active Region 1 (Left)
    with Cluster("Active Region: East US 2", graph_attr={"bgcolor": "#F0F8F0", "style": "rounded"}):
        
        # Network Layer
        with Cluster("Network", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            vnet1 = VirtualNetworks("VNet East")
            appgw1 = ApplicationGateway("App Gateway")
            lb1 = LoadBalancers("Load Balancer")
        
        # Compute Layer  
        with Cluster("Compute & Apps", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            app1 = AppServices("Web App")
            func1 = FunctionApps("Function App")
        
        # Data Layer
        with Cluster("Data & Storage", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            storage1 = StorageAccounts("Storage Account")
            queue1 = QueueStorage("Queue Storage")
            redis1 = CacheForRedis("Redis Cache")
            table1 = TableStorage("Table Storage")
    
    # Active Region 2 (Right)
    with Cluster("Active Region: West US 2", graph_attr={"bgcolor": "#F8F0F8", "style": "rounded"}):
        
        # Network Layer
        with Cluster("Network", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            vnet2 = VirtualNetworks("VNet West")
            appgw2 = ApplicationGateway("App Gateway")
            lb2 = LoadBalancers("Load Balancer")
        
        # Compute Layer
        with Cluster("Compute & Apps", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            app2 = AppServices("Web App")
            func2 = FunctionApps("Function App")
        
        # Data Layer
        with Cluster("Data & Storage", graph_attr={"bgcolor": "#FFFFFF", "style": "dashed"}):
            storage2 = StorageAccounts("Storage Account")
            queue2 = QueueStorage("Queue Storage")
            redis2 = CacheForRedis("Redis Cache")
            table2 = TableStorage("Table Storage")
    
    # Monitoring Layer (Bottom)
    with Cluster("Monitoring & Observability", graph_attr={"bgcolor": "#EBF5FB", "style": "rounded"}):
        logs = LogAnalyticsWorkspaces("Log Analytics")
    
    # Primary Flow: Internet -> Front Door -> App Gateways -> Apps
    fd >> step("1 (HTTPS)") >> appgw1
    fd >> step("1 (HTTPS)") >> appgw2
    
    # Regional Flows: App Gateway -> Load Balancer -> Apps
    appgw1 >> step("2 (HTTP)") >> lb1 >> step("3 (HTTP)") >> app1
    appgw2 >> step("2 (HTTP)") >> lb2 >> step("3 (HTTP)") >> app2
    
    # App to Functions communication
    app1 >> step("4 (API)") >> func1
    app2 >> step("4 (API)") >> func2
    
    # Function to Storage flows
    func1 >> step("5 (Queue)") >> queue1
    func2 >> step("5 (Queue)") >> queue2
    
    # App to Cache flows
    app1 >> step("Cache") >> redis1
    app2 >> step("Cache") >> redis2
    
    # App to Table Storage flows
    app1 >> step("Data") >> table1
    app2 >> step("Data") >> table2
    
    # Cross-region replication (minimal crossing)
    storage1 >> primary() >> storage2
    redis1 >> repl() >> redis2
    
    # Identity and Security flows (control plane)
    aad >> ctrl() >> fd
    kv >> ctrl() >> app1
    kv >> ctrl() >> app2
    
    # Monitoring flows (dotted to avoid clutter)
    app1 >> ctrl() >> logs
    app2 >> ctrl() >> logs
    func1 >> ctrl() >> logs
    func2 >> ctrl() >> logs

print("Generated HA Web App + Functions multi-region architecture diagram")