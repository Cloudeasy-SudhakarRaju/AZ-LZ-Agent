"""
Enhanced Service Validation with Auto-Correction
This module provides enhanced service validation that automatically corrects common service naming mistakes.
"""

from service_name_mappings import normalize_service_name, SERVICE_NAME_ALIASES, VALID_SERVICES_BY_CATEGORY

def validate_and_correct_services(service_categories: dict) -> dict:
    """
    Validate service categories and automatically correct common naming issues.
    
    Args:
        service_categories: Dictionary with service category names as keys and service lists as values
        
    Returns:
        Dictionary with corrected services and validation results
    """
    corrected_categories = {}
    corrections_made = {}
    validation_errors = {}
    
    for category_name, service_list in service_categories.items():
        if not service_list:
            continue
            
        # Normalize category name (remove _services suffix for lookup)
        category_key = category_name.replace('_services', '')
        valid_services = VALID_SERVICES_BY_CATEGORY.get(category_key, [])
        
        corrected_services = []
        category_corrections = []
        category_errors = []
        
        for service in service_list:
            # Try to normalize the service name
            normalized_service = normalize_service_name(service)
            
            if normalized_service in valid_services:
                corrected_services.append(normalized_service)
                if normalized_service != service:
                    category_corrections.append(f"{service} -> {normalized_service}")
            else:
                # Service is invalid even after normalization
                category_errors.append(f"'{service}' (normalized: '{normalized_service}')")
        
        # Store results
        if corrected_services:
            corrected_categories[category_name] = corrected_services
        if category_corrections:
            corrections_made[category_name] = category_corrections
        if category_errors:
            validation_errors[category_name] = {
                "invalid_services": category_errors,
                "available_services": valid_services
            }
    
    return {
        "corrected_services": corrected_categories,
        "corrections_made": corrections_made,
        "validation_errors": validation_errors,
        "has_errors": bool(validation_errors)
    }

def create_helpful_error_message(category_name: str, invalid_services: list, available_services: list) -> str:
    """
    Create a helpful error message with suggestions for invalid services.
    
    Args:
        category_name: The category name (e.g., 'compute_services')
        invalid_services: List of invalid service names
        available_services: List of valid service names for this category
        
    Returns:
        Formatted error message with suggestions
    """
    category_display = category_name.replace('_', ' ').title()
    
    # Find suggestions for each invalid service
    suggestions = {}
    for invalid_service in invalid_services:
        service_suggestions = []
        invalid_lower = invalid_service.lower()
        
        # Look for partial matches in valid services
        for valid_service in available_services:
            if (invalid_lower in valid_service.lower() or 
                valid_service.lower() in invalid_lower or
                any(part in valid_service.lower() for part in invalid_lower.split('_'))):
                service_suggestions.append(valid_service)
        
        # Also check aliases
        if invalid_lower in SERVICE_NAME_ALIASES:
            suggested = SERVICE_NAME_ALIASES[invalid_lower]
            if suggested in available_services and suggested not in service_suggestions:
                service_suggestions.append(suggested)
        
        if service_suggestions:
            suggestions[invalid_service] = service_suggestions[:3]  # Limit to top 3 suggestions
    
    # Build error message
    error_parts = [
        f"Invalid services in '{category_display}': {', '.join(invalid_services)}.",
        f"Available services include: {', '.join(available_services)}"
    ]
    
    if suggestions:
        suggestion_text = []
        for invalid, suggested in suggestions.items():
            suggestion_text.append(f"'{invalid}' -> try: {', '.join(suggested)}")
        error_parts.append(f"Suggestions: {'; '.join(suggestion_text)}")
    
    return " | ".join(error_parts)

# Example usage and testing
if __name__ == "__main__":
    # Test the validation with common mistakes
    test_categories = {
        "compute_services": ["app_service", "kubernetes", "vm", "invalid_service"],
        "database_services": ["sql", "cosmosdb", "azure_database"],
        "monitoring_services": ["azure_monitor", "app_insights"],
        "security_services": ["keyvault", "azure_ad", "nonexistent_service"]
    }
    
    result = validate_and_correct_services(test_categories)
    
    print("Validation Results:")
    print("==================")
    print(f"Corrected Services: {result['corrected_services']}")
    print(f"Corrections Made: {result['corrections_made']}")
    print(f"Has Errors: {result['has_errors']}")
    
    if result['validation_errors']:
        print("\nValidation Errors:")
        for category, error_info in result['validation_errors'].items():
            error_msg = create_helpful_error_message(
                category, 
                error_info['invalid_services'], 
                error_info['available_services']
            )
            print(f"- {error_msg}")