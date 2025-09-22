# Azure Diagram Generation Scripts

This directory contains Python scripts for generating professional Azure architecture diagrams using the `diagrams` library with official Microsoft Azure icons.

## Structure

- `style.py` - Common styling constants and helper functions for consistent diagram appearance
- `network.py` - Network architecture diagram generation
- `security.py` - Security architecture diagram generation  
- `integration.py` - Integration architecture diagram generation
- `data.py` - Data architecture diagram generation
- `generate_all.py` - Script to generate all diagrams at once

## Usage

### Generate All Diagrams
```bash
python scripts/diagrams/generate_all.py
```

### Generate Individual Diagrams
From the repository root:
```bash
python -c "import scripts.diagrams.network"
python -c "import scripts.diagrams.security"
python -c "import scripts.diagrams.integration"
python -c "import scripts.diagrams.data"
```

## Output

All diagrams are generated as PNG files in the `docs/diagrams/` directory:
- `network.png` - Azure network topology
- `security.png` - Security and identity architecture
- `integration.png` - Integration and messaging architecture
- `data.png` - Data platform architecture

## Dependencies

- `diagrams>=0.23.4` - Python diagrams library
- `graphviz>=0.20.1` - Python Graphviz wrapper
- System Graphviz installation (`apt-get install graphviz`)

## CI/CD

The GitHub workflow in `.github/workflows/generate-diagrams.yml` automatically generates diagrams when changes are made to the scripts.