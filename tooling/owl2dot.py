#!/usr/bin/env python3
"""
Convert OWL ontology to DOT format for Graphviz visualization

Usage:
  python3 owl2dot.py --input FILE.owl --output FILE.dot [--type TYPE] [--format FORMAT]

Options:
  --input FILE.owl   Input OWL file
  --output FILE.dot  Output DOT file
  --type TYPE        Type of visualization: classes (default), objproperties, dataproperties, all
  --format FORMAT    Output format: dot (default), svg, png, pdf

Examples:
  python3 owl2dot.py --input mhm_ontology.owl --output class-hierarchy.dot --type classes
  python3 owl2dot.py --input mhm_ontology.owl --output obj-properties.dot --type objproperties
"""

import argparse
import os
import subprocess
import tempfile
from rdflib import Graph, RDF, RDFS, OWL, URIRef

def parse_args():
    parser = argparse.ArgumentParser(description='Convert OWL ontology to DOT format for visualization')
    parser.add_argument('--input', required=True, help='Input OWL file')
    parser.add_argument('--output', required=True, help='Output DOT file (or SVG/PNG/PDF with --format)')
    parser.add_argument('--type', choices=['classes', 'objproperties', 'dataproperties', 'all'], 
                        default='classes', help='Type of visualization')
    parser.add_argument('--format', choices=['dot', 'svg', 'png', 'pdf'], 
                        default='dot', help='Output format')
    return parser.parse_args()

def load_ontology(input_file):
    """Load an OWL ontology into an RDFLib graph"""
    g = Graph()
    print(f"Loading ontology: {input_file}")
    g.parse(input_file)
    print(f"Loaded {len(g)} triples")
    return g

def get_label(g, entity, default=""):
    """Get label for an entity, or return the URI fragment if no label exists"""
    for label in g.objects(entity, RDFS.label):
        return str(label)
    
    # No label found, extract fragment from URI
    uri = str(entity)
    if '#' in uri:
        return uri.split('#')[-1]
    return uri.split('/')[-1] if default == "" else default

def get_class_hierarchy(g):
    """Extract class hierarchy as list of (parent, child) tuples"""
    hierarchy = []
    
    # Find all owl:Class entities
    for cls in g.subjects(RDF.type, OWL.Class):
        if isinstance(cls, URIRef):  # Skip blank nodes
            # Add subclass relationships
            for parent in g.objects(cls, RDFS.subClassOf):
                if isinstance(parent, URIRef):  # Skip blank nodes & restrictions
                    hierarchy.append((parent, cls))
    
    return hierarchy

def get_object_properties(g):
    """Extract object property hierarchy and domain/range information"""
    props = []
    domains_ranges = []
    
    # Find all owl:ObjectProperty entities
    for prop in g.subjects(RDF.type, OWL.ObjectProperty):
        if isinstance(prop, URIRef):
            # Add subproperty relationships
            for parent in g.objects(prop, RDFS.subPropertyOf):
                if isinstance(parent, URIRef):
                    props.append((parent, prop))
            
            # Add domain and range information
            for domain in g.objects(prop, RDFS.domain):
                if isinstance(domain, URIRef):
                    domains_ranges.append((domain, prop, "domain"))
            
            for range_cls in g.objects(prop, RDFS.range):
                if isinstance(range_cls, URIRef):
                    domains_ranges.append((prop, range_cls, "range"))
    
    return props, domains_ranges

def get_data_properties(g):
    """Extract data property hierarchy and domain information"""
    props = []
    domains = []
    
    # Find all owl:DatatypeProperty entities
    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        if isinstance(prop, URIRef):
            # Add subproperty relationships
            for parent in g.objects(prop, RDFS.subPropertyOf):
                if isinstance(parent, URIRef):
                    props.append((parent, prop))
            
            # Add domain information
            for domain in g.objects(prop, RDFS.domain):
                if isinstance(domain, URIRef):
                    domains.append((domain, prop))
    
    return props, domains

def generate_class_dot(g, class_hierarchy):
    """Generate DOT format for class hierarchy"""
    dot = []
    dot.append('digraph "Class Hierarchy" {')
    dot.append('  rankdir=BT;')
    dot.append('  node [shape=box, style=filled, fillcolor=lightblue];')
    
    # Add nodes (classes)
    added_classes = set()
    for parent, child in class_hierarchy:
        if parent not in added_classes:
            parent_label = get_label(g, parent)
            dot.append(f'  "{parent}" [label="{parent_label}"];')
            added_classes.add(parent)
        
        if child not in added_classes:
            child_label = get_label(g, child)
            dot.append(f'  "{child}" [label="{child_label}"];')
            added_classes.add(child)
    
    # Add edges (subclass relationships)
    for parent, child in class_hierarchy:
        dot.append(f'  "{child}" -> "{parent}" [label="rdfs:subClassOf"];')
    
    dot.append('}')
    return '\n'.join(dot)

