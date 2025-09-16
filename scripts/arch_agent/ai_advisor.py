"""
AI Advisor for architectural pattern selection and dependency inference.
Implements requirement 8: AI Reasoning and Dynamic Pattern Selection.
"""
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from .schemas import Requirements, UserIntent, LayoutGraph

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIArchitecturalAdvisor:
    """
    AI-powered advisor for architectural decisions and pattern selection.
    Implements requirement 8: AI Reasoning and Dynamic Pattern Selection.
    """
    
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self._initialize_ai_clients()
    
    def _initialize_ai_clients(self) -> None:
        """Initialize available AI clients based on environment variables."""
        # Try OpenAI first
        if OPENAI_AVAILABLE:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                try:
                    openai.api_key = openai_key
                    self.openai_client = openai
                except Exception as e:
                    print(f"Warning: Failed to initialize OpenAI client: {e}")
        
        # Try Gemini as fallback
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                except Exception as e:
                    print(f"Warning: Failed to initialize Gemini client: {e}")
    
    def analyze_architectural_intent(self, requirements: Requirements) -> Dict[str, Any]:
        """
        Analyze architectural intent and provide recommendations.
        
        Args:
            requirements: Current architecture requirements
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        if not self._has_ai_capability():
            return self._fallback_analysis(requirements)
        
        # Prepare context for AI analysis
        context = self._prepare_analysis_context(requirements)
        prompt = self._build_analysis_prompt(context)
        
        try:
            # Try to get AI recommendations
            response = self._query_ai(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            print(f"Warning: AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(requirements)
    
    def infer_missing_dependencies(self, services: List[UserIntent]) -> List[UserIntent]:
        """
        Use AI to infer missing dependencies for better architectural completeness.
        Implements requirement 6: Component Completeness.
        
        Args:
            services: List of explicitly requested services
            
        Returns:
            List of additional recommended services
        """
        if not self._has_ai_capability():
            return self._fallback_dependency_inference(services)
        
        # Prepare context for dependency analysis
        service_types = [service.kind for service in services]
        prompt = self._build_dependency_prompt(service_types)
        
        try:
            response = self._query_ai(prompt)
            return self._parse_dependency_response(response)
        except Exception as e:
            print(f"Warning: AI dependency inference failed, using fallback: {e}")
            return self._fallback_dependency_inference(services)
    
    def optimize_service_grouping(self, services: List[UserIntent], requirements: Requirements) -> Dict[str, List[UserIntent]]:
        """
        Use AI to optimize service grouping for better visual hierarchy.
        Implements requirement 1: Containerization and Logical Layers.
        
        Args:
            services: List of services to group
            requirements: Architecture requirements
            
        Returns:
            Dictionary of service groups optimized by AI
        """
        if not self._has_ai_capability():
            return self._fallback_service_grouping(services, requirements)
        
        # Prepare context for grouping analysis
        prompt = self._build_grouping_prompt(services, requirements)
        
        try:
            response = self._query_ai(prompt)
            return self._parse_grouping_response(response, services)
        except Exception as e:
            print(f"Warning: AI service grouping failed, using fallback: {e}")
            return self._fallback_service_grouping(services, requirements)
    
    def suggest_pattern_selection(self, requirements: Requirements) -> str:
        """
        Use AI to suggest the best architectural pattern based on requirements.
        
        Args:
            requirements: Architecture requirements
            
        Returns:
            Recommended pattern name
        """
        if not self._has_ai_capability():
            return self._fallback_pattern_selection(requirements)
        
        prompt = self._build_pattern_prompt(requirements)
        
        try:
            response = self._query_ai(prompt)
            return self._parse_pattern_response(response)
        except Exception as e:
            print(f"Warning: AI pattern selection failed, using fallback: {e}")
            return self._fallback_pattern_selection(requirements)
    
    def _has_ai_capability(self) -> bool:
        """Check if AI capabilities are available."""
        return self.openai_client is not None or self.gemini_model is not None
    
    def _query_ai(self, prompt: str) -> str:
        """Query available AI service with the given prompt."""
        if self.openai_client:
            return self._query_openai(prompt)
        elif self.gemini_model:
            return self._query_gemini(prompt)
        else:
            raise Exception("No AI service available")
    
    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI with the given prompt."""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI query failed: {e}")
    
    def _query_gemini(self, prompt: str) -> str:
        """Query Gemini with the given prompt."""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini query failed: {e}")
    
    def _prepare_analysis_context(self, requirements: Requirements) -> Dict[str, Any]:
        """Prepare context for AI analysis."""
        return {
            "regions": requirements.regions,
            "ha_mode": requirements.ha_mode,
            "environment": requirements.environment,
            "services": [{"kind": s.kind, "name": s.name} for s in requirements.services],
            "edge_services": requirements.edge_services,
            "identity_services": requirements.identity_services
        }
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for architectural analysis."""
        return f"""
