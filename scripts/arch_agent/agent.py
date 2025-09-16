#!/usr/bin/env python3
"""
Architecture Diagram Agent CLI.
Generates organized Azure diagrams from user intent with dependency inference.
"""
import argparse
import os
import sys
import yaml
from typing import Dict, Any, List, Optional

# Add the repository root to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, repo_root)

from scripts.arch_agent.schemas import Requirements, UserIntent
from scripts.arch_agent.catalog import ServiceCatalog
from scripts.arch_agent.layout import LayoutComposer
from scripts.arch_agent.render import DiagramRenderer


class ArchitectureDiagramAgent:
    """Main agent class that orchestrates diagram generation."""
    
    def __init__(self):
        self.catalog = ServiceCatalog()
        self.composer = LayoutComposer(self.catalog)
        self.renderer = DiagramRenderer()
    
    def generate_from_manifest(self, manifest_path: str, pattern: str = "ha-multiregion", output_path: str = None) -> str:
        """
        Generate diagram from a YAML manifest file.
        
        Args:
            manifest_path: Path to YAML manifest file
            pattern: Layout pattern to use
            output_path: Output file path (without extension)
            
        Returns:
            Path to generated PNG file
        """
        # Load and validate manifest
        requirements = self._load_manifest(manifest_path)
        
        # Validate requirements
        validation_errors = self.composer.validate_requirements(requirements)
        if validation_errors:
            raise ValueError(f"Validation errors: {'; '.join(validation_errors)}")
        
        # Generate layout
        layout_graph = self.composer.compose_layout(requirements, pattern)
        
        # Render diagram
        if not output_path:
            output_path = "docs/diagrams/architecture"
        
        return self.renderer.render(layout_graph, output_path, "Azure Architecture")
    
    def generate_interactive(self, pattern: str = "ha-multiregion", output_path: str = None) -> str:
        """
        Generate diagram through interactive prompts.
        
        Args:
            pattern: Layout pattern to use
            output_path: Output file path (without extension)
            
        Returns:
            Path to generated PNG file
        """
        print("🚀 Azure Architecture Diagram Agent")
        print("====================================")
        print()
        
        # Gather basic requirements
        requirements = self._gather_requirements()
        
        # Gather service selections
        self._gather_services(requirements)
        
        # Handle missing configurations
        self._handle_missing_configurations(requirements)
        
        # Validate and generate
        validation_errors = self.composer.validate_requirements(requirements)
        if validation_errors:
            print("❌ Validation errors:")
            for error in validation_errors:
                print(f"   - {error}")
            return None
        
        # Generate layout
        print("🔄 Generating layout...")
        layout_graph = self.composer.compose_layout(requirements, pattern)
        
        # Render diagram
        if not output_path:
            output_path = "docs/diagrams/architecture"
        
        print("🎨 Rendering diagram...")
        output_file = self.renderer.render(layout_graph, output_path, "Azure Architecture")
        
        print(f"✅ Architecture diagram generated: {output_file}")
        return output_file
    
    def _load_manifest(self, manifest_path: str) -> Requirements:
        """Load requirements from YAML manifest."""
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert to Requirements object
        return Requirements(**data)
    
    def _gather_requirements(self) -> Requirements:
        """Interactively gather basic requirements."""
        print("📋 Basic Requirements")
        print("--------------------")
        
        # Project name
        project_name = input("Project name (optional): ").strip() or None
        
        # Environment
        environment = input("Environment [prod]: ").strip() or "prod"
        
        # Regions
        print("\nRegions (comma-separated):")
        print("Examples: East US 2, West US 2")
        regions_input = input("Regions [East US 2]: ").strip()
        if regions_input:
            regions = [r.strip() for r in regions_input.split(",")]
        else:
            regions = ["East US 2"]
        
        # HA Mode
        print("\nHigh Availability Mode:")
        print("  1. single-region")
        print("  2. multi-region")
        print("  3. active-passive")
        print("  4. active-active")
        ha_choice = input("Choice [1]: ").strip() or "1"
        ha_modes = ["single-region", "multi-region", "active-passive", "active-active"]
        ha_mode = ha_modes[int(ha_choice) - 1] if ha_choice.isdigit() and 1 <= int(ha_choice) <= 4 else "single-region"
        
        return Requirements(
            project_name=project_name,
            environment=environment,
            regions=regions,
            ha_mode=ha_mode,
            services=[]
        )
    
    def _gather_services(self, requirements: Requirements) -> None:
        """Interactively gather service selections."""
        print()
        print("🔧 Service Selection")
        print("-------------------")
        
        categories = self.catalog.get_categories()
        
        print("Available service categories:")
        for i, category in enumerate(categories.keys(), 1):
            print(f"  {i}. {category}")
        
        while True:
            print()
            choice = input("Select category (number) or 'done' to finish: ").strip()
            
            if choice.lower() == "done":
                break
            
            if not choice.isdigit():
                continue
            
            category_idx = int(choice) - 1
            category_names = list(categories.keys())
            
            if 0 <= category_idx < len(category_names):
                category = category_names[category_idx]
                self._select_services_from_category(requirements, category, categories[category])
        
        if not requirements.services:
            print("⚠️  No services selected. Adding a default web application...")
            requirements.services.append(UserIntent(kind="web_app", name="Web App"))
    
    def _select_services_from_category(self, requirements: Requirements, category: str, service_types: List[str]) -> None:
        """Select services from a specific category."""
        print(f"\n{category.title()} services:")
        for i, service_type in enumerate(service_types, 1):
            service_def = self.catalog.get_service(service_type)
            print(f"  {i}. {service_def.name if service_def else service_type}")
        
        selections = input("Select services (comma-separated numbers): ").strip()
        if not selections:
            return
        
        for selection in selections.split(","):
            selection = selection.strip()
            if selection.isdigit():
                service_idx = int(selection) - 1
                if 0 <= service_idx < len(service_types):
                    service_type = service_types[service_idx]
                    service_def = self.catalog.get_service(service_type)
                    name = service_def.name if service_def else service_type
                    
                    intent = UserIntent(kind=service_type, name=name)
                    requirements.services.append(intent)
                    print(f"   ✅ Added {name}")
    
    def _handle_missing_configurations(self, requirements: Requirements) -> None:
        """Handle missing service configurations through prompts."""
        missing_configs = self.composer.get_missing_configurations(requirements)
        
        if not missing_configs:
            return
        
        print()
        print("⚙️  Service Configuration")
        print("------------------------")
        print("Some services need additional configuration. Press Enter to use defaults.")
        print()
        
        for service_name, prompts in missing_configs.items():
            print(f"📝 {service_name}:")
            for prompt in prompts:
                answer = input(f"   {prompt}: ").strip()
                if answer:
                    # In a full implementation, we'd store these answers
                    # For now, we'll just collect them
                    pass
            print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Azure architecture diagrams from user intent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Non-interactive mode with manifest
  python agent.py --manifest examples/sample_ha.yaml --pattern ha-multiregion
  
  # Interactive mode
  python agent.py --interactive
  
  # Custom output path
  python agent.py --manifest examples/sample_ha.yaml --out docs/diagrams/my_architecture
        """
    )
    
    parser.add_argument(
        "--manifest",
        help="Path to YAML manifest file (non-interactive mode)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode with Q&A prompts"
    )
    
    parser.add_argument(
        "--pattern",
        default="ha-multiregion",
        choices=["ha-multiregion"],
        help="Layout pattern to use (default: ha-multiregion)"
    )
    
    parser.add_argument(
        "--out",
        default="docs/diagrams/architecture",
        help="Output file path without extension (default: docs/diagrams/architecture)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.manifest and not args.interactive:
        parser.error("Either --manifest or --interactive must be specified")
    
    if args.manifest and args.interactive:
        parser.error("Cannot use both --manifest and --interactive modes")
    
    try:
        agent = ArchitectureDiagramAgent()
        
        if args.manifest:
            output_file = agent.generate_from_manifest(args.manifest, args.pattern, args.out)
            print(f"✅ Diagram generated: {output_file}")
        else:
            agent.generate_interactive(args.pattern, args.out)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()