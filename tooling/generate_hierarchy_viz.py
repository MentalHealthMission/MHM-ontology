#!/usr/bin/env python3
"""
Generate class hierarchy visualization from OWL ontology
"""
import sys
import subprocess
import csv
import io
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

def generate_class_hierarchy_dot(owl_file, output_file):
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
        f.write('  rankdir=TB;\n')
        f.write('  node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial"];\n')
        f.write('  edge [fontsize=10, fontname="Arial"];\n')
        f.write('  \n')
        f.write('  // Layout settings\n')
        f.write('  ranksep=1.0;\n')
        f.write('  nodesep=0.5;\n')
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
        
        # Add ranking to improve layout
        if root_nodes:
            f.write('  \n')
            f.write('  // Root nodes at top\n')
            f.write('  { rank=min; ')
            for root in sorted(root_nodes):
                f.write(f'"{root}"; ')
            f.write('}\n')
        
        f.write('}\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 generate_hierarchy_viz.py input.owl output.dot")
        sys.exit(1)
    
    owl_file = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_class_hierarchy_dot(owl_file, output_file)
    print(f"Generated class hierarchy visualization: {output_file}")
