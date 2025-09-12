# ODIM-MH Ontology Visualizations

This directory contains auto-generated visualizations of the ODIM-MH ontology structure.

## Available Visualizations

- `class-hierarchy.svg` - Class hierarchy visualization showing subclass relationships
- `object-properties.svg` - Object properties visualization including domains and ranges
- `data-properties.svg` - Data properties visualization including domains

## How to Generate

These visualizations are generated using the ontology tooling:

```bash
# Rebuild the Docker image with Graphviz support
tooling/run_ontology_tools.sh build

# Generate all visualizations
tooling/run_ontology_tools.sh visualize-all mhm_ontology.owl

# Generate individual visualizations
tooling/run_ontology_tools.sh visualize-classes mhm_ontology.owl
tooling/run_ontology_tools.sh visualize-objproperties mhm_ontology.owl
tooling/run_ontology_tools.sh visualize-dataproperties mhm_ontology.owl
```

## Implementation

The visualizations are created using:
- Python script to convert OWL to DOT format (`tooling/owl2dot.py`)
- Graphviz to render the DOT files as SVG
- Integration into the standard ontology tooling
