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
        """
        # Sort nodes within clusters by service type for consistency
        cluster_nodes = {}
        for node in graph.nodes:
            cluster = node.cluster or "default"
            if cluster not in cluster_nodes:
                cluster_nodes[cluster] = []
            cluster_nodes[cluster].append(node)
        
        # Requirement 3 & 10: Service priority for proper visual hierarchy (identity/edge → compute → data)
        service_priority = {
            # Edge services (top tier - requirement 3)
            "front_door": 1,
            "cdn": 2,
            "application_gateway": 3,
            
            # Identity services (left side - requirement 3)
            "entra_id": 10,
            "key_vault": 11,
            
            # Compute services (middle tier - requirement 3)
            "load_balancer": 20,
            "vm": 21,
            "web_app": 22,
            "function_app": 23,
            "aks": 24,
            
            # Network services (infrastructure)
            "vnet": 30,
            "nsg": 31,
            "public_ip": 32,
            
            # Requirement 5 & 3: Data services (bottom tier) - Add specified components with proper ordering
            "redis": 40,           # Cache tier - specified component
            "queue_storage": 41,   # Messaging tier - specified component
            "table_storage": 42,   # NoSQL tier - specified component  
            "storage_account": 43, # Blob storage tier
            "sql_database": 44,    # Relational database tier
            "cosmos_db": 45,       # Global database tier
            
            # Monitoring services (observability layer)
            "log_analytics": 50,
            "application_insights": 51,
        }
        
        for cluster, nodes in cluster_nodes.items():
            nodes.sort(key=lambda n: service_priority.get(n.service_type, 100))
        
        # Update edge labels to ensure proper numbering sequence
        self._update_edge_numbering(graph)
    
    def _update_edge_numbering(self, graph: LayoutGraph) -> None:
        """
        Update edge numbering to ensure a logical flow sequence (requirements 4, 9).
        """
        # Find edges with numeric labels (workflow steps)
        workflow_edges = []
        other_edges = []
        
        for edge in graph.edges:
            # Check if edge label starts with a number (workflow step)
            if edge.label and any(edge.label.startswith(f"{i}.") for i in range(1, 20)):
                workflow_edges.append(edge)
            else:
                other_edges.append(edge)
        
        # Sort workflow edges by current step number
        def get_step_number(edge):
            if edge.label:
                for i in range(1, 20):
                    if edge.label.startswith(f"{i}."):
                        return i
            return 999
        
        workflow_edges.sort(key=get_step_number)
        
        # Renumber workflow edges sequentially for clear workflow (requirement 9)
        for i, edge in enumerate(workflow_edges, 1):
            if edge.label:
                # Preserve the description part after the number
                parts = edge.label.split(".", 1)
                if len(parts) > 1:
                    edge.label = f"{i}.{parts[1]}"
                else:
                    edge.label = f"{i}. {edge.label}"
    
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