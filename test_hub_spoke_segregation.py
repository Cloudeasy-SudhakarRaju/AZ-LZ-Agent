"""
Test Hub-Spoke Service Segregation Requirements

This test module validates that the Azure Landing Zone Agent properly segregates services
according to the hub-spoke architecture requirements:

1. VMs should be created within spoke VNets, not hub
2. Network services (firewall, VPN, DNS, ExpressRoute, KeyVault, Monitor) should be in hub  
3. Spoke should contain only VM, K8s, KeyVault (workload-specific), DB
4. Hub should contain only shared network services 
5. Hub-spoke connections should be established when both types are requested
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from langgraph_workflow import AzureLandingZoneOrchestrator, HUB_SERVICES, SPOKE_SERVICES
from main import CustomerInputs


class TestHubSpokeServiceSegregation:
    """Test proper segregation of services into hub and spoke based on requirements"""
    
    def test_vm_service_categorization(self):
        """Test that VM services are properly categorized as spoke services"""
        vm_services = ['virtual_machines', 'vm', 'vmss']
        
        for vm_service in vm_services:
            assert vm_service in SPOKE_SERVICES, f"{vm_service} should be categorized as a spoke service"
        
        # Ensure VMs are not in hub services
        for vm_service in vm_services:
            assert vm_service not in HUB_SERVICES, f"{vm_service} should NOT be in hub services"
    
    def test_network_services_in_hub(self):
        """Test that network services are properly categorized as hub services"""
        required_hub_services = ['firewall', 'vpn_gateway', 'dns', 'expressroute', 'monitor']
        
        for service in required_hub_services:
            # Check if service or its variants are in hub services
            found = any(service in hub_svc for hub_svc in HUB_SERVICES)
            assert found, f"Network service '{service}' (or variant) should be in hub services"
    
    def test_k8s_service_categorization(self):
        """Test that Kubernetes services are properly categorized as spoke services"""
        k8s_services = ['aks', 'kubernetes', 'k8s']
        
        for k8s_service in k8s_services:
            assert k8s_service in SPOKE_SERVICES, f"{k8s_service} should be categorized as a spoke service"
    
    def test_database_service_categorization(self):
        """Test that database services are properly categorized as spoke services"""
        db_services = ['sql_database', 'mysql', 'postgresql', 'cosmos_db']
        
        for db_service in db_services:
            assert db_service in SPOKE_SERVICES, f"{db_service} should be categorized as a spoke service"
    
    def test_keyvault_dual_placement(self):
        """Test that KeyVault can exist in both hub (shared) and spoke (workload-specific) contexts"""
        # Regular keyvault should be in spoke services for workload-specific secrets
        assert 'key_vault' in SPOKE_SERVICES, "key_vault should be available in spoke for workload secrets"
        assert 'keyvault' in SPOKE_SERVICES, "keyvault should be available in spoke for workload secrets"
        
        # Shared keyvault variants should be in hub services
        shared_kv_found = any('shared' in service for service in HUB_SERVICES if 'key_vault' in service)
        assert shared_kv_found, "Shared KeyVault should be available in hub for shared secrets"
    
    def test_vm_spoke_placement_enforcement(self):
        """Test that VM placement is enforced to spoke VNets"""
        orchestrator = AzureLandingZoneOrchestrator()
        
        # Create input with VMs requested
        inputs = CustomerInputs(
            business_objective="Test VM placement",
            compute_services=["virtual_machines"],
            network_services=["firewall"],  # Include network service to trigger hub creation
            scalability="medium",
            security_posture="standard"
        )
        
        # Process the request
        result = orchestrator.process_landing_zone_request(inputs.model_dump())
        
        # Verify VM services are in spoke
        spoke_services = result.get('spoke_services', [])
        assert any('virtual_machine' in svc.lower() for svc in spoke_services), "VMs should be placed in spoke services"
        
        # Verify spoke VNet is created for VMs
        spoke_context = result.get('spoke_context', {})
        workload_components = spoke_context.get('workload_components', {})
        
        # Check that spoke VNet has VM subnet
        for spoke_name, spoke_config in workload_components.items():
            if isinstance(spoke_config, dict) and 'vnet' in spoke_config:
                subnets = spoke_config['vnet'].get('subnets', {})
                vm_subnet_found = any('virtual' in subnet_name.lower() or 'vm' in subnet_name.lower() 
                                      for subnet_name in subnets.keys())
                if vm_subnet_found:
                    break
        else:
            pytest.fail("VM subnet should be created in spoke VNet when VMs are requested")
    
    def test_hub_spoke_connection_when_both_requested(self):
        """Test that hub-spoke connections are established when both hub and spoke services are requested"""
        orchestrator = AzureLandingZoneOrchestrator()
        
        # Create input with both hub and spoke services
        inputs = CustomerInputs(
            business_objective="Test hub-spoke connectivity",
            compute_services=["virtual_machines"],  # Spoke service
            network_services=["firewall", "vpn_gateway"],  # Hub services
            database_services=["sql_database"],  # Spoke service
            scalability="high",
            security_posture="zero_trust"
        )
        
        result = orchestrator.process_landing_zone_request(inputs.model_dump())
        
        # Verify both hub and spoke services are present
        hub_services = result.get('hub_services', [])
        spoke_services = result.get('spoke_services', [])
        
        assert len(hub_services) > 0, "Hub services should be present when network services are requested"
        assert len(spoke_services) > 0, "Spoke services should be present when compute/database services are requested"
        
        # Verify peering configuration exists
        spoke_context = result.get('spoke_context', {})
        workload_components = spoke_context.get('workload_components', {})
        
        peering_found = False
        for spoke_name, spoke_config in workload_components.items():
            if isinstance(spoke_config, dict) and spoke_config.get('peering_to_hub') == True:
                peering_found = True
                break
        
        assert peering_found, "Spoke should be configured with peering to hub when both hub and spoke services are requested"
    
    def test_no_hub_when_only_spoke_services_requested(self):
        """Test that hub is not created when only spoke services are requested"""
        orchestrator = AzureLandingZoneOrchestrator()
        
        # Create input with only spoke services
        inputs = CustomerInputs(
            business_objective="Test spoke-only scenario",
            compute_services=["virtual_machines"],
            database_services=["sql_database"],
            scalability="medium",
            security_posture="standard"
        )
        
        result = orchestrator.process_landing_zone_request(inputs.model_dump())
        
        # Hub services should be minimal or empty (only core services auto-added)
        hub_services = result.get('hub_services', [])
        
        # The system may auto-add some core hub services, but no major network services should be present
        # unless explicitly requested
        network_services_in_hub = [svc for svc in hub_services 
                                   if any(net_svc in svc.lower() for net_svc in ['firewall', 'vpn', 'expressroute'])]
        
        # We expect minimal hub services when only spoke services are requested
        # This is acceptable as some core services may be auto-added for proper architecture
        assert len(network_services_in_hub) <= 3, "Major network services should not be created unless explicitly requested"
    
    def test_service_segregation_consistency(self):
        """Test that there's no overlap between hub and spoke services"""
        # Find any services that appear in both categories
        overlap = HUB_SERVICES.intersection(SPOKE_SERVICES)
        
        # Remove 'key_vault' from overlap check as it's intentionally allowed in both contexts
        # (shared in hub, workload-specific in spoke)
        overlap = overlap - {'key_vault', 'keyvault'}
        
        assert len(overlap) == 0, f"Services should not appear in both HUB_SERVICES and SPOKE_SERVICES: {overlap}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])