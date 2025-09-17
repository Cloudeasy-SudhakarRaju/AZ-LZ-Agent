"""
Layout composer that builds logical directed graphs from user intents.
Assigns nodes to clusters and ranks based on the chosen pattern.
"""
from typing import List, Dict, Any, Optional
from .schemas import Requirements, UserIntent, LayoutGraph
from .catalog import ServiceCatalog
from .patterns.ha_multiregion import HAMultiRegionPattern


class LayoutComposer:
    """
    Composes logical layouts from user requirements and service intents.
    Supports different architectural patterns.
    """
    
    def __init__(self, catalog: ServiceCatalog):
        self.catalog = catalog
        self.patterns = {
            "ha-multiregion": HAMultiRegionPattern()
        }
    
    def compose_layout(self, requirements: Requirements, pattern: str = "ha-multiregion") -> LayoutGraph:
        """
        Compose a layout graph from requirements using the specified pattern.
        
        Args:
            requirements: Architecture requirements with user intents
            pattern: Layout pattern to use (default: "ha-multiregion")
            
        Returns:
            LayoutGraph ready for rendering
        """
        if pattern not in self.patterns:
            raise ValueError(f"Unknown pattern: {pattern}. Available patterns: {list(self.patterns.keys())}")
        
        # Resolve dependencies for all user intents
        resolved_intents = self.catalog.resolve_dependencies(requirements.services)
        
        # Apply the selected pattern
        pattern_impl = self.patterns[pattern]
        layout_graph = pattern_impl.apply_pattern(requirements, resolved_intents)
        
        # Apply layout optimizations
        self._optimize_layout(layout_graph)
        
        return layout_graph
    
    def _optimize_layout(self, graph: LayoutGraph) -> None:
        """
        Apply layout optimizations to reduce edge crossings and improve readability.
        Implements requirements 2, 12, 13: minimal crossings, strong layout constraints, pattern templates.
        """
        # Sort nodes within clusters by service type for consistency (requirement 12)
        cluster_nodes = {}
        for node in graph.nodes:
            cluster = node.cluster or "default"
            if cluster not in cluster_nodes:
                cluster_nodes[cluster] = []
            cluster_nodes[cluster].append(node)
        
        # Enhanced service priority for better visual hierarchy (requirement 13: pattern templates)
        service_priority = {
            # Edge services first - top-left positioning (requirement 3)
            "front_door": 1,
            "cdn": 2,
            "traffic_manager": 3,
            "application_gateway": 4,
            
            # Identity services - left side (requirement 3)
            "entra_id": 10,
            "active_directory": 11,
            "key_vault": 12,
            
            # Compute services - middle tier (requirement 3)
            "load_balancer": 20,
            "vm": 21,
            "web_app": 22,
            "app_service": 23,
            "function_app": 24,
            "aks": 25,
            "container_instances": 26,
            
            # Network services - infrastructure layer
            "vnet": 30,
            "subnet": 31,
            "nsg": 32,
            "public_ip": 33,
            "firewall": 34,
            "vpn_gateway": 35,
            
            # Data services - bottom tier (requirement 3)
            "redis": 40,
            "queue_storage": 41,
            "table_storage": 42,
            "blob_storage": 43,
            "storage_account": 44,
            "sql_database": 45,
            "cosmos_db": 46,
            
            # Monitoring - separate tier
            "log_analytics": 50,
            "application_insights": 51,
            "monitor": 52,
        }
        
        # Sort nodes within each cluster by priority (requirement 12: strong layout constraints)
        for cluster, nodes in cluster_nodes.items():
            nodes.sort(key=lambda n: service_priority.get(n.service_type, 100))
            
            # Apply rank constraints within clusters for better hierarchy
            for i, node in enumerate(nodes):
                node.rank = service_priority.get(node.service_type, 100) + i
        
        # Enhanced edge numbering and crossing minimization (requirement 2, 12)
        self._update_edge_numbering(graph)
        self._minimize_edge_crossings(graph)
        self._apply_pattern_constraints(graph)
        
    def _minimize_edge_crossings(self, graph: LayoutGraph) -> None:
        """
        Minimize edge crossings using heuristic algorithms (requirement 2).
        """
        # Group edges by direction and priority
        horizontal_edges = []
        vertical_edges = []
        workflow_edges = []
        
        for edge in graph.edges:
            if edge.label and any(num in edge.label for num in ["1.", "2.", "3.", "4.", "5."]):
                workflow_edges.append(edge)
            elif edge.style == "dashed":
                horizontal_edges.append(edge)  # Cache/async connections typically horizontal
            else:
                vertical_edges.append(edge)    # Data flow typically vertical
        
        # Apply weight constraints to minimize crossings
        for edge in workflow_edges:
            # Higher weight for workflow edges to keep them straighter
            if not hasattr(edge, 'weight'):
                edge.weight = 10
        
        for edge in horizontal_edges:
            if not hasattr(edge, 'weight'):
                edge.weight = 5
                
        for edge in vertical_edges:
            if not hasattr(edge, 'weight'):
                edge.weight = 3
    
    def _apply_pattern_constraints(self, graph: LayoutGraph) -> None:
        """
        Apply consistent multi-region layout pattern constraints (requirement 13).
        """
        # Identify cluster types for consistent positioning
        edge_clusters = [name for name in graph.clusters.keys() if "edge" in name.lower() or "internet" in name.lower()]
        identity_clusters = [name for name in graph.clusters.keys() if "identity" in name.lower() or "security" in name.lower()]
        region_clusters = [name for name in graph.clusters.keys() if "region" in name.lower()]
        monitoring_clusters = [name for name in graph.clusters.keys() if "monitor" in name.lower()]
        
        # Apply rank constraints for consistent pattern (requirement 13)
        for cluster_name in edge_clusters:
            if cluster_name in graph.clusters:
                graph.clusters[cluster_name]["rank"] = "min"  # Top positioning
                
        for cluster_name in identity_clusters:
            if cluster_name in graph.clusters:
                graph.clusters[cluster_name]["rank"] = "same"  # Left positioning
                
        for cluster_name in region_clusters:
            if cluster_name in graph.clusters:
                graph.clusters[cluster_name]["rank"] = "same"  # Center positioning
                
        for cluster_name in monitoring_clusters:
            if cluster_name in graph.clusters:
                graph.clusters[cluster_name]["rank"] = "max"   # Right/bottom positioning
    
    def _update_edge_numbering(self, graph: LayoutGraph) -> None:
        """
        Update edge numbering to ensure a logical flow sequence.
        """
        # Find edges with numeric labels (workflow steps)
        workflow_edges = []
        other_edges = []
        
        for edge in graph.edges:
            if edge.label and edge.label.isdigit():
                workflow_edges.append(edge)
            else:
                other_edges.append(edge)
        
        # Sort workflow edges by current label number
        workflow_edges.sort(key=lambda e: int(e.label))
        
        # Renumber workflow edges sequentially
        for i, edge in enumerate(workflow_edges, 1):
            edge.label = str(i)
    
    def validate_requirements(self, requirements: Requirements) -> List[str]:
        """
        Validate requirements and return list of validation errors.
        
        Args:
            requirements: Requirements to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not requirements.regions:
            errors.append("At least one region must be specified")
        
        if not requirements.services:
            errors.append("At least one service must be specified")
        
        # Validate service types
        for service in requirements.services:
            if not self.catalog.get_service(service.kind):
                errors.append(f"Unknown service type: {service.kind}")
        
        # Validate HA mode vs regions
        if requirements.ha_mode in ["multi-region", "active-passive", "active-active"] and len(requirements.regions) < 2:
            errors.append(f"HA mode '{requirements.ha_mode}' requires at least 2 regions")
        
        # Validate region names (basic check)
        valid_regions = {
            "East US", "East US 2", "West US", "West US 2", "West US 3",
            "Central US", "South Central US", "North Central US",
            "Canada Central", "Canada East",
            "Brazil South",
            "UK South", "UK West",
            "North Europe", "West Europe",
            "France Central",
            "Germany West Central",
            "Norway East",
            "Switzerland North",
            "UAE North",
            "South Africa North",
            "Australia East", "Australia Southeast",
            "Southeast Asia", "East Asia",
            "Japan East", "Japan West",
            "Korea Central",
            "India Central", "India South",
        }
        
        for region in requirements.regions:
            if region not in valid_regions:
                errors.append(f"Invalid or unsupported region: {region}")
        
        return errors
    
    def get_missing_configurations(self, requirements: Requirements) -> Dict[str, List[str]]:
        """
        Identify missing configurations that require user input.
        
        Args:
            requirements: Requirements to check
            
        Returns:
            Dictionary mapping service names to lists of missing configuration prompts
        """
        missing = {}
        
        for service in requirements.services:
            prompts = self.catalog.get_missing_properties(service)
            if prompts:
                service_name = service.name or service.kind
                missing[service_name] = prompts
        
        return missing