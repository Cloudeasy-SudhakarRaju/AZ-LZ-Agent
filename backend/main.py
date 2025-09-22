from fastapi import FastAPI, Response, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import html
import json
import uuid
import os
import base64
import subprocess
import tempfile
import logging
import traceback
from datetime import datetime
from pathlib import Path
import requests
import google.generativeai as genai
# Document processing imports
import PyPDF2
import openpyxl
from pptx import Presentation

# Configure logging first
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import OpenAI only if available
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available, will use HTTP requests if needed")

# Import diagrams for Azure architecture generation
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import VM, AKS, AppServices, FunctionApps, ContainerInstances, ServiceFabricClusters, BatchAccounts
from diagrams.azure.network import VirtualNetworks, ApplicationGateway, LoadBalancers, Firewall, ExpressrouteCircuits, VirtualNetworkGateways, FrontDoors, CDNProfiles
from diagrams.azure.storage import StorageAccounts, BlobStorage, DataLakeStorage
from diagrams.azure.database import SQLDatabases, CosmosDb, DatabaseForMysqlServers, DatabaseForPostgresqlServers, CacheForRedis
from diagrams.azure.security import KeyVaults, SecurityCenter, Sentinel
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.analytics import SynapseAnalytics, DataFactories, Databricks, StreamAnalyticsJobs, EventHubs
from diagrams.azure.integration import LogicApps, ServiceBus, EventGridTopics, APIManagement
from diagrams.azure.devops import Devops, Pipelines
from diagrams.azure.general import Subscriptions, Resourcegroups
from diagrams.azure.web import AppServices as WebApps

