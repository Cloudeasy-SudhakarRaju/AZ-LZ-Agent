from diagrams import Edge

# Global styling helpers for consistency across diagrams
GRAPH_ATTR = {
    "pad": "0.5",
    "nodesep": "0.6",
    "ranksep": "0.8",
    "splines": "ortho",     # straighter connectors, fewer crossings
    "rankdir": "LR",        # enforce left-to-right
    "fontname": "Inter",
    "fontsize": "11",
    "labelloc": "t",
}

NODE_ATTR = {
    "fontsize": "10",
    "width": "1.6",
    "height": "1.2",
    "fontname": "Inter",
}

# Palette
COLOR_PRIMARY = "#2E86C1"
COLOR_REPL    = "#7D3C98"
COLOR_CTRL    = "#566573"

# Domain cluster fills
FILL_NETWORK     = "#E9F7EF"
FILL_SECURITY    = "#FDECEE"
FILL_INTEGRATION = "#F4ECF7"
FILL_DATA        = "#EBF5FB"

def step(label: str, color: str = COLOR_PRIMARY, style: str = "solid", penwidth: str = "1.4"):
    "Convenience to label edges with step numbers or callouts."
    return Edge(label=label, color=color, style=style, penwidth=penwidth)

def primary():
    return Edge(color=COLOR_PRIMARY, penwidth="1.4")

def repl():
    return Edge(color=COLOR_REPL, style="dashed", penwidth="1.2")

def ctrl():
    return Edge(color=COLOR_CTRL, style="dotted", penwidth="1.0")