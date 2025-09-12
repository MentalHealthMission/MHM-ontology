#!/usr/bin/env python3
"""
Generate object properties visualization from OWL ontology
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

def generate_object_properties_dot(owl_file, output_file, layout_engine='sfdp', use_clustering=True):
    """Generate DOT file for object properties"""
    
    # Query for object properties with domains, ranges, and subproperties
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?property ?domain ?range ?subprop ?propLabel ?domainLabel ?rangeLabel ?superpropLabel
    WHERE {
      ?property a owl:ObjectProperty .
      
      OPTIONAL { 
        ?property rdfs:domain ?domain .
        OPTIONAL { ?domain rdfs:label ?domainLabel }
      }
      OPTIONAL { 
        ?property rdfs:range ?range .
        OPTIONAL { ?range rdfs:label ?rangeLabel }
      }
      OPTIONAL { 
        ?property rdfs:subPropertyOf ?subprop .
        FILTER(?subprop != ?property)
        OPTIONAL { ?subprop rdfs:label ?superpropLabel }
      }
      
      OPTIONAL { ?property rdfs:label ?propLabel }
      
      # Only include named properties (not blank nodes)
      FILTER(isIRI(?property))
    }
    """
    
    results = run_sparql_query(owl_file, query)
    
    # Build property structure
    properties = {}
    domains = defaultdict(set)
    ranges = defaultdict(set)
    subproperties = defaultdict(set)
    labels = {}
    
    for row in results:
        prop_uri = row['property']
        prop_id = extract_local_name(prop_uri)
        prop_label = row.get('propLabel', '') or prop_id
        
        properties[prop_id] = prop_uri
        labels[prop_id] = prop_label
        
        if row.get('domain'):
            domain_id = extract_local_name(row['domain'])
            domain_label = row.get('domainLabel', '') or domain_id
            domains[prop_id].add(domain_id)
            labels[domain_id] = domain_label
        
        if row.get('range'):
            range_id = extract_local_name(row['range'])
            range_label = row.get('rangeLabel', '') or range_id
            ranges[prop_id].add(range_id)
            labels[range_id] = range_label
        
        if row.get('subprop'):
            super_id = extract_local_name(row['subprop'])
            super_label = row.get('superpropLabel', '') or super_id
            subproperties[super_id].add(prop_id)
            labels[super_id] = super_label
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph "Object Properties" {\n')
        
        # Graph-level attributes based on layout engine
        f.write('  // Layout configuration\n')
        if layout_engine == 'sfdp':
            f.write('  layout=sfdp;\n')
            f.write('  overlap=prism;\n')
            f.write('  splines=true;\n')
            f.write('  K=2.0;\n')  # Ideal spring length
        elif layout_engine == 'neato':
            f.write('  layout=neato;\n')
            f.write('  overlap=false;\n')
            f.write('  splines=true;\n')
        elif layout_engine == 'fdp':
            f.write('  layout=fdp;\n')
            f.write('  overlap=false;\n')
            f.write('  splines=true;\n')
        elif layout_engine == 'dot':
            f.write('  rankdir=LR;\n')
        
        f.write('  graph [splines=true, nodesep=1.0, ranksep=1.5, concentrate=false];\n')
        f.write('  node [fontname="Arial"];\n')
        f.write('  edge [fontsize=10, fontname="Arial"];\n')
        f.write('  \n')
        
        # Create clusters for better organization if enabled
        if use_clustering and layout_engine == 'dot':
            # Cluster by domain classes
            domain_classes = set()
            for prop_domains in domains.values():
                domain_classes.update(prop_domains)
            
            cluster_id = 0
            for domain_class in sorted(domain_classes):
                f.write(f'  subgraph cluster_{cluster_id} {{\n')
                f.write(f'    label="{labels.get(domain_class, domain_class)} Domain";\n')
                f.write(f'    style=filled;\n')
                f.write(f'    fillcolor=lightgray;\n')
                f.write(f'    "{domain_class}" [shape=box, style=filled, fillcolor=lightblue];\n')
                f.write(f'  }}\n')
                cluster_id += 1
        
        # Add class nodes
        all_classes = set()
        for prop_domains in domains.values():
            all_classes.update(prop_domains)
        for prop_ranges in ranges.values():
            all_classes.update(prop_ranges)
        
        for class_id in all_classes:
            label = labels.get(class_id, class_id)
            label = label.replace('"', '\\"')
            f.write(f'  "{class_id}" [shape=box, style=filled, fillcolor=lightblue, label="{label}"];\n')
        
        # Add property nodes
        for prop_id in properties:
            label = labels.get(prop_id, prop_id)
            label = label.replace('"', '\\"')
            f.write(f'  "{prop_id}" [shape=ellipse, style=filled, fillcolor=lightyellow, label="{label}"];\n')
        
        f.write('  \n')
        
        # Add domain/range relationships
        for prop_id in properties:
            prop_domains = domains.get(prop_id, set())
            prop_ranges = ranges.get(prop_id, set())
            
            # Domain to property edges
            for domain_id in prop_domains:
                f.write(f'  "{domain_id}" -> "{prop_id}" [color=blue, label="domain"];\n')
            
            # Property to range edges
            for range_id in prop_ranges:
                f.write(f'  "{prop_id}" -> "{range_id}" [color=green, label="range"];\n')
        
        # Add subproperty relationships
        for super_prop, sub_props in subproperties.items():
            for sub_prop in sub_props:
                f.write(f'  "{sub_prop}" -> "{super_prop}" [color=red, style=dashed, label="subPropertyOf"];\n')
        
        f.write('}\n')

def parse_args():
    parser = argparse.ArgumentParser(description='Generate object properties visualization')
    parser.add_argument('owl_file', help='Input OWL file')
    parser.add_argument('output_file', help='Output DOT file')
    parser.add_argument('--engine', choices=['dot', 'sfdp', 'neato', 'fdp', 'circo', 'twopi', 'osage', 'patchwork'], 
                        default='sfdp', help='Layout engine (default: sfdp)')
    parser.add_argument('--no-clustering', dest='clustering', action='store_false', default=True,
                        help='Disable subgraph clustering')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    generate_object_properties_dot(args.owl_file, args.output_file, 
                                  args.engine, args.clustering)
    print(f"Generated object properties visualization: {args.output_file} (engine: {args.engine})")
