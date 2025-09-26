# Azure Landing Zone Agent

Professional Azure Landing Zone Architecture Generator with **Intelligent AI-Powered Diagram Generation**.

## 🎯 Key Features

### 🧠 **NEW: Intelligent Architecture Diagram Generator**
- **Natural Language Processing**: Generate diagrams from simple text descriptions
- **LangChain Orchestration**: Advanced AI workflow management for complex requirements
- **OpenAI LLM Integration**: Intelligent parsing and code generation (with fallback mode)
- **Enterprise Review Agent**: Automated compliance auditing against enterprise standards
- **Smart Service Detection**: Automatically identify required Azure services from descriptions

### 📋 **Traditional Features**
- **Enterprise-Grade Diagrams**: Generate Azure architecture diagrams with official Microsoft Azure icons
- **Multiple Output Formats**: PNG diagrams with Python Diagrams library and Draw.io XML
- **Professional Documentation**: Technical Specification Document (TSD), High-Level Design (HLD), and Low-Level Design (LLD)
- **Azure Architecture Templates**: Support for multiple Azure Landing Zone patterns
- **API-Driven**: RESTful API with comprehensive endpoints

## 🚀 Quick Start

### Prerequisites
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y graphviz graphviz-dev

# REQUIRED: Set OpenAI API key for intelligent diagram generation
# The intelligent diagram generator requires a valid OpenAI API key
# Get your API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="your-openai-api-key"
```

⚠️ **Important**: The intelligent diagram generation feature requires a valid OpenAI API key. Without it, the `/generate-intelligent-diagram` endpoint will return a 503 error. Traditional diagram generation endpoints will still work without the API key.
```

### Backend Server
```bash
cd backend
pip3 install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8001
```

### Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```

**Access Points:**
- **Backend API**: http://127.0.0.1:8001
- **Frontend UI**: http://localhost:5173  
- **API Documentation**: http://127.0.0.1:8001/docs

## 🧠 Intelligent Diagram Generation

### 🚀 **NEW: LangGraph Hub-Spoke Orchestration**
Advanced multi-agent workflow for Azure Landing Zone architecture that clearly separates hub and spoke components:

```bash
curl -X POST "http://127.0.0.1:8001/generate-hub-spoke-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Enterprise e-commerce platform",
    "network_services": ["azure_firewall", "bastion", "vpn_gateway"],
    "compute_services": ["app_services", "aks"],
    "database_services": ["sql_database", "cosmos_db"],
    "security_services": ["security_center", "key_vault"],
    "scalability": "high",
    "security_posture": "zero_trust"
  }'
```

**Key Features:**
- **Hub Agent**: Manages shared services (firewall, bastion, DNS, security center, monitoring)
- **Spoke Agent**: Manages workload services (app services, databases, storage, compute)
- **Sequential Execution**: Hub → Spoke → Merge with intelligent context passing
- **Network Topology**: Automated VNet design with proper CIDR allocation
- **Service Categorization**: Intelligent classification of Azure services
- **Enhanced Diagrams**: Clear visual separation in Mermaid and Draw.io outputs

### Simple Usage
```bash
curl -X POST "http://127.0.0.1:8001/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a web application with high availability, secure database storage, and identity management for enterprise use"
  }'
```

### Advanced Example
```bash
curl -X POST "http://127.0.0.1:8001/generate-intelligent-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Design a microservices architecture using Kubernetes with auto-scaling, API management, monitoring, and secure data storage for a financial services application requiring GDPR compliance"
  }'
```

### Test All Features
```bash
# Run comprehensive test suite
./test_intelligent_generator.sh
```

## 📊 What Makes It Intelligent?

### Natural Language Understanding
Convert requirements like:
> *"Create a secure web application with auto-scaling and database backend"*

Into professional Azure architecture diagrams with:
- ✅ App Services for web hosting
- ✅ Application Gateway for load balancing  
- ✅ SQL Database for data storage
- ✅ Key Vault for secrets management
- ✅ Active Directory for identity
- ✅ Proper security zones and connections

### Enterprise Review Agent
Every generated diagram is automatically reviewed against enterprise standards:
- **Compliance Score**: 0-100 rating with detailed feedback
- **Security Validation**: Ensures proper security controls
- **Best Practices**: Validates Azure Well-Architected Framework
- **Missing Elements**: Identifies gaps and provides recommendations

## 🛠️ API Endpoints

### **NEW: LangGraph Orchestration**
| Endpoint | Description |
|----------|-------------|
| `POST /generate-hub-spoke-diagram` | **Multi-agent hub-spoke architecture generation** |

### Intelligent Generation
| Endpoint | Description |
|----------|-------------|
| `POST /generate-intelligent-diagram` | Generate from natural language |
| `POST /enhance-diagram` | Enhance existing diagrams |

### Traditional Generation  
| Endpoint | Description |
|----------|-------------|
| `POST /generate-azure-diagram` | Structured input diagram |
| `POST /generate-comprehensive-azure-architecture` | Full diagram suite |
| `POST /generate-interactive-azure-architecture` | Interactive SVG |

### Utilities
| Endpoint | Description |
|----------|-------------|
| `GET /health` | System health check |
| `GET /templates` | Available templates |
| `GET /services` | Azure services catalog |

## 🏗️ Architecture Support

The system supports comprehensive Azure services with intelligent detection:

### Compute Services
- **Virtual Machines**: Scalable compute instances
- **App Services**: Managed web application hosting  
- **AKS**: Kubernetes container orchestration
- **Functions**: Serverless compute
- **Container Instances**: Simple container deployment

