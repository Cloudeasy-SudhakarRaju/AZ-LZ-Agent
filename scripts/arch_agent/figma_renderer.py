"""
Figma-based renderer that creates diagrams using the Figma API.
Provides an alternative to the existing DiagramRenderer for cloud-based diagram generation.
"""
import os
import json
import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from .schemas import LayoutGraph, LayoutNode, LayoutEdge

# Configure logging
logger = logging.getLogger(__name__)


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
            logger.info(f"Starting Figma diagram render for file_id: {file_id}, page: {page_name}")
            
            # Validate inputs
            if not graph or not graph.nodes:
                raise ValueError("Graph is empty or has no nodes to render")
            
            # Create or get the Figma file
            if file_id:
                logger.info(f"Using existing Figma file: {file_id}")
                figma_file_id = file_id
                # Validate file access first
                self._validate_file_access(figma_file_id)
            else:
                logger.info("Creating new Figma file")
                figma_file_id = self._create_figma_file(page_name)
            
            # Get the file structure to find the page
            logger.info(f"Getting or creating page: {page_name}")
            page_id = self._get_or_create_page(figma_file_id, page_name)
            
            # Calculate layout positions for nodes
            logger.info(f"Calculating layout for {len(graph.nodes)} nodes")
            node_positions = self._calculate_layout(graph)
            
            # Create the diagram elements
            logger.info("Creating main frame")
            frame_id = self._create_main_frame(figma_file_id, page_id, page_name)
            
            logger.info("Creating nodes")
            node_map = self._create_nodes(figma_file_id, frame_id, graph.nodes, node_positions)
            
            logger.info(f"Creating {len(graph.edges)} connections")
            self._create_connections(figma_file_id, frame_id, graph.edges, node_map, node_positions)
            
            # Return the Figma file URL
            figma_url = f"https://www.figma.com/file/{figma_file_id}"
            logger.info(f"Figma diagram successfully created: {figma_url}")
            return figma_url
            
        except Exception as e:
            logger.error(f"Failed to render diagram in Figma: {str(e)}")
            raise RuntimeError(f"Failed to render diagram in Figma: {str(e)}")
    
    def _create_figma_file(self, name: str) -> str:
        """Create a new Figma file."""
        # Note: Figma API doesn't support creating files via API
        # This would require using Figma's file duplication or team file creation
        # For now, we'll raise an informative error
        logger.error("Attempted to create new Figma file via API - not supported")
        raise NotImplementedError(
            "Creating new Figma files via API is not supported. "
            "Please provide an existing file_id or create a file manually in Figma."
        )
    
    def _validate_file_access(self, file_id: str) -> bool:
        """Validate that the file exists and is accessible with the current token."""
        try:
            logger.info(f"Validating access to Figma file: {file_id}")
            response = requests.get(f"{self.base_url}/files/{file_id}", headers=self.headers, timeout=10)
            
            if response.status_code == 403:
                logger.error(f"Access denied to Figma file {file_id} - check token permissions")
                raise PermissionError(f"Access denied to Figma file {file_id}. Check that your Figma API token has access to this file.")
            elif response.status_code == 404:
                logger.error(f"Figma file {file_id} not found")
                raise FileNotFoundError(f"Figma file {file_id} not found. Please check the file ID.")
            elif response.status_code != 200:
                logger.error(f"Figma API error: {response.status_code} - {response.text}")
                raise ConnectionError(f"Figma API error {response.status_code}: {response.text}")
            
            file_data = response.json()
            logger.info(f"File access validated. File name: {file_data.get('name', 'Unknown')}")
            return True
            
        except requests.exceptions.Timeout:
            logger.error("Timeout while accessing Figma file")
            raise TimeoutError("Timeout while accessing Figma file")
        except requests.exceptions.ConnectionError:
            logger.error("Network error while accessing Figma API")
            raise ConnectionError("Network error while accessing Figma API")
    
    def _get_or_create_page(self, file_id: str, page_name: str) -> str:
        """Get existing page or create a new one."""
        try:
            logger.info(f"Getting file structure for {file_id}")
            # Get file structure
            response = requests.get(f"{self.base_url}/files/{file_id}", headers=self.headers, timeout=10)
            response.raise_for_status()
            
            file_data = response.json()
            logger.info(f"File retrieved successfully. Name: {file_data.get('name', 'Unknown')}")
            
            # Look for existing page with the name
            pages = file_data.get("document", {}).get("children", [])
            logger.info(f"Found {len(pages)} pages in file")
            
            for page in pages:
                if page.get("name") == page_name:
                    logger.info(f"Found existing page '{page_name}' with ID: {page.get('id')}")
                    return page.get("id")
            
            # If no existing page found, use the first page and rename it
            if pages:
                page_id = pages[0]["id"]
                logger.info(f"Using first page (ID: {page_id}) for diagram - page renaming not implemented")
                # Note: Renaming pages requires additional API calls not implemented yet
                return page_id
            
            logger.error("No pages found in Figma file")
            raise RuntimeError("No pages found in Figma file - file may be corrupted or empty")
            
        except requests.exceptions.Timeout:
            logger.error("Timeout while getting Figma file structure")
            raise TimeoutError("Timeout while getting Figma file structure")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while getting file structure: {e}")
            raise RuntimeError(f"HTTP error while accessing Figma file: {e}")
    
    def _create_main_frame(self, file_id: str, page_id: str, title: str) -> str:
        """Create the main frame for the diagram."""
        try:
            logger.info(f"Creating main frame '{title}' on page {page_id}")
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
                json={"nodes": [frame_data]},
                timeout=15
            )
            
            if response.status_code == 403:
                logger.error(f"Permission denied creating frame - check edit permissions")
                raise PermissionError("Permission denied creating frame. Ensure your Figma API token has edit permissions for this file.")
            
            response.raise_for_status()
            
            result = response.json()
            node_ids = result.get("node_ids", [])
            
            if not node_ids:
                logger.error("No node IDs returned from frame creation")
                raise RuntimeError("Failed to create main frame - no node ID returned")
            
            frame_id = node_ids[0]
            logger.info(f"Main frame created successfully with ID: {frame_id}")
            return frame_id
            
        except requests.exceptions.Timeout:
            logger.error("Timeout while creating main frame")
            raise TimeoutError("Timeout while creating main frame")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while creating frame: {e}")
            raise RuntimeError(f"HTTP error while creating frame: {e}")
    
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
            logger.warning("No Figma API token provided")
            return False
        
        if not token.startswith('figd_'):
            logger.warning("Figma API token does not start with 'figd_' - may be invalid format")
        
        headers = {"X-Figma-Token": token}
        try:
            logger.info("Validating Figma API token")
            response = requests.get("https://api.figma.com/v1/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Token validated successfully for user: {user_data.get('name', 'Unknown')}")
                return True
            elif response.status_code == 403:
                logger.warning("Figma API token is invalid or expired")
                return False
            else:
                logger.warning(f"Figma API token validation failed with status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while validating Figma API token")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Network error while validating Figma API token")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating Figma API token: {e}")
            return False
    
    @staticmethod
    def get_user_info(token: str) -> Optional[Dict[str, Any]]:
        """Get user information for the provided token."""
        if not token:
            logger.warning("No token provided for user info")
            return None
            
        headers = {"X-Figma-Token": token}
        try:
            logger.info("Getting Figma user info")
            response = requests.get("https://api.figma.com/v1/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"User info retrieved for: {user_data.get('name', 'Unknown')}")
                return user_data
            else:
                logger.warning(f"Failed to get user info: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while getting Figma user info")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Network error while getting Figma user info")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting Figma user info: {e}")
            return None