"""
Service catalog with dependency inference for Azure services.
Handles automatic dependency resolution and prompting for missing configurations.
"""
from typing import List, Dict, Any, Optional
from .schemas import ServiceDefinition, ServiceDependency, UserIntent


class ServiceCatalog:
    """Service catalog with dependency inference and configuration prompts."""
    
    def __init__(self):
        self._catalog = self._build_catalog()
    
    def _build_catalog(self) -> Dict[str, ServiceDefinition]:
        """Build the service catalog with dependencies and prompts."""
        return {
            # Compute Services
            "vm": ServiceDefinition(
                name="Virtual Machine",
                category="compute",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                    ServiceDependency(service_type="subnet", required=True),
                    ServiceDependency(service_type="nsg", required=True),
                    ServiceDependency(service_type="nic", required=True),
                    ServiceDependency(service_type="disk", required=True),
                    ServiceDependency(service_type="public_ip", required=False),
                ],
                prompts=[
                    "What operating system? (windows/linux)",
                    "What VM size? (Standard_B2s, Standard_D2s_v3, etc.)",
                    "Do you need public internet access? (yes/no)",
                    "Do you need managed disks for data? (yes/no)"
                ],
                diagram_class="VirtualMachines"
            ),
            
            "web_app": ServiceDefinition(
                name="App Service",
                category="compute",
                dependencies=[
                    ServiceDependency(service_type="app_service_plan", required=True),
                ],
                prompts=[
                    "What runtime stack? (.NET, Node.js, Python, Java, PHP)",
                    "What pricing tier? (F1, B1, S1, P1v2, etc.)",
                    "Do you need custom domain? (yes/no)",
                    "Do you need SSL certificate? (yes/no)"
                ],
                diagram_class="AppServices"
            ),
            
            "function_app": ServiceDefinition(
                name="Function App",
                category="compute",
                dependencies=[
                    ServiceDependency(service_type="app_service_plan", required=True),
                    ServiceDependency(service_type="storage_account", required=True),
                ],
                prompts=[
                    "What runtime? (.NET, Node.js, Python, Java, PowerShell)",
                    "What hosting plan? (Consumption, Premium, Dedicated)",
                ],
                diagram_class="FunctionApps"
            ),
            
            # Storage Services
            "storage_account": ServiceDefinition(
                name="Storage Account",
                category="storage",
                dependencies=[],
                prompts=[
                    "What performance tier? (Standard, Premium)",
                    "What replication? (LRS, GRS, RA-GRS, ZRS)",
                    "What services needed? (blob, queue, table, file)"
                ],
                diagram_class="StorageAccounts"
            ),
            
            "queue_storage": ServiceDefinition(
                name="Queue Storage",
                category="storage",
                dependencies=[
                    ServiceDependency(service_type="storage_account", required=True),
                ],
                prompts=[
                    "What visibility timeout? (default: 30 seconds)",
                    "What message TTL? (default: 7 days)",
                    "Do you need encryption at rest? (yes/no)"
                ],
                diagram_class="QueuesStorage"
            ),
            
            "table_storage": ServiceDefinition(
                name="Table Storage",
                category="storage",
                dependencies=[
                    ServiceDependency(service_type="storage_account", required=True),
                ],
                prompts=[
                    "What consistency level needed? (Strong, Eventual)",
                    "Do you need encryption at rest? (yes/no)",
                    "What access tier? (Hot, Cool, Archive)"
                ],
                diagram_class="TableStorage"
            ),
            
            "redis": ServiceDefinition(
                name="Azure Cache for Redis",
                category="database",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=False),
                    ServiceDependency(service_type="subnet", required=False),
                ],
                prompts=[
                    "What tier? (Basic, Standard, Premium)",
                    "What size? (C0, C1, C2, C3, C4, C5, C6)",
                    "Do you need VNet integration? (yes/no)"
                ],
                diagram_class="RedisCaches"
            ),
            
            "cosmosdb": ServiceDefinition(
                name="Azure Cosmos DB",
                category="database",
                dependencies=[],
                prompts=[
                    "What API? (SQL, MongoDB, Cassandra, Gremlin, Table)",
                    "What consistency level? (Strong, Bounded Staleness, Session, Consistent Prefix, Eventual)",
                    "Do you need multi-region writes? (yes/no)"
                ],
                diagram_class="CosmosDb"
            ),
            
            # Database Services
            "sql_database": ServiceDefinition(
                name="Azure SQL Database",
                category="database",
                dependencies=[],
                prompts=[
                    "What service tier? (Basic, Standard, Premium, General Purpose, Business Critical)",
                    "What compute size? (S0, S1, S2, GP_Gen5_2, etc.)",
                    "Do you need geo-replication? (yes/no)"
                ],
                diagram_class="SQLDatabases"
            ),
            
            # Networking Services
            "vnet": ServiceDefinition(
                name="Virtual Network",
                category="network",
                dependencies=[],
                prompts=[
                    "What address space? (e.g., 10.0.0.0/16)",
                ],
                diagram_class="VirtualNetworks"
            ),
            
            "subnet": ServiceDefinition(
                name="Subnet",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                ],
                prompts=[
                    "What subnet prefix? (e.g., 10.0.1.0/24)",
                ],
                diagram_class=None  # Represented within VNet
            ),
            
            "nsg": ServiceDefinition(
                name="Network Security Group",
                category="network",
                dependencies=[],
                prompts=[
                    "What inbound rules needed? (RDP, SSH, HTTP, HTTPS, custom)",
                ],
                diagram_class="NetworkSecurityGroups"
            ),
            
            "public_ip": ServiceDefinition(
                name="Public IP",
                category="network",
                dependencies=[],
                prompts=[
                    "What SKU? (Basic, Standard)",
                    "Static or dynamic allocation? (static/dynamic)"
                ],
                diagram_class="PublicIpAddresses"
            ),
            
            "load_balancer": ServiceDefinition(
                name="Load Balancer",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="public_ip", required=False),
                ],
                prompts=[
                    "What SKU? (Basic, Standard)",
                    "Internal or public? (internal/public)"
                ],
                diagram_class="LoadBalancers"
            ),
            
            "application_gateway": ServiceDefinition(
                name="Application Gateway",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                    ServiceDependency(service_type="subnet", required=True),
                    ServiceDependency(service_type="public_ip", required=True),
                ],
                prompts=[
                    "What SKU? (Standard_v2, WAF_v2)",
                    "Do you need WAF protection? (yes/no)",
                    "How many instances? (1-125)"
                ],
                diagram_class="ApplicationGateway"
            ),
            
            "azure_firewall": ServiceDefinition(
                name="Azure Firewall",
                category="security",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                    ServiceDependency(service_type="public_ip", required=True),
                ],
                prompts=[
                    "What SKU? (Standard, Premium)",
                    "Do you need threat intelligence? (yes/no)",
                    "What firewall policy rules needed?"
                ],
                diagram_class="Firewall"
            ),
            
            "expressroute": ServiceDefinition(
                name="ExpressRoute",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                ],
                prompts=[
                    "What bandwidth? (50Mbps, 100Mbps, 200Mbps, 500Mbps, 1Gbps, 2Gbps, 5Gbps, 10Gbps)",
                    "What peering type? (Microsoft, Private, Public)",
                    "Do you need redundancy? (yes/no)"
                ],
                diagram_class="ExpressrouteCircuits"
            ),
            
            "vpn_gateway": ServiceDefinition(
                name="VPN Gateway",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                    ServiceDependency(service_type="public_ip", required=True),
                ],
                prompts=[
                    "What VPN type? (Route-based, Policy-based)",
                    "What SKU? (Basic, VpnGw1, VpnGw2, VpnGw3, VpnGw4, VpnGw5)",
                    "Do you need active-active configuration? (yes/no)"
                ],
                diagram_class="VirtualNetworkGateways"
            ),
            
            "vnet_peering": ServiceDefinition(
                name="VNet Peering",
                category="network",
                dependencies=[
                    ServiceDependency(service_type="vnet", required=True),
                ],
                prompts=[
                    "What peering type? (Regional, Global)",
                    "Do you need gateway transit? (yes/no)"
                ],
                diagram_class=None  # Represented as connections
            ),
            
            # Edge Services
            "front_door": ServiceDefinition(
                name="Azure Front Door",
                category="edge",
                dependencies=[],
                prompts=[
                    "What SKU? (Standard, Premium)",
                    "Do you need WAF policies? (yes/no)",
                    "What backend pool origins?"
                ],
                diagram_class="FrontDoors"
            ),
            
            "cdn": ServiceDefinition(
                name="Content Delivery Network",
                category="edge",
                dependencies=[],
                prompts=[
                    "What SKU? (Standard Microsoft, Standard Akamai, Standard Verizon, Premium Verizon)",
                    "What origin type? (Storage, Web App, Custom)"
                ],
                diagram_class="CdnProfiles"
            ),
            
            # Identity Services
            "entra_id": ServiceDefinition(
                name="Microsoft Entra ID",
                category="identity",
                dependencies=[],
                prompts=[
                    "What license? (Free, P1, P2)",
                    "Do you need conditional access? (yes/no)",
                    "Do you need privileged identity management? (yes/no)"
                ],
                diagram_class="ActiveDirectory"
            ),
            
            "key_vault": ServiceDefinition(
                name="Azure Key Vault",
                category="security",
                dependencies=[],
                prompts=[
                    "What SKU? (Standard, Premium)",
                    "Do you need HSM protection? (yes/no)",
                    "What access policies needed?"
                ],
                diagram_class="KeyVaults"
            ),
            
            # Monitoring Services - Enhanced for observability requirements (req 11)
            "log_analytics": ServiceDefinition(
                name="Log Analytics Workspace",
                category="monitoring",
                dependencies=[],
                prompts=[
                    "What retention period? (30, 90, 120, 365 days)",
                    "What pricing tier? (PerGB2018, CapacityReservation)"
                ],
                diagram_class="LogAnalyticsWorkspaces"
            ),
            
            "application_insights": ServiceDefinition(
                name="Application Insights",
                category="monitoring",
                dependencies=[
                    ServiceDependency(service_type="log_analytics", required=True),
                ],
                prompts=[
                    "What application type? (web, other)",
                    "What ingestion method? (workspace-based, classic)"
                ],
                diagram_class="ApplicationInsights"
            ),
            
            "azure_monitor": ServiceDefinition(
                name="Azure Monitor",
                category="monitoring",
                dependencies=[
                    ServiceDependency(service_type="log_analytics", required=True),
                ],
                prompts=[
                    "What monitoring scope? (subscription, resource group, resource)",
                    "Do you need action groups? (yes/no)"
                ],
                diagram_class="Monitor"
            ),
            
            "sentinel": ServiceDefinition(
                name="Microsoft Sentinel",
                category="security",
                dependencies=[
                    ServiceDependency(service_type="log_analytics", required=True),
                ],
                prompts=[
                    "What data connectors needed? (Azure AD, Office 365, AWS, etc.)",
                    "Do you need threat intelligence? (yes/no)"
                ],
                diagram_class="Sentinel"
            ),
            
            # Internal components (auto-created)
            "nic": ServiceDefinition(
                name="Network Interface",
                category="network",
                dependencies=[],
                prompts=[],
                diagram_class=None  # Not shown separately
            ),
            
            "disk": ServiceDefinition(
                name="Managed Disk",
                category="storage",
                dependencies=[],
                prompts=[],
                diagram_class=None  # Not shown separately
            ),
            
            "app_service_plan": ServiceDefinition(
                name="App Service Plan",
                category="compute",
                dependencies=[],
                prompts=[],
                diagram_class=None  # Not shown separately
            ),
        }
    
    def get_service(self, service_type: str) -> Optional[ServiceDefinition]:
        """Get service definition by type."""
        return self._catalog.get(service_type)
    
    def get_dependencies(self, service_type: str) -> List[ServiceDependency]:
        """Get dependencies for a service type."""
        service = self.get_service(service_type)
        return service.dependencies if service else []
    
    def get_prompts(self, service_type: str) -> List[str]:
        """Get prompts for a service type."""
        service = self.get_service(service_type)
        return service.prompts if service else []
    
    def resolve_dependencies(self, intents: List[UserIntent]) -> List[UserIntent]:
        """
        Resolve dependencies for the given user intents.
        Returns a complete list including auto-inferred dependencies.
        """
        resolved = []
        added_services = set()
        
        # Process explicit intents first
        for intent in intents:
            if intent.kind not in added_services:
                resolved.append(intent)
                added_services.add(intent.kind)
        
        # Add dependencies
        for intent in resolved[:]:  # Create a copy to iterate over
            dependencies = self.get_dependencies(intent.kind)
            
            for dep in dependencies:
                if dep.service_type not in added_services:
                    # Create a dependency intent with minimal configuration
                    dep_intent = UserIntent(
                        kind=dep.service_type,
                        name=f"Auto-{dep.service_type}",
                        properties=dep.properties.copy()
                    )
                    
                    # Handle special dependency logic
                    if dep.service_type == "public_ip" and not dep.required:
                        # For optional public IP, check if user wants it
                        # This would be handled by the interactive prompting
                        continue
                    
                    resolved.append(dep_intent)
                    added_services.add(dep.service_type)
        
        return resolved
    
    def get_missing_properties(self, intent: UserIntent) -> List[str]:
        """
        Check what required properties are missing for a service.
        Returns list of prompts for missing properties.
        """
        service = self.get_service(intent.kind)
        if not service:
            return []
        
        # For now, return all prompts as potentially missing
        # In a real implementation, we'd check against intent.properties
        return service.prompts
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get services organized by category."""
        categories = {}
        for service_type, service_def in self._catalog.items():
            category = service_def.category
            if category not in categories:
                categories[category] = []
            categories[category].append(service_type)
        return categories