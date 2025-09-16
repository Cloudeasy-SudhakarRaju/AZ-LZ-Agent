"""
Mock backend for testing the simplified UI functionality without external dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

app = FastAPI(title="Azure Landing Zone Agent - Mock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplifiedAnalysisRequest(BaseModel):
    free_text_input: str

class SimplifiedGenerationRequest(BaseModel):
    free_text_input: str
    ai_analysis: Optional[Dict[str, Any]] = None
    follow_up_answers: Optional[Dict[str, str]] = None

def mock_analyze_requirements(text: str) -> Dict[str, Any]:
    """Mock AI analysis based on keywords in the text"""
    text_lower = text.lower()
    
    # Default response
    analysis = {
        "services": [],
        "reasoning": "",
        "architecture_pattern": "Simple web application architecture",
        "connectivity_requirements": "Standard Azure networking with Virtual Network",
        "security_considerations": "Basic security with Key Vault and Network Security Groups",
        "scalability_design": "Manual scaling with load balancing capabilities",
        "operational_excellence": "Azure Monitor for basic monitoring and logging",
        "cost_optimization": "Standard pricing tiers with basic cost optimization",
        "needs_confirmation": False,
        "suggested_additions": [],
        "follow_up_questions": []
    }
    
    # Hub & Spoke pattern
    if "hub" in text_lower and "spoke" in text_lower:
        analysis.update({
            "services": ["virtual_network", "virtual_machines", "application_gateway", "firewall", "key_vault", "azure_monitor"],
            "reasoning": "Designed a hub-and-spoke network architecture with central security and connectivity. The hub virtual network contains shared services like Azure Firewall for centralized security policies. Spoke networks host workloads (VMs) with secure connectivity through the hub. Application Gateway provides layer-7 load balancing and SSL termination. Key Vault manages encryption keys and secrets. Azure Monitor provides comprehensive monitoring and logging across the infrastructure.",
            "architecture_pattern": "Hub-and-spoke network topology with centralized security and shared services",
            "connectivity_requirements": "Hub VNet with Azure Firewall, spoke VNets for workloads, VNet peering for connectivity",
            "security_considerations": "Azure Firewall for network security, NSGs for subnet-level security, Key Vault for secrets management",
            "needs_confirmation": True,
            "follow_up_questions": [
                "How many spoke networks do you need?",
                "What type of workloads will run in the spoke networks?",
                "Do you need ExpressRoute or VPN connectivity to on-premises?"
            ]
        })
    
    # E-commerce platform
    elif "e-commerce" in text_lower or "microservices" in text_lower:
        analysis.update({
            "services": ["aks", "application_gateway", "virtual_network", "cosmos_db", "redis", "service_bus", "api_management", "key_vault", "azure_monitor", "storage_accounts", "cdn"],
            "reasoning": "Designed a scalable microservices-based e-commerce platform using Azure Kubernetes Service (AKS) for container orchestration. Application Gateway provides SSL termination and web application firewall. Cosmos DB offers globally distributed NoSQL database for product catalogs and user data. Redis provides high-performance caching. Service Bus enables reliable messaging between microservices. API Management provides centralized API gateway. CDN improves global performance for static content.",
            "architecture_pattern": "Cloud-native microservices architecture with event-driven communication",
            "connectivity_requirements": "Application Gateway -> AKS Ingress -> Microservices, Service Bus for async communication",
            "security_considerations": "Zero Trust network model with private endpoints, Key Vault integration, Application Gateway WAF",
            "scalability_design": "Horizontal pod autoscaling in AKS, Cosmos DB auto-scaling, Redis clustering",
            "needs_confirmation": True,
            "follow_up_questions": [
                "What's your expected traffic volume?",
                "Do you need global distribution?",
                "What payment processing requirements do you have?"
            ]
        })
    
    # Data analytics
    elif "data" in text_lower and ("analytics" in text_lower or "databricks" in text_lower):
        analysis.update({
            "services": ["synapse_analytics", "data_factory", "databricks", "data_lake_storage", "stream_analytics", "event_hubs", "power_bi", "key_vault", "azure_monitor"],
            "reasoning": "Designed a comprehensive data analytics solution with Azure Synapse Analytics as the central analytics service. Data Factory orchestrates data movement and transformation. Databricks provides advanced analytics and machine learning capabilities. Data Lake Storage offers scalable storage for structured and unstructured data. Stream Analytics processes real-time data streams. Event Hubs ingests high-throughput data. Power BI provides business intelligence and visualization.",
            "architecture_pattern": "Modern data platform with lake house architecture",
            "connectivity_requirements": "Event Hubs -> Stream Analytics -> Data Lake, Data Factory orchestration, Synapse Analytics for querying",
            "security_considerations": "Private endpoints for all data services, Azure AD integration, data encryption at rest and in transit",
            "scalability_design": "Auto-scaling for Stream Analytics, elastic pools for Synapse, Databricks auto-scaling clusters",
            "needs_confirmation": True,
            "follow_up_questions": [
                "What data sources will you be ingesting?",
                "Do you need real-time or batch processing?",
                "What types of analytics workloads do you plan to run?"
            ]
        })
    
    # Basic web application
    elif "web" in text_lower or "app" in text_lower:
        analysis.update({
            "services": ["app_services", "sql_database", "application_gateway", "virtual_network", "key_vault", "azure_monitor", "storage_accounts"],
            "reasoning": "Designed a scalable web application architecture using Azure App Services for hosting the web application with built-in scaling and deployment features. SQL Database provides reliable relational database with automated backups and high availability. Application Gateway offers SSL termination, web application firewall, and load balancing. Virtual Network ensures secure communication. Key Vault manages connection strings and secrets. Storage Accounts handle static content and file uploads.",
            "architecture_pattern": "Three-tier web application architecture with presentation, application, and data layers",
            "connectivity_requirements": "Application Gateway -> App Services -> SQL Database, VNet integration for secure communication",
            "security_considerations": "Application Gateway WAF, VNet integration, private endpoints for database, Key Vault for secrets",
            "scalability_design": "App Services auto-scaling, SQL Database scaling options, Application Gateway auto-scaling",
            "needs_confirmation": True,
            "follow_up_questions": [
                "What technology stack are you using (.NET, Java, Python, etc.)?",
                "Do you need a specific database type?",
                "What are your expected user load requirements?"
            ]
        })
    
    # Default for other cases
    else:
        analysis.update({
            "services": ["virtual_machines", "virtual_network", "load_balancer", "storage_accounts", "key_vault", "azure_monitor"],
            "reasoning": "Designed a basic cloud infrastructure with Virtual Machines for compute workloads, Virtual Network for secure networking, Load Balancer for high availability, Storage Accounts for data storage, Key Vault for secrets management, and Azure Monitor for monitoring and logging. This provides a solid foundation that can be extended based on specific requirements.",
            "needs_confirmation": True,
            "follow_up_questions": [
                "Can you provide more details about your specific use case?",
                "What type of applications will you be running?",
                "Do you have any specific compliance or security requirements?"
            ]
        })
    
    return analysis

def mock_generate_architecture(request: SimplifiedGenerationRequest) -> Dict[str, Any]:
    """Mock architecture generation"""
    
    # Use provided analysis or generate new one
    if request.ai_analysis:
        analysis = request.ai_analysis
    else:
        analysis = mock_analyze_requirements(request.free_text_input)
    
    # Mock architecture components
    services = analysis.get("services", [])
    
    # Generate basic mermaid diagram
    mermaid_diagram = f"""
