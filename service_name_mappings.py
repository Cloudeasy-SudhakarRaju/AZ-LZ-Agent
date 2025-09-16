#!/usr/bin/env python3
"""
Service Name Mapping and Validation Tool
This tool helps map common service names to valid Azure service names for the diagram generation API.
"""

# Common service name aliases that users might use mapped to valid service names
SERVICE_NAME_ALIASES = {
    # Compute services
    "app_service": "app_services",  # Common mistake: singular vs plural
    "webapp": "app_services",
    "web_app": "app_services", 
    "kubernetes": "aks",
    "container_service": "aks",
    "vm": "virtual_machines",
    "virtual_machine": "virtual_machines",
    "compute": "virtual_machines",
    "function": "functions",
    "function_app": "functions",
    "serverless": "functions",
    
    # Network services
    "vnet": "virtual_network",
    "virtual_network_gateway": "vpn_gateway",
    "vpn": "vpn_gateway",
    "lb": "load_balancer",
    "alb": "application_gateway",
    "app_gateway": "application_gateway",
    "app_gw": "application_gateway",
    "waf": "application_gateway",  # WAF is part of App Gateway
    "cdn": "front_door",  # Azure CDN is part of Front Door
    
    # Database services
    "database": "sql_database",
    "sql": "sql_database",
    "sql_server": "sql_database",
    "cosmosdb": "cosmos_db",
    "cosmos": "cosmos_db",
    "mysql_db": "mysql",
    "postgres": "postgresql",
    "postgres_db": "postgresql",
    "cache": "redis",
    
    # Storage services
    "storage": "storage_accounts",
    "blob": "blob_storage",
    "files": "file_storage",
    "queue": "queue_storage",
    "table": "table_storage",
    "disk": "disk_storage",
    "disks": "disk_storage",
    
    # Security services
    "ad": "active_directory",
    "aad": "active_directory",
    "azure_ad": "active_directory",
    "keyvault": "key_vault",
    "vault": "key_vault",
    "asc": "security_center",
    
    # Monitoring services
    "azure_monitor": "monitor",  # Common mistake: adding "azure_" prefix
    "monitoring": "monitor",
    "logs": "log_analytics",
    "log_analytics_workspace": "log_analytics",
    "app_insights": "application_insights",
    "insights": "application_insights",
    
    # AI/ML services
    "ml": "machine_learning",
    "azure_ml": "machine_learning",
    "cognitive": "cognitive_services",
    "ai": "cognitive_services",
    "bot": "bot_service",
    "chatbot": "bot_service",
    
    # Analytics services
    "analytics": "synapse",
    "synapse_analytics": "synapse",
    "adf": "data_factory",
    "datafactory": "data_factory",
    "streaming": "stream_analytics",
    "stream": "stream_analytics",
    "powerbi": "power_bi",
    
    # Integration services
    "logic_app": "logic_apps",
    "workflow": "logic_apps",
    "servicebus": "service_bus",
    "sb": "service_bus",
    "messaging": "service_bus",
    "eventgrid": "event_grid",
    "events": "event_grid",
    "eventhub": "event_hubs",
    "event_hub": "event_hubs",
    "api_mgmt": "api_management",
    "apim": "api_management",
    
    # DevOps services
    "azure_devops": "devops",
    "ado": "devops",
    "container_registry": "devops",  # Common mistake: using CR instead of DevOps
    "acr": "devops",
    "github": "devops",
    "cicd": "devops",
    
    # Backup services
    "azure_backup": "backup",
    "asr": "site_recovery",
    "disaster_recovery": "site_recovery",
    "dr": "site_recovery"
}

# Valid service names by category (from backend validation)
VALID_SERVICES_BY_CATEGORY = {
    "compute": ["virtual_machines", "aks", "app_services", "web_apps", "functions", "container_instances", "service_fabric", "batch"],
    "network": ["virtual_network", "vpn_gateway", "expressroute", "load_balancer", "application_gateway", "front_door", "firewall", "waf", "cdn", "traffic_manager", "virtual_wan"],
    "storage": ["storage_accounts", "blob_storage", "queue_storage", "table_storage", "file_storage", "disk_storage", "data_lake"],
    "database": ["sql_database", "sql_managed_instance", "cosmos_db", "mysql", "postgresql", "mariadb", "redis"],
    "security": ["key_vault", "active_directory", "security_center", "sentinel", "defender", "information_protection"],
    "monitoring": ["monitor", "log_analytics", "application_insights", "service_health", "advisor"],
    "ai": ["cognitive_services", "machine_learning", "bot_service", "form_recognizer"],
    "analytics": ["synapse", "data_factory", "databricks", "stream_analytics", "power_bi"],
    "integration": ["logic_apps", "service_bus", "event_grid", "event_hubs", "api_management"],
    "devops": ["devops", "automation"],
    "backup": ["backup", "site_recovery"]
}

