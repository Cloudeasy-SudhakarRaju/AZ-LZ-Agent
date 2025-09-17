"""
Analytics and ML Services Diagrams
Implements requirement 36: Analytics and ML services with data pipelines
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.analytics import SynapseAnalytics, DataFactories, Databricks, StreamAnalyticsJobs, EventHubs
from diagrams.azure.ml import MachineLearningServiceWorkspaces, CognitiveServices, BotServices
from diagrams.azure.database import CosmosDb, SQLDatabases
from diagrams.azure.storage import StorageAccounts, DataLakeStorage
from diagrams.azure.integration import LogicApps, ServiceBus
from diagrams.azure.iot import IotHub, IotCentralApplications
from style import *

def generate_analytics_diagram():
    """Generate analytics and ML services diagram"""
    
    with Diagram(
        "Azure Analytics and Machine Learning Platform",
        filename="docs/diagrams/analytics",
        show=False,
        direction="TB",
        outformat="png",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR
    ):
        
        # Data Ingestion Layer
        with Cluster("Data Ingestion", graph_attr={"bgcolor": "#E6F3FF", "style": "rounded,filled"}):
            event_hubs = EventHubs("Event Hubs\n• Real-time Streaming\n• 1M events/sec\n• Partitioned Data")
            iot_hub = IotHub("IoT Hub\n• Device Telemetry\n• Command & Control\n• Device Management")
            data_factory = DataFactories("Data Factory\n• ETL/ELT Pipelines\n• Hybrid Integration\n• Schedule & Trigger")
        
        # Data Storage Layer
        with Cluster("Data Storage", graph_attr={"bgcolor": FILL_DATA, "style": "rounded,filled"}):
            data_lake = DataLakeStorage("Data Lake Gen2\n• Raw Data\n• Hierarchical NS\n• ACL Security")
            sql_dw = SQLDatabases("SQL Database\n• Structured Data\n• OLTP Workloads\n• Relational")
            cosmos_db = CosmosDb("Cosmos DB\n• NoSQL Data\n• Global Distribution\n• Multi-Model")
        
        # Data Processing Layer
        with Cluster("Data Processing", graph_attr={"bgcolor": "#F0F8E6", "style": "rounded,filled"}):
            synapse = SynapseAnalytics("Synapse Analytics\n• Data Warehouse\n• Spark Pools\n• SQL Pools")
            databricks = Databricks("Azure Databricks\n• Apache Spark\n• MLflow\n• Delta Lake")
            stream_analytics = StreamAnalyticsJobs("Stream Analytics\n• Real-time Analytics\n• CEP Queries\n• Windowing")
        
        # Machine Learning Layer
        with Cluster("Machine Learning", graph_attr={"bgcolor": "#FFF0E6", "style": "rounded,filled"}):
            ml_workspace = MachineLearningServiceWorkspaces("ML Workspace\n• Model Training\n• Automated ML\n• MLOps")
            cognitive_services = CognitiveServices("Cognitive Services\n• Pre-built AI\n• Vision, Speech, Language\n• Custom Models")
            bot_service = BotServices("Bot Service\n• Conversational AI\n• Natural Language\n• Multi-channel")
        
        # Integration and Orchestration
        with Cluster("Integration Layer", graph_attr={"bgcolor": FILL_MONITORING, "style": "rounded,filled"}):
            logic_apps = LogicApps("Logic Apps\n• Workflow Orchestration\n• API Integration\n• Event Processing")
            service_bus = ServiceBus("Service Bus\n• Message Queuing\n• Pub/Sub\n• Reliable Messaging")
        
        # IoT and Edge Computing
        with Cluster("IoT Platform", graph_attr={"bgcolor": "#E8F5E8", "style": "rounded,filled"}):
            iot_central = IotCentralApplications("IoT Central\n• Device Management\n• Rules & Actions\n• Dashboards")
            edge_storage = StorageAccounts("Edge Storage\n• Local Processing\n• Offline Capability\n• Sync to Cloud")
        
        # Data Pipeline Flows
        iot_hub >> step("1", COLOR_PRIMARY) >> event_hubs
        event_hubs >> step("2", COLOR_SECONDARY) >> stream_analytics
        data_factory >> step("3", COLOR_WARNING) >> data_lake
        
        # Processing Flows
        data_lake >> step("4", COLOR_PRIMARY) >> synapse
        synapse >> step("5", COLOR_SECONDARY) >> sql_dw
        databricks >> step("6", COLOR_WARNING) >> ml_workspace
        
        # Real-time Analytics
        stream_analytics >> step("7", COLOR_PRIMARY) >> cosmos_db
        event_hubs >> data_flow("Real-time") >> stream_analytics
        data_lake >> data_flow("Batch") >> databricks
        
        # ML Pipeline
        ml_workspace >> step("8", COLOR_SECONDARY) >> cognitive_services
        cognitive_services >> step("9", COLOR_WARNING) >> bot_service
        
        # Integration Flows
        logic_apps >> step("10", COLOR_PRIMARY) >> data_factory
        service_bus >> step("11", COLOR_SECONDARY) >> logic_apps
        
        # IoT Edge Computing
        iot_central >> step("12", COLOR_WARNING) >> iot_hub
        edge_storage >> dr_connection("Sync") >> data_lake
        
        # Monitoring and Feedback
        synapse >> monitoring("Insights") >> ml_workspace
        ml_workspace >> secondary("Retrain") >> databricks

if __name__ == "__main__":
    generate_analytics_diagram()
    print("✅ Analytics diagram generated: docs/diagrams/analytics.png")