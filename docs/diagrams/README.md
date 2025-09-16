# Generated Architecture Diagrams (mingrammer/diagrams)

This folder contains PNG outputs for domain-specific Azure architecture diagrams.

How to regenerate:
1. pip install diagrams graphviz
2. Ensure Graphviz is installed and on PATH.
3. python scripts/diagrams/generate_all.py

Conventions:
- Left-to-right flow, minimal crossings (`splines=ortho`)
- Domain swimlanes using clusters with a consistent palette
- Step numbers on primary paths (`Edge(label="n")`)
- Buses to reduce fan-in/fan-out complexity