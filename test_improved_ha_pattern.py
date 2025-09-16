#!/usr/bin/env python3
"""
Test the improved HA multi-region pattern with Azure App Service and Functions.
Demonstrates the enhanced layout with clear swimlanes and proper layering.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.arch_agent.schemas import Requirements, UserIntent, NetworkingDefaults
from scripts.arch_agent.catalog import ServiceCatalog
from scripts.arch_agent.layout import LayoutComposer
from scripts.arch_agent.render import DiagramRenderer

def test_ha_webapp_pattern():
    """Test the HA webapp pattern with clear layering."""
    
    # Define requirements for HA App Service + Functions deployment
    requirements = Requirements(
        regions=["East US 2", "West US 2"],
        ha_mode="active-active",
        edge_services=["front_door"],
        identity_services=["entra_id", "key_vault"],
        services=[
            # Compute services
            UserIntent(kind="web_app", name="Web Application"),
            UserIntent(kind="function_app", name="Background Functions"),
            
            # Network services
            UserIntent(kind="application_gateway", name="App Gateway"),
            UserIntent(kind="load_balancer", name="Load Balancer"),
            UserIntent(kind="vnet", name="Virtual Network"),
            
            # Storage services (as specifically requested)
            UserIntent(kind="storage_account", name="General Storage"),
            UserIntent(kind="queue_storage", name="Message Queue"),
            UserIntent(kind="table_storage", name="Table Data"),
            
            # Cache services (as specifically requested)
            UserIntent(kind="redis", name="Redis Cache"),
            
            # Monitoring
            UserIntent(kind="log_analytics", name="Log Analytics"),
            UserIntent(kind="application_insights", name="Application Insights"),
        ],
        networking=NetworkingDefaults(
            address_space="10.0.0.0/16",
            subnet_prefix="10.0.1.0/24"
        ),
        project_name="HA Web App Demo",
        environment="prod"
    )
    
    # Create the layout
    catalog = ServiceCatalog()
    composer = LayoutComposer(catalog)
    
    try:
        layout_graph = composer.compose_layout(requirements, pattern="ha-multiregion")
        
        # Render the diagram
        renderer = DiagramRenderer()
        output_path = "docs/diagrams/improved_ha_webapp"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        diagram_path = renderer.render(
            layout_graph, 
            output_path, 
            "Improved HA - App Service + Functions Multi-Region"
        )
        
        print(f"✅ Generated improved HA diagram: {diagram_path}")
        
        # Print layout summary
        print(f"\n📊 Layout Summary:")
        print(f"   - Nodes: {len(layout_graph.nodes)}")
        print(f"   - Edges: {len(layout_graph.edges)}")
        print(f"   - Clusters: {len(layout_graph.clusters)}")
        
        print(f"\n🏗️ Clusters created:")
        for cluster_name, cluster_def in layout_graph.clusters.items():
            print(f"   - {cluster_name}: {cluster_def.get('label', 'No label')}")
        
        print(f"\n🔗 Edge flows:")
        for edge in layout_graph.edges:
            if edge.label and (edge.label.isdigit() or "(" in edge.label):
                print(f"   - {edge.label}: {edge.source} -> {edge.target}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating diagram: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ha_webapp_pattern()
    sys.exit(0 if success else 1)