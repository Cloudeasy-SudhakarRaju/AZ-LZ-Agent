"""
HA Multi-Region pattern implementation.
Enforces Image1-style layout with left-to-right flow, logical clustering, and visual hierarchy.
"""
from typing import List, Dict, Any, Optional, Tuple
from ..schemas import Requirements, UserIntent, LayoutGraph, LayoutNode, LayoutEdge


class HAMultiRegionPattern:
    """
    Implements the HA Multi-Region pattern with Image1-style layout.
    
    Layout structure:
    - Left column: Identity/Edge services
    - Center: Two Active regions side-by-side
    - Bottom: One Standby region (if multi-region)
    - Sub-clusters per region (App Service, Functions, etc.)
    """
    
    def __init__(self):
        self.edge_step_counter = 1
    
    def apply_pattern(self, requirements: Requirements, resolved_intents: List[UserIntent]) -> LayoutGraph:
        """
        Apply the HA Multi-Region pattern to create a layout graph.
        
        Args:
            requirements: Architecture requirements
            resolved_intents: List of services including dependencies
            
        Returns:
            LayoutGraph with nodes, edges, and clusters defined
        """
        graph = LayoutGraph()
        
        # Organize services by type and region
        service_groups = self._organize_services(resolved_intents, requirements)
        
        # Create clusters based on the pattern
        self._create_clusters(graph, requirements)
        
        # Place nodes in appropriate clusters
        self._place_nodes(graph, service_groups, requirements)
        
        # Create edges with proper styling and numbering
        self._create_edges(graph, service_groups, requirements)
        
        return graph
    
    def _organize_services(self, intents: List[UserIntent], requirements: Requirements) -> Dict[str, List[UserIntent]]:
        """Organize services into logical groups."""
        groups = {
            "edge": [],
            "identity": [],
            "region_compute": [],
            "region_network": [],
            "region_storage": [],
            "region_database": [],
            "monitoring": []
        }
        
        for intent in intents:
            service_type = intent.kind
            
            if service_type in ["front_door", "cdn", "traffic_manager"]:
                groups["edge"].append(intent)
            elif service_type in ["entra_id", "key_vault"]:
                groups["identity"].append(intent)
            elif service_type in ["vm", "web_app", "function_app", "app_service_plan"]:
                groups["region_compute"].append(intent)
            elif service_type in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway"]:
                groups["region_network"].append(intent)
            elif service_type in ["storage_account", "disk"]:
                groups["region_storage"].append(intent)
            elif service_type in ["sql_database", "redis"]:
                groups["region_database"].append(intent)
            elif service_type in ["log_analytics", "application_insights"]:
                groups["monitoring"].append(intent)
            else:
                # Default to region compute
                groups["region_compute"].append(intent)
        
        return groups
    
    def _create_clusters(self, graph: LayoutGraph, requirements: Requirements) -> None:
        """Create cluster definitions for the layout."""
        # Edge/Identity column (left side)
        if any(len(group) > 0 for group in [requirements.edge_services, requirements.identity_services]):
            graph.clusters["edge_identity"] = {
                "label": "Edge & Identity",
                "bgcolor": "#E8F4F8",
                "style": "rounded",
                "rank": "min",
                "graph_attr": {"rankdir": "TB"}
            }
        
        # Primary regions
        for i, region in enumerate(requirements.regions[:2]):  # Max 2 active regions
            cluster_name = f"region_{region.lower().replace(' ', '_')}"
            graph.clusters[cluster_name] = {
                "label": f"Region: {region}",
                "bgcolor": "#F0F8F0" if i == 0 else "#F8F0F8",
                "style": "rounded",
                "rank": "same" if len(requirements.regions) > 1 else "max"
            }
            
            # Sub-clusters within region
            graph.clusters[f"{cluster_name}_compute"] = {
                "label": "Compute & Apps",
                "bgcolor": "#FFFFFF",
                "style": "dashed",
                "parent": cluster_name
            }
            
            graph.clusters[f"{cluster_name}_data"] = {
                "label": "Data & Storage",
                "bgcolor": "#FFFFFF",
                "style": "dashed", 
                "parent": cluster_name
            }
            
            graph.clusters[f"{cluster_name}_network"] = {
                "label": "Networking",
                "bgcolor": "#FFFFFF",
                "style": "dashed",
                "parent": cluster_name
            }
        
        # Standby region (if multi-region and more than 2 regions)
        if len(requirements.regions) > 2:
            standby_region = requirements.regions[2]
            cluster_name = f"region_{standby_region.lower().replace(' ', '_')}_standby"
            graph.clusters[cluster_name] = {
                "label": f"Standby: {standby_region}",
                "bgcolor": "#F5F5F5",
                "style": "rounded",
                "rank": "max"
            }
        
        # Monitoring cluster (right side)
        graph.clusters["monitoring"] = {
            "label": "Monitoring & Observability",
            "bgcolor": "#FFF8DC",
            "style": "rounded",
            "rank": "max"
        }
    
    def _place_nodes(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Place service nodes in appropriate clusters."""
        node_id_counter = 1
        
        # Edge and Identity services (left column)
        for intent in service_groups["edge"] + service_groups["identity"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="edge_identity",
                rank=1,
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
        
        # Regional services
        for i, region in enumerate(requirements.regions[:2]):
            cluster_prefix = f"region_{region.lower().replace(' ', '_')}"
            
            # Compute services
            for intent in service_groups["region_compute"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_compute",
                    rank=2 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Data services
            for intent in service_groups["region_storage"] + service_groups["region_database"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_data",
                    rank=2 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Network services (place in network sub-cluster)
            for intent in service_groups["region_network"]:
                # Skip internal components like NIC, disk that aren't shown separately
                if intent.kind in ["nic", "disk"]:
                    continue
                    
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_network",
                    rank=2 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
        
        # Monitoring services (right side)
        for intent in service_groups["monitoring"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="monitoring",
                rank=4,
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
    
    def _create_edges(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Create edges with proper workflow numbering and styling."""
        # Create a mapping of service types to node IDs for easier edge creation
        service_to_nodes = {}
        for node in graph.nodes:
            service_type = node.service_type
            if service_type not in service_to_nodes:
                service_to_nodes[service_type] = []
            service_to_nodes[service_type].append(node.id)
        
        # Edge flow: External traffic -> Edge services -> Regional services
        self._create_edge_flow(graph, service_to_nodes)
        
        # Regional connectivity
        self._create_regional_connectivity(graph, service_to_nodes, requirements)
        
        # Data flow
        self._create_data_flow(graph, service_to_nodes)
        
        # Monitoring connections
        self._create_monitoring_connections(graph, service_to_nodes)
    
    def _create_edge_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create edge flow connections with numbering."""
        # Front Door/CDN -> Application Gateway -> Web App
        if "front_door" in service_to_nodes and "application_gateway" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                for ag_node in service_to_nodes["application_gateway"]:
                    edge = LayoutEdge(
                        source=fd_node,
                        target=ag_node,
                        label=f"{self.edge_step_counter}",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
                    self.edge_step_counter += 1
        
        if "application_gateway" in service_to_nodes and "web_app" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=wa_node,
                        label=f"{self.edge_step_counter}",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
                    self.edge_step_counter += 1
    
    def _create_regional_connectivity(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]], requirements: Requirements) -> None:
        """Create connectivity between regional services."""
        # Web App -> Function App
        if "web_app" in service_to_nodes and "function_app" in service_to_nodes:
            for wa_node in service_to_nodes["web_app"]:
                for fa_node in service_to_nodes["function_app"]:
                    edge = LayoutEdge(
                        source=wa_node,
                        target=fa_node,
                        label="API",
                        style="solid",
                        color="#008B8B"
                    )
                    graph.edges.append(edge)
        
        # VM -> Load Balancer
        if "vm" in service_to_nodes and "load_balancer" in service_to_nodes:
            for vm_node in service_to_nodes["vm"]:
                for lb_node in service_to_nodes["load_balancer"]:
                    edge = LayoutEdge(
                        source=lb_node,
                        target=vm_node,
                        style="solid",
                        color="#FF8C00"
                    )
                    graph.edges.append(edge)
    
    def _create_data_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create data flow connections."""
        # App services -> Redis cache
        app_services = service_to_nodes.get("web_app", []) + service_to_nodes.get("function_app", [])
        for app_node in app_services:
            for redis_node in service_to_nodes.get("redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label="Cache",
                    style="dashed",
                    color="#87CEEB"
                )
                graph.edges.append(edge)
        
        # App services -> Storage/Database
        for app_node in app_services:
            # Storage connections
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label="Data",
                    style="solid",
                    color="#1E90FF"
                )
                graph.edges.append(edge)
            
            # Database connections
            for db_node in service_to_nodes.get("sql_database", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=db_node,
                    label="SQL",
                    style="solid",
                    color="#1E90FF"
                )
                graph.edges.append(edge)
    
    def _create_monitoring_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create monitoring connections with dotted lines."""
        # All services -> Application Insights/Log Analytics
        monitoring_nodes = service_to_nodes.get("application_insights", []) + service_to_nodes.get("log_analytics", [])
        
        for monitoring_node in monitoring_nodes:
            # Connect all compute services to monitoring
            for service_type in ["web_app", "function_app", "vm"]:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=monitoring_node,
                        label="Telemetry",
                        style="dotted",
                        color="#9932CC"
                    )
                    graph.edges.append(edge)
    
    def _get_default_name(self, service_type: str) -> str:
        """Get default display name for a service type."""
        name_mapping = {
            "vm": "Virtual Machine",
            "web_app": "Web App",
            "function_app": "Function App",
            "storage_account": "Storage Account",
            "sql_database": "SQL Database",
            "redis": "Redis Cache",
            "front_door": "Front Door",
            "application_gateway": "App Gateway",
            "load_balancer": "Load Balancer",
            "vnet": "Virtual Network",
            "nsg": "Security Group",
            "public_ip": "Public IP",
            "key_vault": "Key Vault",
            "entra_id": "Entra ID",
            "log_analytics": "Log Analytics",
            "application_insights": "App Insights"
        }
        return name_mapping.get(service_type, service_type.replace("_", " ").title())