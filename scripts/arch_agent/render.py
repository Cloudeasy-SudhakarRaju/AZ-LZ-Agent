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
    PublicIpAddresses, NetworkSecurityGroupsClassic as NetworkSecurityGroups,
    FrontDoors, CDNProfiles
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
            "front_door": FrontDoors,
            "cdn": CDNProfiles,
            "public_ip": PublicIpAddresses,
            "nsg": NetworkSecurityGroups,
            "entra_id": ActiveDirectory,
            "key_vault": KeyVaults,
            "log_analytics": LogAnalyticsWorkspaces,
            "application_insights": ApplicationInsights,
        }
        
        # Track created nodes for edge connections
        self.node_instances = {}
    
    def render(self, graph: LayoutGraph, output_path: str, title: str = "Azure Architecture", format: str = "png") -> str:
        """
        Render a layout graph as a diagram in the specified format.
        
        Args:
            graph: Layout graph to render
            output_path: Output file path (without extension)
            title: Diagram title
            format: Output format ("png" or "svg")
            
        Returns:
            Path to the generated file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Validate format
        output_format = format.lower()
        if output_format not in ["png", "svg"]:
            output_format = "png"
        
        # Create enhanced graph attributes implementing architectural requirements 1-16
        custom_graph_attr = GRAPH_ATTR.copy()
        custom_graph_attr.update({
            # Requirements 1 & 7: Clear containers/swimlanes and region separation
            "rankdir": "TB",           # Top-to-bottom for clear logical layers
            "splines": "polyline",     # Polyline routing for minimal crossings (req 2)
            "nodesep": "3.5",          # Enhanced node separation for clarity (req 11)
            "ranksep": "4.0",          # Enhanced rank separation for visual hierarchy (req 3, 10)
            "compound": "true",        # Allow edges between clusters (req 1)
            "concentrate": "false",    # Prevent edge merging for clarity (req 2)
            "remincross": "true",      # Minimize edge crossings (req 2)
            "ordering": "out",         # Consistent edge ordering (req 12)
            "overlap": "false",        # Prevent node overlaps (req 11)
            "sep": "+40,40",          # Enhanced separation (req 11) 
            "esep": "+25,25",         # Enhanced edge separation (req 2)
            "bgcolor": "#ffffff",      # Clean background (req 11)
            "margin": "1.0,1.0",      # Better margins (req 11)
            # Requirements 12 & 13: Strong layout constraints and pattern templates
            "pack": "true",           # Efficient packing
            "packmode": "cluster",    # Cluster-based packing for logical grouping (req 8)
            "maxiter": "3000",        # Better layout convergence for complex diagrams
            "mclimit": "20.0",        # Enhanced memory cluster limit for complex diagrams
            # Advanced layout enhancements (requirement 2: minimal crossings)
            "clusterrank": "local",   # Local cluster ranking for better hierarchy (req 13)
            "newrank": "true",        # Use new ranking algorithm for better layout
            "mode": "hier",           # Hierarchical mode for clear layers (req 3)
            "ratio": "auto",          # Automatic aspect ratio optimization
            "smoothing": "spring",    # Spring model for better edge routing
            "levelsgap": "2.0",       # Gap between levels for clarity
            "searchsize": "30",       # Enhanced search for crossing reduction
            "mincross": "true"        # Enable minimal crossing algorithm
        })
        
        # Enhanced node attributes implementing requirements 6, 10, 11
        custom_node_attr = NODE_ATTR.copy()
        custom_node_attr.update({
            # Requirement 11: Enhanced readability
            "fontsize": "13",
            "width": "3.0",            # Larger width for service names
            "height": "2.0",           # Increased height for better visibility
            "fontname": "Segoe UI Bold",    # Professional bold font
            "shape": "box",
            "style": "rounded,filled,bold",
            "margin": "0.2,0.2",
            # Requirement 6: Horizontal alignment with borders
            "penwidth": "2.5",         # Enhanced borders
            "color": "#1565C0",        # Professional blue border color
            "fillcolor": "#E3F2FD",    # Light blue background color
            # Requirement 10: Visual hierarchy with color coding
            "gradientangle": "90",     # Vertical gradient effect
            "fontcolor": "#0D47A1"     # Professional dark blue text color
        })
        
        with Diagram(
            title,
            show=False,
            outformat=output_format,
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
        
        return f"{output_path}.{output_format}"
    
    def _create_clusters(self, graph: LayoutGraph) -> Dict[str, Any]:
        """
        Create diagram clusters implementing requirements 1, 6, 7, 8, 10.
        Requirements: Clear containers/swimlanes, horizontal alignment with borders,
        clear region separation, logical grouping, visual hierarchy.
        """
        cluster_contexts = {}
        
        # Sort clusters by dependency (parent clusters first)
        sorted_clusters = self._sort_clusters_by_dependency(graph.clusters)
        
        # Define cluster styling for visual hierarchy (requirement 10)
        cluster_styles = {
            "internet_edge": {
                "bgcolor": "#FFF5F5",     # Light red for edge/internet
                "pencolor": "#E53E3E", 
                "penwidth": "3",
                "style": "rounded,filled",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            },
            "identity_security": {
                "bgcolor": "#FFFAF0",     # Light orange for identity
                "pencolor": "#DD6B20",
                "penwidth": "3", 
                "style": "rounded,filled",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            },
            "active_region": {
                "bgcolor": "#F0FFF4",     # Light green for active regions
                "pencolor": "#38A169",
                "penwidth": "3",
                "style": "rounded,filled", 
                "fontcolor": "#1A202C",
                "fontsize": "14"
            },
            "standby_region": {
                "bgcolor": "#F7FAFC",     # Light gray for standby regions
                "pencolor": "#4A5568",
                "penwidth": "3",
                "style": "rounded,filled",
                "fontcolor": "#1A202C", 
                "fontsize": "14"
            },
            "monitoring": {
                "bgcolor": "#EBF4FF",     # Light blue for monitoring
                "pencolor": "#3182CE",
                "penwidth": "3",
                "style": "rounded,filled",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            },
            "default": {
                "bgcolor": "#F8F9FA",     # Light gray for other clusters
                "pencolor": "#6B73FF",
                "penwidth": "2",
                "style": "rounded,filled",
                "fontcolor": "#1A202C",
                "fontsize": "13"
            }
        }
        
        for cluster_name, cluster_def in sorted_clusters:
            # Skip sub-clusters for now - handle them in a second pass
            if cluster_def.get("parent"):
                continue
            
            # Determine cluster style based on logical grouping (requirement 8)
            style_key = "default"
            if "edge" in cluster_name.lower() or "internet" in cluster_name.lower():
                style_key = "internet_edge"
            elif "identity" in cluster_name.lower() or "security" in cluster_name.lower():
                style_key = "identity_security"
            elif "active" in cluster_name.lower() and "region" in cluster_name.lower():
                style_key = "active_region"
            elif "standby" in cluster_name.lower() and "region" in cluster_name.lower():
                style_key = "standby_region"
            elif "monitor" in cluster_name.lower():
                style_key = "monitoring"
            
            # Apply enhanced styling (requirements 1, 6, 7, 10)
            attrs = cluster_styles[style_key].copy()
            attrs["label"] = cluster_def.get("label", cluster_name)
            
            # Override with custom attributes if provided
            attrs.update(cluster_def.get("graph_attr", {}))
            
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
        """Get edge attributes implementing requirements 4, 9, 14, 15 for enhanced connectivity visualization."""
        attrs = {}
        
        # Base attributes for all edges
        if edge.label:
            attrs["label"] = edge.label
            attrs["fontsize"] = "11"
            attrs["fontname"] = "Segoe UI"
            attrs["labeldistance"] = "1.2"
            attrs["labelangle"] = "0"
        
        if edge.color:
            attrs["color"] = edge.color
        else:
            attrs["color"] = "#2D3748"  # Professional default color
        
        # Requirement 14: Line type distinctions for different purposes
        if edge.style:
            attrs["style"] = edge.style
        else:
            attrs["style"] = "solid"
        
        # Requirement 4 & 9: Clear connection labeling with numbered workflow steps
        if edge.label and any(word in edge.label.lower() for word in ["1.", "2.", "3.", "4.", "5.", "step", "traffic", "https", "request", "response"]):
            # Primary workflow edges - requirement 9: numbered traffic flow
            attrs.update({
                "penwidth": "4.5",
                "fontsize": "14",
                "fontcolor": "#0D47A1",
                "fontweight": "bold",
                "arrowsize": "1.8",
                "arrowhead": "normal",
                "color": "#1976D2",  # Strong blue for main flow
                "style": "solid",
                "minlen": "2",        # Minimum edge length for clarity
                "weight": "10"        # Highest weight for workflow edges
            })
        elif edge.style == "dashed":
            # Requirement 14: Dashed lines for async/cache patterns
            attrs.update({
                "penwidth": "3.0",
                "fontsize": "11",
                "fontcolor": "#C53030",
                "arrowsize": "1.4",
                "arrowhead": "vee",
                "color": "#E53E3E",  # Red for async patterns
                "style": "dashed",
                "minlen": "1.5",
                "weight": "5"
            })
        elif edge.style == "dotted":
            # Requirement 14: Dotted lines for monitoring and control
            attrs.update({
                "penwidth": "2.5",
                "fontsize": "10",
                "fontcolor": "#4A5568",
                "arrowsize": "1.2",
                "arrowhead": "diamond",
                "color": "#718096",  # Gray for monitoring
                "style": "dotted",
                "minlen": "1",
                "weight": "2"
            })
        elif any(word in (edge.label or "").lower() for word in ["auth", "secret", "cert", "identity", "key", "security"]):
            # Security connections - special styling for security flows
            attrs.update({
                "penwidth": "3.5",
                "fontsize": "11",
                "fontcolor": "#744210",
                "arrowsize": "1.5",
                "arrowhead": "box",
                "color": "#D69E2E",  # Gold for security
                "style": "solid",
                "minlen": "1.5",
                "weight": "7"  # High weight for security
            })
        elif any(word in (edge.label or "").lower() for word in ["data", "query", "read", "write", "backup", "sync"]):
            # Data flow connections - requirement 15: directional clarity for data
            attrs.update({
                "penwidth": "3.0",
                "fontsize": "10",
                "fontcolor": "#2D5016",
                "arrowsize": "1.3",
                "arrowhead": "normal",
                "color": "#38A169",  # Green for data flow
                "style": "solid",
                "minlen": "1.5",
                "weight": "5"  # Higher weight for data flow
            })
        else:
            # Standard service connections - requirement 15: directional clarity
            attrs.update({
                "penwidth": "2.5",
                "fontsize": "10",
                "fontcolor": "#2D3748",
                "arrowsize": "1.1",
                "arrowhead": "normal",
                "color": "#4A5568",  # Neutral gray for standard connections
                "style": "solid",
                "weight": "3"  # Standard weight
            })
        
        # Requirement 2 & 12: Add constraints to minimize edge crossings
        attrs["constraint"] = "true"
        if "weight" not in attrs:
            attrs["weight"] = "1"
        
        # Requirement 15: Enhance directional clarity
        if "bidirectional" in (edge.label or "").lower():
            attrs["dir"] = "both"
            attrs["arrowtail"] = attrs["arrowhead"]
        else:
            attrs["dir"] = "forward"
        
        return attrs


class BatchRenderer:
    """
    Utility class for rendering multiple diagrams with consistent styling.
    """
    
    def __init__(self):
        self.renderer = DiagramRenderer()
    
    def render_multiple(self, graphs: Dict[str, LayoutGraph], output_dir: str, title_prefix: str = "Azure", format: str = "png") -> Dict[str, str]:
        """
        Render multiple layout graphs.
        
        Args:
            graphs: Dictionary mapping names to layout graphs
            output_dir: Output directory
            title_prefix: Prefix for diagram titles
            format: Output format ("png" or "svg")
            
        Returns:
            Dictionary mapping names to output file paths
        """
        output_files = {}
        
        for name, graph in graphs.items():
            output_path = os.path.join(output_dir, name)
            title = f"{title_prefix} - {name.replace('_', ' ').title()}"
            
            try:
                file_path = self.renderer.render(graph, output_path, title, format)
                output_files[name] = file_path
            except Exception as e:
                print(f"Error rendering {name}: {e}")
                output_files[name] = None
        
        return output_files