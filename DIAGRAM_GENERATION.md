# Azure Landing Zone Agent - Professional Diagram Generation

## Overview

The Azure Landing Zone Agent now supports **enterprise-style Azure architecture diagrams** with official Microsoft Azure icons and professional styling, addressing all requirements for professional Azure architectural visualization.

## Professional Diagram Generation (ENHANCED - RECOMMENDED) 

**Endpoint:** `POST /generate-azure-diagram`

- ✅ **Official Microsoft Azure icons and stencils**
- ✅ **Professional Hub-Spoke architecture with proper sections**
- ✅ **Azure Bastion, Azure Firewall, VPN Gateway, and Azure Monitor integration**
- ✅ **Professional line styles** (dotted for VNet peering, solid for direct connections, colored for diagnostics)
- ✅ **Official Azure color scheme and Segoe UI typography**
- ✅ **Clear section organization** (Hub VNet, Spoke VNets, Cross-premises Network)
- ✅ **Azure branding and professional labels**
- ✅ **Industry-standard Azure Landing Zone visualization**

**Key Architectural Sections:**
- **Cross-premises Network**: VPN Gateway/ExpressRoute connectivity
- **Hub Virtual Network**: Shared services with Azure Bastion and Firewall
- **Spoke Virtual Networks**: Production and Non-Production environments
- **Management & Governance**: Subscription and management group hierarchy
- **Identity & Security**: Azure AD and Key Vault integration

**Professional Styling Features:**
- Official Azure color palette (#0078d4, #005a9e, #d83b01, etc.)
- Microsoft Segoe UI typography
- Orthogonal line routing with proper spacing
- Professional clustering with Azure-branded backgrounds
- Enhanced visual hierarchy with proper margins and spacing

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
- Basic clustering without proper Azure sections
- Limited visual hierarchy and generic styling
- Missing key Azure network components
- Basic connection patterns without professional line styles

**After (Enhanced Professional Approach):**
- **Professional Azure Hub-Spoke Architecture**:
  - Cross-premises Network section with VPN Gateway/ExpressRoute
  - Hub Virtual Network with Azure Bastion and Firewall
  - Separate Production and Non-Production Spoke VNets
  - Management & Governance with proper subscription hierarchy
  - Identity & Security dedicated section
- **Official Microsoft Azure styling**:
  - Azure color palette (#0078d4, #005a9e, #d83b01, #107c10)
  - Segoe UI typography (Microsoft standard)
  - Professional clustering with Azure-branded backgrounds
- **Professional connection patterns**:
  - Dotted lines for VNet peering connections
  - Solid lines for direct connections (color-coded by type)
  - Dashed lines for monitoring and diagnostics
- **Enhanced network components**:
  - Azure Bastion for secure access
  - Azure Firewall for centralized security
  - Azure Monitor for comprehensive diagnostics
  - Proper cross-premises connectivity options
- **Industry-standard architectural clarity**:
  - Orthogonal line routing for clean appearance
  - Optimized spacing and visual hierarchy
  - Professional labeling and Azure branding

## File Output

Generated diagrams are saved as PNG files with:
- High resolution for professional presentations
- Proper Azure branding and styling
- File sizes typically 150-300KB
- Suitable for documentation and architecture reviews

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