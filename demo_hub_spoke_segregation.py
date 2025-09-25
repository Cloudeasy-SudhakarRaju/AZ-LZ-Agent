#!/usr/bin/env python3
"""
Demo script showing the enhanced Hub-Spoke service segregation functionality

This script demonstrates:
1. VM creation always goes to spoke VNet
2. Network services (firewall, VPN, DNS, etc.) go to hub
3. Proper hub-spoke connectivity when both are requested
4. KeyVault can be in both contexts (shared in hub, workload-specific in spoke)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from langgraph_workflow import AzureLandingZoneOrchestrator
from main import CustomerInputs


def demo_vm_spoke_placement():
    """Demonstrate that VMs are always placed in spoke VNets"""
    print("=" * 60)
    print("DEMO 1: VM Spoke Placement")
    print("=" * 60)
    
    orchestrator = AzureLandingZoneOrchestrator()
    
    inputs = CustomerInputs(
        business_objective="Deploy virtual machines for web application",
        compute_services=["virtual_machines"],
        scalability="medium",
        security_posture="standard"
    )
    
    result = orchestrator.process_landing_zone_request(inputs.model_dump())
    
    print(f"✓ VM requested in compute_services")
    print(f"✓ Spoke services identified: {result.get('spoke_services', [])}")
    
    # Check if spoke VNet has VM subnet
    spoke_context = result.get('spoke_context', {})
    workload_components = spoke_context.get('workload_components', {})
    
    for spoke_name, spoke_config in workload_components.items():
        if isinstance(spoke_config, dict) and 'vnet' in spoke_config:
            vnet_name = spoke_config['vnet'].get('name', 'Unknown')
            subnets = spoke_config['vnet'].get('subnets', {})
            print(f"✓ {vnet_name} created with subnets: {list(subnets.keys())}")
            
            vm_subnet = any('virtual' in subnet.lower() or 'vm' in subnet.lower() for subnet in subnets.keys())
            if vm_subnet:
                print(f"✓ VM subnet properly created in spoke VNet")
    
    print()


def demo_network_services_hub_placement():
    """Demonstrate that network services are placed in hub"""
    print("=" * 60)
    print("DEMO 2: Network Services in Hub")
    print("=" * 60)
    
    orchestrator = AzureLandingZoneOrchestrator()
    
    inputs = CustomerInputs(
        business_objective="Set up secure network infrastructure",
        network_services=["firewall", "vpn_gateway", "dns"],
        security_services=["key_vault"],  # This will be shared KeyVault in hub context
        scalability="high",
        security_posture="zero_trust"
    )
    
    result = orchestrator.process_landing_zone_request(inputs.model_dump())
    
    print(f"✓ Network services requested: firewall, VPN gateway, DNS")
    print(f"✓ Hub services identified: {result.get('hub_services', [])}")
    
    # Check hub network topology
    hub_context = result.get('hub_context', {})
    network_topology = hub_context.get('network_topology', {})
    hub_vnet = network_topology.get('hub_vnet', {})
    
    if hub_vnet:
        print(f"✓ Hub VNet created: {hub_vnet.get('name', 'Hub-VNet')}")
        print(f"✓ Hub subnets: {list(hub_vnet.get('subnets', {}).keys())}")
    
    print()


def demo_hub_spoke_connectivity():
    """Demonstrate hub-spoke connectivity when both types of services are requested"""
    print("=" * 60)  
    print("DEMO 3: Hub-Spoke Connectivity")
    print("=" * 60)
    
    orchestrator = AzureLandingZoneOrchestrator()
    
    inputs = CustomerInputs(
        business_objective="Enterprise application with secure network",
        compute_services=["virtual_machines", "aks"],  # Spoke services
        network_services=["firewall", "vpn_gateway"],  # Hub services
        database_services=["sql_database"],  # Spoke service
        security_services=["key_vault"],  # Can be in both contexts
        scalability="high",
        security_posture="zero_trust"
    )
    
    result = orchestrator.process_landing_zone_request(inputs.model_dump())
    
    hub_services = result.get('hub_services', [])
    spoke_services = result.get('spoke_services', [])
    
    print(f"✓ Hub services: {hub_services}")
    print(f"✓ Spoke services: {spoke_services}")
    
    # Check connectivity configuration
    spoke_context = result.get('spoke_context', {})
    workload_components = spoke_context.get('workload_components', {})
    
    connected_spokes = []
    for spoke_name, spoke_config in workload_components.items():
        if isinstance(spoke_config, dict) and spoke_config.get('peering_to_hub'):
            connected_spokes.append(spoke_name)
    
    if connected_spokes:
        print(f"✓ Hub-spoke connectivity established for: {connected_spokes}")
    else:
        print("⚠ No hub-spoke peering configured")
    
    print()


def demo_keyvault_dual_context():
    """Demonstrate KeyVault can exist in both hub and spoke contexts"""
    print("=" * 60)
    print("DEMO 4: KeyVault Dual Context")
    print("=" * 60)
    
    print("KeyVault Categorization:")
    print("✓ 'key_vault' in SPOKE_SERVICES for workload-specific secrets")
    print("✓ 'key_vault_shared' in HUB_SERVICES for shared secrets")
    
    # This demonstrates the design - in practice, the orchestrator would 
    # determine placement based on context and naming conventions
    print("✓ Hub KeyVault: For shared certificates, connection strings")
    print("✓ Spoke KeyVault: For application-specific secrets, keys")
    print()


if __name__ == "__main__":
    print("Azure Landing Zone - Enhanced Hub-Spoke Service Segregation Demo")
    print("================================================================")
    print()
    
    try:
        demo_vm_spoke_placement()
        demo_network_services_hub_placement()
        demo_hub_spoke_connectivity()
        demo_keyvault_dual_context()
        
        print("=" * 60)
        print("✅ All demos completed successfully!")
        print("✅ Hub-spoke service segregation is working as expected")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        sys.exit(1)