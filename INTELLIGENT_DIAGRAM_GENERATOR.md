# Intelligent Architecture Diagram Generator

## Overview

The Azure Landing Zone Agent now includes an **Intelligent Architecture Diagram Generator** that uses natural language processing and AI to create professional Azure architecture diagrams from simple text descriptions.

## Key Features

### 🧠 Natural Language Processing
- **Parse Requirements**: Convert natural language architecture requirements into structured data
- **Intelligent Service Detection**: Automatically identify required Azure services from descriptions
- **Context Understanding**: Extract business objectives, technical requirements, and compliance needs

### 🎨 Professional Diagram Generation
- **Official Azure Icons**: Uses authentic Microsoft Azure icons and branding
- **Enterprise Styling**: Boxed sections, proper clustering, and professional layout
- **Smart Connections**: Intelligent workflow arrows and data flow visualization
- **Multiple Formats**: PNG and SVG output with high resolution

### ✅ Enterprise Review Agent
- **Compliance Auditing**: Reviews generated diagrams against enterprise standards
- **Security Validation**: Ensures proper security controls are included
- **Best Practices**: Validates Azure Well-Architected Framework principles
- **Scoring System**: Provides compliance scores (0-100) with detailed feedback

### 🔧 LangChain Orchestration
- **Workflow Management**: Orchestrates multiple AI calls for complex processing
- **Error Handling**: Graceful fallbacks when AI services are unavailable
- **Extensible Design**: Easy to add new AI providers and capabilities

## API Endpoints

### Generate Intelligent Diagram
```http
POST /generate-intelligent-diagram
Content-Type: application/json

{
  "requirements": "Build a web application with high availability, secure database storage, and identity management for enterprise use."
}
```

**Response:**
```json
{
  "success": true,
  "requirements_processed": "Build a web application...",
  "generated_code": "from diagrams import Diagram...",
  "description": "Architecture diagram for: Enterprise web application",
  "review_comments": [
    "Add proper clustering for logical groupings",
    "Consider backup and disaster recovery for data services"
  ],
  "enterprise_compliance_score": 85,
  "diagram_path": "/tmp/azure_architecture_intelligent.png",
  "diagram_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "execution_error": null,
  "intelligent_features": {
    "natural_language_parsing": true,
    "enterprise_review": true,
    "code_generation": true,
    "compliance_scoring": true
  },
  "metadata": {
    "generated_at": "2025-09-22T10:20:00",
    "agent": "Intelligent Azure Architecture Generator",
    "llm_mode": "mock"
  }
}
```

### Enhance Existing Diagram
```http
POST /enhance-diagram
Content-Type: application/json

{
  "existing_code": "from diagrams import Diagram...",
  "enhancement_requirements": "Add monitoring and backup capabilities"
}
```

## Usage Examples

### Example 1: Simple Web Application
```bash
curl -X POST "http://localhost:8001/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Create a simple web application with database backend and user authentication"
  }'
```

### Example 2: Enterprise Microservices
```bash
curl -X POST "http://localhost:8001/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Design a microservices architecture using Kubernetes with auto-scaling, API management, monitoring, and secure data storage for a financial services application requiring GDPR compliance"
  }'
```

### Example 3: Data Analytics Platform
```bash
curl -X POST "http://localhost:8001/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a data analytics platform with data ingestion, processing, machine learning capabilities, and real-time dashboards with high security and compliance"
  }'
```

## Natural Language Capabilities

The system intelligently parses various requirement patterns:

### Business Objectives
- "Create an e-commerce platform"
- "Build a data analytics solution" 
- "Modernize legacy applications"

### Technical Requirements
- "High availability and scalability"
- "Microservices architecture"
- "Auto-scaling capabilities"
- "Performance optimization"

### Security Requirements
- "Secure authentication and authorization"
- "Data encryption at rest and in transit"
- "Network security and firewalls"
- "Zero-trust architecture"

### Compliance Requirements
- "GDPR compliance for data privacy"
- "HIPAA compliance for healthcare"
- "SOC 2 compliance for security"

