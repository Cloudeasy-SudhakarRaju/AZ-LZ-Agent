"""
LangGraph Agent Orchestration for Azure Landing Zone Hub and Spoke Architecture

This module implements a multi-agent workflow using LangGraph to create diagrams
that clearly differentiate hub and spoke architecture principles. The workflow:
1. Hub agent handles shared services (Active Directory, Firewall, DNS, Bastion, Security Center)
2. Spoke agent handles workload-specific services (DB, KeyVault, App Service, Storage Account)
3. Hub executes first, passes context to spoke, results are merged for final output
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass, asdict
import json

# LangGraph imports - with fallback for environments without langgraph
try:
    from langgraph.graph import Graph, StateGraph
    from langgraph.graph.state import State
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Create mock classes for when langgraph is not available
    class Graph:
        pass
    class StateGraph:
        def __init__(self, state_schema):
            self.state_schema = state_schema
            self.nodes = {}
            self.edges = []
        def add_node(self, name, func):
            self.nodes[name] = func
        def add_edge(self, from_node, to_node):
            self.edges.append((from_node, to_node))
        def set_entry_point(self, node):
            self.entry_point = node
        def set_finish_point(self, node):
            self.finish_point = node
        def compile(self, checkpointer=None):
            return MockCompiledGraph(self)
    
    class MockCompiledGraph:
        def __init__(self, graph):
            self.graph = graph
        def invoke(self, initial_state, config=None):
            # Mock execution - process through hub then spoke then merge
            state = initial_state.copy()
            if "hub_agent" in self.graph.nodes:
                state = self.graph.nodes["hub_agent"](state)
            if "spoke_agent" in self.graph.nodes:
                state = self.graph.nodes["spoke_agent"](state)
            if "merge_results" in self.graph.nodes:
                state = self.graph.nodes["merge_results"](state)
            return state
    
    class MemorySaver:
        pass

logger = logging.getLogger(__name__)

# Azure service categorization for hub and spoke separation
HUB_SERVICES = {
    # Shared Infrastructure Services
    'firewall', 'azure_firewall', 'network_security_groups',
    'dns', 'private_dns', 'azure_dns',
    'bastion', 'azure_bastion',
    'active_directory', 'azure_ad', 'entra_id',
    'security_center', 'defender_for_cloud',
    'sentinel', 'azure_sentinel',
    'policy', 'azure_policy',
    'management_groups',
    'log_analytics', 'monitor',
    'backup', 'site_recovery',
    # Network Hub Services
    'virtual_network_gateway', 'vpn_gateway', 'expressroute',
    'application_gateway', 'load_balancer', 'traffic_manager',
    # Identity and Access
    'key_vault', 'managed_identity',
    # Governance
    'cost_management', 'advisor'
}

SPOKE_SERVICES = {
    # Compute Services
    'virtual_machines', 'vm', 'vmss',
    'app_services', 'web_apps', 'function_apps',
    'aks', 'kubernetes', 'container_instances',
    'service_fabric', 'batch',
    # Database Services  
    'sql_database', 'mysql', 'postgresql', 'cosmos_db',
    'redis_cache', 'database_for_mysql', 'database_for_postgresql',
    # Storage Services
    'storage_accounts', 'blob_storage', 'file_shares',
    'data_lake', 'synapse_analytics',
    # Application Services
    'api_management', 'service_bus', 'event_hubs',
    'logic_apps', 'event_grid',
    # Analytics & AI
    'databricks', 'data_factory', 'cognitive_services',
    'machine_learning', 'search_service'
}

class WorkflowState(TypedDict):
    """State schema for LangGraph workflow"""
    customer_inputs: Dict[str, Any]
    hub_services: List[str]
    spoke_services: List[str]
    hub_context: Dict[str, Any]
    spoke_context: Dict[str, Any]
    diagram_components: Dict[str, Any]
    network_topology: Dict[str, Any]
    final_result: Dict[str, Any]
    execution_log: List[str]

@dataclass
class HubAgentResult:
    """Result from hub agent processing"""
    hub_services: List[str]
    network_topology: Dict[str, Any]
    shared_infrastructure: Dict[str, Any]
    security_policies: Dict[str, Any]
    connectivity_matrix: Dict[str, Any]
    
@dataclass 
class SpokeAgentResult:
    """Result from spoke agent processing"""
    spoke_services: List[str]
    workload_components: Dict[str, Any]
    data_flow: Dict[str, Any]
    resource_dependencies: Dict[str, Any]
    scaling_configuration: Dict[str, Any]

class HubAgent:
    """Agent responsible for hub services and shared infrastructure"""
    
    def __init__(self):
        self.name = "hub_agent"
        
    def analyze_hub_services(self, inputs: Dict[str, Any]) -> HubAgentResult:
        """Analyze and determine hub services based on customer inputs"""
        
        # Extract services that belong to hub
        all_services = []
        
        # Collect all selected services
        for service_category in ['network_services', 'security_services', 'monitoring_services']:
            if service_category in inputs and inputs[service_category]:
                all_services.extend(inputs[service_category])
        
        # Filter hub services
        hub_services = [svc for svc in all_services if any(hub_svc in svc.lower() for hub_svc in HUB_SERVICES)]
        
        # Always include core hub services for proper architecture
        core_hub_services = ['azure_firewall', 'bastion', 'dns']
        for core_svc in core_hub_services:
            if core_svc not in hub_services:
                hub_services.append(core_svc)
        
        # Determine network topology
        network_topology = self._design_hub_network_topology(inputs, hub_services)
        
        # Define shared infrastructure
        shared_infrastructure = self._define_shared_infrastructure(inputs, hub_services)
        
        # Security policies for hub
        security_policies = self._define_hub_security_policies(inputs, hub_services)
        
        # Connectivity matrix (how hub connects to spokes)
        connectivity_matrix = self._define_connectivity_matrix(inputs)
        
        return HubAgentResult(
            hub_services=hub_services,
            network_topology=network_topology,
            shared_infrastructure=shared_infrastructure,
            security_policies=security_policies,
            connectivity_matrix=connectivity_matrix
        )
    
    def _design_hub_network_topology(self, inputs: Dict[str, Any], hub_services: List[str]) -> Dict[str, Any]:
        """Design the hub network topology"""
        topology = {
            "hub_vnet": {
                "name": "Hub-VNet",
                "address_space": "10.0.0.0/16",
                "subnets": {
                    "AzureFirewallSubnet": "10.0.1.0/26",
                    "AzureBastionSubnet": "10.0.2.0/27", 
                    "GatewaySubnet": "10.0.3.0/27",
                    "SharedServicesSubnet": "10.0.4.0/24"
                }
            },
            "gateway_config": {
                "type": "vpn" if "vpn_gateway" in hub_services else "expressroute" if "expressroute" in hub_services else "none",
                "sku": "VpnGw2" if "vpn_gateway" in hub_services else "Standard" if "expressroute" in hub_services else None
            },
            "peering_configuration": {
                "allow_virtual_network_access": True,
                "allow_forwarded_traffic": True,
                "allow_gateway_transit": True,
                "use_remote_gateways": False
            }
        }
        return topology
    
    def _define_shared_infrastructure(self, inputs: Dict[str, Any], hub_services: List[str]) -> Dict[str, Any]:
        """Define shared infrastructure components"""
        infrastructure = {
            "identity_services": {
                "azure_ad": True,
                "managed_identity": True,
                "privileged_identity_management": inputs.get('security_posture') == 'zero_trust'
            },
            "monitoring_services": {
                "log_analytics_workspace": True,
                "azure_monitor": True,
                "application_insights": True,
                "azure_sentinel": "sentinel" in hub_services
            },
            "backup_services": {
                "recovery_services_vault": True,
                "azure_backup": True,
                "site_recovery": inputs.get('backup') == 'comprehensive'
            },
            "governance_services": {
                "azure_policy": True,
                "management_groups": True,
                "cost_management": True,
                "azure_advisor": True
            }
        }
        return infrastructure
    
    def _define_hub_security_policies(self, inputs: Dict[str, Any], hub_services: List[str]) -> Dict[str, Any]:
        """Define security policies for hub"""
        policies = {
            "network_security": {
                "default_deny_all": True,
                "firewall_rules": [],
                "nsg_rules": []
            },
            "identity_security": {
                "mfa_required": True,
                "conditional_access": True,
                "zero_trust": inputs.get('security_posture') == 'zero_trust'
            },
            "data_protection": {
                "encryption_in_transit": True,
                "encryption_at_rest": True,
                "key_management": "azure_key_vault"
            }
        }
        return policies
    
    def _define_connectivity_matrix(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Define how hub connects to spokes"""
        matrix = {
            "hub_to_spoke_connectivity": "vnet_peering",
            "spoke_to_spoke_connectivity": "via_hub_firewall",
            "internet_connectivity": "via_hub_firewall",
            "on_premises_connectivity": "via_hub_gateway",
            "traffic_flow": {
                "north_south": "hub_firewall",
                "east_west": "hub_firewall", 
                "spoke_to_internet": "hub_firewall"
            }
        }
        return matrix