def normalize_service_name(service_name: str) -> str:
    """
    Normalize a service name to match backend validation requirements.
    
    Args:
        service_name: The service name to normalize
        
    Returns:
        The normalized service name, or original if no mapping exists
    """
    # Convert to lowercase and strip whitespace
    normalized = service_name.lower().strip()
    
    # Remove common prefixes
    prefixes_to_remove = ["azure_", "azure ", "microsoft_", "microsoft "]
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    # Check for direct aliases
    if normalized in SERVICE_NAME_ALIASES:
        return SERVICE_NAME_ALIASES[normalized]
    
    # Return original if no mapping found
    return service_name

def validate_service_names(services_by_category: dict) -> dict:
    """
    Validate and normalize service names for each category.
    
    Args:
        services_by_category: Dictionary with category names as keys and service lists as values
        
    Returns:
        Dictionary with normalized service names and validation results
    """
    results = {
        "normalized_services": {},
        "invalid_services": {},
        "suggestions": {}
    }
    
    for category, services in services_by_category.items():
        if not services:
            continue
            
        category_key = category.replace("_services", "")  # Remove _services suffix
        valid_services = VALID_SERVICES_BY_CATEGORY.get(category_key, [])
        
        normalized = []
        invalid = []
        suggestions = []
        
        for service in services:
            normalized_name = normalize_service_name(service)
            
            if normalized_name in valid_services:
                normalized.append(normalized_name)
            else:
                invalid.append(service)
                # Find closest matches
                closest_matches = [s for s in valid_services if service.lower() in s or s in service.lower()]
                if closest_matches:
                    suggestions.extend(closest_matches)
        
        if normalized:
            results["normalized_services"][category] = normalized
        if invalid:
            results["invalid_services"][category] = invalid
        if suggestions:
            results["suggestions"][category] = list(set(suggestions))
    
    return results

def get_service_recommendations(text_description: str) -> dict:
    """
    Get service recommendations based on text description.
    
    Args:
        text_description: Free text description of requirements
        
    Returns:
        Dictionary with recommended services by category
    """
    text_lower = text_description.lower()
    recommendations = {}
    
    # Basic keyword matching for recommendations
    keyword_mappings = {
        # Web/API keywords
        ("web", "website", "api", "rest", "http"): {"compute": ["app_services"], "network": ["application_gateway"]},
        ("kubernetes", "container", "docker", "microservices"): {"compute": ["aks"], "network": ["virtual_network"]},
        ("serverless", "function", "lambda"): {"compute": ["functions"]},
        
        # Database keywords
        ("database", "data", "sql", "storage"): {"database": ["sql_database"], "storage": ["blob_storage"]},
        ("nosql", "document", "mongodb"): {"database": ["cosmos_db"]},
        ("cache", "redis", "session"): {"database": ["redis"]},
        
        # Security keywords
        ("security", "authentication", "auth", "login"): {"security": ["key_vault", "active_directory"]},
        ("secrets", "keys", "certificates"): {"security": ["key_vault"]},
        
        # Monitoring keywords
        ("monitoring", "logs", "metrics", "observability"): {"monitoring": ["monitor", "application_insights"]},
        ("analytics", "reporting", "dashboard"): {"analytics": ["synapse"], "monitoring": ["monitor"]},
        
        # Integration keywords
        ("integration", "workflow", "automation"): {"integration": ["logic_apps"]},
        ("messaging", "queue", "events"): {"integration": ["service_bus", "event_hubs"]},
    }
    
    for keywords, services in keyword_mappings.items():
        if any(keyword in text_lower for keyword in keywords):
            for category, service_list in services.items():
                if category not in recommendations:
                    recommendations[category] = []
                recommendations[category].extend(service_list)
    
    # Always include basic networking
    if "network" not in recommendations:
        recommendations["network"] = ["virtual_network"]
    
    # Remove duplicates
    for category in recommendations:
        recommendations[category] = list(set(recommendations[category]))
    
    return recommendations

if __name__ == "__main__":
    # Example usage
    print("Azure Service Name Mapping Tool")
    print("=" * 40)
    
    # Test common mistakes
    test_services = {
        "compute_services": ["app_service", "kubernetes", "vm"],
        "database_services": ["sql", "cosmosdb"], 
        "monitoring_services": ["azure_monitor", "app_insights"],
        "security_services": ["keyvault", "azure_ad"]
    }
    
    results = validate_service_names(test_services)
    
    print("Test Results:")
    print(f"Normalized: {results['normalized_services']}")
    print(f"Invalid: {results['invalid_services']}")
    print(f"Suggestions: {results['suggestions']}")
    
    # Test text recommendations
    description = "I need a web application with database and monitoring"
    recommendations = get_service_recommendations(description)
    print(f"\nRecommendations for '{description}':")
    print(recommendations)