### Azure Services
The system automatically detects and suggests Azure services:
- **Web/Apps**: App Services, AKS, Virtual Machines
- **Database**: SQL Database, Cosmos DB, MySQL, PostgreSQL
- **Storage**: Storage Accounts, Blob Storage, Data Lake
- **Security**: Key Vault, Active Directory, Firewall
- **Analytics**: Synapse, Data Factory, Databricks
- **Integration**: Logic Apps, API Management, Service Bus

## Enterprise Review Checklist

The review agent evaluates diagrams against:

### ✅ Architecture Standards
- Official Azure icons and branding
- Proper clustering and visual hierarchy
- Clear data flow and connections
- Appropriate service selection

### 🔒 Security Controls
- Identity and access management
- Network security and segmentation
- Data encryption and key management
- Security monitoring and logging

### 🏢 Enterprise Requirements
- High availability design patterns
- Disaster recovery planning
- Compliance with regulations
- Cost optimization considerations

### 📊 Well-Architected Framework
- Reliability and availability
- Security and compliance
- Performance efficiency
- Cost optimization
- Operational excellence

## Configuration

### OpenAI Integration
Set the OpenAI API key for enhanced AI capabilities:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

Without an API key, the system uses intelligent mock responses that still provide valuable diagram generation.

### Environment Variables
```bash
# Optional: OpenAI API key for enhanced AI features
OPENAI_API_KEY=your-openai-api-key

# Optional: Custom output directory
DIAGRAM_OUTPUT_DIR=/custom/output/path
```

## Advanced Features

### Smart Service Detection
The system uses intelligent pattern matching to detect required services:

```text
Input: "web application with database"
Detected: app_services, sql_database, application_gateway

Input: "kubernetes microservices with monitoring"
Detected: aks, api_management, monitoring, storage_accounts

Input: "data analytics with machine learning"
Detected: synapse, data_factory, databricks, storage_accounts
```

### Compliance Scoring
Each generated diagram receives a compliance score:
- **90-100**: Excellent - Enterprise ready
- **80-89**: Good - Minor improvements needed
- **70-79**: Acceptable - Several improvements recommended
- **Below 70**: Needs work - Significant issues to address

### Error Handling
- Graceful degradation when AI services are unavailable
- Intelligent fallbacks for code generation
- Detailed error messages and recommendations
- Timeout protection for long-running operations

## Integration with Existing Features

The intelligent diagram generator works alongside existing capabilities:

### Legacy Endpoints
- `/generate-azure-diagram` - Traditional structured input
- `/generate-comprehensive-azure-architecture` - Full diagram suite
- `/generate-interactive-azure-architecture` - Interactive SVG diagrams

### Combined Workflows
1. Use intelligent generation for initial architecture
2. Enhance with traditional endpoints for refinement
3. Download in multiple formats (PNG, SVG, Draw.io XML)
4. Generate professional documentation (TSD, HLD, LLD)

## Limitations and Considerations

### Current Limitations
- Mock mode when OpenAI API key not provided
- Limited to predefined Azure service mappings
- Code execution in sandboxed environment for security

### Future Enhancements
- Support for multi-cloud architectures
- Custom service definitions
- Integration with Azure Resource Manager templates
- Real-time collaboration features

## Security Considerations

### Code Execution Safety
- Sandboxed execution environment
- Limited Python built-ins access
- Safe file system operations
- Timeout protection

### API Security
- Input validation and sanitization
- Rate limiting capabilities
- Secure API key handling
- Error message sanitization

## Support and Troubleshooting

### Common Issues

**Issue**: "Requirements text too short"
**Solution**: Provide at least 10 characters of meaningful requirements

**Issue**: "Intelligent diagram generator not available"
**Solution**: Check server logs for initialization errors

**Issue**: "Generated diagram file not found"
**Solution**: Verify output directory permissions and disk space

### Debug Information
Enable debug logging to see detailed processing:
```python
import logging
logging.getLogger('intelligent_diagram_generator').setLevel(logging.DEBUG)
```

## Examples Gallery

See the `/examples` directory for sample requirements and generated diagrams demonstrating various architecture patterns and enterprise use cases.

---

*This intelligent diagram generator represents a significant advancement in Azure architecture design, combining the power of natural language processing with enterprise-grade diagram generation capabilities.*