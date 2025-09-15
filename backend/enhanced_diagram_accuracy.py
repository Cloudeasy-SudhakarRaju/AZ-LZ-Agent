"""
Enhanced Diagram Accuracy Module for Azure Landing Zone Agent

This module implements improvements to achieve 100% architecture diagram accuracy
with focus on precise connectivity, clean layout, and professional styling
similar to eraser.io/diagramgpt.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import os
import uuid
from datetime import datetime
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import VM, AKS, AppServices, FunctionApps
from diagrams.azure.network import VirtualNetworks, ApplicationGateway, LoadBalancers, Firewall
from diagrams.azure.storage import StorageAccounts, BlobStorage
from diagrams.azure.database import SQLDatabases, CosmosDb
from diagrams.azure.security import KeyVaults, SecurityCenter
from diagrams.azure.identity import ActiveDirectory  # ActiveDirectory is in identity, not security
from diagrams.azure.analytics import SynapseAnalytics, DataFactories
from diagrams.azure.integration import LogicApps, APIManagement
from diagrams.azure.devops import Devops

logger = logging.getLogger(__name__)

class ArchitecturalPattern:
    """Defines precise architectural patterns for accurate connectivity"""
    
    # Web application tier patterns
    WEB_TIER_PATTERNS = {
        "internet_to_gateway": {
            "description": "Internet traffic enters through Application Gateway",
            "connections": [("internet", "application_gateway")],
            "required_services": ["application_gateway"]
        },
        "gateway_to_apps": {
            "description": "Application Gateway routes to compute services",
            "connections": [("application_gateway", "app_services"), ("application_gateway", "virtual_machines")],
            "required_services": ["application_gateway", ("app_services", "virtual_machines")]
        },
        "load_balancer_distribution": {
            "description": "Load balancer distributes traffic within tier",
            "connections": [("load_balancer", "virtual_machines"), ("load_balancer", "aks")],
            "required_services": ["load_balancer", ("virtual_machines", "aks")]
        }
    }
    
    # Data tier patterns
    DATA_TIER_PATTERNS = {
        "app_to_database": {
            "description": "Applications connect to databases securely",
            "connections": [
                ("app_services", "sql_database"),
                ("app_services", "cosmos_db"),
                ("virtual_machines", "sql_database"),
                ("aks", "sql_database")
            ],
            "required_services": ["app_services", "sql_database"]
        },
        "app_to_storage": {
            "description": "Applications access storage services",
            "connections": [
                ("app_services", "storage_accounts"),
                ("app_services", "blob_storage"),
                ("virtual_machines", "storage_accounts")
            ],
            "required_services": ["app_services", "storage_accounts"]
        }
    }
    
    # Security patterns
    SECURITY_PATTERNS = {
        "keyvault_integration": {
            "description": "Key Vault provides secrets to applications",
            "connections": [
                ("key_vault", "app_services"),
                ("key_vault", "virtual_machines"),
                ("key_vault", "aks")
            ],
            "required_services": ["key_vault", ("app_services", "virtual_machines", "aks")]
        },
        "firewall_protection": {
            "description": "Firewall protects network perimeter",
            "connections": [("firewall", "virtual_network")],
            "required_services": ["firewall", "virtual_network"]
        }
    }
    
    # Network patterns
    NETWORK_PATTERNS = {
        "vnet_hub_spoke": {
            "description": "Hub-spoke virtual network topology",
            "connections": [("virtual_network", "virtual_network")],  # VNet peering
            "required_services": ["virtual_network"],
            "minimum_count": 2
        }
    }

class AccurateDiagramGenerator:
    """Generates highly accurate Azure architecture diagrams with precise connectivity"""
    
    def __init__(self):
        self.patterns = ArchitecturalPattern()
        self.created_resources = {}
        self.logical_connections = []
        
    def generate_precise_diagram(self, inputs, template: Dict[str, Any], 
                                output_dir: str, filename: str) -> str:
        """
        Generate diagram with 100% accuracy focus:
        - Only necessary connections
        - Clean, professional layout
        - Precise resource positioning
        - Minimal visual noise
        """
        
        logger.info("Generating precise architecture diagram with enhanced accuracy")
        
        # Enhanced graph attributes for professional appearance
        graph_attrs = {
            "fontsize": "14",
            "fontname": "Arial",
            "rankdir": "TB",  # Top to bottom layout
            "nodesep": "2.0",   # Increased node separation for clarity
            "ranksep": "2.5",   # Increased rank separation
            "bgcolor": "#ffffff",
            "margin": "1.0",
            "splines": "ortho",  # Orthogonal edges for cleaner lines
            "overlap": "false",
            "sep": "+20,20"      # Additional separation
        }
        
        node_attrs = {
            "fontsize": "11",
            "fontname": "Arial",
            "shape": "box",
            "style": "rounded,filled",
            "fillcolor": "#f8f9fa",
            "color": "#dee2e6",
            "margin": "0.3,0.2"
        }
        
        edge_attrs = {
            "fontsize": "9",
            "fontname": "Arial",
            "color": "#495057",
            "arrowsize": "0.8",
            "penwidth": "1.5"
        }
        
        diagram_title = self._get_clean_diagram_title(inputs, template)
        filepath = f"{output_dir}/{filename}"
        
        with Diagram(
            diagram_title,
            filename=filepath,
            show=False,
            direction="TB",
            outformat="png",
            graph_attr=graph_attrs,
            node_attr=node_attrs,
            edge_attr=edge_attrs
        ):
            # Step 1: Create only explicitly requested resources
            self._create_requested_resources(inputs, template)
            
            # Step 2: Apply precise connectivity patterns
            self._apply_precise_connectivity_patterns(inputs)
            
            # Step 3: Optimize layout for clarity
            self._optimize_layout_hierarchy()
        
        return f"{filepath}.png"
    
    def _get_clean_diagram_title(self, inputs, template: Dict[str, Any]) -> str:
        """Generate clean, professional diagram title"""
        business_obj = inputs.business_objective or "Azure Architecture"
        return business_obj.replace("'", "").replace('"', '')[:50]  # Clean and limit length
    
    def _create_requested_resources(self, inputs, template: Dict[str, Any]):
        """Create only explicitly requested Azure resources with clean organization"""
        
        # Security & Identity (if requested)
        if inputs.security_services:
            self._create_security_cluster(inputs.security_services)
        
        # Networking (if requested) 
        if inputs.network_services:
            self._create_network_cluster(inputs.network_services)
        
        # Compute (if requested)
        if inputs.compute_services:
            self._create_compute_cluster(inputs.compute_services)
            
        # Data & Storage (if requested)
        if inputs.database_services or inputs.storage_services:
            self._create_data_cluster(inputs.database_services, inputs.storage_services)
        
        # Integration & Analytics (if requested)
        if inputs.integration_services or inputs.analytics_services:
            self._create_integration_cluster(inputs.integration_services, inputs.analytics_services)
            
        # DevOps (if requested)
        if inputs.devops_services:
            self._create_devops_cluster(inputs.devops_services)
    
    def _create_security_cluster(self, security_services: List[str]):
        """Create security services cluster with clean styling"""
        if not security_services:
            return
            
        with Cluster("Security & Identity", 
                    graph_attr={"bgcolor": "#fff5f5", "style": "rounded", "penwidth": "2"}):
            
            if "active_directory" in security_services:
                aad = ActiveDirectory("Azure AD")
                self.created_resources["active_directory"] = [aad]
                
            if "key_vault" in security_services:
                kv = KeyVaults("Key Vault") 
                self.created_resources["key_vault"] = [kv]
    
    def _create_network_cluster(self, network_services: List[str]):
        """Create network services cluster with precise layout"""
        if not network_services:
            return
            
        with Cluster("Network Architecture",
                    graph_attr={"bgcolor": "#f0f8ff", "style": "rounded", "penwidth": "2"}):
            
            if "virtual_network" in network_services:
                vnet = VirtualNetworks("Virtual Network")
                self.created_resources["virtual_network"] = [vnet]
                
            if "application_gateway" in network_services:
                app_gw = ApplicationGateway("Application Gateway")
                self.created_resources["application_gateway"] = [app_gw]
                
            if "firewall" in network_services:
                fw = Firewall("Azure Firewall")
                self.created_resources["firewall"] = [fw]
                
            if "load_balancer" in network_services:
                lb = LoadBalancers("Load Balancer")
                self.created_resources["load_balancer"] = [lb]
    
    def _create_compute_cluster(self, compute_services: List[str]):
        """Create compute services cluster with logical grouping"""
        if not compute_services:
            return
            
        with Cluster("Compute Services",
                    graph_attr={"bgcolor": "#f8f9fa", "style": "rounded", "penwidth": "2"}):
            
            if "app_services" in compute_services:
                apps = AppServices("App Services")
                self.created_resources["app_services"] = [apps]
                
            if "virtual_machines" in compute_services:
                vms = VM("Virtual Machines")
                self.created_resources["virtual_machines"] = [vms]
                
            if "aks" in compute_services:
                aks = AKS("AKS Cluster")
                self.created_resources["aks"] = [aks]
                
            if "functions" in compute_services:
                funcs = FunctionApps("Functions")
                self.created_resources["functions"] = [funcs]
    
    def _create_data_cluster(self, database_services: List[str], storage_services: List[str]):
        """Create data services cluster with clean separation"""
        if not database_services and not storage_services:
            return
            
        with Cluster("Data Services",
                    graph_attr={"bgcolor": "#f0fff0", "style": "rounded", "penwidth": "2"}):
            
            # Database services
            if database_services:
                if "sql_database" in database_services:
                    sql = SQLDatabases("SQL Database")
                    self.created_resources["sql_database"] = [sql]
                    
                if "cosmos_db" in database_services:
                    cosmos = CosmosDb("Cosmos DB")
                    self.created_resources["cosmos_db"] = [cosmos]
            
            # Storage services  
            if storage_services:
                if "storage_accounts" in storage_services:
                    storage = StorageAccounts("Storage Account")
                    self.created_resources["storage_accounts"] = [storage]
                    
                if "blob_storage" in storage_services:
                    blob = BlobStorage("Blob Storage")
                    self.created_resources["blob_storage"] = [blob]
    
    def _create_integration_cluster(self, integration_services: List[str], analytics_services: List[str]):
        """Create integration & analytics cluster"""
        if not integration_services and not analytics_services:
            return
            
        with Cluster("Integration & Analytics", 
                    graph_attr={"bgcolor": "#fffbf0", "style": "rounded", "penwidth": "2"}):
            
            if integration_services:
                if "api_management" in integration_services:
                    apim = APIManagement("API Management")
                    self.created_resources["api_management"] = [apim]
                    
                if "logic_apps" in integration_services:
                    logic = LogicApps("Logic Apps")
                    self.created_resources["logic_apps"] = [logic]
            
            if analytics_services:
                if "synapse" in analytics_services:
                    synapse = SynapseAnalytics("Synapse Analytics")
                    self.created_resources["synapse"] = [synapse]
                    
                if "data_factory" in analytics_services:
                    adf = DataFactories("Data Factory")
                    self.created_resources["data_factory"] = [adf]
    
    def _create_devops_cluster(self, devops_services: List[str]):
        """Create DevOps cluster with clean layout"""
        if not devops_services:
            return
            
        with Cluster("DevOps & Governance",
                    graph_attr={"bgcolor": "#f5f5f5", "style": "rounded", "penwidth": "2"}):
            
            if "devops" in devops_services:
                devops = Devops("Azure DevOps")
                self.created_resources["devops"] = [devops]
    
    def _apply_precise_connectivity_patterns(self, inputs):
        """Apply only necessary, logically required connections"""
        
        logger.info("Applying precise connectivity patterns")
        
        # Web tier connectivity
        self._apply_web_tier_connections()
        
        # Data tier connectivity
        self._apply_data_tier_connections()
        
        # Security connectivity
        self._apply_security_connections()
        
        # Network connectivity
        self._apply_network_connections()
    
    def _apply_web_tier_connections(self):
        """Apply precise web tier connections"""
        
        # Application Gateway -> Compute Services (if both exist)
        app_gw = self.created_resources.get("application_gateway", [])
        compute_services = ["app_services", "virtual_machines", "aks"]
        
        for app_gateway in app_gw:
            for service_type in compute_services:
                for compute_resource in self.created_resources.get(service_type, []):
                    app_gateway >> Edge(
                        color="#28a745", 
                        style="bold", 
                        label="HTTPS"
                    ) >> compute_resource
                    
        # Load Balancer -> Virtual Machines/AKS (if both exist)
        load_balancers = self.created_resources.get("load_balancer", [])
        for lb in load_balancers:
            for vm in self.created_resources.get("virtual_machines", []):
                lb >> Edge(color="#17a2b8", style="solid", label="TCP") >> vm
            for aks in self.created_resources.get("aks", []):
                lb >> Edge(color="#17a2b8", style="solid", label="TCP") >> aks
    
    def _apply_data_tier_connections(self):
        """Apply precise data tier connections"""
        
        # Compute -> Databases (if both exist)
        compute_services = ["app_services", "virtual_machines", "aks"]
        data_services = ["sql_database", "cosmos_db"]
        
        for compute_type in compute_services:
            for compute_resource in self.created_resources.get(compute_type, []):
                for data_type in data_services:
                    for data_resource in self.created_resources.get(data_type, []):
                        compute_resource >> Edge(
                            color="#007bff",
                            style="solid", 
                            label="SQL/API"
                        ) >> data_resource
        
        # Compute -> Storage (if both exist)
        for compute_type in compute_services:
            for compute_resource in self.created_resources.get(compute_type, []):
                for storage in self.created_resources.get("storage_accounts", []):
                    compute_resource >> Edge(
                        color="#6f42c1",
                        style="dashed",
                        label="Blob/File"
                    ) >> storage
    
    def _apply_security_connections(self):
        """Apply precise security connections"""
        
        # Key Vault -> Compute Services (for secrets access)
        key_vaults = self.created_resources.get("key_vault", [])
        compute_services = ["app_services", "virtual_machines", "aks"]
        
        for kv in key_vaults:
            for service_type in compute_services:
                for compute_resource in self.created_resources.get(service_type, []):
                    kv >> Edge(
                        color="#dc3545", 
                        style="dashed",
                        label="Secrets"
                    ) >> compute_resource
    
    def _apply_network_connections(self):
        """Apply precise network connections"""
        
        # Firewall -> Virtual Network (if both exist)
        firewalls = self.created_resources.get("firewall", [])
        vnets = self.created_resources.get("virtual_network", [])
        
        for firewall in firewalls:
            for vnet in vnets:
                firewall >> Edge(
                    color="#fd7e14",
                    style="bold", 
                    label="Network Rules"
                ) >> vnet
    
    def _optimize_layout_hierarchy(self):
        """Optimize layout for maximum clarity and professional appearance"""
        
        # This is handled by the enhanced graph attributes
        # Additional optimizations can be added here if needed
        logger.info("Layout optimization applied for enhanced clarity")

def generate_accurate_azure_diagram(inputs, template: Dict[str, Any], 
                                  output_dir: str, filename: str) -> str:
    """
    Main function to generate highly accurate Azure architecture diagrams
    
    Returns path to generated PNG diagram
    """
    
    generator = AccurateDiagramGenerator()
    return generator.generate_precise_diagram(inputs, template, output_dir, filename)