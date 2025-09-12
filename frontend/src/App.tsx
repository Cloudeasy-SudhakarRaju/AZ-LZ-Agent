import * as React from "react";
import { Box, Heading, VStack, HStack, Button, Text, SimpleGrid, Card, Badge, Container } from "@chakra-ui/react";
import { Field } from "@chakra-ui/react";
import { FiCloud, FiSettings, FiMonitor, FiDownload } from "react-icons/fi";
import Mermaid from "./components/Mermaid";

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
        alert("Architecture Generated Successfully!");
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
      
      alert("Draw.io file download started!");
    } catch (err) {
      console.error(err);
      alert("Failed to download Draw.io file.");
    }
  };

  return (
    <Box bg="gray.50" minH="100vh" p="8">
        <Container maxW="7xl">
          <VStack gap="6" align="stretch">
            {/* Header */}
            <Box textAlign="center">
              <Heading size="2xl" color="blue.600" mb="2">
                🏢 Azure Landing Zone Agent
              </Heading>
              <Text fontSize="lg" color="gray.600">
                Professional Azure Architecture Generator with Enterprise Stencils
              </Text>
              <Badge colorScheme="blue" mt="2">Version 1.0.0 - Professional Edition</Badge>
            </Box>

            {/* Progress Indicator */}
            <Box>
              <Text mb="2" fontSize="sm" fontWeight="medium">Configuration Progress</Text>
              <Box bg="gray.200" borderRadius="md" h="3">
                <Box 
                  bg="blue.500" 
                  borderRadius="md" 
                  h="3" 
                  w={`${(Object.keys(formData).length / 15) * 100}%`}
                  transition="width 0.3s"
                />
              </Box>
            </Box>

            {/* Main Content */}
            <SimpleGrid columns={{ base: 1, lg: results ? 2 : 1 }} gap="8">
              
              {/* Input Form */}
              <Card.Root>
                <Card.Header>
                  <Heading size="lg" color="blue.700">
                    ⚙️ Customer Requirements Input
                  </Heading>
                </Card.Header>
                <Card.Body>
                  <VStack gap="6" align="stretch">
                    
                    {/* Business Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">1. Business Requirements</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Primary Business Objective</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.business_objective || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("business_objective", e.target.value)}
                            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', width: '100%' }}
                          >
                            <option value="">Select your primary objective</option>
                            <option value="cost">Cost Optimization</option>
                            <option value="agility">Business Agility</option>
                            <option value="innovation">Innovation & Growth</option>
                            <option value="scalability">Scalability & Performance</option>
                            <option value="security">Security & Compliance</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Industry Vertical</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.industry || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("industry", e.target.value)}
                          >
                            <option value="">Select your industry</option>
                            <option value="financial">Financial Services</option>
                            <option value="healthcare">Healthcare</option>
                            <option value="retail">Retail & E-commerce</option>
                            <option value="manufacturing">Manufacturing</option>
                            <option value="government">Government</option>
                            <option value="technology">Technology</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Organization Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">2. Organization Structure</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Organization Size</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.org_structure || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("org_structure", e.target.value)}
                          >
                            <option value="enterprise">Large Enterprise (10,000+ employees)</option>
                            <option value="medium">Medium Enterprise (1,000-10,000 employees)</option>
                            <option value="small">Small Business (100-1,000 employees)</option>
                            <option value="startup">Startup (&lt; 100 employees)</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Governance Model</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.governance || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("governance", e.target.value)}
                          >
                            <option value="centralized">Centralized (Central IT controls all)</option>
                            <option value="federated">Federated (Shared responsibility)</option>
                            <option value="decentralized">Decentralized (Business unit autonomy)</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Network Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">3. Network & Connectivity</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Network Topology</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.network_model || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("network_model", e.target.value)}
                          >
                            <option value="hub-spoke">Hub-Spoke (Traditional)</option>
                            <option value="vwan">Virtual WAN (Modern)</option>
                            <option value="mesh">Mesh Network</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Connectivity</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.connectivity || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("connectivity", e.target.value)}
                          >
                            <option value="expressroute">ExpressRoute (Private)</option>
                            <option value="vpn">Site-to-Site VPN</option>
                            <option value="internet">Internet Only</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Security Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">4. Security & Identity</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Security Posture</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.security_posture || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("security_posture", e.target.value)}
                          >
                            <option value="zero-trust">Zero Trust Architecture</option>
                            <option value="defense-in-depth">Defense in Depth</option>
                            <option value="compliance-first">Compliance First</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Identity Management</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.identity || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("identity", e.target.value)}
                          >
                            <option value="azure-ad">Azure Active Directory</option>
                            <option value="azure-ad-b2c">Azure AD B2C</option>
                            <option value="hybrid">Hybrid (On-premises + Cloud)</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Workloads Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">5. Workloads & Applications</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Primary Workload</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.workload || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("workload", e.target.value)}
                          >
                            <option value="aks">Azure Kubernetes Service (AKS)</option>
                            <option value="appservices">Azure App Services</option>
                            <option value="vm">Virtual Machines</option>
                            <option value="sap">SAP on Azure</option>
                            <option value="ai">AI/ML Workloads</option>
                            <option value="data">Data & Analytics</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Monitoring Strategy</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.monitoring || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("monitoring", e.target.value)}
                          >
                            <option value="azure-monitor">Azure Monitor Suite</option>
                            <option value="log-analytics">Log Analytics focused</option>
                            <option value="application-insights">Application Insights</option>
                            <option value="third-party">Third-party (Datadog, etc.)</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Operations Section */}
                    <Box>
                      <Heading size="md" color="blue.600" mb="4">6. Operations & Management</Heading>
                      <SimpleGrid columns={2} gap="4">
                        <Box>
                          <Text mb="2" fontWeight="medium">Infrastructure as Code</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.iac || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("iac", e.target.value)}
                          >
                            <option value="bicep">Bicep (Recommended)</option>
                            <option value="arm">ARM Templates</option>
                            <option value="terraform">Terraform</option>
                            <option value="pulumi">Pulumi</option>
                          </select>
                        </Box>
                        
                        <Box>
                          <Text mb="2" fontWeight="medium">Cost Priority</Text>
                          <select style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            style={{ padding: "8px", borderRadius: "4px", border: "1px solid #ccc", width: "100%" }}
                            value={formData.cost_priority || ""}
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange("cost_priority", e.target.value)}
                          >
                            <option value="cost-first">Cost Optimization First</option>
                            <option value="performance-first">Performance First</option>
                            <option value="balanced">Balanced Approach</option>
                          </select>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Generate Button */}
                    <Button
                      colorScheme="blue"
                      size="lg"
                      w="full"
                      onClick={handleSubmit}
                      loading={loading}
                    >
                      🏗️ Generate Azure Landing Zone Architecture
                    </Button>
                  </VStack>
                </Card.Body>
              </Card.Root>

              {/* Results Panel */}
              {results && (
                <Card.Root>
                  <Card.Header>
                    <HStack justify="space-between">
                      <Heading size="lg" color="green.700">
                        📊 Generated Architecture
                      </Heading>
                      <Button
                        onClick={downloadDrawio}
                        colorScheme="blue"
                        variant="outline"
                        size="sm"
                      >
                        📥 Download Draw.io
                      </Button>
                    </HStack>
                  </Card.Header>
                  <Card.Body>
                    <VStack gap="4" align="stretch">
                      <Box p="3" bg="green.50" borderRadius="md" borderLeft="4px solid" borderColor="green.500">
                        <Text fontWeight="bold" color="green.800">Architecture Generated Successfully!</Text>
                        <Text fontSize="sm" color="green.600">
                          Template: {results.architecture_template?.template?.name}
                        </Text>
                      </Box>

                      {/* Tab Navigation */}
                      <Box>
                        <HStack mb="4" borderBottom="1px solid" borderColor="gray.200">
                          {["Diagram", "TSD", "HLD", "LLD"].map((tab, index) => (
                            <Button
                              key={tab}
                              variant={activeTab === index ? "solid" : "ghost"}
                              colorScheme={activeTab === index ? "blue" : "gray"}
                              onClick={() => setActiveTab(index)}
                              size="sm"
                            >
                              {tab}
                            </Button>
                          ))}
                        </HStack>

                        {/* Tab Content */}
                        {activeTab === 0 && (
                          <Box>
                            <Heading size="md" mb="4">🏗️ Azure Landing Zone Architecture Diagram</Heading>
                            <Box 
                              border="1px solid" 
                              borderColor="gray.200" 
                              borderRadius="md" 
                              p="4" 
                              bg="white"
                              maxH="600px"
                              overflowY="auto"
                            >
                              <Mermaid chart={results.mermaid} />
                            </Box>
                          </Box>
                        )}

                        {activeTab === 1 && (
                          <Box>
                            <Heading size="md" mb="4">📘 Technical Specification Document (TSD)</Heading>
                            <Box 
                              border="1px solid" 
                              borderColor="gray.200" 
                              borderRadius="md" 
                              p="4" 
                              bg="white"
                              maxH="600px"
                              overflowY="auto"
                            >
                              <Text whiteSpace="pre-wrap" fontSize="sm" fontFamily="mono">
                                {results.tsd}
                              </Text>
                            </Box>
                          </Box>
                        )}

                        {activeTab === 2 && (
                          <Box>
                            <Heading size="md" mb="4">📗 High Level Design (HLD)</Heading>
                            <Box 
                              border="1px solid" 
                              borderColor="gray.200" 
                              borderRadius="md" 
                              p="4" 
                              bg="white"
                              maxH="600px"
                              overflowY="auto"
                            >
                              <Text whiteSpace="pre-wrap" fontSize="sm" fontFamily="mono">
                                {results.hld}
                              </Text>
                            </Box>
                          </Box>
                        )}

                        {activeTab === 3 && (
                          <Box>
                            <Heading size="md" mb="4">📙 Low Level Design (LLD)</Heading>
                            <Box 
                              border="1px solid" 
                              borderColor="gray.200" 
                              borderRadius="md" 
                              p="4" 
                              bg="white"
                              maxH="600px"
                              overflowY="auto"
                            >
                              <Text whiteSpace="pre-wrap" fontSize="sm" fontFamily="mono">
                                {results.lld}
                              </Text>
                            </Box>
                          </Box>
                        )}
                      </Box>
                    </VStack>
                  </Card.Body>
                </Card.Root>
              )}
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>
  );
}

export default App;