"""
Pydantic schemas for the Architecture Diagram Agent.
Defines data models for user intents, requirements, and service configurations.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class UserIntent(BaseModel):
    """Represents a single user intent for a service or component."""
    kind: str = Field(..., description="Type of service (vm, web_app, function_app, etc.)")
    name: Optional[str] = Field(None, description="Custom name for the service")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Service-specific configuration")


class NetworkingDefaults(BaseModel):
    """Default networking configuration."""
    address_space: str = Field("10.0.0.0/16", description="Default VNet address space")
    subnet_prefix: str = Field("10.0.1.0/24", description="Default subnet prefix")
    enable_bastion: bool = Field(False, description="Whether to include Azure Bastion")
    enable_nat_gateway: bool = Field(False, description="Whether to include NAT Gateway")


class Requirements(BaseModel):
    """Overall architecture requirements and constraints."""
    # Geographic and HA requirements
    regions: List[str] = Field(default=["East US 2"], description="Azure regions for deployment")
    ha_mode: Literal["single-region", "multi-region", "active-passive", "active-active"] = Field(
        "single-region", description="High availability mode"
    )
    
    # Architecture components
    edge_services: List[str] = Field(default_factory=list, description="Edge services (front_door, cdn, etc.)")
    identity_services: List[str] = Field(default_factory=list, description="Identity services (entra_id, etc.)")
    
    # User intents for services
    services: List[UserIntent] = Field(default_factory=list, description="List of requested services")
    
    # Networking defaults
    networking: NetworkingDefaults = Field(default_factory=NetworkingDefaults, description="Networking configuration")
    
    # Optional metadata
    project_name: Optional[str] = Field(None, description="Project or application name")
    environment: Optional[str] = Field("prod", description="Environment (dev, test, prod)")


class ServiceDependency(BaseModel):
    """Represents a dependency between services."""
    service_type: str = Field(..., description="Type of dependent service")
    required: bool = Field(True, description="Whether this dependency is required")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Dependency-specific properties")


class ServiceDefinition(BaseModel):
    """Definition of a service in the catalog with its dependencies."""
    name: str = Field(..., description="Display name of the service")
    category: str = Field(..., description="Service category (compute, network, storage, etc.)")
    dependencies: List[ServiceDependency] = Field(default_factory=list, description="Required dependencies")
    prompts: List[str] = Field(default_factory=list, description="Questions to ask when this service is selected")
    diagram_class: Optional[str] = Field(None, description="Diagrams library class name")


class LayoutNode(BaseModel):
    """Represents a node in the layout graph."""
    id: str = Field(..., description="Unique identifier for the node")
    service_type: str = Field(..., description="Type of service")
    name: str = Field(..., description="Display name")
    cluster: Optional[str] = Field(None, description="Cluster this node belongs to")
    rank: Optional[int] = Field(None, description="Layout rank/order")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class LayoutEdge(BaseModel):
    """Represents an edge in the layout graph."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label")
    style: Optional[str] = Field(None, description="Edge style (solid, dashed, dotted)")
    color: Optional[str] = Field(None, description="Edge color")


class LayoutGraph(BaseModel):
    """Complete layout graph representation."""
    nodes: List[LayoutNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[LayoutEdge] = Field(default_factory=list, description="Graph edges")
    clusters: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Cluster definitions")