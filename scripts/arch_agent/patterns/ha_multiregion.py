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
        """Organize services into logical groups with enhanced categorization (req 7)."""
        groups = {
            "edge": [],
            "identity": [],
            "security": [],
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
            
            # Edge services - Entry points and CDN (req 4, 16)
            if service_type in ["front_door", "cdn", "traffic_manager"]:
                groups["edge"].append(intent)
            
            # Identity services
            elif service_type in ["entra_id", "active_directory"]:
                groups["identity"].append(intent)
            
            # Security services (separate from identity for better organization - req 12)
            elif service_type in ["key_vault", "azure_firewall", "sentinel"]:
                groups["security"].append(intent)
            
            # Compute services - Application layer (req 3)
            elif service_type in ["vm", "web_app", "function_app", "app_service_plan", "aks", "container_instances"]:
                groups["region_compute"].append(intent)
            
            # Network services - Infrastructure layer (req 3, 16)
            elif service_type in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway", 
                                 "azure_firewall", "vpn_gateway", "expressroute", "vnet_peering"]:
                groups["region_network"].append(intent)
            
            # Storage services - Data layer (req 3, 4)
            elif service_type in ["storage_account", "disk", "queue_storage", "table_storage", "blob_storage", "file_storage"]:
                groups["region_storage"].append(intent)
            
            # Database services - Data layer (req 3, 4)
            elif service_type in ["sql_database", "redis", "cosmosdb", "mysql", "postgresql"]:
                groups["region_database"].append(intent)
            
            # Monitoring and observability services (req 11)
            elif service_type in ["log_analytics", "application_insights", "azure_monitor", "sentinel"]:
                groups["monitoring"].append(intent)
            
            else:
                # Default to region compute for unknown services
                groups["region_compute"].append(intent)
        
        return groups
    
    def _create_clusters(self, graph: LayoutGraph, service_groups: Dict[str, List[UserIntent]], requirements: Requirements) -> None:
        """Create cluster definitions with improved logical separation and visual hierarchy."""
        
        # Internet/Edge Layer (Top-Left) - Entry points (req 1, 3, 12)
        if len(service_groups["edge"]) > 0:
            graph.clusters["internet_edge"] = {
                "label": "🌐 Internet & Edge Services (DMZ)",
                "bgcolor": "#FFF5F5",  # Light red for internet/edge (DMZ zone)
                "pencolor": "#E53E3E",
                "penwidth": "3",
                "style": "bold,rounded,filled",
                "rank": "min",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            }
        
        # Identity/Security Layer (Left side) - Security and Identity (req 1, 3, 12)
        if len(service_groups["identity"]) > 0 or len(service_groups["security"]) > 0:
            graph.clusters["identity_security"] = {
                "label": "🔐 Identity & Security Services",
                "bgcolor": "#FFFAF0",  # Light orange for identity/security
                "pencolor": "#DD6B20",
                "penwidth": "3",
                "style": "bold,rounded,filled", 
                "rank": "min",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            }
        
        # Active Regions - Enhanced horizontal layout for better visibility (req 6, 13, 14)
        active_regions = requirements.regions[:2] if requirements.ha_mode in ["multi-region", "active-active"] else requirements.regions[:1]
        
        for i, region in enumerate(active_regions):
            cluster_name = f"active_region_{i+1}_{region.lower().replace(' ', '_')}"
            
            # HA/DR annotations and environment labeling (req 13, 14)
            ha_mode = "Active-Active" if requirements.ha_mode == "active-active" else f"Active-{i+1}"
            env_label = requirements.environment.upper() if requirements.environment else "PROD"
            
            # Main region cluster with enhanced styling and annotations
            graph.clusters[cluster_name] = {
                "label": f"🏢 {region} ({ha_mode}) [{env_label}]",
                "bgcolor": "#EBF5FB" if i == 0 else "#F0F8FF",  # Light blue variants for active regions
                "pencolor": "#3182CE",
                "penwidth": "3",
                "style": "bold,rounded,filled",
                "rank": "same" if len(active_regions) > 1 else "same",
                "fontcolor": "#1A202C",
                "fontsize": "14"
            }
            
            # Network Layer (Top of region) - Enhanced for networking core (req 3, 16)
            if any(intent.kind in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway",
                                   "azure_firewall", "expressroute", "vpn_gateway", "vnet_peering"] 
                   for intent in service_groups["region_network"]):
                graph.clusters[f"{cluster_name}_network"] = {
                    "label": "🌐 Network & Connectivity Layer",
                    "bgcolor": "#E9F7EF",  # Light green for networking (trusted zone)
                    "pencolor": "#38A169",
                    "penwidth": "2",
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "min",
                    "fontsize": "12"
                }
            
            # Application/Compute Layer (Middle of region) - Following requirement 3
            if len(service_groups["region_compute"]) > 0:
                graph.clusters[f"{cluster_name}_compute"] = {
                    "label": "⚙️ Application & Compute Services",
                    "bgcolor": "#FFFFFF", 
                    "pencolor": "#4A5568",
                    "penwidth": "2",
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "same",
                    "fontsize": "12"
                }
            
            # Data Layer (Bottom of region) - Following requirement 3
            if len(service_groups["region_storage"]) > 0 or len(service_groups["region_database"]) > 0:
                graph.clusters[f"{cluster_name}_data"] = {
                    "label": "💾 Data & Storage Layer",
                    "bgcolor": "#F3E8FF",  # Light purple for data (trusted zone)
                    "pencolor": "#805AD5",
                    "penwidth": "2",
                    "style": "dashed,rounded,filled",
                    "parent": cluster_name,
                    "rank": "max",
                    "fontsize": "12"
                }
        
        # Standby Region (Bottom) - Enhanced DR annotations (req 6, 13)
        if len(requirements.regions) > 2 or requirements.ha_mode == "active-passive":
            standby_region = requirements.regions[-1] if len(requirements.regions) > 2 else requirements.regions[1]
            cluster_name = f"standby_region_{standby_region.lower().replace(' ', '_')}"
            
            graph.clusters[cluster_name] = {
                "label": f"🔄 Standby Region: {standby_region} (Passive) [DR]",
                "bgcolor": "#F8F9FA",  # Light gray for standby
                "pencolor": "#6C757D",
                "penwidth": "2",
                "style": "bold,rounded,dashed,filled",
                "rank": "max",
                "fontcolor": "#495057",
                "fontsize": "14"
            }
            
            # Simplified standby components with DR annotations (req 13)
            graph.clusters[f"{cluster_name}_backup"] = {
                "label": "💾 Backup & DR Storage",
                "bgcolor": "#F8D7DA",  # Light red for DR
                "pencolor": "#DC3545",
                "penwidth": "2",
                "style": "dashed,rounded,filled",
                "parent": cluster_name,
                "fontsize": "12"
            }
        
        # Monitoring & Observability (Enhanced for comprehensive observability - req 11)
        if len(service_groups["monitoring"]) > 0:
            graph.clusters["monitoring_observability"] = {
                "label": "📊 Monitoring & Observability (SIEM)",
                "bgcolor": "#FDF4E3",  # Light yellow for monitoring
                "pencolor": "#D69E2E",
                "penwidth": "3",
                "style": "bold,rounded,filled",
                "rank": "same",
                "fontcolor": "#1A202C",
                "fontsize": "14"
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
        
        # Identity and Security services (Left side) - Security layer (req 12)
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
        
        # Security services (also in identity_security cluster)
        for intent in service_groups["security"]:
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
        """Create primary traffic flow with clear numbering and minimal crossings (req 2, 4, 8)."""
        step_counter = 1
        
        # Step 1: Internet -> Front Door (entry point - req 8)
        if "front_door" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                # Connect to Application Gateway if available
                if "application_gateway" in service_to_nodes:
                    for ag_node in service_to_nodes["application_gateway"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=ag_node,
                            label=f"{step_counter}",
                            style="primary",
                            color="#0078D4"  # Azure primary blue
                        )
                        graph.edges.append(edge)
                        step_counter += 1
                
                # Direct connection to Web App if no App Gateway
                elif "web_app" in service_to_nodes:
                    for wa_node in service_to_nodes["web_app"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=wa_node,
                            label=f"{step_counter}",
                            style="primary",
                            color="#0078D4"
                        )
                        graph.edges.append(edge)
                        step_counter += 1
        
        # Step 2: Application Gateway -> Azure Firewall (security layer - req 8, 16)
        if "application_gateway" in service_to_nodes and "azure_firewall" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for fw_node in service_to_nodes["azure_firewall"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=fw_node,
                        label=f"{step_counter}",
                        style="primary",
                        color="#0078D4"
                    )
                    graph.edges.append(edge)
                    step_counter += 1
        
        # Step 3: Firewall -> Load Balancer (routing layer - req 8)
        if "azure_firewall" in service_to_nodes and "load_balancer" in service_to_nodes:
            for fw_node in service_to_nodes["azure_firewall"]:
                for lb_node in service_to_nodes["load_balancer"]:
                    edge = LayoutEdge(
                        source=fw_node,
                        target=lb_node,
                        label=f"{step_counter}",
                        style="primary",
                        color="#0078D4"
                    )
                    graph.edges.append(edge)
                    step_counter += 1
        
        # Step 4: Load Balancer -> Applications (compute layer - req 8)
        if "load_balancer" in service_to_nodes:
            for lb_node in service_to_nodes["load_balancer"]:
                # Connect to web apps
                for wa_node in service_to_nodes.get("web_app", []):
                    edge = LayoutEdge(
                        source=lb_node,
                        target=wa_node,
                        label=f"{step_counter}",
                        style="primary",
                        color="#0078D4"
                    )
                    graph.edges.append(edge)
                    step_counter += 1
                
                # Connect to VMs
                for vm_node in service_to_nodes.get("vm", []):
                    edge = LayoutEdge(
                        source=lb_node,
                        target=vm_node,
                        label=f"{step_counter}",
                        style="primary",
                        color="#0078D4"
                    )
                    graph.edges.append(edge)
                    step_counter += 1
    
    def _create_data_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create data flow connections with proper styling (req 8, 14, 15)."""
        app_services = service_to_nodes.get("web_app", []) + service_to_nodes.get("function_app", []) + service_to_nodes.get("vm", [])
        step_counter = 5  # Continue from previous workflow steps
        
        for app_node in app_services:
            # Step 5: Applications -> Cache (Redis) - Fast data access (req 4, 8)
            for redis_node in service_to_nodes.get("redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label=f"{step_counter}",
                    style="data_flow",
                    color="#107C10"  # Azure green for data operations
                )
                graph.edges.append(edge)
                step_counter += 1
            
            # Step 6: Applications -> Queue Storage - Async messaging (req 4, 8)
            for queue_node in service_to_nodes.get("queue_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=queue_node,
                    label=f"{step_counter}",
                    style="secondary",
                    color="#FF8C00"  # Azure orange for async patterns
                )
                graph.edges.append(edge)
                step_counter += 1
            
            # Step 7: Applications -> Table Storage - NoSQL operations (req 4, 8)
            for table_node in service_to_nodes.get("table_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=table_node,
                    label=f"{step_counter}",
                    style="data_flow",
                    color="#107C10"
                )
                graph.edges.append(edge)
                step_counter += 1
            
            # Step 8: Applications -> Storage Account - File/Blob operations (req 8)
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label=f"{step_counter}",
                    style="data_flow",
                    color="#107C10"
                )
                graph.edges.append(edge)
                step_counter += 1
            
            # Step 9: Applications -> Databases - SQL operations (req 8)
            for db_node in service_to_nodes.get("sql_database", []) + service_to_nodes.get("cosmosdb", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=db_node,
                    label=f"{step_counter}",
                    style="data_flow",
                    color="#107C10"
                )
                graph.edges.append(edge)
                step_counter += 1
    
    def _create_security_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create security connections with clear labeling (req 14, 15)."""
        # Entra ID -> All compute services (authentication flows)
        entra_nodes = service_to_nodes.get("entra_id", [])
        compute_services = ["web_app", "function_app", "vm", "application_gateway"]
        
        for entra_node in entra_nodes:
            for service_type in compute_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=entra_node,
                        target=service_node,
                        label="Auth",
                        style="ctrl",
                        color="#6B7280"  # Gray for control connections
                    )
                    graph.edges.append(edge)
        
        # Key Vault -> Compute services (secrets/certificates)
        key_vault_nodes = service_to_nodes.get("key_vault", [])
        
        for kv_node in key_vault_nodes:
            for service_type in compute_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=kv_node,
                        target=service_node,
                        label="Secrets",
                        style="ctrl",
                        color="#6B7280"
                    )
                    graph.edges.append(edge)
        
        # Azure Firewall -> Network resources (security policies - req 16)
        firewall_nodes = service_to_nodes.get("azure_firewall", [])
        network_services = ["vnet", "load_balancer", "application_gateway"]
        
        for fw_node in firewall_nodes:
            for service_type in network_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=fw_node,
                        target=service_node,
                        label="Policy",
                        style="ctrl",
                        color="#6B7280"
                    )
                    graph.edges.append(edge)
    
    def _create_monitoring_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """Create comprehensive monitoring connections for observability (req 11, 14)."""
        # Enhanced monitoring services (req 11)
        monitoring_nodes = (service_to_nodes.get("application_insights", []) + 
                          service_to_nodes.get("log_analytics", []) + 
                          service_to_nodes.get("azure_monitor", []))
        
        # Sentinel for SIEM (req 11)
        sentinel_nodes = service_to_nodes.get("sentinel", [])
        
        # All services send telemetry to monitoring
        all_services = ["web_app", "function_app", "vm", "sql_database", "cosmosdb", "redis", 
                       "storage_account", "application_gateway", "azure_firewall", "front_door"]
        
        for monitoring_node in monitoring_nodes:
            for service_type in all_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=monitoring_node,
                        label="Logs",
                        style="monitoring",
                        color="#FF8C00"  # Azure orange for monitoring
                    )
                    graph.edges.append(edge)
        
        # Sentinel connections for security monitoring (req 11)
        for sentinel_node in sentinel_nodes:
            security_services = ["azure_firewall", "entra_id", "key_vault", "application_gateway"]
            for service_type in security_services:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=sentinel_node,
                        label="Security Events",
                        style="monitoring",
                        color="#D13438"  # Azure red for security
                    )
                    graph.edges.append(edge)
    
    def _create_inter_region_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]], requirements: Requirements) -> None:
        """Create inter-region connections for HA/DR scenarios (req 13, 15)."""
        # Active-Active or Multi-Region connections
        if requirements.ha_mode in ["multi-region", "active-active"]:
            # Data replication between active regions
            storage_services = ["storage_account", "sql_database", "cosmosdb"]
            
            for service_type in storage_services:
                nodes = service_to_nodes.get(service_type, [])
                if len(nodes) >= 2:  # At least 2 instances for replication
                    primary_node = nodes[0]
                    secondary_node = nodes[1]
                    
                    edge = LayoutEdge(
                        source=primary_node,
                        target=secondary_node,
                        label="Active Replication",
                        style="secondary",
                        color="#107C10"  # Azure green for active replication
                    )
                    graph.edges.append(edge)
        
        # Active-Passive or DR connections (req 13)
        elif requirements.ha_mode == "active-passive":
            # DR backup connections
            storage_services = ["storage_account", "sql_database", "cosmosdb"]
            
            for service_type in storage_services:
                nodes = service_to_nodes.get(service_type, [])
                if len(nodes) >= 2:
                    active_node = nodes[0]
                    dr_node = nodes[1]
                    
                    edge = LayoutEdge(
                        source=active_node,
                        target=dr_node,
                        label="DR Backup",
                        style="dr_connection",
                        color="#D13438"  # Azure red for DR
                    )
                    graph.edges.append(edge)
        
        # ExpressRoute and VPN connectivity between regions (req 16)
        expressroute_nodes = service_to_nodes.get("expressroute", [])
        vpn_nodes = service_to_nodes.get("vpn_gateway", [])
        
        if expressroute_nodes:
            for i, er_node in enumerate(expressroute_nodes):
                if i < len(expressroute_nodes) - 1:  # Connect to next region
                    next_er_node = expressroute_nodes[i + 1]
                    edge = LayoutEdge(
                        source=er_node,
                        target=next_er_node,
                        label="Private Peering",
                        style="primary",
                        color="#0078D4"
                    )
                    graph.edges.append(edge)
        
        if vpn_nodes:
            for i, vpn_node in enumerate(vpn_nodes):
                if i < len(vpn_nodes) - 1:  # Connect to next region  
                    next_vpn_node = vpn_nodes[i + 1]
                    edge = LayoutEdge(
                        source=vpn_node,
                        target=next_vpn_node,
                        label="Site-to-Site VPN",
                        style="secondary",
                        color="#FF8C00"
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