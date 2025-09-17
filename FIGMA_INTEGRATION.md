# Figma API Integration for Azure Landing Zone Agent

This document describes the new Figma API integration feature that allows generating Azure architecture diagrams directly in Figma.

## Overview

The Azure Landing Zone Agent now supports two diagram generation methods:
1. **Standard (Python Diagrams)** - Generate PNG/SVG diagrams using the Python diagrams library
2. **Figma API Integration** - Create diagrams directly in Figma using the Figma API

## Prerequisites

### Figma Setup

1. **Create a Figma Account**: If you don't have one, sign up at [figma.com](https://www.figma.com)

2. **Generate a Personal Access Token**:
   - Go to [Figma Settings → Personal Access Tokens](https://www.figma.com/developers/api#access-tokens)
   - Click "Create a new token"
   - Give it a descriptive name (e.g., "Azure Landing Zone Agent")
   - Copy the token (it starts with `figd_`)

3. **Create or Identify a Figma File**:
   - Create a new design file or use an existing one
   - Copy the File ID from the URL: `figma.com/file/[FILE_ID]/file-name`

### Environment Variables (Optional)

You can set the Figma API token as an environment variable:

```bash
export FIGMA_API_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Usage

### Backend API

#### Endpoint: POST `/generate-figma-diagram`

**Request Body:**
```json
{
  "customer_inputs": {
    "business_objective": "Enterprise cloud transformation",
    "free_text_input": "I want to create a hub & spoke architecture with VMs, VNET, security groups, and firewall",
    "compute_services": ["virtual_machines", "app_services"],
    "network_services": ["virtual_network", "application_gateway", "firewall"],
    "storage_services": ["storage_accounts"],
    "database_services": ["sql_database"],
    "security_services": ["key_vault", "active_directory"]
  },
  "figma_api_token": "figd_xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "figma_file_id": "abc123def456ghi789",
  "page_name": "Azure Architecture",
  "pattern": "ha-multiregion"
}
```

**Response:**
```json
{
  "success": true,
  "figma_url": "https://www.figma.com/file/abc123def456ghi789",
  "figma_file_id": "abc123def456ghi789",
  "page_name": "Azure Architecture",
  "pattern": "ha-multiregion",
  "user_info": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "metadata": {
    "generated_at": "2025-09-17T07:57:51.973Z",
    "version": "1.0.0",
    "agent": "Azure Landing Zone Agent - Figma Integration",
    "diagram_format": "Figma native format"
  }
}
```

### Frontend Interface

1. **Select Generation Method**: Choose "Figma API Integration" from the dropdown
2. **Configure Figma Settings**:
   - Enter your Figma API Token
   - Provide the target Figma File ID
   - Optionally specify a custom page name
3. **Describe Architecture**: Enter your requirements in plain text
4. **Generate**: Click "Analyze & Generate" to create the diagram

## Features

### Azure Service Support

The Figma renderer supports all major Azure services with proper styling:

- **Compute**: Virtual Machines, App Services, Function Apps, AKS
- **Network**: Virtual Networks, Application Gateway, Load Balancer, Firewall
- **Storage**: Storage Accounts, Blob Storage
- **Database**: SQL Database, Cosmos DB, Redis Cache
- **Security**: Key Vault, Active Directory, Security Center
- **And more...**

### Automatic Layout

- Intelligent node positioning with proper spacing
- Cluster-based grouping for related services
- Connection lines between dependent services
- Azure-branded styling and colors

### Security

- API tokens are handled securely (not stored server-side)
- Validation of Figma credentials before diagram generation
- Error handling for invalid tokens or permissions

## Example Usage

### cURL Example

```bash
curl -X POST "http://localhost:8001/generate-figma-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_inputs": {
      "free_text_input": "Create a web application with load balancer, VMs, database, and storage",
      "compute_services": ["virtual_machines", "app_services"],
      "network_services": ["virtual_network", "load_balancer"],
      "storage_services": ["storage_accounts"],
      "database_services": ["sql_database"],
      "security_services": ["key_vault"]
    },
    "figma_api_token": "figd_your_token_here",
    "figma_file_id": "your_file_id_here",
    "page_name": "Web App Architecture"
  }'
```

### Python Example

```python
import requests

# Configuration
API_URL = "http://localhost:8001/generate-figma-diagram"
FIGMA_TOKEN = "figd_your_token_here"
FIGMA_FILE_ID = "your_file_id_here"

# Request data
data = {
    "customer_inputs": {
        "free_text_input": "I need a scalable e-commerce platform with microservices",
        "compute_services": ["aks", "app_services"],
        "network_services": ["virtual_network", "application_gateway"],
        "storage_services": ["storage_accounts", "blob_storage"],
        "database_services": ["sql_database", "cosmos_db"],
        "security_services": ["key_vault", "active_directory"]
    },
    "figma_api_token": FIGMA_TOKEN,
    "figma_file_id": FIGMA_FILE_ID,
    "page_name": "E-commerce Architecture"
}

# Generate diagram
response = requests.post(API_URL, json=data)
result = response.json()

if result["success"]:
    print(f"Diagram created successfully!")
    print(f"View at: {result['figma_url']}")
else:
    print(f"Error: {result.get('detail', 'Unknown error')}")
```

## Troubleshooting

### Common Issues

1. **Invalid API Token**
   - Error: "Invalid Figma API token"
   - Solution: Generate a new token from Figma settings

2. **File Not Found**
   - Error: "No pages found in Figma file"
   - Solution: Check the File ID and ensure you have access

3. **Permission Denied**
   - Error: API request fails with 403
   - Solution: Ensure your token has edit permissions for the file

4. **Architecture Agent Not Available**
   - Error: "Architecture agent is not available"
   - Solution: Check backend logs for import errors

### Getting Help

- Check the FastAPI docs at `http://localhost:8001/docs`
- Review backend logs for detailed error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Integration Details

### Architecture

The Figma integration consists of:

1. **FigmaRenderer** (`scripts/arch_agent/figma_renderer.py`)
   - Handles Figma API communication
   - Converts layout graphs to Figma elements
   - Manages styling and positioning

2. **Agent Integration** (`scripts/arch_agent/agent.py`)
   - Added `generate_figma_diagram()` method
   - Supports both standard and Figma rendering

3. **API Endpoint** (`backend/main.py`)
   - `/generate-figma-diagram` endpoint
   - Request validation and error handling
   - Integration with existing analysis workflow

4. **Frontend Components** (`frontend/src/SimplifiedApp.tsx`)
   - Method selection interface
   - Figma configuration form
   - Result display with Figma links

This integration maintains backward compatibility while adding powerful new capabilities for cloud-native diagram generation.