# ODIM-MH Ontology Visualizations

This directory contains auto-generated visualizations of the ODIM-MH ontology structure.

## Available Visualizations

- `class-hierarchy.svg` - Class hierarchy visualization showing subclass relationships
- `object-properties.svg` - Object properties visualization including domains and ranges
- `data-properties.svg` - Data properties visualization including domains

## How to Generate

These visualizations are generated using the ontology tooling. Canonical outputs are:

- `class-hierarchy.svg`
- `object-properties.svg`
- `data-properties.svg`

```bash
# Rebuild the Docker image with Graphviz support
tooling/run_ontology_tools.sh build

# Generate all visualizations (also refreshes canonical SVGs)
tooling/run_ontology_tools.sh visualize-all mhm_ontology.owl

# Generate individual visualizations
tooling/run_ontology_tools.sh visualize-classes mhm_ontology.owl
tooling/run_ontology_tools.sh visualize-objproperties mhm_ontology.owl
tooling/run_ontology_tools.sh visualize-dataproperties mhm_ontology.owl
```

## Implementation

Implementation notes:
- SPARQL-based Python generators in `tooling/` produce DOT files for classes, object properties, and data properties.
- Graphviz renders DOT to SVG.
- A local `.gitignore` in this folder ignores generated DOTs and engine-suffixed variants; only the three canonical SVGs are tracked.
