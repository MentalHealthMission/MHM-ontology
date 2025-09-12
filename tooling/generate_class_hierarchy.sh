#!/usr/bin/env bash
# Script to generate a DOT file representing the class hierarchy from an OWL file
# Usage: generate_class_hierarchy.sh input.owl output.dot

set -euo pipefail

# Input and output files
input_file=$1
output_file=$2

# Generate DOT header
cat > "$output_file" << 'EOT'
digraph "Class Hierarchy" {
  rankdir=BT;
  node [shape=box, style=filled, fillcolor=lightblue];
EOT

# Create temporary SPARQL query file
cat > /tmp/class_query.rq << 'SPARQL'
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
SPARQL

# Extract rdfs:subClassOf relationships using SPARQL and store in temp file
sparql --data "$input_file" --query /tmp/class_query.rq > /tmp/class_results.txt

# Process SPARQL results to DOT format
# First, filter the SPARQL output to get just the CSV data without headers
tail -n +2 /tmp/class_results.txt | awk '
{
  # Skip empty lines or separator lines
  if(NF < 2 || $0 ~ /^[-=]+$/) { next }
  
  # Process each CSV row 
  child = $1
  parent = $2
  childLabel = $3
  parentLabel = $4
  
  # Remove < > from URIs if present
  gsub(/^<|>$/, "", child)
  gsub(/^<|>$/, "", parent)
  
  # Use label if available, otherwise extract local name from URI
  if (childLabel == "" || childLabel == "childLabel") {
    if (match(child, /[#\/]([^#\/]+)$/)) {
      childLabel = substr(child, RSTART+1, RLENGTH-1)
    } else {
      childLabel = child
    }
  }
  
  if (parentLabel == "" || parentLabel == "parentLabel") {
    if (match(parent, /[#\/]([^#\/]+)$/)) {
      parentLabel = substr(parent, RSTART+1, RLENGTH-1)
    } else {
      parentLabel = parent
    }
  }
  
  # Remove quotes if present
  gsub(/^"|"$/, "", childLabel)
  gsub(/^"|"$/, "", parentLabel)
  
  # Ensure valid node names
  if (length(child) > 0 && length(parent) > 0) {
    # Output DOT statements
    print "  \"" child "\" [label=\"" childLabel "\"];"
    print "  \"" parent "\" [label=\"" parentLabel "\"];"
    print "  \"" child "\" -> \"" parent "\" [label=\"rdfs:subClassOf\"];"
  }
}
' >> "$output_file"

# Close DOT file
echo "}" >> "$output_file"
