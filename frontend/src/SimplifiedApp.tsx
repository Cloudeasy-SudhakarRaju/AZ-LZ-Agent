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
  Spinner
} from "@chakra-ui/react";

import Mermaid from "./components/Mermaid";
import InteractiveSVGViewer from "./components/InteractiveSVGViewer";

interface SimplifiedFormData {
  user_requirements: string;
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
  mermaid: string;
  drawio_xml?: string;
  svg_diagram?: string;
  svg_diagram_path?: string;
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
}

function SimplifiedApp() {
  const [formData, setFormData] = React.useState<SimplifiedFormData>({
    user_requirements: ""
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
        // Proceed directly to generation
        generateArchitecture(analysis);
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
    
    generateArchitecture(enhancedAnalysis);
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

  const resetForm = () => {
    setFormData({ user_requirements: "" });
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

                  <Button
                    colorScheme="blue"
                    size="lg"
                    onClick={analyzeRequirements}
                    isDisabled={!formData.user_requirements.trim()}
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