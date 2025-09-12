#!/usr/bin/env python3
"""
Generate data properties visualization from OWL ontology
"""
import sys
import subprocess
import csv
import io
import argparse
from collections import defaultdict

def extract_local_name(uri):
    """Extract local name from URI"""
    if '#' in uri:
        return uri.split('#')[-1]
    elif '/' in uri:
        return uri.split('/')[-1]
    return uri

def run_sparql_query(owl_file, query):
    """Run SPARQL query and return CSV results"""
    with open('/tmp/query.rq', 'w') as f:
        f.write(query)
    
    result = subprocess.run([
        'sparql', '--data', owl_file, '--query', '/tmp/query.rq', '--results=CSV'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"SPARQL query failed: {result.stderr}", file=sys.stderr)
        return []
    
    # Parse CSV output
    csv_reader = csv.DictReader(io.StringIO(result.stdout))
    return list(csv_reader)

def generate_data_properties_dot(owl_file, output_file, layout_engine='dot', use_clustering=True):
    """Generate DOT file for data properties"""
    
    # Query for data properties and their domains/ranges
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?prop ?domain ?range 
           ?propLabelEn ?propLabelAny 
           ?domainLabelEn ?domainLabelAny
    WHERE {
      ?prop rdf:type owl:DatatypeProperty .
      
      # Get domains when available
      OPTIONAL { 
        ?prop rdfs:domain ?domain .
        FILTER(isIRI(?domain))
        OPTIONAL { ?domain rdfs:label ?domainLabelEn FILTER(langMatches(lang(?domainLabelEn), "en")) }
        OPTIONAL { ?domain rdfs:label ?domainLabelAny }
      }
      
      # Get ranges (datatypes)
      OPTIONAL { 
        ?prop rdfs:range ?range .
      }
      
      # Get property label when available
      OPTIONAL { ?prop rdfs:label ?propLabelEn FILTER(langMatches(lang(?propLabelEn), "en")) }
      OPTIONAL { ?prop rdfs:label ?propLabelAny }
    }
    """
    
    results = run_sparql_query(owl_file, query)
    
    # Query for subPropertyOf relationships
    subprop_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?child ?parent
    WHERE {
      ?child rdf:type owl:DatatypeProperty .
      ?parent rdf:type owl:DatatypeProperty .
      ?child rdfs:subPropertyOf ?parent .
      
      # Only named properties (not blank nodes)
      FILTER(isIRI(?child) && isIRI(?parent))
      
      # Exclude self-references
      FILTER(?child != ?parent)
    }
    """
    
    subprop_results = run_sparql_query(owl_file, subprop_query)
    
    # Collect all nodes and their information
    properties = {}
    classes = {}
    domain_edges = []
    subprop_edges = []
    datatypes = {}
    
    for row in results:
        prop_uri = row['prop']
        prop_id = extract_local_name(prop_uri)
        prop_label = row.get('propLabelEn') or row.get('propLabelAny') or prop_id
        
        # Get datatype for range
        range_type = ""
        if row.get('range'):
            range_uri = row['range']
            range_type = extract_local_name(range_uri)
            # Simplify common XSD types
            if range_type in ['dateTime', 'string', 'int', 'integer', 'double', 'float', 'boolean']:
                range_type = range_type
            elif 'XMLSchema' in range_uri:
                range_type = extract_local_name(range_uri)
        
        if range_type:
            properties[prop_id] = f"{prop_label}\\n({range_type})"
        else:
            properties[prop_id] = prop_label
        
        if row.get('domain'):
            domain_uri = row['domain']
            domain_id = extract_local_name(domain_uri)
            domain_label = row.get('domainLabelEn') or row.get('domainLabelAny') or domain_id
            classes[domain_id] = domain_label
            domain_edges.append((prop_id, domain_id))
    
    for row in subprop_results:
        child_id = extract_local_name(row['child'])
        parent_id = extract_local_name(row['parent'])
        subprop_edges.append((child_id, parent_id))
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph "Data Properties" {\n')
        
        # Graph-level attributes based on layout engine
        f.write('  // Layout configuration\n')
        if layout_engine == 'dot':
            f.write('  rankdir=LR;\n')
        elif layout_engine == 'sfdp':
            f.write('  layout=sfdp;\n')
            f.write('  overlap=prism;\n')
            f.write('  splines=true;\n')
            f.write('  K=1.5;\n')
        elif layout_engine == 'neato':
            f.write('  layout=neato;\n')
            f.write('  overlap=false;\n')
            f.write('  splines=true;\n')
        elif layout_engine == 'fdp':
            f.write('  layout=fdp;\n')
            f.write('  overlap=false;\n')
            f.write('  splines=true;\n')
        
        f.write('  graph [splines=true, nodesep=1.0, ranksep=1.5, concentrate=false];\n')
        f.write('  node [fontname="Helvetica"];\n')
        f.write('  edge [fontsize=10, fontname="Helvetica"];\n')
        f.write('  \n')
        
        # Create clusters for better organization if enabled
        if use_clustering and layout_engine == 'dot':
            # Cluster by domain classes
            domain_classes = set(classes.keys())
            
            cluster_id = 0
            for domain_class in sorted(domain_classes):
                f.write(f'  subgraph cluster_{cluster_id} {{\n')
                f.write(f'    label="{classes.get(domain_class, domain_class)} Properties";\n')
                f.write(f'    style=filled;\n')
                f.write(f'    fillcolor=lightgray;\n')
                f.write(f'    "{domain_class}" [shape=box, style=filled, fillcolor=lightblue];\n')
                f.write(f'  }}\n')
                cluster_id += 1
        
        # Add property nodes
        for prop_id, prop_label in properties.items():
            label = prop_label.replace('"', '\\"')
            f.write(f'  "{prop_id}" [label="{label}", shape=ellipse, style=filled, fillcolor=lightyellow];\n')
        
        # Add class nodes (domains)
        for class_id, class_label in classes.items():
            label = class_label.replace('"', '\\"')
            if len(label) > 20:
                # Break long labels
                words = label.split()
                lines = []
                current_line = []
                current_length = 0
                for word in words:
                    if current_length + len(word) > 15 and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + 1
                if current_line:
                    lines.append(' '.join(current_line))
                label = '\\n'.join(lines)
            
            f.write(f'  "{class_id}" [label="{label}", shape=box, style=filled, fillcolor=lightblue];\n')
        
        f.write('  \n')
        
        # Add domain edges
        for prop_id, domain_id in domain_edges:
            f.write(f'  "{domain_id}" -> "{prop_id}" [label="domain", style=dashed, color=blue];\n')
        
        # Add subPropertyOf edges
        for child_id, parent_id in subprop_edges:
            f.write(f'  "{child_id}" -> "{parent_id}" [label="subPropertyOf", color=darkgreen];\n')
        
        f.write('}\n')

def parse_args():
    parser = argparse.ArgumentParser(description='Generate data properties visualization')
    parser.add_argument('owl_file', help='Input OWL file')
    parser.add_argument('output_file', help='Output DOT file')
    parser.add_argument('--engine', choices=['dot', 'sfdp', 'neato', 'fdp', 'circo', 'twopi', 'osage', 'patchwork'], 
                        default='dot', help='Layout engine (default: dot)')
    parser.add_argument('--no-clustering', dest='clustering', action='store_false', default=True,
                        help='Disable subgraph clustering')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    generate_data_properties_dot(args.owl_file, args.output_file, 
                                args.engine, args.clustering)
    print(f"Generated data properties visualization: {args.output_file} (engine: {args.engine})")
