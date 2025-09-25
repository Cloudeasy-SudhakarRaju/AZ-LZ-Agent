# Azure Landing Zone Agent - Diagram Generation

## Overview

The Azure Landing Zone Agent now supports **enterprise-style Azure architecture diagrams** with official Microsoft Azure icons and stencils, addressing the previous issue where diagrams used emoji icons instead of proper Azure architectural styling.

## Diagram Generation Options

### 1. Python Diagrams with Official Azure Icons (NEW - RECOMMENDED) 

**Endpoint:** `POST /generate-azure-diagram`

- ✅ **Official Microsoft Azure icons and stencils**
- ✅ **Enterprise-style architectural diagrams**
- ✅ **High-quality PNG output with proper color coding**
- ✅ **Industry-standard Azure Landing Zone visualization**
- ✅ **Graphviz-powered professional rendering**

**Features:**
- Uses the Python Diagrams library (https://diagrams.mingrammer.com)
- Official Azure node components for all service categories
- Professional clustering and visual hierarchy
- Proper enterprise architectural styling
- Base64 encoded response for web integration
- File download support

### 2. Legacy Options (Still Available)

**Mermaid Diagrams:** `POST /generate-diagram` - Text-based diagrams with emoji icons
**Draw.io XML:** `POST /generate-drawio` - XML format for Draw.io editor

## API Usage

### Generate Azure Architecture Diagram

```bash
curl -X POST "http://localhost:8000/generate-azure-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Enterprise cloud transformation",
    "org_structure": "Enterprise",
    "network_model": "hub-spoke",
    "security_posture": "zero-trust",
    "compute_services": ["virtual_machines", "aks", "app_services"],
    "network_services": ["virtual_network", "firewall", "application_gateway"],
    "storage_services": ["storage_accounts", "blob_storage"],
    "database_services": ["sql_database", "cosmos_db"],
    "security_services": ["key_vault", "active_directory", "security_center"],
    "analytics_services": ["synapse", "data_factory"],
    "integration_services": ["logic_apps", "api_management"],
    "devops_services": ["devops"]
  }'
```

### Response Format

```json
{
  "success": true,
  "diagram_path": "/tmp/azure_landing_zone_20240912_120000.png",
  "diagram_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "tsd": "# Technical Specification Document...",
  "hld": "# High Level Design...",
  "lld": "# Low Level Design...",
  "architecture_template": {...},
  "metadata": {
    "generated_at": "2024-09-12T12:00:00.000000",
    "version": "1.0.0",
    "agent": "Azure Landing Zone Agent - Python Diagrams",
    "diagram_format": "PNG with Azure official icons"
  }
}
```

## Dependencies

The new functionality requires:

- `diagrams==0.23.4` - Python Diagrams library
- `graphviz==0.20.1` - Python Graphviz wrapper  
- System Graphviz installation (`apt-get install graphviz graphviz-dev`)

## Azure Service Support

The system supports official Azure icons for:

- **Compute:** Virtual Machines, AKS, App Services, Functions, Container Instances
- **Network:** Virtual Networks, Firewall, Application Gateway, Load Balancers, VPN Gateway
- **Storage:** Storage Accounts, Blob Storage, Data Lake Storage
- **Database:** SQL Database, Cosmos DB, MySQL, PostgreSQL
- **Security:** Key Vault, Active Directory, Security Center, Sentinel
- **Analytics:** Synapse Analytics, Data Factory, Databricks, Stream Analytics
- **Integration:** Logic Apps, Service Bus, Event Grid, API Management
- **DevOps:** Azure DevOps, Pipelines

## Visual Improvements

**Before (Old Approach):**
- Emoji icons: 🖥️ ☸️ 🌐 🛡️ 🔐
- Basic text-based diagrams
- Limited visual hierarchy

**After (New Approach):**
- Official Microsoft Azure icons
- Professional enterprise styling
- Proper color coding and visual hierarchy
- Industry-standard architectural diagrams
- High-quality PNG rendering

## File Output

Generated diagrams are saved as PNG files with:
- High resolution for professional presentations
- Proper Azure branding and styling
- File sizes typically 150-300KB
- Suitable for documentation and architecture reviews

## Enterprise Resource Auto-Inclusion

The Azure Landing Zone Agent automatically includes enterprise-critical resources in diagrams to ensure compliance with Azure best practices.

### Auto-Included Enterprise Resources

The following resources are automatically included when not explicitly specified by the user:

- **Azure Key Vault**: Secrets, keys, and certificate management
- **Azure Active Directory**: Identity and access management
- **Azure Firewall**: Network security and traffic filtering
- **Azure Monitor**: Observability, logging, and alerting

### Configuration Modes

#### `auto_when_missing` (Default)
- Includes enterprise resources only when they are not already specified by the user
- Provides compliance without being intrusive
- Recommended for most use cases

#### `always_include`
- Always includes enterprise resources regardless of user input
- Ensures maximum compliance and consistency
- Recommended for highly regulated environments

#### `never_auto_include`
- Never automatically includes enterprise resources
- Only includes what the user explicitly specifies
- Provides maximum user control

### Enhanced Connections

When `show_enterprise_connections` is enabled (default), the system creates explicit visual connections:

- **Key Vault → VNets**: For VM secret access
- **Active Directory → VNets**: For authentication services
- **Azure Firewall → VNets**: For security filtering
- **Security Services Interconnection**: Shows integrated security architecture

### API Usage with Enterprise Resources

```bash
# Use default auto-inclusion behavior
curl -X POST "http://localhost:8000/generate-azure-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Web application deployment",
    "compute_services": ["virtual_machines"],
    "network_services": ["virtual_network"],
    "enterprise_resources_mode": "auto_when_missing",
    "show_enterprise_connections": true
  }'
```

```bash
# Always include enterprise resources
curl -X POST "http://localhost:8000/generate-azure-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Enterprise application",
    "compute_services": ["aks"],
    "enterprise_resources_mode": "always_include",
    "show_enterprise_connections": true
  }'
```

### User Prompt Information

Get the enterprise resource configuration prompt:

```bash
curl -X GET "http://localhost:8000/enterprise-resources-prompt"
```

This returns information about available modes, resource descriptions, and default settings to help users configure their preferences.

### Enhanced Response Format

When enterprise resources are auto-included, the response includes additional information:

```json
{
  "success": true,
  "diagram_base64": "...",
  "enterprise_resources": {
    "auto_included": true,
    "resources": ["key_vault", "active_directory", "firewall", "monitor"],
    "prompt": "Would you like to always include these enterprise resources...",
    "current_mode": "auto_when_missing",
    "show_connections": true
  },
  "metadata": {...}
}
```

## Troubleshooting

### Draw.io XML Issues

**Problem**: "Not a diagram file (error on line 1 at column 1: Start tag expected, '<' not found)" when uploading to app.diagrams.net

**Solution**: This issue was resolved in version 1.0.0. The problem was caused by emoji characters being used as shape names in the XML (e.g., `shape=mxgraph.azure.☸️`). The fix replaced emoji icons with valid Draw.io shape names (e.g., `shape=mxgraph.azure.kubernetes_service`).

**Testing**: To verify your generated .drawio file is valid:
```bash
# Test with AKS workload
curl -X POST http://localhost:8001/generate-drawio \
  -H "Content-Type: application/json" \
  -d '{"workload": "aks"}' \
  --output diagram.drawio

# Verify XML structure
python3 -c "import xml.etree.ElementTree as ET; ET.parse('diagram.drawio'); print('✅ Valid XML')"
```

The generated XML should contain proper shape references like:
- `shape=mxgraph.azure.kubernetes_service` ✅
- NOT `shape=mxgraph.azure.☸️` ❌