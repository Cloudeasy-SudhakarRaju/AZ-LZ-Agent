"""
DevOps Pipeline Integration Diagrams
Implements requirement 26: DevOps pipeline integration with CI/CD markers
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.devops import Devops, Pipelines, Repos, Artifacts, TestPlans
from diagrams.azure.compute import AppServices, AKS, FunctionApps
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.security import KeyVaults
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.general import Templates
from style import *

def generate_devops_diagram():
    """Generate DevOps pipeline integration diagram"""
    
    with Diagram(
        "Azure DevOps Pipeline Integration",
        filename="docs/diagrams/devops",
        show=False,
        direction="LR",
        outformat="png",
        graph_attr={**GRAPH_ATTR, "rankdir": "LR"},
        node_attr=NODE_ATTR
    ):
        
        # Source Control
        with Cluster("Source Control", graph_attr={"bgcolor": "#E6F7FF", "style": "rounded,filled"}):
            git_repo = Repos("Git Repository\n• Branch Policies\n• Code Reviews\n• Pull Requests")
            artifacts = Artifacts("Artifact Registry\n• Container Images\n• NuGet Packages\n• NPM Packages")
        
        # CI Pipeline
        with Cluster("Continuous Integration", graph_attr={"bgcolor": "#F0F8E6", "style": "rounded,filled"}):
            build_pipeline = Pipelines("Build Pipeline\n• Code Quality Gates\n• Security Scans\n• Unit Tests")
            test_plans = TestPlans("Test Automation\n• Unit Tests: >90%\n• Integration Tests\n• Security Tests")
        
        # CD Pipeline
        with Cluster("Continuous Deployment", graph_attr={"bgcolor": "#FFF7E6", "style": "rounded,filled"}):
            release_pipeline = Pipelines("Release Pipeline\n• Blue-Green Deploy\n• Canary Releases\n• Rollback Strategy")
            automation = Templates("Infrastructure as Code\n• ARM Templates\n• Terraform\n• Bicep")
        
        # Environment Management
        with Cluster("Environment Orchestration", graph_attr={"bgcolor": FILL_COMPUTE, "style": "rounded,filled"}):
            dev_env = AppServices("Development\n• Feature Branches\n• Auto-Deploy\n• Fast Feedback")
            uat_env = AppServices("UAT/Staging\n• Release Candidates\n• E2E Testing\n• Performance Testing")
            prod_env = AKS("Production\n• Blue-Green\n• Health Checks\n• Monitoring")
        
        # Security and Compliance
        with Cluster("Security Integration", graph_attr={"bgcolor": FILL_IDENTITY_SECURITY, "style": "rounded,filled"}):
            key_vault = KeyVaults("Key Vault\n• Secrets Management\n• Certificate Rotation\n• Deployment Keys")
            security_scans = Devops("Security Scanning\n• SAST/DAST\n• Dependency Check\n• Container Scan")
        
        # Monitoring and Feedback
        with Cluster("Monitoring & Feedback", graph_attr={"bgcolor": FILL_MONITORING, "style": "rounded,filled"}):
            azure_monitor = LogAnalyticsWorkspaces("Azure Monitor\n• Application Insights\n• Log Analytics\n• Alerts & Dashboards")
            feedback_loop = Devops("Feedback Loop\n• Performance Metrics\n• User Analytics\n• Error Tracking")
        
        # Storage and Configuration
        with Cluster("Configuration Management", graph_attr={"bgcolor": "#F5F5F5", "style": "rounded,filled"}):
            config_storage = StorageAccounts("Configuration Store\n• Environment Configs\n• Feature Flags\n• App Settings")
            backup_storage = StorageAccounts("Backup Storage\n• Database Backups\n• Configuration Backups\n• Disaster Recovery")
        
        # DevOps Flow
        git_repo >> step("1", COLOR_PRIMARY) >> build_pipeline
        build_pipeline >> step("2", COLOR_SECONDARY) >> test_plans
        test_plans >> step("3", COLOR_PRIMARY) >> artifacts
        
        artifacts >> step("4", COLOR_SECONDARY) >> dev_env
        dev_env >> step("5", COLOR_WARNING) >> uat_env
        uat_env >> step("6", COLOR_PRIMARY) >> prod_env
        
        # Security Integration
        build_pipeline >> ctrl("SAST") >> security_scans
        security_scans >> monitoring("Critical") >> key_vault
        key_vault >> primary("Secrets") >> release_pipeline
        
        # Infrastructure as Code
        automation >> step("7", COLOR_SECONDARY) >> prod_env
        config_storage >> step("8", COLOR_WARNING) >> prod_env
        
        # Monitoring and Feedback
        prod_env >> step("9", COLOR_PRIMARY) >> azure_monitor
        azure_monitor >> step("10", COLOR_SECONDARY) >> feedback_loop
        feedback_loop >> data_flow("Feedback") >> git_repo
        
        # Backup and Recovery
        prod_env >> dr_connection("DR") >> backup_storage
        backup_storage >> dr_connection("Recovery") >> uat_env

if __name__ == "__main__":
    generate_devops_diagram()
    print("✅ DevOps diagram generated: docs/diagrams/devops.png")