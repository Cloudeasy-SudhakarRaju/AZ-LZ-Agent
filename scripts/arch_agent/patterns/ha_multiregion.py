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
        """Organize services into logical groups with enhanced categorization."""
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
        
        # Then process the main services list with improved categorization
        for intent in intents:
            service_type = intent.kind
            
            # Edge services - Entry points and CDN
            if service_type in ["front_door", "cdn", "traffic_manager"]:
                groups["edge"].append(intent)
            
            # Identity and Security services
            elif service_type in ["entra_id", "key_vault", "active_directory"]:
                groups["identity"].append(intent)
            
            # Compute services - Application layer
            elif service_type in ["vm", "web_app", "function_app", "app_service_plan", "aks", "container_instances"]:
                groups["region_compute"].append(intent)
            
            # Network services - Infrastructure layer
            elif service_type in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway", 
                                 "firewall", "vpn_gateway", "express_route"]:
                groups["region_network"].append(intent)
            
            # Storage services - Data layer (following requirement 5)
            elif service_type in ["storage_account", "disk", "queue_storage", "table_storage", "blob_storage", "file_storage"]:
                groups["region_storage"].append(intent)
            
            # Database services - Data layer (following requirement 5)
            elif service_type in ["sql_database", "redis", "cosmos_db", "mysql", "postgresql"]:
                groups["region_database"].append(intent)
            
            # Monitoring and observability services
            elif service_type in ["log_analytics", "application_insights", "monitor", "sentinel"]:
                groups["monitoring"].append(intent)
            
            else:
                # Default to region compute for unknown services
                groups["region_compute"].append(intent)
        
        return groups
    
    def _create_clusters(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Create cluster definitions with improved logical separation and visual hierarchy."""
        
        # Requirement 1: Clear containers/swimlanes - Internet/Edge Layer (Top-Left) - Entry points
        if len(service_groups["edge"]) > 0:
            graph.clusters["internet_edge"] = {
                "label": "Internet & Edge Services",
                "bgcolor": "#FFF5F5",  # Light red for edge/internet per requirement 10
                "style": "bold,rounded,filled",
                "rank": "min",
                "penwidth": "3",
                "fontcolor": "#1A202C",
                "fontsize": "14",
                "pencolor": "#E53E3E"
            }
        
        # Requirement 1 & 8: Identity Layer (Left side, below edge) - Security and Identity
        if len(service_groups["identity"]) > 0:
            graph.clusters["identity_security"] = {
                "label": "Identity & Security",
                "bgcolor": "#FFFAF0",  # Light orange for identity per requirement 10
                "style": "bold,rounded,filled", 
                "rank": "min",
                "penwidth": "3",
                "fontcolor": "#1A202C",
                "fontsize": "14",
                "pencolor": "#DD6B20"
            }
        
        # Requirement 1 & 7: Active Regions - Clear region separation with horizontal alignment
        active_regions = requirements.regions[:2] if requirements.ha_mode in ["multi-region", "active-active"] else requirements.regions[:1]
        
        for i, region in enumerate(active_regions):
            cluster_name = f"active_region_{i+1}_{region.lower().replace(' ', '_')}"
            
            # Requirement 6 & 10: Main region cluster with enhanced styling and horizontal alignment
            graph.clusters[cluster_name] = {
                "label": f"Active Region {i+1}: {region}",
                "bgcolor": "#F0FFF4" if i == 0 else "#F3E5F5",  # Green for primary, purple for secondary per requirement 10
                "style": "bold,rounded,filled",
                "rank": "same" if len(active_regions) > 1 else "same",
                "penwidth": "3",
                "fontcolor": "#1A202C",
                "fontsize": "14",
                "pencolor": "#38A169" if i == 0 else "#9F7AEA"
            }
            
            # Requirement 3 & 8: Network Layer (Top of region) - Proper visual hierarchy
            if any(intent.kind in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway"] 
                   for intent in service_groups["region_network"]):
                graph.clusters[f"{cluster_name}_network"] = {
                    "label": "Network Layer",
                    "bgcolor": "#FFFFFF",
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "min",
                    "penwidth": "2",
                    "fontcolor": "#2D3748",
                    "pencolor": "#4A5568"
                }
            
            # Requirement 3 & 8: Application/Compute Layer (Middle of region) - Following visual hierarchy
            if len(service_groups["region_compute"]) > 0:
                graph.clusters[f"{cluster_name}_compute"] = {
                    "label": "Application & Compute",
                    "bgcolor": "#FFFFFF", 
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "same",
                    "penwidth": "2",
                    "fontcolor": "#2D3748",
                    "pencolor": "#4A5568"
                }
            
            # Requirement 3 & 8: Data Layer (Bottom of region) - Following visual hierarchy
            if len(service_groups["region_storage"]) > 0 or len(service_groups["region_database"]) > 0:
                graph.clusters[f"{cluster_name}_data"] = {
                    "label": "Data & Storage",
                    "bgcolor": "#FFFFFF",
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "max",
                    "penwidth": "2",
                    "fontcolor": "#2D3748",
                    "pencolor": "#4A5568"
                }
        
        # Requirement 7 & 13: Standby Region (Bottom) - Clear region separation with pattern templates
        if len(requirements.regions) > 2 or requirements.ha_mode == "active-passive":
            standby_region = requirements.regions[-1] if len(requirements.regions) > 2 else requirements.regions[1]
            cluster_name = f"standby_region_{standby_region.lower().replace(' ', '_')}"
            
            graph.clusters[cluster_name] = {
                "label": f"Standby Region: {standby_region}",
                "bgcolor": "#F7FAFC",  # Light gray for standby per requirement 10
                "style": "bold,rounded,filled,dashed",
                "rank": "max",
                "penwidth": "3",
                "fontcolor": "#2D3748",
                "fontsize": "13",
                "pencolor": "#718096"
            }
            
            # Requirement 8: Simplified standby components - logical grouping
            graph.clusters[f"{cluster_name}_backup"] = {
                "label": "Backup & DR",
                "bgcolor": "#FFFFFF",
                "style": "dashed,rounded,filled",
                "parent": cluster_name,
                "penwidth": "2",
                "fontcolor": "#2D3748",
                "pencolor": "#718096"
            }
        
        # Requirement 1 & 8: Monitoring & Observability (Right side) - Logical grouping
        if len(service_groups["monitoring"]) > 0:
            graph.clusters["monitoring_observability"] = {
                "label": "Monitoring & Observability",
                "bgcolor": "#FFFBF0",  # Light yellow for monitoring per requirement 10
                "style": "bold,rounded,filled",
                "rank": "same",
                "penwidth": "3",
                "fontcolor": "#1A202C",
                "fontsize": "14",
                "pencolor": "#F6AD55"
            }
    
    def _place_nodes(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Place service nodes in appropriate clusters following visual hierarchy."""
        node_id_counter = 1
        
        # Edge services (Top-Left) - Internet entry points
        for intent in service_groups["edge"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="internet_edge",
                rank=1,
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
        
        # Identity services (Left side) - Security layer
        for intent in service_groups["identity"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="identity_security",
                rank=2,
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
        
        # Regional services with proper layering (Network -> Compute -> Data)
        active_regions = requirements.regions[:2] if requirements.ha_mode in ["multi-region", "active-active"] else requirements.regions[:1]
        
        for i, region in enumerate(active_regions):
            cluster_prefix = f"active_region_{i+1}_{region.lower().replace(' ', '_')}"
            
            # Network services (Top layer within region) - Infrastructure
            for intent in service_groups["region_network"]:
                # Skip internal components like NIC, disk that aren't shown separately
                if intent.kind in ["nic", "disk", "subnet"]:
                    continue
                    
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_network",
                    rank=3 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Compute services (Middle layer within region) - Applications
            for intent in service_groups["region_compute"]:
                # Skip internal components
                if intent.kind in ["app_service_plan"]:
                    continue
                    
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_compute",
                    rank=4 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
            
            # Data services (Bottom layer within region) - Storage and databases
            for intent in service_groups["region_storage"] + service_groups["region_database"]:
                node = LayoutNode(
                    id=f"node_{node_id_counter}",
                    service_type=intent.kind,
                    name=f"{intent.name or self._get_default_name(intent.kind)} ({region})",
                    cluster=f"{cluster_prefix}_data",
                    rank=5 + i,
                    properties=intent.properties
                )
                graph.nodes.append(node)
                node_id_counter += 1
        
        # Standby region services (if applicable)
        if len(requirements.regions) > 2 or requirements.ha_mode == "active-passive":
            standby_region = requirements.regions[-1] if len(requirements.regions) > 2 else requirements.regions[1]
            cluster_prefix = f"standby_region_{standby_region.lower().replace(' ', '_')}"
            
            # Only include critical backup services in standby
            for intent in service_groups["region_storage"] + service_groups["region_database"]:
                if intent.kind in ["storage_account", "sql_database"]:  # Only backup-relevant services
                    node = LayoutNode(
                        id=f"node_{node_id_counter}",
                        service_type=intent.kind,
                        name=f"{intent.name or self._get_default_name(intent.kind)} Backup ({standby_region})",
                        cluster=f"{cluster_prefix}_backup",
                        rank=8,
                        properties=intent.properties
                    )
                    graph.nodes.append(node)
                    node_id_counter += 1
        
        # Monitoring services (Right side) - Observability layer
        for intent in service_groups["monitoring"]:
            node = LayoutNode(
                id=f"node_{node_id_counter}",
                service_type=intent.kind,
                name=intent.name or self._get_default_name(intent.kind),
                cluster="monitoring_observability",
                rank=6,
                properties=intent.properties
            )
            graph.nodes.append(node)
            node_id_counter += 1
    
    def _create_edges(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Create edges with enhanced workflow numbering, clear labeling, and proper styling."""
        # Create a mapping of service types to node IDs for easier edge creation
        service_to_nodes = {}
        for node in graph.nodes:
            service_type = node.service_type
            if service_type not in service_to_nodes:
                service_to_nodes[service_type] = []
            service_to_nodes[service_type].append(node.id)
        
        # Primary traffic flow: Internet -> Edge -> App -> Data (requirement 2, 4, 14, 15)
        self._create_primary_traffic_flow(graph, service_to_nodes)
        
        # Security connections: Identity -> Compute services (requirement 15)
        self._create_security_connections(graph, service_to_nodes)
        
        # Data flow: Applications -> Caches -> Databases (requirement 14, 15)
        self._create_data_flow(graph, service_to_nodes)
        
        # Monitoring connections: All services -> Monitoring (requirement 14)
        self._create_monitoring_connections(graph, service_to_nodes)
        
        # Inter-region connections for HA scenarios (requirement 15)
        self._create_inter_region_connections(graph, service_to_nodes, requirements)
    
    def _create_primary_traffic_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create primary traffic flow with clear numbering and minimal crossings (requirements 2, 4, 9)."""
        step = 1
        
        # Step 1: Internet -> Front Door (solid line for primary traffic per requirement 14)
        if "front_door" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                # Connect to Application Gateway if available
                if "application_gateway" in service_to_nodes:
                    for ag_node in service_to_nodes["application_gateway"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=ag_node,
                            label=f"{step}. HTTPS Traffic",
                            style="solid",
                            color="#1976D2"  # Strong blue for primary traffic per requirement 14
                        )
                        graph.edges.append(edge)
                        step += 1
                
                # Direct connection to Web App if no App Gateway
                elif "web_app" in service_to_nodes:
                    for wa_node in service_to_nodes["web_app"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=wa_node,
                            label=f"{step}. Direct HTTPS",
                            style="solid",
                            color="#1976D2"
                        )
                        graph.edges.append(edge)
                        step += 1
        
        # Step N: Application Gateway -> Web Apps (solid line for primary flow)
        if "application_gateway" in service_to_nodes and "web_app" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=wa_node,
                        label=f"{step}. Load Balanced",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
                    step += 1
        
        # Step N+1: Load Balancer -> VMs (solid line for infrastructure traffic)
        if "load_balancer" in service_to_nodes and "vm" in service_to_nodes:
            for lb_node in service_to_nodes["load_balancer"]:
                for vm_node in service_to_nodes["vm"]:
                    edge = LayoutEdge(
                        source=lb_node,
                        target=vm_node,
                        label=f"{step}. VM Traffic",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
                    step += 1
    
    def _create_data_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create data flow connections with proper styling and line type distinctions (requirements 14, 15)."""
        app_services = service_to_nodes.get("web_app", []) + service_to_nodes.get("function_app", []) + service_to_nodes.get("vm", [])
        
        for app_node in app_services:
            # Requirement 14: Cache connections (dashed for cache pattern, bidirectional per requirement 15)
            for redis_node in service_to_nodes.get("redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label="Cache (R/W)",
                    style="dashed",  # Dashed for cache pattern per requirement 14
                    color="#FF6B35"  # Orange for cache traffic
                )
                graph.edges.append(edge)
            
            # Requirement 14: Queue Storage connections (solid, single direction for async patterns per requirement 15)
            for queue_node in service_to_nodes.get("queue_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=queue_node,
                    label="Enqueue Messages",
                    style="solid",  # Solid for direct data operations per requirement 14
                    color="#4CAF50"  # Green for messaging
                )
                graph.edges.append(edge)
            
            # Requirement 14: Table Storage connections (solid, bidirectional for CRUD operations per requirement 15)
            for table_node in service_to_nodes.get("table_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=table_node,
                    label="Table Operations",
                    style="solid",  # Solid for direct data operations per requirement 14
                    color="#4CAF50"  # Green for storage operations
                )
                graph.edges.append(edge)
            
            # Storage Account connections (solid for direct file operations)
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label="File/Blob Data",
                    style="solid",
                    color="#4CAF50"
                )
                graph.edges.append(edge)
            
            # Database connections (solid, bidirectional for CRUD operations per requirement 15)
            for db_node in service_to_nodes.get("sql_database", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=db_node,
                    label="SQL Queries",
                    style="solid",
                    color="#9C27B0"  # Purple for database traffic
                )
                graph.edges.append(edge)
    
    def _create_security_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create security connections with clear labeling and dotted lines (requirements 4, 14, 15)."""
        # Requirement 14: Entra ID -> All compute services (dotted for control/management per requirement 14)
        entra_nodes = service_to_nodes.get("entra_id", [])
        compute_services = ["web_app", "function_app", "vm", "application_gateway"]
        
        for entra_node in entra_nodes:
            for service_type in compute_services:
                for compute_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=entra_node,
                        target=compute_node,
                        label="Auth/Identity",
                        style="dotted",  # Dotted for control/management connections per requirement 14
                        color="#FF9800"  # Orange for security connections
                    )
                    graph.edges.append(edge)
        
        # Requirement 14: Key Vault -> All services needing secrets (dotted for management)
        kv_nodes = service_to_nodes.get("key_vault", [])
        secret_consumers = ["web_app", "function_app", "vm", "sql_database"]
        
        for kv_node in kv_nodes:
            for service_type in secret_consumers:
                for consumer_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=kv_node,
                        target=consumer_node,
                        label="Secrets/Keys",
                        style="dotted",  # Dotted for management connections per requirement 14
                        color="#9C27B0"  # Purple for key management
                    )
                    graph.edges.append(edge)
    
    def _create_monitoring_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create monitoring connections with dotted lines (requirement 14)."""
        monitoring_nodes = service_to_nodes.get("application_insights", []) + service_to_nodes.get("log_analytics", [])
        
        # Requirement 14: All services send telemetry to monitoring (dotted for telemetry/control)
        all_services = ["web_app", "function_app", "vm", "sql_database", "redis", "storage_account", 
                       "queue_storage", "table_storage", "application_gateway", "front_door"]
        
        for monitoring_node in monitoring_nodes:
            for service_type in all_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=monitoring_node,
                        label="Telemetry",
                        style="dotted",  # Dotted for telemetry/monitoring per requirement 14
                        color="#607D8B"  # Blue-grey for monitoring
                    )
                    graph.edges.append(edge)
    
    def _create_inter_region_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]], requirements: Requirements) -> None:
        """Create inter-region connections for HA scenarios with proper styling (requirements 15, 13)."""
        if requirements.ha_mode in ["multi-region", "active-active"]:
            # Requirement 15: Storage replication between regions (dashed for replication patterns)
            storage_services = ["storage_account", "sql_database", "queue_storage", "table_storage"]
            
            for service_type in storage_services:
                nodes = service_to_nodes.get(service_type, [])
                if len(nodes) >= 2:  # At least 2 instances for replication
                    primary_node = nodes[0]
                    secondary_node = nodes[1]
                    
                    edge = LayoutEdge(
                        source=primary_node,
                        target=secondary_node,
                        label="Geo-Replication",
                        style="dashed",  # Dashed for replication per requirement 14
                        color="#FF9800"  # Orange for replication
                    )
                    graph.edges.append(edge)
                    
            # Cache synchronization between regions if Redis is present
            redis_nodes = service_to_nodes.get("redis", [])
            if len(redis_nodes) >= 2:
                edge = LayoutEdge(
                    source=redis_nodes[0],
                    target=redis_nodes[1],
                    label="Cache Sync",
                    style="dashed",  # Dashed for cache sync pattern
                    color="#FF6B35"  # Orange for cache traffic
                )
                graph.edges.append(edge)
    
    def _get_default_name(self, service_type: str) -> str:
        """Get default display name for a service type."""
        name_mapping = {
            "vm": "Virtual Machine",
            "web_app": "Web App",
            "function_app": "Function App",
            "storage_account": "Storage Account",
            "queue_storage": "Queue Storage",
            "table_storage": "Table Storage",
            "sql_database": "SQL Database",
            "redis": "Redis Cache",
            "front_door": "Front Door",
            "application_gateway": "App Gateway",
            "load_balancer": "Load Balancer",
            "vnet": "Virtual Network",
            "nsg": "Network Security Group",
            "public_ip": "Public IP",
            "key_vault": "Key Vault",
            "entra_id": "Entra ID",
            "log_analytics": "Log Analytics",
            "application_insights": "App Insights",
            "cdn": "CDN",
            "firewall": "Azure Firewall",
            "vpn_gateway": "VPN Gateway",
            "express_route": "ExpressRoute"
        }
        return name_mapping.get(service_type, service_type.replace("_", " ").title())