You are an Azure architecture expert. Analyze the following requirements and provide recommendations:

Context: {json.dumps(context, indent=2)}

Please provide analysis in the following JSON format:
{{
    "pattern_recommendation": "recommended pattern name",
    "cluster_strategy": "recommended clustering approach", 
    "missing_components": ["list", "of", "missing", "components"],
    "optimization_suggestions": ["suggestion1", "suggestion2"],
    "risk_assessment": "brief risk assessment"
}}

Focus on Azure best practices, security, scalability, and cost optimization.
"""
    
    def _build_dependency_prompt(self, service_types: List[str]) -> str:
        """Build prompt for dependency inference."""
        return f"""
You are an Azure architecture expert. Given these Azure services: {service_types}

What additional Azure services would typically be required for a complete, production-ready architecture?

Consider:
- Networking infrastructure (VNet, subnets, NSGs)
- Security components (Key Vault, identity services)
- Monitoring and logging
- Storage dependencies
- Load balancing and traffic management

Respond with a JSON array of service types:
["service_type1", "service_type2", ...]

Use standard Azure service names like: vnet, subnet, nsg, key_vault, log_analytics, application_insights, etc.
"""
    
    def _build_grouping_prompt(self, services: List[UserIntent], requirements: Requirements) -> str:
        """Build prompt for service grouping optimization."""
        service_list = [f"{s.kind} ({s.name or 'unnamed'})" for s in services]
        
        return f"""
You are an Azure architecture expert. Group these Azure services into logical layers for optimal visualization:

Services: {service_list}
HA Mode: {requirements.ha_mode}
Regions: {requirements.regions}

Group services into these categories:
- internet_edge: Internet-facing services
- identity_security: Identity and security services  
- active_region_compute: Compute services in active regions
- active_region_network: Network services in active regions
- active_region_data: Data services in active regions
- monitoring: Monitoring and observability
- devops: DevOps and CI/CD services

Respond with JSON:
{{
    "internet_edge": ["service1", "service2"],
    "identity_security": ["service3"],
    "active_region_compute": ["service4", "service5"],
    "active_region_network": ["service6"],
    "active_region_data": ["service7"],
    "monitoring": ["service8"],
    "devops": []
}}
"""
    
    def _build_pattern_prompt(self, requirements: Requirements) -> str:
        """Build prompt for pattern selection."""
        return f"""
You are an Azure architecture expert. Recommend the best architectural pattern for:

Requirements:
- Regions: {requirements.regions}
- HA Mode: {requirements.ha_mode}
- Environment: {requirements.environment}
- Services: {len(requirements.services)} services

Available patterns:
- ha-multiregion: High availability across multiple regions
- single-region: Single region deployment
- hybrid-cloud: Hybrid cloud deployment

