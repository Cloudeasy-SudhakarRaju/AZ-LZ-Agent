#!/usr/bin/env python3
"""
Sample demonstration of LangGraph Hub-Spoke Orchestration

This script demonstrates the LangGraph multi-agent workflow for Azure Landing Zone
Hub-and-Spoke architecture generation.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from langgraph_workflow import create_orchestrator

def demo_hub_spoke_orchestration():
    """Demonstrate the LangGraph hub-spoke orchestration"""
    
    print("🏗️ Azure Landing Zone Agent - LangGraph Hub-Spoke Orchestration Demo")
    print("=" * 70)
    
    # Create orchestrator
    orchestrator = create_orchestrator()
    
    # Sample enterprise scenario
    enterprise_inputs = {
        "business_objective": "Enterprise e-commerce platform with high availability and security",
        "regulatory": "PCI-DSS, SOX compliance required",
        "industry": "Financial Services",
        
        # Hub services (shared infrastructure)
        "network_services": ["azure_firewall", "bastion", "vpn_gateway", "dns"],
        "security_services": ["security_center", "sentinel", "key_vault"],
        "monitoring_services": ["log_analytics", "monitor"],
        
        # Spoke services (workload-specific)
        "compute_services": ["app_services", "virtual_machines", "aks"],
        "database_services": ["sql_database", "cosmos_db"],
        "storage_services": ["storage_accounts", "blob_storage"],
        "ai_services": ["cognitive_services"],
        
        # Configuration
        "scalability": "high",
        "security_posture": "zero_trust",
        "backup": "comprehensive"
    }
    
    print("📋 Input Configuration:")
    print(f"   Business Objective: {enterprise_inputs['business_objective']}")
    print(f"   Industry: {enterprise_inputs['industry']}")
    print(f"   Security Posture: {enterprise_inputs['security_posture']}")
    print(f"   Scalability: {enterprise_inputs['scalability']}")
    print()
    
    # Execute workflow
    print("🔄 Executing LangGraph Multi-Agent Workflow...")
    result = orchestrator.process_landing_zone_request(enterprise_inputs)
    
    # Display results
    print("\n🎯 Hub Agent Results:")
    hub_services = result.get("hub_services", [])
    print(f"   Services Identified: {len(hub_services)}")
    for service in hub_services:
        print(f"   - {service.replace('_', ' ').title()}")
    
    print(f"\n🎯 Spoke Agent Results:")
    spoke_services = result.get("spoke_services", [])
    print(f"   Services Identified: {len(spoke_services)}")
    for service in spoke_services:
        print(f"   - {service.replace('_', ' ').title()}")
    
    # Network topology
    network_topology = result.get("network_topology", {})
    hub_vnet = network_topology.get("hub_vnet", {})
    print(f"\n🌐 Network Architecture:")
    print(f"   Hub VNet: {hub_vnet.get('name', 'Hub-VNet')} ({hub_vnet.get('address_space', '10.0.0.0/16')})")
    
    subnets = hub_vnet.get("subnets", {})
    for subnet_name, cidr in subnets.items():
        print(f"   - {subnet_name}: {cidr}")
    
    # Workload components
    workload_components = result.get("spoke_context", {}).get("workload_components", {})
    if workload_components:
        print(f"\n🏭 Workload Distribution:")
        for spoke_name, spoke_config in workload_components.items():
            spoke_vnet = spoke_config.get("vnet", {})
            print(f"   {spoke_name.replace('_', ' ').title()}: {spoke_vnet.get('name', 'Unknown')} ({spoke_vnet.get('address_space', 'Unknown')})")
    
    # Final status
    final_result = result.get("final_result", {})
    print(f"\n✅ Orchestration Summary:")
    print(f"   Success: {final_result.get('success', False)}")
    print(f"   Architecture Pattern: {final_result.get('architecture_pattern', 'Unknown')}")
    print(f"   Hub Services Count: {final_result.get('hub_services_count', 0)}")
    print(f"   Spoke Services Count: {final_result.get('spoke_services_count', 0)}")
    print(f"   Diagram Ready: {final_result.get('diagram_ready', False)}")
    
    # Execution log
    execution_log = result.get("execution_log", [])
    print(f"\n📝 Execution Log:")
    for i, log_entry in enumerate(execution_log, 1):
        print(f"   {i}. {log_entry}")
    
    return result

def generate_sample_mermaid(orchestration_result):
    """Generate a sample Mermaid diagram from orchestration results"""
    
    print("\n🎨 Sample Mermaid Diagram Generation:")
    print("-" * 50)
    
    # Extract data
    hub_services = orchestration_result.get("hub_services", [])
    spoke_services = orchestration_result.get("spoke_services", [])
    
    # Generate simplified Mermaid syntax
    mermaid_lines = [
        "graph TB",
        "    %% Azure Landing Zone - Hub and Spoke (LangGraph Orchestrated)",
        "    classDef hubStyle fill:#0078d4,stroke:#005a9e,stroke-width:3px,color:#ffffff",
        "    classDef spokeStyle fill:#00bcf2,stroke:#0078d4,stroke-width:2px,color:#ffffff",
        "",
        "    %% Hub Infrastructure",
        "    subgraph \"Hub\" [\"🏢 Hub Infrastructure\"]",
        "        HUBVNET[\"🌐 Hub VNet\"]"
    ]
    
    # Add hub services
    for i, service in enumerate(hub_services[:4]):  # Limit for readability
        service_id = f"HUB{i+1}"
        service_name = service.replace('_', ' ').title()
        mermaid_lines.append(f"        {service_id}[\"🔧 {service_name}\"]")
    
    mermaid_lines.extend([
        "    end",
        "",
        "    %% Production Spoke",
        "    subgraph \"ProdSpoke\" [\"🏭 Production Spoke\"]",
        "        PRODVNET[\"🌐 Production VNet\"]"
    ])
    
    # Add spoke services
    for i, service in enumerate(spoke_services[:4]):  # Limit for readability
        service_id = f"PROD{i+1}"
        service_name = service.replace('_', ' ').title()
        mermaid_lines.append(f"        {service_id}[\"💼 {service_name}\"]")
    
    mermaid_lines.extend([
        "    end",
        "",
        "    %% Connections",
        "    HUBVNET -.->|\"VNet Peering\"| PRODVNET",
        "",
        "    %% Styling",
        "    class HUBVNET,HUB1,HUB2,HUB3,HUB4 hubStyle",
        "    class PRODVNET,PROD1,PROD2,PROD3,PROD4 spokeStyle"
    ])
    
    mermaid_diagram = "\n".join(mermaid_lines)
    print(mermaid_diagram)
    
    return mermaid_diagram

if __name__ == "__main__":
    # Run demonstration
    result = demo_hub_spoke_orchestration()
    
    # Generate sample diagram
    mermaid_output = generate_sample_mermaid(result)
    
    print("\n" + "=" * 70)
    print("🎉 LangGraph Hub-Spoke Orchestration Demo Completed Successfully!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Multi-agent workflow (Hub Agent + Spoke Agent)")
    print("  ✅ Service categorization (Hub vs Spoke)")
    print("  ✅ Sequential execution (Hub → Spoke → Merge)")
    print("  ✅ Network topology design")
    print("  ✅ Context passing between agents")
    print("  ✅ Diagram-ready output generation")
    print("  ✅ Hub-and-spoke architecture separation")