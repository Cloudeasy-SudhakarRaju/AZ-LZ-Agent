from fastapi import FastAPI, Response, HTTPException, UploadFile, File
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

# Import diagrams for Azure architecture generation
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import VM, AKS, AppServices, FunctionApps, ContainerInstances, ServiceFabricClusters, BatchAccounts
from diagrams.azure.network import VirtualNetworks, ApplicationGateway, LoadBalancers, Firewall, ExpressrouteCircuits, VirtualNetworkGateways
from diagrams.azure.storage import StorageAccounts, BlobStorage, DataLakeStorage
from diagrams.azure.database import SQLDatabases, CosmosDb, DatabaseForMysqlServers, DatabaseForPostgresqlServers
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open for dev, restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini API
GEMINI_API_KEY = "AIzaSyCuYYvGh5wjwNniv9ZQ1QC-5pxwdj5lCWQ"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
try:
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    logger.info("Google Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    gemini_model = None


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
    "firewall": {"name": "Azure Firewall", "icon": "🛡️", "drawio_shape": "firewall", "diagram_class": Firewall, "category": "network"},
    "waf": {"name": "Web Application Firewall", "icon": "🛡️", "drawio_shape": "application_gateway", "diagram_class": ApplicationGateway, "category": "network"},
    "cdn": {"name": "Content Delivery Network", "icon": "🌍", "drawio_shape": "cdn_profiles", "diagram_class": None, "category": "network"},
    "traffic_manager": {"name": "Traffic Manager", "icon": "🚦", "drawio_shape": "traffic_manager_profiles", "diagram_class": None, "category": "network"},
    "virtual_wan": {"name": "Virtual WAN", "icon": "🌐", "drawio_shape": "virtual_wan", "diagram_class": VirtualNetworks, "category": "network"},
    
    # Storage Services
    "storage_accounts": {"name": "Storage Accounts", "icon": "💾", "drawio_shape": "storage_accounts", "diagram_class": StorageAccounts, "category": "storage"},
    "blob_storage": {"name": "Blob Storage", "icon": "📄", "drawio_shape": "blob_storage", "diagram_class": BlobStorage, "category": "storage"},
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
    "redis_cache": {"name": "Azure Cache for Redis", "icon": "⚡", "drawio_shape": "cache_redis", "diagram_class": None, "category": "database"},
    
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

# Google Gemini AI Integration Functions
def analyze_url_content(url: str) -> str:
    """Fetch and analyze URL content using Gemini AI"""
    try:
        if not gemini_model:
            return "Gemini AI not available for URL analysis"
            
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
        
        result = gemini_model.generate_content(prompt)
        return result.text
        
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {e}")
        return f"Error analyzing URL: {str(e)}"

def process_uploaded_document(file_content: bytes, filename: str, file_type: str) -> str:
    """Process uploaded document using Gemini AI"""
    try:
        if not gemini_model:
            return "Gemini AI not available for document analysis"
            
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
        
        result = gemini_model.generate_content(prompt)
        return result.text
        
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
    """Generate AI-enhanced architecture recommendations using Gemini"""
    try:
        if not gemini_model:
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
        
        result = gemini_model.generate_content(prompt)
        return result.text
        
    except Exception as e:
        logger.error(f"Error generating AI recommendations: {e}")
        return f"Error generating AI recommendations: {str(e)}"

def analyze_free_text_requirements(free_text: str) -> dict:
    """Analyze free text input to extract comprehensive service requirements using AI"""
    try:
        if not gemini_model or not free_text:
            return {"services": [], "reasoning": "No analysis available"}
            
        prompt = """
        You are an ENTERPRISE AZURE SOLUTIONS ARCHITECT with deep expertise in designing production-ready, scalable, and secure Azure Landing Zone architectures. You have extensive experience with Azure Well-Architected Framework, Azure CAF (Cloud Adoption Framework), and enterprise-grade architectural patterns.

        User Requirement: "{}"

        ENTERPRISE ANALYSIS INSTRUCTIONS:
        
        1. COMPREHENSIVE BUSINESS ANALYSIS:
           - Analyze the business requirement to understand the complete technical and operational context
           - Consider enterprise-grade scalability, security, compliance, and governance needs
           - Think about future growth, disaster recovery, and business continuity requirements
           - Identify the appropriate Azure architectural pattern (e.g., N-tier, microservices, event-driven, etc.)

        2. INTELLIGENT SERVICE SELECTION:
           - Select ONLY services that are truly needed for the specific requirement
           - DO NOT include random or default services unless they are justified by the requirement
           - For each service selected, provide clear architectural reasoning
           - Consider service dependencies and integration patterns
           - Ensure services work together as a cohesive architectural solution

        3. ENTERPRISE ARCHITECTURE PATTERNS:
           - Apply proven enterprise patterns: Hub-and-Spoke networking, Microservices, Event-driven architecture
           - Consider cross-cutting concerns: Security, Monitoring, Logging, Backup, Disaster Recovery
           - Design for High Availability (99.9%+), Scalability, and Performance
           - Include appropriate governance and compliance services when needed

        4. CONNECTIVITY AND INTEGRATION:
           - Design proper service-to-service communication patterns
           - Consider network security groups, private endpoints, and secure communication
           - Plan for API management, service mesh, and integration patterns
           - Design proper data flow and processing pipelines

        5. SECURITY BY DESIGN:
           - Implement Zero Trust security model where appropriate
           - Consider identity and access management, data encryption, network security
           - Include security monitoring and threat detection capabilities
           - Plan for compliance requirements (GDPR, HIPAA, SOC 2, etc.)

        AVAILABLE AZURE SERVICES BY CATEGORY:
        
        Compute: virtual_machines, aks, app_services, functions, container_instances, service_fabric, batch
        Network: virtual_network, vpn_gateway, expressroute, load_balancer, application_gateway, firewall, waf, cdn, traffic_manager, virtual_wan
        Storage: storage_accounts, blob_storage, data_lake_storage, file_storage, disk_storage
        Database: sql_database, cosmos_db, mysql, postgresql, redis, synapse_dedicated_pools
        Security: key_vault, security_center, sentinel, azure_ad_b2c, azure_firewall, ddos_protection, active_directory
        Monitoring: azure_monitor, log_analytics, application_insights, azure_advisor
        Analytics: synapse_analytics, data_factory, databricks, stream_analytics, event_hubs, power_bi
        Integration: logic_apps, service_bus, event_grid, api_management
        DevOps: devops, pipelines, container_registry, azure_artifacts
        Backup: backup_vault, site_recovery, azure_backup

        RESPONSE FORMAT - Provide a DETAILED JSON response with:

        1. "services" - Array of Azure service keys that form a complete, enterprise-ready solution
        2. "reasoning" - Comprehensive architectural explanation (minimum 200 words) covering:
           - Why each service was selected and how it fits the architectural pattern
           - How services integrate and communicate with each other
           - Security, scalability, and operational considerations
           - Alternatives considered and why they were not chosen
           
        3. "architecture_pattern" - Detailed description of the overall architecture pattern and design principles
        4. "connectivity_requirements" - Specific connectivity patterns, network topology, and communication flows
        5. "security_considerations" - Comprehensive security architecture including identity, network, data, and application security
        6. "scalability_design" - How the architecture scales to meet demand
        7. "operational_excellence" - Monitoring, logging, automation, and maintenance considerations
        8. "cost_optimization" - Cost-effective design choices and optimization strategies
        9. "needs_confirmation" - Set to true if clarification is needed from the user
        10. "suggested_additions" - Additional services or patterns to consider for enhancement

        EXAMPLE FOR "I need a scalable e-commerce platform with microservices architecture":
        {{
          "services": ["aks", "application_gateway", "virtual_network", "cosmos_db", "redis", "service_bus", "api_management", "key_vault", "azure_monitor", "log_analytics", "application_insights", "storage_accounts", "cdn", "container_registry"],
          "reasoning": "Designed a comprehensive microservices-based e-commerce platform using Azure Kubernetes Service (AKS) as the container orchestration platform for scalable microservices. Application Gateway provides SSL termination, web application firewall, and load balancing across AKS nodes. Virtual Network ensures secure communication between services with network segmentation. Cosmos DB serves as the primary database for product catalog and user data with global distribution capabilities. Redis provides high-performance caching for session management and frequently accessed data. Service Bus enables reliable asynchronous communication between microservices. API Management provides centralized API gateway functionality with rate limiting, authentication, and API versioning. Key Vault securely manages secrets, certificates, and encryption keys. Comprehensive monitoring stack with Azure Monitor, Log Analytics, and Application Insights provides observability across the entire platform. Storage Accounts handle static assets and file uploads. CDN improves global performance for static content delivery. Container Registry stores and manages container images for the microservices.",
          "architecture_pattern": "Cloud-native microservices architecture with event-driven communication, implementing Domain-Driven Design principles with separate bounded contexts for user management, product catalog, order processing, and payment services",
          "connectivity_requirements": "Application Gateway -> AKS Ingress -> Microservices, Service Bus for async communication, API Management for external APIs, Private endpoints for databases, VNet integration for all services",
          "security_considerations": "Zero Trust network model with NSGs, private endpoints for data services, Key Vault integration for secrets, Application Gateway WAF for web protection, Azure AD integration for authentication, RBAC for authorization",
          "scalability_design": "Horizontal pod autoscaling in AKS, Cosmos DB auto-scaling, Redis clustering, Application Gateway auto-scaling, CDN for global content delivery",
          "operational_excellence": "Centralized logging with Log Analytics, distributed tracing with Application Insights, automated deployment with Container Registry and AKS, health checks and monitoring alerts",
          "cost_optimization": "AKS spot instances for non-critical workloads, Cosmos DB reserved capacity, appropriate storage tiers, CDN for reduced bandwidth costs",
          "needs_confirmation": false,
          "suggested_additions": ["Azure Front Door for global load balancing", "Azure DevOps for CI/CD pipeline", "Azure Backup for data protection"]
        }}

        CRITICAL REQUIREMENTS:
        - ONLY suggest services that are specifically needed for the stated requirement
        - Provide detailed architectural reasoning for every service selection
        - Ensure all services work together as an integrated solution
        - Consider enterprise-grade non-functional requirements (security, scalability, monitoring)
        - Return ONLY valid JSON format with no additional text

        """.format(free_text)
        
        result = gemini_model.generate_content(prompt)
        response_text = result.text.strip()
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Look for JSON content
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                analysis = json.loads(json_str)
                # Ensure backward compatibility by adding missing fields
                if "architecture_pattern" not in analysis:
                    analysis["architecture_pattern"] = "Custom architecture"
                if "connectivity_requirements" not in analysis:
                    analysis["connectivity_requirements"] = "Standard Azure networking"
                if "security_considerations" not in analysis:
                    analysis["security_considerations"] = "Standard security practices"
                if "scalability_design" not in analysis:
                    analysis["scalability_design"] = "Standard scalability patterns"
                if "operational_excellence" not in analysis:
                    analysis["operational_excellence"] = "Standard monitoring and operations"
                if "cost_optimization" not in analysis:
                    analysis["cost_optimization"] = "Standard cost optimization"
                if "needs_confirmation" not in analysis:
                    analysis["needs_confirmation"] = False
                if "suggested_additions" not in analysis:
                    analysis["suggested_additions"] = []
                return analysis
            except json.JSONDecodeError:
                pass
        
        # Fallback parsing if JSON parsing fails
        logger.warning(f"Failed to parse AI response as JSON: {response_text}")
        return {
            "services": [], 
            "reasoning": "Could not parse AI analysis",
            "architecture_pattern": "Unknown",
            "connectivity_requirements": "Not specified",
            "security_considerations": "Not specified",
            "scalability_design": "Not specified",
            "operational_excellence": "Not specified",
            "cost_optimization": "Not specified",
            "needs_confirmation": True,
            "suggested_additions": []
        }
        
    except Exception as e:
        logger.error(f"Error analyzing free text requirements: {e}")
        return {
            "services": [], 
            "reasoning": f"Analysis error: {str(e)}",
            "architecture_pattern": "Error",
            "connectivity_requirements": "Error",
            "security_considerations": "Error",
            "scalability_design": "Error",
            "operational_excellence": "Error",
            "cost_optimization": "Error",
            "needs_confirmation": True,
            "suggested_additions": []
        }

def validate_customer_inputs(inputs: CustomerInputs) -> None:
    """Validate customer inputs to prevent potential errors"""
    # Check for extremely long strings that might cause issues
    string_fields = [
        inputs.business_objective, inputs.regulatory, inputs.industry,
        inputs.org_structure, inputs.governance, inputs.identity,
        inputs.connectivity, inputs.network_model, inputs.ip_strategy,
        inputs.security_zone, inputs.security_posture, inputs.key_vault,
        inputs.threat_protection, inputs.workload, inputs.architecture_style,
        inputs.scalability, inputs.ops_model, inputs.monitoring, inputs.backup,
        inputs.topology_pattern, inputs.migration_scope, inputs.cost_priority, inputs.iac,
        inputs.url_input
    ]
    
    for field in string_fields:
        if field and len(field) > 1000:  # Reasonable limit for most fields
            raise ValueError(f"Input field too long: {len(field)} characters (max 1000)")
    
    # Special validation for free-text input (allowing more characters)
    if inputs.free_text_input and len(inputs.free_text_input) > 10000:
        raise ValueError(f"Free text input too long: {len(inputs.free_text_input)} characters (max 10000)")
    
    # Check service lists for reasonable sizes
    service_lists = [
        inputs.compute_services, inputs.network_services, inputs.storage_services,
        inputs.database_services, inputs.security_services, inputs.monitoring_services,
        inputs.ai_services, inputs.analytics_services, inputs.integration_services,
        inputs.devops_services, inputs.backup_services
    ]
    
    for service_list in service_lists:
        if service_list and len(service_list) > 50:  # Reasonable limit
            raise ValueError(f"Too many services selected: {len(service_list)} (max 50)")
    
    # Validate URL format if provided
    if inputs.url_input:
        if not inputs.url_input.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
    
    # Validate uploaded files info
    if inputs.uploaded_files_info:
        if len(inputs.uploaded_files_info) > 10:  # Reasonable limit
            raise ValueError(f"Too many uploaded files: {len(inputs.uploaded_files_info)} (max 10)")

def generate_azure_architecture_diagram(inputs: CustomerInputs, output_dir: str = None, format: str = "png") -> str:
    """Generate Azure architecture diagram using the Python Diagrams library with proper Azure icons"""
    
    logger.info("Starting Azure architecture diagram generation")
    
    try:
        # Validate inputs first
        validate_customer_inputs(inputs)
        logger.info("Input validation completed successfully")
        
        # Get safe output directory
        if output_dir is None:
            output_dir = get_safe_output_directory()
        
        # Clean up old files to prevent disk space issues
        cleanup_old_files(output_dir)
        
        # Verify Graphviz availability before proceeding
        try:
            result = subprocess.run(['dot', '-V'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception(f"Graphviz 'dot' command failed with return code {result.returncode}. stderr: {result.stderr}")
            logger.info(f"Graphviz version: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            raise Exception("Graphviz 'dot' command timed out. Graphviz may be unresponsive.")
        except FileNotFoundError:
            raise Exception("Graphviz is not installed or not accessible. Please install Graphviz: sudo apt-get install -y graphviz graphviz-dev")
        except subprocess.SubprocessError as e:
            raise Exception(f"Graphviz check failed: {str(e)}. Please install Graphviz: sudo apt-get install -y graphviz graphviz-dev")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for uniqueness
        filename = f"azure_landing_zone_{timestamp}_{unique_id}"
        filepath = os.path.join(output_dir, filename)
        
        logger.info(f"Generating diagram with filename: {filename}")
        
        # Verify output directory is writable
        if not os.access(output_dir, os.W_OK):
            raise Exception(f"Output directory {output_dir} is not writable")
        
        # Determine organization template
        template = generate_architecture_template(inputs)
        org_name = inputs.org_structure or "Enterprise"
        
        logger.info(f"Using template: {template['template']['name']}")
        
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
                    "margin": "0.5"
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
                
                logger.info("Creating diagram structure...")
                
                # Only create management groups if governance services are explicitly selected
                created_resources = []
                
                # Identity and Security Services - ONLY if explicitly selected or AI recommended
                identity_resources = []
                if (inputs.security_services and ("active_directory" in inputs.security_services or "key_vault" in inputs.security_services)) or \
                   (template.get("ai_services") and any(service in ["active_directory", "key_vault"] for service in template["ai_services"])):
                    
                    with Cluster("Identity & Security", graph_attr={"bgcolor": "#e8f4f8", "style": "rounded"}):
                        if (inputs.security_services and "active_directory" in inputs.security_services) or \
                           (template.get("ai_services") and "active_directory" in template["ai_services"]):
                            aad = ActiveDirectory("Azure Active Directory")
                            identity_resources.append(aad)
                            created_resources.append(aad)
                            
                        if (inputs.security_services and "key_vault" in inputs.security_services) or \
                           (template.get("ai_services") and "key_vault" in template["ai_services"]):
                            key_vault = KeyVaults("Key Vault")
                            identity_resources.append(key_vault)
                            created_resources.append(key_vault)
                            
                        if inputs.security_services and "security_center" in inputs.security_services:
                            sec_center = SecurityCenter("Security Center")
                            identity_resources.append(sec_center)
                            created_resources.append(sec_center)
                            
                        if inputs.security_services and "sentinel" in inputs.security_services:
                            sentinel = Sentinel("Sentinel")
                            identity_resources.append(sentinel)
                            created_resources.append(sentinel)
                
                # Azure Subscription - ONLY if we actually have services to put in it
                subscription = None
                total_services = sum([
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
                    len(inputs.backup_services or []),
                    len(template.get("ai_services", []))
                ])
                
                if total_services > 0:
                    with Cluster("Azure Subscription", graph_attr={"bgcolor": "#f0f8ff", "style": "rounded"}):
                        subscription = Subscriptions("Azure Subscription")
                        created_resources.append(subscription)
                
                # Create network services only if explicitly selected
                network_resources_by_type = {}
                if inputs.network_services:
                    with Cluster("Network Architecture", graph_attr={"bgcolor": "#f0fff0", "style": "rounded"}):
                        network_resources = []
                        for service in inputs.network_services:
                            if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["diagram_class"]:
                                diagram_class = AZURE_SERVICES_MAPPING[service]["diagram_class"]
                                service_name = AZURE_SERVICES_MAPPING[service]["name"]
                                network_resource = diagram_class(service_name)
                                network_resources.append(network_resource)
                                created_resources.append(network_resource)
                                
                                # Track network resources by type
                                if service not in network_resources_by_type:
                                    network_resources_by_type[service] = []
                                network_resources_by_type[service].append(network_resource)
                        
                        # Intelligent network connections based on Azure patterns
                        _add_intelligent_network_connections(network_resources, network_resources_by_type)
                
                # Create other service clusters and get resource tracking
                all_resources, resources_by_type = _add_selected_service_clusters(inputs, created_resources)
                
                # Merge network resources into the overall tracking
                resources_by_type.update(network_resources_by_type)
                
                # Add intelligent connections between all services
                _add_intelligent_service_connections(inputs, resources_by_type, template)
                
                # If no services are selected at all, create a placeholder message
                if len(all_resources) == 0:
                    from diagrams.generic.blank import Blank
                    placeholder = Blank("No Services Selected\n\nPlease specify Azure services\nto generate architecture")
                    all_resources.append(placeholder)
                
                logger.info("Diagram structure and intelligent connections created successfully")
        
        except Exception as e:
            logger.error(f"Error during diagram creation: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Error generating Azure architecture diagram: {str(e)}")
        
        # Return the file path of the generated diagram
        if format.lower() == "svg":
            # Check for SVG file generated directly by diagrams library
            svg_path = f"{filepath}.svg"
            if os.path.exists(svg_path):
                file_size = os.path.getsize(svg_path)
                logger.info(f"SVG diagram generated successfully: {svg_path} (size: {file_size} bytes)")
                return svg_path
            else:
                # Fallback: try to generate SVG using dot command from gv file
                dot_path = f"{filepath}.gv" 
                if os.path.exists(dot_path):
                    try:
                        # Convert dot file to SVG
                        result = subprocess.run(['dot', '-Tsvg', dot_path, '-o', svg_path], 
                                              capture_output=True, text=True, timeout=30)
                        if result.returncode != 0:
                            raise Exception(f"SVG generation failed: {result.stderr}")
                        
                        if os.path.exists(svg_path):
                            file_size = os.path.getsize(svg_path)
                            logger.info(f"SVG diagram generated successfully via dot: {svg_path} (size: {file_size} bytes)")
                            return svg_path
                        else:
                            raise Exception(f"SVG generation failed - file not found: {svg_path}")
                    except subprocess.TimeoutExpired:
                        raise Exception("SVG generation timed out")
                    except Exception as e:
                        raise Exception(f"Failed to generate SVG: {str(e)}")
                else:
                    raise Exception(f"Neither SVG nor dot file found: {svg_path}, {dot_path}")
        else:
            # Default PNG generation
            png_path = f"{filepath}.png"
            if os.path.exists(png_path):
                file_size = os.path.getsize(png_path)
                logger.info(f"Diagram generated successfully: {png_path} (size: {file_size} bytes)")
                return png_path
            else:
                raise Exception(f"Diagram generation failed - PNG file not found: {png_path}")
            
    except Exception as e:
        logger.error(f"Failed to generate Azure architecture diagram: {str(e)}")
        logger.error(traceback.format_exc())
        raise

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
        
        # Compute Services - only if explicitly selected
        if inputs.compute_services:
            with Cluster("Compute Services", graph_attr={"bgcolor": "#fff8dc", "style": "rounded"}):
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
        
        # Storage Services - only if explicitly selected  
        if inputs.storage_services:
            with Cluster("Storage Services", graph_attr={"bgcolor": "#f5f5dc", "style": "rounded"}):
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
        
        # Database Services - only if explicitly selected
        if inputs.database_services:
            with Cluster("Database Services", graph_attr={"bgcolor": "#e6f3ff", "style": "rounded"}):
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
        
        # Monitoring Services - only if explicitly selected
        if inputs.monitoring_services:
            with Cluster("Monitoring Services", graph_attr={"bgcolor": "#f0f8ff", "style": "rounded"}):
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

def generate_professional_mermaid(inputs: CustomerInputs) -> str:
    """Generate minimal Mermaid diagram for Azure Landing Zone based only on selected services"""
    
    template = generate_architecture_template(inputs)
    
    lines = [
        "graph TB",
        "    subgraph \"Azure Architecture\"",
    ]
    
    # Check if we have any services selected (including AI suggested ones)
    ai_services = template.get("ai_services", [])
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
        len(inputs.backup_services or []),
        len(ai_services)
    ])
    
    # Only add structure if we have services
    if total_selected_services > 0:
        lines.extend([
            "        SUBSCRIPTION[\"📦 Azure Subscription\"]"
        ])
        
        # Add Resource Group only if we have resources
        lines.extend([
            "        RESOURCEGROUP[\"📁 Resource Group\"]",
            "        SUBSCRIPTION --> RESOURCEGROUP"
        ])
        
        service_count = 0
        
        # Add compute services if selected
        if inputs.compute_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "compute" for service in ai_services)):
            lines.extend([
                "        subgraph \"Compute Services\""
            ])
            
            service_connections = []
            # Add explicitly selected compute services
            for service in (inputs.compute_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"COMPUTE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested compute services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "compute":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"COMPUTE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
        
        # Add network services if selected
        if inputs.network_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "network" for service in ai_services)):
            lines.extend([
                "        subgraph \"Network Services\""
            ])
            
            service_connections = []
            # Add explicitly selected network services
            for service in (inputs.network_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"NETWORK{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested network services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "network":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"NETWORK{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
        
        # Add storage services if selected
        if inputs.storage_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "storage" for service in ai_services)):
            lines.extend([
                "        subgraph \"Storage Services\""
            ])
            
            service_connections = []
            # Add explicitly selected storage services
            for service in (inputs.storage_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"STORAGE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested storage services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "storage":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"STORAGE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
        
        # Add database services if selected
        if inputs.database_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "database" for service in ai_services)):
            lines.extend([
                "        subgraph \"Database Services\""
            ])
            
            service_connections = []
            # Add explicitly selected database services
            for service in (inputs.database_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"DATABASE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested database services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "database":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"DATABASE{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
        
        # Add security services if selected
        if inputs.security_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "security" for service in ai_services)):
            lines.extend([
                "        subgraph \"Security Services\""
            ])
            
            service_connections = []
            # Add explicitly selected security services
            for service in (inputs.security_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"SECURITY{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested security services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "security":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"SECURITY{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
        
        # Add monitoring services if selected
        if inputs.monitoring_services or (ai_services and any(service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "monitoring" for service in ai_services)):
            lines.extend([
                "        subgraph \"Monitoring Services\""
            ])
            
            service_connections = []
            # Add explicitly selected monitoring services
            for service in (inputs.monitoring_services or []):
                if service in AZURE_SERVICES_MAPPING:
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"MONITORING{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            # Add AI-suggested monitoring services
            for service in ai_services:
                if service in AZURE_SERVICES_MAPPING and AZURE_SERVICES_MAPPING[service]["category"] == "monitoring":
                    service_info = AZURE_SERVICES_MAPPING[service]
                    service_id = f"MONITORING{service_count}"
                    lines.append(f"            {service_id}[\"{service_info['icon']} {service_info['name']}\"]")
                    service_connections.append(f"            RESOURCEGROUP --> {service_id}")
                    service_count += 1
            
            lines.extend(service_connections)
            lines.append("        end")
    
    else:
        # If no services selected, show minimal placeholder
        lines.extend([
            "        PLACEHOLDER[\"📝 No Services Selected\"]",
            "        PLACEHOLDER2[\"ℹ️ Please select Azure services to generate architecture\"]"
        ])
    
    lines.append("    end")
    
    # Add styling
    lines.extend([
        "",
        "    classDef subscription fill:#e1f5fe,stroke:#01579b,stroke-width:2px;",
        "    classDef resourceGroup fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;",
        "    classDef compute fill:#fff3e0,stroke:#e65100,stroke-width:2px;",
        "    classDef network fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px;",
        "    classDef storage fill:#fce4ec,stroke:#880e4f,stroke-width:2px;",
        "    classDef database fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px;",
        "    classDef security fill:#ffebee,stroke:#b71c1c,stroke-width:2px;",
        "    classDef monitoring fill:#f1f8e9,stroke:#33691e,stroke-width:2px;",
        "",
        "    class SUBSCRIPTION subscription;",
        "    class RESOURCEGROUP resourceGroup;"
    ])
    
    return "\n".join(lines)

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
    """Generate professional TSD, HLD, and LLD documentation with comprehensive AI enhancement"""
    
    template = generate_architecture_template(inputs)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Generate AI insights if additional inputs are provided
    url_analysis = ""
    doc_analysis = ""
    ai_recommendations = ""
    
    # Get AI analysis results
    architecture_pattern = template.get("architecture_pattern", "Custom Architecture")
    connectivity_requirements = template.get("connectivity_requirements", "Standard Azure networking")
    security_considerations = template.get("security_considerations", "Standard security practices")
    ai_reasoning = template.get("ai_reasoning", "Standard architectural decisions applied")
    
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
    
    # Technical Specification Document (TSD) - Enhanced
    tsd = f"""# Technical Specification Document (TSD)
## Azure Landing Zone Architecture - Enterprise Edition

**Document Version:** 3.0 (AI-Enhanced with Intelligent Connectivity)
**Date:** {timestamp}
**Business Objective:** {inputs.business_objective or 'Enterprise cloud transformation with optimal connectivity'}

### Executive Summary
This document outlines the technical specifications for implementing an enterprise-ready Azure Landing Zone architecture based on comprehensive AI-powered analysis of customer requirements, including intelligent service connectivity and architectural patterns.

### AI-Powered Architecture Analysis
**Architecture Pattern Identified:** {architecture_pattern}

**Architectural Reasoning:**
{ai_reasoning}

**Connectivity Requirements:**
{connectivity_requirements}

**Security Considerations:**
{security_considerations}

### Business Requirements Analysis
- **Primary Objective:** {inputs.business_objective or 'Cost optimization and operational efficiency with enterprise-grade reliability'}
- **Industry:** {inputs.industry or 'Multi-industry applicable'}
- **Regulatory Requirements:** {inputs.regulatory or 'Standard compliance with data protection'}
- **Organization Structure:** {inputs.org_structure or 'Enterprise with distributed teams'}
- **Governance Model:** {inputs.governance or 'Centralized with delegated permissions and policy enforcement'}

### Architecture Template Selection
**Selected Template:** {template['template']['name']}
**Justification:** Based on organizational size, complexity, regulatory requirements, and AI analysis of requirements.

### Service Architecture & Connectivity
#### Selected Azure Services
**Compute Services:** {', '.join(inputs.compute_services) if inputs.compute_services else 'None explicitly selected'}
**Network Services:** {', '.join(inputs.network_services) if inputs.network_services else 'None explicitly selected'}
**Database Services:** {', '.join(inputs.database_services) if inputs.database_services else 'None explicitly selected'}
**Security Services:** {', '.join(inputs.security_services) if inputs.security_services else 'Standard security baseline'}
**Analytics Services:** {', '.join(inputs.analytics_services) if inputs.analytics_services else 'None explicitly selected'}
**Integration Services:** {', '.join(inputs.integration_services) if inputs.integration_services else 'None explicitly selected'}

#### Service Connectivity Patterns
The architecture implements intelligent connectivity patterns based on Azure best practices:

1. **Web Tier Connectivity:** Application Gateway → App Services/VMs with load balancing
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

    # High Level Design (HLD) - Enhanced
    hld = f"""# High Level Design (HLD)
## Azure Landing Zone Implementation with Intelligent Connectivity

**Document Version:** 2.0 (AI-Enhanced)
**Date:** {timestamp}
**Architecture Pattern:** {architecture_pattern}

### Architecture Overview
The proposed Azure Landing Zone follows the {template['template']['name']} pattern with intelligent service connectivity and enterprise-grade security.

### AI-Driven Service Selection
The following services were selected based on comprehensive analysis:
- **AI Reasoning:** {ai_reasoning[:500]}...
- **Connectivity Pattern:** {connectivity_requirements[:300]}...
- **Security Model:** {security_considerations[:300]}...

### Management Group Structure"""
    
    for mg in template['template']['management_groups']:
        hld += f"- **{mg}:** Management group for {mg.lower()} resources with policy enforcement\n"
    
    hld += f"""
### Subscription Strategy"""
    
    for sub in template['template']['subscriptions']:
        hld += f"- **{sub}:** Dedicated subscription for {sub.lower()} workloads with cost management\n"
    
    hld += f"""
### Network Architecture with Intelligent Connectivity
**Topology:** {inputs.network_model or 'Hub-Spoke with intelligent routing'}
- **Hub VNet:** Central connectivity hub with shared services and security controls
- **Spoke VNets:** Workload-specific virtual networks with micro-segmentation
- **Connectivity:** {inputs.connectivity or 'Hybrid connectivity with ExpressRoute and VPN Gateway'}
- **Traffic Flow:** Intelligent traffic routing with Application Gateway and Load Balancers
- **Security Zones:** Network segmentation with Azure Firewall and NSGs

### Service Connectivity Architecture
#### Web Tier Connectivity
- Application Gateway provides SSL termination and web application firewall
- Load balancers distribute traffic to compute services
- CDN integration for global content delivery

#### Data Tier Security
- Secure connections from compute services to databases
- Private endpoints for secure database access
- Key Vault integration for connection string management

#### Monitoring & Observability
- Azure Monitor collects telemetry from all services
- Application Insights provides application performance monitoring
- Log Analytics workspace for centralized logging

### Security Architecture
**Security Model:** {inputs.security_posture or 'Zero Trust with comprehensive defense'}
- **Identity:** {inputs.identity or 'Azure Active Directory'} with conditional access and PIM
- **Network Security:** Network Security Groups, Azure Firewall, and DDoS protection
- **Data Protection:** {inputs.key_vault or 'Azure Key Vault'} for secrets, keys, and certificates
- **Threat Protection:** {inputs.threat_protection or 'Azure Security Center, Sentinel, and Defender for Cloud'}
- **Compliance:** Continuous compliance monitoring with Azure Policy

### Workload Architecture
**Primary Workload:** {inputs.workload or 'Multi-tier web applications'}
- **Compute Strategy:** {', '.join(inputs.compute_services) if inputs.compute_services else 'Azure App Services with auto-scaling'}
- **Architecture Style:** {inputs.architecture_style or 'Microservices with API gateway pattern'}
- **Scalability:** {inputs.scalability or 'Auto-scaling enabled with performance monitoring'}
- **High Availability:** Multi-zone deployment with disaster recovery

### Integration & DevOps
- **CI/CD Pipeline:** Azure DevOps with automated testing and deployment
- **API Management:** Centralized API gateway for service integration
- **Event-Driven Architecture:** Service Bus and Event Grid for decoupled communication
- **Container Strategy:** Azure Kubernetes Service for containerized workloads
"""

    # Low Level Design (LLD) - Enhanced
    lld = f"""# Low Level Design (LLD)
## Azure Landing Zone Technical Implementation with Service Connectivity

**Document Version:** 2.0 (AI-Enhanced)
**Date:** {timestamp}
**Architecture Pattern:** {architecture_pattern}

### Service Connectivity Matrix
#### Implemented Connection Patterns:
1. **Web Tier Flow:** Application Gateway → Load Balancer → Compute Services
2. **Data Flow:** Compute Services → Database Services (via private endpoints)
3. **Security Flow:** All services → Key Vault (for secrets and certificates)
4. **Monitoring Flow:** All services → Azure Monitor → Log Analytics
5. **Integration Flow:** API Management → Logic Apps → Service Bus
6. **Network Flow:** VPN/ExpressRoute → Hub VNet → Spoke VNets

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
        from main import CustomerInputs
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
def download_azure_diagram(filename: str):
    """Download generated Azure architecture diagram PNG file"""
    try:
        file_path = f"/tmp/{filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Diagram file not found")
        
        with open(file_path, "rb") as f:
            diagram_data = f.read()
        
        return Response(
            content=diagram_data,
            media_type="image/png", 
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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
        
        # Check if we should provide human-in-the-loop feedback for better architecture
        feedback_questions = generate_feedback_questions(inputs)
        
        # Generate Mermaid diagram
        logger.info("Generating Mermaid diagram...")
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
            "ai_analysis": {
                "services_used": template_info.get("ai_services", []),
                "reasoning": template_info.get("ai_reasoning", "")
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

def generate_feedback_questions(inputs: CustomerInputs) -> List[str]:
    """Generate human-in-the-loop feedback questions to improve architecture"""
    questions = []
    
    # Check for missing critical information
    if not inputs.business_objective:
        questions.append("What is your primary business objective for this Azure deployment? (Cost optimization, agility, innovation, security, etc.)")
    
    if not inputs.scalability:
        questions.append("What are your expected scalability requirements? (Current and future user load, geographic distribution)")
    
    if not inputs.security_posture:
        questions.append("What security and compliance requirements do you have? (Zero trust, industry regulations, data sovereignty)")
    
    # Check if AI analysis was used and ask for validation
    total_selected_services = sum([
        len(inputs.compute_services or []),
        len(inputs.network_services or []),
        len(inputs.storage_services or []),
        len(inputs.database_services or []),
        len(inputs.security_services or [])
    ])
    
    if inputs.free_text_input and total_selected_services <= 1:
        questions.append("I've analyzed your requirements and suggested specific Azure services. Would you like to review and confirm these selections before finalizing the architecture?")
        questions.append("Are there any specific performance, availability, or disaster recovery requirements I should consider?")
    
    # Ask about budget and cost constraints
    if not inputs.cost_priority:
        questions.append("What is your cost optimization priority? Should we focus on minimizing costs or optimizing for performance?")
    
    # Ask about existing infrastructure
    if inputs.free_text_input and "existing" not in inputs.free_text_input.lower():
        questions.append("Do you have any existing Azure infrastructure or on-premises systems that need to be integrated?")
    
    # Ask about operational model
    if not inputs.ops_model and not inputs.monitoring:
        questions.append("How do you plan to operate and monitor this infrastructure? Do you have a dedicated DevOps team?")
    
    return questions[:3]  # Limit to top 3 most relevant questions

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
