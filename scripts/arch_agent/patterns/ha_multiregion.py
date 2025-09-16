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
    
    def apply_pattern_with_ai_grouping(self, requirements: Requirements, resolved_intents: List[UserIntent], ai_service_groups: Dict[str, List[UserIntent]]) -> LayoutGraph:
        """
        Apply the HA Multi-Region pattern with AI-optimized service grouping.
        Implements requirement 8: AI Reasoning and Dynamic Pattern Selection.
        
        Args:
            requirements: Architecture requirements
            resolved_intents: List of services including dependencies
            ai_service_groups: AI-optimized service grouping
            
        Returns:
            LayoutGraph with AI-enhanced layout
        """
        graph = LayoutGraph()
        
        # Use AI-optimized service groups, with fallback mapping
        service_groups = self._map_ai_groups_to_pattern(ai_service_groups, resolved_intents, requirements)
        
        # Create enhanced clusters with AI grouping insights
        self._create_clusters(graph, service_groups, requirements)
        
        # Place nodes in appropriate clusters
        self._place_nodes(graph, service_groups, requirements)
        
        # Create enhanced edges with AI-informed flow optimization
        self._create_edges(graph, service_groups, requirements)
        
        return graph
    
    def _map_ai_groups_to_pattern(self, ai_groups: Dict[str, List[UserIntent]], resolved_intents: List[UserIntent], requirements: Requirements) -> Dict[str, List[UserIntent]]:
        """
        Map AI service groups to the pattern's expected group structure.
        
        Args:
            ai_groups: AI-optimized service groups
            resolved_intents: All resolved services
            requirements: Architecture requirements
            
        Returns:
            Mapped service groups compatible with the pattern
        """
        # Initialize pattern groups
        pattern_groups = {
            "edge": [],
            "identity": [],
            "region_compute": [],
            "region_network": [],
            "region_storage": [],
            "region_database": [],
            "monitoring": []
        }
        
        # Map AI groups to pattern groups
        ai_to_pattern_mapping = {
            "internet_edge": "edge",
            "identity_security": "identity", 
            "active_region_compute": "region_compute",
            "active_region_network": "region_network",
            "active_region_data": "region_storage",  # Will be split later
            "monitoring": "monitoring",
            "devops": "region_compute"  # DevOps goes to compute for now
        }
        
        # Apply the mapping
        for ai_group_name, services in ai_groups.items():
            pattern_group = ai_to_pattern_mapping.get(ai_group_name, "region_compute")
            pattern_groups[pattern_group].extend(services)
        
        # Split data services into storage and database
        data_services = pattern_groups["region_storage"]
        pattern_groups["region_storage"] = []
        pattern_groups["region_database"] = []
        
        for service in data_services:
            if service.kind in ["sql_database", "redis", "cosmos_db", "mysql", "postgresql"]:
                pattern_groups["region_database"].append(service)
            else:
                pattern_groups["region_storage"].append(service)
        
        # Ensure all services are included (fallback for any missed services) 
        # Also add edge_services and identity_services from requirements
        if requirements:
            for edge_service in requirements.edge_services:
                edge_intent = UserIntent(kind=edge_service, name=None)
                if edge_intent not in pattern_groups["edge"]:
                    pattern_groups["edge"].append(edge_intent)
            
            for identity_service in requirements.identity_services:
                identity_intent = UserIntent(kind=identity_service, name=None)
                if identity_intent not in pattern_groups["identity"]:
                    pattern_groups["identity"].append(identity_intent)
        
        included_services = set()
        for group_services in pattern_groups.values():
            for service in group_services:
                included_services.add(id(service))
        
        for service in resolved_intents:
            if id(service) not in included_services:
                # Default fallback to appropriate group
                if service.kind in ["front_door", "cdn"]:
                    pattern_groups["edge"].append(service)
                elif service.kind in ["entra_id", "key_vault"]:
                    pattern_groups["identity"].append(service)
                elif service.kind in ["log_analytics", "application_insights"]:
                    pattern_groups["monitoring"].append(service)
                else:
                    pattern_groups["region_compute"].append(service)
        
        return pattern_groups
    
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
        """
        Create cluster definitions implementing requirements 1, 3, 5, 7, and 10.
        Creates distinct clusters for: Internet Edge, Identity Security, Active Regions, 
        Standby Region, Monitoring, Network, Compute, Data, Integration, Security, and DevOps.
        """
        
        # Enhanced cluster styling for visual hierarchy (requirement 3 & 10)
        cluster_styles = {
            "internet_edge": {
                "bgcolor": "#E3F2FD",     # Light blue for internet/edge 
                "pencolor": "#1976D2",
                "penwidth": "3",
                "style": "bold,rounded,filled",
                "fontcolor": "#0D47A1",
                "fontsize": "16",
                "rank": "min"
            },
            "identity_security": {
                "bgcolor": "#FFF3E0",     # Light orange for identity/security
                "pencolor": "#F57C00", 
                "penwidth": "3",
                "style": "bold,rounded,filled",
                "fontcolor": "#E65100",
                "fontsize": "14",
                "rank": "min"
            },
            "active_region": {
                "bgcolor": "#E8F5E8",     # Light green for active regions
                "pencolor": "#388E3C",
                "penwidth": "4", 
                "style": "bold,rounded,filled",
                "fontcolor": "#1B5E20",
                "fontsize": "16",
                "rank": "same"
            },
            "standby_region": {
                "bgcolor": "#F3E5F5",     # Light purple for standby region
                "pencolor": "#7B1FA2",
                "penwidth": "3",
                "style": "dashed,rounded,filled",
                "fontcolor": "#4A148C", 
                "fontsize": "14",
                "rank": "same"
            },
            "monitoring": {
                "bgcolor": "#FFF8E1",     # Light yellow for monitoring
                "pencolor": "#F9A825",
                "penwidth": "2",
                "style": "bold,rounded,filled", 
                "fontcolor": "#F57F17",
                "fontsize": "12",
                "rank": "max"
            },
            "network": {
                "bgcolor": "#F1F8E9",     # Light green for network
                "pencolor": "#689F38", 
                "penwidth": "2",
                "style": "rounded,filled",
                "fontcolor": "#33691E",
                "fontsize": "12",
                "rank": "min"
            },
            "compute": {
                "bgcolor": "#FFFFFF",     # White for compute (clean)
                "pencolor": "#5D4037",
                "penwidth": "2", 
                "style": "rounded,filled",
                "fontcolor": "#3E2723",
                "fontsize": "12",
                "rank": "same"
            },
            "data": {
                "bgcolor": "#FAFAFA",     # Very light gray for data
                "pencolor": "#424242",
                "penwidth": "2",
                "style": "rounded,filled",
                "fontcolor": "#212121", 
                "fontsize": "12",
                "rank": "max"
            },
            "integration": {
                "bgcolor": "#E0F2F1",     # Light teal for integration
                "pencolor": "#00695C",
                "penwidth": "2",
                "style": "rounded,filled",
                "fontcolor": "#004D40",
                "fontsize": "12",
                "rank": "same"
            },
            "devops": {
                "bgcolor": "#E8EAF6",     # Light indigo for DevOps
                "pencolor": "#303F9F",
                "penwidth": "2", 
                "style": "rounded,filled",
                "fontcolor": "#1A237E",
                "fontsize": "11",
                "rank": "max"
            }
        }
        
        # 1. Internet Edge Layer (Top-Left) - Entry points (requirement 3)
        if len(service_groups["edge"]) > 0:
            style = cluster_styles["internet_edge"]
            graph.clusters["internet_edge"] = {
                "label": "🌐 Internet & Edge Services",
                **style
            }
        
        # 2. Identity Security Layer (Left side, below edge) - requirement 3
        if len(service_groups["identity"]) > 0:
            style = cluster_styles["identity_security"] 
            graph.clusters["identity_security"] = {
                "label": "🔐 Identity & Security",
                **style
            }
        
        # 3. Monitoring Layer (Bottom) - Global monitoring services
        if len(service_groups["monitoring"]) > 0:
            style = cluster_styles["monitoring"]
            graph.clusters["monitoring"] = {
                "label": "📊 Monitoring & Observability", 
                **style
            }
        
        # 4. DevOps Layer (Bottom-Right) - CI/CD and automation
        devops_services = [s for s in service_groups.get("region_compute", []) if s.kind in ["devops", "pipelines", "artifacts"]]
        if devops_services:
            style = cluster_styles["devops"]
            graph.clusters["devops"] = {
                "label": "🚀 DevOps & Automation",
                **style
            }
        
        # 5. Active Regions - requirement 5: separated clusters with horizontal alignment
        active_regions = requirements.regions[:2] if requirements.ha_mode in ["multi-region", "active-active"] else requirements.regions[:1]
        
        for i, region in enumerate(active_regions):
            cluster_name = f"active_region_{i+1}_{region.lower().replace(' ', '_')}"
            
            # Main region cluster with enhanced styling
            style = cluster_styles["active_region"]
            if i > 0:  # Secondary regions get slightly different styling
                style = style.copy()
                style["bgcolor"] = "#F1F8E9"  # Slightly different green
                style["pencolor"] = "#558B2F"
            
            graph.clusters[cluster_name] = {
                "label": f"🏢 Active Region {i+1}: {region}",
                **style
            }
            
            # 6. Network Layer (Top of region) - requirement 1 & 3
            if any(intent.kind in ["vnet", "subnet", "nsg", "public_ip", "load_balancer", "application_gateway"] 
                   for intent in service_groups["region_network"]):
                network_style = cluster_styles["network"]
                graph.clusters[f"{cluster_name}_network"] = {
                    "label": "🌐 Network Infrastructure",
                    "parent": cluster_name,
                    **network_style
                }
            
            # 7. Compute Layer (Middle of region) - requirement 3
            if len(service_groups["region_compute"]) > 0:
                compute_style = cluster_styles["compute"] 
                graph.clusters[f"{cluster_name}_compute"] = {
                    "label": "⚙️ Application & Compute",
                    "parent": cluster_name,
                    **compute_style
                }
            
            # 8. Data Layer (Bottom of region) - requirement 3
            if len(service_groups["region_storage"]) > 0 or len(service_groups["region_database"]) > 0:
                data_style = cluster_styles["data"]
                graph.clusters[f"{cluster_name}_data"] = {
                    "label": "💾 Data & Storage", 
                    "parent": cluster_name,
                    **data_style
                }
            
            # 9. Integration Layer (for queues, service bus, etc.)
            integration_services = [s for s in service_groups.get("region_storage", []) if s.kind in ["queue_storage", "service_bus", "event_hub"]]
            if integration_services:
                integration_style = cluster_styles["integration"] 
                graph.clusters[f"{cluster_name}_integration"] = {
                    "label": "🔄 Integration & Messaging",
                    "parent": cluster_name,
                    **integration_style
                }
        
        # 10. Standby Region (if applicable) - requirement 5
        if requirements.ha_mode in ["active-passive"] and len(requirements.regions) > 1:
            standby_region = requirements.regions[1]
            standby_cluster_name = f"standby_region_{standby_region.lower().replace(' ', '_')}"
            
            style = cluster_styles["standby_region"]
            graph.clusters[standby_cluster_name] = {
                "label": f"💤 Standby Region: {standby_region}",
                **style
            }
            
            # Add minimal standby infrastructure
            if len(service_groups["region_storage"]) > 0 or len(service_groups["region_database"]) > 0:
                data_style = cluster_styles["data"].copy()
                data_style["style"] = "dashed,rounded,filled"  # Dashed for standby
                graph.clusters[f"{standby_cluster_name}_data"] = {
                    "label": "💾 Standby Data",
                    "parent": standby_cluster_name,
                    **data_style
                }
        
        # 11. Security Layer (Global) - Cross-cutting security concerns
        security_services = [s for s in service_groups.get("identity", []) if s.kind in ["firewall", "waf", "ddos_protection"]]
        if security_services:
            security_style = cluster_styles["identity_security"].copy()
            security_style["label"] = "🛡️ Security Layer"
            graph.clusters["security_global"] = security_style
    
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
        """
        Create edges with enhanced workflow numbering, clear labeling, and proper styling.
        Implements requirements 2, 4, 9, 12, 14, 15: Minimal crossings, workflow numbering,
        connection labeling, pattern templates, line types, and directional clarity.
        """
        # Create a mapping of service types to node IDs for easier edge creation
        service_to_nodes = {}
        for node in graph.nodes:
            service_type = node.service_type
            if service_type not in service_to_nodes:
                service_to_nodes[service_type] = []
            service_to_nodes[service_type].append(node.id)
        
        # Reset step counter for workflow numbering (requirement 4)
        self.edge_step_counter = 1
        
        # Primary traffic flow: Internet -> Edge -> App -> Data (requirements 2, 4, 14, 15)
        self._create_primary_traffic_flow(graph, service_to_nodes)
        
        # Security connections: Identity -> Compute services (requirement 15)
        self._create_security_connections(graph, service_to_nodes)
        
        # Data flow: Applications -> Caches -> Databases (requirements 14, 15)
        self._create_data_flow(graph, service_to_nodes)
        
        # Monitoring connections: All services -> Monitoring (requirement 14)
        self._create_monitoring_connections(graph, service_to_nodes)
        
        # Inter-region connections for HA scenarios (requirement 15)
        self._create_inter_region_connections(graph, service_to_nodes, requirements)
        
        # Integration and messaging flows (requirement 4)
        self._create_integration_flows(graph, service_to_nodes)
    
    def _create_primary_traffic_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """
        Create primary traffic flow with clear numbering and minimal crossings.
        Implements requirements 2, 4: Minimal crossings and workflow numbering.
        """
        # Step 1: Internet → Front Door (Entry point)
        if "front_door" in service_to_nodes:
            for fd_node in service_to_nodes["front_door"]:
                # Connect to Application Gateway if available
                if "application_gateway" in service_to_nodes:
                    for ag_node in service_to_nodes["application_gateway"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=ag_node,
                            label=f"Step {self.edge_step_counter}: Internet → Front Door → App Gateway",
                            style="solid",
                            color="#1976D2"  # Strong blue for primary traffic
                        )
                        graph.edges.append(edge)
                        self.edge_step_counter += 1
                
                # Direct connection to Web App if no App Gateway
                elif "web_app" in service_to_nodes:
                    for wa_node in service_to_nodes["web_app"]:
                        edge = LayoutEdge(
                            source=fd_node,
                            target=wa_node,
                            label=f"Step {self.edge_step_counter}: Internet → Front Door → Web App",
                            style="solid",
                            color="#1976D2"
                        )
                        graph.edges.append(edge)
                        self.edge_step_counter += 1
        
        # Step 2: Application Gateway → Web Apps (Load balancing)
        if "application_gateway" in service_to_nodes and "web_app" in service_to_nodes:
            for ag_node in service_to_nodes["application_gateway"]:
                for wa_node in service_to_nodes["web_app"]:
                    edge = LayoutEdge(
                        source=ag_node,
                        target=wa_node,
                        label=f"Step {self.edge_step_counter}: Load Balanced HTTPS",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
                    self.edge_step_counter += 1
        
        # Step 3: Web Apps → Function Apps (API calls)
        if "web_app" in service_to_nodes and "function_app" in service_to_nodes:
            for wa_node in service_to_nodes["web_app"]:
                for fa_node in service_to_nodes["function_app"][:1]:  # Connect to first function app to minimize crossings
                    edge = LayoutEdge(
                        source=wa_node,
                        target=fa_node,
                        label=f"Step {self.edge_step_counter}: API Calls",
                        style="solid",
                        color="#2E7D32"  # Green for API traffic
                    )
                    graph.edges.append(edge)
                    self.edge_step_counter += 1
        
        # Step 4: Load Balancer → VMs (if present)
        if "load_balancer" in service_to_nodes and "vm" in service_to_nodes:
            for lb_node in service_to_nodes["load_balancer"]:
                for vm_node in service_to_nodes["vm"][:2]:  # Limit connections to reduce crossings
                    edge = LayoutEdge(
                        source=lb_node,
                        target=vm_node,
                        label=f"Step {self.edge_step_counter}: VM Traffic",
                        style="solid",
                        color="#1976D2"
                    )
                    graph.edges.append(edge)
                    self.edge_step_counter += 1
    
    def _create_data_flow(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """
        Create data flow connections with proper styling.
        Implements requirements 14, 15: Line types and directional clarity.
        """
        app_services = (service_to_nodes.get("web_app", []) + 
                       service_to_nodes.get("function_app", []) + 
                       service_to_nodes.get("vm", []))
        
        for app_node in app_services:
            # Cache connections (bidirectional, dashed for cache pattern)
            for redis_node in service_to_nodes.get("redis", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=redis_node,
                    label=f"Step {self.edge_step_counter}: Cache Read/Write",
                    style="dashed",  # Dashed for cache patterns
                    color="#FF6B35"  # Orange for cache traffic
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
            
            # Queue Storage connections (single direction for async patterns)
            for queue_node in service_to_nodes.get("queue_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=queue_node,
                    label=f"Step {self.edge_step_counter}: Async Messages",
                    style="dashed",  # Dashed for async patterns
                    color="#E91E63"  # Pink for messaging
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
            
            # Table Storage connections
            for table_node in service_to_nodes.get("table_storage", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=table_node,
                    label=f"Step {self.edge_step_counter}: NoSQL Data",
                    style="solid",
                    color="#795548"  # Brown for NoSQL data
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
            
            # SQL Database connections
            for sql_node in service_to_nodes.get("sql_database", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=sql_node,
                    label=f"Step {self.edge_step_counter}: SQL Queries",
                    style="solid",
                    color="#3F51B5"  # Indigo for SQL
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
            
            # Storage Account connections
            for storage_node in service_to_nodes.get("storage_account", []):
                edge = LayoutEdge(
                    source=app_node,
                    target=storage_node,
                    label=f"Step {self.edge_step_counter}: Blob Storage",
                    style="solid",
                    color="#607D8B"  # Blue gray for blob storage
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
    
    def _create_security_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """
        Create security connections with dotted lines.
        Implements requirement 14: Line types for security connections.
        """
        # Identity → All compute services (authentication)
        for entra_node in service_to_nodes.get("entra_id", []):
            for service_type in ["web_app", "function_app", "vm"]:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=entra_node,
                        target=service_node,
                        label="Authentication",
                        style="dotted",  # Dotted for security/control
                        color="#9C27B0"  # Purple for security
                    )
                    graph.edges.append(edge)
        
        # Key Vault → All services (secrets)
        for kv_node in service_to_nodes.get("key_vault", []):
            for service_type in ["web_app", "function_app", "vm", "sql_database"]:
                for service_node in service_to_nodes.get(service_type, [])[:1]:  # Limit to reduce clutter
                    edge = LayoutEdge(
                        source=kv_node,
                        target=service_node,
                        label="Secrets",
                        style="dotted",  # Dotted for security/control
                        color="#FF5722"  # Deep orange for secrets
                    )
                    graph.edges.append(edge)
    
    def _create_monitoring_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """
        Create monitoring connections with dotted lines.
        Implements requirement 14: Line types for monitoring connections.
        """
        # All services → Log Analytics (telemetry)
        for log_node in service_to_nodes.get("log_analytics", []):
            for service_type in ["web_app", "function_app", "vm", "sql_database", "redis"]:
                for service_node in service_to_nodes.get(service_type, [])[:1]:  # Limit to reduce clutter
                    edge = LayoutEdge(
                        source=service_node,
                        target=log_node,
                        label="Telemetry",
                        style="dotted",  # Dotted for monitoring
                        color="#4CAF50"  # Green for monitoring
                    )
                    graph.edges.append(edge)
        
        # Application Insights connections
        for ai_node in service_to_nodes.get("application_insights", []):
            for service_type in ["web_app", "function_app"]:
                for service_node in service_to_nodes.get(service_type, []):
                    edge = LayoutEdge(
                        source=service_node,
                        target=ai_node,
                        label="App Telemetry",
                        style="dotted",  # Dotted for monitoring
                        color="#8BC34A"  # Light green for app monitoring
                    )
                    graph.edges.append(edge)
    
    def _create_inter_region_connections(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]], requirements: Requirements) -> None:
        """
        Create inter-region connections for HA scenarios.
        Implements requirement 15: Directional clarity for HA flows.
        """
        if requirements.ha_mode in ["multi-region", "active-active"]:
            # Database replication (if multiple SQL databases exist)
            sql_nodes = service_to_nodes.get("sql_database", [])
            if len(sql_nodes) > 1:
                for i in range(0, len(sql_nodes) - 1):
                    edge = LayoutEdge(
                        source=sql_nodes[i],
                        target=sql_nodes[i + 1],
                        label="Geo-Replication",
                        style="dashed",  # Dashed for replication
                        color="#673AB7"  # Deep purple for replication
                    )
                    graph.edges.append(edge)
            
            # Storage account replication
            storage_nodes = service_to_nodes.get("storage_account", [])
            if len(storage_nodes) > 1:
                for i in range(0, len(storage_nodes) - 1):
                    edge = LayoutEdge(
                        source=storage_nodes[i],
                        target=storage_nodes[i + 1],
                        label="Storage Sync",
                        style="dashed",  # Dashed for async replication
                        color="#FF9800"  # Orange for storage sync
                    )
                    graph.edges.append(edge)
    
    def _create_integration_flows(self, graph: LayoutGraph, service_to_nodes: Dict[str, List[str]]) -> None:
        """
        Create integration and messaging flows.
        Implements requirement 4: Connection labeling for integration patterns.
        """
        # Function Apps → Queue Storage (event processing)
        for fa_node in service_to_nodes.get("function_app", []):
            for queue_node in service_to_nodes.get("queue_storage", []):
                edge = LayoutEdge(
                    source=queue_node,
                    target=fa_node,
                    label=f"Step {self.edge_step_counter}: Event Trigger",
                    style="dashed",  # Dashed for event-driven
                    color="#E91E63"  # Pink for events
                )
                graph.edges.append(edge)
                self.edge_step_counter += 1
    
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