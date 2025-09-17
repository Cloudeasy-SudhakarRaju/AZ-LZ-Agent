"""
Legend and notation guide for Azure architecture diagrams.
Implements requirement 10: Legend & notation guide explaining line types, icons, and cluster meanings.
"""
from diagrams import Diagram, Cluster, Node
from diagrams.azure.general import Helpsupport
from style import (GRAPH_ATTR, NODE_ATTR, step, primary, ctrl, data_flow, 
                   monitoring, dr_connection, secondary)

# Create legend diagram
with Diagram(
    "Azure Architecture - Legend & Notation Guide",
    show=False,
    outformat="png", 
    filename="docs/diagrams/legend",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    
    # Connection Types Legend
    with Cluster("🔗 Connection Types & Workflow", graph_attr={"bgcolor": "#F8F9FA"}):
        start = Node("Start", shape="ellipse", style="filled", fillcolor="#E3F2FD")
        step1 = Node("Service A", shape="box", style="filled", fillcolor="#FFFFFF")
        step2 = Node("Service B", shape="box", style="filled", fillcolor="#FFFFFF") 
        step3 = Node("Service C", shape="box", style="filled", fillcolor="#FFFFFF")
        
        # Workflow numbering examples
        start >> step("1") >> step1 >> step("2") >> step2 >> step("3") >> step3
        
        # Different connection types
        step1 >> primary("Primary Traffic") >> step2
        step1 >> data_flow("Data Flow") >> step3
        step1 >> ctrl("Control/Auth") >> step3
        step1 >> monitoring("Monitoring") >> step3
        step1 >> dr_connection("DR/Backup") >> step3
        step1 >> secondary("Async/Queue") >> step3

    # Zone Types Legend  
    with Cluster("🏢 Security Zones & Regions", graph_attr={"bgcolor": "#F8F9FA"}):
        
        with Cluster("🌐 Internet Edge (DMZ)", graph_attr={"bgcolor": "#FFF5F5"}):
            edge_example = Node("Front Door", shape="box")
            
        with Cluster("🔐 Identity & Security", graph_attr={"bgcolor": "#FFFAF0"}):
            identity_example = Node("Entra ID", shape="box")
            
        with Cluster("🏢 Active Region [PROD]", graph_attr={"bgcolor": "#EBF5FB"}):
            region_example = Node("App Service", shape="box")
            
        with Cluster("🔄 Standby Region [DR]", graph_attr={"bgcolor": "#F8F9FA", "style": "dashed"}):
            dr_example = Node("DR Storage", shape="box")
            
        with Cluster("📊 Monitoring & Observability", graph_attr={"bgcolor": "#FDF4E3"}):
            monitor_example = Node("Log Analytics", shape="box")

    # Service Layer Legend
    with Cluster("📚 Service Layer Hierarchy", graph_attr={"bgcolor": "#F8F9FA"}):
        
        with Cluster("Layer 1: Network & Connectivity", graph_attr={"bgcolor": "#E9F7EF"}):
            network_node = Node("VNet, Firewall, Gateway", shape="box")
            
        with Cluster("Layer 2: Application & Compute", graph_attr={"bgcolor": "#FFFFFF"}):
            compute_node = Node("Web Apps, VMs, Functions", shape="box")
            
        with Cluster("Layer 3: Data & Storage", graph_attr={"bgcolor": "#F3E8FF"}):
            data_node = Node("SQL DB, Storage, Cache", shape="box")

    # Annotation Legend
    with Cluster("📝 Annotations & Labels", graph_attr={"bgcolor": "#F8F9FA"}):
        
        with Cluster("HA/DR Annotations", graph_attr={"bgcolor": "#FFFFFF"}):
            ha_active = Node("(Active-Active)", shape="note", style="filled", fillcolor="#D4EDDA")
            ha_passive = Node("(Active-Passive)", shape="note", style="filled", fillcolor="#F8D7DA")
            
        with Cluster("Environment Labels", graph_attr={"bgcolor": "#FFFFFF"}):
            env_prod = Node("[PROD]", shape="note", style="filled", fillcolor="#D4EDDA")
            env_dev = Node("[DEV]", shape="note", style="filled", fillcolor="#D1ECF1")
            env_dr = Node("[DR]", shape="note", style="filled", fillcolor="#F8D7DA")

    # Icon Consistency Note
    with Cluster("🎨 Icon Standards", graph_attr={"bgcolor": "#F8F9FA"}):
        icon_note = Node("All icons follow Azure\nofficial iconography\nfor consistency", 
                        shape="note", style="filled", fillcolor="#FFF3CD")