Respond with just the pattern name: "ha-multiregion" or "single-region" or "hybrid-cloud"
"""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI analysis response."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return {
                "pattern_recommendation": "ha-multiregion",
                "cluster_strategy": "logical_layers",
                "missing_components": [],
                "optimization_suggestions": ["Use AI-recommended optimizations"],
                "risk_assessment": "Standard Azure architecture risks apply"
            }
    
    def _parse_dependency_response(self, response: str) -> List[UserIntent]:
        """Parse dependency inference response."""
        try:
            service_types = json.loads(response)
            return [UserIntent(kind=service_type, name=None) for service_type in service_types]
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _parse_grouping_response(self, response: str, services: List[UserIntent]) -> Dict[str, List[UserIntent]]:
        """Parse service grouping response."""
        try:
            grouping = json.loads(response)
            result = {}
            
            # Create service lookup
            service_lookup = {s.kind: s for s in services}
            
            for group_name, service_kinds in grouping.items():
                result[group_name] = []
                for kind in service_kinds:
                    if kind in service_lookup:
                        result[group_name].append(service_lookup[kind])
            
            return result
        except (json.JSONDecodeError, TypeError):
            return self._fallback_service_grouping(services, None)
    
    def _parse_pattern_response(self, response: str) -> str:
        """Parse pattern selection response."""
        response = response.strip().lower()
        if "ha-multiregion" in response:
            return "ha-multiregion"
        elif "single-region" in response:
            return "single-region"
        elif "hybrid" in response:
            return "hybrid-cloud"
        else:
            return "ha-multiregion"  # Default fallback
    
    def _fallback_analysis(self, requirements: Requirements) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        return {
            "pattern_recommendation": "ha-multiregion" if len(requirements.regions) > 1 else "single-region",
            "cluster_strategy": "logical_layers",
            "missing_components": ["vnet", "nsg", "log_analytics"] if not any(s.kind in ["vnet", "nsg", "log_analytics"] for s in requirements.services) else [],
            "optimization_suggestions": [
                "Consider adding monitoring services",
                "Ensure proper network segmentation",
                "Add security services if missing"
            ],
            "risk_assessment": "Standard fallback analysis - consider enabling AI advisor for detailed insights"
        }
    
    def _fallback_dependency_inference(self, services: List[UserIntent]) -> List[UserIntent]:
        """Fallback dependency inference when AI is not available."""
        existing_types = {s.kind for s in services}
        recommended = []
        
        # Basic dependency rules
        if any(s.kind in ["vm", "web_app", "function_app"] for s in services):
            if "vnet" not in existing_types:
                recommended.append(UserIntent(kind="vnet", name="Virtual Network"))
            if "nsg" not in existing_types:
                recommended.append(UserIntent(kind="nsg", name="Network Security Group"))
        
        if not any(s.kind in ["log_analytics", "application_insights"] for s in services):
            recommended.append(UserIntent(kind="log_analytics", name="Log Analytics"))
            recommended.append(UserIntent(kind="application_insights", name="Application Insights"))
        
        if not any(s.kind == "key_vault" for s in services):
            recommended.append(UserIntent(kind="key_vault", name="Key Vault"))
        
        return recommended
    
    def _fallback_service_grouping(self, services: List[UserIntent], requirements: Optional[Requirements]) -> Dict[str, List[UserIntent]]:
        """Fallback service grouping when AI is not available."""
        groups = {
            "internet_edge": [],
            "identity_security": [],
            "active_region_compute": [],
            "active_region_network": [],
            "active_region_data": [],
            "monitoring": [],
            "devops": []
        }
        
        # First, add services from requirements edge_services and identity_services
        if requirements:
            for edge_service in requirements.edge_services:
                edge_intent = UserIntent(kind=edge_service, name=None)
                groups["internet_edge"].append(edge_intent)
            
            for identity_service in requirements.identity_services:
                identity_intent = UserIntent(kind=identity_service, name=None)
                groups["identity_security"].append(identity_intent)
        
        # Then process the main services list
        for service in services:
            service_type = service.kind
            
            if service_type in ["front_door", "cdn", "traffic_manager"]:
                groups["internet_edge"].append(service)
            elif service_type in ["entra_id", "key_vault", "active_directory"]:
                groups["identity_security"].append(service)
            elif service_type in ["vm", "web_app", "function_app", "aks"]:
                groups["active_region_compute"].append(service)
            elif service_type in ["vnet", "subnet", "nsg", "load_balancer", "application_gateway"]:
                groups["active_region_network"].append(service)
            elif service_type in ["storage_account", "sql_database", "redis", "cosmos_db", "queue_storage", "table_storage"]:
                groups["active_region_data"].append(service)
            elif service_type in ["log_analytics", "application_insights", "monitor"]:
                groups["monitoring"].append(service)
            else:
                groups["active_region_compute"].append(service)  # Default fallback
        
        return groups
    
    def _fallback_pattern_selection(self, requirements: Requirements) -> str:
        """Fallback pattern selection when AI is not available."""
        if len(requirements.regions) > 1:
            return "ha-multiregion"
        else:
            return "single-region"