class SpokeAgent:
    """Agent responsible for spoke services and workload-specific components"""
    
    def __init__(self):
        self.name = "spoke_agent"
        
    def analyze_spoke_services(self, inputs: Dict[str, Any], hub_context: Dict[str, Any]) -> SpokeAgentResult:
        """Analyze and determine spoke services based on customer inputs and hub context"""
        
        # Extract services that belong to spokes
        all_services = []
        
        # Collect all selected services
        for service_category in ['compute_services', 'database_services', 'storage_services', 'ai_services', 'analytics_services']:
            if service_category in inputs and inputs[service_category]:
                all_services.extend(inputs[service_category])
        
        # Filter spoke services
        spoke_services = [svc for svc in all_services if any(spoke_svc in svc.lower() for spoke_svc in SPOKE_SERVICES)]
        
        # Design workload components based on architecture pattern
        workload_components = self._design_workload_components(inputs, spoke_services, hub_context)
        
        # Define data flow between components
        data_flow = self._define_data_flow(inputs, spoke_services)
        
        # Resource dependencies
        resource_dependencies = self._define_resource_dependencies(spoke_services, hub_context)
        
        # Scaling configuration
        scaling_configuration = self._define_scaling_configuration(inputs, spoke_services)
        
        return SpokeAgentResult(
            spoke_services=spoke_services,
            workload_components=workload_components,
            data_flow=data_flow,
            resource_dependencies=resource_dependencies,
            scaling_configuration=scaling_configuration
        )
    
    def _design_workload_components(self, inputs: Dict[str, Any], spoke_services: List[str], hub_context: Dict[str, Any]) -> Dict[str, Any]:
        """Design workload-specific components"""
        
        # Determine spoke architecture pattern
        architecture_style = inputs.get('architecture_style', 'n_tier')
        
        components = {
            "production_spoke": {
                "vnet": {
                    "name": "Production-Spoke-VNet",
                    "address_space": "10.1.0.0/16",
                    "subnets": self._design_spoke_subnets(spoke_services, "production")
                },
                "services": self._categorize_spoke_services(spoke_services, "production"),
                "peering_to_hub": True
            },
            "development_spoke": {
                "vnet": {
                    "name": "Development-Spoke-VNet", 
                    "address_space": "10.2.0.0/16",
                    "subnets": self._design_spoke_subnets(spoke_services, "development")
                },
                "services": self._categorize_spoke_services(spoke_services, "development"),
                "peering_to_hub": True
            }
        }
        
        return components
    
    def _design_spoke_subnets(self, spoke_services: List[str], environment: str) -> Dict[str, str]:
        """Design subnet layout for spoke based on services"""
        subnets = {}
        
        # Base subnets
        if environment == "production":
            base_cidr = "10.1"
        else:
            base_cidr = "10.2"
        
        subnet_counter = 1
        
        # Web tier subnet if web services present
        if any(svc in spoke_services for svc in ['app_services', 'web_apps']):
            subnets[f"WebTierSubnet"] = f"{base_cidr}.{subnet_counter}.0/24"
            subnet_counter += 1
        
        # App tier subnet if compute services present  
        if any(svc in spoke_services for svc in ['virtual_machines', 'aks', 'function_apps']):
            subnets[f"AppTierSubnet"] = f"{base_cidr}.{subnet_counter}.0/24"
            subnet_counter += 1
        
        # Data tier subnet if database services present
        if any(svc in spoke_services for svc in ['sql_database', 'cosmos_db', 'mysql']):
            subnets[f"DataTierSubnet"] = f"{base_cidr}.{subnet_counter}.0/24"
            subnet_counter += 1
        
        # Container subnet if container services present
        if any(svc in spoke_services for svc in ['aks', 'container_instances']):
            subnets[f"ContainerSubnet"] = f"{base_cidr}.{subnet_counter}.0/23"
            subnet_counter += 2
        
        return subnets
    
    def _categorize_spoke_services(self, spoke_services: List[str], environment: str) -> Dict[str, List[str]]:
        """Categorize services by tier within spoke"""
        categories = {
            "web_tier": [],
            "application_tier": [],
            "data_tier": [],
            "integration_tier": []
        }
        
        for service in spoke_services:
            if service in ['app_services', 'web_apps']:
                categories["web_tier"].append(service)
            elif service in ['virtual_machines', 'function_apps', 'aks']:
                categories["application_tier"].append(service)
            elif service in ['sql_database', 'cosmos_db', 'mysql', 'postgresql']:
                categories["data_tier"].append(service)
            elif service in ['api_management', 'service_bus', 'event_hubs']:
                categories["integration_tier"].append(service)
        
        return categories
    
    def _define_data_flow(self, inputs: Dict[str, Any], spoke_services: List[str]) -> Dict[str, Any]:
        """Define data flow between spoke components"""
        data_flow = {
            "ingress": "via_hub_application_gateway",
            "web_to_app": "internal_load_balancer",
            "app_to_data": "private_endpoints",
            "integration_flow": "service_bus_queues",
            "egress": "via_hub_firewall"
        }
        return data_flow
    
    def _define_resource_dependencies(self, spoke_services: List[str], hub_context: Dict[str, Any]) -> Dict[str, Any]:
        """Define dependencies between spoke resources and hub"""
        dependencies = {
            "hub_dependencies": {
                "dns_resolution": "hub_dns",
                "internet_access": "hub_firewall",
                "backup_services": "hub_recovery_vault",
                "monitoring": "hub_log_analytics",
                "identity": "hub_azure_ad"
            },
            "spoke_internal_dependencies": {
                "app_depends_on": ["sql_database", "storage_accounts"],
                "web_depends_on": ["app_services"],
                "integration_depends_on": ["service_bus", "api_management"]
            }
        }
        return dependencies
    
    def _define_scaling_configuration(self, inputs: Dict[str, Any], spoke_services: List[str]) -> Dict[str, Any]:
        """Define scaling configuration for spoke services"""
        scalability = inputs.get('scalability', 'moderate')
        
        config = {
            "auto_scaling": scalability in ['high', 'elastic'],
            "scaling_metrics": ["cpu_utilization", "memory_utilization", "request_count"],
            "scaling_policies": {
                "scale_out_threshold": 70,
                "scale_in_threshold": 30,
                "min_instances": 2 if scalability == 'high' else 1,
                "max_instances": 20 if scalability == 'high' else 10
            }
        }
        return config