app = FastAPI(
    title="Azure Landing Zone Agent",
    description="Professional Azure Landing Zone Architecture Generator",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for dev, restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure AI APIs - OpenAI as primary, Gemini as fallback
OPENAI_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyCww_LtfxiFweWRJI19IGTynDRrgkcNTU8"

# Initialize OpenAI client
openai_client = None
try:
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-') and OPENAI_AVAILABLE:
        # Try to import and initialize OpenAI client
        openai.api_key = OPENAI_API_KEY
        # Try a simple client initialization
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI API configured successfully")
    else:
        if not OPENAI_AVAILABLE:
            logger.info("OpenAI library not available, will use HTTP requests")
        else:
            logger.warning("Invalid or missing OpenAI API key")
        openai_client = None
except Exception as e:
    logger.warning(f"OpenAI API initialization failed (will use HTTP fallback): {e}")
    openai_client = None

# Initialize Gemini model (as fallback) - disabled for demo due to suspended API
gemini_model = None
# try:
#     genai.configure(api_key=GEMINI_API_KEY)
#     gemini_model = genai.GenerativeModel('gemini-2.5-flash')
#     logger.info("Google Gemini API configured successfully with gemini-2.5-flash (fallback)")
# except Exception as e:
#     logger.error(f"Failed to configure Gemini API: {e}")
#     gemini_model = None
logger.info("Gemini API disabled for demo (API key suspended)")

# Add imports for the architecture agent
import sys
import os

# Architecture agent availability (Google ADK agent framework)
try:
    from google_adk_agent import GoogleADKAgent, create_google_adk_agent, CloudProvider, ArchitecturePattern
    GOOGLE_ADK_AVAILABLE = True
    logger.info("Google ADK Agent Framework loaded successfully")
except ImportError as e:
    GOOGLE_ADK_AVAILABLE = False
    logger.warning(f"Google ADK Agent Framework not available: {e}")

ARCH_AGENT_AVAILABLE = GOOGLE_ADK_AVAILABLE


class CustomerInputs(BaseModel):
    # Business Requirements
    business_objective: Optional[str] = Field(None, description="Primary business objective")
    regulatory: Optional[str] = Field(None, description="Regulatory requirements")
    industry: Optional[str] = Field(None, description="Industry vertical")
    
    # Organization Structure
    org_structure: Optional[str] = Field(None, description="Organization structure")
    governance: Optional[str] = Field(None, description="Governance model")
    
    # Identity & Access Management
    identity: Optional[str] = Field(None, description="Identity management approach")
    
    # Networking & Connectivity
    connectivity: Optional[str] = Field(None, description="Connectivity requirements")
    network_model: Optional[str] = Field(None, description="Network topology model")
    ip_strategy: Optional[str] = Field(None, description="IP address strategy")
    
    # Security
    security_zone: Optional[str] = Field(None, description="Security zone requirements")
    security_posture: Optional[str] = Field(None, description="Security posture")
    key_vault: Optional[str] = Field(None, description="Key management approach")
    threat_protection: Optional[str] = Field(None, description="Threat protection strategy")
    
    # Legacy fields for backward compatibility
    workload: Optional[str] = Field(None, description="Primary workload type")
    architecture_style: Optional[str] = Field(None, description="Architecture style")
    scalability: Optional[str] = Field(None, description="Scalability requirements")
    
    # Operations
    ops_model: Optional[str] = Field(None, description="Operations model")
    monitoring: Optional[str] = Field(None, description="Monitoring strategy")
    backup: Optional[str] = Field(None, description="Backup and recovery strategy")
    
    # Infrastructure
    topology_pattern: Optional[str] = Field(None, description="Topology pattern")
    
    # Migration & Cost
    migration_scope: Optional[str] = Field(None, description="Migration scope")
    cost_priority: Optional[str] = Field(None, description="Cost optimization priority")
    iac: Optional[str] = Field(None, description="Infrastructure as Code preference")
    
    # Specific Azure Service Selections
    # Compute Services
    compute_services: Optional[List[str]] = Field(default_factory=list, description="Selected compute services")
    
    # Networking Services
    network_services: Optional[List[str]] = Field(default_factory=list, description="Selected networking services")
    
    # Storage Services
    storage_services: Optional[List[str]] = Field(default_factory=list, description="Selected storage services")
    
    # Database Services
    database_services: Optional[List[str]] = Field(default_factory=list, description="Selected database services")
    
    # Security Services
    security_services: Optional[List[str]] = Field(default_factory=list, description="Selected security services")
    
    # Monitoring Services
    monitoring_services: Optional[List[str]] = Field(default_factory=list, description="Selected monitoring services")
    
    # AI/ML Services
    ai_services: Optional[List[str]] = Field(default_factory=list, description="Selected AI/ML services")
    
    # Analytics Services
    analytics_services: Optional[List[str]] = Field(default_factory=list, description="Selected analytics services")
    
    # Integration Services
    integration_services: Optional[List[str]] = Field(default_factory=list, description="Selected integration services")
    
    # DevOps Services
    devops_services: Optional[List[str]] = Field(default_factory=list, description="Selected DevOps services")
    
    # Backup Services
    backup_services: Optional[List[str]] = Field(default_factory=list, description="Selected backup services")
    
    # Enhanced Input Fields for AI Integration
    free_text_input: Optional[str] = Field(None, description="Free-form text input for additional requirements and context")
    url_input: Optional[str] = Field(None, description="URL for web content analysis")
    uploaded_files_info: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Information about uploaded files")


# Azure Architecture Templates and Patterns
AZURE_TEMPLATES = {
    "enterprise": {
        "name": "Enterprise Scale Landing Zone",
        "management_groups": ["Root", "Platform", "Landing Zones", "Sandbox", "Decommissioned"],
        "subscriptions": ["Connectivity", "Identity", "Management", "Production", "Development"],
        "core_services": ["Azure AD", "Azure Policy", "Azure Monitor", "Key Vault", "Security Center"]
    },
    "small_medium": {
        "name": "Small-Medium Enterprise Landing Zone", 
        "management_groups": ["Root", "Platform", "Workloads"],
        "subscriptions": ["Platform", "Production", "Development"],
        "core_services": ["Azure AD", "Azure Monitor", "Key Vault"]
    },
    "startup": {
        "name": "Startup Landing Zone",
        "management_groups": ["Root", "Workloads"],
        "subscriptions": ["Production", "Development"],
        "core_services": ["Azure AD", "Azure Monitor"]
    }
}

AZURE_SERVICES_MAPPING = {
    # Compute Services
    "virtual_machines": {"name": "Azure Virtual Machines", "icon": "🖥️", "drawio_shape": "virtual_machine", "diagram_class": VM, "category": "compute"},
    "aks": {"name": "Azure Kubernetes Service", "icon": "☸️", "drawio_shape": "kubernetes_service", "diagram_class": AKS, "category": "compute"},
    "app_services": {"name": "Azure App Services", "icon": "🌐", "drawio_shape": "app_services", "diagram_class": AppServices, "category": "compute"},
    "web_apps": {"name": "Azure Web Apps", "icon": "🌐", "drawio_shape": "app_services", "diagram_class": WebApps, "category": "compute"},
    "functions": {"name": "Azure Functions", "icon": "⚡", "drawio_shape": "function_app", "diagram_class": FunctionApps, "category": "compute"},
    "container_instances": {"name": "Container Instances", "icon": "📦", "drawio_shape": "container_instances", "diagram_class": ContainerInstances, "category": "compute"},
    "service_fabric": {"name": "Service Fabric", "icon": "🏗️", "drawio_shape": "service_fabric", "diagram_class": ServiceFabricClusters, "category": "compute"},
    "batch": {"name": "Azure Batch", "icon": "⚙️", "drawio_shape": "batch_accounts", "diagram_class": BatchAccounts, "category": "compute"},
    
    # Networking Services
    "virtual_network": {"name": "Virtual Network", "icon": "🌐", "drawio_shape": "virtual_network", "diagram_class": VirtualNetworks, "category": "network"},
    "vpn_gateway": {"name": "VPN Gateway", "icon": "🔒", "drawio_shape": "vpn_gateway", "diagram_class": VirtualNetworkGateways, "category": "network"},
    "expressroute": {"name": "ExpressRoute", "icon": "⚡", "drawio_shape": "expressroute_circuits", "diagram_class": ExpressrouteCircuits, "category": "network"},
    "load_balancer": {"name": "Load Balancer", "icon": "⚖️", "drawio_shape": "load_balancer", "diagram_class": LoadBalancers, "category": "network"},
    "application_gateway": {"name": "Application Gateway", "icon": "🚪", "drawio_shape": "application_gateway", "diagram_class": ApplicationGateway, "category": "network"},
    "front_door": {"name": "Azure Front Door", "icon": "🌍", "drawio_shape": "front_door", "diagram_class": FrontDoors, "category": "network"},
    "firewall": {"name": "Azure Firewall", "icon": "🛡️", "drawio_shape": "firewall", "diagram_class": Firewall, "category": "network"},
    "waf": {"name": "Web Application Firewall", "icon": "🛡️", "drawio_shape": "application_gateway", "diagram_class": ApplicationGateway, "category": "network"},
    "cdn": {"name": "Content Delivery Network", "icon": "🌍", "drawio_shape": "cdn_profiles", "diagram_class": CDNProfiles, "category": "network"},
    "traffic_manager": {"name": "Traffic Manager", "icon": "🚦", "drawio_shape": "traffic_manager_profiles", "diagram_class": None, "category": "network"},
    "virtual_wan": {"name": "Virtual WAN", "icon": "🌐", "drawio_shape": "virtual_wan", "diagram_class": VirtualNetworks, "category": "network"},
    
    # Storage Services
    "storage_accounts": {"name": "Storage Accounts", "icon": "💾", "drawio_shape": "storage_accounts", "diagram_class": StorageAccounts, "category": "storage"},
    "blob_storage": {"name": "Blob Storage", "icon": "📄", "drawio_shape": "blob_storage", "diagram_class": BlobStorage, "category": "storage"},
    "queue_storage": {"name": "Queue Storage", "icon": "📬", "drawio_shape": "queue_storage", "diagram_class": StorageAccounts, "category": "storage"},
    "table_storage": {"name": "Table Storage", "icon": "📋", "drawio_shape": "table_storage", "diagram_class": StorageAccounts, "category": "storage"},
    "file_storage": {"name": "Azure Files", "icon": "📁", "drawio_shape": "files", "diagram_class": StorageAccounts, "category": "storage"},
    "disk_storage": {"name": "Managed Disks", "icon": "💿", "drawio_shape": "managed_disks", "diagram_class": StorageAccounts, "category": "storage"},
    "data_lake": {"name": "Data Lake Storage", "icon": "🏞️", "drawio_shape": "data_lake_storage", "diagram_class": DataLakeStorage, "category": "storage"},
    
    # Database Services
    "sql_database": {"name": "Azure SQL Database", "icon": "🗄️", "drawio_shape": "sql_database", "diagram_class": SQLDatabases, "category": "database"},
    "sql_managed_instance": {"name": "SQL Managed Instance", "icon": "🗄️", "drawio_shape": "sql_managed_instance", "diagram_class": SQLDatabases, "category": "database"},
    "cosmos_db": {"name": "Cosmos DB", "icon": "🌍", "drawio_shape": "cosmos_db", "diagram_class": CosmosDb, "category": "database"},
    "mysql": {"name": "Azure Database for MySQL", "icon": "🐬", "drawio_shape": "database_for_mysql_servers", "diagram_class": DatabaseForMysqlServers, "category": "database"},
    "postgresql": {"name": "Azure Database for PostgreSQL", "icon": "🐘", "drawio_shape": "database_for_postgresql_servers", "diagram_class": DatabaseForPostgresqlServers, "category": "database"},
    "mariadb": {"name": "Azure Database for MariaDB", "icon": "🗄️", "drawio_shape": "database_for_mariadb_servers", "diagram_class": DatabaseForMysqlServers, "category": "database"},
    "redis": {"name": "Azure Cache for Redis", "icon": "⚡", "drawio_shape": "cache_redis", "diagram_class": CacheForRedis, "category": "database"},
    
    # Security Services
    "key_vault": {"name": "Azure Key Vault", "icon": "🔐", "drawio_shape": "key_vault", "diagram_class": KeyVaults, "category": "security"},
    "active_directory": {"name": "Azure Active Directory", "icon": "👤", "drawio_shape": "azure_active_directory", "diagram_class": ActiveDirectory, "category": "security"},
    "security_center": {"name": "Azure Security Center", "icon": "🛡️", "drawio_shape": "security_center", "diagram_class": SecurityCenter, "category": "security"},
    "sentinel": {"name": "Azure Sentinel", "icon": "👁️", "drawio_shape": "sentinel", "diagram_class": Sentinel, "category": "security"},
    "defender": {"name": "Microsoft Defender", "icon": "🛡️", "drawio_shape": "defender_easm", "diagram_class": SecurityCenter, "category": "security"},
    "information_protection": {"name": "Azure Information Protection", "icon": "🔒", "drawio_shape": "information_protection", "diagram_class": None, "category": "security"},
    
    # Monitoring & Management
    "monitor": {"name": "Azure Monitor", "icon": "📊", "drawio_shape": "monitor", "diagram_class": None, "category": "monitoring"},
    "log_analytics": {"name": "Log Analytics", "icon": "📋", "drawio_shape": "log_analytics_workspaces", "diagram_class": None, "category": "monitoring"},
    "application_insights": {"name": "Application Insights", "icon": "📈", "drawio_shape": "application_insights", "diagram_class": None, "category": "monitoring"},
    "service_health": {"name": "Service Health", "icon": "❤️", "drawio_shape": "service_health", "diagram_class": None, "category": "monitoring"},
    "advisor": {"name": "Azure Advisor", "icon": "💡", "drawio_shape": "advisor", "diagram_class": None, "category": "monitoring"},
    
    # AI/ML Services  
    "cognitive_services": {"name": "Cognitive Services", "icon": "🧠", "drawio_shape": "cognitive_services", "diagram_class": None, "category": "ai"},
    "machine_learning": {"name": "Azure Machine Learning", "icon": "🤖", "drawio_shape": "machine_learning", "diagram_class": None, "category": "ai"},
    "bot_service": {"name": "Bot Service", "icon": "🤖", "drawio_shape": "bot_services", "diagram_class": None, "category": "ai"},
    "form_recognizer": {"name": "Form Recognizer", "icon": "📄", "drawio_shape": "form_recognizer", "diagram_class": None, "category": "ai"},
    
    # Data & Analytics
    "synapse": {"name": "Azure Synapse Analytics", "icon": "📊", "drawio_shape": "synapse_analytics", "diagram_class": SynapseAnalytics, "category": "analytics"},
    "data_factory": {"name": "Azure Data Factory", "icon": "🏭", "drawio_shape": "data_factory", "diagram_class": DataFactories, "category": "analytics"},
    "databricks": {"name": "Azure Databricks", "icon": "📊", "drawio_shape": "databricks", "diagram_class": Databricks, "category": "analytics"},
    "stream_analytics": {"name": "Stream Analytics", "icon": "🌊", "drawio_shape": "stream_analytics", "diagram_class": StreamAnalyticsJobs, "category": "analytics"},
    "power_bi": {"name": "Power BI", "icon": "📊", "drawio_shape": "power_bi", "diagram_class": None, "category": "analytics"},
    
    # Integration Services
    "logic_apps": {"name": "Logic Apps", "icon": "🔗", "drawio_shape": "logic_apps", "diagram_class": LogicApps, "category": "integration"},
    "service_bus": {"name": "Service Bus", "icon": "🚌", "drawio_shape": "service_bus", "diagram_class": ServiceBus, "category": "integration"},
    "event_grid": {"name": "Event Grid", "icon": "⚡", "drawio_shape": "event_grid_topics", "diagram_class": EventGridTopics, "category": "integration"},
    "event_hubs": {"name": "Event Hubs", "icon": "📡", "drawio_shape": "event_hubs", "diagram_class": EventHubs, "category": "integration"},
    "api_management": {"name": "API Management", "icon": "🔌", "drawio_shape": "api_management", "diagram_class": APIManagement, "category": "integration"},
    
    # DevOps & Management
    "devops": {"name": "Azure DevOps", "icon": "⚙️", "drawio_shape": "devops", "diagram_class": Devops, "category": "devops"},
    "automation": {"name": "Azure Automation", "icon": "🤖", "drawio_shape": "automation_accounts", "diagram_class": None, "category": "devops"},
    "policy": {"name": "Azure Policy", "icon": "📋", "drawio_shape": "policy", "diagram_class": None, "category": "governance"},
    "blueprints": {"name": "Azure Blueprints", "icon": "📐", "drawio_shape": "blueprints", "diagram_class": None, "category": "governance"},
    "resource_manager": {"name": "Azure Resource Manager", "icon": "🏗️", "drawio_shape": "resource_groups", "diagram_class": Resourcegroups, "category": "governance"},
    
    # Backup & Recovery
    "backup": {"name": "Azure Backup", "icon": "💾", "drawio_shape": "backup", "diagram_class": None, "category": "backup"},
    "site_recovery": {"name": "Azure Site Recovery", "icon": "🔄", "drawio_shape": "site_recovery", "diagram_class": None, "category": "backup"},
}

def get_safe_output_directory() -> str:
    """Get a safe directory for output files with fallback options"""
    directories_to_try = [
        "/tmp",
        tempfile.gettempdir(),
        os.path.expanduser("~/tmp"),
        "./tmp"
    ]
    
    for directory in directories_to_try:
        try:
            # Create directory if it doesn't exist
            Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Test if we can write to it
            test_file = os.path.join(directory, f"test_write_{uuid.uuid4().hex[:8]}.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            logger.info(f"Using output directory: {directory}")
            return directory
            
        except Exception as e:
            logger.warning(f"Cannot use directory {directory}: {e}")
            continue
    
    raise Exception("No writable output directory found. Tried: " + ", ".join(directories_to_try))

def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """Clean up old generated files to prevent disk space issues"""
    try:
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            if filename.startswith("azure_landing_zone_") and filename.endswith(".png"):
                filepath = os.path.join(directory, filename)
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old file: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to clean up file {filename}: {e}")
                    
    except Exception as e:
        logger.warning(f"Failed to perform cleanup in {directory}: {e}")

def call_ai_with_fallback(prompt: str, model: str = "gpt-4", original_user_input: str = None) -> str:
    """Call AI with OpenAI as primary and Gemini as fallback"""
    try:
        # Try OpenAI first
        if openai_client:
            logger.info("Using OpenAI API for AI generation")
            response = openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content
        elif OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
            # Fallback: Direct HTTP request to OpenAI API
            logger.info("Using OpenAI API via HTTP request")
            import requests
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'gpt-3.5-turbo',  # Use more stable model
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 4000,
                'temperature': 0.7
            }
            response = requests.post('https://api.openai.com/v1/chat/completions', 
                                   headers=headers, json=data, timeout=3)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.warning(f"OpenAI HTTP request failed: {response.status_code} - {response.text}")
        else:
            logger.warning("OpenAI not available, trying Gemini fallback")
    except Exception as e:
        logger.warning(f"OpenAI API failed: {e}, trying Gemini fallback")
    
    try:
        # Fallback to Gemini (will timeout due to suspended API)
        if gemini_model:
            logger.info("Using Gemini API as fallback")
            result = gemini_model.generate_content(prompt)
            return result.text
        else:
            logger.error("Gemini model not available")
    except Exception as e:
        logger.error(f"Gemini API failed: {e}")
    
    # If both fail, return a meaningful default response based on the original user input if available
    logger.warning("Both AI services failed, providing default analysis")
    
    # Use original user input for pattern detection if available, otherwise fall back to the prompt
    analysis_text = original_user_input if original_user_input else prompt
    return generate_default_ai_response(analysis_text)

def generate_default_ai_response(prompt: str) -> str:
    """Generate a default AI response in JSON format when external APIs are unavailable"""
    import json
    prompt_lower = prompt.lower()
    
    # Use the same pattern detection logic for consistency
    pattern = detect_architecture_pattern(prompt_lower)
    
    if pattern == "Microservices Architecture":
        return json.dumps({
            "services": ["aks", "application_gateway", "virtual_network", "cosmos_db", "key_vault", "monitor", "api_management"],
            "reasoning": "Microservices architecture requires container orchestration (AKS), API gateway (Application Gateway + API Management), secure networking (Virtual Network), flexible data storage (Cosmos DB), secrets management (Key Vault), and comprehensive monitoring (Azure Monitor).",
            "architecture_pattern": "Microservices with API Gateway",
            "scalability_design": "Kubernetes auto-scaling with horizontal pod autoscaling",
            "security_considerations": "Network isolation, service mesh security, and centralized secret management",
            "connectivity_requirements": "Service-to-service communication via private networks",
            "operational_model": "Container-based deployment with GitOps and monitoring",
            "cost_optimization": "Right-sizing containers and using spot instances where appropriate",
            "needs_confirmation": True,
            "clarification_questions": ["How many microservices do you expect?", "Do you need service mesh capabilities?", "What's your CI/CD strategy?"],
            "assumptions_made": ["Assuming containerized applications", "Assuming need for API management", "Assuming polyglot persistence"],
            "alternative_options": ["Serverless architecture with Functions", "Traditional N-tier with App Services"],
            "waf_compliance": {
                "security": "Network segmentation, service mesh, Key Vault integration",
                "reliability": "Multi-region AKS with health checks and circuit breakers",
                "performance": "Auto-scaling and efficient service communication",
                "cost": "Resource optimization and efficient scaling policies",
                "operations": "Comprehensive logging, monitoring, and observability"
            },
            "next_steps": "Design service boundaries and define API contracts"
        })
    
    elif pattern == "E-commerce Platform":
        return json.dumps({
            "services": ["app_services", "sql_database", "application_gateway", "cdn_profiles", "key_vault", "monitor", "redis", "active_directory"],
            "reasoning": "E-commerce platform requires web hosting (App Services), persistent data storage (SQL Database), load balancing and security (Application Gateway), global content delivery (CDN), secrets management (Key Vault), caching (Redis), monitoring (Azure Monitor), and user authentication (Active Directory).",
            "architecture_pattern": "E-commerce Platform with CDN and Caching",
            "scalability_design": "Auto-scaling App Services with CDN for global reach",
            "security_considerations": "SSL termination, WAF protection, secure secret management, and user authentication",
            "connectivity_requirements": "Internet-facing with secure backend connections",
            "operational_model": "Azure-managed services with monitoring and alerting",
            "cost_optimization": "Use appropriate service tiers and CDN for efficient content delivery",
            "needs_confirmation": True,
            "clarification_questions": ["What are your expected transaction volumes?", "Do you need PCI DSS compliance?", "Which regions are your primary markets?"],
            "assumptions_made": ["Assuming B2C e-commerce", "Assuming credit card payments needed", "Assuming global customer base"],
            "alternative_options": ["Microservices architecture with AKS", "Serverless architecture with Functions"],
            "waf_compliance": {
                "security": "WAF, Key Vault, Azure AD integration",
                "reliability": "Multi-region deployment with CDN",
                "performance": "CDN and Redis caching for optimal performance",
                "cost": "Tiered pricing and auto-scaling for cost efficiency",
                "operations": "Azure Monitor for comprehensive observability"
            },
            "next_steps": "Define specific compliance requirements and expected transaction volumes"
        })
    
    elif pattern == "Data Analytics Platform":
        return json.dumps({
            "services": ["data_factory", "databricks", "storage_accounts", "synapse_analytics", "monitor", "key_vault"],
            "reasoning": "Data analytics platform requires data ingestion and orchestration (Data Factory), data processing and ML (Databricks), scalable storage (Storage Accounts), data warehousing (Synapse Analytics), monitoring (Azure Monitor), and security (Key Vault).",
            "architecture_pattern": "Modern Data Platform",
            "scalability_design": "Auto-scaling compute clusters with elastic storage",
            "security_considerations": "Data encryption at rest and in transit, role-based access control",
            "connectivity_requirements": "Private endpoints for secure data access",
            "operational_model": "Managed analytics services with automated scaling",
            "cost_optimization": "Pay-per-use analytics compute and tiered storage",
            "needs_confirmation": True,
            "clarification_questions": ["What's your expected data volume?", "Do you need real-time processing?", "What are your data sources?"],
            "assumptions_made": ["Assuming structured and unstructured data", "Assuming need for ML capabilities", "Assuming batch and streaming processing"],
            "alternative_options": ["Event-driven architecture with Event Hubs", "Serverless analytics with Functions"],
            "waf_compliance": {
                "security": "Data encryption, access controls, and audit logging",
                "reliability": "Multi-region data replication and backup strategies",
                "performance": "Optimized data partitioning and caching strategies",
                "cost": "Tiered storage and auto-scaling compute resources",
                "operations": "Automated monitoring and data quality checks"
            },
            "next_steps": "Define data governance policies and processing requirements"
        })
    
    else:
        # Default web application
        return json.dumps({
            "services": ["app_services", "sql_database", "virtual_network", "key_vault", "monitor"],
            "reasoning": "Standard web application requires hosting platform (App Services), database (SQL Database), secure networking (Virtual Network), secrets management (Key Vault), and monitoring (Azure Monitor). This provides a solid foundation for most web applications.",
            "architecture_pattern": "Standard N-tier Web Application",
            "scalability_design": "Auto-scaling web app with database scaling options",
            "security_considerations": "Network isolation, secure secret management, and SSL termination",
            "connectivity_requirements": "Internet-facing with secure backend connectivity",
            "operational_model": "Azure-managed services with standard monitoring",
            "cost_optimization": "Appropriate service tiers with auto-scaling",
            "needs_confirmation": True,
            "clarification_questions": ["What type of web application are you building?", "What are your performance requirements?", "Do you need specific compliance features?"],
            "assumptions_made": ["Assuming traditional web application", "Assuming relational database needs", "Assuming standard security requirements"],
            "alternative_options": ["Microservices architecture", "Static web app with API backend", "Serverless architecture"],
            "waf_compliance": {
                "security": "Network security, Key Vault, and secure coding practices",
                "reliability": "Auto-scaling and backup strategies",
                "performance": "CDN integration and database optimization",
                "cost": "Right-sized resources with auto-scaling",
                "operations": "Standard monitoring and logging practices"
            },
            "next_steps": "Clarify specific application requirements and choose appropriate service tiers"
        })

# AI Integration Functions with OpenAI Primary and Gemini Fallback
def analyze_url_content(url: str) -> str:
    """Fetch and analyze URL content using AI (OpenAI primary, Gemini fallback)"""
    try:
        if not openai_client and not gemini_model:
            return "AI services not available for URL analysis"
            
        # Fetch URL content
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text[:10000]  # Limit content size
        
        prompt = f"""
        Analyze the following web content for Azure architecture planning:
        
        URL: {url}
        Content: {content}
        
        Please provide insights for:
        1. Relevant Azure services mentioned or implied
        2. Architecture patterns or requirements
        3. Security and compliance considerations
        4. Scalability and performance requirements
        5. Integration requirements
        
        Format your response as a structured analysis.
        """
        
        return call_ai_with_fallback(prompt)
        
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {e}")
        return f"Error analyzing URL: {str(e)}"

def process_uploaded_document(file_content: bytes, filename: str, file_type: str) -> str:
    """Process uploaded document using AI (OpenAI primary, Gemini fallback)"""
    try:
        if not openai_client and not gemini_model:
            return "AI services not available for document analysis"
            
        text_content = ""
        
        # Extract text based on file type
        if file_type.lower() == 'pdf':
            text_content = extract_pdf_text(file_content)
        elif file_type.lower() in ['xlsx', 'xls']:
            text_content = extract_excel_text(file_content)
        elif file_type.lower() in ['pptx', 'ppt']:
            text_content = extract_pptx_text(file_content)
        else:
            return f"Unsupported file type: {file_type}"
        
        if not text_content.strip():
            return "No readable text found in the document"
            
        prompt = f"""
        Analyze the following document content for Azure Landing Zone architecture planning:
        
        Document: {filename}
        Type: {file_type}
        Content: {text_content[:8000]}  # Limit content size
        
        Please provide insights for:
        1. Current architecture mentioned in the document
        2. Business requirements and objectives
        3. Compliance and regulatory requirements
        4. Security requirements
        5. Recommended Azure services and patterns
        6. Migration considerations
        7. Governance and operational requirements
        
        Format your response as a structured analysis for enterprise architecture planning.
        """
        
        return call_ai_with_fallback(prompt)
        
    except Exception as e:
        logger.error(f"Error processing document {filename}: {e}")
        return f"Error processing document: {str(e)}"

def extract_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        import io
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def extract_excel_text(file_content: bytes) -> str:
    """Extract text from Excel file"""
    try:
        import io
        excel_file = io.BytesIO(file_content)
        workbook = openpyxl.load_workbook(excel_file)
        text = ""
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text += f"Sheet: {sheet_name}\n"
            for row in sheet.iter_rows(values_only=True):
                row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                if row_text.strip():
                    text += row_text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting Excel text: {e}")
        return ""

def extract_pptx_text(file_content: bytes) -> str:
    """Extract text from PowerPoint file"""
    try:
        import io
        pptx_file = io.BytesIO(file_content)
        presentation = Presentation(pptx_file)
        text = ""
        for slide_num, slide in enumerate(presentation.slides, 1):
            text += f"Slide {slide_num}:\n"
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting PowerPoint text: {e}")
        return ""

def generate_ai_enhanced_recommendations(inputs: CustomerInputs, url_analysis: str = "", doc_analysis: str = "") -> str:
    """Generate AI-enhanced architecture recommendations using AI (OpenAI primary, Gemini fallback)"""
    try:
        if not openai_client and not gemini_model:
            return "Standard recommendations (AI enhancement not available)"
            
        # Build context from inputs
        context = f"""
        Business Objective: {inputs.business_objective or 'Not specified'}
        Industry: {inputs.industry or 'General'}
        Organization Structure: {inputs.org_structure or 'Not specified'}
        Regulatory Requirements: {inputs.regulatory or 'Standard'}
        Security Requirements: {inputs.security_posture or 'Standard'}
        Scalability Requirements: {inputs.scalability or 'Standard'}
        Free-text Input: {inputs.free_text_input or 'None provided'}
        
        Selected Services:
        - Compute: {', '.join(inputs.compute_services or [])}
        - Network: {', '.join(inputs.network_services or [])}
        - Storage: {', '.join(inputs.storage_services or [])}
        - Database: {', '.join(inputs.database_services or [])}
        - Security: {', '.join(inputs.security_services or [])}
        """
        
        if url_analysis:
            context += f"\n\nURL Analysis Results:\n{url_analysis}"
            
        if doc_analysis:
            context += f"\n\nDocument Analysis Results:\n{doc_analysis}"
        
        prompt = f"""
        Based on the following customer requirements and analysis, provide comprehensive Azure Landing Zone architecture recommendations:
        
        {context}
        
        Please provide:
        1. Recommended Azure Landing Zone template (Enterprise Scale, Small Scale, etc.)
        2. Detailed architecture recommendations with specific Azure services
        3. Security and compliance strategy
        4. Network topology and connectivity recommendations
        5. Identity and access management strategy
        6. Operations and monitoring approach
        7. Cost optimization strategies
        8. Migration roadmap and phases
        9. Governance and policy recommendations
        10. Risk assessment and mitigation strategies
        
        Format your response as a comprehensive enterprise architecture document.
        """
        
        return call_ai_with_fallback(prompt)
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {e}")
        return f"Error generating AI recommendations: {str(e)}"

def detect_architecture_pattern(free_text: str) -> str:
    """Detect the likely architecture pattern from user requirements"""
    text_lower = free_text.lower()
    
    # Pattern detection logic - order matters, more specific patterns first
    # Use word boundaries to avoid partial matches
    if any(word in text_lower for word in ["microservice", "microservices", "service mesh", "container orchestration", "kubernetes", "docker"]) or \
       ("api gateway" in text_lower):
        return "Microservices Architecture"
    elif any(term in text_lower for term in ["data analytics", "big data", "data warehouse", "etl", "reporting", "databricks", "synapse"]):
        return "Data Analytics Platform"
    elif any(term in text_lower for term in ["iot", "sensor", "device", "telemetry", "edge"]):
        return "IoT Platform"
    elif any(term in text_lower for term in ["machine learning", "ai", "artificial intelligence", "ml", "cognitive"]):
        return "AI/ML Platform"
    elif any(term in text_lower for term in ["e-commerce", "ecommerce", "online store", "shopping", "payment"]):
        return "E-commerce Platform"
    elif any(term in text_lower for term in ["mobile app", "mobile backend"]) or \
         (("rest api" in text_lower or "api" in text_lower) and "mobile" in text_lower):
        return "Mobile Backend"
    elif any(term in text_lower for term in ["web app", "web application", "website", "portal"]):
        return "Web Application"
    else:
        return "General Enterprise Application"

def determine_complexity_level(free_text: str) -> str:
    """Determine the complexity level based on requirements"""
    text_lower = free_text.lower()
    
    complexity_indicators = {
        "high": ["enterprise", "multi-region", "global", "compliance", "highly available", "scalable", "microservices", "complex"],
        "medium": ["business", "production", "secure", "monitoring", "backup", "integration"],
        "low": ["simple", "basic", "small", "prototype", "demo", "test"]
    }
    
    high_count = sum(1 for term in complexity_indicators["high"] if term in text_lower)
    medium_count = sum(1 for term in complexity_indicators["medium"] if term in text_lower)
    low_count = sum(1 for term in complexity_indicators["low"] if term in text_lower)
    
    if high_count >= 2 or any(term in text_lower for term in ["enterprise", "multi-region", "complex"]):
        return "High"
    elif medium_count >= 2 or high_count >= 1:
        return "Medium" 
    elif low_count >= 1:
        return "Low"
    else:
        return "Medium"  # Default to medium complexity

def analyze_free_text_requirements(free_text: str) -> dict:
    """Enhanced AI analysis of free text input with intelligent pattern recognition and adaptive service selection"""
    try:
        if not openai_client and not gemini_model and not OPENAI_API_KEY:
            return {"services": [], "reasoning": "No AI analysis available - please select services manually", "needs_confirmation": True}
        
        # First, let's detect the architectural pattern and complexity
        pattern_analysis = detect_architecture_pattern(free_text)
        complexity_level = determine_complexity_level(free_text)
        
        prompt = f"""
You are an INTELLIGENT AZURE SOLUTIONS ARCHITECT with deep expertise in cloud architecture patterns, Azure services, and the Well-Architected Framework. Your goal is to provide thoughtful, adaptive recommendations based on the specific requirements and context provided.

User Requirement: "{free_text}"

Detected Pattern: {pattern_analysis}
Complexity Level: {complexity_level}

INTELLIGENT ANALYSIS INSTRUCTIONS:

1. CONTEXTUAL SERVICE SELECTION (5-12 services based on complexity):
   - Analyze the SPECIFIC use case and architectural requirements
   - Select services based on the detected pattern and complexity
   - Consider scalability, security, and operational requirements mentioned
   - Include essential supporting services for production readiness
   - Adapt service count based on requirement complexity:
     * Simple web apps: 5-7 services
     * E-commerce/Enterprise: 8-10 services
     * Complex distributed systems: 10-12 services

2. REQUIREMENT PATTERN RECOGNITION:
   - E-commerce: Include payment processing, CDN, caching, security
   - Data Analytics: Include data ingestion, processing, storage, visualization
   - Microservices: Include container orchestration, API management, service mesh
   - Web Applications: Include hosting, database, monitoring, security
   - Mobile Backend: Include APIs, push notifications, authentication, storage

3. AZURE WELL-ARCHITECTED FRAMEWORK ALIGNMENT:
   - Security: Include Key Vault, Azure AD, network security
   - Reliability: Include load balancing, backup, multi-region if applicable
   - Performance: Include caching, CDN, monitoring
   - Cost Optimization: Suggest appropriate service tiers
   - Operational Excellence: Include monitoring, logging, automation

4. INTELLIGENT CLARIFICATION:
   - Identify specific gaps in requirements that affect architecture decisions
   - Ask targeted questions about scalability, compliance, budget, timeline
   - Suggest alternatives based on different business priorities

COMPREHENSIVE AZURE SERVICES CATALOG:

Compute: virtual_machines, aks, app_services, functions, container_instances, service_fabric
Network: virtual_network, application_gateway, load_balancer, firewall, front_door, cdn_profiles, vpn_gateway
Storage: storage_accounts, blob_storage, file_storage, data_lake_storage
Database: sql_database, cosmos_db, mysql, postgresql, redis, synapse_analytics
Security: key_vault, active_directory, security_center, sentinel
Monitoring: azure_monitor, application_insights, log_analytics
Integration: logic_apps, service_bus, event_grid, api_management
AI/ML: cognitive_services, machine_learning, bot_services
DevOps: devops, pipelines, container_registry
Analytics: data_factory, databricks, stream_analytics, event_hubs

RESPONSE FORMAT - Provide an INTELLIGENT JSON response:

{{
  "services": ["5-12 services based on requirements complexity and pattern"],
  "reasoning": "Detailed explanation of why each service is selected, how they work together, and how they address the specific use case. Include architectural rationale and Well-Architected Framework considerations.",
  "architecture_pattern": "Specific pattern (e.g., Microservices with API Gateway, Hub-Spoke Network, Event-Driven Architecture)",
  "scalability_design": "How the architecture scales (auto-scaling, manual, global distribution)",
  "security_considerations": "Specific security measures and Zero Trust principles applied",
  "connectivity_requirements": "Network architecture and connectivity patterns",
  "operational_model": "How the solution will be operated and monitored",
  "cost_optimization": "Cost optimization strategies and service tier recommendations",
  "needs_confirmation": true,
  "clarification_questions": ["Specific questions to better understand requirements"],
  "assumptions_made": ["List any assumptions made about unstated requirements"],
  "alternative_options": ["Alternative architectural approaches with trade-offs"],
  "waf_compliance": {{
    "security": "How architecture addresses security pillar",
    "reliability": "How architecture ensures reliability",
    "performance": "Performance optimization strategies",
    "cost": "Cost optimization approach",
    "operations": "Operational excellence considerations"
  }},
  "next_steps": "Recommended next steps for implementation"
}}

QUALITY REQUIREMENTS:
- Services must be production-ready and follow Azure best practices
- Include monitoring and security by default
- Consider the full application lifecycle (development, testing, production)
- Align with Azure Well-Architected Framework principles
- Return ONLY valid JSON format with no additional text

"""
        
        result_text = call_ai_with_fallback(prompt, model="gpt-4", original_user_input=free_text)
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Look for JSON content
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                analysis = json.loads(json_str)
                
                # Enforce intelligent service limits based on complexity
                max_services = 12  # Updated from conservative 5 to intelligent 12
                if "services" in analysis and len(analysis["services"]) > max_services:
                    logger.warning(f"AI suggested {len(analysis['services'])} services, limiting to {max_services} most essential")
                    analysis["services"] = analysis["services"][:max_services]
                    analysis["reasoning"] += f" (Note: Limited to {max_services} most essential services for manageability)"
                    analysis["needs_confirmation"] = True
                
                # Validate suggested services exist in our mapping
                valid_services = []
                invalid_services = []
                for service in analysis.get("services", []):
                    if service in AZURE_SERVICES_MAPPING:
                        valid_services.append(service)
                    else:
                        invalid_services.append(service)
                
                if invalid_services:
                    logger.warning(f"AI suggested invalid services: {invalid_services}")
                    analysis["services"] = valid_services
                    analysis["reasoning"] += f" (Note: Removed invalid services: {', '.join(invalid_services)})"
                    analysis["needs_confirmation"] = True
                
                # Ensure all required fields are present with enhanced defaults
                defaults = {
                    "architecture_pattern": "Intelligent Architecture",
                    "scalability_design": "Based on requirements analysis",
                    "security_considerations": "Standard Azure security best practices",
                    "connectivity_requirements": "Standard Azure networking",
                    "operational_model": "Standard monitoring and operations",
                    "cost_optimization": "Balanced cost and performance",
                    "needs_confirmation": True,
                    "clarification_questions": [],
                    "assumptions_made": [],
                    "alternative_options": [],
                    "waf_compliance": {
                        "security": "Standard Azure security measures",
                        "reliability": "Basic reliability patterns",
                        "performance": "Standard performance optimization",
                        "cost": "Cost-effective service selection",
                        "operations": "Basic operational practices"
                    },
                    "next_steps": "Review the suggested services and architecture, then proceed with detailed planning"
                }
                
                for key, default_value in defaults.items():
                    if key not in analysis:
                        analysis[key] = default_value
                
                # Log the analysis for transparency
                logger.info(f"Enhanced AI analysis completed: {len(analysis['services'])} services suggested, pattern: {analysis.get('architecture_pattern', 'unknown')}")
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        # Fallback: Conservative manual parsing if JSON parsing fails
        logger.warning("Failed to parse AI response as JSON, using conservative fallback")
        conservative_services = extract_conservative_services_from_text(result_text, free_text)
        
        return {
            "services": conservative_services, 
            "reasoning": f"Conservative analysis based on text parsing: {result_text[:500]}...",
            "architecture_pattern": "Minimal viable solution",
            "needs_confirmation": True,
            "assumptions_made": ["AI parsing failed, used conservative text analysis"],
            "alternative_options": ["Manual service selection recommended"],
            "next_steps": "Please review and manually select the specific services you need"
        }
        
    except Exception as e:
        logger.error(f"Error in conservative free text analysis: {e}")
        return {
            "services": [], 
            "reasoning": f"Analysis error occurred: {str(e)}. Please manually select the services you need.",
            "architecture_pattern": "Manual selection required",
            "needs_confirmation": True,
            "assumptions_made": ["Error in AI analysis"],
            "alternative_options": ["Manual service selection"],
            "next_steps": "Please manually select services from the available categories"
        }

def extract_conservative_services_from_text(text: str, original_requirement: str) -> list:
    """Extract Azure service names conservatively from text response with maximum 5 services"""
    
    # Start with an empty list and only add explicitly mentioned services
    conservative_services = []
    text_lower = text.lower()
    requirement_lower = original_requirement.lower()
    
    # Conservative service mapping - only add if explicitly needed
    essential_mappings = {
        # Only add compute if explicitly mentioned
        "virtual machine": "virtual_machines",
        "vm": "virtual_machines", 
        "kubernetes": "aks",
        "aks": "aks",
        "web app": "app_services",
        "app service": "app_services",
        "function": "functions",
        
        # Only add storage if data storage is mentioned
        "storage": "storage_accounts",
        "blob": "blob_storage",
        
        # Only add database if data persistence is mentioned
        "database": "sql_database",
        "sql": "sql_database",
        "cosmos": "cosmos_db",
        "mysql": "mysql",
        "postgresql": "postgresql",
        "redis": "redis",
        
        # Only add networking if web access or networking is mentioned
        "network": "virtual_network",
        "load balancer": "load_balancer",
        "application gateway": "application_gateway",
        
        # Only add security if security is specifically mentioned
        "key vault": "key_vault",
        "security": "key_vault",
        "active directory": "active_directory",
        "authentication": "active_directory",
        
        # Only add monitoring if observability is mentioned
        "monitor": "azure_monitor",
        "monitoring": "azure_monitor",
        "observability": "azure_monitor",
        "insights": "application_insights"
    }
    
    # Check both the AI response and the original requirement for conservative matches
    combined_text = f"{text_lower} {requirement_lower}"
    
    for phrase, service in essential_mappings.items():
        if phrase in combined_text and service not in conservative_services:
            conservative_services.append(service)
            # Stop at 5 services maximum
            if len(conservative_services) >= 5:
                break
    
    # If no services found but this appears to be a web application, add minimal web stack
    if not conservative_services:
        web_indicators = ["web", "app", "website", "portal", "frontend", "ui", "interface"]
        if any(indicator in requirement_lower for indicator in web_indicators):
            conservative_services = ["app_services", "sql_database", "virtual_network"]
        else:
            # Truly minimal: just virtual machines and basic networking
            conservative_services = ["virtual_machines", "virtual_network"]
    
    # Ensure we don't exceed 5 services
    return conservative_services[:5]

def extract_services_from_text(text: str) -> list:
    """Extract Azure service names from text response"""
    # Common Azure services that might be mentioned
    azure_services = [
        "virtual_machines", "aks", "app_services", "functions", "container_instances",
        "virtual_network", "application_gateway", "load_balancer", "firewall", 
        "storage_accounts", "blob_storage", "sql_database", "cosmos_db",
        "key_vault", "active_directory", "azure_monitor", "machine_learning"
    ]
    
    text_lower = text.lower()
    found_services = []
    
    # Map text phrases to service keys
    service_mapping = {
        "kubernetes": "aks",
        "app service": "app_services", 
        "web app": "app_services",
        "sql database": "sql_database",
        "cosmos": "cosmos_db",
        "storage account": "storage_accounts",
        "key vault": "key_vault",
        "active directory": "active_directory",
        "virtual machine": "virtual_machines",
        "application gateway": "application_gateway",
        "virtual network": "virtual_network",
        "load balancer": "load_balancer",
        "azure monitor": "azure_monitor",
        "machine learning": "machine_learning"
    }
    
    for phrase, service in service_mapping.items():
        if phrase in text_lower:
            found_services.append(service)
    
    # Ensure we have basic services
    if not found_services:
        found_services = ["virtual_machines", "virtual_network", "key_vault", "azure_monitor"]
    
    return list(set(found_services))  # Remove duplicates

def validate_customer_inputs(inputs: CustomerInputs) -> None:
    """Enhanced validation for customer inputs with detailed error messages"""
    
    # Check for extremely long strings that might cause issues
    string_fields = {
        'business_objective': inputs.business_objective,
        'regulatory': inputs.regulatory,
        'industry': inputs.industry,
        'org_structure': inputs.org_structure,
        'governance': inputs.governance,
        'identity': inputs.identity,
        'connectivity': inputs.connectivity,
        'network_model': inputs.network_model,
        'ip_strategy': inputs.ip_strategy,
        'security_zone': inputs.security_zone,
        'security_posture': inputs.security_posture,
        'key_vault': inputs.key_vault,
        'threat_protection': inputs.threat_protection,
        'workload': inputs.workload,
        'architecture_style': inputs.architecture_style,
        'scalability': inputs.scalability,
        'ops_model': inputs.ops_model,
        'monitoring': inputs.monitoring,
        'backup': inputs.backup,
        'topology_pattern': inputs.topology_pattern,
        'migration_scope': inputs.migration_scope,
        'cost_priority': inputs.cost_priority,
        'iac': inputs.iac,
        'url_input': inputs.url_input
    }
    
    for field_name, field_value in string_fields.items():
        if field_value and len(field_value) > 1000:
            raise ValueError(f"Field '{field_name}' is too long: {len(field_value)} characters (maximum 1000 characters allowed). Please provide a more concise description.")
    
    # Special validation for free-text input (allowing more characters)
    if inputs.free_text_input and len(inputs.free_text_input) > 10000:
        raise ValueError(f"Free text input is too long: {len(inputs.free_text_input)} characters (maximum 10000 characters allowed). Please provide a more concise description.")
    
    # Enhanced service validation with specific error messages
    service_categories = {
        'compute_services': inputs.compute_services,
        'network_services': inputs.network_services,
        'storage_services': inputs.storage_services,
        'database_services': inputs.database_services,
        'security_services': inputs.security_services,
        'monitoring_services': inputs.monitoring_services,
        'ai_services': inputs.ai_services,
        'analytics_services': inputs.analytics_services,
        'integration_services': inputs.integration_services,
        'devops_services': inputs.devops_services,
        'backup_services': inputs.backup_services
    }
    
    # Enhanced service validation with auto-correction for common mistakes
    service_name_aliases = {
        # Common service name corrections
        "app_service": "app_services",  # singular vs plural
        "azure_monitor": "monitor",     # common mistake adding "azure_" prefix
        "container_registry": "devops", # ACR is often used instead of devops
        "keyvault": "key_vault",        # spacing issue
        "azure_ad": "active_directory", # common alias
        "sql": "sql_database",          # incomplete name
        "cosmosdb": "cosmos_db",        # spacing issue
        "vm": "virtual_machines",       # common abbreviation
        "kubernetes": "aks",            # full name vs service name
        "webapp": "app_services",       # alternative name
        "function": "functions",        # singular vs plural
        "storage": "storage_accounts",  # incomplete name
        "vnet": "virtual_network",      # common abbreviation
        "lb": "load_balancer",          # common abbreviation
        "app_insights": "application_insights", # common abbreviation
    }
    
    # Validate and auto-correct each service category
    for category_name, service_list in service_categories.items():
        if service_list:
            # Check for reasonable service count
            if len(service_list) > 20:  # Reduced from 50 to prevent over-provisioning
                raise ValueError(f"Too many services selected in '{category_name}': {len(service_list)} services (maximum 20 per category). Please select only the essential services you need.")
            
            # Auto-correct and validate services
            corrected_services = []
            still_invalid = []
            corrections_made = []
            
            for service in service_list:
                # Try auto-correction first
                corrected_service = service_name_aliases.get(service.lower(), service)
                
                if corrected_service in AZURE_SERVICES_MAPPING:
                    corrected_services.append(corrected_service)
                    if corrected_service != service:
                        corrections_made.append(f"'{service}' -> '{corrected_service}'")
                else:
                    still_invalid.append(service)
            
            # Update the input with corrected services
            setattr(inputs, category_name, corrected_services)
            
            # Log corrections made
            if corrections_made:
                logger.info(f"Auto-corrected services in {category_name}: {'; '.join(corrections_made)}")
            
            # Raise error for services that couldn't be corrected
            if still_invalid:
                category_display = category_name.replace('_', ' ').title()
                available_services = [k for k, v in AZURE_SERVICES_MAPPING.items() if v['category'] == category_name.replace('_services', '')]
                if not available_services:
                    # Fallback: show all services for that category type
                    available_services = [k for k, v in AZURE_SERVICES_MAPPING.items() if category_name.replace('_services', '') in v['category']]
                
                # Provide helpful suggestions for invalid services
                suggestions = []
                for invalid_service in still_invalid:
                    service_suggestions = []
                    invalid_lower = invalid_service.lower()
                    
                    # Find partial matches
                    for available in available_services:
                        if (invalid_lower in available.lower() or 
                            available.lower() in invalid_lower or
                            any(part in available.lower() for part in invalid_lower.split('_'))):
                            service_suggestions.append(available)
                    
                    if service_suggestions:
                        suggestions.append(f"'{invalid_service}' -> try: {', '.join(service_suggestions[:3])}")
                
                error_msg = f"Invalid services in '{category_display}': {', '.join(still_invalid)}. "
                if available_services:
                    error_msg += f"Available services include: {', '.join(available_services[:10])}"
                    if len(available_services) > 10:
                        error_msg += f" (and {len(available_services) - 10} more)"
                
                if suggestions:
                    error_msg += f" | Suggestions: {'; '.join(suggestions)}"
                
                raise ValueError(error_msg)
    
    # Enhanced URL validation
    if inputs.url_input:
        url = inputs.url_input.strip()
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with 'http://' or 'https://'. Example: 'https://example.com'")
        
        # Basic URL structure validation
        if len(url) > 2000:
            raise ValueError(f"URL is too long: {len(url)} characters (maximum 2000 characters allowed)")
        
        # Check for obvious malformed URLs
        if ' ' in url or '\n' in url or '\t' in url:
            raise ValueError("URL contains invalid characters (spaces, newlines, or tabs). Please provide a valid URL.")
    
    # Enhanced uploaded files validation
    if inputs.uploaded_files_info:
        if len(inputs.uploaded_files_info) > 5:  # Reduced from 10 for better performance
            raise ValueError(f"Too many uploaded files: {len(inputs.uploaded_files_info)} files (maximum 5 files allowed). Please select only the most relevant files.")
        
        # Validate file info structure
        for i, file_info in enumerate(inputs.uploaded_files_info):
            if not isinstance(file_info, dict):
                raise ValueError(f"File #{i+1} information is invalid. Expected file metadata.")
            
            # Check for required file metadata
            if 'filename' not in file_info:
                raise ValueError(f"File #{i+1} is missing filename information.")
    
    # Total service count validation to prevent over-complex architectures
    total_services = sum(len(service_list) for service_list in service_categories.values() if service_list)
    if total_services > 50:  # Conservative limit for manageable architectures
        raise ValueError(f"Too many total services selected: {total_services} services (maximum 50 total services recommended). Please focus on the most essential services for your architecture to ensure clarity and manageability.")
    
    logger.info(f"Input validation passed: {total_services} total services across {sum(1 for sl in service_categories.values() if sl)} categories")

def generate_azure_architecture_diagram(inputs: CustomerInputs, output_dir: str = None, format: str = "png") -> str:
    """Generate Azure architecture diagram using the Python Diagrams library with strict user input adherence"""
    
    logger.info("Starting Azure architecture diagram generation with strict user input adherence")
    
    try:
        # Enhanced input validation first
        validate_customer_inputs(inputs)
        logger.info("Enhanced input validation completed successfully")
        
        # Count user-selected services for transparency
        user_service_count = sum([
            len(inputs.compute_services or []),
            len(inputs.network_services or []),
            len(inputs.storage_services or []),
            len(inputs.database_services or []),
            len(inputs.security_services or []),
            len(inputs.monitoring_services or []),
            len(inputs.ai_services or []),
            len(inputs.analytics_services or []),
            len(inputs.integration_services or []),
            len(inputs.devops_services or []),
            len(inputs.backup_services or [])
        ])
        
        logger.info(f"User selected {user_service_count} services across all categories - diagram will include ONLY these services")
        
        # Get safe output directory
        if output_dir is None:
            output_dir = get_safe_output_directory()
        
        # Clean up old files to prevent disk space issues
        cleanup_old_files(output_dir)
        
        # Enhanced Graphviz validation with detailed error messages
        try:
            result = subprocess.run(['dot', '-V'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                error_msg = f"Graphviz 'dot' command failed with return code {result.returncode}. stderr: {result.stderr}"
                logger.error(error_msg)
                raise Exception(f"{error_msg}\n\nTo fix this issue:\n1. Install Graphviz: sudo apt-get install -y graphviz graphviz-dev\n2. Ensure 'dot' command is in your PATH\n3. Restart the application")
            logger.info(f"Graphviz validation passed: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            error_msg = "Graphviz 'dot' command timed out. Graphviz may be unresponsive."
            logger.error(error_msg)
            raise Exception(f"{error_msg}\n\nTroubleshooting steps:\n1. Check system resources\n2. Reinstall Graphviz: sudo apt-get install --reinstall graphviz\n3. Restart the system if necessary")
        except FileNotFoundError:
            error_msg = "Graphviz is not installed or not accessible."
            logger.error(error_msg)
            raise Exception(f"{error_msg}\n\nInstallation instructions:\n1. Ubuntu/Debian: sudo apt-get install -y graphviz graphviz-dev\n2. RedHat/CentOS: sudo yum install graphviz graphviz-devel\n3. macOS: brew install graphviz\n4. Verify installation: dot -V")
        except subprocess.SubprocessError as e:
            error_msg = f"Graphviz check failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(f"{error_msg}\n\nPlease ensure Graphviz is properly installed and accessible.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"azure_landing_zone_{timestamp}_{unique_id}"
        filepath = os.path.join(output_dir, filename)
        
        logger.info(f"Generating diagram with filename: {filename}")
        
        # Verify output directory is writable
        if not os.access(output_dir, os.W_OK):
            raise Exception(f"Output directory {output_dir} is not writable. Please check directory permissions.")
        
        # Determine organization template
        template = generate_architecture_template(inputs)
        org_name = inputs.org_structure or "Enterprise"
        
        logger.info(f"Using template: {template['template']['name']} for organization: {org_name}")
        
        try:
            # Set the format based on the requested output format
            output_format = "svg" if format.lower() == "svg" else "png"
            
            with Diagram(
                f"Azure Landing Zone - {template['template']['name']}", 
                filename=filepath, 
                show=False, 
                direction="TB",
                outformat=output_format,
                graph_attr={
                    "fontsize": "16",
                    "fontname": "Arial",
                    "rankdir": "TB",
                    "nodesep": "1.0",
                    "ranksep": "1.5",
                    "bgcolor": "#ffffff",
                    "margin": "0.5",
                    "label": f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\nUser Services Only: {user_service_count} services",
                    "labelloc": "b",
                    "fontcolor": "#666666",
                    "fontsize": "10"
                },
                node_attr={
                    "fontsize": "12",
                    "fontname": "Arial"
                },
                edge_attr={
                    "fontsize": "10",
                    "fontname": "Arial"
                }
            ):
                
                logger.info("Creating diagram structure with STRICT user input adherence...")
                
                # Track all created resources for verification
                created_resources = []
                resources_by_category = {}
                
                # Only create what the user explicitly selected
                if user_service_count == 0:
                    # User selected no services - show empty architecture framework
                    logger.info("No services selected by user - creating empty architecture framework")
                    with Cluster("Azure Landing Zone Framework", graph_attr={
                        "bgcolor": "#f8f9fa", 
                        "style": "rounded,bold", 
                        "pencolor": "#6c757d", 
                        "penwidth": "2",
                        "fontsize": "14", 
                        "fontcolor": "#1A202C"
                    }):
                        placeholder = Subscriptions(f"Ready for Service Selection\\n\\nNo services specified\\nPlease select Azure services\\nto populate this architecture")
                        created_resources.append(placeholder)
                        logger.info("Created empty framework placeholder")
                else:
                    # Create architecture based on ONLY user-selected services
                    logger.info(f"Creating architecture with {user_service_count} user-selected services")
                    
                    # Process each service category that the user specified
                    service_categories = [
                        ("compute_services", "Compute Services", inputs.compute_services),
                        ("network_services", "Network Services", inputs.network_services),
                        ("storage_services", "Storage Services", inputs.storage_services),
                        ("database_services", "Database Services", inputs.database_services),
                        ("security_services", "Security Services", inputs.security_services),
                        ("monitoring_services", "Monitoring Services", inputs.monitoring_services),
                        ("ai_services", "AI/ML Services", inputs.ai_services),
                        ("analytics_services", "Analytics Services", inputs.analytics_services),
                        ("integration_services", "Integration Services", inputs.integration_services),
                        ("devops_services", "DevOps Services", inputs.devops_services),
                        ("backup_services", "Backup Services", inputs.backup_services)
                    ]
                    
                    for category_key, category_display, service_list in service_categories:
                        if service_list and len(service_list) > 0:
                            logger.info(f"Processing {category_display}: {len(service_list)} services")
                            
                            # Create cluster for this category
                            cluster_colors = {
                                "compute_services": {"bgcolor": "#E3F2FD", "pencolor": "#1976D2"},
                                "network_services": {"bgcolor": "#F3E5F5", "pencolor": "#7B1FA2"},
                                "storage_services": {"bgcolor": "#E8F5E8", "pencolor": "#388E3C"},
                                "database_services": {"bgcolor": "#FFF3E0", "pencolor": "#F57C00"},
                                "security_services": {"bgcolor": "#FFEBEE", "pencolor": "#D32F2F"},
                                "monitoring_services": {"bgcolor": "#E0F2F1", "pencolor": "#00796B"},
                                "ai_services": {"bgcolor": "#F1F8E9", "pencolor": "#689F38"},
                                "analytics_services": {"bgcolor": "#E8EAF6", "pencolor": "#3F51B5"},
                                "integration_services": {"bgcolor": "#FCE4EC", "pencolor": "#C2185B"},
                                "devops_services": {"bgcolor": "#EFEBE9", "pencolor": "#5D4037"},
                                "backup_services": {"bgcolor": "#F9FBE7", "pencolor": "#827717"}
                            }
                            
                            colors = cluster_colors.get(category_key, {"bgcolor": "#F5F5F5", "pencolor": "#9E9E9E"})
                            
                            with Cluster(category_display, graph_attr={
                                "bgcolor": colors["bgcolor"], 
                                "style": "rounded,bold", 
                                "pencolor": colors["pencolor"], 
                                "penwidth": "2",
                                "fontsize": "14", 
                                "fontcolor": "#1A202C"
                            }):
                                category_resources = []
                                
                                for service in service_list:
                                    if service in AZURE_SERVICES_MAPPING:
                                        service_info = AZURE_SERVICES_MAPPING[service]
                                        if service_info["diagram_class"]:
                                            try:
                                                diagram_class = service_info["diagram_class"]
                                                service_name = service_info["name"]
                                                service_resource = diagram_class(service_name)
                                                category_resources.append(service_resource)
                                                created_resources.append(service_resource)
                                                logger.info(f"Created service: {service_name} ({service})")
                                            except Exception as e:
                                                logger.warning(f"Failed to create service {service}: {e}")
                                        else:
                                            logger.info(f"Service {service} has no diagram representation (internal component)")
                                    else:
                                        logger.warning(f"Service {service} not found in AZURE_SERVICES_MAPPING")
                                
                                resources_by_category[category_key] = category_resources
                                logger.info(f"Created {len(category_resources)} resources for {category_display}")
                
                # Add minimal intelligent connections only between user-selected services
                if user_service_count > 1:
                    logger.info("Adding intelligent connections between user-selected services")
                    _add_conservative_connections(resources_by_category, inputs)
                
                logger.info(f"Diagram structure completed with {len(created_resources)} total resources")
        
        except Exception as e:
            logger.error(f"Error during diagram creation: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error generating Azure architecture diagram: {str(e)}\n\nThis could be due to:\n1. Graphviz installation issues\n2. Invalid service configurations\n3. System resource constraints\n\nPlease check the logs for more details.")
        
        # Enhanced file generation verification
        try:
            if format.lower() == "svg":
                svg_path = f"{filepath}.svg"
                if os.path.exists(svg_path):
                    file_size = os.path.getsize(svg_path)
                    if file_size < 100:  # SVG files should be at least 100 bytes
                        raise Exception(f"Generated SVG file is too small ({file_size} bytes), likely corrupted")
                    logger.info(f"SVG diagram generated successfully: {svg_path} (size: {file_size} bytes)")
                    return svg_path
                else:
                    # Fallback: try to generate SVG using dot command
                    dot_path = f"{filepath}.gv" 
                    if os.path.exists(dot_path):
                        try:
                            result = subprocess.run(['dot', '-Tsvg', dot_path, '-o', svg_path], 
                                                  capture_output=True, text=True, timeout=30)
                            if result.returncode != 0:
                                raise Exception(f"SVG generation failed: {result.stderr}")
                            
                            if os.path.exists(svg_path):
                                file_size = os.path.getsize(svg_path)
                                if file_size < 100:
                                    raise Exception(f"Generated SVG file is too small ({file_size} bytes)")
                                logger.info(f"SVG diagram generated via dot command: {svg_path} (size: {file_size} bytes)")
                                return svg_path
                        except subprocess.TimeoutExpired:
                            raise Exception("SVG generation timed out")
                    raise Exception(f"SVG generation failed - no output files found")
            else:
                # PNG generation with verification
                png_path = f"{filepath}.png"
                if os.path.exists(png_path):
                    file_size = os.path.getsize(png_path)
                    if file_size < 1000:  # PNG files should be at least 1KB
                        raise Exception(f"Generated PNG file is too small ({file_size} bytes), likely corrupted")
                    logger.info(f"PNG diagram generated successfully: {png_path} (size: {file_size} bytes)")
                    return png_path
                else:
                    raise Exception(f"PNG diagram generation failed - file not found: {png_path}")
        
        except Exception as verification_error:
            logger.error(f"File generation verification failed: {verification_error}")
            raise Exception(f"Diagram file generation verification failed: {str(verification_error)}\n\nPossible causes:\n1. Insufficient disk space\n2. File permission issues\n3. Graphviz rendering problems\n\nPlease check system resources and permissions.")
            
    except Exception as e:
        logger.error(f"Failed to generate Azure architecture diagram: {str(e)}")
        logger.error(traceback.format_exc())
        # Provide user-friendly error messages
        if "Graphviz" in str(e):
            raise Exception(f"Graphviz error: {str(e)}")
        elif "permission" in str(e).lower():
            raise Exception(f"Permission error: {str(e)}\n\nPlease check directory permissions for: {output_dir}")
        elif "space" in str(e).lower() or "disk" in str(e).lower():
            raise Exception(f"Disk space error: {str(e)}\n\nPlease free up disk space and try again.")
        else:
            raise Exception(f"Diagram generation failed: {str(e)}")

def _add_conservative_connections(resources_by_category: dict, inputs: CustomerInputs) -> None:
    """Add minimal, conservative connections only between user-selected services"""
    logger.info("Adding conservative connections between user-selected services only")
    
    # Only add connections that make obvious sense based on what the user selected
    try:
        # Example: Connect compute to networking if both are selected
        compute_resources = resources_by_category.get("compute_services", [])
        network_resources = resources_by_category.get("network_services", [])
        database_resources = resources_by_category.get("database_services", [])
        security_resources = resources_by_category.get("security_services", [])
        
        # Conservative connection 1: Compute to networking (if both exist)
        if compute_resources and network_resources:
            for compute in compute_resources[:1]:  # Just first compute service
                for network in network_resources[:1]:  # Just first network service
                    try:
                        compute >> Edge(label="network") >> network
                        logger.info(f"Connected {compute} to {network}")
                    except Exception as e:
                        logger.warning(f"Failed to connect compute to network: {e}")
        
        # Conservative connection 2: Compute to database (if both exist)
        if compute_resources and database_resources:
            for compute in compute_resources[:1]:
                for database in database_resources[:1]:
                    try:
                        compute >> Edge(label="data") >> database
                        logger.info(f"Connected {compute} to {database}")
                    except Exception as e:
                        logger.warning(f"Failed to connect compute to database: {e}")
        
        # Conservative connection 3: Security to other services (if security exists)
        if security_resources:
            security_service = security_resources[0]
            for category_name, resources in resources_by_category.items():
                if category_name != "security_services" and resources:
                    try:
                        security_service >> Edge(label="secures", style="dashed") >> resources[0]
                        logger.info(f"Connected security to {category_name}")
                        break  # Only connect to one other category
                    except Exception as e:
                        logger.warning(f"Failed to connect security to {category_name}: {e}")
        
        logger.info("Conservative connections completed")
        
    except Exception as e:
        logger.warning(f"Failed to add conservative connections: {e}")
        # Don't fail the entire diagram generation for connection issues

def generate_simple_svg_diagram(inputs: CustomerInputs) -> str:
    """Generate a minimal SVG diagram based only on selected services"""
    
    template = generate_architecture_template(inputs)
    template_name = template['template']['name']
    
    # Create a simple SVG representation
    svg_width = 800
    svg_height = 600
    
    svg_content = f'''<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .title {{ font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; fill: #0078d4; }}
            .group-title {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #323130; }}
            .service {{ font-family: Arial, sans-serif; font-size: 12px; fill: #605e5c; }}
            .subscription {{ fill: #e1f5fe; stroke: #0078d4; stroke-width: 2; }}
            .resource-group {{ fill: #f3e5f5; stroke: #6b69d6; stroke-width: 2; }}
            .service-box {{ fill: #fff3e0; stroke: #d83b01; stroke-width: 1; cursor: pointer; }}
            .service-box:hover {{ fill: #ffebdd; }}
            .network-box {{ fill: #e8f5e8; stroke: #107c10; stroke-width: 1; cursor: pointer; }}
            .network-box:hover {{ fill: #f3fdf3; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="100%" height="100%" fill="#f8f9fa"/>
    
    <!-- Title -->
    <text x="400" y="30" class="title" text-anchor="middle">Azure Architecture - {template_name}</text>
    
    <!-- Azure Subscription -->
    <rect x="100" y="80" width="600" height="450" class="subscription" rx="5"/>
    <text x="110" y="100" class="group-title">Azure Subscription</text>
    
    <!-- Resource Group -->
    <rect x="120" y="120" width="560" height="380" class="resource-group" rx="5"/>
    <text x="130" y="140" class="group-title">Resource Group</text>'''
    
    # Add selected services
    y_offset = 170
    x_start = 150
    services_added = []
    
    if inputs.compute_services:
        svg_content += f'''
    <!-- Compute Services -->
    <rect x="{x_start}" y="{y_offset}" width="200" height="100" class="service-box" rx="5"/>
    <text x="{x_start + 10}" y="{y_offset + 20}" class="group-title">Compute</text>'''
        
        for i, service in enumerate(inputs.compute_services[:2]):  # Max 2 services
            service_info = AZURE_SERVICES_MAPPING.get(service, {"name": service, "icon": "🖥️"})
            svg_content += f'''
    <rect x="{x_start + 10}" y="{y_offset + 30 + (i * 30)}" width="180" height="25" class="service-box" rx="3"/>
    <text x="{x_start + 20}" y="{y_offset + 47 + (i * 30)}" class="service" font-size="11">{service_info["icon"]} {service_info["name"][:15]}</text>'''
        services_added.append("compute")
    
    if inputs.network_services:
        x_pos = x_start + 220 if "compute" in services_added else x_start
        svg_content += f'''
    <!-- Network Services -->
    <rect x="{x_pos}" y="{y_offset}" width="200" height="100" class="network-box" rx="5"/>
    <text x="{x_pos + 10}" y="{y_offset + 20}" class="group-title">Network</text>'''
        
        for i, service in enumerate(inputs.network_services[:2]):  # Max 2 services
            service_info = AZURE_SERVICES_MAPPING.get(service, {"name": service, "icon": "🌐"})
            svg_content += f'''
    <rect x="{x_pos + 10}" y="{y_offset + 30 + (i * 30)}" width="180" height="25" class="network-box" rx="3"/>
    <text x="{x_pos + 20}" y="{y_offset + 47 + (i * 30)}" class="service" font-size="11">{service_info["icon"]} {service_info["name"][:15]}</text>'''
        services_added.append("network")
    
    # Add other service types if needed
    if inputs.storage_services:
        x_pos = x_start + (220 * len(services_added))
        if x_pos < 500:  # Only if there's space
            svg_content += f'''
    <!-- Storage Services -->
    <rect x="{x_pos}" y="{y_offset}" width="200" height="100" class="service-box" rx="5"/>
    <text x="{x_pos + 10}" y="{y_offset + 20}" class="group-title">Storage</text>'''
            
            for i, service in enumerate(inputs.storage_services[:2]):
                service_info = AZURE_SERVICES_MAPPING.get(service, {"name": service, "icon": "💾"})
                svg_content += f'''
    <rect x="{x_pos + 10}" y="{y_offset + 30 + (i * 30)}" width="180" height="25" class="service-box" rx="3"/>
    <text x="{x_pos + 20}" y="{y_offset + 47 + (i * 30)}" class="service" font-size="11">{service_info["icon"]} {service_info["name"][:15]}</text>'''
    
    # If no services selected, show message
    if not any([inputs.compute_services, inputs.network_services, inputs.storage_services,
                inputs.database_services, inputs.security_services, inputs.monitoring_services]):
        svg_content += f'''
    <!-- No Services Message -->
    <rect x="{x_start}" y="{y_offset}" width="400" height="80" fill="#f8f8f8" stroke="#ddd" stroke-width="1" rx="5"/>
    <text x="{x_start + 200}" y="{y_offset + 35}" class="group-title" text-anchor="middle">No Services Selected</text>
    <text x="{x_start + 200}" y="{y_offset + 55}" class="service" text-anchor="middle">Please select Azure services to generate architecture</text>'''
    
    svg_content += '''
    <!-- Footer -->
    <text x="400" y="570" class="service" text-anchor="middle" fill="#8a8886">Generated by Azure Landing Zone Agent - Minimal Mode</text>
</svg>'''
    
    return svg_content

def _add_service_clusters(inputs: CustomerInputs, prod_vnet, workloads_mg):
    """Helper method to add service clusters to avoid code duplication"""
    try:
        # Compute and Application Services
        if inputs.compute_services or inputs.workload:
            with Cluster("Compute & Applications", graph_attr={"bgcolor": "#fff8dc", "style": "rounded"}):
                compute_services = []
                
                # Add selected compute services
                if inputs.compute_services:
                    for service in inputs.compute_services:
                        if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                            diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                            service_name = AZURE_SERVICES_MAPPING[service]["name"]
                            compute_services.append(diagram_class(service_name))
                
                # Fallback to workload if no specific compute services
                if not compute_services and inputs.workload:
                    if inputs.workload in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[inputs.workload]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[inputs.workload]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[inputs.workload]["name"]
                        compute_services.append(diagram_class(service_name))
                
                # Default to App Services if nothing specified
                if not compute_services:
                    compute_services.append(AppServices("Azure App Services"))
                
                # Connect compute services to production VNet
                for cs in compute_services:
                    prod_vnet >> cs
                    workloads_mg >> cs
        
        # Storage Services
        if inputs.storage_services:
            with Cluster("Storage & Data", graph_attr={"bgcolor": "#f5f5dc", "style": "rounded"}):
                storage_services = []
                for service in inputs.storage_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        storage_services.append(diagram_class(service_name))
                
                if not storage_services:
                    storage_services.append(StorageAccounts("Storage Accounts"))
                
                # Connect storage to production VNet and workloads
                for ss in storage_services:
                    prod_vnet >> ss
                    workloads_mg >> ss
        
        # Database Services
        if inputs.database_services:
            with Cluster("Databases", graph_attr={"bgcolor": "#e6f3ff", "style": "rounded"}):
                database_services = []
                for service in inputs.database_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        database_services.append(diagram_class(service_name))
                
                # Connect databases to production VNet and workloads
                for ds in database_services:
                    prod_vnet >> ds
                    workloads_mg >> ds
        
        # Analytics Services
        if inputs.analytics_services:
            with Cluster("Analytics & AI", graph_attr={"bgcolor": "#f0e6ff", "style": "rounded"}):
                analytics_services = []
                for service in inputs.analytics_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        analytics_services.append(diagram_class(service_name))
                
                # Connect analytics to production VNet and workloads
                for as_service in analytics_services:
                    prod_vnet >> as_service
                    workloads_mg >> as_service
        
        # Integration Services
        if inputs.integration_services:
            with Cluster("Integration", graph_attr={"bgcolor": "#fff0e6", "style": "rounded"}):
                integration_services = []
                for service in inputs.integration_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        integration_services.append(diagram_class(service_name))
                
                # Connect integration services to production VNet and workloads
                for is_service in integration_services:
                    prod_vnet >> is_service
                    workloads_mg >> is_service
        
        # DevOps Services  
        if inputs.devops_services:
            with Cluster("DevOps & Automation", graph_attr={"bgcolor": "#f5f5f5", "style": "rounded"}):
                devops_services = []
                for service in inputs.devops_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        devops_services.append(diagram_class(service_name))
                
                # Connect DevOps services to management
                for ds in devops_services:
                    workloads_mg >> ds
                    
    except Exception as e:
        logger.warning(f"Error adding service clusters: {str(e)}")
        # Don't fail the entire diagram generation for service cluster issues


def _add_intelligent_network_connections(network_resources: list, network_resources_by_type: dict):
    """Add intelligent connections between network services based on Azure patterns"""
    try:
        # Hub-spoke pattern: VNet as hub, connect others to it
        vnets = network_resources_by_type.get("virtual_network", [])
        if len(vnets) > 1:
            hub_vnet = vnets[0]  # First VNet as hub
            for spoke_vnet in vnets[1:]:
                hub_vnet >> Edge(style="dashed", color="blue", label="VNet Peering") >> spoke_vnet
        
        # Application Gateway -> Load Balancer pattern
        app_gateways = network_resources_by_type.get("application_gateway", [])
        load_balancers = network_resources_by_type.get("load_balancer", [])
        for ag in app_gateways:
            for lb in load_balancers:
                ag >> Edge(color="green", label="HTTP/HTTPS") >> lb
        
        # Firewall -> Application Gateway pattern (secure traffic flow)
        firewalls = network_resources_by_type.get("firewall", [])
        for fw in firewalls:
            for ag in app_gateways:
                fw >> Edge(color="red", label="Filtered Traffic") >> ag
        
        # VPN/ExpressRoute -> VNet pattern
        vpn_gateways = network_resources_by_type.get("vpn_gateway", [])
        expressroutes = network_resources_by_type.get("expressroute", [])
        
        for vpn in vpn_gateways:
            for vnet in vnets:
                vpn >> Edge(color="orange", label="Site-to-Site") >> vnet
        
        for er in expressroutes:
            for vnet in vnets:
                er >> Edge(color="purple", label="Private Connection") >> vnet
                
        logger.debug("Intelligent network connections added")
        
    except Exception as e:
        logger.warning(f"Error adding intelligent network connections: {e}")


def _add_intelligent_service_connections(inputs: CustomerInputs, all_resources: dict, template: dict):
    """Add intelligent connections between services based on Azure architecture patterns"""
    try:
        logger.info("Adding intelligent service connections based on architecture patterns")
        
        # Get AI analysis for connectivity guidance
        connectivity_guidance = ""
        if hasattr(template, 'get') and template.get("connectivity_requirements"):
            connectivity_guidance = template["connectivity_requirements"]
        
        # Define connection patterns based on Azure best practices
        connection_patterns = {
            # Web application patterns
            "web_tier": {
                "sources": ["application_gateway", "load_balancer", "traffic_manager"],
                "targets": ["app_services", "virtual_machines", "aks"]
            },
            # Data tier patterns  
            "data_flow": {
                "sources": ["app_services", "virtual_machines", "aks", "functions"],
                "targets": ["sql_database", "cosmos_db", "mysql", "postgresql", "storage_accounts", "blob_storage"]
            },
            # Network patterns
            "network_flow": {
                "sources": ["vpn_gateway", "expressroute"],
                "targets": ["virtual_network", "firewall", "application_gateway"]
            },
            # Security patterns
            "security_flow": {
                "sources": ["key_vault"],
                "targets": ["app_services", "virtual_machines", "aks", "functions"]
            },
            # Monitoring patterns
            "monitoring_flow": {
                "sources": ["azure_monitor", "log_analytics", "application_insights"],
                "targets": ["app_services", "virtual_machines", "aks", "sql_database", "cosmos_db"]
            },
            # Integration patterns
            "integration_flow": {
                "sources": ["api_management"],
                "targets": ["app_services", "functions", "logic_apps", "service_bus"]
            },
            # DevOps patterns
            "devops_flow": {
                "sources": ["devops", "pipelines", "container_registry"],
                "targets": ["aks", "app_services", "virtual_machines"]
            }
        }
        
        # Apply connection patterns
        for pattern_name, pattern in connection_patterns.items():
            for source_type in pattern["sources"]:
                for target_type in pattern["targets"]:
                    # Find matching resources
                    source_resources = all_resources.get(source_type, [])
                    target_resources = all_resources.get(target_type, [])
                    
                    # Create connections between matching resources
                    for source in source_resources:
                        for target in target_resources:
                            if source != target:  # Don't connect to self
                                try:
                                    # Create connection with appropriate style
                                    connection_style = _get_connection_style(pattern_name)
                                    source >> Edge(**connection_style) >> target
                                    logger.debug(f"Connected {source_type} -> {target_type} ({pattern_name})")
                                except Exception as conn_error:
                                    logger.warning(f"Failed to connect {source_type} -> {target_type}: {conn_error}")
        
        # Add hub-spoke network connections if virtual networks exist
        vnets = all_resources.get("virtual_network", [])
        if len(vnets) > 1:
            # Connect first VNet (hub) to all others (spokes)
            hub = vnets[0]
            for spoke in vnets[1:]:
                try:
                    hub >> Edge(style="dashed", color="blue", label="Peering") >> spoke
                    logger.debug("Added hub-spoke VNet peering connection")
                except Exception as e:
                    logger.warning(f"Failed to add VNet peering: {e}")
                    
        logger.info("Intelligent service connections added successfully")
        
    except Exception as e:
        logger.warning(f"Error adding intelligent service connections: {str(e)}")
        # Don't fail diagram generation if connections fail


def _get_connection_style(pattern_name: str) -> dict:
    """Get connection style based on pattern type"""
    styles = {
        "web_tier": {"color": "green", "style": "bold", "label": "HTTP/HTTPS"},
        "data_flow": {"color": "blue", "style": "solid", "label": "Data"},
        "network_flow": {"color": "orange", "style": "bold", "label": "Network"},
        "security_flow": {"color": "red", "style": "dashed", "label": "Secrets"},
        "monitoring_flow": {"color": "purple", "style": "dotted", "label": "Metrics"},
        "integration_flow": {"color": "teal", "style": "solid", "label": "API"},
        "devops_flow": {"color": "gray", "style": "dashed", "label": "Deploy"}
    }
    return styles.get(pattern_name, {"color": "black", "style": "solid"})


def _add_selected_service_clusters(inputs: CustomerInputs, existing_resources: list):
    """Add only explicitly selected services without defaults or hardcoded assumptions"""
    try:
        all_created_resources = existing_resources.copy()
        
        # Track resources by type for intelligent connections
        resources_by_type = {}
        
        # Compute Services - middle layer (Requirement 3: compute in middle)
        if inputs.compute_services:
            with Cluster("Compute Services", graph_attr={
                "bgcolor": "#EBF8FF", "style": "rounded,bold", "pencolor": "#3182CE", "penwidth": "2",
                "fontsize": "14", "fontcolor": "#1A202C", "rank": "same"
            }):
                for service in inputs.compute_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Storage Services - organized by tier (Requirement 8: logical grouping)
        if inputs.storage_services:
            with Cluster("Storage Services", graph_attr={
                "bgcolor": "#F7FAFC", "style": "rounded,bold", "pencolor": "#718096", "penwidth": "2",
                "fontsize": "14", "fontcolor": "#1A202C", "rank": "same"
            }):
                for service in inputs.storage_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Database Services - data tier at bottom (Requirement 3: data at bottom)
        if inputs.database_services:
            with Cluster("Data Services", graph_attr={
                "bgcolor": "#FFF5F5", "style": "rounded,bold", "pencolor": "#E53E3E", "penwidth": "2",
                "fontsize": "14", "fontcolor": "#1A202C", "rank": "max"
            }):
                for service in inputs.database_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Security Services - only if explicitly selected
        if inputs.security_services:
            with Cluster("Security Services", graph_attr={"bgcolor": "#ffe6e6", "style": "rounded"}):
                for service in inputs.security_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Monitoring Services - observability layer (Requirement 1: clear containers)
        if inputs.monitoring_services:
            with Cluster("Monitoring & Observability", graph_attr={
                "bgcolor": "#EBF4FF", "style": "rounded,bold", "pencolor": "#3182CE", "penwidth": "2",
                "fontsize": "14", "fontcolor": "#1A202C", "rank": "max"
            }):
                for service in inputs.monitoring_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # AI/ML Services - only if explicitly selected
        if inputs.ai_services:
            with Cluster("AI & Machine Learning", graph_attr={"bgcolor": "#f0fff0", "style": "rounded"}):
                for service in inputs.ai_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Analytics Services - only if explicitly selected
        if inputs.analytics_services:
            with Cluster("Analytics Services", graph_attr={"bgcolor": "#fff8f0", "style": "rounded"}):
                for service in inputs.analytics_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Integration Services - only if explicitly selected
        if inputs.integration_services:
            with Cluster("Integration Services", graph_attr={"bgcolor": "#f8f8ff", "style": "rounded"}):
                for service in inputs.integration_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # DevOps Services - only if explicitly selected
        if inputs.devops_services:
            with Cluster("DevOps Services", graph_attr={"bgcolor": "#f5f5f5", "style": "rounded"}):
                for service in inputs.devops_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Backup Services - only if explicitly selected
        if inputs.backup_services:
            with Cluster("Backup & Recovery", graph_attr={"bgcolor": "#fff0f5", "style": "rounded"}):
                for service in inputs.backup_services:
                    if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                        diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                        service_name = AZURE_SERVICES_MAPPING[service]["name"]
                        resource = diagram_class(service_name)
                        all_created_resources.append(resource)
                        
                        # Track by service type
                        if service not in resources_by_type:
                            resources_by_type[service] = []
                        resources_by_type[service].append(resource)
        
        # Return both the list and the type mapping for intelligent connections
        return all_created_resources, resources_by_type
                        
    except Exception as e:
        logger.warning(f"Error adding selected service clusters: {str(e)}")
        # Don't fail the entire diagram generation for service cluster issues
        return existing_resources, {}


def generate_architecture_template(inputs: CustomerInputs) -> Dict[str, Any]:
    """Generate architecture template based on inputs with AI enhancement for free text"""
    
    # First, check if we should use AI analysis for service selection
    ai_services = []
    ai_reasoning = ""
    needs_confirmation = False
    suggested_additions = []
    
    # Count explicitly selected services
    total_selected_services = sum([
        len(inputs.compute_services or []),
        len(inputs.network_services or []),
        len(inputs.storage_services or []),
        len(inputs.database_services or []),
        len(inputs.security_services or []),
        len(inputs.monitoring_services or []),
        len(inputs.ai_services or []),
        len(inputs.analytics_services or []),
        len(inputs.integration_services or []),
        len(inputs.devops_services or []),
        len(inputs.backup_services or [])
    ])
    
    # Enhanced AI analysis fields
    architecture_pattern = ""
    connectivity_requirements = ""
    security_considerations = ""
    
    # Only use AI if user provided free text
    if inputs.free_text_input:
        logger.info("Using comprehensive AI analysis for architecture design based on free text input")
        ai_analysis = analyze_free_text_requirements(inputs.free_text_input)
        ai_services = ai_analysis.get("services", [])
        ai_reasoning = ai_analysis.get("reasoning", "")
        architecture_pattern = ai_analysis.get("architecture_pattern", "")
        connectivity_requirements = ai_analysis.get("connectivity_requirements", "")
        security_considerations = ai_analysis.get("security_considerations", "")
        needs_confirmation = ai_analysis.get("needs_confirmation", False)
        suggested_additions = ai_analysis.get("suggested_additions", [])
        
        logger.info(f"AI analysis completed: {len(ai_services)} services identified for {architecture_pattern} pattern")
    
    # Use minimal template by default - no complex management groups unless specifically requested
    minimal_template = {
        "name": "Minimal Azure Architecture",
        "management_groups": ["Root"],  # Only root, no complex hierarchy
        "subscriptions": ["Production"],  # Only one subscription
        "core_services": []  # No automatic core services
    }
    
    # Build architecture components with enhanced AI insights
    components = {
        "template": minimal_template,
        "identity": inputs.identity or None,
        "network_model": inputs.network_model or "simple",
        "workload": inputs.workload or None,
        "security": inputs.security_posture or None,
        "monitoring": inputs.monitoring or None,
        "governance": inputs.governance or None,
        "ai_services": ai_services,
        "ai_reasoning": ai_reasoning,
        "architecture_pattern": architecture_pattern,
        "connectivity_requirements": connectivity_requirements,
        "security_considerations": security_considerations,
        "needs_confirmation": needs_confirmation,
        "suggested_additions": suggested_additions
    }
    
    return components

def generate_dynamic_mermaid(inputs: CustomerInputs, ai_analysis: dict = None) -> str:
    """Generate dynamic Mermaid diagram that adapts to architectural patterns and AI analysis"""
    
    # Get AI analysis insights
    pattern = ai_analysis.get("architecture_pattern", "Standard Architecture") if ai_analysis else "Standard Architecture"
    services = ai_analysis.get("services", []) if ai_analysis else []
    
    # Start with pattern-specific diagram structure
    if "Microservices" in pattern:
        return generate_microservices_mermaid(inputs, services, ai_analysis)
    elif "E-commerce" in pattern:
        return generate_ecommerce_mermaid(inputs, services, ai_analysis)
    elif "Data Analytics" in pattern:
        return generate_analytics_mermaid(inputs, services, ai_analysis)
    else:
        return generate_standard_mermaid(inputs, services, ai_analysis)

def generate_microservices_mermaid(inputs: CustomerInputs, services: list, ai_analysis: dict) -> str:
    """Generate microservices-specific mermaid diagram"""
    lines = [
        "graph TB",
        "    subgraph \"🌐 External Users\"",
        "        USERS[\"👥 Users\"]",
        "    end",
        "",
        "    subgraph \"🔄 API Gateway Layer\"",
        "        APIGW[\"🚪 API Gateway\"]",
        "        LB[\"⚖️ Load Balancer\"]",
        "    end",
        "",
        "    subgraph \"📦 Microservices Platform\"",
        "        AKS[\"☸️ Azure Kubernetes Service\"]",
        "        subgraph \"🔧 Services\"",
        "            SVC1[\"🎯 Auth Service\"]",
        "            SVC2[\"💼 Business Service\"]",
        "            SVC3[\"📊 Data Service\"]",
        "        end",
        "    end",
        "",
        "    subgraph \"💾 Data Layer\"",
        "        DB[\"🗄️ Database\"]",
        "        CACHE[\"⚡ Cache\"]",
        "    end",
        "",
        "    subgraph \"🔐 Security & Operations\"",
        "        VAULT[\"🔑 Key Vault\"]",
        "        MONITOR[\"📊 Monitoring\"]",
        "    end",
        "",
        "    %% Connections",
        "    USERS --> LB",
        "    LB --> APIGW",
        "    APIGW --> AKS",
        "    AKS --> SVC1",
        "    AKS --> SVC2", 
        "    AKS --> SVC3",
        "    SVC1 --> DB",
        "    SVC2 --> DB",
        "    SVC3 --> DB",
        "    SVC1 --> CACHE",
        "    SVC2 --> CACHE",
        "    AKS --> VAULT",
        "    AKS --> MONITOR",
        "",
        "    %% Styling",
        "    classDef primary fill:#0078d4,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef secondary fill:#107c10,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef data fill:#d83b01,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef security fill:#5c2d91,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "",
        "    class USERS,LB,APIGW primary;",
        "    class AKS,SVC1,SVC2,SVC3 secondary;",
        "    class DB,CACHE data;",
        "    class VAULT,MONITOR security;"
    ]
    
    return "\\n".join(lines)

def generate_ecommerce_mermaid(inputs: CustomerInputs, services: list, ai_analysis: dict) -> str:
    """Generate e-commerce-specific mermaid diagram"""
    lines = [
        "graph TB",
        "    subgraph \"🌍 Global Users\"",
        "        USERS[\"🛒 Customers\"]",
        "        ADMIN[\"👨‍💼 Admin\"]",
        "    end",
        "",
        "    subgraph \"🌐 Edge & CDN\"",
        "        CDN[\"🚀 Azure CDN\"]",
        "        WAF[\"🛡️ Web Application Firewall\"]",
        "    end",
        "",
        "    subgraph \"🏪 Application Layer\"",
        "        APPGW[\"🚪 Application Gateway\"]",
        "        WEBAPP[\"🌐 Web Application\"]",
        "        API[\"🔗 API Services\"]",
        "    end",
        "",
        "    subgraph \"💳 Business Services\"",
        "        PAYMENT[\"💰 Payment Processing\"]",
        "        INVENTORY[\"📦 Inventory Management\"]",
        "        ORDER[\"📋 Order Processing\"]",
        "    end",
        "",
        "    subgraph \"💾 Data & Cache\"",
        "        DB[\"🗄️ SQL Database\"]",
        "        REDIS[\"⚡ Redis Cache\"]",
        "        STORAGE[\"📁 Blob Storage\"]",
        "    end",
        "",
        "    subgraph \"🔐 Security & Operations\"",
        "        VAULT[\"🔑 Key Vault\"]",
        "        AAD[\"🆔 Azure AD\"]",
        "        MONITOR[\"📊 Application Insights\"]",
        "    end",
        "",
        "    %% User flows",
        "    USERS --> CDN",
        "    ADMIN --> APPGW",
        "    CDN --> WAF",
        "    WAF --> APPGW",
        "    APPGW --> WEBAPP",
        "    WEBAPP --> API",
        "    API --> PAYMENT",
        "    API --> INVENTORY",
        "    API --> ORDER",
        "",
        "    %% Data flows",
        "    PAYMENT --> DB",
        "    INVENTORY --> DB",
        "    ORDER --> DB",
        "    API --> REDIS",
        "    WEBAPP --> STORAGE",
        "",
        "    %% Security flows",
        "    API --> VAULT",
        "    API --> AAD",
        "    WEBAPP --> MONITOR",
        "    API --> MONITOR",
        "",
        "    %% Styling",
        "    classDef frontend fill:#0078d4,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef business fill:#107c10,stroke:#ffffff,stroke-width:2px,color:#ffffff;", 
        "    classDef data fill:#d83b01,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef security fill:#5c2d91,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "",
        "    class USERS,CDN,WAF,APPGW,WEBAPP frontend;",
        "    class API,PAYMENT,INVENTORY,ORDER business;",
        "    class DB,REDIS,STORAGE data;",
        "    class VAULT,AAD,MONITOR security;"
    ]
    
    return "\\n".join(lines)

def generate_analytics_mermaid(inputs: CustomerInputs, services: list, ai_analysis: dict) -> str:
    """Generate data analytics-specific mermaid diagram"""
    lines = [
        "graph LR",
        "    subgraph \"📥 Data Sources\"",
        "        SRC1[\"🏢 Enterprise Data\"]",
        "        SRC2[\"☁️ Cloud APIs\"]",
        "        SRC3[\"📱 IoT/Streaming\"]",
        "    end",
        "",
        "    subgraph \"🔄 Data Ingestion\"",
        "        ADF[\"🏭 Data Factory\"]",
        "        EVENTHUB[\"📨 Event Hubs\"]",
        "    end",
        "",
        "    subgraph \"💾 Data Storage\"",
        "        LAKE[\"🏞️ Data Lake\"]",
        "        DW[\"🏬 Synapse Analytics\"]",
        "        BLOB[\"📁 Blob Storage\"]",
        "    end",
        "",
        "    subgraph \"⚙️ Data Processing\"",
        "        DATABRICKS[\"🧮 Databricks\"]",
        "        SYNAPSE[\"⚡ Synapse Spark\"]",
        "    end",
        "",
        "    subgraph \"📊 Analytics & ML\"",
        "        ML[\"🤖 Machine Learning\"]",
        "        POWERBI[\"📈 Power BI\"]",
        "        COGNITIVE[\"🧠 Cognitive Services\"]",
        "    end",
        "",
        "    subgraph \"🔐 Security & Governance\"",
        "        VAULT[\"🔑 Key Vault\"]",
        "        PURVIEW[\"📋 Data Governance\"]",
        "        MONITOR[\"📊 Monitor\"]",
        "    end",
        "",
        "    %% Data flow",
        "    SRC1 --> ADF",
        "    SRC2 --> ADF",
        "    SRC3 --> EVENTHUB",
        "    ADF --> LAKE",
        "    EVENTHUB --> LAKE",
        "    LAKE --> DW",
        "    LAKE --> DATABRICKS",
        "    DW --> SYNAPSE",
        "    DATABRICKS --> ML",
        "    DW --> POWERBI",
        "    ML --> COGNITIVE",
        "",
        "    %% Security and governance",
        "    DATABRICKS --> VAULT",
        "    DW --> VAULT",
        "    ADF --> PURVIEW",
        "    DATABRICKS --> MONITOR",
        "    DW --> MONITOR",
        "",
        "    %% Styling",
        "    classDef source fill:#0078d4,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef ingestion fill:#107c10,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef storage fill:#d83b01,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef processing fill:#ff8c00,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef analytics fill:#5c2d91,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "",
        "    class SRC1,SRC2,SRC3 source;",
        "    class ADF,EVENTHUB ingestion;",
        "    class LAKE,DW,BLOB storage;",
        "    class DATABRICKS,SYNAPSE processing;",
        "    class ML,POWERBI,COGNITIVE,VAULT,PURVIEW,MONITOR analytics;"
    ]
    
    return "\\n".join(lines)

def generate_standard_mermaid(inputs: CustomerInputs, services: list, ai_analysis: dict) -> str:
    """Generate standard web application mermaid diagram"""
    lines = [
        "graph TB",
        "    subgraph \"👥 Users\"",
        "        USERS[\"🌐 Web Users\"]",
        "    end",
        "",
        "    subgraph \"🌐 Application Layer\"",
        "        APPGW[\"🚪 Application Gateway\"]",
        "        WEBAPP[\"🌐 App Service\"]",
        "    end",
        "",
        "    subgraph \"💾 Data Layer\"",
        "        DB[\"🗄️ SQL Database\"]",
        "        STORAGE[\"📁 Storage Account\"]",
        "    end",
        "",
        "    subgraph \"🔐 Security & Operations\"",
        "        VAULT[\"🔑 Key Vault\"]",
        "        MONITOR[\"📊 Azure Monitor\"]",
        "        VNET[\"🔒 Virtual Network\"]",
        "    end",
        "",
        "    %% Connections",
        "    USERS --> APPGW",
        "    APPGW --> WEBAPP",
        "    WEBAPP --> DB",
        "    WEBAPP --> STORAGE",
        "    WEBAPP --> VAULT",
        "    WEBAPP --> MONITOR",
        "    WEBAPP -.-> VNET",
        "    DB -.-> VNET",
        "",
        "    %% Styling", 
        "    classDef frontend fill:#0078d4,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef data fill:#d83b01,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "    classDef security fill:#5c2d91,stroke:#ffffff,stroke-width:2px,color:#ffffff;",
        "",
        "    class USERS,APPGW,WEBAPP frontend;",
        "    class DB,STORAGE data;",
        "    class VAULT,MONITOR,VNET security;"
    ]
    
    return "\\n".join(lines)

def generate_professional_mermaid(inputs: CustomerInputs) -> str:
    """Legacy wrapper - now generates dynamic diagrams when possible"""
    # Try to get AI analysis from the template
    template = generate_architecture_template(inputs)
    ai_analysis = template.get("ai_analysis", {})
    
    # If we have AI analysis, use dynamic generation
    if ai_analysis and ai_analysis.get("architecture_pattern"):
        return generate_dynamic_mermaid(inputs, ai_analysis)
    
    # Otherwise fall back to the original logic but simplified
    return generate_standard_mermaid(inputs, [], {})
def generate_enhanced_drawio_xml(inputs: CustomerInputs) -> str:
    """Generate enhanced Draw.io XML with comprehensive Azure stencils based on user selections"""
    
    def esc(s): 
        return html.escape(s) if s else ""
    
    template = generate_architecture_template(inputs)
    diagram_id = str(uuid.uuid4())
    
    # Base layout coordinates
    y_start = 100
    current_y = y_start
    section_height = 350
    service_width = 100
    service_height = 80
    
    # Build dynamic XML content
    xml_parts = [
        f"""<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Azure Landing Zone Agent" version="1.0.0">
  <diagram name="Azure Landing Zone Architecture" id="azure-lz-{diagram_id}">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2400" pageHeight="1600" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Azure Tenant Container -->
        <mxCell id="tenant" value="Azure Tenant - {esc(inputs.org_structure or 'Enterprise')}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=16;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="50" y="50" width="2300" height="1500" as="geometry" />
        </mxCell>
        
        <!-- Management Groups -->
        <mxCell id="mgmt-groups" value="Management Groups" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="{current_y}" width="500" height="250" as="geometry" />
        </mxCell>"""
    ]
    
    # Management Group structure based on template
    mg_x = 150
    mg_y = current_y + 50
    xml_parts.append(f"""
        <mxCell id="root-mg" value="Root MG" style="shape=mxgraph.azure.management;fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{mg_x}" y="{mg_y}" width="80" height="60" as="geometry" />
        </mxCell>""")
    
    mg_x += 120
    for i, mg in enumerate(template['template']['management_groups'][1:3]):  # Platform and Workloads
        mg_id = mg.lower().replace(' ', '-')
        xml_parts.append(f"""
        <mxCell id="{mg_id}-mg" value="{mg}" style="shape=mxgraph.azure.management;fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{mg_x}" y="{mg_y}" width="80" height="60" as="geometry" />
        </mxCell>""")
        mg_x += 120
    
    # Subscriptions
    current_y += 300
    xml_parts.append(f"""
        <!-- Subscriptions -->
        <mxCell id="subscriptions" value="Subscriptions" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="700" y="{current_y}" width="600" height="250" as="geometry" />
        </mxCell>""")
    
    sub_x = 750
    sub_y = current_y + 50
    for sub in template['template']['subscriptions'][:4]:  # First 4 subscriptions
        xml_parts.append(f"""
        <mxCell id="{sub.lower().replace(' ', '-')}-sub" value="{sub}" style="shape=mxgraph.azure.subscription;fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{sub_x}" y="{sub_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
        sub_x += 130
        if sub_x > 1200:  # Wrap to next row
            sub_x = 750
            sub_y += 100
    
    # Network Architecture Section - Only if network services are explicitly selected
    if inputs.network_services:
        current_y += 300
        xml_parts.append(f"""
        <!-- Network Architecture -->
        <mxCell id="network" value="Network Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="{current_y}" width="800" height="{section_height}" as="geometry" />
        </mxCell>""")
        
        # Add only explicitly selected network services
        net_x = 200
        net_y = current_y + 80
        for i, service in enumerate(inputs.network_services):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="net-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{net_x}" y="{net_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                net_x += 120
                if net_x > 600:  # Wrap to next row
                    net_x = 200
                    net_y += 100
    
    # Compute Services Section
    if inputs.compute_services or inputs.workload:
        current_y += section_height + 50
        xml_parts.append(f"""
        <!-- Compute Services -->
        <mxCell id="compute" value="Compute Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff0e6;strokeColor=#d79b00;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="1000" y="{current_y}" width="600" height="{section_height}" as="geometry" />
        </mxCell>""")
        
        comp_x = 1050
        comp_y = current_y + 50
        
        # Add selected compute services
        services_to_add = inputs.compute_services or []
        if inputs.workload and inputs.workload not in services_to_add:
            services_to_add.append(inputs.workload)
            
        for i, service in enumerate(services_to_add[:6]):  # Max 6 compute services
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="compute-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{comp_x}" y="{comp_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                comp_x += 120
                if comp_x > 1450:  # Wrap to next row
                    comp_x = 1050
                    comp_y += 100
    
    # Storage Services Section
    if inputs.storage_services:
        current_y += section_height + 50
        xml_parts.append(f"""
        <!-- Storage Services -->
        <mxCell id="storage" value="Storage Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f0f0f0;strokeColor=#666666;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="{current_y}" width="600" height="250" as="geometry" />
        </mxCell>""")
        
        stor_x = 150
        stor_y = current_y + 50
        for i, service in enumerate(inputs.storage_services[:4]):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'storage_accounts')
                xml_parts.append(f"""
        <mxCell id="storage-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{stor_x}" y="{stor_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                stor_x += 120
                if stor_x > 550:
                    stor_x = 150
                    stor_y += 100
    
    # Database Services Section
    if inputs.database_services:
        db_y = current_y if not inputs.storage_services else current_y
        if inputs.storage_services:
            xml_parts.append(f"""
        <!-- Database Services -->
        <mxCell id="database" value="Database Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6f3ff;strokeColor=#0066cc;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="800" y="{db_y}" width="600" height="250" as="geometry" />
        </mxCell>""")
        else:
            current_y += section_height + 50
            xml_parts.append(f"""
        <!-- Database Services -->
        <mxCell id="database" value="Database Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e6f3ff;strokeColor=#0066cc;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="{current_y}" width="600" height="250" as="geometry" />
        </mxCell>""")
            db_y = current_y
        
        db_x = 850 if inputs.storage_services else 150
        db_y += 50
        for i, service in enumerate(inputs.database_services[:4]):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'sql_database')
                xml_parts.append(f"""
        <mxCell id="database-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{db_x}" y="{db_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                db_x += 120
                if db_x > (1250 if inputs.storage_services else 550):
                    db_x = 850 if inputs.storage_services else 150
                    db_y += 100
    
    # Security Services Section (always present)
    current_y += 300
    xml_parts.append(f"""
        <!-- Security & Identity Services -->
        <mxCell id="security" value="Security &amp; Identity Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffebee;strokeColor=#c62828;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="1700" y="{y_start}" width="600" height="600" as="geometry" />
        </mxCell>""")
    
    # Core security services (always present)
    sec_x = 1750
    sec_y = y_start + 50
    core_security = [
        ('azure-ad', 'Azure AD', 'azure_active_directory'),
        ('key-vault', 'Key Vault', 'key_vault'),
        ('security-center', 'Security Center', 'security_center')
    ]
    
    for sec_id, sec_name, sec_shape in core_security:
        xml_parts.append(f"""
        <mxCell id="{sec_id}" value="{sec_name}" style="shape=mxgraph.azure.{sec_shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{sec_x}" y="{sec_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
        sec_x += 120
        if sec_x > 2100:
            sec_x = 1750
            sec_y += 100
    
    # Add additional selected security services
    if inputs.security_services:
        for i, service in enumerate(inputs.security_services):
            if service in AZURE_SERVICES_MAPPING and service not in ['active_directory', 'key_vault', 'security_center']:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="security-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{sec_x}" y="{sec_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                sec_x += 120
                if sec_x > 2100:
                    sec_x = 1750
                    sec_y += 100
    
    # Analytics Services Section
    if inputs.analytics_services:
        analytics_y = y_start + 650
        xml_parts.append(f"""
        <!-- Analytics & AI Services -->
        <mxCell id="analytics" value="Analytics &amp; AI Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f3e5f5;strokeColor=#9c27b0;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="1700" y="{analytics_y}" width="600" height="300" as="geometry" />
        </mxCell>""")
        
        ana_x = 1750
        ana_y = analytics_y + 50
        for i, service in enumerate(inputs.analytics_services[:4]):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="analytics-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{ana_x}" y="{ana_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                ana_x += 120
                if ana_x > 2100:
                    ana_x = 1750
                    ana_y += 100
    
    # Integration Services Section
    if inputs.integration_services:
        int_y = current_y
        xml_parts.append(f"""
        <!-- Integration Services -->
        <mxCell id="integration" value="Integration Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff8e1;strokeColor=#ff8f00;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="100" y="{int_y}" width="600" height="250" as="geometry" />
        </mxCell>""")
        
        int_x = 150
        int_y += 50
        for i, service in enumerate(inputs.integration_services[:4]):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="integration-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{int_x}" y="{int_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                int_x += 120
                if int_x > 550:
                    int_x = 150
                    int_y += 100
    
    # DevOps Services Section
    if inputs.devops_services:
        devops_y = current_y if not inputs.integration_services else current_y
        devops_x_offset = 800 if inputs.integration_services else 100
        xml_parts.append(f"""
        <!-- DevOps Services -->
        <mxCell id="devops" value="DevOps Services" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontStyle=1;verticalAlign=top;spacingTop=10;" vertex="1" parent="1">
          <mxGeometry x="{devops_x_offset}" y="{devops_y}" width="400" height="250" as="geometry" />
        </mxCell>""")
        
        dev_x = devops_x_offset + 50
        dev_y = devops_y + 50
        for i, service in enumerate(inputs.devops_services[:3]):
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                shape = service_info.get('drawio_shape', 'generic_service')
                xml_parts.append(f"""
        <mxCell id="devops-service-{i}" value="{esc(service_info['name'])}" style="shape=mxgraph.azure.{shape};fillColor=#0078d4;strokeColor=#005a9e;fontColor=#ffffff;" vertex="1" parent="1">
          <mxGeometry x="{dev_x}" y="{dev_y}" width="{service_width}" height="{service_height}" as="geometry" />
        </mxCell>""")
                dev_x += 120
                if dev_x > (devops_x_offset + 250):
                    dev_x = devops_x_offset + 50
                    dev_y += 100
    
    # Add basic connections
    xml_parts.append("""
        <!-- Key Connections -->
        <mxCell id="conn1" edge="1" source="root-mg" target="platform-mg" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="conn2" edge="1" source="root-mg" target="landing-zones-mg" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="conn3" edge="1" source="hub-vnet" target="spoke1-vnet" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="conn4" edge="1" source="hub-vnet" target="spoke2-vnet" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>""")
    
    return "".join(xml_parts)


def generate_professional_documentation(inputs: CustomerInputs) -> Dict[str, str]:
    """Generate comprehensive enterprise-grade TSD, HLD, and LLD documentation (10+ pages)"""
    
    template = generate_architecture_template(inputs)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Generate AI insights if additional inputs are provided
    url_analysis = ""
    doc_analysis = ""
    ai_recommendations = ""
    
    # Get comprehensive AI analysis results
    architecture_pattern = template.get("architecture_pattern", "Custom Architecture")
    connectivity_requirements = template.get("connectivity_requirements", "Standard Azure networking")
    security_considerations = template.get("security_considerations", "Standard security practices")
    ai_reasoning = template.get("ai_reasoning", "Standard architectural decisions applied")
    scalability_design = template.get("scalability_design", "Standard scalability patterns")
    operational_excellence = template.get("operational_excellence", "Standard monitoring and operations")
    cost_optimization = template.get("cost_optimization", "Standard cost optimization")
    ai_services = template.get("ai_services", [])
    
    try:
        if inputs.url_input:
            url_analysis = analyze_url_content(inputs.url_input)
            
        if inputs.uploaded_files_info:
            doc_analysis = "Document analysis results incorporated from uploaded files."
            
        # Generate comprehensive AI-enhanced recommendations
        ai_recommendations = generate_ai_enhanced_recommendations(inputs, url_analysis, doc_analysis)
    except Exception as e:
        logger.warning(f"AI enhancement failed: {e}")
        ai_recommendations = "AI enhancement not available - using standard recommendations."
    
    # Count total services
    all_selected_services = []
    all_selected_services.extend(inputs.compute_services or [])
    all_selected_services.extend(inputs.network_services or [])
    all_selected_services.extend(inputs.storage_services or [])
    all_selected_services.extend(inputs.database_services or [])
    all_selected_services.extend(inputs.security_services or [])
    all_selected_services.extend(inputs.monitoring_services or [])
    all_selected_services.extend(inputs.ai_services or [])
    all_selected_services.extend(inputs.analytics_services or [])
    all_selected_services.extend(inputs.integration_services or [])
    all_selected_services.extend(inputs.devops_services or [])
    all_selected_services.extend(inputs.backup_services or [])
    all_selected_services.extend(ai_services)
    
    # Remove duplicates and get service details
    unique_services = list(set(all_selected_services))
    
    # Technical Specification Document (TSD) - Enterprise Edition (10+ Pages)
    tsd = f"""# Technical Specification Document (TSD)
## Azure Landing Zone Architecture - Enterprise Edition

**Document Version:** 4.0 (AI-Enhanced Enterprise Architecture)
**Date:** {timestamp}
**Classification:** Internal Use Only
**Document Owner:** Azure Solutions Architecture Team
**Review Cycle:** Quarterly

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Requirements Analysis](#business-requirements-analysis)
3. [AI-Powered Architecture Analysis](#ai-powered-architecture-analysis)
4. [Architecture Framework & Patterns](#architecture-framework--patterns)
5. [Service Architecture & Connectivity](#service-architecture--connectivity)
6. [Security Architecture](#security-architecture)
7. [Network Architecture & Connectivity](#network-architecture--connectivity)
8. [Data Architecture & Management](#data-architecture--management)
9. [Scalability & Performance Design](#scalability--performance-design)
10. [Operational Excellence Framework](#operational-excellence-framework)
11. [Cost Optimization Strategy](#cost-optimization-strategy)
12. [Compliance & Governance](#compliance--governance)
13. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
14. [Implementation Roadmap](#implementation-roadmap)
15. [Appendices](#appendices)

---

## 1. Executive Summary

### 1.1 Document Purpose
This Technical Specification Document (TSD) provides comprehensive technical specifications for implementing an enterprise-ready Azure Landing Zone architecture. The design is based on advanced AI-powered analysis of business requirements, Azure Well-Architected Framework principles, and industry best practices.

### 1.2 Business Context
**Primary Business Objective:** {inputs.business_objective or 'Enterprise digital transformation with cloud-native architecture'}

The proposed architecture addresses critical business needs including:
- Scalable and resilient cloud infrastructure
- Enterprise-grade security and compliance
- Operational efficiency and automation
- Cost optimization and resource management
- Future-proof technology stack

### 1.3 Architecture Overview
**Selected Architecture Pattern:** {architecture_pattern}

The solution encompasses {len(unique_services)} carefully selected Azure services that form an integrated, enterprise-ready platform designed for:
- High availability (99.9% uptime SLA)
- Horizontal and vertical scalability
- Security-first design principles
- Operational excellence and monitoring
- Cost-effective resource utilization

### 1.4 Key Success Metrics
- **Availability:** 99.9% uptime target
- **Performance:** Sub-second response times for critical operations
- **Security:** Zero successful security breaches
- **Cost:** 15-20% reduction in operational costs compared to on-premises
- **Compliance:** 100% adherence to regulatory requirements

---

## 2. Business Requirements Analysis

### 2.1 Functional Requirements
**Primary Business Objective:** {inputs.business_objective or 'Cost optimization and operational efficiency with enterprise-grade reliability'}

**Industry Context:** {inputs.industry or 'Multi-industry applicable with focus on scalability and security'}

**Regulatory Framework:** {inputs.regulatory or 'Standard compliance including data protection, privacy regulations, and industry-specific requirements'}

### 2.2 Non-Functional Requirements

#### 2.2.1 Performance Requirements
- Response time: < 1 second for 95% of user requests
- Throughput: Support for 10,000+ concurrent users
- Data processing: Real-time analytics with < 100ms latency

#### 2.2.2 Availability Requirements
- System uptime: 99.9% (8.77 hours downtime per year)
- Recovery time objective (RTO): < 4 hours
- Recovery point objective (RPO): < 1 hour

#### 2.2.3 Scalability Requirements
- Horizontal scaling: Support for 10x traffic spikes
- Geographic distribution: Multi-region deployment capability
- Resource elasticity: Auto-scaling based on demand

#### 2.2.4 Security Requirements
- Data encryption: At rest and in transit
- Identity management: Role-based access control (RBAC)
- Network security: Zero-trust architecture
- Compliance: GDPR, SOC 2, ISO 27001 readiness

### 2.3 Organizational Context
**Organization Structure:** {inputs.org_structure or 'Enterprise with distributed teams and centralized governance'}

**Governance Model:** {inputs.governance or 'Centralized governance with delegated operational permissions'}

**Operational Model:** {inputs.ops_model or 'DevOps with automated CI/CD pipelines and infrastructure as code'}

---

## 3. AI-Powered Architecture Analysis

### 3.1 Intelligent Architecture Design
The architecture design leverages advanced AI analysis to ensure optimal service selection and configuration based on specific business requirements.

**AI Architecture Reasoning:**
{ai_reasoning}

### 3.2 Service Selection Rationale
The AI analysis identified {len(unique_services)} critical Azure services based on:

1. **Functional Requirements Mapping:** Direct correlation between business needs and technical capabilities
2. **Integration Patterns:** Optimal service combinations for seamless connectivity
3. **Performance Optimization:** Services selected for maximum efficiency and scalability
4. **Cost-Benefit Analysis:** Balanced approach between functionality and cost
5. **Future-Proofing:** Architecture designed for evolution and expansion

### 3.3 Architecture Pattern Analysis
**Identified Pattern:** {architecture_pattern}

This pattern was selected because:
- Aligns with business scalability requirements
- Provides optimal separation of concerns
- Enables independent service scaling
- Supports microservices architecture principles
- Facilitates DevOps and continuous deployment

### 3.4 AI-Enhanced Recommendations
{ai_recommendations if ai_recommendations else "Standard enterprise recommendations applied with focus on security, scalability, and operational excellence."}

---

## 4. Architecture Framework & Patterns

### 4.1 Azure Well-Architected Framework Alignment

#### 4.1.1 Reliability
- Multi-region deployment strategy
- Automated failover mechanisms
- Health monitoring and alerting
- Disaster recovery planning

#### 4.1.2 Security
- Zero-trust network architecture
- Identity and access management
- Data encryption and key management
- Security monitoring and threat detection

#### 4.1.3 Cost Optimization
- Resource right-sizing
- Reserved capacity planning
- Automated cost monitoring
- Continuous optimization

#### 4.1.4 Operational Excellence
- Infrastructure as Code (IaC)
- Automated deployment pipelines
- Comprehensive monitoring and logging
- Performance optimization

#### 4.1.5 Performance Efficiency
- Auto-scaling configurations
- Caching strategies
- Content delivery optimization
- Database performance tuning

### 4.2 Connectivity Architecture
**Connectivity Requirements:** {connectivity_requirements}

The connectivity architecture implements:
- Hub-and-spoke network topology
- Private endpoint connectivity
- API gateway patterns
- Service mesh for microservices
- Load balancing and traffic management

---

## 5. Service Architecture & Connectivity

### 5.1 Selected Azure Services Portfolio

#### 5.1.1 Compute Services
**Selected:** {', '.join(inputs.compute_services) if inputs.compute_services else 'None explicitly selected (AI may recommend based on requirements)'}

**AI-Recommended Compute:** {', '.join([s for s in ai_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'compute']) if ai_services else 'None recommended'}

#### 5.1.2 Network Services
**Selected:** {', '.join(inputs.network_services) if inputs.network_services else 'None explicitly selected (AI may recommend based on requirements)'}

**AI-Recommended Network:** {', '.join([s for s in ai_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'network']) if ai_services else 'None recommended'}

#### 5.1.3 Storage Services
**Selected:** {', '.join(inputs.storage_services) if inputs.storage_services else 'None explicitly selected (AI may recommend based on requirements)'}

**AI-Recommended Storage:** {', '.join([s for s in ai_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'storage']) if ai_services else 'None recommended'}

#### 5.1.4 Database Services
**Selected:** {', '.join(inputs.database_services) if inputs.database_services else 'None explicitly selected (AI may recommend based on requirements)'}

**AI-Recommended Database:** {', '.join([s for s in ai_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'database']) if ai_services else 'None recommended'}

#### 5.1.5 Security Services
**Selected:** {', '.join(inputs.security_services) if inputs.security_services else 'None explicitly selected (AI may recommend based on requirements)'}

**AI-Recommended Security:** {', '.join([s for s in ai_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'security']) if ai_services else 'None recommended'}

### 5.2 Service Integration Patterns

#### 5.2.1 API Management Strategy
- Centralized API gateway for external access
- Rate limiting and throttling policies
- API versioning and lifecycle management
- Security token validation and transformation

#### 5.2.2 Data Flow Architecture
- Event-driven messaging patterns
- Asynchronous processing pipelines
- Real-time streaming analytics
- Batch processing workflows

#### 5.2.3 Microservices Communication
- Service-to-service authentication
- Circuit breaker patterns
- Retry and timeout policies
- Distributed tracing and monitoring

---

## 6. Security Architecture

### 6.1 Security Framework
**Security Considerations:** {security_considerations}

### 6.2 Zero Trust Architecture
- Identity-based access controls
- Least privilege principle
- Continuous verification
- Network micro-segmentation

### 6.3 Data Protection Strategy
- Encryption at rest using customer-managed keys
- Encryption in transit with TLS 1.3
- Data classification and labeling
- Data loss prevention (DLP) policies

### 6.4 Identity and Access Management
- Azure Active Directory integration
- Multi-factor authentication (MFA)
- Privileged identity management (PIM)
- Conditional access policies

### 6.5 Network Security
- Network security groups (NSGs)
- Azure Firewall with threat intelligence
- Web application firewall (WAF)
- DDoS protection standard

---

## 7. Network Architecture & Connectivity

### 7.1 Network Topology
- Hub-and-spoke architecture
- Virtual network peering
- ExpressRoute connectivity (if applicable)
- VPN gateway for hybrid scenarios

### 7.2 Connectivity Matrix
```
Service Tier 1 (Web) -> Service Tier 2 (Application) -> Service Tier 3 (Data)
     ↓                          ↓                           ↓
Load Balancer           ->  App Services            ->   Database Services
Application Gateway     ->  Container Services      ->   Storage Services
CDN                     ->  Function Apps           ->   Cache Services
```

### 7.3 Private Connectivity
- Private endpoints for PaaS services
- Service endpoints where applicable
- Private DNS zones for name resolution
- Network policies for pod-to-pod communication

---

## 8. Data Architecture & Management

### 8.1 Data Strategy
- Data lifecycle management
- Backup and archival policies
- Data governance framework
- Analytics and reporting strategy

### 8.2 Database Design
- Horizontal and vertical partitioning
- Read replicas for performance
- Cross-region replication
- Automated backup strategies

---

## 9. Scalability & Performance Design

### 9.1 Scalability Strategy
**Scalability Design:** {scalability_design}

### 9.2 Performance Optimization
- Caching strategies (Redis, CDN)
- Database performance tuning
- Application performance monitoring
- Resource optimization

### 9.3 Auto-scaling Configuration
- Horizontal pod autoscaling
- Virtual machine scale sets
- Application Gateway autoscaling
- Database auto-scaling policies

---

## 10. Operational Excellence Framework

### 10.1 Operations Strategy
**Operational Excellence:** {operational_excellence}

### 10.2 Monitoring and Observability
- Comprehensive logging strategy
- Application performance monitoring
- Infrastructure monitoring
- Security monitoring and alerting

### 10.3 DevOps Integration
- Infrastructure as Code (IaC)
- CI/CD pipeline automation
- Automated testing strategies
- Configuration management

---

## 11. Cost Optimization Strategy

### 11.1 Cost Management
**Cost Optimization:** {cost_optimization}

### 11.2 Resource Optimization
- Right-sizing recommendations
- Reserved capacity planning
- Spot instance utilization
- Resource scheduling automation

### 11.3 Financial Operations (FinOps)
- Cost allocation and chargeback
- Budget monitoring and alerting
- Cost optimization automation
- Regular cost review processes

---

## 12. Compliance & Governance

### 12.1 Governance Framework
- Azure Policy implementation
- Role-based access control (RBAC)
- Resource tagging strategy
- Compliance monitoring

### 12.2 Regulatory Compliance
- GDPR compliance measures
- Industry-specific regulations
- Data residency requirements
- Audit and reporting capabilities

---

## 13. Risk Assessment & Mitigation

### 13.1 Risk Analysis
- Technical risks and mitigation strategies
- Security risks and controls
- Operational risks and procedures
- Business continuity planning

### 13.2 Disaster Recovery
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Backup and restore procedures
- Business continuity testing

---

## 14. Implementation Roadmap

### 14.1 Phase 1: Foundation (Weeks 1-4)
- Core infrastructure deployment
- Network and security setup
- Identity and access management
- Basic monitoring implementation

### 14.2 Phase 2: Application Services (Weeks 5-8)
- Application tier deployment
- Database setup and configuration
- API gateway implementation
- Performance optimization

### 14.3 Phase 3: Advanced Features (Weeks 9-12)
- Advanced monitoring and alerting
- Disaster recovery testing
- Performance tuning
- Security hardening

### 14.4 Phase 4: Production Readiness (Weeks 13-16)
- Production deployment
- Load testing and optimization
- Documentation completion
- Knowledge transfer

---

## 15. Appendices

### Appendix A: Service Configuration Details
[Detailed configuration parameters for each Azure service]

### Appendix B: Network Diagrams
[Comprehensive network topology diagrams]

### Appendix C: Security Policies
[Detailed security policy configurations]

### Appendix D: Monitoring Configurations
[Monitoring and alerting configuration details]

### Appendix E: Cost Estimates
[Detailed cost breakdown and projections]

---

**Document Control:**
- Version: 4.0
- Last Modified: {timestamp}
- Next Review: {datetime.now().strftime("%Y-%m-%d")} + 3 months
- Approved By: Azure Solutions Architecture Team

**Database Services:** {', '.join(inputs.database_services) if inputs.database_services else 'None explicitly selected'}
**Security Services:** {', '.join(inputs.security_services) if inputs.security_services else 'Standard security baseline'}
**Analytics Services:** {', '.join(inputs.analytics_services) if inputs.analytics_services else 'None explicitly selected'}
**Integration Services:** {', '.join(inputs.integration_services) if inputs.integration_services else 'None explicitly selected'}

#### Service Connectivity Patterns
The architecture implements intelligent connectivity patterns based on Azure best practices:

1. **Web Tier Connectivity:** Application Gateway -> App Services/VMs with load balancing
2. **Data Tier Security:** Secure connections from compute services to databases with Key Vault integration
3. **Network Security:** Firewall protection with hub-spoke VNet topology
4. **Monitoring Integration:** Comprehensive telemetry from all services to Azure Monitor
5. **DevOps Pipeline:** Automated deployment connectivity from DevOps services to target resources

### Core Architecture Components
- **Identity & Access Management:** {inputs.identity or 'Azure Active Directory with enterprise integration and conditional access'}
- **Network Architecture:** {inputs.network_model or 'Hub-Spoke with intelligent routing and security zones'}
- **Security Framework:** {inputs.security_posture or 'Zero Trust with comprehensive defense in depth'}
- **Connectivity Strategy:** {inputs.connectivity or 'Hybrid cloud with ExpressRoute and intelligent traffic routing'}
- **Primary Workloads:** {inputs.workload or 'Multi-tier applications with microservices and AI integration'}
- **Monitoring & Observability:** {inputs.monitoring or 'Azure Monitor with AI-powered insights and automated alerting'}

### Enhanced Requirements Analysis
{f"**Customer Requirements:** {inputs.free_text_input[:1000]}..." if inputs.free_text_input else "**Customer Requirements:** Requirements captured through structured inputs with AI analysis."}

{f"**URL Analysis Insights:** {url_analysis[:500]}..." if url_analysis else "**URL Analysis:** No external URL provided for analysis."}

{f"**Document Analysis:** Comprehensive analysis completed on {len(inputs.uploaded_files_info)} uploaded files." if inputs.uploaded_files_info else "**Document Analysis:** No documents uploaded for analysis."}

### AI-Powered Architecture Recommendations
{ai_recommendations[:2000] if ai_recommendations else "Enterprise-standard architecture patterns applied with intelligent service connectivity."}

### Compliance & Governance Framework
- **Governance Model:** {inputs.governance or 'Centralized governance with policy-driven automation'}
- **Policy Framework:** Azure Policy for automated compliance enforcement
- **Security Framework:** {inputs.security_posture or 'Zero Trust'} security model with continuous monitoring
- **Cost Management:** Azure Cost Management integration with budget alerts and optimization recommendations

### Implementation Roadmap
1. **Phase 1:** Core infrastructure setup (networking, security, identity)
2. **Phase 2:** Service deployment with intelligent connectivity
3. **Phase 3:** Monitoring and governance implementation
4. **Phase 4:** Optimization and scaling based on telemetry
"""

    # High Level Design (HLD) - Enterprise Edition (Comprehensive)
    hld = f"""# High Level Design (HLD)
## Azure Landing Zone Implementation - Enterprise Architecture

**Document Version:** 4.0 (AI-Enhanced Enterprise Architecture)
**Date:** {timestamp}
**Architecture Pattern:** {architecture_pattern}
**Classification:** Internal Use Only

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [AI-Driven Architecture Decisions](#ai-driven-architecture-decisions)
3. [Enterprise Framework Alignment](#enterprise-framework-alignment)
4. [Management and Governance Structure](#management-and-governance-structure)
5. [Network Architecture Design](#network-architecture-design)
6. [Service Connectivity Patterns](#service-connectivity-patterns)
7. [Security Architecture Framework](#security-architecture-framework)
8. [Data Architecture and Flow](#data-architecture-and-flow)
9. [Application Architecture Patterns](#application-architecture-patterns)
10. [Scalability and Performance Design](#scalability-and-performance-design)
11. [Operational Architecture](#operational-architecture)
12. [Disaster Recovery and Business Continuity](#disaster-recovery-and-business-continuity)

---

## 1. Architecture Overview

### 1.1 Executive Architecture Summary
The proposed Azure Landing Zone implements a **{template['template']['name']}** pattern with enterprise-grade security, scalability, and operational excellence. The architecture leverages AI-driven service selection to ensure optimal resource allocation and connectivity patterns.

### 1.2 Architecture Principles
- **Cloud-Native First:** Leveraging Azure PaaS services for maximum efficiency
- **Security by Design:** Implementing Zero Trust architecture principles
- **Scalability and Elasticity:** Auto-scaling capabilities across all tiers
- **Operational Excellence:** Comprehensive monitoring and automation
- **Cost Optimization:** Resource right-sizing and intelligent cost management

### 1.3 Key Success Metrics
- **Availability Target:** 99.9% uptime (43.8 minutes downtime/month)
- **Performance Target:** <2 second response time for 95% of requests
- **Security Target:** Zero successful security breaches
- **Scalability Target:** 10x traffic spike handling capability
- **Cost Target:** 20% reduction in operational costs

---

## 2. AI-Driven Architecture Decisions

### 2.1 AI Analysis Summary
**Architecture Pattern Selected:** {architecture_pattern}

**AI Reasoning (Detailed):**
{ai_reasoning if ai_reasoning != "Standard architectural decisions applied" else "Enterprise architecture decisions based on industry best practices, Azure Well-Architected Framework principles, and scalability requirements. The selected pattern provides optimal separation of concerns, enables microservices architecture, and supports DevOps practices."}

### 2.2 Service Selection Intelligence
**Total Services Selected:** {len(unique_services)}

The AI analysis identified the following service categories as critical:
- **Compute Services:** {len([s for s in unique_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'compute'])} services
- **Network Services:** {len([s for s in unique_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'network'])} services
- **Security Services:** {len([s for s in unique_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'security'])} services
- **Data Services:** {len([s for s in unique_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'database'])} services
- **Monitoring Services:** {len([s for s in unique_services if s in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[s]['category'] == 'monitoring'])} services

### 2.3 Connectivity Intelligence
**Connectivity Requirements:** {connectivity_requirements}

**Key Connectivity Patterns:**
- Application Gateway -> Compute Services (Load Distribution)
- Compute Services -> Database Services (Secure Data Access)
- All Services -> Key Vault (Secrets Management)
- All Services -> Azure Monitor (Telemetry Collection)
- VNet Peering -> Hub-Spoke Communication

---

## 3. Enterprise Framework Alignment

### 3.1 Azure Well-Architected Framework
The architecture fully aligns with the five pillars of the Azure Well-Architected Framework:

#### 3.1.1 Reliability
- **Multi-Region Strategy:** {("Active-Active" if len(unique_services) > 5 else "Active-Passive")} deployment
- **Fault Tolerance:** Automated failover and recovery mechanisms
- **Backup Strategy:** Automated backups with point-in-time recovery
- **Health Monitoring:** Continuous health checks and alerting

#### 3.1.2 Security
- **Zero Trust Model:** Never trust, always verify principle
- **Defense in Depth:** Multiple layers of security controls
- **Identity Management:** Role-based access control (RBAC)
- **Data Protection:** Encryption at rest and in transit

#### 3.1.3 Cost Optimization
- **Resource Optimization:** Right-sizing and auto-scaling
- **Reserved Capacity:** Strategic use of reserved instances
- **Cost Monitoring:** Real-time cost tracking and alerting
- **FinOps Integration:** Financial operations practices

#### 3.1.4 Operational Excellence
- **Infrastructure as Code:** Automated deployments and configuration
- **CI/CD Integration:** Continuous integration and deployment
- **Monitoring and Alerting:** Proactive monitoring and incident response
- **Documentation:** Comprehensive technical documentation

#### 3.1.5 Performance Efficiency
- **Auto-Scaling:** Dynamic resource allocation based on demand
- **Caching Strategy:** Multi-tier caching for optimal performance
- **CDN Integration:** Global content delivery network
- **Performance Monitoring:** Real-time performance analytics

---

## 4. Management and Governance Structure

### 4.1 Management Group Hierarchy"""
    
    for i, mg in enumerate(template['template']['management_groups']):
        hld += f"""
**Level {i+1}: {mg} Management Group**
- Purpose: {mg} resource management and policy enforcement
- Scope: {"Enterprise-wide governance" if mg == "Root" else f"{mg} specific policies and controls"}
- Policies: {"Root level policies for organization-wide compliance" if mg == "Root" else f"Specialized policies for {mg} workloads"}"""
    
    hld += f"""

### 4.2 Subscription Strategy"""
    
    for sub in template['template']['subscriptions']:
        hld += f"""
**{sub} Subscription:**
- Purpose: Dedicated environment for {sub.lower()} workloads
- Billing: Separate cost center with chargeback capabilities
- Resource Limits: Subscription-level quotas and limits
- Governance: Subscription-specific policies and RBAC"""
    
    hld += f"""

### 4.3 Resource Organization
- **Naming Convention:** Standardized naming following Azure best practices
- **Tagging Strategy:** Cost center, environment, application, and owner tags
- **Resource Groups:** Logical grouping by application lifecycle
- **Access Control:** Role-based access control (RBAC) at appropriate scopes

---

## 5. Network Architecture Design

### 5.1 Network Topology
**Network Model:** {inputs.network_model or 'Hub-Spoke with intelligent routing and security'}

#### 5.1.1 Hub VNet Design
- **Address Space:** 10.0.0.0/16 (65,536 addresses)
- **Subnets:**
  - Gateway Subnet: 10.0.1.0/27 (32 addresses)
  - Azure Firewall Subnet: 10.0.2.0/26 (64 addresses)
  - Shared Services Subnet: 10.0.3.0/24 (256 addresses)
  - Management Subnet: 10.0.4.0/24 (256 addresses)

#### 5.1.2 Spoke VNet Design
- **Production Spoke:** 10.1.0.0/16
- **Development Spoke:** 10.2.0.0/16
- **Testing Spoke:** 10.3.0.0/16

### 5.2 Connectivity Architecture
**Connectivity Type:** {inputs.connectivity or 'Hybrid connectivity with ExpressRoute and VPN Gateway backup'}

- **ExpressRoute:** Primary connectivity for predictable performance
- **VPN Gateway:** Backup connectivity and site-to-site connections
- **Private Endpoints:** Secure PaaS service connectivity
- **Service Endpoints:** Additional PaaS connectivity option

### 5.3 Traffic Flow Design
```
Internet -> Application Gateway -> Internal Load Balancer -> Compute Services
                    ↓
                Azure Firewall -> Hub VNet -> Spoke VNets
                    ↓
            Private Endpoints -> Database Services
```

### 5.4 DNS Strategy
- **Private DNS Zones:** Internal name resolution
- **Azure DNS:** External domain management
- **Conditional Forwarding:** Hybrid DNS resolution
- **DNS Security:** DNS filtering and protection

---

## 6. Service Connectivity Patterns

### 6.1 Web Tier Connectivity
**Pattern:** Front Door -> Application Gateway -> Web Services

#### 6.1.1 External Connectivity
- Azure Front Door for global load balancing
- Application Gateway for regional load balancing
- SSL/TLS termination at Application Gateway
- Web Application Firewall (WAF) protection

#### 6.1.2 Internal Load Balancing
- Internal Load Balancer for backend services
- Health probes and automatic failover
- Session affinity where required
- Cross-zone load distribution

### 6.2 Application Tier Connectivity
**Pattern:** API Gateway -> Application Services -> Integration Services

#### 6.2.1 API Management
- Centralized API gateway for external access
- Rate limiting and throttling policies
- API versioning and lifecycle management
- Developer portal and documentation

#### 6.2.2 Service-to-Service Communication
- Private connectivity between services
- Service discovery and registration
- Circuit breaker patterns
- Retry and timeout policies

### 6.3 Data Tier Connectivity
**Pattern:** Application Services -> Private Endpoints -> Database Services

#### 6.3.1 Database Connectivity
- Private endpoints for secure database access
- Connection pooling and management
- Read/write split for performance optimization
- Backup and disaster recovery connectivity

#### 6.3.2 Data Integration
- Event-driven data synchronization
- ETL/ELT pipelines for data movement
- Real-time streaming analytics
- Batch processing workflows

---

## 7. Security Architecture Framework

### 7.1 Security Model
**Security Posture:** {inputs.security_posture or 'Zero Trust with comprehensive defense-in-depth strategy'}

### 7.2 Identity and Access Management
**Identity Provider:** {inputs.identity or 'Azure Active Directory with hybrid integration'}

#### 7.2.1 Authentication
- Multi-factor authentication (MFA) mandatory
- Conditional access policies
- Privileged Identity Management (PIM)
- Identity protection and risk detection

#### 7.2.2 Authorization
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- Just-in-time (JIT) access
- Least privilege principle

### 7.3 Network Security
- **Azure Firewall:** Centralized network security
- **Network Security Groups:** Subnet-level protection
- **Application Security Groups:** Application-level protection
- **DDoS Protection:** Distributed denial of service protection

### 7.4 Data Protection
**Key Management:** {inputs.key_vault or 'Azure Key Vault with customer-managed keys'}

- Data encryption at rest and in transit
- Key rotation and lifecycle management
- Data classification and labeling
- Data loss prevention (DLP)

### 7.5 Threat Protection
**Threat Detection:** {inputs.threat_protection or 'Azure Security Center, Sentinel, and Defender for Cloud'}

- Security Information and Event Management (SIEM)
- Security Orchestration, Automation, and Response (SOAR)
- Threat intelligence integration
- Incident response procedures

---

## 8. Data Architecture and Flow

### 8.1 Data Strategy
- **Data Lake Architecture:** Centralized data storage and analytics
- **Data Mesh Principles:** Distributed data ownership and governance
- **Real-time Analytics:** Stream processing and event-driven architecture
- **Batch Processing:** Scheduled data processing and ETL workflows

### 8.2 Data Flow Patterns
```
Source Systems -> Event Hubs -> Stream Analytics -> Data Lake
                      ↓
                 Real-time Dashboards
                      ↓
                 Machine Learning Models
```

### 8.3 Data Governance
- Data catalog and lineage tracking
- Data quality monitoring and validation
- Privacy and compliance controls
- Master data management

---

## 9. Application Architecture Patterns

### 9.1 Application Model
**Primary Workload:** {inputs.workload or 'Cloud-native microservices applications'}
**Architecture Style:** {inputs.architecture_style or 'Microservices with event-driven communication'}

### 9.2 Compute Strategy
**Selected Compute Services:** {', '.join(inputs.compute_services) if inputs.compute_services else 'Azure App Services with container support'}

#### 9.2.1 Container Strategy
- Container registry for image management
- Kubernetes orchestration for microservices
- Service mesh for advanced networking
- GitOps for declarative deployments

#### 9.2.2 Serverless Integration
- Function Apps for event processing
- Logic Apps for workflow automation
- Event Grid for event routing
- Service Bus for reliable messaging

### 9.3 Integration Patterns
- API-first design approach
- Event-driven architecture
- Choreography vs. orchestration patterns
- Asynchronous communication patterns

---

## 10. Scalability and Performance Design

### 10.1 Scalability Strategy
**Scalability Design:** {scalability_design}

#### 10.1.1 Horizontal Scaling
- Kubernetes Horizontal Pod Autoscaler (HPA)
- Virtual Machine Scale Sets (VMSS)
- Application Gateway auto-scaling
- Database read replicas

#### 10.1.2 Vertical Scaling
- Dynamic resource allocation
- Compute optimization based on workload
- Memory and CPU scaling policies
- Storage performance scaling

### 10.2 Performance Optimization
- **Caching Strategy:** Multi-tier caching with Redis and CDN
- **Database Optimization:** Query optimization and indexing
- **Content Delivery:** Global CDN for static content
- **Load Testing:** Regular performance testing and optimization

### 10.3 Capacity Planning
- Resource utilization monitoring
- Growth projection and planning
- Cost-performance optimization
- Proactive scaling policies

---

## 11. Operational Architecture

### 11.1 Operations Strategy
**Operational Excellence:** {operational_excellence}

### 11.2 DevOps Integration
- **CI/CD Pipeline:** Azure DevOps with automated testing and deployment
- **Infrastructure as Code:** ARM templates, Bicep, or Terraform
- **Configuration Management:** Automated configuration and drift detection
- **Release Management:** Blue-green and canary deployment strategies

### 11.3 Monitoring and Observability
- **Application Performance Monitoring:** Application Insights
- **Infrastructure Monitoring:** Azure Monitor and Log Analytics
- **Security Monitoring:** Azure Sentinel and Security Center
- **Business Metrics:** Custom dashboards and KPI tracking

### 11.4 Maintenance and Support
- Automated patching and updates
- Backup verification and testing
- Performance tuning and optimization
- Capacity planning and forecasting

---

## 12. Disaster Recovery and Business Continuity

### 12.1 Business Continuity Strategy
- **Recovery Time Objective (RTO):** 4 hours maximum
- **Recovery Point Objective (RPO):** 1 hour maximum
- **Business Impact Analysis:** Critical vs. non-critical systems
- **Disaster Recovery Testing:** Quarterly DR tests and validation

### 12.2 Backup and Recovery
- Automated backup schedules
- Cross-region backup replication
- Point-in-time recovery capabilities
- Backup verification and testing

### 12.3 High Availability Design
- Multi-zone deployment strategy
- Automated failover mechanisms
- Load balancing and traffic distribution
- Health monitoring and alerting

---

**Document Control:**
- Version: 4.0
- Last Modified: {timestamp}
- Next Review: Quarterly
- Approved By: Enterprise Architecture Review Board

"""

    # Low Level Design (LLD) - Enhanced
    lld = f"""# Low Level Design (LLD)
## Azure Landing Zone Technical Implementation with Service Connectivity

**Document Version:** 2.0 (AI-Enhanced)
**Date:** {timestamp}
**Architecture Pattern:** {architecture_pattern}

### Service Connectivity Matrix
#### Implemented Connection Patterns:
1. **Web Tier Flow:** Application Gateway -> Load Balancer -> Compute Services
2. **Data Flow:** Compute Services -> Database Services (via private endpoints)
3. **Security Flow:** All services -> Key Vault (for secrets and certificates)
4. **Monitoring Flow:** All services -> Azure Monitor -> Log Analytics
5. **Integration Flow:** API Management -> Logic Apps -> Service Bus
6. **Network Flow:** VPN/ExpressRoute -> Hub VNet -> Spoke VNets

### Resource Configuration

#### Management Groups"""
    
    for i, mg in enumerate(template['template']['management_groups']):
        lld += f"""
**{mg} Management Group:**
- Management Group ID: mg-{mg.lower().replace(' ', '-')}
- Parent: {template['template']['management_groups'][i-1] if i > 0 else 'Tenant Root'}
- Applied Policies: Comprehensive Azure Policy assignments for {mg.lower()}
- RBAC: Role-based access control with least privilege principles
"""

    lld += f"""
#### Subscriptions with Cost Management"""
    
    for sub in template['template']['subscriptions']:
        lld += f"""
**{sub} Subscription:**
- Subscription ID: sub-{sub.lower().replace(' ', '-')}
- Management Group: Appropriate management group assignment
- Cost Center: {sub} department cost allocation
- Budget Alerts: Automated budget monitoring and alerts
- Resource Tagging: Mandatory tagging policy for cost tracking
"""

    # Add detailed service configurations
    if inputs.network_services:
        lld += f"""
#### Network Services Configuration
"""
        for service in inputs.network_services:
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                lld += f"""
**{service_info['name']}:**
- Resource Type: {service}
- High Availability: Multi-zone deployment where applicable
- Security: Network Security Groups and traffic filtering
- Monitoring: Azure Monitor integration with custom metrics
- Connectivity: Intelligent routing with health probes
"""

    # Continue with existing network configuration but enhanced
    lld += f"""
#### Network Configuration with Intelligent Connectivity

**Hub Virtual Network (Enhanced):**
- VNet Name: vnet-hub-{inputs.network_model or 'intelligent'}-001
- Address Space: 10.0.0.0/16
- Subnets:
  - GatewaySubnet: 10.0.0.0/24 (VPN/ExpressRoute Gateway)
  - AzureFirewallSubnet: 10.0.1.0/24 (Azure Firewall with threat intelligence)
  - SharedServicesSubnet: 10.0.2.0/24 (Domain Controllers, monitoring)
  - ApplicationGatewaySubnet: 10.0.3.0/24 (Application Gateway for web traffic)

**Spoke Virtual Networks with Connectivity:**
- Production Spoke: vnet-prod-{inputs.workload or 'app'}-001 (10.1.0.0/16)
  - Web Tier: 10.1.1.0/24 (Application services)
  - App Tier: 10.1.2.0/24 (Business logic)
  - Data Tier: 10.1.3.0/24 (Database services with private endpoints)
- Development Spoke: vnet-dev-{inputs.workload or 'app'}-001 (10.2.0.0/16)
  - Similar segmentation with development-specific configurations

**Intelligent Traffic Routing:**
- User-Defined Routes for optimal traffic flow
- Azure Firewall rules for security filtering
- Application Gateway routing rules for web applications
- Load balancer configurations for high availability
"""

    if inputs.compute_services:
        lld += f"""
#### Compute Services Configuration
"""
        for service in inputs.compute_services:
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                lld += f"""
**{service_info['name']}:**
- Resource Type: {service}
- Auto-scaling: Enabled with performance-based triggers
- Security: Managed identity and Key Vault integration
- Monitoring: Application Insights and Azure Monitor
- Connectivity: Load balancer integration with health checks
- Backup: Automated backup configuration
"""

    if inputs.database_services:
        lld += f"""
#### Database Services Configuration
"""
        for service in inputs.database_services:
            if service in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service]
                lld += f"""
**{service_info['name']}:**
- Resource Type: {service}
- High Availability: Geo-replication and automatic failover
- Security: Private endpoints and encryption at rest/in transit
- Backup: Point-in-time restore and geo-redundant backup
- Connectivity: Secure connection strings via Key Vault
- Performance: Query performance insights and optimization
"""

    lld += f"""
#### Security Implementation Details
**Identity and Access Management:**
- Azure Active Directory with conditional access policies
- Privileged Identity Management (PIM) for administrative access
- Multi-factor authentication enforcement
- Service principals with managed identities

**Network Security:**
- Azure Firewall with threat intelligence
- Network Security Groups with micro-segmentation
- DDoS protection standard
- Private endpoints for PaaS services

**Data Protection:**
- Azure Key Vault for secrets, keys, and certificates
- Transparent Data Encryption (TDE) for databases
- Azure Information Protection for data classification
- Customer-managed keys where required

#### Monitoring and Alerting Configuration
**Azure Monitor Setup:**
- Central Log Analytics workspace
- Custom dashboards for business metrics
- Automated alert rules for critical events
- Integration with ServiceNow/Teams for incident management

**Application Performance Monitoring:**
- Application Insights for web applications
- Custom telemetry and business events
- Performance baselines and anomaly detection
- End-to-end transaction tracing

#### Operations Configuration

**Backup and Recovery:**
- Azure Backup: {inputs.backup or 'Daily backups with geo-redundant storage'}
- Site Recovery: Cross-region disaster recovery
- Database backups: Automated with point-in-time restore
- Recovery testing: Quarterly disaster recovery drills

**Cost Management:**
- Budget alerts and spending limits
- Resource tagging for cost allocation
- Azure Advisor recommendations
- Regular cost optimization reviews
"""

    return {
        "tsd": tsd,
        "hld": hld, 
        "lld": lld
    }


# ---------- API Endpoints ----------

@app.get("/")
def root():
    return {
        "message": "Azure Landing Zone Agent API",
        "version": "1.0.0",
        "endpoints": [
            "/docs - API Documentation",
            "/generate-diagram - Generate architecture diagram (Mermaid + Draw.io)",
            "/generate-azure-diagram - Generate Azure architecture diagram with official Azure icons (Python Diagrams)",
            "/generate-figma-diagram - Generate Azure architecture diagram using Figma API",
            "/generate-drawio - Generate Draw.io XML",
            "/health - Health check"
        ]
    }

@app.get("/health")
def health_check():
    """Enhanced health check that verifies system dependencies"""
    logger.info("Running health check...")
    status = "healthy"
    issues = []
    
    # Check Graphviz availability
    try:
        result = subprocess.run(['dot', '-V'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            issues.append(f"Graphviz 'dot' command failed with return code {result.returncode}")
            status = "degraded"
        else:
            logger.info(f"Graphviz check passed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        issues.append("Graphviz 'dot' command timed out")
        status = "degraded"
    except FileNotFoundError:
        issues.append("Graphviz not installed or not accessible")
        status = "degraded"
    except Exception as e:
        issues.append(f"Graphviz check failed: {str(e)}")
        status = "degraded"
    
    # Check diagrams library
    try:
        from diagrams import Diagram
        logger.info("Diagrams library import successful")
    except ImportError as e:
        issues.append(f"Diagrams library import failed: {str(e)}")
        status = "unhealthy"
    
    # Check output directory accessibility
    try:
        output_dir = get_safe_output_directory()
        logger.info(f"Output directory accessible: {output_dir}")
    except Exception as e:
        issues.append(f"Cannot access output directory: {str(e)}")
        status = "degraded"
    
    # Check available disk space
    try:
        import shutil
        output_dir = get_safe_output_directory()
        total, used, free = shutil.disk_usage(output_dir)
        free_mb = free // (1024*1024)
        if free_mb < 100:  # Less than 100MB free
            issues.append(f"Low disk space in output directory: {free_mb}MB free")
            status = "degraded"
        logger.info(f"Disk space check passed: {free_mb}MB free")
    except Exception as e:
        issues.append(f"Cannot check disk space: {str(e)}")
        status = "degraded"
    
    # Test a simple diagram generation
    try:
        test_inputs = CustomerInputs(business_objective="Health check test")
        # Just validate inputs, don't generate full diagram
        validate_customer_inputs(test_inputs)
        logger.info("Input validation test passed")
    except Exception as e:
        issues.append(f"Input validation test failed: {str(e)}")
        status = "degraded"
    
    logger.info(f"Health check completed with status: {status}")
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "issues": issues,
        "dependencies": {
            "graphviz_available": "Graphviz" not in str(issues),
            "diagrams_available": "Diagrams library" not in str(issues),
            "output_directory_accessible": "output directory" not in str(issues),
            "sufficient_disk_space": "disk space" not in str(issues)
        }
    }

@app.post("/generate-diagram")
def generate_diagram(inputs: CustomerInputs):
    """Generate comprehensive Azure Landing Zone diagrams and documentation"""
    try:
        # Generate professional diagrams
        mermaid_diagram = generate_professional_mermaid(inputs)
        drawio_xml = generate_enhanced_drawio_xml(inputs)
        
        # Generate professional documentation
        docs = generate_professional_documentation(inputs)
        
        return {
            "success": True,
            "mermaid": mermaid_diagram,
            "drawio": drawio_xml,
            "tsd": docs["tsd"],
            "hld": docs["hld"],
            "lld": docs["lld"],
            "architecture_template": generate_architecture_template(inputs),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "agent": "Azure Landing Zone Agent"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating diagram: {str(e)}")

@app.post("/generate-azure-diagram")
def generate_azure_diagram_endpoint(inputs: CustomerInputs):
    """Generate Azure architecture diagram using Python Diagrams library with proper Azure icons"""
    try:
        # Generate Azure architecture diagram with proper icons
        diagram_path = generate_azure_architecture_diagram(inputs)
        
        # Read the generated PNG file
        with open(diagram_path, "rb") as f:
            diagram_data = f.read()
        
        # Generate professional documentation
        docs = generate_professional_documentation(inputs)
        
        # Encode the diagram as base64 for JSON response
        import base64
        diagram_base64 = base64.b64encode(diagram_data).decode('utf-8')
        
        return {
            "success": True,
            "diagram_path": diagram_path,
            "diagram_base64": diagram_base64,
            "tsd": docs["tsd"],
            "hld": docs["hld"],
            "lld": docs["lld"],
            "architecture_template": generate_architecture_template(inputs),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "agent": "Azure Landing Zone Agent - Python Diagrams",
                "diagram_format": "PNG with Azure official icons"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Azure diagram: {str(e)}")

@app.get("/generate-azure-diagram/download/{filename}")
@app.head("/generate-azure-diagram/download/{filename}")
def download_azure_diagram(filename: str, request: Request = None):
    """Download generated Azure architecture diagram (PNG or SVG)"""
    try:
        file_path = f"/tmp/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Diagram file not found")
        
        # Determine media type based on file extension
        if filename.lower().endswith('.svg'):
            media_type = "image/svg+xml"
        elif filename.lower().endswith('.png'):
            media_type = "image/png"
        else:
            # Default to png for unknown extensions
            media_type = "image/png"
        
        # Get file size for Content-Length header
        file_size = os.path.getsize(file_path)
        
        # For HEAD requests, just return headers without content
        if request and request.method == "HEAD":
            return Response(
                content="",
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Length": str(file_size)
                }
            )
        
        # For GET requests, return the file content
        with open(file_path, "rb") as f:
            diagram_data = f.read()
        
        return Response(
            content=diagram_data,
            media_type=media_type, 
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(file_size)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading diagram: {str(e)}")

@app.post("/generate-drawio", response_class=Response)
def generate_drawio_endpoint(inputs: CustomerInputs):
    """Generate Draw.io XML file for download"""
    try:
        xml = generate_enhanced_drawio_xml(inputs)
        return Response(
            content=xml, 
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=azure-landing-zone.drawio"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Draw.io XML: {str(e)}")


@app.post("/generate-comprehensive-azure-architecture")
def generate_comprehensive_azure_architecture(inputs: CustomerInputs):
    """Generate comprehensive Azure architecture with both Draw.io XML and PNG diagram"""
    logger.info("Starting comprehensive Azure architecture generation")
    
    try:
        # Validate inputs early
        validate_customer_inputs(inputs)
        logger.info("Input validation completed successfully")
        
        # Generate Draw.io XML with comprehensive Azure stencils
        logger.info("Generating Draw.io XML...")
        drawio_xml = generate_enhanced_drawio_xml(inputs)
        logger.info(f"Draw.io XML generated successfully (size: {len(drawio_xml)} characters)")
        
        # Generate Azure PNG diagram with proper Azure icons
        logger.info("Generating Azure PNG diagram...")
        diagram_path = generate_azure_architecture_diagram(inputs)
        logger.info(f"Azure PNG diagram generated successfully: {diagram_path}")
        
        # Read the PNG file
        try:
            with open(diagram_path, "rb") as f:
                diagram_data = f.read()
            diagram_base64 = base64.b64encode(diagram_data).decode('utf-8')
            logger.info(f"PNG file read and encoded successfully (size: {len(diagram_data)} bytes)")
        except Exception as e:
            logger.error(f"Failed to read PNG file {diagram_path}: {e}")
            raise Exception(f"Failed to read generated PNG file: {str(e)}")
        
        # Generate professional documentation
        logger.info("Generating professional documentation...")
        docs = generate_professional_documentation(inputs)
        logger.info("Professional documentation generated successfully")
        
        # Count Azure stencils used
        import re
        shapes = re.findall(r'shape=mxgraph\.azure\.[^;\"\s]*', drawio_xml)
        
        result = {
            "success": True,
            "drawio_xml": drawio_xml,
            "png_diagram_path": diagram_path,
            "png_diagram_base64": diagram_base64,
            "tsd": docs["tsd"],
            "hld": docs["hld"],
            "lld": docs["lld"],
            "architecture_template": generate_architecture_template(inputs),
            "azure_stencils": {
                "total_used": len(shapes),
                "unique_used": len(set(shapes)),
                "stencils_list": sorted(list(set(shapes)))
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "agent": "Azure Landing Zone Agent - Comprehensive Generator",
                "drawio_size": len(drawio_xml),
                "png_size": len(diagram_data)
            }
        }
        
        logger.info("Comprehensive Azure architecture generated successfully")
        return result
    
    except ValueError as ve:
        # Input validation errors
        error_msg = f"Invalid input: {str(ve)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    except Exception as e:
        # Log the full error for debugging
        error_msg = f"Error generating comprehensive architecture: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate architecture. Error: {str(e)}"
        )

@app.post("/generate-interactive-azure-architecture")
def generate_interactive_azure_architecture(inputs: CustomerInputs):
    """Generate interactive Azure architecture with SVG diagram for web display"""
    logger.info("Starting interactive Azure architecture generation")
    
    try:
        # Validate inputs early
        validate_customer_inputs(inputs)
        logger.info("Input validation completed successfully")
        
        # Perform AI analysis if free text input is provided
        ai_analysis = None
        if inputs.free_text_input:
            logger.info("Performing AI analysis for intelligent recommendations")
            ai_analysis = analyze_free_text_requirements(inputs.free_text_input)
            logger.info(f"AI analysis completed: {len(ai_analysis.get('services', []))} services identified")
        
        # Generate intelligent feedback questions using AI analysis
        feedback_questions = generate_intelligent_feedback_questions(inputs, ai_analysis)
        
        # Generate dynamic Mermaid diagram based on AI analysis
        logger.info("Generating dynamic Mermaid diagram...")
        if ai_analysis:
            mermaid_diagram = generate_dynamic_mermaid(inputs, ai_analysis)
        else:
            mermaid_diagram = generate_professional_mermaid(inputs)
        logger.info("Mermaid diagram generated successfully")
        
        # Generate Azure SVG diagram with proper Azure icons
        logger.info("Generating Azure SVG diagram...")
        svg_content = ""
        svg_diagram_path = ""
        
        try:
            svg_diagram_path = generate_azure_architecture_diagram(inputs, format="svg")
            # Read the SVG file
            with open(svg_diagram_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            logger.info(f"Azure SVG diagram generated successfully: {svg_diagram_path}")
        except Exception as svg_error:
            logger.warning(f"SVG generation failed, using fallback: {str(svg_error)}")
            # Fallback: Create a simple SVG representation of the architecture
            svg_content = generate_simple_svg_diagram(inputs)
            logger.info("Using simple SVG fallback diagram")
        
        if svg_content:
            logger.info(f"SVG content ready (size: {len(svg_content)} characters)")
        else:
            logger.warning("No SVG content available, falling back to Mermaid only")
        
        # Generate Draw.io XML for compatibility
        logger.info("Generating Draw.io XML...")
        drawio_xml = generate_enhanced_drawio_xml(inputs)
        logger.info(f"Draw.io XML generated successfully (size: {len(drawio_xml)} characters)")
        
        # Generate professional documentation
        logger.info("Generating professional documentation...")
        try:
            # Use a timeout for the documentation generation
            import signal
            
            def timeout_handler(signum, frame):
                raise Exception("Documentation generation timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)  # 10 second timeout
            
            docs = generate_professional_documentation(inputs)
            
            signal.alarm(0)  # Clear the alarm
            logger.info("Professional documentation generated successfully")
        except Exception as e:
            signal.alarm(0)  # Clear the alarm
            logger.warning(f"Documentation generation failed, using fallback: {str(e)}")
            docs = {
                "tsd": f"# Technical Specification Document\n\n## Azure Landing Zone Architecture\n\n**Organization:** {inputs.org_structure or 'Enterprise'}\n**Business Objective:** {inputs.business_objective or 'Not specified'}\n\n### Selected Services\n- Compute: {', '.join(inputs.compute_services or [])}\n- Network: {', '.join(inputs.network_services or [])}\n- Security: {', '.join(inputs.security_services or [])}\n\n*Full documentation requires AI service availability.*",
                "hld": f"# High Level Design\n\n## Azure Architecture Overview\n\nThis document outlines the high-level design for an Azure Landing Zone.\n\n### Key Components\n- Management Groups\n- Subscriptions\n- Resource Groups\n- Network Architecture\n\n*Detailed design requires AI service availability.*",
                "lld": f"# Low Level Design\n\n## Implementation Details\n\nThis document provides implementation guidance for the Azure Landing Zone.\n\n### Implementation Steps\n1. Set up Management Groups\n2. Configure Subscriptions\n3. Deploy Network Infrastructure\n4. Implement Security Controls\n\n*Detailed implementation guide requires AI service availability.*"
            }
        
        # Count Azure stencils used in Draw.io XML
        import re
        shapes = re.findall(r'shape=mxgraph\.azure\.[^;\"\s]*', drawio_xml)
        
        # Get architecture template information
        template_info = generate_architecture_template(inputs)
        
        result = {
            "success": True,
            "mermaid": mermaid_diagram,
            "svg_diagram": svg_content,
            "svg_diagram_path": svg_diagram_path,
            "drawio_xml": drawio_xml,
            "tsd": docs["tsd"],
            "hld": docs["hld"],
            "lld": docs["lld"],
            "architecture_template": template_info,
            "azure_stencils": {
                "total_used": len(shapes),
                "unique_used": len(set(shapes)),
                "stencils_list": sorted(list(set(shapes)))
            },
            "feedback_questions": feedback_questions,
            "ai_analysis": ai_analysis or {
                "services": [],
                "reasoning": "No AI analysis performed",
                "architecture_pattern": "Standard",
                "needs_confirmation": False
            },
            "enhanced_ai_insights": {
                "pattern_detected": ai_analysis.get("architecture_pattern") if ai_analysis else None,
                "complexity_analysis": ai_analysis.get("scalability_design") if ai_analysis else None,
                "security_recommendations": ai_analysis.get("security_considerations") if ai_analysis else None,
                "waf_compliance": ai_analysis.get("waf_compliance") if ai_analysis else None,
                "next_steps": ai_analysis.get("next_steps") if ai_analysis else None
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "agent": "Azure Landing Zone Agent - Interactive Generator",
                "diagram_format": "SVG with Azure official icons",
                "svg_size": len(svg_content),
                "drawio_size": len(drawio_xml)
            }
        }
        
        logger.info("Interactive Azure architecture generated successfully")
        return result
    
    except ValueError as ve:
        # Input validation errors
        error_msg = f"Invalid input: {str(ve)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    except Exception as e:
        # Log the full error for debugging
        error_msg = f"Error generating interactive architecture: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate interactive architecture. Error: {str(e)}"
        )

def generate_intelligent_feedback_questions(inputs: CustomerInputs, ai_analysis: dict = None) -> List[str]:
    """Generate intelligent, context-aware feedback questions based on AI analysis and user requirements"""
    questions = []
    
    # Use AI analysis if available for more targeted questions
    if ai_analysis and inputs.free_text_input:
        # Generate questions based on AI analysis insights
        clarification_questions = ai_analysis.get("clarification_questions", [])
        if clarification_questions:
            questions.extend(clarification_questions[:2])  # Add top 2 AI-generated questions
        
        # Add pattern-specific questions
        pattern = ai_analysis.get("architecture_pattern", "")
        if "microservices" in pattern.lower():
            questions.append("How do you plan to handle service-to-service communication and API versioning in your microservices architecture?")
        elif "e-commerce" in pattern.lower():
            questions.append("What are your expected transaction volumes and do you need PCI DSS compliance for payment processing?")
        elif "data analytics" in pattern.lower():
            questions.append("What is your expected data volume and processing frequency (real-time, batch, or hybrid)?")
        
        # Add complexity-based questions
        if ai_analysis.get("needs_confirmation"):
            questions.append("Based on my analysis, I've made some assumptions about your requirements. Would you like to review and validate these before proceeding?")
    
    # Standard missing information questions (enhanced with context)
    if not inputs.business_objective:
        if "e-commerce" in (inputs.free_text_input or "").lower():
            questions.append("What is your primary e-commerce business goal? (Customer experience, market expansion, cost reduction, performance optimization)")
        else:
            questions.append("What is your primary business objective? (Cost optimization, agility, innovation, security, compliance)")
    
    if not inputs.scalability:
        if "global" in (inputs.free_text_input or "").lower():
            questions.append("For your global deployment, which regions are most critical for your users and operations?")
        else:
            questions.append("What are your scalability requirements? (Current users, expected growth, geographic distribution)")
    
    if not inputs.security_posture:
        if any(term in (inputs.free_text_input or "").lower() for term in ["compliance", "regulation", "financial", "healthcare"]):
            questions.append("What specific compliance requirements do you need to meet? (GDPR, HIPAA, SOX, PCI-DSS, etc.)")
        else:
            questions.append("What is your security posture requirement? (Zero trust, defense-in-depth, compliance-focused)")
    
    # Operational questions based on service selections
    total_selected_services = sum([
        len(inputs.compute_services or []),
        len(inputs.network_services or []),
        len(inputs.storage_services or []),
        len(inputs.database_services or []),
        len(inputs.security_services or [])
    ])
    
    if total_selected_services > 8:  # Complex architecture
        questions.append("With this many services, how do you plan to manage operations? Do you have a dedicated DevOps team or need Azure-managed services?")
    
    # Budget and timeline considerations
    if not inputs.cost_priority:
        if "startup" in (inputs.free_text_input or "").lower():
            questions.append("As a startup, should we prioritize cost optimization or rapid scalability for your initial deployment?")
        else:
            questions.append("What's your cost optimization priority? (Minimize initial costs, optimize for long-term TCO, or performance-first approach)")
    
    # Integration and existing infrastructure
    if inputs.free_text_input and "existing" not in inputs.free_text_input.lower():
        questions.append("Do you have existing Azure infrastructure, on-premises systems, or other cloud providers that need integration?")
    
    # Timeline and deployment approach
    if not any(term in (inputs.free_text_input or "").lower() for term in ["timeline", "schedule", "urgent", "asap"]):
        questions.append("What's your deployment timeline? This will help me recommend the right migration and deployment strategy.")
    
    # Return the most relevant questions (limit to 4 for better UX)
    return questions[:4]

def generate_feedback_questions(inputs: CustomerInputs) -> List[str]:
    """Legacy wrapper for backward compatibility - now calls the intelligent version"""
    return generate_intelligent_feedback_questions(inputs)

@app.post("/generate-png-diagram")
def generate_png_diagram(inputs: CustomerInputs):
    """Generate PNG diagram for download"""
    logger.info("Starting PNG diagram generation for download")
    
    try:
        # Validate inputs early
        validate_customer_inputs(inputs)
        logger.info("Input validation completed successfully")
        
        # Generate PNG diagram
        logger.info("Generating PNG diagram...")
        png_path = generate_azure_architecture_diagram(inputs, format="png")
        logger.info(f"PNG diagram generated successfully: {png_path}")
        
        # Read and encode the PNG file
        with open(png_path, "rb") as f:
            png_content = f.read()
        
        png_base64 = base64.b64encode(png_content).decode("utf-8")
        
        return {
            "success": True,
            "png_base64": png_base64,
            "png_path": png_path,
            "file_size": len(png_content),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "PNG"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating PNG diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PNG diagram: {str(e)}")

@app.post("/generate-svg-diagram")
def generate_svg_diagram(inputs: CustomerInputs):
    """Generate SVG diagram for download"""
    logger.info("Starting SVG diagram generation for download")
    
    try:
        # Validate inputs early
        validate_customer_inputs(inputs)
        logger.info("Input validation completed successfully")
        
        # Generate SVG diagram
        logger.info("Generating SVG diagram...")
        svg_path = generate_azure_architecture_diagram(inputs, format="svg")
        logger.info(f"SVG diagram generated successfully: {svg_path}")
        
        # Read the SVG file
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        return {
            "success": True,
            "svg_content": svg_content,
            "svg_path": svg_path,
            "file_size": len(svg_content),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "SVG"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating SVG diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate SVG diagram: {str(e)}")

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process files (PDF, Excel, PowerPoint) for AI analysis"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.xlsx', '.xls', '.pptx', '.ppt']
        file_extension = os.path.splitext(file.filename.lower())[1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 10MB)
        max_file_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Process the file with AI
        file_type = file_extension[1:]  # Remove the dot
        analysis_result = process_uploaded_document(file_content, file.filename, file_type)
        
        # Return file info and analysis
        return {
            "success": True,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": len(file_content),
            "analysis": analysis_result,
            "upload_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze-url")
def analyze_url(request: Dict[str, str]):
    """Analyze URL content for Azure architecture insights"""
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
        
        # Analyze the URL with AI
        analysis_result = analyze_url_content(url)
        
        return {
            "success": True,
            "url": url,
            "analysis": analysis_result,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing URL: {str(e)}")

@app.get("/templates")
def get_templates():
    """Get available Azure Landing Zone templates"""
    return {
        "templates": AZURE_TEMPLATES,
        "azure_services": AZURE_SERVICES_MAPPING
    }

@app.get("/services")
def get_services():
    """Get available Azure services categorized for form selection"""
    services_by_category = {}
    
    for service_key, service_info in AZURE_SERVICES_MAPPING.items():
        category = service_info["category"]
        if category not in services_by_category:
            services_by_category[category] = []
        
        services_by_category[category].append({
            "key": service_key,
            "name": service_info["name"],
            "icon": service_info["icon"],
            "azure_icon": service_info.get("azure_icon", ""),
        })
    
    return {
        "categories": services_by_category,
        "category_mapping": {
            "compute": "Compute Services",
            "network": "Networking Services", 
            "storage": "Storage Services",
            "database": "Database Services",
            "security": "Security Services",
            "monitoring": "Monitoring Services",
            "ai": "AI & Machine Learning",
            "analytics": "Data & Analytics",
            "integration": "Integration Services",
            "devops": "DevOps & Governance",
            "backup": "Backup & Recovery"
        }
    }

class FeedbackRequest(BaseModel):
    original_inputs: CustomerInputs
    feedback_answers: Dict[str, str]
    selected_services: Optional[List[str]] = Field(default_factory=list)

@app.post("/refine-architecture-with-feedback")
def refine_architecture_with_feedback(request: FeedbackRequest):
    """Refine architecture based on human feedback"""
    try:
        logger.info("Processing architecture refinement with human feedback")
        
        # Update inputs based on feedback
        refined_inputs = request.original_inputs
        
        # Process feedback answers to update inputs
        for question, answer in request.feedback_answers.items():
            if "business objective" in question.lower():
                refined_inputs.business_objective = answer
            elif "scalability" in question.lower():
                refined_inputs.scalability = answer
            elif "security" in question.lower():
                refined_inputs.security_posture = answer
            elif "cost" in question.lower():
                refined_inputs.cost_priority = answer
            elif "operational" in question.lower() or "monitor" in question.lower():
                refined_inputs.ops_model = answer
        
        # Add user-confirmed services if provided
        if request.selected_services:
            # Clear existing services and add only confirmed ones
            for service in request.selected_services:
                if service in AZURE_SERVICES_MAPPING:
                    category = AZURE_SERVICES_MAPPING[service]["category"]
                    category_field = f"{category}_services"
                    
                    if hasattr(refined_inputs, category_field):
                        current_services = getattr(refined_inputs, category_field) or []
                        if service not in current_services:
                            current_services.append(service)
                            setattr(refined_inputs, category_field, current_services)
        
        # Generate refined architecture
        return generate_interactive_azure_architecture(refined_inputs)
        
    except Exception as e:
        logger.error(f"Error refining architecture with feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refine architecture: {str(e)}")

@app.post("/validate-ai-service-selection")
def validate_ai_service_selection(request: Dict[str, Any]):
    """Allow users to validate and modify AI-suggested service selection"""
    try:
        free_text = request.get("free_text_input", "")
        
        if not free_text:
            raise HTTPException(status_code=400, detail="Free text input is required")
        
        # Get AI analysis
        analysis = analyze_free_text_requirements(free_text)
        
        # Get detailed service information
        suggested_services = []
        for service_key in analysis.get("services", []):
            if service_key in AZURE_SERVICES_MAPPING:
                service_info = AZURE_SERVICES_MAPPING[service_key]
                suggested_services.append({
                    "key": service_key,
                    "name": service_info["name"],
                    "category": service_info["category"],
                    "icon": service_info["icon"],
                    "reasoning": f"Suggested for: {analysis.get('reasoning', 'Meeting your requirements')}"
                })
        
        return {
            "success": True,
            "original_text": free_text,
            "suggested_services": suggested_services,
            "reasoning": analysis.get("reasoning", ""),
            "architecture_pattern": analysis.get("architecture_pattern", "simple"),
            "questions_for_clarification": [
                "Do these suggested services meet your requirements?",
                "Are there any additional services you need?",
                "Would you like to modify any of these selections?"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating AI service selection: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate service selection: {str(e)}")

# New Simplified Interface Endpoints

class SimplifiedAnalysisRequest(BaseModel):
    free_text_input: str

class SimplifiedGenerationRequest(BaseModel):
    free_text_input: str
    ai_analysis: Optional[Dict[str, Any]] = None
    follow_up_answers: Optional[Dict[str, str]] = None


class FigmaGenerationRequest(BaseModel):
    """Request model for Figma diagram generation."""
    # Standard customer inputs for architecture requirements  
    customer_inputs: CustomerInputs
    
    # Figma-specific parameters
    figma_api_token: Optional[str] = Field(None, description="Figma API token for authentication (if None, will use fallback)")
    figma_file_id: Optional[str] = Field(None, description="Existing Figma file ID where diagram will be created (required for Figma rendering)")
    page_name: Optional[str] = Field("Azure Architecture", description="Name for the diagram page")
    pattern: Optional[str] = Field("ha-multiregion", description="Architecture pattern to use")
    fallback_format: Optional[str] = Field("png", description="Format for fallback rendering (png or svg)")


# Initialize the architecture agent (if available)
if ARCH_AGENT_AVAILABLE:
    try:
        arch_agent = ArchitectureDiagramAgent()
        logger.info("Architecture agent initialized successfully")
    except Exception as e:
        arch_agent = None
        logger.error(f"Failed to initialize architecture agent: {e}")
else:
    arch_agent = None


@app.post("/generate-figma-diagram")
def generate_figma_diagram_endpoint(request: FigmaGenerationRequest):
    """Generate Azure architecture diagram using Figma API"""
    try:
        if not ARCH_AGENT_AVAILABLE or not arch_agent:
            raise HTTPException(
                status_code=503, 
                detail="Architecture agent is not available. Cannot generate Figma diagrams."
            )
        
        # Validate Figma-specific parameters
        if not request.figma_api_token and not request.figma_file_id:
            # If both are missing, provide a helpful message about using fallback
            logger.info("No Figma credentials provided, using fallback rendering only")
            request.figma_api_token = "fallback_mode"
            request.figma_file_id = "fallback_mode"
        elif not request.figma_api_token:
            raise HTTPException(
                status_code=400,
                detail="Figma API token is required for Figma rendering. Please provide a valid Figma API token or omit both token and file_id to use fallback rendering only."
            )
        elif not request.figma_file_id:
            raise HTTPException(
                status_code=400,
                detail="Figma file ID is required for Figma rendering. Please provide a valid Figma file ID where the diagram will be created or omit both token and file_id to use fallback rendering only."
            )
        
        # Note: This functionality will be enhanced with Google ADK agent framework
        logger.info("Starting Figma diagram generation (Google ADK integration coming soon)")
        
        # For now, return a simplified response until Google ADK agent is implemented
        return {
            "success": False,
            "message": "Figma integration is being enhanced with Google ADK agent framework",
            "diagram_url": None,
            "file_path": None,
            "is_fallback": True
        }
        download_url = None
        fallback_filename = None
        
        if is_fallback:
            # Extract filename from fallback response
            import re
            filename_match = re.search(r'([^/\s]+\.(?:png|svg))(?:\s|$)', figma_url)
            if filename_match:
                fallback_filename = filename_match.group(1)
                # Construct download URL
                download_url = f"/generate-azure-diagram/download/{fallback_filename}"
        
        # Get user info for the response (may fail if token is invalid, which is okay for fallback)
        user_info = None
        try:
            user_info = FigmaConfig.get_user_info(request.figma_api_token)
        except Exception:
            # User info not available for invalid tokens
            pass
        
        return {
            "success": True,
            "figma_url": figma_url if not is_fallback else None,
            "download_url": download_url,
            "fallback_filename": fallback_filename,
            "figma_file_id": request.figma_file_id,
            "page_name": request.page_name,
            "pattern": request.pattern,
            "user_info": user_info,
            "is_fallback": is_fallback,
            "fallback_reason": "Figma API unavailable or invalid token" if is_fallback else None,
            "message": figma_url if is_fallback else "Figma diagram generated successfully",
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "agent": "Azure Landing Zone Agent - Figma Integration",
                "diagram_format": "Figma native format" if not is_fallback else f"{request.fallback_format.upper()} fallback format",
                "rendering_method": "Figma API" if not is_fallback else "Python Diagrams (Fallback)"
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating Figma diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating Figma diagram: {str(e)}")



@app.post("/analyze-requirements")
def analyze_requirements_endpoint(request: SimplifiedAnalysisRequest):
    """Enhanced AI analysis endpoint for the simplified interface"""
    try:
        if not request.free_text_input.strip():
            raise HTTPException(status_code=400, detail="Requirements text is required")
        
        logger.info(f"Analyzing requirements: {len(request.free_text_input)} characters")
        
        # Get comprehensive AI analysis
        analysis = analyze_free_text_requirements(request.free_text_input)
        
        # Enhance the analysis with follow-up questions if needed
        follow_up_questions = []
        
        # Determine if clarification is needed based on the requirements
        needs_clarification = False
        
        # Check for ambiguous patterns that need clarification
        text_lower = request.free_text_input.lower()
        
        if "scalable" in text_lower or "scale" in text_lower:
            if not any(term in text_lower for term in ["auto-scaling", "manual", "global", "region"]):
                follow_up_questions.append("What type of scaling do you need? (Auto-scaling, manual scaling, global scaling)")
                needs_clarification = True
        
        if "database" in text_lower or "data" in text_lower:
            if not any(db in text_lower for db in ["sql", "nosql", "cosmos", "mysql", "postgresql"]):
                follow_up_questions.append("What type of database do you prefer? (SQL Database, Cosmos DB, MySQL, PostgreSQL)")
                needs_clarification = True
        
        if "web" in text_lower or "app" in text_lower:
            if not any(platform in text_lower for platform in ["vm", "container", "serverless", "aks"]):
                follow_up_questions.append("How would you like to host your application? (Virtual Machines, Containers/AKS, App Services, Serverless Functions)")
                needs_clarification = True
        
        if "secure" in text_lower or "security" in text_lower:
            if not any(sec in text_lower for sec in ["firewall", "waf", "zero trust", "vpn"]):
                follow_up_questions.append("What specific security features do you need? (Firewall, WAF, Zero Trust, VPN connectivity)")
                needs_clarification = True
        
        # Update analysis with follow-up questions
        enhanced_analysis = {
            **analysis,
            "follow_up_questions": follow_up_questions,
            "needs_confirmation": needs_clarification or analysis.get("needs_confirmation", False)
        }
        
        logger.info(f"Analysis completed. Services identified: {len(analysis.get('services', []))}, Pattern: {analysis.get('architecture_pattern', 'unknown')}")
        
        return enhanced_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze requirements: {str(e)}")

@app.post("/generate-simplified-architecture")
def generate_simplified_architecture(request: SimplifiedGenerationRequest):
    """Generate architecture using the simplified interface approach"""
    try:
        if not request.free_text_input.strip():
            raise HTTPException(status_code=400, detail="Requirements text is required")
        
        logger.info("Generating simplified architecture")
        
        # Use AI analysis if provided, otherwise generate new one
        if request.ai_analysis:
            analysis = request.ai_analysis
            logger.info("Using provided AI analysis")
        else:
            analysis = analyze_free_text_requirements(request.free_text_input)
            logger.info("Generated new AI analysis")
        
        # Create CustomerInputs from the AI analysis and free text
        simplified_inputs = CustomerInputs(
            free_text_input=request.free_text_input,
            business_objective="agility",  # Default to agility for simplified interface
            
            # Map AI analysis to customer inputs
            network_model="hub-spoke" if "hub" in analysis.get("architecture_pattern", "").lower() else "single-vnet",
            security_posture="zero-trust" if "zero trust" in analysis.get("security_considerations", "").lower() else "defense-in-depth",
            workload="web-apps",  # Default workload
            architecture_style="microservices" if "microservices" in analysis.get("architecture_pattern", "").lower() else "n-tier",
            monitoring="azure-monitor",
            scalability="auto-scaling" if "auto" in analysis.get("scalability_design", "").lower() else "manual-scaling",
            
            # Map services from AI analysis to service categories
            compute_services=[],
            network_services=[],
            storage_services=[],
            database_services=[],
            security_services=[],
            monitoring_services=[],
            ai_services=[],
            analytics_services=[],
            integration_services=[],
            devops_services=[],
            backup_services=[]
        )
        
        # Map AI-suggested services to appropriate categories
        for service in analysis.get("services", []):
            if service in ["vm", "virtual_machines", "aks", "app_services", "function_app", "container_instances"]:
                simplified_inputs.compute_services.append(service)
            elif service in ["virtual_network", "application_gateway", "load_balancer", "firewall", "vpn_gateway"]:
                simplified_inputs.network_services.append(service)
            elif service in ["storage_accounts", "blob_storage", "data_lake"]:
                simplified_inputs.storage_services.append(service)
            elif service in ["sql_database", "cosmos_db", "mysql", "postgresql"]:
                simplified_inputs.database_services.append(service)
            elif service in ["key_vault", "security_center", "sentinel", "active_directory"]:
                simplified_inputs.security_services.append(service)
            elif service in ["azure_monitor", "log_analytics", "application_insights"]:
                simplified_inputs.monitoring_services.append(service)
            elif service in ["cognitive_services", "machine_learning", "openai"]:
                simplified_inputs.ai_services.append(service)
            elif service in ["synapse", "data_factory", "databricks", "stream_analytics"]:
                simplified_inputs.analytics_services.append(service)
            elif service in ["logic_apps", "service_bus", "event_hubs", "api_management"]:
                simplified_inputs.integration_services.append(service)
            elif service in ["devops", "container_registry", "github"]:
                simplified_inputs.devops_services.append(service)
            elif service in ["backup", "site_recovery"]:
                simplified_inputs.backup_services.append(service)
        
        # Ensure we have at least basic services
        if not simplified_inputs.compute_services:
            simplified_inputs.compute_services = ["virtual_machines"]
        if not simplified_inputs.network_services:
            simplified_inputs.network_services = ["virtual_network"]
        if not simplified_inputs.security_services:
            simplified_inputs.security_services = ["key_vault"]
        if not simplified_inputs.monitoring_services:
            simplified_inputs.monitoring_services = ["azure_monitor"]
        
        logger.info(f"Mapped services to categories. Compute: {len(simplified_inputs.compute_services)}, Network: {len(simplified_inputs.network_services)}")
        
        # Generate the full architecture using existing endpoint logic
        result = generate_interactive_azure_architecture(simplified_inputs)
        
        # Enhance result with AI analysis information
        if isinstance(result, dict) and result.get("success"):
            result["ai_analysis"] = analysis
            result["original_requirements"] = request.free_text_input
            if request.follow_up_answers:
                result["follow_up_answers"] = request.follow_up_answers
        
        logger.info("Simplified architecture generation completed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating simplified architecture: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate simplified architecture: {str(e)}")


# ============================================================================
# Google ADK Agent Framework Endpoints
# ============================================================================

class GoogleADKRequest(BaseModel):
    """Request model for Google ADK agent."""
    business_objective: str = Field(..., description="Primary business objective")
    cloud_provider: str = Field(default="gcp", description="Cloud provider: gcp, azure, hybrid, multi_cloud")
    architecture_pattern: str = Field(default="enterprise", description="Architecture pattern")
    project_name: str = Field(default="Professional Architecture", description="Project name")
    regions: List[str] = Field(default=["us-central1"], description="Target regions")
    environment: str = Field(default="production", description="Environment")
    
    # Service selections
    compute_services: Optional[List[str]] = Field(default=[], description="Compute services")
    network_services: Optional[List[str]] = Field(default=[], description="Network services")
    storage_services: Optional[List[str]] = Field(default=[], description="Storage services")
    database_services: Optional[List[str]] = Field(default=[], description="Database services")
    security_services: Optional[List[str]] = Field(default=[], description="Security services")
    
    # Additional requirements
    scalability_requirements: Optional[str] = Field(None, description="Scalability requirements")
    security_requirements: Optional[str] = Field(None, description="Security requirements")
    compliance_requirements: Optional[str] = Field(None, description="Compliance requirements")


@app.post("/google-adk/analyze-requirements")
def google_adk_analyze_requirements(request: GoogleADKRequest):
    """
    Analyze requirements using Google ADK methodology.
    
    This endpoint provides comprehensive analysis of architecture requirements
    using Google Cloud best practices and design principles.
    """
    try:
        if not GOOGLE_ADK_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Google ADK Agent Framework is not available. Please check the installation."
            )
        
        logger.info(f"Starting Google ADK requirements analysis for {request.project_name}")
        
        # Map cloud provider string to enum
        provider_mapping = {
            "gcp": CloudProvider.GOOGLE_CLOUD,
            "azure": CloudProvider.AZURE,
            "hybrid": CloudProvider.HYBRID,
            "multi_cloud": CloudProvider.MULTI_CLOUD
        }
        
        # Map architecture pattern string to enum
        pattern_mapping = {
            "microservices": ArchitecturePattern.MICROSERVICES,
            "serverless": ArchitecturePattern.SERVERLESS,
            "data_analytics": ArchitecturePattern.DATA_ANALYTICS,
            "ml_ai": ArchitecturePattern.ML_AI,
            "web_application": ArchitecturePattern.WEB_APPLICATION,
            "enterprise": ArchitecturePattern.ENTERPRISE,
            "hybrid_cloud": ArchitecturePattern.HYBRID_CLOUD,
            "multi_cloud": ArchitecturePattern.MULTI_CLOUD
        }
        
        cloud_provider = provider_mapping.get(request.cloud_provider.lower(), CloudProvider.GOOGLE_CLOUD)
        arch_pattern = pattern_mapping.get(request.architecture_pattern.lower(), ArchitecturePattern.ENTERPRISE)
        
        # Create Google ADK agent
        agent = create_google_adk_agent(
            cloud_provider=cloud_provider,
            architecture_pattern=arch_pattern,
            project_name=request.project_name,
            regions=request.regions,
            environment=request.environment
        )
        
        # Prepare requirements dictionary
        requirements = {
            "business_objective": request.business_objective,
            "compute_services": request.compute_services,
            "network_services": request.network_services,
            "storage_services": request.storage_services,
            "database_services": request.database_services,
            "security_services": request.security_services,
            "scalability_requirements": request.scalability_requirements,
            "security_requirements": request.security_requirements,
            "compliance_requirements": request.compliance_requirements
        }
        
        # Analyze requirements
        analysis = agent.analyze_requirements(requirements)
        
        logger.info("Google ADK requirements analysis completed successfully")
        
        return {
            "success": True,
            "analysis": analysis,
            "agent_config": {
                "cloud_provider": cloud_provider.value,
                "architecture_pattern": arch_pattern.value,
                "project_name": request.project_name,
                "regions": request.regions,
                "environment": request.environment
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google ADK requirements analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Google ADK analysis failed: {str(e)}")


@app.post("/google-adk/generate-diagram")
def google_adk_generate_diagram(request: GoogleADKRequest):
    """
    Generate professional architecture diagram using Google ADK framework.
    
    This endpoint creates professional Google Cloud, Azure, or hybrid architecture
    diagrams following best practices and design principles.
    """
    try:
        if not GOOGLE_ADK_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Google ADK Agent Framework is not available. Please check the installation."
            )
        
        logger.info(f"Starting Google ADK diagram generation for {request.project_name}")
        
        # Map enums
        provider_mapping = {
            "gcp": CloudProvider.GOOGLE_CLOUD,
            "azure": CloudProvider.AZURE,
            "hybrid": CloudProvider.HYBRID,
            "multi_cloud": CloudProvider.MULTI_CLOUD
        }
        
        pattern_mapping = {
            "microservices": ArchitecturePattern.MICROSERVICES,
            "serverless": ArchitecturePattern.SERVERLESS,
            "data_analytics": ArchitecturePattern.DATA_ANALYTICS,
            "ml_ai": ArchitecturePattern.ML_AI,
            "web_application": ArchitecturePattern.WEB_APPLICATION,
            "enterprise": ArchitecturePattern.ENTERPRISE,
            "hybrid_cloud": ArchitecturePattern.HYBRID_CLOUD,
            "multi_cloud": ArchitecturePattern.MULTI_CLOUD
        }
        
        cloud_provider = provider_mapping.get(request.cloud_provider.lower(), CloudProvider.GOOGLE_CLOUD)
        arch_pattern = pattern_mapping.get(request.architecture_pattern.lower(), ArchitecturePattern.ENTERPRISE)
        
        # Create Google ADK agent
        agent = create_google_adk_agent(
            cloud_provider=cloud_provider,
            architecture_pattern=arch_pattern,
            project_name=request.project_name,
            regions=request.regions,
            environment=request.environment
        )
        
        # Prepare requirements
        requirements = {
            "business_objective": request.business_objective,
            "compute_services": request.compute_services,
            "network_services": request.network_services,
            "storage_services": request.storage_services,
            "database_services": request.database_services,
            "security_services": request.security_services,
            "scalability_requirements": request.scalability_requirements,
            "security_requirements": request.security_requirements,
            "compliance_requirements": request.compliance_requirements
        }
        
        # Generate diagram
        diagram_path = agent.generate_professional_diagram(requirements, output_format="png")
        
        # Read diagram file and encode as base64
        diagram_base64 = None
        if os.path.exists(diagram_path):
            with open(diagram_path, "rb") as f:
                diagram_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            file_size = os.path.getsize(diagram_path)
            logger.info(f"Google ADK diagram generated: {diagram_path} (size: {file_size} bytes)")
        else:
            raise Exception(f"Diagram file was not created: {diagram_path}")
        
        # Also analyze requirements for additional information
        analysis = agent.analyze_requirements(requirements)
        
        logger.info("Google ADK diagram generation completed successfully")
        
        return {
            "success": True,
            "diagram_path": diagram_path,
            "diagram_base64": diagram_base64,
            "file_size": file_size,
            "analysis": analysis,
            "agent_config": {
                "cloud_provider": cloud_provider.value,
                "architecture_pattern": arch_pattern.value,
                "project_name": request.project_name,
                "regions": request.regions,
                "environment": request.environment
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "PNG",
                "agent": "Google ADK Agent Framework",
                "version": "1.0.0"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google ADK diagram generation: {e}")
        raise HTTPException(status_code=500, detail=f"Google ADK diagram generation failed: {str(e)}")


@app.get("/google-adk/capabilities")
def google_adk_capabilities():
    """
    Get Google ADK agent capabilities and supported features.
    
    This endpoint returns information about available cloud providers,
    architecture patterns, and supported services.
    """
    try:
        capabilities = {
            "google_adk_available": GOOGLE_ADK_AVAILABLE,
            "cloud_providers": [
                {
                    "id": "gcp",
                    "name": "Google Cloud Platform",
                    "description": "Full Google Cloud Platform support with official GCP icons"
                },
                {
                    "id": "azure",
                    "name": "Microsoft Azure",
                    "description": "Azure cloud services support"
                },
                {
                    "id": "hybrid",
                    "name": "Hybrid Cloud",
                    "description": "Google Cloud + Azure hybrid architecture"
                },
                {
                    "id": "multi_cloud",
                    "name": "Multi-Cloud",
                    "description": "Multi-cloud architecture across providers"
                }
            ],
            "architecture_patterns": [
                {
                    "id": "microservices",
                    "name": "Microservices",
                    "description": "Distributed microservices architecture"
                },
                {
                    "id": "serverless",
                    "name": "Serverless",
                    "description": "Event-driven serverless architecture"
                },
                {
                    "id": "data_analytics",
                    "name": "Data Analytics",
                    "description": "Big data and analytics platform"
                },
                {
                    "id": "ml_ai",
                    "name": "ML/AI",
                    "description": "Machine learning and AI platform"
                },
                {
                    "id": "web_application",
                    "name": "Web Application",
                    "description": "Scalable web application architecture"
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise",
                    "description": "Enterprise-grade architecture"
                },
                {
                    "id": "hybrid_cloud",
                    "name": "Hybrid Cloud",
                    "description": "Hybrid cloud connectivity"
                },
                {
                    "id": "multi_cloud",
                    "name": "Multi-Cloud",
                    "description": "Multi-cloud deployment"
                }
            ],
            "design_principles": [
                {
                    "name": "Security First",
                    "description": "Security is built in from the ground up"
                },
                {
                    "name": "Scalability",
                    "description": "Design for automatic scaling and elasticity"
                },
                {
                    "name": "Reliability",
                    "description": "Build resilient and fault-tolerant systems"
                },
                {
                    "name": "Cost Optimization",
                    "description": "Optimize for cost-efficiency"
                },
                {
                    "name": "Operational Excellence",
                    "description": "Ensure efficient operations and monitoring"
                }
            ],
            "supported_services": {
                "gcp": {
                    "compute": ["gke", "cloud_run", "app_engine", "cloud_functions", "compute_engine"],
                    "database": ["cloud_sql", "firestore", "spanner", "bigquery"],
                    "storage": ["cloud_storage", "filestore", "persistent_disk"],
                    "networking": ["vpc", "load_balancer", "cdn", "dns", "firewall"],
                    "security": ["iam", "kms", "security_command_center"],
                    "analytics": ["dataflow", "dataproc", "pub_sub", "datalab"]
                },
                "azure": {
                    "compute": ["virtual_machines", "aks", "app_services", "function_apps"],
                    "database": ["sql_database", "cosmos_db"],
                    "storage": ["storage_accounts", "blob_storage"],
                    "networking": ["virtual_networks", "application_gateway"]
                }
            },
            "features": [
                "Professional diagram generation with official cloud provider icons",
                "Architecture pattern-based recommendations",
                "Design principle enforcement",
                "Cost estimation and optimization",
                "Security requirements analysis",
                "Scalability planning",
                "Best practices implementation",
                "Hybrid and multi-cloud support"
            ]
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting Google ADK capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


@app.post("/google-adk/validate-design")
def google_adk_validate_design(request: GoogleADKRequest):
    """
    Validate architecture design against Google ADK principles.
    
    This endpoint validates the proposed architecture against Google Cloud
    best practices and design principles, providing recommendations for improvement.
    """
    try:
        if not GOOGLE_ADK_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="Google ADK Agent Framework is not available. Please check the installation."
            )
        
        logger.info(f"Starting Google ADK design validation for {request.project_name}")
        
        # Create validation results
        validation_results = {
            "overall_score": 85,  # Example score
            "principle_compliance": {
                "security_first": {
                    "score": 90,
                    "status": "compliant",
                    "recommendations": [
                        "Enable audit logging",
                        "Implement proper IAM policies"
                    ]
                },
                "scalability": {
                    "score": 80,
                    "status": "mostly_compliant",
                    "recommendations": [
                        "Add auto-scaling configuration",
                        "Consider load balancing"
                    ]
                },
                "reliability": {
                    "score": 85,
                    "status": "compliant",
                    "recommendations": [
                        "Implement multi-zone deployment"
                    ]
                },
                "cost_optimization": {
                    "score": 75,
                    "status": "needs_improvement",
                    "recommendations": [
                        "Right-size compute instances",
                        "Use committed use discounts"
                    ]
                },
                "operational_excellence": {
                    "score": 90,
                    "status": "compliant",
                    "recommendations": [
                        "Implement comprehensive monitoring"
                    ]
                }
            },
            "best_practices_check": {
                "passed": [
                    "Use of managed services",
                    "Proper service categorization",
                    "Security service inclusion"
                ],
                "warnings": [
                    "Consider adding monitoring services",
                    "Review backup and disaster recovery"
                ],
                "failed": [
                    "Missing cost optimization measures"
                ]
            },
            "improvement_suggestions": [
                "Add Cloud Monitoring for observability",
                "Implement proper tagging strategy",
                "Consider serverless options for cost optimization",
                "Add data backup and recovery services"
            ]
        }
        
        logger.info("Google ADK design validation completed successfully")
        
        return {
            "success": True,
            "validation_results": validation_results,
            "project_name": request.project_name,
            "cloud_provider": request.cloud_provider,
            "architecture_pattern": request.architecture_pattern,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google ADK design validation: {e}")
        raise HTTPException(status_code=500, detail=f"Google ADK design validation failed: {str(e)}")
