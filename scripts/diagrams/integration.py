from diagrams import Diagram, Cluster
from diagrams.azure.integration import ServiceBus, EventGridDomains as EventGrid, APIManagement
from diagrams.azure.analytics import EventHubs
from diagrams.azure.web import AppServices
from diagrams.azure.compute import FunctionApps
from diagrams.azure.storage import StorageAccounts
from diagrams.generic.place import Datacenter as Bus
from scripts.diagrams.style import GRAPH_ATTR, NODE_ATTR, FILL_COMPUTE, step, primary, secondary

with Diagram(
    "Azure - Integration",
    show=False,
    outformat="png",
    filename="docs/diagrams/integration",
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    with Cluster("Producers"):
        apim = APIManagement("API Management")
        app = AppServices("Web App")
        func = FunctionApps("Function App")

    with Cluster("Integration Fabric", graph_attr={"bgcolor": FILL_COMPUTE}):
        grid = EventGrid("Event Grid")
        hub = EventHubs("Event Hubs")
        sb = ServiceBus("Service Bus")
        bus = Bus("Integration Bus")

    with Cluster("Sinks"):
        sa = StorageAccounts("Storage")
        sa2 = StorageAccounts("Archive")

    # Enforce a bus to minimize crossings
    apim >> step("1") >> bus
    app >> step("2") >> bus
    func >> step("3") >> bus

    bus >> primary() >> grid
    bus >> primary() >> hub
    bus >> primary() >> sb

    # Fan-out from integration services to sinks
    grid >> primary() >> sa
    hub >> primary() >> sa
    sb >> secondary() >> sa2