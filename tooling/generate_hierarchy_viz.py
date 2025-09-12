#!/usr/bin/env python3
"""
Generate class hierarchy visualization from OWL ontology
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

def generate_class_hierarchy_dot(owl_file, output_file, layout_engine='dot', use_tred=True, use_unflatten=False):
    """Generate DOT file for class hierarchy"""
    
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?child ?parent ?childLabel ?parentLabel
    WHERE {
      ?child rdfs:subClassOf ?parent .
      
      # Only include named classes (not blank nodes)
      FILTER(isIRI(?child) && isIRI(?parent))
      
      # Exclude owl:Thing as parent
      FILTER(?parent != owl:Thing)
      
      # Get labels when available
      OPTIONAL { ?child rdfs:label ?childLabel }
      OPTIONAL { ?parent rdfs:label ?parentLabel }
    }
    """
    
    results = run_sparql_query(owl_file, query)
    
    # Build hierarchy structure
    children = defaultdict(set)
    all_nodes = set()
    labels = {}
    
    for row in results:
        child_uri = row['child']
        parent_uri = row['parent']
        child_label = row.get('childLabel', '') or extract_local_name(child_uri)
        parent_label = row.get('parentLabel', '') or extract_local_name(parent_uri)
        
        child_id = extract_local_name(child_uri)
        parent_id = extract_local_name(parent_uri)
        
        children[parent_id].add(child_id)
        all_nodes.add(child_id)
        all_nodes.add(parent_id)
        
        labels[child_id] = child_label
        labels[parent_id] = parent_label
    
    # Find root nodes (nodes that are not children of others)
    root_nodes = all_nodes - {child for parent_children in children.values() for child in parent_children}
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph "Class Hierarchy" {\n')
        
        # Graph-level attributes for better layout
        f.write('  // Layout configuration\n')
        if layout_engine == 'dot':
            f.write('  rankdir=TB;\n')
        elif layout_engine == 'sfdp':
            f.write('  layout=sfdp;\n')
            f.write('  overlap=prism;\n')
            f.write('  splines=true;\n')
        elif layout_engine == 'neato':
            f.write('  layout=neato;\n')
            f.write('  overlap=false;\n')
        
        f.write('  graph [splines=true, overlap=false, nodesep=0.6, ranksep=1.0, concentrate=true];\n')
        f.write('  node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial"];\n')
        f.write('  edge [fontsize=10, fontname="Arial"];\n')
        f.write('  \n')
        
        # Add all nodes with labels
        for node_id in all_nodes:
            label = labels.get(node_id, node_id)
            # Escape quotes and wrap long labels
            label = label.replace('"', '\\"')
            if len(label) > 20:
                # Break long labels into multiple lines
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
            
            f.write(f'  "{node_id}" [label="{label}"];\n')
        
        f.write('  \n')
        
        # Add edges
        for parent_id, child_set in children.items():
            for child_id in child_set:
                f.write(f'  "{child_id}" -> "{parent_id}";\n')
        
        # Add ranking to improve layout for hierarchical engines
        if layout_engine == 'dot' and root_nodes:
            f.write('  \n')
            f.write('  // Root nodes at top\n')
            f.write('  { rank=min; ')
            for root in sorted(root_nodes):
                f.write(f'"{root}"; ')
            f.write('}\n')
        
        f.write('}\n')

def parse_args():
    parser = argparse.ArgumentParser(description='Generate class hierarchy visualization')
    parser.add_argument('owl_file', help='Input OWL file')
    parser.add_argument('output_file', help='Output DOT file')
    parser.add_argument('--engine', choices=['dot', 'sfdp', 'neato', 'fdp', 'circo', 'twopi', 'osage', 'patchwork'], 
                        default='dot', help='Layout engine (default: dot)')
    parser.add_argument('--tred', action='store_true', default=True, 
                        help='Apply transitive reduction (default: True)')
    parser.add_argument('--no-tred', dest='tred', action='store_false',
                        help='Skip transitive reduction')
    parser.add_argument('--unflatten', action='store_true', 
                        help='Apply unflatten preprocessing')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    generate_class_hierarchy_dot(args.owl_file, args.output_file, 
                                args.engine, args.tred, args.unflatten)
    print(f"Generated class hierarchy visualization: {args.output_file} (engine: {args.engine})")
