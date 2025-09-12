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

# Extract rdfs:subClassOf relationships using SPARQL
sparql --data "$input_file" --query - >> "$output_file" << 'SPARQL'
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

# Process SPARQL results to DOT format
awk '
BEGIN { FS="\t"; skip=1 }
# Skip header
NR <= 2 { next }
# Process results
{
  child = $1
  parent = $2
  childLabel = length($3) > 0 ? $3 : getLocalName($1)
  parentLabel = length($4) > 0 ? $4 : getLocalName($2)
  
  gsub(/"/, "\\\"", childLabel)
  gsub(/"/, "\\\"", parentLabel)
  
  print "  \"" child "\" [label=\"" childLabel "\"];"
  print "  \"" parent "\" [label=\"" parentLabel "\"];"
  print "  \"" child "\" -> \"" parent "\" [label=\"rdfs:subClassOf\"];"
}

function getLocalName(uri) {
  if (match(uri, /[#\/]([^#\/]+)$/)) {
    return substr(uri, RSTART+1, RLENGTH-1)
  }
  return uri
}
' "$output_file" > "$output_file.tmp"

# Close DOT file
echo "}" >> "$output_file.tmp"

# Replace output with processed file
mv "$output_file.tmp" "$output_file"
