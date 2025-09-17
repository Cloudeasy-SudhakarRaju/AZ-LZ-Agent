"""
Figma-based renderer that creates diagrams using the Figma API.
Provides an alternative to the existing DiagramRenderer for cloud-based diagram generation.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List, Tuple
from .schemas import LayoutGraph, LayoutNode, LayoutEdge


class FigmaRenderer:
    """
    Renders layout graphs as Figma diagrams using the Figma API.
    Creates diagrams with proper Azure service representations and layouts.
    """
    
    def __init__(self, api_token: str = None):
        """
        Initialize the Figma renderer with API credentials.
        
        Args:
            api_token: Figma API token. If None, will try to get from FIGMA_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv('FIGMA_API_TOKEN')
        if not self.api_token:
            raise ValueError("Figma API token is required. Set FIGMA_API_TOKEN environment variable or pass api_token parameter.")
        
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.api_token,
            "Content-Type": "application/json"
        }
        
        # Azure service styling configuration
        self.service_styles = {
            "vm": {"fill": "#0078D4", "stroke": "#106EBE", "icon": "🖥️"},
            "web_app": {"fill": "#00BCF2", "stroke": "#0099CC", "icon": "🌐"},
            "function_app": {"fill": "#FFB900", "stroke": "#CC9400", "icon": "⚡"},
            "storage_account": {"fill": "#00B7C3", "stroke": "#009299", "icon": "💾"},
            "sql_database": {"fill": "#E81123", "stroke": "#BA0E1F", "icon": "🗄️"},
            "redis": {"fill": "#DC382D", "stroke": "#B02E23", "icon": "⚡"},
            "vnet": {"fill": "#5C2D91", "stroke": "#4A2474", "icon": "🔗"},
            "load_balancer": {"fill": "#0078D4", "stroke": "#106EBE", "icon": "⚖️"},
            "application_gateway": {"fill": "#00BCF2", "stroke": "#0099CC", "icon": "🚪"},
            "key_vault": {"fill": "#FFB900", "stroke": "#CC9400", "icon": "🔑"},
            "default": {"fill": "#737373", "stroke": "#595959", "icon": "📦"}
        }
        
        # Layout configuration
        self.node_width = 120
        self.node_height = 80
        self.horizontal_spacing = 200
        self.vertical_spacing = 150
        
    def render(self, graph: LayoutGraph, file_id: str = None, page_name: str = "Azure Architecture") -> str:
        """
        Render a layout graph as a Figma diagram.
        
        Args:
            graph: Layout graph to render
            file_id: Existing Figma file ID. If None, creates a new file.
            page_name: Name for the diagram page
            
        Returns:
            URL to the generated Figma file
        """
        try:
            # Create or get the Figma file
            if file_id:
                figma_file_id = file_id
            else:
                figma_file_id = self._create_figma_file(page_name)
            
            # Get the file structure to find the page
            page_id = self._get_or_create_page(figma_file_id, page_name)
            
            # Calculate layout positions for nodes
            node_positions = self._calculate_layout(graph)
            
            # Create the diagram elements
            frame_id = self._create_main_frame(figma_file_id, page_id, page_name)
            node_map = self._create_nodes(figma_file_id, frame_id, graph.nodes, node_positions)
            self._create_connections(figma_file_id, frame_id, graph.edges, node_map, node_positions)
            
            # Return the Figma file URL
            return f"https://www.figma.com/file/{figma_file_id}"
            
        except Exception as e:
            raise RuntimeError(f"Failed to render diagram in Figma: {str(e)}")
    
    def _create_figma_file(self, name: str) -> str:
        """Create a new Figma file."""
        # Note: Figma API doesn't support creating files via API
        # This would require using Figma's file duplication or team file creation
        # For now, we'll raise an informative error
        raise NotImplementedError(
            "Creating new Figma files via API is not supported. "
            "Please provide an existing file_id or create a file manually in Figma."
        )
    
    def _get_or_create_page(self, file_id: str, page_name: str) -> str:
        """Get existing page or create a new one."""
        # Get file structure
        response = requests.get(f"{self.base_url}/files/{file_id}", headers=self.headers)
        response.raise_for_status()
        
        file_data = response.json()
        
        # Look for existing page with the name
        for page in file_data.get("document", {}).get("children", []):
            if page.get("name") == page_name:
                return page.get("id")
        
        # If no existing page found, use the first page and rename it
        if file_data.get("document", {}).get("children"):
            page_id = file_data["document"]["children"][0]["id"]
            # Note: Renaming pages requires additional API calls
            return page_id
        
        raise RuntimeError("No pages found in Figma file")
    
    def _create_main_frame(self, file_id: str, page_id: str, title: str) -> str:
        """Create the main frame for the diagram."""
        frame_data = {
            "type": "FRAME",
            "name": title,
            "x": 0,
            "y": 0,
            "width": 1200,
            "height": 800,
            "fills": [{"type": "SOLID", "color": {"r": 0.98, "g": 0.98, "b": 0.98}}],
            "children": []
        }
        
        # Add the frame to the page
        response = requests.post(
            f"{self.base_url}/files/{file_id}/nodes/{page_id}/children",
            headers=self.headers,
            json={"nodes": [frame_data]}
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get("node_ids", [])[0] if result.get("node_ids") else None
    
    def _calculate_layout(self, graph: LayoutGraph) -> Dict[str, Tuple[float, float]]:
        """Calculate positions for all nodes in the graph."""
        positions = {}
        
        # Group nodes by clusters for better layout
        clusters = {}
        standalone_nodes = []
        
        for node in graph.nodes:
            if node.cluster:
                if node.cluster not in clusters:
                    clusters[node.cluster] = []
                clusters[node.cluster].append(node)
            else:
                standalone_nodes.append(node)
        
        # Layout clusters and standalone nodes
        current_x = 50
        current_y = 100
        
        # Place clusters
        for cluster_name, cluster_nodes in clusters.items():
            cluster_x = current_x
            cluster_y = current_y
            
            # Arrange nodes within cluster
            for i, node in enumerate(cluster_nodes):
                node_x = cluster_x + (i % 3) * self.horizontal_spacing
                node_y = cluster_y + (i // 3) * self.vertical_spacing
                positions[node.id] = (node_x, node_y)
            
            current_x += 3 * self.horizontal_spacing + 100
            if current_x > 1000:  # Wrap to next row
                current_x = 50
                current_y += 300
        
        # Place standalone nodes
        for i, node in enumerate(standalone_nodes):
            node_x = current_x + (i % 4) * self.horizontal_spacing
            node_y = current_y + (i // 4) * self.vertical_spacing
            positions[node.id] = (node_x, node_y)
        
        return positions
    
    def _create_nodes(self, file_id: str, frame_id: str, nodes: List[LayoutNode], positions: Dict[str, Tuple[float, float]]) -> Dict[str, str]:
        """Create Figma nodes for each graph node."""
        node_map = {}
        
        for node in nodes:
            x, y = positions.get(node.id, (0, 0))
            style = self.service_styles.get(node.service_type, self.service_styles["default"])
            
            # Create a rectangle with text for each service
            node_data = {
                "type": "FRAME",
                "name": node.name,
                "x": x,
                "y": y,
                "width": self.node_width,
                "height": self.node_height,
                "fills": [{"type": "SOLID", "color": self._hex_to_rgb(style["fill"])}],
                "strokes": [{"type": "SOLID", "color": self._hex_to_rgb(style["stroke"])}],
                "strokeWeight": 2,
                "cornerRadius": 8,
                "children": [
                    {
                        "type": "TEXT",
                        "name": f"{node.name}_text",
                        "x": 10,
                        "y": 10,
                        "width": self.node_width - 20,
                        "height": self.node_height - 20,
                        "characters": f"{style['icon']}\n{node.name}",
                        "style": {
                            "fontFamily": "Inter",
                            "fontSize": 12,
                            "fontWeight": 500,
                            "textAlignHorizontal": "CENTER",
                            "textAlignVertical": "CENTER"
                        }
                    }
                ]
            }
            
            # Add node to frame
            response = requests.post(
                f"{self.base_url}/files/{file_id}/nodes/{frame_id}/children",
                headers=self.headers,
                json={"nodes": [node_data]}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("node_ids"):
                    node_map[node.id] = result["node_ids"][0]
        
        return node_map
    
    def _create_connections(self, file_id: str, frame_id: str, edges: List[LayoutEdge], 
                          node_map: Dict[str, str], positions: Dict[str, Tuple[float, float]]):
        """Create connections between nodes."""
        for edge in edges:
            source_pos = positions.get(edge.source)
            target_pos = positions.get(edge.target)
            
            if source_pos and target_pos:
                # Create a line between the nodes
                line_data = {
                    "type": "VECTOR",
                    "name": f"connection_{edge.source}_{edge.target}",
                    "vectorPaths": [
                        {
                            "windingRule": "NONZERO",
                            "data": f"M {source_pos[0] + self.node_width/2} {source_pos[1] + self.node_height/2} L {target_pos[0] + self.node_width/2} {target_pos[1] + self.node_height/2}"
                        }
                    ],
                    "strokes": [{"type": "SOLID", "color": {"r": 0.2, "g": 0.2, "b": 0.2}}],
                    "strokeWeight": 2
                }
                
                # Add line to frame
                requests.post(
                    f"{self.base_url}/files/{file_id}/nodes/{frame_id}/children",
                    headers=self.headers,
                    json={"nodes": [line_data]}
                )
    
    def _hex_to_rgb(self, hex_color: str) -> Dict[str, float]:
        """Convert hex color to RGB values for Figma API."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return {"r": r, "g": g, "b": b}


class FigmaConfig:
    """Configuration helper for Figma API settings."""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate a Figma API token."""
        if not token:
            return False
        
        headers = {"X-Figma-Token": token}
        try:
            response = requests.get("https://api.figma.com/v1/me", headers=headers)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    def get_user_info(token: str) -> Optional[Dict[str, Any]]:
        """Get user information for the provided token."""
        headers = {"X-Figma-Token": token}
        try:
            response = requests.get("https://api.figma.com/v1/me", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None