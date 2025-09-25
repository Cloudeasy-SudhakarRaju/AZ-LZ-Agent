"""
Azure Landing Zone Architecture Validation and Diagram Generation

This module provides comprehensive validation rules and diagram generation utilities
for Azure Landing Zone architectures. It validates resources against security, 
compliance, monitoring, and governance requirements while preparing structured
output for diagram generation.

Features:
- Comprehensive validation rules for Azure services
- Individual resource validation with actionable feedback
- Full architecture validation with detailed reporting
- Diagram structure generation for UI visualization
- Integration with existing backend workflow
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass, field
from enum import Enum
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ValidationIssue:
    """Represents a validation issue with detailed information"""
    resource_name: str
    resource_type: str
    issue_type: str
    severity: ValidationSeverity
    message: str
    recommendation: str
    rule_id: str
    compliance_impact: Optional[str] = None

@dataclass
class ValidationResult:
    """Represents the result of architecture validation"""
    passed: bool
    total_resources: int
    issues_count: int
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    compliance_score: float = 0.0

@dataclass
class DiagramNode:
    """Represents a node in the diagram structure"""
    id: str
    name: str
    type: str
    category: str
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    hub_spoke_role: Optional[str] = None  # 'hub', 'spoke', 'shared'

@dataclass
class DiagramConnection:
    """Represents a connection between diagram nodes"""
    source_id: str
    target_id: str
    connection_type: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiagramStructure:
    """Complete diagram structure for visualization"""
    nodes: List[DiagramNode] = field(default_factory=list)
    connections: List[DiagramConnection] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Comprehensive Azure Landing Zone validation rules
AZ_LZ_RULES = {
    "VM": {
        "placement": {
            "required_subnet": ["private", "protected"],
            "avoid_subnet": ["public", "dmz"],
            "required_vnet": True,
            "availability_zone": "recommended",
            "rule_id": "VM001"
        },
        "security": {
            "network_security_group": "required",
            "backup_enabled": "required",
            "disk_encryption": "required",
            "antimalware": "recommended",
            "vulnerability_assessment": "required",
            "rule_id": "VM002"
        },
        "monitoring": {
            "azure_monitor": "required",
            "log_analytics": "required",
            "diagnostic_settings": "required",
            "alerts_configured": "recommended",
            "rule_id": "VM003"
        },
        "governance": {
            "tags_required": ["environment", "project", "owner"],
            "naming_convention": "required",
            "resource_group": "required",
            "rbac": "required",
            "rule_id": "VM004"
        }
    },
    "SQL": {
        "placement": {
            "private_endpoint": "required",
            "vnet_integration": "required",
            "subnet_delegation": "recommended",
            "rule_id": "SQL001"
        },
        "security": {
            "public_access": "forbidden",
            "firewall_rules": "restrictive",
            "encryption_at_rest": "required",
            "encryption_in_transit": "required",
            "advanced_threat_protection": "required",
            "vulnerability_assessment": "required",
            "rule_id": "SQL002"
        },
        "monitoring": {
            "auditing": "required",
            "diagnostic_logs": "required",
            "performance_insights": "recommended",
            "alerts_configured": "required",
            "rule_id": "SQL003"
        },
        "governance": {
            "backup_retention": "30_days_minimum",
            "geo_redundancy": "recommended",
            "access_reviews": "required",
            "rule_id": "SQL004"
        }
    },
    "AKS": {
        "placement": {
            "private_cluster": "required",
            "system_node_pool": "required",
            "availability_zones": "required",
            "rule_id": "AKS001"
        },
        "security": {
            "network_policy": "required",
            "pod_security": "required",
            "rbac_enabled": "required",
            "aad_integration": "required",
            "secret_management": "key_vault",
            "image_scanning": "required",
            "rule_id": "AKS002"
        },
        "monitoring": {
            "container_insights": "required",
            "prometheus_metrics": "recommended",
            "log_aggregation": "required",
            "rule_id": "AKS003"
        },
        "governance": {
            "resource_quotas": "required",
            "network_policies": "required",
            "admission_controllers": "required",
            "rule_id": "AKS004"
        }
    },
    "Storage": {
        "placement": {
            "private_endpoint": "required",
            "network_acls": "required",
            "rule_id": "STG001"
        },
        "security": {
            "public_blob_access": "forbidden",
            "https_only": "required",
            "min_tls_version": "1.2",
            "encryption_at_rest": "required",
            "access_keys_rotation": "required",
            "rule_id": "STG002"
        },
        "monitoring": {
            "storage_analytics": "required",
            "diagnostic_logs": "required",
            "metrics_enabled": "required",
            "rule_id": "STG003"
        },
        "governance": {
            "lifecycle_management": "recommended",
            "immutable_storage": "recommended",
            "access_tier_optimization": "required",
            "rule_id": "STG004"
        }
    },
    "AppService": {
        "placement": {
            "vnet_integration": "required",
            "private_endpoint": "required",
            "rule_id": "APP001"
        },
        "security": {
            "https_only": "required",
            "client_certificates": "recommended",
            "managed_identity": "required",
            "authentication": "required",
            "rule_id": "APP002"
        },
        "monitoring": {
            "application_insights": "required",
            "diagnostic_logs": "required",
            "availability_tests": "recommended",
            "rule_id": "APP003"
        },
        "governance": {
            "deployment_slots": "recommended",
            "auto_scaling": "recommended",
            "backup_strategy": "required",
            "rule_id": "APP004"
        }
    },
    "Firewall": {
        "placement": {
            "hub_vnet": "required",
            "dedicated_subnet": "AzureFirewallSubnet",
            "availability_zones": "required",
            "rule_id": "FW001"
        },
        "security": {
            "threat_intelligence": "required",
            "dns_proxy": "required",
            "rule_collections": "required",
            "forced_tunneling": "recommended",
            "rule_id": "FW002"
        },
        "monitoring": {
            "diagnostic_logs": "required",
            "firewall_workbook": "recommended",
            "alerts_configured": "required",
            "rule_id": "FW003"
        },
        "governance": {
            "policy_management": "required",
            "rule_hierarchy": "required",
            "change_management": "required",
            "rule_id": "FW004"
        }
    },
    "Redis": {
        "placement": {
            "private_endpoint": "required",
            "vnet_integration": "required",
            "rule_id": "REDIS001"
        },
        "security": {
            "access_keys": "required",
            "ssl_only": "required",
            "firewall_rules": "required",
            "rule_id": "REDIS002"
        },
        "monitoring": {
            "diagnostic_logs": "required",
            "performance_counters": "required",
            "alerts_configured": "recommended",
            "rule_id": "REDIS003"
        },
        "governance": {
            "backup_enabled": "required",
            "patch_schedule": "required",
            "scaling_policy": "recommended",
            "rule_id": "REDIS004"
        }
    },
    "CosmosDB": {
        "placement": {
            "private_endpoint": "required",
            "multi_region": "recommended",
            "rule_id": "COSMOS001"
        },
        "security": {
            "public_network_access": "forbidden",
            "encryption_at_rest": "required",
            "key_vault_integration": "required",
            "firewall_enabled": "required",
            "rule_id": "COSMOS002"
        },
        "monitoring": {
            "diagnostic_logs": "required",
            "metrics_enabled": "required",
            "insights_enabled": "recommended",
            "rule_id": "COSMOS003"
        },
        "governance": {
            "backup_policy": "required",
            "consistency_level": "defined",
            "throughput_optimization": "required",
            "rule_id": "COSMOS004"
        }
    }
}

def validate_resource(resource: Dict[str, Any], resource_type: str, architecture_context: Dict[str, Any] = None) -> List[ValidationIssue]:
    """
    Validates a single resource against its rule set and returns actionable errors.
    
    Args:
        resource: Resource configuration dictionary
        resource_type: Type of Azure resource (VM, SQL, AKS, etc.)
        architecture_context: Overall architecture context for cross-resource validation
        
    Returns:
        List of ValidationIssue objects with actionable feedback
    """
    issues = []
    resource_name = resource.get('name', 'Unknown')
    
    # Get rules for this resource type (handle common variations)
    resource_type_normalized = resource_type.upper()
    
    # Handle common resource type variations and normalize to rule keys
    type_mappings = {
        'STORAGE': 'Storage',
        'STORAGE_ACCOUNT': 'Storage', 
        'STORAGEACCOUNT': 'Storage',
        'FIREWALL': 'Firewall',
        'AZURE_FIREWALL': 'Firewall',
        'AZUREFIREWALL': 'Firewall',
        'VIRTUAL_MACHINE': 'VM',
        'VIRTUALMACHINE': 'VM',
        'SQL_DATABASE': 'SQL',
        'SQLDATABASE': 'SQL',
        'APP_SERVICE': 'AppService',
        'APPSERVICE': 'AppService',
        'COSMOS_DB': 'CosmosDB',
        'COSMOSDB': 'CosmosDB',
        'REDIS_CACHE': 'Redis',
        'REDISCACHE': 'Redis'
    }
    
    # First try exact match, then try mapped version
    rules = AZ_LZ_RULES.get(resource_type_normalized)
    if not rules and resource_type_normalized in type_mappings:
        mapped_type = type_mappings[resource_type_normalized]
        rules = AZ_LZ_RULES.get(mapped_type)
        resource_type_normalized = mapped_type
    
    if not rules:
        logger.warning(f"No validation rules defined for resource type: {resource_type} (normalized: {resource_type_normalized})")
        return issues
    
    # Validate placement requirements
    if 'placement' in rules:
        issues.extend(_validate_placement(resource, resource_name, resource_type, rules['placement'], architecture_context))
    
    # Validate security requirements
    if 'security' in rules:
        issues.extend(_validate_security(resource, resource_name, resource_type, rules['security']))
    
    # Validate monitoring requirements
    if 'monitoring' in rules:
        issues.extend(_validate_monitoring(resource, resource_name, resource_type, rules['monitoring']))
    
    # Validate governance requirements
    if 'governance' in rules:
        issues.extend(_validate_governance(resource, resource_name, resource_type, rules['governance']))
    
    return issues

def _validate_placement(resource: Dict[str, Any], resource_name: str, resource_type: str, 
                       placement_rules: Dict[str, Any], architecture_context: Dict[str, Any] = None) -> List[ValidationIssue]:
    """Validate resource placement requirements"""
    issues = []
    
    # Check required subnet types
    if 'required_subnet' in placement_rules:
        required_subnets = placement_rules['required_subnet']
        if isinstance(required_subnets, str):
            required_subnets = [required_subnets]
        
        resource_subnet = resource.get('subnet', '').lower()
        if not any(req_subnet in resource_subnet for req_subnet in required_subnets):
            issues.append(ValidationIssue(
                resource_name=resource_name,
                resource_type=resource_type,
                issue_type="placement",
                severity=ValidationSeverity.HIGH,
                message=f"Resource must be placed in one of: {', '.join(required_subnets)}",
                recommendation=f"Move {resource_name} to a private/protected subnet for security",
                rule_id=placement_rules.get('rule_id', 'UNKNOWN'),
                compliance_impact="Security - Network segmentation"
            ))
    
    # Check forbidden subnet types
    if 'avoid_subnet' in placement_rules:
        avoid_subnets = placement_rules['avoid_subnet']
        if isinstance(avoid_subnets, str):
            avoid_subnets = [avoid_subnets]
        
        resource_subnet = resource.get('subnet', '').lower()
        if any(avoid_subnet in resource_subnet for avoid_subnet in avoid_subnets):
            issues.append(ValidationIssue(
                resource_name=resource_name,
                resource_type=resource_type,
                issue_type="placement",
                severity=ValidationSeverity.CRITICAL,
                message=f"Resource must not be in: {', '.join(avoid_subnets)} subnets",
                recommendation=f"Move {resource_name} to a secure, private subnet",
                rule_id=placement_rules.get('rule_id', 'UNKNOWN'),
                compliance_impact="Security - Public exposure risk"
            ))
    
    # Check VNet requirement
    if placement_rules.get('required_vnet') and not resource.get('vnet'):
        issues.append(ValidationIssue(
            resource_name=resource_name,
            resource_type=resource_type,
            issue_type="placement",
            severity=ValidationSeverity.HIGH,
            message="Resource must be deployed within a Virtual Network",
            recommendation=f"Deploy {resource_name} in a dedicated VNet with proper network segmentation",
            rule_id=placement_rules.get('rule_id', 'UNKNOWN'),
            compliance_impact="Network isolation and security"
        ))
    
    # Check availability zone configuration
    if placement_rules.get('availability_zone') == 'required' and not resource.get('availability_zones'):
        issues.append(ValidationIssue(
            resource_name=resource_name,
            resource_type=resource_type,
            issue_type="placement",
            severity=ValidationSeverity.MEDIUM,
            message="Resource should be configured with availability zones for high availability",
            recommendation=f"Enable availability zones for {resource_name} to ensure resilience",
            rule_id=placement_rules.get('rule_id', 'UNKNOWN'),
            compliance_impact="Availability and disaster recovery"
        ))
    
    return issues

def _validate_security(resource: Dict[str, Any], resource_name: str, resource_type: str, 
                      security_rules: Dict[str, Any]) -> List[ValidationIssue]:
    """Validate security requirements"""
    issues = []
    
    # Check forbidden configurations
    for rule_key, rule_value in security_rules.items():
        if rule_value == "forbidden":
            if resource.get(rule_key, False):
                issues.append(ValidationIssue(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    issue_type="security",
                    severity=ValidationSeverity.CRITICAL,
                    message=f"{rule_key.replace('_', ' ').title()} must be disabled",
                    recommendation=f"Disable {rule_key.replace('_', ' ')} on {resource_name} for security",
                    rule_id=security_rules.get('rule_id', 'UNKNOWN'),
                    compliance_impact="Security - Data exposure risk"
                ))
    
    # Check required security features
    required_features = {
        'network_security_group': 'Network Security Group',
        'backup_enabled': 'Backup',
        'disk_encryption': 'Disk Encryption',
        'encryption_at_rest': 'Encryption at Rest',
        'encryption_in_transit': 'Encryption in Transit',
        'advanced_threat_protection': 'Advanced Threat Protection',
        'vulnerability_assessment': 'Vulnerability Assessment',
        'https_only': 'HTTPS Only',
        'rbac_enabled': 'Role-Based Access Control',
        'managed_identity': 'Managed Identity',
        'authentication': 'Authentication'
    }
    
    for rule_key, rule_value in security_rules.items():
        if rule_value == "required" and rule_key in required_features:
            if not resource.get(rule_key, False):
                issues.append(ValidationIssue(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    issue_type="security",
                    severity=ValidationSeverity.HIGH,
                    message=f"{required_features[rule_key]} is required but not configured",
                    recommendation=f"Enable {required_features[rule_key]} on {resource_name}",
                    rule_id=security_rules.get('rule_id', 'UNKNOWN'),
                    compliance_impact="Security - Missing protection controls"
                ))
    
    # Check minimum TLS version
    if 'min_tls_version' in security_rules:
        required_tls = security_rules['min_tls_version']
        current_tls = resource.get('tls_version', '1.0')
        if current_tls < required_tls:
            issues.append(ValidationIssue(
                resource_name=resource_name,
                resource_type=resource_type,
                issue_type="security",
                severity=ValidationSeverity.HIGH,
                message=f"Minimum TLS version {required_tls} required, currently {current_tls}",
                recommendation=f"Update TLS version to {required_tls} or higher on {resource_name}",
                rule_id=security_rules.get('rule_id', 'UNKNOWN'),
                compliance_impact="Security - Encryption standards"
            ))
    
    return issues

def _validate_monitoring(resource: Dict[str, Any], resource_name: str, resource_type: str, 
                        monitoring_rules: Dict[str, Any]) -> List[ValidationIssue]:
    """Validate monitoring and observability requirements"""
    issues = []
    
    required_monitoring = {
        'azure_monitor': 'Azure Monitor',
        'log_analytics': 'Log Analytics',
        'diagnostic_settings': 'Diagnostic Settings',
        'application_insights': 'Application Insights',
        'container_insights': 'Container Insights',
        'auditing': 'SQL Auditing',
        'diagnostic_logs': 'Diagnostic Logs',
        'storage_analytics': 'Storage Analytics',
        'metrics_enabled': 'Metrics Collection'
    }
    
    for rule_key, rule_value in monitoring_rules.items():
        if rule_value == "required" and rule_key in required_monitoring:
            if not resource.get(rule_key, False):
                severity = ValidationSeverity.MEDIUM
                if rule_key in ['diagnostic_logs', 'auditing']:
                    severity = ValidationSeverity.HIGH  # Critical for compliance
                
                issues.append(ValidationIssue(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    issue_type="monitoring",
                    severity=severity,
                    message=f"{required_monitoring[rule_key]} is required but not configured",
                    recommendation=f"Enable {required_monitoring[rule_key]} on {resource_name} for observability",
                    rule_id=monitoring_rules.get('rule_id', 'UNKNOWN'),
                    compliance_impact="Monitoring - Observability and audit trail"
                ))
    
    # Check for recommended monitoring features
    for rule_key, rule_value in monitoring_rules.items():
        if rule_value == "recommended" and rule_key in required_monitoring:
            if not resource.get(rule_key, False):
                issues.append(ValidationIssue(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    issue_type="monitoring",
                    severity=ValidationSeverity.LOW,
                    message=f"{required_monitoring[rule_key]} is recommended for better observability",
                    recommendation=f"Consider enabling {required_monitoring[rule_key]} on {resource_name}",
                    rule_id=monitoring_rules.get('rule_id', 'UNKNOWN'),
                    compliance_impact="Monitoring - Enhanced observability"
                ))
    
    return issues

def _validate_governance(resource: Dict[str, Any], resource_name: str, resource_type: str, 
                        governance_rules: Dict[str, Any]) -> List[ValidationIssue]:
    """Validate governance and compliance requirements"""
    issues = []
    
    # Check required tags
    if 'tags_required' in governance_rules:
        required_tags = governance_rules['tags_required']
        resource_tags = resource.get('tags', {})
        
        for required_tag in required_tags:
            if required_tag not in resource_tags or not resource_tags[required_tag]:
                issues.append(ValidationIssue(
                    resource_name=resource_name,
                    resource_type=resource_type,
                    issue_type="governance",
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Required tag '{required_tag}' is missing or empty",
                    recommendation=f"Add '{required_tag}' tag to {resource_name} for proper governance",
                    rule_id=governance_rules.get('rule_id', 'UNKNOWN'),
                    compliance_impact="Governance - Resource tagging and organization"
                ))
    
    # Check naming convention
    if governance_rules.get('naming_convention') == 'required':
        if not resource.get('follows_naming_convention', False):
            issues.append(ValidationIssue(
                resource_name=resource_name,
                resource_type=resource_type,
                issue_type="governance",
                severity=ValidationSeverity.LOW,
                message="Resource name doesn't follow organizational naming convention",
                recommendation=f"Rename {resource_name} to follow naming standards",
                rule_id=governance_rules.get('rule_id', 'UNKNOWN'),
                compliance_impact="Governance - Naming standardization"
            ))
    
    # Check backup retention
    if 'backup_retention' in governance_rules:
        required_retention = governance_rules['backup_retention']
        current_retention = resource.get('backup_retention_days', 0)
        
        if '30_days_minimum' in required_retention and current_retention < 30:
            issues.append(ValidationIssue(
                resource_name=resource_name,
                resource_type=resource_type,
                issue_type="governance",
                severity=ValidationSeverity.HIGH,
                message=f"Backup retention is {current_retention} days, minimum 30 days required",
                recommendation=f"Set backup retention to at least 30 days for {resource_name}",
                rule_id=governance_rules.get('rule_id', 'UNKNOWN'),
                compliance_impact="Data retention and compliance"
            ))
    
    return issues

def validate_architecture(architecture: Dict[str, Any]) -> ValidationResult:
    """
    Validates all resources in a user-supplied architecture and returns a comprehensive report.
    
    Args:
        architecture: Complete architecture configuration with resources and metadata
        
    Returns:
        ValidationResult with detailed analysis and recommendations
    """
    logger.info("Starting comprehensive architecture validation")
    
    all_issues = []
    total_resources = 0
    
    # Extract resources from architecture
    resources = architecture.get('resources', [])
    if not resources:
        # Try alternative structure
        resources = []
        for category in ['compute', 'network', 'storage', 'database', 'security']:
            category_resources = architecture.get(category, [])
            if category_resources:
                resources.extend(category_resources)
    
    total_resources = len(resources)
    
    # Validate each resource
    for resource in resources:
        resource_type = resource.get('type', 'Unknown')
        resource_issues = validate_resource(resource, resource_type, architecture)
        all_issues.extend(resource_issues)
    
    # Calculate compliance score
    compliance_score = _calculate_compliance_score(all_issues, total_resources)
    
    # Generate summary
    summary = _generate_validation_summary(all_issues, total_resources)
    
    # Create result
    result = ValidationResult(
        passed=len([issue for issue in all_issues if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]) == 0,
        total_resources=total_resources,
        issues_count=len(all_issues),
        issues=all_issues,
        summary=summary,
        compliance_score=compliance_score
    )
    
    logger.info(f"Architecture validation completed. Score: {compliance_score:.1f}%, Issues: {len(all_issues)}")
    return result

def _calculate_compliance_score(issues: List[ValidationIssue], total_resources: int) -> float:
    """Calculate overall compliance score based on issues"""
    if total_resources == 0:
        return 100.0
    
    # Weight issues by severity
    severity_weights = {
        ValidationSeverity.CRITICAL: 20,
        ValidationSeverity.HIGH: 10,
        ValidationSeverity.MEDIUM: 5,
        ValidationSeverity.LOW: 2,
        ValidationSeverity.INFO: 1
    }
    
    total_deductions = sum(severity_weights.get(issue.severity, 1) for issue in issues)
    max_possible_score = total_resources * 20  # Maximum deductions per resource
    
    if max_possible_score == 0:
        return 100.0
    
    score = max(0, 100 - (total_deductions / max_possible_score * 100))
    return round(score, 1)

def _generate_validation_summary(issues: List[ValidationIssue], total_resources: int) -> Dict[str, Any]:
    """Generate comprehensive validation summary"""
    # Group issues by category
    issues_by_category = {}
    issues_by_severity = {}
    issues_by_type = {}
    
    for issue in issues:
        # By category (resource type)
        if issue.resource_type not in issues_by_category:
            issues_by_category[issue.resource_type] = []
        issues_by_category[issue.resource_type].append(issue)
        
        # By severity
        severity_str = issue.severity.value
        if severity_str not in issues_by_severity:
            issues_by_severity[severity_str] = []
        issues_by_severity[severity_str].append(issue)
        
        # By issue type
        if issue.issue_type not in issues_by_type:
            issues_by_type[issue.issue_type] = []
        issues_by_type[issue.issue_type].append(issue)
    
    # Generate recommendations
    top_recommendations = _generate_top_recommendations(issues)
    
    return {
        "total_resources": total_resources,
        "total_issues": len(issues),
        "critical_issues": len([i for i in issues if i.severity == ValidationSeverity.CRITICAL]),
        "high_issues": len([i for i in issues if i.severity == ValidationSeverity.HIGH]),
        "medium_issues": len([i for i in issues if i.severity == ValidationSeverity.MEDIUM]),
        "low_issues": len([i for i in issues if i.severity == ValidationSeverity.LOW]),
        "issues_by_category": {k: len(v) for k, v in issues_by_category.items()},
        "issues_by_type": {k: len(v) for k, v in issues_by_type.items()},
        "top_recommendations": top_recommendations,
        "validation_coverage": {
            "placement": len([i for i in issues if i.issue_type == "placement"]),
            "security": len([i for i in issues if i.issue_type == "security"]),
            "monitoring": len([i for i in issues if i.issue_type == "monitoring"]),
            "governance": len([i for i in issues if i.issue_type == "governance"])
        }
    }

def _generate_top_recommendations(issues: List[ValidationIssue]) -> List[str]:
    """Generate prioritized list of top recommendations"""
    # Group similar recommendations
    recommendation_counts = {}
    for issue in issues:
        if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
            rec = issue.recommendation
            if rec not in recommendation_counts:
                recommendation_counts[rec] = {'count': 0, 'severity': issue.severity}
            recommendation_counts[rec]['count'] += 1
    
    # Sort by severity and frequency
    sorted_recommendations = sorted(
        recommendation_counts.items(),
        key=lambda x: (x[1]['severity'].value, x[1]['count']),
        reverse=True
    )
    
    return [rec[0] for rec in sorted_recommendations[:10]]  # Top 10

def generate_diagram_structure(architecture: Dict[str, Any], validation_result: ValidationResult = None) -> DiagramStructure:
    """
    Produces a structured output for diagram generation, organizing resources into hub and spoke VNets.
    
    Args:
        architecture: Architecture configuration
        validation_result: Optional validation results to include status information
        
    Returns:
        DiagramStructure ready for UI visualization or export to draw.io
    """
    logger.info("Generating diagram structure for visualization")
    
    nodes = []
    connections = []
    
    # Extract resources and organize by hub/spoke
    resources = architecture.get('resources', [])
    hub_resources = []
    spoke_resources = []
    shared_resources = []
    
    # Categorize resources based on type and configuration
    for resource in resources:
        resource_type = resource.get('type', '').lower()
        resource_name = resource.get('name', 'Unknown')
        
        # Normalize resource type for consistent processing
        type_mappings = {
            'storage_account': 'storage',
            'storageaccount': 'storage', 
            'virtual_machine': 'vm',
            'virtualmachine': 'vm',
            'sql_database': 'sql',
            'sqldatabase': 'sql',
            'app_service': 'appservice',
            'appservice': 'appservice',
            'cosmos_db': 'cosmosdb',
            'cosmosdb': 'cosmosdb',
            'azure_firewall': 'firewall',
            'azurefirewall': 'firewall'
        }
        
        normalized_type = type_mappings.get(resource_type, resource_type)
        
        # Hub services (shared infrastructure)
        if normalized_type in ['firewall', 'vpn_gateway', 'expressroute', 'bastion']:
            hub_resources.append(resource)
        # Spoke services (workload-specific)
        elif normalized_type in ['vm', 'aks', 'app_service', 'appservice', 'sql']:
            spoke_resources.append(resource)
        # Shared services
        else:
            shared_resources.append(resource)
    
    # Create hub VNet node
    hub_node = DiagramNode(
        id="hub-vnet",
        name="Hub VNet",
        type="virtual_network",
        category="networking",
        properties={
            "address_space": "10.0.0.0/16",
            "subnets": ["AzureFirewallSubnet", "GatewaySubnet", "BastionSubnet"]
        },
        hub_spoke_role="hub",
        position={"x": 400, "y": 100}
    )
    nodes.append(hub_node)
    
    # Add hub resources
    hub_y_pos = 200
    for i, resource in enumerate(hub_resources):
        node = DiagramNode(
            id=f"hub-{resource.get('name', f'resource-{i}')}".lower().replace(' ', '-'),
            name=resource.get('name', f'Hub Resource {i}'),
            type=resource.get('type', 'unknown'),
            category=_get_resource_category(resource.get('type', '')),
            properties=resource.get('properties', {}),
            hub_spoke_role="hub",
            position={"x": 200 + (i * 150), "y": hub_y_pos}
        )
        nodes.append(node)
        
        # Connect to hub VNet
        connections.append(DiagramConnection(
            source_id="hub-vnet",
            target_id=node.id,
            connection_type="contains",
            properties={"label": "hosts"}
        ))
    
    # Create spoke VNets
    spoke_vnets = []
    spoke_categories = _group_spoke_resources(spoke_resources)
    
    for i, (category, category_resources) in enumerate(spoke_categories.items()):
        spoke_vnet_id = f"spoke-{category}-vnet"
        spoke_node = DiagramNode(
            id=spoke_vnet_id,
            name=f"{category.title()} Spoke VNet",
            type="virtual_network",
            category="networking",
            properties={
                "address_space": f"10.{i+1}.0.0/16",
                "subnets": [f"{category}-subnet"]
            },
            hub_spoke_role="spoke",
            position={"x": 200 + (i * 300), "y": 400}
        )
        nodes.append(spoke_node)
        spoke_vnets.append(spoke_node)
        
        # Connect spoke to hub
        connections.append(DiagramConnection(
            source_id="hub-vnet",
            target_id=spoke_vnet_id,
            connection_type="peering",
            properties={"label": "VNet Peering", "bidirectional": True}
        ))
        
        # Add resources to spoke
        for j, resource in enumerate(category_resources):
            resource_node = DiagramNode(
                id=f"spoke-{category}-{resource.get('name', f'resource-{j}')}".lower().replace(' ', '-'),
                name=resource.get('name', f'{category.title()} Resource {j}'),
                type=resource.get('type', 'unknown'),
                category=_get_resource_category(resource.get('type', '')),
                properties=resource.get('properties', {}),
                hub_spoke_role="spoke",
                position={"x": 150 + (i * 300) + (j * 100), "y": 500}
            )
            
            # Add validation status if available
            if validation_result:
                resource_issues = [issue for issue in validation_result.issues if issue.resource_name == resource.get('name')]
                resource_node.properties['validation_status'] = {
                    'issues_count': len(resource_issues),
                    'has_critical': any(issue.severity == ValidationSeverity.CRITICAL for issue in resource_issues),
                    'has_high': any(issue.severity == ValidationSeverity.HIGH for issue in resource_issues)
                }
            
            nodes.append(resource_node)
            
            # Connect to spoke VNet
            connections.append(DiagramConnection(
                source_id=spoke_vnet_id,
                target_id=resource_node.id,
                connection_type="contains",
                properties={"label": "hosts"}
            ))
    
    # Add shared resources
    for i, resource in enumerate(shared_resources):
        shared_node = DiagramNode(
            id=f"shared-{resource.get('name', f'resource-{i}')}".lower().replace(' ', '-'),
            name=resource.get('name', f'Shared Resource {i}'),
            type=resource.get('type', 'unknown'),
            category=_get_resource_category(resource.get('type', '')),
            properties=resource.get('properties', {}),
            hub_spoke_role="shared",
            position={"x": 50 + (i * 100), "y": 600}
        )
        
        # Add validation status if available
        if validation_result:
            resource_issues = [issue for issue in validation_result.issues if issue.resource_name == resource.get('name')]
            shared_node.properties['validation_status'] = {
                'issues_count': len(resource_issues),
                'has_critical': any(issue.severity == ValidationSeverity.CRITICAL for issue in resource_issues),
                'has_high': any(issue.severity == ValidationSeverity.HIGH for issue in resource_issues)
            }
        
        nodes.append(shared_node)
    
    # Create diagram structure
    diagram = DiagramStructure(
        nodes=nodes,
        connections=connections,
        layout={
            "type": "hub-spoke",
            "hub_position": {"x": 400, "y": 100},
            "spoke_positions": [{"x": 200 + (i * 300), "y": 400} for i in range(len(spoke_vnets))],
            "shared_position": {"x": 50, "y": 600}
        },
        metadata={
            "total_resources": len(resources),
            "hub_resources": len(hub_resources),
            "spoke_resources": len(spoke_resources),
            "shared_resources": len(shared_resources),
            "validation_included": validation_result is not None,
            "generated_at": "2024-01-01T00:00:00Z"  # Would be datetime.utcnow().isoformat() in production
        }
    )
    
    logger.info(f"Diagram structure generated: {len(nodes)} nodes, {len(connections)} connections")
    return diagram

def _get_resource_category(resource_type: str) -> str:
    """Map resource types to categories"""
    category_map = {
        'vm': 'compute',
        'aks': 'compute',
        'app_service': 'compute',
        'virtual_network': 'networking',
        'firewall': 'security',
        'bastion': 'security',
        'sql': 'database',
        'cosmos_db': 'database',
        'storage_account': 'storage',
        'key_vault': 'security'
    }
    return category_map.get(resource_type.lower(), 'other')

def _group_spoke_resources(resources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group spoke resources by category for VNet organization"""
    groups = {}
    
    for resource in resources:
        resource_type = resource.get('type', '').lower()
        category = _get_resource_category(resource_type)
        
        if category not in groups:
            groups[category] = []
        groups[category].append(resource)
    
    return groups