def generate_objprop_dot(g, prop_hierarchy, domains_ranges):
    """Generate DOT format for object property hierarchy"""
    dot = []
    dot.append('digraph "Object Properties" {')
    dot.append('  rankdir=BT;')
    dot.append('  node [shape=box, style=filled];')
    
    # Add nodes (properties)
    added_props = set()
    for parent, child in prop_hierarchy:
        if parent not in added_props:
            parent_label = get_label(g, parent)
            dot.append(f'  "{parent}" [label="{parent_label}", fillcolor=lightgreen];')
            added_props.add(parent)
        
        if child not in added_props:
            child_label = get_label(g, child)
            dot.append(f'  "{child}" [label="{child_label}", fillcolor=lightgreen];')
            added_props.add(child)
    
    # Add class nodes for domains and ranges
    added_classes = set()
    for item1, item2, rel_type in domains_ranges:
        if rel_type == "domain":
            domain, prop = item1, item2
            if domain not in added_classes:
                domain_label = get_label(g, domain)
                dot.append(f'  "{domain}" [label="{domain_label}", fillcolor=lightblue];')
                added_classes.add(domain)
        elif rel_type == "range":
            prop, range_cls = item1, item2
            if range_cls not in added_classes:
                range_label = get_label(g, range_cls)
                dot.append(f'  "{range_cls}" [label="{range_label}", fillcolor=lightblue];')
                added_classes.add(range_cls)
    
    # Add edges (subproperty relationships)
    for parent, child in prop_hierarchy:
        dot.append(f'  "{child}" -> "{parent}" [label="rdfs:subPropertyOf"];')
    
    # Add domain/range edges
    for item1, item2, rel_type in domains_ranges:
        if rel_type == "domain":
            domain, prop = item1, item2
            dot.append(f'  "{prop}" -> "{domain}" [label="rdfs:domain", style="dashed"];')
        elif rel_type == "range":
            prop, range_cls = item1, item2
            dot.append(f'  "{prop}" -> "{range_cls}" [label="rdfs:range", style="dotted"];')
    
    dot.append('}')
    return '\n'.join(dot)

def generate_dataprop_dot(g, prop_hierarchy, domains):
    """Generate DOT format for data property hierarchy"""
    dot = []
    dot.append('digraph "Data Properties" {')
    dot.append('  rankdir=BT;')
    dot.append('  node [shape=box, style=filled];')
    
    # Add nodes (properties)
    added_props = set()
    for parent, child in prop_hierarchy:
        if parent not in added_props:
            parent_label = get_label(g, parent)
            dot.append(f'  "{parent}" [label="{parent_label}", fillcolor=lightyellow];')
            added_props.add(parent)
        
        if child not in added_props:
            child_label = get_label(g, child)
            dot.append(f'  "{child}" [label="{child_label}", fillcolor=lightyellow];')
            added_props.add(child)
    
    # Add class nodes for domains
    added_classes = set()
    for domain, prop in domains:
        if domain not in added_classes:
            domain_label = get_label(g, domain)
            dot.append(f'  "{domain}" [label="{domain_label}", fillcolor=lightblue];')
            added_classes.add(domain)
    
    # Add edges (subproperty relationships)
    for parent, child in prop_hierarchy:
        dot.append(f'  "{child}" -> "{parent}" [label="rdfs:subPropertyOf"];')
    
    # Add domain edges
    for domain, prop in domains:
        dot.append(f'  "{prop}" -> "{domain}" [label="rdfs:domain", style="dashed"];')
    
    dot.append('}')
    return '\n'.join(dot)

def save_dot(dot_content, output_file):
    """Save DOT content to file"""
    with open(output_file, 'w') as f:
        f.write(dot_content)
    print(f"DOT file saved to: {output_file}")

def convert_dot_to_format(dot_file, output_file, format_type):
    """Convert DOT to specified format using Graphviz"""
    try:
        subprocess.run(["dot", f"-T{format_type}", dot_file, "-o", output_file], check=True)
        print(f"{format_type.upper()} file saved to: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting DOT to {format_type}: {e}")
        return False

def main():
    args = parse_args()
    
    # Load ontology
    g = load_ontology(args.input)
    
    # Create output directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
    
    # Determine visualization type and create DOT content
    dot_content = None
    if args.type == 'classes' or args.type == 'all':
        hierarchy = get_class_hierarchy(g)
        dot_content = generate_class_dot(g, hierarchy)
    elif args.type == 'objproperties':
        prop_hierarchy, domains_ranges = get_object_properties(g)
        dot_content = generate_objprop_dot(g, prop_hierarchy, domains_ranges)
    elif args.type == 'dataproperties':
        prop_hierarchy, domains = get_data_properties(g)
        dot_content = generate_dataprop_dot(g, prop_hierarchy, domains)
    
    # Output based on format
    if args.format == 'dot':
        save_dot(dot_content, args.output)
    else:
        # For SVG/PNG/PDF, create temp DOT file and convert
        with tempfile.NamedTemporaryFile(suffix='.dot', delete=False) as tmp:
            tmp.write(dot_content.encode('utf-8'))
            tmp_name = tmp.name
        
        convert_dot_to_format(tmp_name, args.output, args.format)
        os.unlink(tmp_name)  # Clean up temp file

if __name__ == '__main__':
    main()
