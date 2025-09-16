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
        
        # Create clusters based on the pattern and actual service groups
        self._create_clusters(graph, service_groups, requirements)
        
        # Place nodes in appropriate clusters
        self._place_nodes(graph, service_groups, requirements)
        
        # Create edges with proper styling and numbering
        self._create_edges(graph, service_groups, requirements)
        
        return graph
    
    def _organize_services(self, intents: List[UserIntent], requirements: Requirements) -> Dict[str, List[UserIntent]]:
        """Organize services into logical groups for clear layering."""
        groups = {
            "edge": [],
            "identity": [],
            "region_compute": [],
            "region_network": [],
            "region_storage": [],
            "region_database": [],
            "monitoring": []
        }
        
        # First, add services from the edge_services and identity_services sections
        for edge_service in requirements.edge_services:
            edge_intent = UserIntent(kind=edge_service, name=None)
            groups["edge"].append(edge_intent)
        
        for identity_service in requirements.identity_services:
            identity_intent = UserIntent(kind=identity_service, name=None)
            groups["identity"].append(identity_intent)
        
        # Then process the main services list
        for intent in intents:
            service_type = intent.kind
            
            # Edge/Internet services (top layer)
            if service_type in ["front_door", "cdn", "traffic_manager"]:
                groups["edge"].append(intent)
            
            # Identity and security services (top-left layer)
            elif service_type in ["entra_id", "key_vault", "active_directory"]:
                groups["identity"].append(intent)
            
            # Compute services (middle layer)
            elif service_type in ["vm", "web_app", "function_app", "app_service_plan", "app_services", "container_instances", "aks"]:
                groups["region_compute"].append(intent)
            
            # Network services (entry layer within regions)
            elif service_type in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway", "vpn_gateway", "express_route"]:
                groups["region_network"].append(intent)
            
            # Storage services (bottom layer) - includes Queue Storage and Table Storage
            elif service_type in ["storage_account", "disk", "blob_storage", "queue_storage", "table_storage", "file_storage", "data_lake"]:
                groups["region_storage"].append(intent)
            
            # Database and cache services (bottom layer) - includes Redis
            elif service_type in ["sql_database", "redis", "cosmos_db", "mysql", "postgresql", "cache_for_redis"]:
                groups["region_database"].append(intent)
            
            # Monitoring and observability (bottom/right layer)
            elif service_type in ["log_analytics", "application_insights", "monitor", "sentinel", "security_center"]:
                groups["monitoring"].append(intent)
            
            else:
                # Default to region compute for unknown services
                groups["region_compute"].append(intent)
        
        return groups
    
    def _create_clusters(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Create cluster definitions for clear swimlanes and logical layering."""
        
        # Internet/Edge Layer (Top) - Global entry points
        if len(service_groups["edge"]) > 0:
            graph.clusters["internet_edge"] = {
                "label": "Internet & Edge Services",
                "bgcolor": "#E8F4F8",
                "style": "rounded,bold",
                "rank": "min",
                "penwidth": "2.0"
            }
        
        # Identity Layer (Top-Left) - Authentication and security
        if len(service_groups["identity"]) > 0:
            graph.clusters["identity_security"] = {
                "label": "Identity & Security",
                "bgcolor": "#FDECEE", 
                "style": "rounded,bold",
                "rank": "min",
                "penwidth": "2.0"
            }
        
        # Active regions with clear horizontal alignment
        for i, region in enumerate(requirements.regions[:2]):  # Max 2 active regions
            cluster_name = f"region_{region.lower().replace(' ', '_')}"
            region_label = f"Active Region: {region}" if i < 2 else f"Region: {region}"
            
            graph.clusters[cluster_name] = {
                "label": region_label,
                "bgcolor": "#F0F8F0" if i == 0 else "#F8F0F8",
                "style": "rounded,bold",
                "rank": "same",
                "penwidth": "2.0"
            }
            
            # Clear sub-clusters for layered architecture within region
            graph.clusters[f"{cluster_name}_network"] = {
                "label": "Network Layer",
                "bgcolor": "#FFFFFF",
                "style": "dashed",
                "parent": cluster_name,
                "rank": "0"
            }
            
            graph.clusters[f"{cluster_name}_compute"] = {
                "label": "App & Compute Layer", 
                "bgcolor": "#FFFFFF",
                "style": "dashed",
                "parent": cluster_name,
                "rank": "1"
            }
            
            graph.clusters[f"{cluster_name}_data"] = {
                "label": "Data & Storage Layer",
                "bgcolor": "#FFFFFF", 
                "style": "dashed",
                "parent": cluster_name,
                "rank": "2"
            }
        
        # Standby region (if multi-region and more than 2 regions)
        if len(requirements.regions) > 2:
            standby_region = requirements.regions[2]
            cluster_name = f"region_{standby_region.lower().replace(' ', '_')}_standby"
            graph.clusters[cluster_name] = {
                "label": f"Standby Region: {standby_region}",
                "bgcolor": "#F5F5F5",
                "style": "rounded,bold",
                "rank": "max",
                "penwidth": "2.0"
            }
            
            # Add standby sub-clusters for consistency
            graph.clusters[f"{cluster_name}_compute"] = {
                "label": "Standby Compute",
                "bgcolor": "#FFFFFF",
                "style": "dashed",
                "parent": cluster_name
            }
            
            graph.clusters[f"{cluster_name}_data"] = {
                "label": "Standby Data",
                "bgcolor": "#FFFFFF",
                "style": "dashed", 
                "parent": cluster_name
            }
        
        # Monitoring cluster (Bottom/Right) - Observability layer
        if len(service_groups["monitoring"]) > 0:
            graph.clusters["monitoring"] = {
                "label": "Monitoring & Observability",
                "bgcolor": "#EBF5FB",
                "style": "rounded,bold", 
                "rank": "max",
                "penwidth": "2.0"
            }
    
    def _place_nodes(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Place service nodes in appropriate clusters with clear layering."""
        node_id_counter = 1
        
        # Internet/Edge services (Top layer)
        for intent in service_groups["edge"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="internet_edge",
                rank=0,  # Top layer
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
        
        # Identity services (Top-Left layer)
        for intent in service_groups["identity"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="identity_security",
                rank=0,  # Top layer
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
        
        # Regional services with proper layering
        for i, region in enumerate(requirements.regions[:2]):
            cluster_prefix = f"region_{region.lower().replace(' ', '_')}"
            
            # Network services (Layer 0 - Entry points)
            for intent in service_groups["region_network"]:
                # Skip internal components that aren't shown separately
                if intent.kind in ["nic", "disk", "subnet"]:
                    continue
                    
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_network",
                    rank=10 + i,  # Network layer
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Compute services (Layer 1 - Application layer)
            for intent in service_groups["region_compute"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_compute",
                    rank=20 + i,  # Compute layer
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Data/Storage services (Layer 2 - Data layer)
            for intent in service_groups["region_storage"] + service_groups["region_database"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_data",
                    rank=30 + i,  # Data layer
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
        
        # Standby region services (if applicable)
        if len(requirements.regions) > 2:
            standby_region = requirements.regions[2]
            cluster_prefix = f"region_{standby_region.lower().replace(' ', '_')}_standby"
            
            # Standby compute services
            for intent in service_groups["region_compute"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} (Standby {standby_region})",
                    cluster=f"{cluster_prefix}_compute",
                    rank=50,  # Standby layer
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Standby data services
            for intent in service_groups["region_storage"] + service_groups["region_database"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} (Standby {standby_region})",
                    cluster=f"{cluster_prefix}_data",
                    rank=51,  # Standby data layer
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
        
        # Monitoring services (Bottom/Right layer)
        for intent in service_groups["monitoring"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="monitoring",
                rank=100,  # Bottom layer
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
        
        # Security connections (Key Vault)
        self._create_security_connections(graph, service_to_nodes)
    
    def _create_edge_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create edge flow connections with clear labeling and minimal crossings."""
        step_counter = 1
        
        # Primary flow: Internet -> Edge services -> Regional gateways -> Apps
        
        # Step 1: Front Door/CDN -> Application Gateway
        if "front_door" in service_to_nodes and "application_gateway" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                for ag_node in service_to_nodes["application_gateway"]:
                    edge = LayoutEdge(
                        source=fd_node,
                        target=ag_node,
                        label=f"{step_counter} (HTTPS)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
            step_counter += 1
        
        # Step 2: Application Gateway -> Load Balancer (if present)
        if "application_gateway" in service_to_nodes and "load_balancer" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for lb_node in service_to_nodes["load_balancer"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=lb_node,
                        label=f"{step_counter} (HTTP)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
            step_counter += 1
        
        # Step 3: Load Balancer -> Web App OR Application Gateway -> Web App (if no LB)
        if "load_balancer" in service_to_nodes and "web_app" in service_to_nodes:
            for lb_node in service_to_nodes["load_balancer"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=lb_node,
                        target=wa_node,
                        label=f"{step_counter} (HTTP)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
            step_counter += 1
        elif "application_gateway" in service_to_nodes and "web_app" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=wa_node,
                        label=f"{step_counter} (HTTP)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
            step_counter += 1
        
        # Step 4: Web App -> Function App
        if "web_app" in service_to_nodes and "function_app" in service_to_nodes:
            for wa_node in service_to_nodes["web_app"]:
                for fa_node in service_to_nodes["function_app"]:
                    edge = LayoutEdge(
                        source=wa_node,
                        target=fa_node,
                        label=f"{step_counter} (API)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
            step_counter += 1
        
        # Direct Front Door -> Web App if no gateway
        if "front_door" in service_to_nodes and "web_app" in service_to_nodes and "application_gateway" not in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=fd_node,
                        target=wa_node,
                        label=f"{step_counter} (HTTPS)",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
    
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
        """Create data flow connections with specific patterns for storage services."""
        
        # Get app services that will connect to data layers
        app_services = (service_to_nodes.get("web_app", []) + 
                       service_to_nodes.get("function_app", []) + 
                       service_to_nodes.get("app_services", []))
        
        # Function App -> Queue Storage (Step 5: Messaging pattern)
        if "function_app" in service_to_nodes and "queue_storage" in service_to_nodes:
            for fa_node in service_to_nodes["function_app"]:
                for queue_node in service_to_nodes["queue_storage"]:
                    edge = LayoutEdge(
                        source=fa_node,
                        target=queue_node,
                        label="5 (Queue)",
                        style="solid",
                        color="#FF8C00"
                    )
                    graph.edges.append(edge)
        
        # App services -> Redis Cache (Caching pattern)
        for app_node in app_services:
            for redis_node in service_to_nodes.get("redis", []) + service_to_nodes.get("cache_for_redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label="Cache",
                    style="dashed",
                    color="#87CEEB"
                )
                graph.edges.append(edge)
        
        # App services -> Table Storage (Data pattern)
        for app_node in app_services:
            for table_node in service_to_nodes.get("table_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=table_node,
                    label="Data",
                    style="solid",
                    color="#1E90FF"
                )
                graph.edges.append(edge)
        
        # App services -> Storage Account (General storage)
        for app_node in app_services:
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label="Files",
                    style="solid",
                    color="#1E90FF"
                )
                graph.edges.append(edge)
        
        # App services -> SQL Database
        for app_node in app_services:
            for db_node in service_to_nodes.get("sql_database", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=db_node,
                    label="SQL",
                    style="solid",
                    color="#1E90FF"
                )
                graph.edges.append(edge)
        
        # Cross-region replication patterns (minimal crossings)
        self._create_replication_edges(graph, service_to_nodes)
    
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
    
    def _create_security_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create security connections from Key Vault to compute services."""
        # Key Vault -> All compute services for secrets/certificates
        key_vault_nodes = service_to_nodes.get("key_vault", [])
        
        for kv_node in key_vault_nodes:
            # Connect Key Vault to compute services
            for service_type in ["web_app", "function_app", "vm"]:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=kv_node,
                        target=service_node,
                        label="Secrets",
                        style="dashed",
                        color="#FF6B6B"
                    )
                    graph.edges.append(edge)
    
    def _create_replication_edges(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create cross-region replication edges with minimal crossings."""
        
        # Storage account replication (primary connection)
        storage_nodes = service_to_nodes.get("storage_account", [])
        if len(storage_nodes) >= 2:
            for i in range(0, len(storage_nodes) - 1, 2):
                if i + 1 < len(storage_nodes):
                    edge = LayoutEdge(
                        source=storage_nodes[i],
                        target=storage_nodes[i + 1],
                        label="Replication",
                        style="solid",
                        color="#2E86C1"
                    )
                    graph.edges.append(edge)
        
        # Redis cache replication (dashed for cache sync)
        redis_nodes = (service_to_nodes.get("redis", []) + 
                      service_to_nodes.get("cache_for_redis", []))
        if len(redis_nodes) >= 2:
            for i in range(0, len(redis_nodes) - 1, 2):
                if i + 1 < len(redis_nodes):
                    edge = LayoutEdge(
                        source=redis_nodes[i],
                        target=redis_nodes[i + 1],
                        label="Sync",
                        style="dashed",
                        color="#7D3C98"
                    )
                    graph.edges.append(edge)
    
    def _get_default_name(self, service_type: str) -> str:
        """Get default display name for a service type."""
        name_mapping = {
            "vm": "Virtual Machine",
            "web_app": "Web App",
            "function_app": "Function App",
            "app_services": "App Service",
            "storage_account": "Storage Account",
            "queue_storage": "Queue Storage",
            "table_storage": "Table Storage",
            "blob_storage": "Blob Storage",
            "file_storage": "File Storage",
            "sql_database": "SQL Database",
            "redis": "Redis Cache", 
            "cache_for_redis": "Redis Cache",
            "cosmos_db": "Cosmos DB",
            "front_door": "Front Door",
            "application_gateway": "App Gateway",
            "load_balancer": "Load Balancer",
            "vnet": "Virtual Network",
            "nsg": "Security Group",
            "public_ip": "Public IP",
            "key_vault": "Key Vault",
            "entra_id": "Entra ID",
            "active_directory": "Active Directory",
            "log_analytics": "Log Analytics",
            "application_insights": "App Insights",
            "aks": "Kubernetes Service",
            "container_instances": "Container Instances"
        }
        return name_mapping.get(service_type, service_type.replace("_", " ").title())