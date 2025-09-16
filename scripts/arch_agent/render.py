"""
Render engine that converts layout graphs into diagrams using the diagrams library.
Applies shared styling and proper Azure service representations.
"""
import os
from typing import Dict, Any, Optional, List
from diagrams import Diagram, Cluster, Node
from diagrams.azure.compute import VM, AppServices, FunctionApps
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.database import SQLDatabases, CacheForRedis
from diagrams.azure.network import (
    VirtualNetworks, LoadBalancers, ApplicationGateway, 
    PublicIpAddresses, NetworkSecurityGroupsClassic as NetworkSecurityGroups
)
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.security import KeyVaults
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights
from diagrams.azure.network import FrontDoors, CDNProfiles
from diagrams import Edge

from .schemas import LayoutGraph, LayoutNode, LayoutEdge
from ..diagrams.style import GRAPH_ATTR, NODE_ATTR


class DiagramRenderer:
    """
    Renders layout graphs as PNG diagrams using the diagrams library.
    Maintains consistency with existing diagram styling.
    """
    
    def __init__(self):
        # Map service types to diagrams classes
        self.service_classes = {
            "vm": VM,
            "web_app": AppServices,
            "function_app": FunctionApps,
            "storage_account": StorageAccounts,
            "queue_storage": StorageAccounts,  # Use StorageAccounts for queue storage
            "table_storage": StorageAccounts,  # Use StorageAccounts for table storage
            "sql_database": SQLDatabases,
            "redis": CacheForRedis,
            "vnet": VirtualNetworks,
            "load_balancer": LoadBalancers,
            "application_gateway": ApplicationGateway,
            "public_ip": PublicIpAddresses,
            "nsg": NetworkSecurityGroups,
            "entra_id": ActiveDirectory,
            "key_vault": KeyVaults,
            "log_analytics": LogAnalyticsWorkspaces,
            "application_insights": ApplicationInsights,
            "front_door": FrontDoors,
            "cdn": CDNProfiles,
        }
        
        # Track created nodes for edge connections
        self.node_instances = {}
    
    def render(self, graph: LayoutGraph, output_path: str, title: str = "Azure Architecture") -> str:
        """
        Render a layout graph as a PNG diagram.
        
        Args:
            graph: Layout graph to render
            output_path: Output file path (without extension)
            title: Diagram title
            
        Returns:
            Path to the generated PNG file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create enhanced graph attributes for better layout (requirement 12)
        custom_graph_attr = GRAPH_ATTR.copy()
        custom_graph_attr.update({
            "rankdir": "LR",           # Left-to-right flow (requirement 3)
            "splines": "polyline",     # Use polyline instead of ortho for edge labels
            "nodesep": "1.5",          # Increased node separation for clarity
            "ranksep": "2.5",          # Increased rank separation for visual hierarchy
            "compound": "true",        # Allow edges between clusters
            "concentrate": "false",    # Prevent edge merging for clarity
            "remincross": "true",      # Minimize edge crossings (requirement 2)
            "ordering": "out",         # Consistent edge ordering
            "overlap": "false",        # Prevent node overlaps
            "sep": "+25,25",           # Minimum separation
            "esep": "+15,15",          # Edge separation
        })
        
        # Enhanced node attributes for better visibility (requirement 6, 11)
        custom_node_attr = NODE_ATTR.copy()
        custom_node_attr.update({
            "fontsize": "11",
            "width": "2.2",            # Larger width for long service names
            "height": "1.5",           # Increased height
            "fontname": "Inter",
            "shape": "box",
            "style": "rounded,filled",
            "margin": "0.1,0.1"
        })
        
        with Diagram(
            title,
            show=False,
            outformat="png",
            filename=output_path,
            graph_attr=custom_graph_attr,
            node_attr=custom_node_attr,
        ):
            # Create clusters first
            cluster_contexts = self._create_clusters(graph)
            
            # Create nodes within their clusters
            self._create_nodes(graph, cluster_contexts)
            
            # Create edges
            self._create_edges(graph)
        
        return f"{output_path}.png"
    
    def _create_clusters(self, graph: LayoutGraph) -> Dict[str, Any]:
        """
        Create diagram clusters from the layout graph.
        Returns a dictionary of cluster names to their context managers.
        """
        cluster_contexts = {}
        
        # Sort clusters by dependency (parent clusters first)
        sorted_clusters = self._sort_clusters_by_dependency(graph.clusters)
        
        for cluster_name, cluster_def in sorted_clusters:
            # Skip sub-clusters for now - handle them in a second pass
            if cluster_def.get("parent"):
                continue
                
            attrs = {
                "label": cluster_def.get("label", cluster_name),
                "bgcolor": cluster_def.get("bgcolor", "#FFFFFF"),
                "style": cluster_def.get("style", "solid"),
            }
            
            # Create the cluster context
            cluster_contexts[cluster_name] = Cluster(
                cluster_def.get("label", cluster_name),
                graph_attr=attrs
            )
        
        return cluster_contexts
    
    def _sort_clusters_by_dependency(self, clusters: Dict[str, Dict[str, Any]]) -> List[tuple]:
        """Sort clusters so parent clusters come before child clusters."""
        sorted_items = []
        
        # First pass: clusters without parents
        for name, definition in clusters.items():
            if not definition.get("parent"):
                sorted_items.append((name, definition))
        
        # Second pass: clusters with parents
        for name, definition in clusters.items():
            if definition.get("parent"):
                sorted_items.append((name, definition))
        
        return sorted_items
    
    def _create_nodes(self, graph: LayoutGraph, cluster_contexts: Dict[str, Any]) -> None:
        """Create diagram nodes within their appropriate clusters."""
        # Group nodes by cluster
        cluster_nodes = {}
        unclustered_nodes = []
        
        for node in graph.nodes:
            if node.cluster and node.cluster in cluster_contexts:
                if node.cluster not in cluster_nodes:
                    cluster_nodes[node.cluster] = []
                cluster_nodes[node.cluster].append(node)
            else:
                unclustered_nodes.append(node)
        
        # Create nodes within clusters
        for cluster_name, cluster_context in cluster_contexts.items():
            with cluster_context:
                if cluster_name in cluster_nodes:
                    for node in cluster_nodes[cluster_name]:
                        self._create_single_node(node)
        
        # Create unclustered nodes
        for node in unclustered_nodes:
            self._create_single_node(node)
    
    def _create_single_node(self, node: LayoutNode) -> None:
        """Create a single diagram node."""
        service_class = self.service_classes.get(node.service_type)
        
        if service_class:
            # Create the diagram node
            instance = service_class(node.name)
            self.node_instances[node.id] = instance
        else:
            # Fallback for unknown service types - create a generic node
            # This is a simple fallback - in production you might want a more sophisticated approach
            from diagrams.generic.compute import Rack
            instance = Rack(node.name)
            self.node_instances[node.id] = instance
    
    def _create_edges(self, graph: LayoutGraph) -> None:
        """Create diagram edges between nodes."""
        for edge in graph.edges:
            source_node = self.node_instances.get(edge.source)
            target_node = self.node_instances.get(edge.target)
            
            if source_node and target_node:
                edge_attrs = self._get_edge_attributes(edge)
                
                # Create the edge
                source_node >> Edge(**edge_attrs) >> target_node
    
    def _get_edge_attributes(self, edge: LayoutEdge) -> Dict[str, Any]:
        """Get edge attributes for diagram rendering with enhanced styling (requirement 4, 14)."""
        attrs = {}
        
        if edge.label:
            attrs["label"] = edge.label
            attrs["fontsize"] = "10"
            attrs["fontname"] = "Inter"
        
        if edge.color:
            attrs["color"] = edge.color
        else:
            attrs["color"] = "#2E86C1"  # Default blue
        
        if edge.style:
            attrs["style"] = edge.style
        else:
            attrs["style"] = "solid"
        
        # Enhanced styling based on connection type and requirements
        if edge.label and any(word in edge.label for word in ["1.", "2.", "3.", "Traffic", "HTTPS"]):
            # Primary workflow edges (requirement 4, 9)
            attrs.update({
                "penwidth": "3.0",
                "fontsize": "12",
                "fontcolor": edge.color or "#1976D2",
                "arrowsize": "1.2",
                "arrowhead": "normal"
            })
        elif edge.style == "dashed":
            # Cache, replication, and async patterns (requirement 14)
            attrs.update({
                "penwidth": "2.0",
                "fontsize": "9",
                "fontcolor": edge.color or "#FF6B35",
                "arrowsize": "1.0",
                "arrowhead": "vee"
            })
        elif edge.style == "dotted":
            # Monitoring and control connections (requirement 14)
            attrs.update({
                "penwidth": "1.5",
                "fontsize": "8",
                "fontcolor": edge.color or "#607D8B",
                "arrowsize": "0.8",
                "arrowhead": "diamond"
            })
        elif any(word in edge.label for word in ["Auth", "Secret", "Cert"]) if edge.label else False:
            # Security connections (requirement 15)
            attrs.update({
                "penwidth": "2.0",
                "fontsize": "9",
                "fontcolor": edge.color or "#795548",
                "arrowsize": "1.0",
                "arrowhead": "box"
            })
        else:
            # Standard data flow edges (requirement 15)
            attrs.update({
                "penwidth": "1.8",
                "fontsize": "9",
                "fontcolor": edge.color or "#4CAF50",
                "arrowsize": "0.9",
                "arrowhead": "normal"
            })
        
        # Add constraint to minimize edge crossings (requirement 2, 12)
        attrs["constraint"] = "true"
        
        return attrs


class BatchRenderer:
    """
    Utility class for rendering multiple diagrams with consistent styling.
    """
    
    def __init__(self):
        self.renderer = DiagramRenderer()
    
    def render_multiple(self, graphs: Dict[str, LayoutGraph], output_dir: str, title_prefix: str = "Azure") -> Dict[str, str]:
        """
        Render multiple layout graphs.
        
        Args:
            graphs: Dictionary mapping names to layout graphs
            output_dir: Output directory
            title_prefix: Prefix for diagram titles
            
        Returns:
            Dictionary mapping names to output file paths
        """
        output_files = {}
        
        for name, graph in graphs.items():
            output_path = os.path.join(output_dir, name)
            title = f"{title_prefix} - {name.replace('_', ' ').title()}"
            
            try:
                file_path = self.renderer.render(graph, output_path, title)
                output_files[name] = file_path
            except Exception as e:
                print(f"Error rendering {name}: {e}")
                output_files[name] = None
        
        return output_files