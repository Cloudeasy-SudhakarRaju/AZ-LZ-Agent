import * as React from "react";
import { 
  ChakraProvider, 
  Box, 
  Heading, 
  VStack, 
  HStack, 
  Button, 
  Text, 
  Container, 
  Textarea, 
  useToast, 
  Progress, 
  Card,
  CardBody,
  Badge,
  Spinner,
  Input,
  FormControl,
  FormLabel,
  FormHelperText,
  Select,
  Alert,
  AlertIcon,
  Link
} from "@chakra-ui/react";

import Mermaid from "./components/Mermaid";
import InteractiveSVGViewer from "./components/InteractiveSVGViewer";

interface SimplifiedFormData {
  user_requirements: string;
  generation_method: 'standard' | 'figma';
  figma_api_token?: string;
  figma_file_id?: string;
  figma_page_name?: string;
  fallback_format?: 'png' | 'svg';
}

interface AIAnalysisResult {
  services: string[];
  reasoning: string;
  architecture_pattern: string;
  connectivity_requirements: string;
  security_considerations: string;
  needs_confirmation: boolean;
  suggested_additions: string[];
  follow_up_questions?: string[];
}

interface Results {
  success: boolean;
  mermaid?: string;
  drawio_xml?: string;
  svg_diagram?: string;
  svg_diagram_path?: string;
  figma_url?: string;
  figma_file_id?: string;
  figma_page_name?: string;
  user_info?: any;
  tsd: string;
  hld: string;
  lld: string;
  architecture_template: any;
  metadata: any;
  azure_stencils?: {
    total_used: number;
    unique_used: number;
    stencils_list: string[];
  };
  ai_analysis?: AIAnalysisResult;
  // Figma fallback fields
  download_url?: string;
  is_fallback?: boolean;
  fallback_filename?: string;
  fallback_reason?: string;
}

