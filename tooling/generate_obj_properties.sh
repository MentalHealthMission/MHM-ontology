#!/usr/bin/env bash
# Script to generate a DOT file representing object properties from an OWL file
# Usage: generate_obj_properties.sh input.owl output.dot

set -euo pipefail

# Input and output files
input_file=$1
output_file=$2

# Generate DOT header
cat > "$output_file" << 'EOT'
digraph "Object Properties" {
  rankdir=BT;
  node [shape=box, style=filled];
EOT

# Create temporary SPARQL query file
cat > /tmp/objprop_query.rq << 'SPARQL'
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
SPARQL

# Extract object properties using SPARQL
sparql --data "$input_file" --query /tmp/objprop_query.rq >> "$output_file"

# Process SPARQL results to DOT format
awk '
BEGIN { FS="\t"; skip=1 }
# Skip header
NR <= 2 { next }
# Process results
{
  prop = $1
  domain = $2
  range = $3
  propLabel = length($4) > 0 ? $4 : getLocalName($1)
  domainLabel = length($5) > 0 ? $5 : getLocalName($2)
  rangeLabel = length($6) > 0 ? $6 : getLocalName($3)
  
  gsub(/"/, "\\\"", propLabel)
  gsub(/"/, "\\\"", domainLabel)
  gsub(/"/, "\\\"", rangeLabel)
  
  # Add property node
  print "  \"" prop "\" [label=\"" propLabel "\", fillcolor=lightgreen];"
  
  # Add domain and range if present
  if (length(domain) > 0) {
    print "  \"" domain "\" [label=\"" domainLabel "\", fillcolor=lightblue];"
    print "  \"" prop "\" -> \"" domain "\" [label=\"rdfs:domain\", style=\"dashed\"];"
  }
  
  if (length(range) > 0) {
    print "  \"" range "\" [label=\"" rangeLabel "\", fillcolor=lightblue];"
    print "  \"" prop "\" -> \"" range "\" [label=\"rdfs:range\", style=\"dotted\"];"
  }
}

function getLocalName(uri) {
  if (match(uri, /[#\/]([^#\/]+)$/)) {
    return substr(uri, RSTART+1, RLENGTH-1)
  }
  return uri
}
' "$output_file" > "$output_file.tmp"

# Create temporary subPropertyOf query
cat > /tmp/subprop_query.rq << 'SPARQL'
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
SPARQL

# Extract subPropertyOf relationships
sparql --data "$input_file" --query /tmp/subprop_query.rq >> "$output_file.tmp"

# Process subPropertyOf relationships
awk '
BEGIN { FS="\t"; skip=1 }
# Skip header
NR <= 2 { next }
# Process results
{
  child = $1
  parent = $2
  print "  \"" child "\" -> \"" parent "\" [label=\"rdfs:subPropertyOf\"];"
}
' "$output_file.tmp" >> "$output_file.tmp2"

# Close DOT file
echo "}" >> "$output_file.tmp2"

# Replace output with processed file
mv "$output_file.tmp2" "$output_file"
rm -f "$output_file.tmp"
