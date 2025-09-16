from diagrams import Diagram, Cluster
from diagrams.azure.storage import DataLakeStorage, BlobStorage
from diagrams.azure.storage import QueuesStorage as Queue, TableStorage as Table
from diagrams.azure.database import SQLDatabases as SQL, CosmosDb, CacheForRedis as Redis
from diagrams.azure.analytics import SynapseAnalytics, DataFactories as ADF
from scripts.diagrams.style import GRAPH_ATTR, NODE_ATTR, FILL_DATA, step, primary, repl

with Diagram(
    "Azure - Data",
    show=False,
    outformat="png",
    filename="docs/diagrams/data",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    with Cluster("Data Sources"):
        q = Queue("Queue")
        blob = BlobStorage("Blob")
        table = Table("Table")

    with Cluster("Data Platform", graph_attr={"bgcolor": FILL_DATA}):
        dl = DataLakeStorage("Data Lake")
        syn = SynapseAnalytics("Synapse")
        adf = ADF("Data Factory")
        sql = SQL("Azure SQL")
        cos = CosmosDb("Cosmos DB")
        redis = Redis("Redis Cache")

    # Left-to-right ingestion and processing
    q >> step("1") >> dl
    blob >> step("2") >> dl
    table >> step("3") >> dl

    dl >> step("4 (ETL)") >> adf >> step("5 (Transform)") >> syn
    syn >> primary() >> sql
    syn >> primary() >> cos

    # Caching / replication paths
    sql >> repl() >> redis
    cos >> repl() >> redis