# Example usage and testing
def example_usage():
    """
    Example usage demonstrating the validation and diagram generation functionality
    """
    print("Azure Landing Zone Architecture Validation - Example Usage")
    print("=" * 60)
    
    # Example architecture configuration
    example_architecture = {
        "metadata": {
            "name": "Enterprise Web Application",
            "version": "1.0",
            "compliance_requirements": ["ISO27001", "SOX"]
        },
        "resources": [
            {
                "name": "web-vm-01",
                "type": "VM",
                "subnet": "public-subnet",  # This will trigger a violation
                "vnet": "spoke-web-vnet",
                "availability_zones": False,  # This will trigger a recommendation
                "network_security_group": True,
                "backup_enabled": False,  # This will trigger a violation
                "disk_encryption": True,
                "tags": {"environment": "production", "project": "webapp"}
            },
            {
                "name": "webapp-sql-01",
                "type": "SQL",
                "public_access": True,  # This will trigger a critical violation
                "private_endpoint": False,
                "encryption_at_rest": True,
                "auditing": False,  # This will trigger a violation
                "backup_retention_days": 7,  # This will trigger a violation (min 30)
                "tags": {"environment": "production"}  # Missing required tags
            },
            {
                "name": "webapp-aks-01",
                "type": "AKS",
                "private_cluster": True,
                "rbac_enabled": True,
                "network_policy": False,  # This will trigger a violation
                "container_insights": True,
                "tags": {"environment": "production", "project": "webapp", "owner": "devteam"}
            },
            {
                "name": "webapp-storage-01",
                "type": "STORAGE",
                "public_blob_access": True,  # This will trigger a critical violation
                "https_only": True,
                "private_endpoint": False,  # This will trigger a violation
                "storage_analytics": True,
                "tags": {"environment": "production", "project": "webapp"}
            },
            {
                "name": "hub-firewall-01",
                "type": "FIREWALL",
                "hub_vnet": True,
                "threat_intelligence": True,
                "diagnostic_logs": True,
                "tags": {"environment": "shared", "project": "infrastructure", "owner": "netteam"}
            }
        ]
    }
    
    # Validate architecture
    print("\n1. Validating Architecture...")
    validation_result = validate_architecture(example_architecture)
    
    print(f"   Total Resources: {validation_result.total_resources}")
    print(f"   Compliance Score: {validation_result.compliance_score}%")
    print(f"   Total Issues: {validation_result.issues_count}")
    print(f"   Critical Issues: {validation_result.summary['critical_issues']}")
    print(f"   High Issues: {validation_result.summary['high_issues']}")
    
    # Show top issues
    print("\n2. Top Validation Issues:")
    critical_issues = [issue for issue in validation_result.issues if issue.severity == ValidationSeverity.CRITICAL]
    high_issues = [issue for issue in validation_result.issues if issue.severity == ValidationSeverity.HIGH]
    
    for issue in critical_issues[:3]:  # Top 3 critical
        print(f"   🔴 CRITICAL: {issue.resource_name} - {issue.message}")
        print(f"      → {issue.recommendation}")
    
    for issue in high_issues[:3]:  # Top 3 high
        print(f"   🟡 HIGH: {issue.resource_name} - {issue.message}")
        print(f"      → {issue.recommendation}")
    
    # Generate diagram structure
    print("\n3. Generating Diagram Structure...")
    diagram_structure = generate_diagram_structure(example_architecture, validation_result)
    
    print(f"   Diagram Nodes: {len(diagram_structure.nodes)}")
    print(f"   Connections: {len(diagram_structure.connections)}")
    print(f"   Layout: {diagram_structure.layout['type']}")
    
    # Show diagram nodes by role
    hub_nodes = [node for node in diagram_structure.nodes if node.hub_spoke_role == "hub"]
    spoke_nodes = [node for node in diagram_structure.nodes if node.hub_spoke_role == "spoke"]
    shared_nodes = [node for node in diagram_structure.nodes if node.hub_spoke_role == "shared"]
    
    print(f"   Hub Resources: {len(hub_nodes)}")
    print(f"   Spoke Resources: {len(spoke_nodes)}")
    print(f"   Shared Resources: {len(shared_nodes)}")
    
    # Show validation integration
    validated_nodes = [node for node in diagram_structure.nodes if 'validation_status' in node.properties]
    print(f"   Nodes with Validation Status: {len(validated_nodes)}")
    
    print("\n4. Top Recommendations:")
    for i, recommendation in enumerate(validation_result.summary['top_recommendations'][:5], 1):
        print(f"   {i}. {recommendation}")
    
    print("\n5. Diagram Structure Sample (First 3 Nodes):")
    for node in diagram_structure.nodes[:3]:
        validation_info = ""
        if 'validation_status' in node.properties:
            status = node.properties['validation_status']
            validation_info = f" (Issues: {status['issues_count']})"
        
        print(f"   - {node.name} ({node.type}) - {node.hub_spoke_role.upper()}{validation_info}")
        print(f"     Position: {node.position}")
    
    print("\n✅ Example completed successfully!")
    print("\nThis validation module is ready for integration with the Azure Landing Zone Agent backend.")

if __name__ == "__main__":
    example_usage()