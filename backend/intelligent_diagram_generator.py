"""
Intelligent Architecture Diagram Generator for Azure using LangChain and OpenAI LLM
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureRequirement:
    """Represents an architecture requirement parsed from natural language"""
    business_objective: str
    technical_requirements: List[str]
    security_requirements: List[str]
    compliance_requirements: List[str]
    scalability_requirements: List[str]
    azure_services: List[str]
    network_topology: str
    data_flow: List[Dict[str, str]]

@dataclass
class DiagramGenerationResult:
    """Result of diagram code generation"""
    python_code: str
    description: str
    review_comments: List[str]
    enterprise_compliance_score: float

class OpenAILLMOrchestrator:
    """Orchestrates OpenAI LLM calls for intelligent architecture processing"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OpenAI API key not provided. The intelligent diagram generator requires a valid OpenAI API key.")
            raise ValueError("OpenAI API key is required for intelligent diagram generation. Please set OPENAI_API_KEY environment variable.")
        
        # Validate API key format (basic check)
        if not self.api_key.startswith('sk-'):
            logger.error("Invalid OpenAI API key format. API keys should start with 'sk-'.")
            raise ValueError("Invalid OpenAI API key format. API keys should start with 'sk-'.")
        
        self.mock_mode = False
    
    def parse_natural_language_requirements(self, requirements_text: str) -> ArchitectureRequirement:
        """Parse natural language architecture requirements into structured format"""
        
        # OpenAI API call
        try:
            return self._call_openai_parse(requirements_text)
        except Exception as e:
            logger.error(f"Error parsing requirements with OpenAI: {e}")
            # Re-raise the error instead of falling back to mock
            raise RuntimeError(f"OpenAI API call failed: {str(e)}") from e
    
    def generate_diagram_code(self, requirements: ArchitectureRequirement) -> str:
        """Generate Python diagrams code based on architecture requirements"""
        
        # OpenAI API call
        try:
            return self._call_openai_generate(requirements)
        except Exception as e:
            logger.error(f"Error generating diagram code with OpenAI: {e}")
            # Re-raise the error instead of falling back to mock
            raise RuntimeError(f"OpenAI API call failed: {str(e)}") from e
    
    def _call_openai_parse(self, requirements_text: str) -> ArchitectureRequirement:
        """Call OpenAI API for requirements parsing"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""
        Parse the following architecture requirements into a structured format:
        
        Requirements: {requirements_text}
        
        Extract and return JSON with these keys:
        {{
            "business_objective": "",
            "technical_requirements": [],
            "security_requirements": [],
            "compliance_requirements": [],
            "scalability_requirements": [],
            "azure_services": [],
            "network_topology": "",
            "data_flow": []
        }}
        """
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an Azure architecture expert that parses requirements into structured JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            parsed_data = json.loads(content)
            return ArchitectureRequirement(**parsed_data)
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _call_openai_generate(self, requirements: ArchitectureRequirement) -> str:
        """Call OpenAI API for diagram code generation"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        prompt = f"""
        Generate Python code using the 'diagrams' library to create a professional Azure architecture diagram.
        
        Requirements:
        - Business Objective: {requirements.business_objective}
        - Azure Services: {', '.join(requirements.azure_services)}
        - Network Topology: {requirements.network_topology}
        
        Return ONLY the Python code with proper imports and diagram creation.
        """
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an expert in creating Azure architecture diagrams using the Python diagrams library."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _intelligent_parse_requirements(self, requirements_text: str) -> ArchitectureRequirement:
        """Intelligent parsing implementation for when OpenAI is not available"""
        text_lower = requirements_text.lower()
        
        # Extract business objective
        business_obj = "Enterprise Azure architecture"
        if "objective" in text_lower or "goal" in text_lower:
            # Extract sentence containing objective/goal
            sentences = requirements_text.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['objective', 'goal', 'purpose', 'need']):
                    business_obj = sentence.strip()
                    break
        
        # Parse technical requirements
        tech_req = []
        if any(word in text_lower for word in ['high availability', 'ha', 'availability']):
            tech_req.append("High availability")
        if any(word in text_lower for word in ['scale', 'scalability', 'elastic']):
            tech_req.append("Auto-scaling capabilities")
        if any(word in text_lower for word in ['performance', 'fast', 'speed']):
            tech_req.append("High performance")
        if any(word in text_lower for word in ['microservice', 'container', 'kubernetes']):
            tech_req.append("Microservices architecture")
        
        # Parse security requirements
        security_req = []
        if any(word in text_lower for word in ['security', 'secure', 'protection']):
            security_req.append("Network security")
        if any(word in text_lower for word in ['encryption', 'encrypt']):
            security_req.append("Data encryption")
        if any(word in text_lower for word in ['identity', 'authentication', 'auth']):
            security_req.append("Identity management")
        if any(word in text_lower for word in ['firewall', 'waf']):
            security_req.append("Web application firewall")
        
        # Parse compliance
        compliance_req = []
        if any(word in text_lower for word in ['gdpr', 'privacy']):
            compliance_req.append("GDPR compliance")
        if any(word in text_lower for word in ['hipaa', 'healthcare']):
            compliance_req.append("HIPAA compliance")
        if any(word in text_lower for word in ['soc', 'audit']):
            compliance_req.append("SOC 2 compliance")
        
        # Parse scalability
        scalability_req = []
        if any(word in text_lower for word in ['load balancing', 'load balancer']):
            scalability_req.append("Load balancing")
        if any(word in text_lower for word in ['auto scale', 'autoscale']):
            scalability_req.append("Auto-scaling")
        if any(word in text_lower for word in ['cdn', 'content delivery']):
            scalability_req.append("Content delivery network")
        
        # Intelligently detect Azure services
        services = []
        if any(word in text_lower for word in ['web app', 'web application', 'website']):
            services.append("app_services")
        if any(word in text_lower for word in ['virtual machine', 'vm', 'compute']):
            services.append("virtual_machines")
        if any(word in text_lower for word in ['kubernetes', 'aks', 'container']):
            services.append("aks")
        if any(word in text_lower for word in ['database', 'sql', 'data']):
            services.append("sql_database")
        if any(word in text_lower for word in ['storage', 'blob', 'file']):
            services.append("storage_accounts")
        if any(word in text_lower for word in ['cosmos', 'nosql']):
            services.append("cosmos_db")
        if any(word in text_lower for word in ['key vault', 'secrets']):
            services.append("key_vault")
        if any(word in text_lower for word in ['active directory', 'ad', 'identity']):
            services.append("active_directory")
        if any(word in text_lower for word in ['firewall', 'security']):
            services.append("firewall")
        if any(word in text_lower for word in ['application gateway', 'load balancer']):
            services.append("application_gateway")
        if any(word in text_lower for word in ['virtual network', 'vnet', 'network']):
            services.append("virtual_network")
        
        # Only use explicitly detected services - DO NOT add defaults
        # This ensures we only create what the user specifically requests
        
        # Determine network topology
        topology = "hub-spoke"
        if any(word in text_lower for word in ['hub spoke', 'hub-spoke']):
            topology = "hub-spoke"
        elif any(word in text_lower for word in ['single vnet', 'simple']):
            topology = "single-vnet"
        elif any(word in text_lower for word in ['mesh', 'multi-region']):
            topology = "mesh"
        
        # Create data flow patterns
        data_flow = []
        if "app_services" in services or "virtual_machines" in services:
            data_flow.append({"source": "Internet", "destination": "Application Layer", "protocol": "HTTPS"})
        if "sql_database" in services or "cosmos_db" in services:
            data_flow.append({"source": "Application Layer", "destination": "Database Layer", "protocol": "TDS/SQL"})
        if "storage_accounts" in services:
            data_flow.append({"source": "Application Layer", "destination": "Storage Layer", "protocol": "HTTPS"})
        
        return ArchitectureRequirement(
            business_objective=business_obj,
            technical_requirements=tech_req,
            security_requirements=security_req,
            compliance_requirements=compliance_req,
            scalability_requirements=scalability_req,
            azure_services=services,
            network_topology=topology,
            data_flow=data_flow
        )
    
    def _intelligent_generate_diagram_code(self, requirements: ArchitectureRequirement) -> str:
        """Intelligent diagram code generation"""
        
        # Build imports based on services
        imports = ["from diagrams import Diagram, Cluster, Edge"]
        compute_imports = []
        network_imports = []
        storage_imports = []
        database_imports = []
        security_imports = []
        
        # Map services to imports
        service_import_map = {
            "virtual_machines": ("diagrams.azure.compute", "VM"),
            "app_services": ("diagrams.azure.compute", "AppServices"),
            "aks": ("diagrams.azure.compute", "AKS"),
            "virtual_network": ("diagrams.azure.network", "VirtualNetworks"),
            "application_gateway": ("diagrams.azure.network", "ApplicationGateway"),
            "firewall": ("diagrams.azure.network", "Firewall"),
            "storage_accounts": ("diagrams.azure.storage", "StorageAccounts"),
            "sql_database": ("diagrams.azure.database", "SQLDatabases"),
            "cosmos_db": ("diagrams.azure.database", "CosmosDb"),
            "key_vault": ("diagrams.azure.security", "KeyVaults"),
            "active_directory": ("diagrams.azure.identity", "ActiveDirectory")
        }
        
        used_imports = set()
        for service in requirements.azure_services:
            if service in service_import_map:
                module, class_name = service_import_map[service]
                used_imports.add(f"from {module} import {class_name}")
        
        imports.extend(sorted(used_imports))
        
        # Generate diagram code
        code_parts = []
        code_parts.append('\n'.join(imports))
        code_parts.append('')
        
        # Diagram header
        diagram_name = requirements.business_objective[:50] + "..." if len(requirements.business_objective) > 50 else requirements.business_objective
        code_parts.append(f'''with Diagram(
    "{diagram_name}",
    filename="azure_architecture_intelligent",
    show=False,
    direction="TB",
    graph_attr={{
        "fontsize": "16",
        "fontname": "Arial",
        "rankdir": "TB",
        "bgcolor": "white",
        "pad": "1.0",
        "nodesep": "1.0",
        "ranksep": "1.0"
    }}
):''')
        
        # Generate clusters and components
        if "application_gateway" in requirements.azure_services or "firewall" in requirements.azure_services:
            code_parts.append('    # Internet-facing layer')
            code_parts.append('    with Cluster("Internet Gateway", graph_attr={"style": "rounded,filled", "color": "lightblue"}):')
            if "application_gateway" in requirements.azure_services:
                code_parts.append('        app_gw = ApplicationGateway("Application Gateway")')
            if "firewall" in requirements.azure_services:
                code_parts.append('        fw = Firewall("Azure Firewall")')
            code_parts.append('')
        
        # Application layer
        if any(svc in requirements.azure_services for svc in ["app_services", "virtual_machines", "aks"]):
            code_parts.append('    # Application layer')
            code_parts.append('    with Cluster("Application Tier", graph_attr={"style": "rounded,filled", "color": "lightgreen"}):')
            if "app_services" in requirements.azure_services:
                code_parts.append('        apps = AppServices("Web Applications")')
            elif "aks" in requirements.azure_services:
                code_parts.append('        apps = AKS("Kubernetes Cluster")')
            elif "virtual_machines" in requirements.azure_services:
                code_parts.append('        apps = VM("Application VMs")')
            code_parts.append('')
        
        # Data layer
        if any(svc in requirements.azure_services for svc in ["sql_database", "cosmos_db", "storage_accounts"]):
            code_parts.append('    # Data layer')
            code_parts.append('    with Cluster("Data Tier", graph_attr={"style": "rounded,filled", "color": "lightyellow"}):')
            if "sql_database" in requirements.azure_services:
                code_parts.append('        db = SQLDatabases("SQL Database")')
            if "cosmos_db" in requirements.azure_services:
                code_parts.append('        cosmos = CosmosDb("Cosmos DB")')
            if "storage_accounts" in requirements.azure_services:
                code_parts.append('        storage = StorageAccounts("Storage Accounts")')
            code_parts.append('')
        
        # Security layer
        if any(svc in requirements.azure_services for svc in ["key_vault", "active_directory"]):
            code_parts.append('    # Security & Identity')
            code_parts.append('    with Cluster("Security & Identity", graph_attr={"style": "rounded,filled", "color": "lightcoral"}):')
            if "key_vault" in requirements.azure_services:
                code_parts.append('        kv = KeyVaults("Key Vault")')
            if "active_directory" in requirements.azure_services:
                code_parts.append('        ad = ActiveDirectory("Active Directory")')
            code_parts.append('')
        
        # Add connections based on data flow and common patterns
        code_parts.append('    # Define connections with proper styling')
        
        # Internet to gateway
        if "application_gateway" in requirements.azure_services:
            code_parts.append('    "Internet Users" >> Edge(label="HTTPS", style="bold", color="blue") >> app_gw')
        
        # Gateway to applications
        if "application_gateway" in requirements.azure_services and any(svc in requirements.azure_services for svc in ["app_services", "aks", "virtual_machines"]):
            code_parts.append('    app_gw >> Edge(label="HTTP/HTTPS", style="bold") >> apps')
        
        # Applications to database
        if any(svc in requirements.azure_services for svc in ["app_services", "aks", "virtual_machines"]) and "sql_database" in requirements.azure_services:
            code_parts.append('    apps >> Edge(label="SQL", style="dashed") >> db')
        
        # Applications to storage
        if any(svc in requirements.azure_services for svc in ["app_services", "aks", "virtual_machines"]) and "storage_accounts" in requirements.azure_services:
            code_parts.append('    apps >> Edge(label="Storage API", style="dashed") >> storage')
        
        # Security connections
        if "key_vault" in requirements.azure_services and any(svc in requirements.azure_services for svc in ["app_services", "aks", "virtual_machines"]):
            code_parts.append('    apps >> Edge(label="Secrets", style="dotted", color="red") >> kv')
        
        return '\n'.join(code_parts)

class EnterpriseReviewAgent:
    """Reviews diagram code against enterprise checklist"""
    
    def __init__(self, llm_orchestrator: OpenAILLMOrchestrator):
        self.llm = llm_orchestrator
        self.enterprise_checklist = [
            "Uses official Azure icons and branding",
            "Implements proper security zones",
            "Includes network segmentation",
            "Shows proper data flow",
            "Implements high availability design",
            "Includes monitoring and logging",
            "Follows Azure Well-Architected Framework",
            "Implements least privilege access",
            "Includes backup and disaster recovery",
            "Uses managed services where appropriate"
        ]
    
    def review_diagram_code(self, diagram_code: str, requirements: ArchitectureRequirement) -> Dict[str, Any]:
        """Review generated diagram code against enterprise standards"""
        
        if self.llm.mock_mode:
            return self._intelligent_review(diagram_code, requirements)
        
        # OpenAI API call would go here
        try:
            return self._call_openai_review(diagram_code, requirements)
        except Exception as e:
            logger.error(f"Error reviewing diagram code with OpenAI: {e}")
            return self._intelligent_review(diagram_code, requirements)
    
    def _call_openai_review(self, diagram_code: str, requirements: ArchitectureRequirement) -> Dict[str, Any]:
        """Call OpenAI API for diagram review"""
        # Implementation would go here
        return self._intelligent_review(diagram_code, requirements)
    
    def _intelligent_review(self, diagram_code: str, requirements: ArchitectureRequirement) -> Dict[str, Any]:
        """Intelligent review implementation"""
        issues = []
        recommendations = []
        missing_elements = []
        score = 100
        
        # Security checks
        if "KeyVaults" not in diagram_code and "key_vault" not in str(requirements.azure_services):
            issues.append("Missing Key Vault for secrets management")
            missing_elements.append("Key Vault")
            score -= 10
        
        if "ActiveDirectory" not in diagram_code and "active_directory" not in str(requirements.azure_services):
            issues.append("Missing Active Directory for identity management")
            missing_elements.append("Active Directory")
            score -= 10
        
        # Architecture checks
        if "Cluster" not in diagram_code:
            issues.append("Missing logical groupings (clusters)")
            recommendations.append("Add proper clustering for logical groupings")
            score -= 5
        
        if "Edge" not in diagram_code:
            issues.append("Missing connection definitions")
            recommendations.append("Add proper edge connections between components")
            score -= 5
        
        # Network security
        if "Firewall" not in diagram_code and not any(sec in requirements.security_requirements for sec in ["Network security", "firewall"]):
            recommendations.append("Consider adding Azure Firewall for network security")
            score -= 5
        
        # High availability
        if not any(ha in str(requirements.technical_requirements) for ha in ["High availability", "availability"]):
            recommendations.append("Consider high availability design patterns")
            score -= 5
        
        # Monitoring
        if "Monitor" not in diagram_code and "monitoring" not in str(requirements.technical_requirements):
            recommendations.append("Add Azure Monitor for observability")
            score -= 5
        
        # Data protection
        if any(db in requirements.azure_services for db in ["sql_database", "cosmos_db"]) and "backup" not in str(requirements.technical_requirements):
            recommendations.append("Consider backup and disaster recovery for data services")
            score -= 5
        
        # Professional styling
        styling_score = 0
        if "graph_attr" in diagram_code:
            styling_score += 10
        if "style" in diagram_code:
            styling_score += 10
        if "color" in diagram_code:
            styling_score += 10
        
        score = max(score, styling_score)
        
        return {
            "compliance_score": max(0, min(100, score)),
            "issues": issues,
            "recommendations": recommendations,
            "missing_elements": missing_elements,
            "approved": score >= 70,
            "styling_score": styling_score,
            "security_score": max(0, 100 - len([i for i in issues if "security" in i.lower() or "vault" in i.lower() or "directory" in i.lower()]) * 20)
        }

class IntelligentArchitectureDiagramGenerator:
    """Main class that orchestrates the intelligent diagram generation process"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.llm_orchestrator = OpenAILLMOrchestrator(openai_api_key)
        self.review_agent = EnterpriseReviewAgent(self.llm_orchestrator)
    
    def generate_from_natural_language(self, requirements_text: str) -> DiagramGenerationResult:
        """Generate architecture diagram from natural language requirements"""
        
        logger.info("Starting intelligent diagram generation from natural language")
        
        # Step 1: Parse natural language requirements
        logger.info("Parsing natural language requirements...")
        requirements = self.llm_orchestrator.parse_natural_language_requirements(requirements_text)
        logger.info(f"Parsed requirements: {requirements.business_objective}")
        
        # Step 2: Generate diagram code
        logger.info("Generating diagram code...")
        diagram_code = self.llm_orchestrator.generate_diagram_code(requirements)
        logger.info("Diagram code generated successfully")
        
        # Step 3: Review with enterprise agent
        logger.info("Reviewing diagram against enterprise standards...")
        review_result = self.review_agent.review_diagram_code(diagram_code, requirements)
        logger.info(f"Review completed - Compliance score: {review_result.get('compliance_score', 0)}")
        
        # Step 4: Return result
        result = DiagramGenerationResult(
            python_code=diagram_code,
            description=f"Architecture diagram for: {requirements.business_objective}",
            review_comments=review_result.get('issues', []) + review_result.get('recommendations', []),
            enterprise_compliance_score=review_result.get('compliance_score', 0)
        )
        
        logger.info("Intelligent diagram generation completed")
        return result
    
    def enhance_existing_diagram(self, existing_code: str, enhancement_requirements: str) -> DiagramGenerationResult:
        """Enhance existing diagram code based on new requirements"""
        
        logger.info("Enhancing existing diagram")
        
        # Parse enhancement requirements
        enhancement_parsed = self.llm_orchestrator.parse_natural_language_requirements(enhancement_requirements)
        
        # Simple enhancement by adding components
        enhanced_code = existing_code
        
        # Add new services if they don't exist
        for service in enhancement_parsed.azure_services:
            service_patterns = {
                "monitoring": "Monitor",
                "backup": "Backup",
                "cdn": "CDN",
                "api_management": "APIManagement"
            }
            
            for pattern, class_name in service_patterns.items():
                if pattern in service and class_name not in existing_code:
                    # Add import and component
                    enhanced_code += f"\n# Enhanced with {service}\n"
                    enhanced_code += f"# Add {class_name} component as needed\n"
        
        # Review enhanced code
        review_result = self.review_agent.review_diagram_code(enhanced_code, enhancement_parsed)
        
        return DiagramGenerationResult(
            python_code=enhanced_code,
            description=f"Enhanced diagram with: {enhancement_requirements}",
            review_comments=review_result.get('issues', []) + review_result.get('recommendations', []),
            enterprise_compliance_score=review_result.get('compliance_score', 0)
        )