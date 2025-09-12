#!/usr/bin/env python3
"""
Generate object properties visualization from OWL ontology
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

def generate_obj_properties_dot(owl_file, output_file):
    """Generate DOT file for object properties"""
    
    # Query for object properties and their domains/ranges
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?prop ?domain ?range ?propLabel ?domainLabel ?rangeLabel
    WHERE {
      ?prop rdf:type owl:ObjectProperty .
      
      # Get domains and ranges when available
      OPTIONAL { 
        ?prop rdfs:domain ?domain .
        FILTER(isIRI(?domain))
        OPTIONAL { ?domain rdfs:label ?domainLabel }
      }
      OPTIONAL { 
        ?prop rdfs:range ?range .
        FILTER(isIRI(?range))
        OPTIONAL { ?range rdfs:label ?rangeLabel }
      }
      
      # Get property label when available
      OPTIONAL { ?prop rdfs:label ?propLabel }
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
      ?child rdf:type owl:ObjectProperty .
      ?parent rdf:type owl:ObjectProperty .
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
    range_edges = []
    subprop_edges = []
    
    for row in results:
        prop_uri = row['prop']
        prop_id = extract_local_name(prop_uri)
        prop_label = row.get('propLabel', '') or prop_id
        
        properties[prop_id] = prop_label
        
        if row.get('domain'):
            domain_uri = row['domain']
            domain_id = extract_local_name(domain_uri)
            domain_label = row.get('domainLabel', '') or domain_id
            classes[domain_id] = domain_label
            domain_edges.append((prop_id, domain_id))
        
        if row.get('range'):
            range_uri = row['range']
            range_id = extract_local_name(range_uri)
            range_label = row.get('rangeLabel', '') or range_id
            classes[range_id] = range_label
            range_edges.append((prop_id, range_id))
    
    for row in subprop_results:
        child_id = extract_local_name(row['child'])
        parent_id = extract_local_name(row['parent'])
        subprop_edges.append((child_id, parent_id))
    
    # Generate DOT file
    with open(output_file, 'w') as f:
        f.write('digraph "Object Properties" {\n')
        f.write('  rankdir=TB;\n')
        f.write('  node [fontname="Arial"];\n')
        f.write('  edge [fontsize=10, fontname="Arial"];\n')
        f.write('  \n')
        f.write('  // Layout settings\n')
        f.write('  ranksep=1.0;\n')
        f.write('  nodesep=0.8;\n')
        f.write('  \n')
        
        # Add property nodes
        for prop_id, prop_label in properties.items():
            label = prop_label.replace('"', '\\"')
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
            
            f.write(f'  "{prop_id}" [label="{label}", shape=ellipse, style=filled, fillcolor=lightgreen];\n')
        
        # Add class nodes
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
        
        # Add range edges  
        for prop_id, range_id in range_edges:
            f.write(f'  "{prop_id}" -> "{range_id}" [label="range", style=dotted, color=red];\n')
        
        # Add subPropertyOf edges
        for child_id, parent_id in subprop_edges:
            f.write(f'  "{child_id}" -> "{parent_id}" [label="subPropertyOf", color=darkgreen];\n')
        
        f.write('}\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 generate_objprop_viz.py input.owl output.dot")
        sys.exit(1)
    
    owl_file = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_obj_properties_dot(owl_file, output_file)
    print(f"Generated object properties visualization: {output_file}")
