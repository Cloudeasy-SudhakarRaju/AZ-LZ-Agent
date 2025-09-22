from diagrams import Edge

# Global styling helpers for consistency across diagrams
GRAPH_ATTR = {
    "pad": "0.8",
    "nodesep": "2.0",          # Enhanced node separation for clarity (req 2, 9)
    "ranksep": "3.0",          # Enhanced rank separation for visual hierarchy (req 3, 9)
    "splines": "polyline",     # Polyline routing for minimal crossings (req 2)
    "rankdir": "TB",           # Top-to-bottom for proper visual hierarchy (req 3)
    "fontname": "Segoe UI",    # Professional font for enterprise diagrams (req 9)
    "fontsize": "12",          # Improved readability (req 9)
    "labelloc": "t",
    "compound": "true",        # Allow edges between clusters (req 1)
    "concentrate": "false",    # Prevent edge merging for clarity (req 2)
    "remincross": "true",      # Minimize edge crossings (req 2)
    "ordering": "out",         # Consistent edge ordering (req 2)
    "overlap": "false",        # Prevent node overlaps (req 9)
    "sep": "+30,30",          # Enhanced separation (req 9)
    "esep": "+20,20",         # Enhanced edge separation (req 2)
    "bgcolor": "#ffffff",      # Clean background (req 9)
    "margin": "1.0,1.0",      # Better margins (req 9)
    "packmode": "cluster",    # Cluster-based packing for logical grouping (req 7)
    "maxiter": "1000",        # Better layout convergence
}

NODE_ATTR = {
    "fontsize": "11",
    "width": "2.0",           # Improved node sizing (req 9)
    "height": "1.5",          # Improved node sizing (req 9)
    "fontname": "Segoe UI",   # Professional font (req 9)
    "shape": "box",           # Consistent shape for Azure services (req 15)
    "style": "rounded,filled", # Professional appearance (req 9)
    "fillcolor": "#F8F9FA",   # Light background for readability (req 9)
    "color": "#495057",       # Professional border color (req 9)
    "penwidth": "1.5",        # Defined borders (req 9)
}

# Enhanced palette for enterprise diagram standards (req 12, 15)
COLOR_PRIMARY = "#0078D4"      # Azure blue
COLOR_SECONDARY = "#107C10"    # Azure green  
COLOR_WARNING = "#FF8C00"      # Azure orange
COLOR_DANGER = "#D13438"       # Azure red
COLOR_CTRL = "#6B7280"         # Management/control connections

# Enhanced domain cluster fills implementing security zoning (req 12)
FILL_INTERNET_EDGE = "#FFF5F5"    # Light red for internet/edge (DMZ)
FILL_IDENTITY_SECURITY = "#FFFAF0" # Light orange for identity/security
FILL_NETWORK = "#E9F7EF"          # Light green for networking (trusted)
FILL_COMPUTE = "#EBF5FB"          # Light blue for compute (trusted)
FILL_DATA = "#F3E8FF"             # Light purple for data (trusted)
FILL_MONITORING = "#FDF4E3"       # Light yellow for monitoring
FILL_STANDBY = "#F8F9FA"          # Light gray for standby/DR

# Environment labeling colors (req 14)
ENV_COLORS = {
    "dev": "#D1ECF1",      # Light blue
    "uat": "#FFF3CD",      # Light yellow  
    "prod": "#D4EDDA",     # Light green
    "dr": "#F8D7DA"        # Light red
}

def step(label: str, color: str = COLOR_PRIMARY, style: str = "solid", penwidth: str = "2.0"):
    """Convenience to label edges with step numbers for workflow numbering (req 8)."""
    return Edge(
        label=f" {label} ",  # Add spaces for better visibility
        color=color, 
        style=style, 
        penwidth=penwidth,
        fontsize="10",
        fontcolor="#FFFFFF",
        labelbgcolor=color,
        labelmargin="0.2"
    )

def primary(label: str = ""):
    """Primary connection edge with enhanced styling (req 9)."""
    return Edge(
        label=label,
        color=COLOR_PRIMARY, 
        penwidth="2.5",
        arrowsize="1.2",
        fontsize="10"
    )

def secondary(label: str = ""):
    """Secondary connection edge (req 9)."""
    return Edge(
        label=label,
        color=COLOR_SECONDARY, 
        style="dashed", 
        penwidth="2.0",
        arrowsize="1.1",
        fontsize="9"
    )

def ctrl(label: str = ""):
    """Control/management connection with dotted style (req 11, 14)."""
    return Edge(
        label=label,
        color=COLOR_CTRL, 
        style="dotted", 
        penwidth="1.5",
        arrowsize="1.0",
        fontsize="8"
    )

def data_flow(label: str = ""):
    """Data flow connection with distinctive styling (req 8, 14)."""
    return Edge(
        label=label,
        color=COLOR_SECONDARY,
        penwidth="3.0",
        arrowsize="1.3",
        fontsize="10",
        style="solid"
    )

def monitoring(label: str = ""):
    """Monitoring and observability connections (req 11)."""
    return Edge(
        label=label,
        color=COLOR_WARNING,
        style="dotted",
        penwidth="1.5",
        arrowsize="0.9",
        fontsize="8"
    )

def dr_connection(label: str = ""):
    """Disaster recovery connections (req 13)."""
    return Edge(
        label=label,
        color=COLOR_DANGER,
        style="dashed",
        penwidth="2.0",
        arrowsize="1.1",
        fontsize="9"
    )