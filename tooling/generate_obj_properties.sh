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
sparql --data "$input_file" --query /tmp/objprop_query.rq > /tmp/objprop_results.txt

# Process SPARQL results to DOT format
# First, filter the SPARQL output to get just the CSV data without headers
tail -n +2 /tmp/objprop_results.txt | awk '
{
  # Skip empty lines or separator lines
  if(NF < 1 || $0 ~ /^[-=]+$/) { next }
  
  # Process each CSV row
  prop = $1
  domain = $2
  range = $3
  propLabel = $4
  domainLabel = $5
  rangeLabel = $6
  
  # Remove < > from URIs if present
  gsub(/^<|>$/, "", prop)
  gsub(/^<|>$/, "", domain)
  gsub(/^<|>$/, "", range)
  
  # Use label if available, otherwise extract local name from URI
  if (propLabel == "" || propLabel == "propLabel") {
    if (match(prop, /[#\/]([^#\/]+)$/)) {
      propLabel = substr(prop, RSTART+1, RLENGTH-1)
    } else {
      propLabel = prop
    }
  }
  
  if ((domainLabel == "" || domainLabel == "domainLabel") && domain != "") {
    if (match(domain, /[#\/]([^#\/]+)$/)) {
      domainLabel = substr(domain, RSTART+1, RLENGTH-1)
    } else {
      domainLabel = domain
    }
  }
  
  if ((rangeLabel == "" || rangeLabel == "rangeLabel") && range != "") {
    if (match(range, /[#\/]([^#\/]+)$/)) {
      rangeLabel = substr(range, RSTART+1, RLENGTH-1)
    } else {
      rangeLabel = range
    }
  }
  
  # Remove quotes if present
  gsub(/^"|"$/, "", propLabel)
  gsub(/^"|"$/, "", domainLabel)
  gsub(/^"|"$/, "", rangeLabel)
  
  # Ensure valid node names
  if (length(prop) > 0) {
    # Add property node
    print "  \"" prop "\" [label=\"" propLabel "\", fillcolor=lightgreen];"
    
    # Add domain and range if present
    if (domain != "") {
      print "  \"" domain "\" [label=\"" domainLabel "\", fillcolor=lightblue];"
      print "  \"" prop "\" -> \"" domain "\" [label=\"rdfs:domain\", style=\"dashed\"];"
    }
    
    if (range != "") {
      print "  \"" range "\" [label=\"" rangeLabel "\", fillcolor=lightblue];"
      print "  \"" prop "\" -> \"" range "\" [label=\"rdfs:range\", style=\"dotted\"];"
    }
  }
}
' >> "$output_file"

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
sparql --data "$input_file" --query /tmp/subprop_query.rq > /tmp/subprop_results.txt

# Process subPropertyOf relationships
# First, filter the SPARQL output to get just the CSV data without headers
tail -n +2 /tmp/subprop_results.txt | awk '
{
  # Skip empty lines or separator lines
  if(NF < 2 || $0 ~ /^[-=]+$/) { next }
  
  # Process each CSV row
  child = $1
  parent = $2
  
  # Remove < > from URIs if present
  gsub(/^<|>$/, "", child)
  gsub(/^<|>$/, "", parent)
  
  # Ensure valid node names
  if (length(child) > 0 && length(parent) > 0) {
    print "  \"" child "\" -> \"" parent "\" [label=\"rdfs:subPropertyOf\"];"
  }
}
' >> "$output_file"

# Close DOT file
echo "}" >> "$output_file"
