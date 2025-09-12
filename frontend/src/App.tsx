import * as React from "react";
import { FiCloud, FiSettings, FiMonitor, FiDownload, FiCheckCircle } from "react-icons/fi";
import Mermaid from "./components/Mermaid";
import "./App.css";

interface FormData {
  business_objective?: string;
  regulatory?: string;
  industry?: string;
  org_structure?: string;
  governance?: string;
  identity?: string;
  connectivity?: string;
  network_model?: string;
  ip_strategy?: string;
  security_zone?: string;
  security_posture?: string;
  key_vault?: string;
  threat_protection?: string;
  workload?: string;
  architecture_style?: string;
  scalability?: string;
  ops_model?: string;
  monitoring?: string;
  backup?: string;
  topology_pattern?: string;
  migration_scope?: string;
  cost_priority?: string;
  iac?: string;
}

interface Results {
  success: boolean;
  mermaid: string;
  drawio: string;
  tsd: string;
  hld: string;
  lld: string;
  architecture_template: any;
  metadata: any;
}

function App() {
  const [formData, setFormData] = React.useState<FormData>({});
  const [results, setResults] = React.useState<Results | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState(0);

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8001/generate-diagram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      if (data.success) {
        setResults(data);
      } else {
        throw new Error("Failed to generate architecture");
      }
    } catch (err) {
      console.error(err);
      alert("Error: Failed to generate architecture. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const downloadDrawio = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8001/generate-drawio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'azure-landing-zone.drawio';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error(err);
      alert("Failed to download Draw.io file.");
    }
  };

  const progressPercentage = Math.min((Object.keys(formData).length / 15) * 100, 100);

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="header-content">
            <div className="title-section">
              <FiCloud className="header-icon" />
              <h1>Azure Landing Zone Agent</h1>
            </div>
            <p className="subtitle">Professional Azure Architecture Generator with Enterprise Stencils</p>
            <span className="version-badge">Version 1.0.0 - Professional Edition</span>
          </div>
        </header>

        {/* Progress */}
        <div className="progress-section">
          <div className="progress-label">Configuration Progress</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progressPercentage}%` }}></div>
          </div>
        </div>

        {/* Main Content */}
        <div className={`main-content ${results ? 'with-results' : ''}`}>
          
          {/* Input Form */}
          <div className="form-panel">
            <div className="panel-header">
              <FiSettings className="panel-icon" />
              <h2>Customer Requirements Input</h2>
            </div>
            
            <div className="form-content">
              
              {/* Business Section */}
              <div className="form-section">
                <h3>1. Business Requirements</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Primary Business Objective</label>
                    <select
                      value={formData.business_objective || ""}
                      onChange={(e) => handleChange("business_objective", e.target.value)}
                    >
                      <option value="">Select your primary objective</option>
                      <option value="cost">Cost Optimization</option>
                      <option value="agility">Business Agility</option>
                      <option value="innovation">Innovation & Growth</option>
                      <option value="scalability">Scalability & Performance</option>
                      <option value="security">Security & Compliance</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Industry Vertical</label>
                    <select
                      value={formData.industry || ""}
                      onChange={(e) => handleChange("industry", e.target.value)}
                    >
                      <option value="">Select your industry</option>
                      <option value="financial">Financial Services</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="retail">Retail & E-commerce</option>
                      <option value="manufacturing">Manufacturing</option>
                      <option value="government">Government</option>
                      <option value="technology">Technology</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Organization Section */}
              <div className="form-section">
                <h3>2. Organization Structure</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Organization Size</label>
                    <select
                      value={formData.org_structure || ""}
                      onChange={(e) => handleChange("org_structure", e.target.value)}
                    >
                      <option value="">Select organization type</option>
                      <option value="enterprise">Large Enterprise (10,000+ employees)</option>
                      <option value="medium">Medium Enterprise (1,000-10,000 employees)</option>
                      <option value="small">Small Business (100-1,000 employees)</option>
                      <option value="startup">Startup (&lt; 100 employees)</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Governance Model</label>
                    <select
                      value={formData.governance || ""}
                      onChange={(e) => handleChange("governance", e.target.value)}
                    >
                      <option value="">Select governance approach</option>
                      <option value="centralized">Centralized (Central IT controls all)</option>
                      <option value="federated">Federated (Shared responsibility)</option>
                      <option value="decentralized">Decentralized (Business unit autonomy)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Network Section */}
              <div className="form-section">
                <h3>3. Network & Connectivity</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Network Topology</label>
                    <select
                      value={formData.network_model || ""}
                      onChange={(e) => handleChange("network_model", e.target.value)}
                    >
                      <option value="">Select network architecture</option>
                      <option value="hub-spoke">Hub-Spoke (Traditional)</option>
                      <option value="vwan">Virtual WAN (Modern)</option>
                      <option value="mesh">Mesh Network</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Connectivity</label>
                    <select
                      value={formData.connectivity || ""}
                      onChange={(e) => handleChange("connectivity", e.target.value)}
                    >
                      <option value="">Select connectivity type</option>
                      <option value="expressroute">ExpressRoute (Private)</option>
                      <option value="vpn">Site-to-Site VPN</option>
                      <option value="internet">Internet Only</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Security Section */}
              <div className="form-section">
                <h3>4. Security & Identity</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Security Posture</label>
                    <select
                      value={formData.security_posture || ""}
                      onChange={(e) => handleChange("security_posture", e.target.value)}
                    >
                      <option value="">Select security approach</option>
                      <option value="zero-trust">Zero Trust Architecture</option>
                      <option value="defense-in-depth">Defense in Depth</option>
                      <option value="compliance-first">Compliance First</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Identity Management</label>
                    <select
                      value={formData.identity || ""}
                      onChange={(e) => handleChange("identity", e.target.value)}
                    >
                      <option value="">Select identity solution</option>
                      <option value="azure-ad">Azure Active Directory</option>
                      <option value="azure-ad-b2c">Azure AD B2C</option>
                      <option value="hybrid">Hybrid (On-premises + Cloud)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Workloads Section */}
              <div className="form-section">
                <h3>5. Workloads & Applications</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Primary Workload</label>
                    <select
                      value={formData.workload || ""}
                      onChange={(e) => handleChange("workload", e.target.value)}
                    >
                      <option value="">Select workload type</option>
                      <option value="aks">Azure Kubernetes Service (AKS)</option>
                      <option value="appservices">Azure App Services</option>
                      <option value="vm">Virtual Machines</option>
                      <option value="sap">SAP on Azure</option>
                      <option value="ai">AI/ML Workloads</option>
                      <option value="data">Data & Analytics</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Monitoring Strategy</label>
                    <select
                      value={formData.monitoring || ""}
                      onChange={(e) => handleChange("monitoring", e.target.value)}
                    >
                      <option value="">Select monitoring approach</option>
                      <option value="azure-monitor">Azure Monitor Suite</option>
                      <option value="log-analytics">Log Analytics focused</option>
                      <option value="application-insights">Application Insights</option>
                      <option value="third-party">Third-party (Datadog, etc.)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Operations Section */}
              <div className="form-section">
                <h3>6. Operations & Management</h3>
                <div className="input-grid">
                  <div className="input-group">
                    <label>Infrastructure as Code</label>
                    <select
                      value={formData.iac || ""}
                      onChange={(e) => handleChange("iac", e.target.value)}
                    >
                      <option value="">Select IaC preference</option>
                      <option value="bicep">Bicep (Recommended)</option>
                      <option value="arm">ARM Templates</option>
                      <option value="terraform">Terraform</option>
                      <option value="pulumi">Pulumi</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label>Cost Priority</label>
                    <select
                      value={formData.cost_priority || ""}
                      onChange={(e) => handleChange("cost_priority", e.target.value)}
                    >
                      <option value="">Select cost approach</option>
                      <option value="cost-first">Cost Optimization First</option>
                      <option value="performance-first">Performance First</option>
                      <option value="balanced">Balanced Approach</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Generate Button */}
              <button
                className={`generate-btn ${loading ? 'loading' : ''}`}
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? (
                  <>🔄 Generating Architecture...</>
                ) : (
                  <>🏗️ Generate Azure Landing Zone Architecture</>
                )}
              </button>
            </div>
          </div>

          {/* Results Panel */}
          {results && (
            <div className="results-panel">
              <div className="panel-header">
                <div className="header-left">
                  <FiCheckCircle className="panel-icon success" />
                  <h2>Generated Architecture</h2>
                </div>
                <button
                  className="download-btn"
                  onClick={downloadDrawio}
                >
                  <FiDownload />
                  Download Draw.io
                </button>
              </div>
              
              <div className="results-content">
                <div className="success-banner">
                  <FiCheckCircle className="success-icon" />
                  <div>
                    <strong>Architecture Generated Successfully!</strong>
                    <div className="template-info">
                      Template: {results.architecture_template?.template?.name}
                    </div>
                  </div>
                </div>

                {/* Tab Navigation */}
                <div className="tab-container">
                  <div className="tab-nav">
                    {["Diagram", "TSD", "HLD", "LLD"].map((tab, index) => (
                      <button
                        key={tab}
                        className={`tab-btn ${activeTab === index ? 'active' : ''}`}
                        onClick={() => setActiveTab(index)}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>

                  {/* Tab Content */}
                  <div className="tab-content">
                    {activeTab === 0 && (
                      <div className="tab-panel">
                        <h4>🏗️ Azure Landing Zone Architecture Diagram</h4>
                        <div className="diagram-container">
                          <Mermaid chart={results.mermaid} />
                        </div>
                      </div>
                    )}

                    {activeTab === 1 && (
                      <div className="tab-panel">
                        <h4>📘 Technical Specification Document (TSD)</h4>
                        <div className="document-container">
                          <pre>{results.tsd}</pre>
                        </div>
                      </div>
                    )}

                    {activeTab === 2 && (
                      <div className="tab-panel">
                        <h4>📗 High Level Design (HLD)</h4>
                        <div className="document-container">
                          <pre>{results.hld}</pre>
                        </div>
                      </div>
                    )}

                    {activeTab === 3 && (
                      <div className="tab-panel">
                        <h4>📙 Low Level Design (LLD)</h4>
                        <div className="document-container">
                          <pre>{results.lld}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;