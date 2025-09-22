"""
Performance Indicators and Monitoring Diagrams
Implements requirement 19: Performance indicators and SLA markers
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import AppServices, FunctionApps, AKS, VM
from diagrams.azure.database import SQLDatabases, CosmosDb, CacheForRedis
from diagrams.azure.network import ApplicationGateway, LoadBalancers, CDNProfiles
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.ml import MachineLearningServiceWorkspaces
from style import *

def generate_performance_diagram():
    """Generate performance indicators and SLA monitoring diagram"""
    
    with Diagram(
        "Azure Performance and SLA Monitoring",
        filename="docs/diagrams/performance",
        show=False,
        direction="TB",
        outformat="png",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR
    ):
        
        # Performance Monitoring Layer
        with Cluster("Performance Monitoring", graph_attr={"bgcolor": "#E6F3FF", "style": "rounded,filled"}):
            app_insights = MachineLearningServiceWorkspaces("Application Insights\n• Response Time < 200ms\n• Availability > 99.9%")
            azure_monitor = LogAnalyticsWorkspaces("Azure Monitor\n• CPU < 80%\n• Memory < 85%\n• Disk < 90%")
            log_analytics = LogAnalyticsWorkspaces("Log Analytics\n• Query Performance\n• Custom Metrics")
        
        # Application Performance Tier
        with Cluster("Application Layer - SLA: 99.95%", graph_attr={"bgcolor": FILL_COMPUTE, "style": "rounded,filled"}):
            app_gateway = ApplicationGateway("App Gateway\n• Latency < 50ms\n• Throughput > 1000 RPS")
            web_apps = AppServices("Web Apps\n• Response < 500ms\n• CPU < 70%")
            functions = FunctionApps("Functions\n• Cold Start < 1s\n• Duration < 5min")
        
        # Container Performance Tier
        with Cluster("Container Layer - SLA: 99.9%", graph_attr={"bgcolor": "#E8F5E8", "style": "rounded,filled"}):
            aks_cluster = AKS("AKS Cluster\n• Pod CPU < 80%\n• Memory < 85%\n• Node Health > 95%")
            load_balancer = LoadBalancers("Load Balancer\n• Health Probes\n• Distribution Metrics")
        
        # Data Performance Tier
        with Cluster("Data Layer - SLA: 99.99%", graph_attr={"bgcolor": FILL_DATA, "style": "rounded,filled"}):
            sql_db = SQLDatabases("SQL Database\n• DTU < 80%\n• Query < 1s\n• Deadlocks = 0")
            cosmos_db = CosmosDb("Cosmos DB\n• RU/s Consumption\n• Latency < 10ms")
            redis_cache = CacheForRedis("Redis Cache\n• Hit Ratio > 90%\n• Memory < 80%")
        
        # Storage Performance Tier
        with Cluster("Storage Layer - SLA: 99.9%", graph_attr={"bgcolor": "#FFF0E6", "style": "rounded,filled"}):
            storage = StorageAccounts("Storage Account\n• IOPS Monitoring\n• Throughput Limits")
            cdn = CDNProfiles("CDN Profile\n• Cache Hit > 85%\n• Origin Load < 20%")
        
        # Compute Infrastructure
        with Cluster("Infrastructure - SLA: 99.95%", graph_attr={"bgcolor": "#F0F0F0", "style": "rounded,filled"}):
            vms = VM("Virtual Machines\n• CPU < 75%\n• Available Memory\n• Disk Queue < 10")
        
        # Performance Flow Monitoring
        app_gateway >> step("1", COLOR_PRIMARY) >> app_insights
        web_apps >> step("2", COLOR_SECONDARY) >> app_insights
        functions >> step("3", COLOR_WARNING) >> azure_monitor
        
        aks_cluster >> step("4", COLOR_PRIMARY) >> azure_monitor
        load_balancer >> step("5", COLOR_SECONDARY) >> log_analytics
        
        sql_db >> step("6", COLOR_PRIMARY) >> azure_monitor
        cosmos_db >> step("7", COLOR_SECONDARY) >> app_insights
        redis_cache >> step("8", COLOR_WARNING) >> azure_monitor
        
        storage >> step("9", COLOR_PRIMARY) >> azure_monitor
        cdn >> step("10", COLOR_SECONDARY) >> log_analytics
        vms >> step("11", COLOR_WARNING) >> azure_monitor
        
        # Alerting and Response
        azure_monitor >> monitoring("Critical") >> app_insights
        app_insights >> primary("Scale Out") >> aks_cluster
        log_analytics >> secondary("Forecast") >> vms

if __name__ == "__main__":
    generate_performance_diagram()
    print("✅ Performance diagram generated: docs/diagrams/performance.png")