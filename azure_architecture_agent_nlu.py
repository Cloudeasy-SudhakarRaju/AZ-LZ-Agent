import spacy
import json

class AzureArchitectureAgent:
    def __init__(self):
        # Load the spaCy model
        self.nlp = spacy.load("en_core_web_sm")

    def parse_request(self, request):
        # Parse the human-language request
        doc = self.nlp(request)
        return doc

    def extract_services(self, doc):
        # Extract relevant Azure services and zones from the parsed request
        services = []
        for ent in doc.ents:
            if ent.label_ == "SERVICE":  # Assuming we have a custom named entity 'SERVICE'
                services.append(ent.text)
        return services

    def generate_architecture(self, services):
        # Generate architecture output in JSON format
        architecture = {
            "services": services,
            "diagram": "link_to_diagram",  # Placeholder for diagram link
            "description": "Generated architecture based on user request."
        }
        return json.dumps(architecture, indent=4)

    def explain_architecture(self, architecture_json):
        # Provide a human-readable explanation of the architecture
        architecture = json.loads(architecture_json)
        explanation = f"This architecture includes the following services: {', '.join(architecture['services'])}."
        return explanation

# Example usage
if __name__ == "__main__":
    agent = AzureArchitectureAgent()
    request = "I need a scalable web application using Azure Functions and Azure SQL Database."
    doc = agent.parse_request(request)
    services = agent.extract_services(doc)
    architecture_json = agent.generate_architecture(services)
    explanation = agent.explain_architecture(architecture_json)
    print(architecture_json)
    print(explanation)