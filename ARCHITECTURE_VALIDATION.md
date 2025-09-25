# Azure Landing Zone Architecture Validation

This document describes the new architecture validation capabilities added to the Azure Landing Zone Agent.

## Overview

The `validate_architecture.py` module provides comprehensive validation and diagram generation capabilities for Azure Landing Zone architectures. It validates resources against security, compliance, monitoring, and governance requirements while preparing structured output for diagram generation.

## Key Features

### 1. Comprehensive Validation Rules (`AZ_LZ_RULES`)
- **VM**: Placement, security (NSG, backup, encryption), monitoring, governance
- **SQL**: Security (no public access, encryption, threat protection), monitoring, governance  
- **AKS**: Security (private cluster, RBAC, network policies), monitoring, governance
- **Storage**: Security (private endpoints, encryption, no public access), monitoring, governance
- **AppService**: Security (HTTPS, managed identity, authentication), monitoring, governance
- **Firewall**: Hub placement, security (threat intelligence), monitoring, governance
- **Redis**: Security (SSL, access keys), monitoring, governance
- **CosmosDB**: Security (private endpoints, encryption), monitoring, governance
- **KeyVault**: Security (private access, soft delete), monitoring, governance

### 2. Validation Functions

#### `validate_resource(resource, resource_type, architecture_context)`
Validates individual resources against their rule sets and returns actionable errors with:
- **Resource name and type**
- **Issue severity** (Critical, High, Medium, Low, Info)
- **Issue category** (placement, security, monitoring, governance)
- **Actionable recommendations**
- **Compliance impact assessment**

#### `validate_architecture(architecture)`
Validates complete architecture and returns comprehensive report with:
- **Compliance score** (0-100%)
- **Issue categorization** and prioritization  
- **Summary statistics** by resource type and issue category
- **Top recommendations** for remediation
- **Validation coverage** metrics

#### `generate_diagram_structure(architecture, validation_result)`
Produces structured output for diagram generation with:
- **Hub-spoke organization** of resources
- **Node positioning** for visualization
- **Connection mapping** between components
- **Validation status** integration for visual feedback
- **Metadata** for rendering systems (draw.io, UI components)

### 3. Backend Integration

#### New API Endpoints

##### `POST /validate-architecture`
Validates architecture from CustomerInputs and returns:
```json
{
  "validation": {
    "compliance_score": 85.2,
    "total_issues": 12,
    "critical_issues": 0,
    "high_issues": 3,
    "issues": [...],
    "summary": {...}
  },
  "diagram_structure": {...},
  "architecture": {...}
}
```

##### `POST /validate-and-generate-diagram`
Combines validation with full diagram generation including:
- Validation results with compliance scoring
- Mermaid diagrams with validation feedback
- Draw.io XML with validation status
- Professional documentation (TSD, HLD, LLD)
- Top recommendations for architecture improvement

#### Integration Features

##### `convert_customer_inputs_to_architecture(inputs)`
Converts CustomerInputs to validation-ready architecture format by:
- **Mapping service selections** to resource configurations
- **Applying security posture** settings (zero-trust, defense-in-depth)
- **Setting compliance requirements** based on regulatory inputs
- **Configuring monitoring** and backup based on selections
- **Applying tagging** and governance policies

##### Security Posture Integration
- **Zero Trust**: All resources configured with private endpoints, no public access
- **Defense in Depth**: Layered security with NSGs, firewalls, and monitoring
- **Compliance-aware**: Automatic configuration based on regulatory requirements

## Usage Examples

### Standalone Module Usage
```python
from validate_architecture import validate_architecture, generate_diagram_structure

# Validate architecture
validation_result = validate_architecture(architecture_config)
print(f"Compliance Score: {validation_result.compliance_score}%")

# Generate diagram structure  
diagram = generate_diagram_structure(architecture_config, validation_result)
```

### API Integration
```bash
# Test validation endpoint
curl -X POST "http://localhost:8001/validate-architecture" \
  -H "Content-Type: application/json" \
  -d '{
    "security_posture": "zero-trust",
    "compute_services": ["virtual_machines"],
    "database_services": ["sql_database"],
    "monitoring": "azure-monitor"
  }'
```

### Validation Results Interpretation

#### Compliance Scores
- **90-100%**: Excellent - Ready for production
- **70-89%**: Good - Minor improvements needed
- **50-69%**: Fair - Significant improvements required  
- **Below 50%**: Poor - Major security/compliance issues

#### Issue Severities
- **Critical**: Security vulnerabilities, compliance violations
- **High**: Important security/monitoring gaps
- **Medium**: Best practice recommendations
- **Low**: Minor improvements, naming conventions
- **Info**: Informational recommendations

## Testing

Run the integration test to verify all functionality:

```bash
# Start backend server
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8001

# Run integration tests
python3 test_validation_integration.py
```

Run standalone module examples:
```bash
python3 validate_architecture.py
```

## Architecture Benefits

### For Development Teams
- **Early validation** of architecture decisions
- **Actionable feedback** with specific recommendations
- **Compliance scoring** for project tracking
- **Integration** with existing development workflows

### for Enterprise Governance  
- **Consistent standards** enforcement across projects
- **Audit trail** of validation results and remediation
- **Compliance reporting** with detailed issue tracking
- **Risk assessment** with severity classification

### For Solution Architects
- **Visual validation** feedback in diagrams
- **Hub-spoke optimization** for network design
- **Security posture** validation and recommendations
- **Documentation generation** with validation context

The validation module seamlessly integrates with the existing Azure Landing Zone Agent while providing powerful new capabilities for ensuring architecture quality and compliance.