graph TB
    subgraph "Azure Architecture"
        User[👤 User] --> Gateway[🔗 Application Gateway]
"""
    
    if "virtual_network" in services:
        mermaid_diagram += "        Gateway --> VNet[🌐 Virtual Network]\n"
    
    if "virtual_machines" in services:
        mermaid_diagram += "        VNet --> VM[💻 Virtual Machines]\n"
    
    if "aks" in services:
        mermaid_diagram += "        VNet --> AKS[☸️ Azure Kubernetes Service]\n"
    
    if "app_services" in services:
        mermaid_diagram += "        VNet --> AppSvc[🚀 App Services]\n"
    
    if "sql_database" in services:
        mermaid_diagram += "        VNet --> SQL[🗄️ SQL Database]\n"
    
    if "cosmos_db" in services:
        mermaid_diagram += "        VNet --> Cosmos[🌍 Cosmos DB]\n"
    
    if "storage_accounts" in services:
        mermaid_diagram += "        VNet --> Storage[💾 Storage Accounts]\n"
    
    if "key_vault" in services:
        mermaid_diagram += "        VNet --> KV[🔐 Key Vault]\n"
    
    if "azure_monitor" in services:
        mermaid_diagram += "        VNet --> Monitor[📊 Azure Monitor]\n"
    
    mermaid_diagram += "    end"
    
    # Mock documentation
    tsd = f"""
