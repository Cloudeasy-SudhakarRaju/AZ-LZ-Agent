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
        
        # Internet/Edge Layer (Top-Left) - Entry points - Requirements 1, 3, 6, 8, 10
        if len(service_groups["edge"]) > 0:
            graph.clusters["internet_edge"] = {
                "label": "🌐 Internet & Edge Services",
                "bgcolor": "#E8F4FD",  # Enhanced light blue for internet/edge
                "style": "bold,rounded,filled",
                "rank": "min",
                "penwidth": "3",
                "fontsize": "14",
                "fontname": "Segoe UI Bold",
                "fontcolor": "#1565C0",
                "margin": "20",
                "color": "#1976D2"  # Strong blue border
            }
        
        # Identity Layer (Left side, below edge) - Security and Identity - Requirements 1, 3, 6, 8, 10
        if len(service_groups["identity"]) > 0:
            graph.clusters["identity_security"] = {
                "label": "🔐 Identity & Security",
                "bgcolor": "#FFF8E1",  # Enhanced light amber for security
                "style": "bold,rounded,filled", 
                "rank": "min",
                "penwidth": "3",
                "fontsize": "14",
                "fontname": "Segoe UI Bold",
                "fontcolor": "#E65100",
                "margin": "20",
                "color": "#FF8F00"  # Orange border for security
            }
        
        # Active Regions - Horizontal layout for better visibility
        active_regions = requirements.regions[:2] if requirements.ha_mode in ["multi-region", "active-active"] else requirements.regions[:1]
        
        for i, region in enumerate(active_regions):
            cluster_name = f"active_region_{i+1}_{region.lower().replace(' ', '_')}"
            
            # Main region cluster with enhanced styling - Requirements 1, 6, 7, 8, 10
            graph.clusters[cluster_name] = {
                "label": f"🏢 Active Region {i+1}: {region}",
                "bgcolor": "#E8F8F5" if i == 0 else "#F3E5F5",  # Enhanced green for primary, purple for secondary
                "style": "bold,rounded,filled",
                "rank": "same" if len(active_regions) > 1 else "same",
                "penwidth": "4",
                "fontsize": "16",
                "fontname": "Segoe UI Bold",
                "fontcolor": "#1B5E20" if i == 0 else "#4A148C",
                "margin": "25",
                "color": "#2E7D32" if i == 0 else "#7B1FA2"  # Strong green/purple borders for clear region separation
            }
            
            # Network Layer (Top of region) - Following requirement 3, 6, 8
            if any(intent.kind in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway"] 
                   for intent in service_groups["region_network"]):
                graph.clusters[f"{cluster_name}_network"] = {
                    "label": "🌐 Network Layer",
                    "bgcolor": "#F0F8FF",  # Alice blue for network
                    "style": "filled,rounded,bold",
                    "parent": cluster_name,
                    "rank": "min",
                    "penwidth": "2",
                    "fontsize": "12",
                    "fontname": "Segoe UI",
                    "fontcolor": "#0D47A1",
                    "color": "#1976D2"
                }
            
            # Application/Compute Layer (Middle of region) - Following requirement 3, 6, 8
            if len(service_groups["region_compute"]) > 0:
                graph.clusters[f"{cluster_name}_compute"] = {
                    "label": "⚙️ Application & Compute",
                    "bgcolor": "#FFF3E0",  # Light orange for compute
                    "style": "filled,rounded,bold",
                    "parent": cluster_name,
                    "rank": "same",
                    "penwidth": "2",
                    "fontsize": "12",
                    "fontname": "Segoe UI",
                    "fontcolor": "#E65100",
                    "color": "#FF9800"
                }
            
            # Data Layer (Bottom of region) - Following requirement 3, 6, 8
            if len(service_groups["region_storage"]) > 0 or len(service_groups["region_database"]) > 0:
                graph.clusters[f"{cluster_name}_data"] = {
                    "label": "💾 Data & Storage",
                    "bgcolor": "#E8F5E8",  # Light green for data
                    "style": "filled,rounded,bold",
                    "parent": cluster_name,
                    "rank": "max",
                    "penwidth": "2",
                    "fontsize": "12",
                    "fontname": "Segoe UI",
                    "fontcolor": "#2E7D32",
                    "color": "#4CAF50"
                }
        
        # Standby Region (Bottom) - Separate from active regions for clear distinction - Requirements 7, 8, 10
        if len(requirements.regions) > 2 or requirements.ha_mode == "active-passive":
            standby_region = requirements.regions[-1] if len(requirements.regions) > 2 else requirements.regions[1]
            cluster_name = f"standby_region_{standby_region.lower().replace(' ', '_')}"
            
            graph.clusters[cluster_name] = {
                "label": f"🏖️ Standby Region: {standby_region}",
                "bgcolor": "#FAFAFA",  # Enhanced light gray for standby
                "style": "bold,rounded,dashed,filled",
                "rank": "max",
                "penwidth": "3",
                "fontsize": "14",
                "fontname": "Segoe UI Bold",
                "fontcolor": "#616161",
                "margin": "20",
                "color": "#9E9E9E"  # Gray border for standby region
            }
            
            # Simplified standby components - Requirements 6, 8
            graph.clusters[f"{cluster_name}_backup"] = {
                "label": "🔄 Backup & DR",
                "bgcolor": "#FFFFFF",
                "style": "filled,rounded,bold",
                "parent": cluster_name,
                "penwidth": "2",
                "fontsize": "11",
                "fontname": "Segoe UI",
                "fontcolor": "#616161",
                "color": "#9E9E9E"
            }
        
        # Monitoring & Observability (Right side) - Separate from operational clusters - Requirements 8, 10
        if len(service_groups["monitoring"]) > 0:
            graph.clusters["monitoring_observability"] = {
                "label": "📊 Monitoring & Observability",
                "bgcolor": "#FFFDE7",  # Enhanced light yellow for monitoring
                "style": "bold,rounded,filled",
                "rank": "same",
                "penwidth": "3",
                "fontsize": "14",
                "fontname": "Segoe UI Bold",
                "fontcolor": "#F57F17",
                "margin": "20",
                "color": "#FBC02D"  # Yellow border for monitoring
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
        """Create primary traffic flow with clear numbering and minimal crossings (requirement 2, 4, 9)."""
        step_counter = 1
        
        # Step 1: Internet -> Front Door (straight line, solid)
        if "front_door" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                # Connect to Application Gateway if available
                if "application_gateway" in service_to_nodes:
                    for ag_node in service_to_nodes["application_gateway"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=ag_node,
                            label=f"{step_counter}. Global HTTPS Entry Point",
                            style="solid",
                            color="#1976D2"  # Strong blue for primary traffic
                        )
                        graph.edges.append(edge)
                        step_counter += 1
                
                # Direct connection to Web App if no App Gateway
                elif "web_app" in service_to_nodes:
                    for wa_node in service_to_nodes["web_app"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=wa_node,
                            label=f"{step_counter}. Direct HTTPS to App",
                            style="solid",
                            color="#1976D2"
                        )
                        graph.edges.append(edge)
                        step_counter += 1
        
        # Step 2: Application Gateway -> Web Apps (straight line, solid)
        if "application_gateway" in service_to_nodes and "web_app" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=wa_node,
                        label=f"{step_counter}. Load Balanced Routing",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
                    step_counter += 1
        
        # Step 3: Load Balancer -> VMs (if present)
        if "load_balancer" in service_to_nodes and "vm" in service_to_nodes:
            for lb_node in service_to_nodes["load_balancer"]:
                for vm_node in service_to_nodes["vm"]:
                    edge = LayoutEdge(
                        source=lb_node,
                        target=vm_node,
                        label=f"{step_counter}. VM Workload Distribution",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
    
    def _create_data_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create data flow connections with proper styling (requirement 14, 15)."""
        app_services = service_to_nodes.get("web_app", []) + service_to_nodes.get("function_app", []) + service_to_nodes.get("vm", [])
        
        for app_node in app_services:
            # Cache connections (bidirectional, dashed for cache pattern)
            for redis_node in service_to_nodes.get("redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label="🔄 High-Speed Cache Access",
                    style="dashed",
                    color="#FF6B35"  # Orange for cache traffic
                )
                graph.edges.append(edge)
            
            # Queue Storage connections (single direction for async patterns)
            for queue_node in service_to_nodes.get("queue_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=queue_node,
                    label="📨 Async Message Queue",
                    style="solid",
                    color="#4CAF50"  # Green for messaging
                )
                graph.edges.append(edge)
            
            # Table Storage connections (bidirectional for CRUD operations)
            for table_node in service_to_nodes.get("table_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=table_node,
                    label="📊 NoSQL Table Operations",
                    style="solid",
                    color="#4CAF50"
                )
                graph.edges.append(edge)
            
            # Storage Account connections (bidirectional for file operations)
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label="📁 Blob & File Storage",
                    style="solid",
                    color="#4CAF50"
                )
                graph.edges.append(edge)
            
            # Database connections (bidirectional for CRUD operations)
            for db_node in service_to_nodes.get("sql_database", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=db_node,
                    label="🗄️ Relational Database",
                    style="solid",
                    color="#9C27B0"  # Purple for database traffic
                )
                graph.edges.append(edge)
    
    def _create_security_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create security connections with clear labeling (requirement 4, 15)."""
        # Entra ID -> All compute services (single direction for authentication)
        entra_nodes = service_to_nodes.get("entra_id", [])
        compute_services = ["web_app", "function_app", "vm", "application_gateway"]
        
        for entra_node in entra_nodes:
            for service_type in compute_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=entra_node,
                        target=service_node,
                        label="Authentication",
                        style="dotted",
                        color="#795548"  # Brown for security
                    )
                    graph.edges.append(edge)
        
        # Key Vault -> Compute services (single direction for secrets)
        key_vault_nodes = service_to_nodes.get("key_vault", [])
        
        for kv_node in key_vault_nodes:
            for service_type in compute_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=kv_node,
                        target=service_node,
                        label="Secrets/Certs",
                        style="dashed",
                        color="#795548"
                    )
                    graph.edges.append(edge)
    
    def _create_monitoring_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create monitoring connections with dotted lines (requirement 14)."""
        monitoring_nodes = service_to_nodes.get("application_insights", []) + service_to_nodes.get("log_analytics", [])
        
        # All services send telemetry to monitoring (single direction, dotted)
        all_services = ["web_app", "function_app", "vm", "sql_database", "redis", "storage_account", "application_gateway"]
        
        for monitoring_node in monitoring_nodes:
            for service_type in all_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=monitoring_node,
                        label="Telemetry",
                        style="dotted",
                        color="#607D8B"  # Blue-grey for monitoring
                    )
                    graph.edges.append(edge)
    
    def _create_inter_region_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]], requirements: Requirements) -> None:
        """Create inter-region connections for HA scenarios (requirement 15)."""
        if requirements.ha_mode in ["multi-region", "active-active"]:
            # Storage replication between regions (bidirectional, dashed)
            storage_services = ["storage_account", "sql_database"]
            
            for service_type in storage_services:
                nodes = service_to_nodes.get(service_type, [])
                if len(nodes) >= 2:  # At least 2 instances for replication
                    primary_node = nodes[0]
                    secondary_node = nodes[1]
                    
                    edge = LayoutEdge(
                        source=primary_node,
                        target=secondary_node,
                        label="Geo-Replication",
                        style="dashed",
                        color="#FF9800"  # Orange for replication
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