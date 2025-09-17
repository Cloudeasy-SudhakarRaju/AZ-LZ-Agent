"""
Compliance and Regulatory Overlay Diagrams
Implements requirement 17: Compliance/regulatory overlays with zone indicators
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.security import KeyVaults, SecurityCenter, Sentinel
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.general import Subscriptions, Resourcegroups, Templates
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from style import *

def generate_compliance_diagram():
    """Generate compliance and regulatory overlay diagram"""
    
    with Diagram(
        "Azure Compliance and Regulatory Framework",
        filename="docs/diagrams/compliance",
        show=False,
        direction="TB",
        outformat="png",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR
    ):
        
        # Compliance Framework Layer
        with Cluster("Compliance Framework", graph_attr={"bgcolor": "#FFF8DC", "style": "rounded,filled"}):
            
            # Regulatory Standards
            with Cluster("Regulatory Standards", graph_attr={"bgcolor": "#F0E68C", "style": "dashed"}):
                gdpr = Templates("GDPR Compliance")
                hipaa = Templates("HIPAA Controls")
                sox = Templates("SOX Compliance")
                iso27001 = Templates("ISO 27001")
            
            # Policy Engine
            with Cluster("Policy Enforcement", graph_attr={"bgcolor": "#E6E6FA", "style": "dotted"}):
                azure_policy = Templates("Azure Policy")
                blueprints = Templates("Azure Blueprints")
                initiatives = Templates("Policy Initiatives")
        
        # Identity and Access Governance
        with Cluster("Identity Governance", graph_attr={"bgcolor": FILL_IDENTITY_SECURITY, "style": "rounded,filled"}):
            entra_id = ActiveDirectory("Microsoft Entra ID")
            privileged_access = SecurityCenter("Privileged Access")
            access_reviews = SecurityCenter("Access Reviews")
        
        # Security and Monitoring
        with Cluster("Security Compliance", graph_attr={"bgcolor": "#FFE4E1", "style": "rounded,filled"}):
            sentinel = Sentinel("Microsoft Sentinel")
            security_center = SecurityCenter("Defender for Cloud")
            key_vault = KeyVaults("Key Vault HSM")
        
        # Audit and Reporting
        with Cluster("Audit and Reporting", graph_attr={"bgcolor": "#F5F5DC", "style": "rounded,filled"}):
            audit_logs = LogAnalyticsWorkspaces("Audit Logs")
            compliance_reports = LogAnalyticsWorkspaces("Compliance Reports")
            risk_assessment = SecurityCenter("Risk Assessment")
        
        # Resource Management
        with Cluster("Resource Governance", graph_attr={"bgcolor": FILL_COMPUTE, "style": "rounded,filled"}):
            subscriptions = Subscriptions("Subscription Governance")
            resource_groups = Resourcegroups("Resource Group Tags")
            cost_management = LogAnalyticsWorkspaces("Cost Management")
        
        # Compliance Flows
        azure_policy >> step("1", COLOR_PRIMARY) >> subscriptions
        blueprints >> step("2", COLOR_SECONDARY) >> resource_groups
        entra_id >> step("3", COLOR_PRIMARY) >> privileged_access
        security_center >> step("4", COLOR_WARNING) >> audit_logs
        sentinel >> step("5", COLOR_DANGER) >> compliance_reports
        
        # Regulatory Compliance Flows
        gdpr >> ctrl("GDPR") >> key_vault
        hipaa >> ctrl("HIPAA") >> sentinel
        sox >> ctrl("SOX") >> audit_logs
        iso27001 >> ctrl("ISO") >> security_center

if __name__ == "__main__":
    generate_compliance_diagram()
    print("✅ Compliance diagram generated: docs/diagrams/compliance.png")