# Technical Specification Document (TSD)

## Architecture Overview
{analysis.get('reasoning', 'Architecture designed based on requirements')}

## Architecture Pattern
{analysis.get('architecture_pattern', 'Standard cloud architecture')}

## Services Included
{', '.join(services)}

## Security Considerations
{analysis.get('security_considerations', 'Standard security practices applied')}

## Scalability Design
{analysis.get('scalability_design', 'Designed for scalability')}
"""
    
    hld = f"""
# High-Level Design (HLD)

## System Overview
This architecture implements {analysis.get('architecture_pattern', 'a cloud-based solution')} using Azure services.

## Component Architecture
- **Network Layer**: {analysis.get('connectivity_requirements', 'Standard networking')}
- **Security Layer**: {analysis.get('security_considerations', 'Basic security')}
- **Application Layer**: Core application services and compute resources
- **Data Layer**: Storage and database services
- **Monitoring Layer**: Observability and monitoring services

## Integration Patterns
Services are integrated following Azure best practices for security, scalability, and reliability.
"""
    
    lld = f"""
# Low-Level Design (LLD)

## Detailed Service Configuration

### Network Configuration
- Virtual Network with appropriate subnet segmentation
- Network Security Groups for traffic control
- Private endpoints where applicable

### Security Configuration
- Azure AD integration for identity management
- Key Vault for secrets and certificate management
- Role-based access control (RBAC)

### Monitoring Configuration
- Azure Monitor for infrastructure monitoring
- Application Insights for application performance monitoring
- Log Analytics for centralized logging

## Deployment Considerations
- Infrastructure as Code (IaC) recommended
- Blue-green deployment strategy for zero-downtime updates
- Automated backup and disaster recovery procedures
"""
    
    return {
        "success": True,
        "mermaid": mermaid_diagram,
        "svg_diagram": None,  # Would be generated by actual diagram service
        "tsd": tsd,
        "hld": hld,
        "lld": lld,
        "architecture_template": analysis,
        "metadata": {
            "generated_at": "2024-01-01T00:00:00Z",
            "services_count": len(services),
            "pattern": analysis.get('architecture_pattern', 'standard')
        },
        "azure_stencils": {
            "total_used": len(services),
            "unique_used": len(services),
            "stencils_list": services
        },
        "ai_analysis": analysis,
        "original_requirements": request.free_text_input
    }

@app.get("/")
def root():
    return {"message": "Azure Landing Zone Agent - Mock Backend", "status": "running"}

@app.post("/analyze-requirements")
def analyze_requirements_endpoint(request: SimplifiedAnalysisRequest):
    """Enhanced AI analysis endpoint for the simplified interface"""
    try:
        if not request.free_text_input.strip():
            raise HTTPException(status_code=400, detail="Requirements text is required")
        
        analysis = mock_analyze_requirements(request.free_text_input)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze requirements: {str(e)}")

@app.post("/generate-simplified-architecture")
def generate_simplified_architecture(request: SimplifiedGenerationRequest):
    """Generate architecture using the simplified interface approach"""
    try:
        if not request.free_text_input.strip():
            raise HTTPException(status_code=400, detail="Requirements text is required")
        
        result = mock_generate_architecture(request)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate simplified architecture: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)