class AzureLandingZoneOrchestrator:
    """Main orchestrator for hub and spoke workflow using LangGraph"""
    
    def __init__(self):
        self.hub_agent = HubAgent()
        self.spoke_agent = SpokeAgent()
        self.workflow = self._create_workflow()
        
    def _create_workflow(self):
        """Create LangGraph workflow for hub and spoke orchestration"""
        
        def hub_agent_node(state: WorkflowState) -> WorkflowState:
            """Hub agent processing node"""
            logger.info("Hub agent processing started")
            
            hub_result = self.hub_agent.analyze_hub_services(state["customer_inputs"])
            
            # Update state with hub results
            state["hub_services"] = hub_result.hub_services
            state["hub_context"] = asdict(hub_result)
            state["network_topology"] = hub_result.network_topology
            state["execution_log"].append("Hub agent completed successfully")
            
            logger.info(f"Hub agent identified {len(hub_result.hub_services)} hub services")
            return state
        
        def spoke_agent_node(state: WorkflowState) -> WorkflowState:
            """Spoke agent processing node"""
            logger.info("Spoke agent processing started")
            
            spoke_result = self.spoke_agent.analyze_spoke_services(
                state["customer_inputs"], 
                state["hub_context"]
            )
            
            # Update state with spoke results
            state["spoke_services"] = spoke_result.spoke_services  
            state["spoke_context"] = asdict(spoke_result)
            state["execution_log"].append("Spoke agent completed successfully")
            
            logger.info(f"Spoke agent identified {len(spoke_result.spoke_services)} spoke services")
            return state
        
        def merge_results_node(state: WorkflowState) -> WorkflowState:
            """Merge hub and spoke results for final diagram"""
            logger.info("Merging hub and spoke results")
            
            # Combine all components for diagram generation
            diagram_components = {
                "hub": {
                    "services": state["hub_services"],
                    "network": state["network_topology"],
                    "infrastructure": state["hub_context"].get("shared_infrastructure", {})
                },
                "spokes": {
                    "services": state["spoke_services"],
                    "workloads": state["spoke_context"].get("workload_components", {}),
                    "data_flow": state["spoke_context"].get("data_flow", {})
                },
                "connectivity": state["hub_context"].get("connectivity_matrix", {}),
                "architecture_pattern": "hub_and_spoke"
            }
            
            state["diagram_components"] = diagram_components
            state["final_result"] = {
                "success": True,
                "hub_services_count": len(state["hub_services"]),
                "spoke_services_count": len(state["spoke_services"]),
                "diagram_ready": True,
                "architecture_pattern": "hub_and_spoke"
            }
            state["execution_log"].append("Results merged successfully")
            
            logger.info("Hub and spoke orchestration completed successfully")
            return state
        
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("hub_agent", hub_agent_node)
        workflow.add_node("spoke_agent", spoke_agent_node) 
        workflow.add_node("merge_results", merge_results_node)
        
        # Define flow: hub -> spoke -> merge
        workflow.add_edge("hub_agent", "spoke_agent")
        workflow.add_edge("spoke_agent", "merge_results")
        
        # Set entry and finish points
        workflow.set_entry_point("hub_agent")
        workflow.set_finish_point("merge_results")
        
        # Compile workflow
        if LANGGRAPH_AVAILABLE:
            checkpointer = MemorySaver()
            return workflow.compile(checkpointer=checkpointer)
        else:
            return workflow.compile()
    
    def process_landing_zone_request(self, customer_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer inputs through hub and spoke workflow"""
        
        # Initialize workflow state
        initial_state = WorkflowState(
            customer_inputs=customer_inputs,
            hub_services=[],
            spoke_services=[],
            hub_context={},
            spoke_context={}, 
            diagram_components={},
            network_topology={},
            final_result={},
            execution_log=["Workflow started"]
        )
        
        try:
            # Execute workflow
            config = {"configurable": {"thread_id": f"lz-{hash(str(customer_inputs))}"}}
            result = self.workflow.invoke(initial_state, config=config)
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_log": initial_state["execution_log"] + [f"Error: {str(e)}"]
            }

# Utility functions for integration

def categorize_services_by_hub_spoke(services: List[str]) -> Dict[str, List[str]]:
    """Categorize a list of services into hub and spoke categories"""
    hub_services = [svc for svc in services if any(hub_svc in svc.lower() for hub_svc in HUB_SERVICES)]
    spoke_services = [svc for svc in services if any(spoke_svc in svc.lower() for spoke_svc in SPOKE_SERVICES)]
    
    return {
        "hub_services": hub_services,
        "spoke_services": spoke_services,
        "uncategorized": [svc for svc in services if svc not in hub_services and svc not in spoke_services]
    }

def create_orchestrator() -> AzureLandingZoneOrchestrator:
    """Factory function to create orchestrator instance"""
    return AzureLandingZoneOrchestrator()

# Sample execution for testing
if __name__ == "__main__":
    # Sample customer inputs
    sample_inputs = {
        "business_objective": "Enterprise web application with high availability",
        "network_services": ["firewall", "bastion", "vpn_gateway"],
        "compute_services": ["app_services", "virtual_machines"],
        "database_services": ["sql_database"],
        "storage_services": ["storage_accounts"],
        "security_services": ["key_vault", "security_center"],
        "scalability": "high",
        "security_posture": "zero_trust"
    }
    
    # Create and run orchestrator
    orchestrator = create_orchestrator()
    result = orchestrator.process_landing_zone_request(sample_inputs)
    
    print("Hub and Spoke Orchestration Result:")
    print(json.dumps(result.get("final_result", {}), indent=2))