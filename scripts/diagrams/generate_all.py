import os
from importlib import import_module

# Ensure output folder exists
os.makedirs("docs/diagrams", exist_ok=True)

# Import modules to trigger diagram generation
for mod in ["scripts.diagrams.network", "scripts.diagrams.security", "scripts.diagrams.integration", "scripts.diagrams.data"]:
    import_module(mod)

print("Diagrams generated in docs/diagrams/")