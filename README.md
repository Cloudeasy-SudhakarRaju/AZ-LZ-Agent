# Azure Landing Zone Agent

An intelligent web application that helps customers design Azure Landing Zones by collecting requirements and automatically generating architectural diagrams and documentation.

## 🏗️ Architecture

- **Backend**: FastAPI Python application that generates diagrams and documentation
- **Frontend**: React + TypeScript + Vite application with Chakra UI for customer input collection

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

The backend API will be available at: `http://127.0.0.1:8001`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend application will be available at: `http://localhost:5173`

## 🎯 Usage

1. **Start the Backend**: Run the FastAPI server first
2. **Start the Frontend**: Run the React development server
3. **Open the Application**: Navigate to `http://localhost:5173` in your browser
4. **Fill Customer Requirements**: Complete the form with customer needs across 9 domains:
   - Business & Compliance
   - Organization
   - Networking & Connectivity
   - Security
   - Workloads
   - Operations
   - Cost
   - Migration
   - Customer Preferences
5. **Generate Architecture**: Click "Generate Architecture" to create diagrams and documentation

## 📊 Output

The application generates:

- **Mermaid Diagram**: Interactive network topology diagram
- **Draw.io XML**: Exportable diagram for further editing
- **TSD (Technical Solution Document)**: High-level solution overview
- **HLD (High Level Design)**: Architecture design document
- **LLD (Low Level Design)**: Detailed implementation guide

## 🛠️ API Endpoints

### POST `/generate-diagram`
Generates all diagram types and documentation based on customer inputs.

**Request Body:**
```json
{
  "business_objective": "cost",
  "regulatory": "GDPR", 
  "network_model": "hub-spoke",
  "workload": "aks",
  "security_posture": "zero-trust"
}
```

**Response:**
```json
{
  "mermaid": "graph TD...",
  "drawio": "<mxfile>...",
  "tsd": "TSD: Generated with objective cost",
  "hld": "HLD: Topology = hub-spoke", 
  "lld": "LLD: Workload = aks, Identity = Azure AD"
}
```

### POST `/generate-drawio`
Returns only the Draw.io XML for direct import.

## 🏗️ Customer Input Domains

1. **Business & Compliance**: Objectives, regulatory requirements
2. **Organization**: Tenant structure, subscriptions
3. **Networking**: Hub-spoke, mesh, Virtual WAN models
4. **Security**: Zero-trust, SIEM/SOAR integration
5. **Workloads**: AKS, App Services, VMs, SAP, AI/ML, Data & Analytics
6. **Operations**: Centralized vs federated models
7. **Cost**: Optimization priorities
8. **Migration**: New workloads vs lift-and-shift
9. **Preferences**: IaC tools (Terraform, Bicep, ARM)

## 🧪 Testing the API

Test the backend directly:

```bash
curl -X POST "http://127.0.0.1:8001/generate-diagram" \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "cost",
    "regulatory": "GDPR",
    "network_model": "hub-spoke", 
    "workload": "aks"
  }'
```

## 🔧 Development

### Backend Development
```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --host 127.0.0.1 --port 8001 --reload

# The API docs will be available at http://127.0.0.1:8001/docs
```

### Frontend Development
```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## 📝 Notes

- The backend runs on port 8001 by default
- The frontend expects the backend to be available at `http://127.0.0.1:8001`
- CORS is enabled for development (should be restricted in production)
- The application generates Azure-specific architectural patterns and best practices

## 🚀 What Should You Do? Execute!

Yes, you should execute this application! Follow these steps:

1. **Install Dependencies**: Run the setup commands above
2. **Start Backend**: `uvicorn main:app --host 127.0.0.1 --port 8001 --reload`
3. **Start Frontend**: `npm run dev`
4. **Open Browser**: Go to `http://localhost:5173`
5. **Design Landing Zones**: Input customer requirements and generate Azure architectures!

The application is now ready to help you design Azure Landing Zones automatically based on customer requirements.