function SimplifiedApp() {
  const [formData, setFormData] = React.useState<SimplifiedFormData>({
    user_requirements: "",
    generation_method: 'standard',
    fallback_format: 'png'
  });
  const [results, setResults] = React.useState<Results | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [aiAnalysis, setAiAnalysis] = React.useState<AIAnalysisResult | null>(null);
  const [followUpAnswers, setFollowUpAnswers] = React.useState<Record<string, string>>({});
  const [analysisStage, setAnalysisStage] = React.useState<'input' | 'analyzing' | 'clarifying' | 'generating' | 'complete'>('input');
  const toast = useToast();

  const handleRequirementsChange = (value: string) => {
    setFormData({ user_requirements: value });
  };

  const analyzeRequirements = async () => {
    if (!formData.user_requirements.trim()) {
      toast({
        title: "Requirements needed",
        description: "Please describe what you want to build",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setLoading(true);
    setAnalysisStage('analyzing');
    
    try {
      const response = await fetch("http://127.0.0.1:8001/analyze-requirements", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          free_text_input: formData.user_requirements 
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }
      
      const analysis = await response.json();
      setAiAnalysis(analysis);
      
      // Check if AI needs clarification
      if (analysis.needs_confirmation || (analysis.follow_up_questions && analysis.follow_up_questions.length > 0)) {
        setAnalysisStage('clarifying');
      } else {
        // Proceed directly to generation based on selected method
        if (formData.generation_method === 'figma') {
          generateFigmaDiagram(analysis);
        } else {
          generateArchitecture(analysis);
        }
      }
      
    } catch (error) {
      console.error("Analysis error:", error);
      toast({
        title: "Analysis failed",
        description: "Error analyzing your requirements. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      setAnalysisStage('input');
    } finally {
      setLoading(false);
    }
  };

  const handleFollowUpAnswer = (question: string, answer: string) => {
    setFollowUpAnswers(prev => ({ ...prev, [question]: answer }));
  };

  const proceedWithGeneration = async () => {
    if (!aiAnalysis) return;
    
    // Include follow-up answers in the analysis
    const enhancedAnalysis = {
      ...aiAnalysis,
      follow_up_answers: followUpAnswers
    };
    
    // Choose generation method based on user selection
    if (formData.generation_method === 'figma') {
      generateFigmaDiagram(enhancedAnalysis);
    } else {
      generateArchitecture(enhancedAnalysis);
    }
  };

  const generateArchitecture = async (analysis: AIAnalysisResult) => {
    setAnalysisStage('generating');
    setLoading(true);
    
    try {
      // Prepare the request with AI analysis results
      const requestData = {
        free_text_input: formData.user_requirements,
        ai_analysis: analysis,
        follow_up_answers: followUpAnswers
      };

      const response = await fetch("http://127.0.0.1:8001/generate-simplified-architecture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });
      
      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data);
        setAnalysisStage('complete');
        
        toast({
          title: "Architecture Generated!",
          description: `Successfully created architecture with ${data.azure_stencils?.unique_used || 0} Azure services.`,
          status: "success",
          duration: 5000,
          isClosable: true,
        });
      } else {
        throw new Error("Failed to generate architecture");
      }
      
    } catch (error) {
      console.error("Generation error:", error);
      toast({
        title: "Generation failed",
        description: "Error generating architecture. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      setAnalysisStage('input');
    } finally {
      setLoading(false);
    }
  };

  const generateFigmaDiagram = async (analysis: AIAnalysisResult) => {
    setAnalysisStage('generating');
    setLoading(true);
    
    try {
      if (!formData.figma_api_token || !formData.figma_file_id) {
        throw new Error("Figma API token and File ID are required for Figma generation");
      }

      // Convert analysis to customer inputs format
      const customerInputs = {
        business_objective: "Architecture Generation",
        free_text_input: formData.user_requirements,
        compute_services: analysis.services.filter(s => ['virtual_machines', 'app_services', 'function_apps', 'aks'].includes(s)),
        network_services: analysis.services.filter(s => ['virtual_network', 'application_gateway', 'load_balancer', 'firewall'].includes(s)),
        storage_services: analysis.services.filter(s => ['storage_accounts', 'blob_storage'].includes(s)),
        database_services: analysis.services.filter(s => ['sql_database', 'cosmos_db', 'cache_for_redis'].includes(s)),
        security_services: analysis.services.filter(s => ['key_vault', 'active_directory', 'security_center'].includes(s)),
        security_posture: "standard"
      };

      const requestData = {
        customer_inputs: customerInputs,
        figma_api_token: formData.figma_api_token,
        figma_file_id: formData.figma_file_id,
        page_name: formData.figma_page_name || "Azure Architecture",
        pattern: "ha-multiregion",
        fallback_format: formData.fallback_format || "png"
      };

      const response = await fetch("http://127.0.0.1:8001/generate-figma-diagram", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Figma generation failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data);
        setAnalysisStage('complete');
        
        toast({
          title: "Figma Diagram Generated!",
          description: `Successfully created diagram in Figma. View it at the provided link.`,
          status: "success",
          duration: 8000,
          isClosable: true,
        });
      } else {
        throw new Error("Failed to generate Figma diagram");
      }
      
    } catch (error) {
      console.error("Figma generation error:", error);
      toast({
        title: "Figma Generation Failed",
        description: error instanceof Error ? error.message : "Error generating Figma diagram. Please try again.",
        status: "error",
        duration: 8000,
        isClosable: true,
      });
      setAnalysisStage('input');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ 
      user_requirements: "",
      generation_method: 'standard'
    });
    setResults(null);
    setAiAnalysis(null);
    setFollowUpAnswers({});
    setAnalysisStage('input');
  };

  const examplePrompts = [
    "I want to create a hub & spoke architecture with VMs, VNET, security groups, and firewall for a web application",
    "Build a scalable e-commerce platform with microservices on Azure using AKS, databases, and CDN",
    "Design a data analytics solution with data lake, Databricks, and real-time streaming capabilities",
    "Create a secure multi-tier application with load balancing, auto-scaling, and monitoring"
  ];

  return (
    <ChakraProvider>
      <Container maxW="6xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box textAlign="center">
            <Heading size="2xl" color="blue.600" mb={2}>
              Azure Architecture Agent
            </Heading>
            <Text fontSize="lg" color="gray.600">
              Describe your architecture needs in plain English, and I'll design it for you
            </Text>
          </Box>

          {/* Main Input Area */}
          {analysisStage === 'input' && (
            <Card>
              <CardBody>
                <VStack spacing={6}>
                  <Box w="100%">
                    <Text mb={4} fontSize="lg" fontWeight="semibold">
                      What do you want to build?
                    </Text>
                    <Textarea
                      placeholder="Describe your architecture requirements... 

For example:
• I want to create a hub & spoke with VMs, VNET, security groups, and firewall
• Build a scalable web app with databases and load balancing
• Design a data platform with analytics and streaming capabilities"
                      value={formData.user_requirements}
                      onChange={(e) => handleRequirementsChange(e.target.value)}
                      minH="200px"
                      fontSize="md"
                      resize="vertical"
                    />
                  </Box>

                  {/* Generation Method Selection */}
                  <Box w="100%">
                    <FormControl>
                      <FormLabel fontSize="lg" fontWeight="semibold">
                        Diagram Generation Method
                      </FormLabel>
                      <Select
                        value={formData.generation_method}
                        onChange={(e) => setFormData({...formData, generation_method: e.target.value as 'standard' | 'figma'})}
                        size="lg"
                      >
                        <option value="standard">Standard (Python Diagrams)</option>
                        <option value="figma">Figma API Integration</option>
                      </Select>
                      <FormHelperText>
                        {formData.generation_method === 'standard' 
                          ? "Generate PNG/SVG diagrams using Python diagrams library"
                          : "Create diagrams directly in Figma using the Figma API"
                        }
                      </FormHelperText>
                    </FormControl>
                  </Box>

                  {/* Figma Configuration (shown when Figma method selected) */}
                  {formData.generation_method === 'figma' && (
                    <Box w="100%" p={4} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderLeftColor="blue.400">
                      <VStack spacing={4} align="stretch">
                        <Text fontSize="md" fontWeight="semibold" color="blue.700">
                          Figma Configuration
                        </Text>
                        
                        <FormControl isRequired>
                          <FormLabel>Figma API Token</FormLabel>
                          <Input
                            type="password"
                            placeholder="figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                            value={formData.figma_api_token || ''}
                            onChange={(e) => setFormData({...formData, figma_api_token: e.target.value})}
                          />
                          <FormHelperText>
                            Get your token from{' '}
                            <Link href="https://www.figma.com/developers/api#access-tokens" isExternal color="blue.600">
                              Figma Settings → Personal Access Tokens
                            </Link>
                          </FormHelperText>
                        </FormControl>

                        <FormControl isRequired>
                          <FormLabel>Figma File ID</FormLabel>
                          <Input
                            placeholder="e.g., abc123def456ghi789"
                            value={formData.figma_file_id || ''}
                            onChange={(e) => setFormData({...formData, figma_file_id: e.target.value})}
                          />
                          <FormHelperText>
                            Found in the Figma file URL: figma.com/file/[FILE_ID]/file-name
                          </FormHelperText>
                        </FormControl>

                        <FormControl>
                          <FormLabel>Page Name (optional)</FormLabel>
                          <Input
                            placeholder="Azure Architecture"
                            value={formData.figma_page_name || ''}
                            onChange={(e) => setFormData({...formData, figma_page_name: e.target.value})}
                          />
                          <FormHelperText>
                            Name for the diagram page in Figma (defaults to "Azure Architecture")
                          </FormHelperText>
                        </FormControl>

                        <FormControl>
                          <FormLabel>Fallback Format</FormLabel>
                          <Select
                            value={formData.fallback_format || 'png'}
                            onChange={(e) => setFormData({...formData, fallback_format: e.target.value as 'png' | 'svg'})}
                          >
                            <option value="png">PNG (recommended)</option>
                            <option value="svg">SVG (vector format)</option>
                          </Select>
                          <FormHelperText>
                            Format used if Figma is unavailable and fallback diagram is generated
                          </FormHelperText>
                        </FormControl>

                        <Alert status="info" size="sm">
                          <AlertIcon />
                          <Text fontSize="sm">
                            Make sure you have edit access to the Figma file and that your API token has the necessary permissions.
                          </Text>
                        </Alert>
                      </VStack>
                    </Box>
                  )}

                  <Button
                    colorScheme="blue"
                    size="lg"
                    onClick={analyzeRequirements}
                    isDisabled={
                      !formData.user_requirements.trim() || 
                      (formData.generation_method === 'figma' && 
                       (!formData.figma_api_token || !formData.figma_file_id))
                    }
                    width="200px"
                  >
                    🤖 Analyze & Generate
                  </Button>

                  {/* Example Prompts */}
                  <Box w="100%">
                    <Text mb={3} fontSize="sm" color="gray.600">
                      Try these examples:
                    </Text>
                    <VStack spacing={2} align="stretch">
                      {examplePrompts.map((prompt, index) => (
                        <Button
                          key={index}
                          variant="ghost"
                          size="sm"
                          textAlign="left"
                          justifyContent="flex-start"
                          onClick={() => handleRequirementsChange(prompt)}
                          color="blue.600"
                          fontWeight="normal"
                        >
                          {prompt}
                        </Button>
                      ))}
                    </VStack>
                  </Box>
                </VStack>
              </CardBody>
            </Card>
          )}

          {/* Loading States */}
          {loading && (
            <Card>
              <CardBody>
                <VStack spacing={4}>
                  <Spinner size="lg" color="blue.500" />
                  <Text fontSize="lg">
                    {analysisStage === 'analyzing' && "🧠 Analyzing your requirements..."}
                    {analysisStage === 'generating' && "🏗️ Generating your architecture..."}
                  </Text>
                  <Progress value={analysisStage === 'analyzing' ? 30 : 70} colorScheme="blue" w="100%" />
                </VStack>
              </CardBody>
            </Card>
          )}

          {/* AI Analysis Results & Follow-up Questions */}
          {aiAnalysis && analysisStage === 'clarifying' && (
            <Card>
              <CardBody>
                <VStack spacing={6} align="stretch">
                  <Box>
                    <Heading size="md" mb={4}>
                      🤖 I understand you want to build:
                    </Heading>
                    <Text fontSize="md" mb={4}>
                      {aiAnalysis.reasoning}
                    </Text>
                    
                    <HStack spacing={4} wrap="wrap">
                      <Badge colorScheme="blue" p={2}>
                        Pattern: {aiAnalysis.architecture_pattern}
                      </Badge>
                      <Badge colorScheme="green" p={2}>
                        {aiAnalysis.services.length} Services Identified
                      </Badge>
                    </HStack>
                  </Box>

                  {aiAnalysis.follow_up_questions && aiAnalysis.follow_up_questions.length > 0 && (
                    <Box>
                      <Heading size="sm" mb={4}>
                        I need a few more details:
                      </Heading>
                      <VStack spacing={4} align="stretch">
                        {aiAnalysis.follow_up_questions.map((question, index) => (
                          <Box key={index}>
                            <Text mb={2} fontWeight="medium">
                              {question}
                            </Text>
                            <Textarea
                              placeholder="Your answer..."
                              value={followUpAnswers[question] || ""}
                              onChange={(e) => handleFollowUpAnswer(question, e.target.value)}
                              size="sm"
                            />
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  <HStack spacing={4}>
                    <Button colorScheme="blue" onClick={proceedWithGeneration}>
                      Generate Architecture
                    </Button>
                    <Button variant="outline" onClick={resetForm}>
                      Start Over
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          )}

          {/* Results */}
          {results && analysisStage === 'complete' && (
            <VStack spacing={6} align="stretch">
              <Card>
                <CardBody>
                  <HStack justify="space-between" align="center" mb={4}>
                    <Heading size="lg">Your Azure Architecture</Heading>
                    <Button variant="outline" onClick={resetForm}>
                      Create New Architecture
                    </Button>
                  </HStack>
                  
                  {/* Figma Results Display */}
                  {(results.figma_url || results.is_fallback) && (
                    <VStack spacing={4} align="stretch" mb={6}>
                      {results.figma_url ? (
                        <Alert status="success">
                          <AlertIcon />
                          <VStack align="start" spacing={2}>
                            <Text fontWeight="semibold">
                              Diagram created in Figma successfully! 🎨
                            </Text>
                            <Link 
                              href={results.figma_url} 
                              isExternal 
                              color="blue.600" 
                              fontWeight="semibold"
                              fontSize="lg"
                            >
                              🔗 Open in Figma
                            </Link>
                          </VStack>
                        </Alert>
                      ) : results.is_fallback ? (
                        <Alert status="warning">
                          <AlertIcon />
                          <VStack align="start" spacing={3} w="100%">
                            <Text fontWeight="semibold">
                              Figma unavailable - generated downloadable diagram instead! 📊
                            </Text>
                            <Text fontSize="sm" color="orange.700">
                              {results.fallback_reason || "Figma API was not available, but we've created a downloadable diagram for you."}
                            </Text>
                            {results.download_url && (
                              <HStack spacing={3}>
                                <Button
                                  as="a"
                                  href={`http://127.0.0.1:8001${results.download_url}`}
                                  download={results.fallback_filename}
                                  colorScheme="blue"
                                  size="sm"
                                  leftIcon={<span>📥</span>}
                                >
                                  Download {results.fallback_filename?.endsWith('.svg') ? 'SVG' : 'PNG'} Diagram
                                </Button>
                                <Text fontSize="xs" color="gray.600">
                                  Format: {results.fallback_filename?.endsWith('.svg') ? 'SVG' : 'PNG'}
                                </Text>
                              </HStack>
                            )}
                          </VStack>
                        </Alert>
                      ) : null}

                      {results.user_info && (
                        <Box p={3} bg="blue.50" borderRadius="md">
                          <Text fontSize="sm" color="blue.700">
                            <strong>File ID:</strong> {results.figma_file_id}
                          </Text>
                          <Text fontSize="sm" color="blue.700">
                            <strong>Page:</strong> {results.figma_page_name || 'Azure Architecture'}
                          </Text>
                          {results.user_info.name && (
                            <Text fontSize="sm" color="blue.700">
                              <strong>Figma Account:</strong> {results.user_info.name}
                            </Text>
                          )}
                        </Box>
                      )}
                    </VStack>
                  )}
                  
                  {/* Standard diagram results */}
                  {results.svg_diagram && (
                    <Box mb={6}>
                      <InteractiveSVGViewer svgContent={results.svg_diagram} />
                    </Box>
                  )}
                  
                  {results.mermaid && (
                    <Box mb={6}>
                      <Text mb={2} fontWeight="semibold">Architecture Diagram:</Text>
                      <Mermaid chart={results.mermaid} />
                    </Box>
                  )}
                </CardBody>
              </Card>

              {/* Documentation */}
              {(results.tsd || results.hld || results.lld) && (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Documentation</Heading>
                    <VStack spacing={4} align="stretch">
                      {results.tsd && (
                        <Box>
                          <Text fontWeight="semibold" mb={2}>Technical Specification Document</Text>
                          <Box
                            p={4}
                            bg="gray.50"
                            borderRadius="md"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                            maxH="300px"
                            overflowY="auto"
                          >
                            {results.tsd}
                          </Box>
                        </Box>
                      )}
                      
                      {results.hld && (
                        <Box>
                          <Text fontWeight="semibold" mb={2}>High-Level Design</Text>
                          <Box
                            p={4}
                            bg="gray.50"
                            borderRadius="md"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                            maxH="300px"
                            overflowY="auto"
                          >
                            {results.hld}
                          </Box>
                        </Box>
                      )}
                      
                      {results.lld && (
                        <Box>
                          <Text fontWeight="semibold" mb={2}>Low-Level Design</Text>
                          <Box
                            p={4}
                            bg="gray.50"
                            borderRadius="md"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                            maxH="300px"
                            overflowY="auto"
                          >
                            {results.lld}
                          </Box>
                        </Box>
                      )}
                    </VStack>
                  </CardBody>
                </Card>
              )}
            </VStack>
          )}
        </VStack>
      </Container>
    </ChakraProvider>
  );
}

export default SimplifiedApp;