# Figma API Integration - Fallback Mechanism

## Overview

The Azure Landing Zone Agent now includes a robust Figma API integration with an automatic fallback mechanism to the Python Diagrams library. This ensures that diagram generation always succeeds, even when the Figma API is unavailable or misconfigured.

## How It Works

### Primary Path: Figma API
1. **Token Validation**: The system validates the provided Figma API token
2. **Service Mapping**: Customer inputs are mapped to the internal service catalog
3. **Layout Generation**: A layout graph is created based on requirements
4. **Figma Rendering**: The diagram is rendered directly in Figma using the API

### Fallback Path: Python Diagrams
1. **Automatic Trigger**: When Figma API fails for any reason, the system automatically falls back
2. **Local Rendering**: Uses the Python Diagrams library with Graphviz for rendering
3. **File Generation**: Creates a PNG diagram file in the local file system
4. **Metadata Indication**: The response clearly indicates that fallback was used

## Key Features

### 🔄 Automatic Fallback
- No manual intervention required
- Seamless transition when Figma API fails
- Comprehensive error logging for debugging

### ✅ Input Validation
- Validates Figma API tokens before attempting to render
- Checks for required parameters (file ID, token)
- Maps customer service names to internal catalog names

### 🛡️ Error Handling
- Descriptive error messages for common issues
- Validation of architecture patterns
- Graceful handling of missing dependencies

### 📊 Response Metadata
- `is_fallback` flag indicates if fallback was used
- `diagram_format` shows the output format
- Detailed metadata for tracking and debugging

## Usage Examples

### Successful Fallback Response
```json
{
  "success": true,
  "figma_url": "Figma rendering failed. Diagram generated using fallback method: docs/diagrams/architecture_fallback.png",
  "figma_file_id": "test-file-id",
  "page_name": "Test Architecture",
  "pattern": "ha-multiregion",
  "user_info": null,
  "is_fallback": true,
  "metadata": {
    "generated_at": "2025-09-17T08:30:24.015585",
    "version": "1.0.0",
    "agent": "Azure Landing Zone Agent - Figma Integration",
    "diagram_format": "PNG fallback format"
  }
}
```

### Error Response for Missing Token
```json
{
  "detail": "Error generating Figma diagram: Figma API token is required for Figma rendering. Please provide a valid Figma API token or use the standard diagram generation endpoint."
}
```

## Service Name Mapping

The system automatically maps customer-friendly service names to internal catalog names:

| Customer Input | Internal Catalog |
|----------------|------------------|
| `virtual_machines` | `vm` |
| `virtual_network` | `vnet` |
| `storage_accounts` | `storage_account` |
| `app_services` | `web_app` |
| `function_apps` | `function_app` |
| `sql_database` | `sql_database` |
| `key_vault` | `key_vault` |

## Testing

Use the provided test script to validate the fallback mechanism:

```bash
python test_fallback_mechanism.py
```

This comprehensive test validates:
- Fallback mechanism functionality
- Error handling for edge cases
- File generation and metadata
- Service name mapping

## Benefits

1. **Reliability**: Diagram generation never fails completely
2. **Flexibility**: Works with or without Figma credentials
3. **User Experience**: Clear feedback about which method was used
4. **Debugging**: Detailed error messages and logging
5. **Compatibility**: Supports existing customer input formats

## Common Issues and Solutions

### Issue: Invalid Figma API Token
**Solution**: The system automatically falls back to Python Diagrams and clearly indicates this in the response.

### Issue: Missing Graphviz
**Solution**: Ensure Graphviz is installed (`sudo apt-get install graphviz`) for the fallback mechanism to work.

### Issue: Service Name Not Found
**Solution**: Check the service name mapping table above and use the correct customer input names.

## Architecture Benefits

This implementation provides:
- **Fault Tolerance**: Multiple rendering paths ensure success
- **Scalability**: Can handle high loads with local fallback
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new service mappings or patterns