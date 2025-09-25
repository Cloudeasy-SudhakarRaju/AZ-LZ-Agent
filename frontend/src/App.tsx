import * as React from "react";
import {
  ChakraProvider,
  Box,
  Heading,
  VStack,
  Button,
  Text,
  Container,
  Textarea,
  useToast,
  Card,
  CardHeader,
  CardBody,
  Alert,
  AlertIcon,
  AlertDescription,
  Image,
} from "@chakra-ui/react";

interface IntelligentDiagramResult {
  success: boolean;
  requirements_processed: string;
  generated_code: string;
  description: string;
  review_comments: string[];
  enterprise_compliance_score: number;
  diagram_path?: string;
  diagram_base64?: string;
  execution_error?: string;
  intelligent_features: {
    natural_language_parsing: boolean;
    enterprise_review: boolean;
    code_generation: boolean;
    compliance_scoring: boolean;
  };
  metadata: {
    generated_at: string;
    version: string;
    agent: string;
    llm_mode: string;
  };
}

function App() {
  const [prompt, setPrompt] = React.useState<string>("");
  const [result, setResult] = React.useState<IntelligentDiagramResult | null>(null);
  const [loading, setLoading] = React.useState(false);
  const toast = useToast();

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      toast({
        title: "Input Required",
        description: "Please describe the Azure resources you want to create.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (prompt.length < 10) {
      toast({
        title: "Input Too Short",
        description: "Please provide at least 10 characters describing your requirements.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8001/generate-intelligent-diagram", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          requirements: prompt,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: IntelligentDiagramResult = await response.json();
      setResult(data);

      toast({
        title: "Success!",
        description: "Azure architecture diagram generated successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error generating diagram:", error);
      toast({
        title: "Generation Failed",
        description: error instanceof Error ? error.message : "Failed to generate diagram. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setPrompt("");
    setResult(null);
  };

  return (
    <ChakraProvider>
      <Box bg="gray.50" minH="100vh" p="8">
        <Container maxW="6xl">
          <VStack gap="8" align="stretch">
            {/* Header */}
            <Box textAlign="center">
              <Heading size="2xl" color="blue.600" mb="4">
                🏢 Azure Architecture Agent
              </Heading>
              <Text fontSize="lg" color="gray.600" mb="2">
                Describe your Azure resources and get instant architecture diagrams
              </Text>
              <Text fontSize="sm" color="gray.500">
                Smart, minimal, and precise - only creates what you request
              </Text>
            </Box>

            {/* Input Section */}
            <Card>
              <CardHeader>
                <Heading size="md" color="blue.700">
                  Describe Your Azure Architecture
                </Heading>
              </CardHeader>
              <CardBody>
                <VStack gap="4" align="stretch">
                  <Text fontSize="sm" color="gray.600" mb="2">
                    Examples: "Create a VM", "Create VNet with VM inside", 
                    "Build web app with database", "Set up Kubernetes cluster with monitoring"
                  </Text>
                  
                  <Textarea
                    placeholder="Describe the Azure resources or architecture you want to create..."
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    rows={4}
                    resize="vertical"
                    bg="white"
                    border="2px solid"
                    borderColor="gray.200"
                    _focus={{
                      borderColor: "blue.500",
                      boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)",
                    }}
                  />
                  
                  <Text fontSize="xs" color="gray.500">
                    {prompt.length}/5000 characters
                  </Text>
                  
                  <VStack gap="2" w="100%">
                    <Button
                      colorScheme="blue"
                      size="lg"
                      w="100%"
                      onClick={handleSubmit}
                      isLoading={loading}
                      loadingText="Generating Architecture..."
                      isDisabled={!prompt.trim() || prompt.length < 10}
                    >
                      Generate Azure Architecture
                    </Button>
                    
                    {(prompt || result) && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleClear}
                        isDisabled={loading}
                      >
                        Clear
                      </Button>
                    )}
                  </VStack>
                </VStack>
              </CardBody>
            </Card>

            {/* Results Section */}
            {result && (
              <Card>
                <CardHeader>
                  <Heading size="md" color="green.700">
                    📊 Generated Azure Architecture
                  </Heading>
                </CardHeader>
                <CardBody>
                  <VStack gap="4" align="stretch">
                    {/* Success Message */}
                    <Alert status="success" borderRadius="md">
                      <AlertIcon />
                      <AlertDescription>
                        <Text fontWeight="bold">Architecture generated successfully!</Text>
                        <Text fontSize="sm">
                          Requirements: {result.requirements_processed}
                        </Text>
                        <Text fontSize="sm">
                          Compliance Score: {result.enterprise_compliance_score}%
                        </Text>
                      </AlertDescription>
                    </Alert>

                    {/* Generated Diagram */}
                    {result.diagram_base64 && (
                      <Box>
                        <Text fontWeight="bold" mb="2">Architecture Diagram:</Text>
                        <Box
                          border="1px solid"
                          borderColor="gray.200"
                          borderRadius="md"
                          p="4"
                          bg="white"
                          textAlign="center"
                        >
                          <Image
                            src={`data:image/png;base64,${result.diagram_base64}`}
                            alt="Generated Azure Architecture Diagram"
                            maxW="100%"
                            height="auto"
                            borderRadius="md"
                          />
                        </Box>
                      </Box>
                    )}

                    {/* Error Message */}
                    {result.execution_error && (
                      <Alert status="warning" borderRadius="md">
                        <AlertIcon />
                        <AlertDescription>
                          <Text fontWeight="bold">Execution Note:</Text>
                          <Text fontSize="sm">{result.execution_error}</Text>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Description */}
                    {result.description && (
                      <Box>
                        <Text fontWeight="bold" mb="2">Description:</Text>
                        <Text fontSize="sm" color="gray.700" bg="gray.50" p="3" borderRadius="md">
                          {result.description}
                        </Text>
                      </Box>
                    )}

                    {/* Review Comments */}
                    {result.review_comments && result.review_comments.length > 0 && (
                      <Box>
                        <Text fontWeight="bold" mb="2">Enterprise Review:</Text>
                        <VStack align="start" gap="2">
                          {result.review_comments.map((comment, index) => (
                            <Text
                              key={index}
                              fontSize="sm"
                              color="blue.700"
                              bg="blue.50"
                              p="2"
                              borderRadius="md"
                              w="100%"
                            >
                              • {comment}
                            </Text>
                          ))}
                        </VStack>
                      </Box>
                    )}

                    {/* Generated Code */}
                    {result.generated_code && (
                      <Box>
                        <Text fontWeight="bold" mb="2">Generated Python Code:</Text>
                        <Box
                          as="pre"
                          fontSize="xs"
                          bg="gray.800"
                          color="green.300"
                          p="4"
                          borderRadius="md"
                          overflow="auto"
                          maxH="400px"
                          fontFamily="mono"
                        >
                          {result.generated_code}
                        </Box>
                      </Box>
                    )}

                    {/* Metadata */}
                    <Box fontSize="xs" color="gray.500" textAlign="center" borderTop="1px solid" borderColor="gray.200" pt="3">
                      Generated on {new Date(result.metadata.generated_at).toLocaleString()} | 
                      Version {result.metadata.version} | 
                      Agent: {result.metadata.agent} | 
                      Mode: {result.metadata.llm_mode}
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            )}
          </VStack>
        </Container>
      </Box>
    </ChakraProvider>
  );
}

export default App;