### Network & Security
- **Virtual Networks**: Network isolation and segmentation
- **Application Gateway**: Web application firewall and load balancer
- **Firewall**: Network security and traffic filtering
- **VPN Gateway**: Hybrid connectivity
- **Key Vault**: Secrets and certificate management
- **Active Directory**: Identity and access management

### Data & Storage
- **SQL Database**: Managed relational database
- **Cosmos DB**: Global distributed NoSQL database
- **Storage Accounts**: Blob, file, and queue storage
- **Data Lake**: Big data analytics storage
- **Synapse Analytics**: Data warehousing and analytics

### Integration & DevOps
- **API Management**: API gateway and management
- **Logic Apps**: Workflow automation
- **Service Bus**: Enterprise messaging
- **DevOps**: CI/CD pipelines and repositories
- **Monitor**: Application and infrastructure monitoring

## 🔧 Configuration

### Environment Variables
```bash
# Required for enhanced AI features
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Custom output directory  
export DIAGRAM_OUTPUT_DIR="/custom/output/path"
```

### AI Mode Configuration
- **With OpenAI API Key**: Full AI-powered natural language processing
- **Without API Key**: Intelligent mock mode with pattern-based parsing
- **Hybrid Mode**: Graceful fallback if AI services are unavailable

## 📚 Documentation

### Core Documentation
- **[INTELLIGENT_DIAGRAM_GENERATOR.md](INTELLIGENT_DIAGRAM_GENERATOR.md)** - Complete AI features guide
- **[DIAGRAM_GENERATION.md](DIAGRAM_GENERATION.md)** - Traditional diagram generation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Tests
- **[test_intelligent_generator.sh](test_intelligent_generator.sh)** - Comprehensive AI feature testing
- **[test_functionality.sh](test_functionality.sh)** - Traditional feature testing

## 💡 Usage Examples

### Example 1: E-commerce Platform
```bash
# Natural language input
"Build an e-commerce platform with microservices architecture, auto-scaling, 
secure payment processing, and real-time analytics"

# Automatically generates:
# - AKS cluster for microservices
# - Application Gateway for load balancing
# - SQL Database for transaction data
# - Cosmos DB for catalog data  
# - Key Vault for payment secrets
# - API Management for service orchestration
# - Application Insights for monitoring
```

### Example 2: Data Analytics Solution
```bash
# Natural language input  
"Create a data analytics platform with real-time streaming, 
machine learning, and interactive dashboards"

# Automatically generates:
# - Event Hubs for data ingestion
# - Stream Analytics for real-time processing
# - Data Lake for raw data storage
# - Synapse Analytics for data warehousing
# - Databricks for machine learning
# - Power BI for visualization
```

### Example 3: Enterprise Web Application
```bash
# Natural language input
"Design a secure enterprise web application with high availability,
identity management, and compliance for healthcare data"

# Automatically generates:
# - App Services with availability zones
# - Application Gateway with WAF
# - SQL Database with encryption
# - Active Directory for SSO
# - Key Vault for certificates
# - Security Center for compliance monitoring
```

## 🎯 Enterprise Features

### Compliance & Governance
- **Azure Well-Architected Framework**: Automated validation
- **Security Standards**: Built-in security best practices  
- **Compliance Scoring**: 0-100 rating with detailed feedback
- **Audit Trail**: Complete generation and review history

### Professional Output
- **Official Azure Icons**: Authentic Microsoft branding
- **Enterprise Styling**: Boxed sections, proper clustering
- **Multiple Formats**: PNG, SVG, Draw.io XML export
- **High Resolution**: Presentation and documentation ready

### Extensibility
- **Custom Templates**: Define your own architecture patterns
- **Service Extensions**: Add new Azure services easily
- **Review Rules**: Customize enterprise compliance rules
- **Integration Ready**: REST API for external tool integration

## 🚨 Troubleshooting

### Common Issues

**"Intelligent diagram generator not available"**
```bash
# Check server logs for initialization errors
# Ensure all dependencies are installed
pip3 install -r requirements.txt
```

**"Requirements text too short"**
```bash
# Provide at least 10 characters of meaningful requirements
# Example: "Web app with database" (minimum)
# Better: "Secure web application with SQL database and user authentication"
```

**"Generated diagram file not found"**
```bash
# Check output directory permissions
ls -la /tmp/

# Verify disk space
df -h /tmp/

# Check Graphviz installation
dot -V
```

**Low compliance scores**
```bash
# Add security components: "with secure authentication and encryption"
# Include monitoring: "with comprehensive monitoring and logging"  
# Specify availability: "with high availability and disaster recovery"
```

### Performance Optimization
- Use structured requirements for faster processing
- Enable caching for repeated similar requests
- Set reasonable timeouts for complex diagrams
- Monitor resource usage during peak loads

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd AZ-LZ-Agent

# Setup backend
cd backend
pip3 install -r requirements.txt

# Setup frontend  
cd ../frontend
npm install

# Run tests
./test_intelligent_generator.sh
```

### Adding New Features
1. **New Azure Services**: Update service mappings in `intelligent_diagram_generator.py`
2. **Custom Templates**: Add patterns to architecture templates
3. **Review Rules**: Extend enterprise checklist in review agent
4. **AI Providers**: Add new LLM integrations to orchestrator

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

- **Documentation**: Complete guides in `/docs` directory
- **API Reference**: Available at `http://127.0.0.1:8001/docs`
- **Examples**: Test scripts and sample requests included
- **Issues**: Report bugs and feature requests via GitHub issues

---

*Revolutionizing Azure architecture design with intelligent AI-powered diagram generation*