#!/usr/bin/env bash
# Script to generate a DOT file representing data properties from an OWL file
# Usage: generate_data_properties.sh input.owl output.dot

set -euo pipefail

# Input and output files
input_file=$1
output_file=$2

# Generate DOT header
cat > "$output_file" << 'EOT'
digraph "Data Properties" {
  rankdir=BT;
  node [shape=box, style=filled];
EOT

# Create temporary SPARQL query file
cat > /tmp/dataprop_query.rq << 'SPARQL'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?prop ?domain ?range ?propLabel ?domainLabel
WHERE {
  ?prop rdf:type owl:DatatypeProperty .
  
  # Get domains when available
  OPTIONAL { 
    ?prop rdfs:domain ?domain .
    FILTER(isIRI(?domain))
    OPTIONAL { ?domain rdfs:label ?domainLabel }
  }
  
  # Get ranges (datatypes)
  OPTIONAL { 
    ?prop rdfs:range ?range .
  }
  
  # Get property label when available
  OPTIONAL { ?prop rdfs:label ?propLabel }
}
SPARQL

# Extract data properties using SPARQL
sparql --data "$input_file" --query /tmp/dataprop_query.rq > /tmp/dataprop_results.txt

# Process SPARQL results to DOT format
# First, filter the SPARQL output to get just the CSV data without headers
tail -n +2 /tmp/dataprop_results.txt | awk '
{
  # Skip empty lines or separator lines
  if(NF < 1 || $0 ~ /^[-=]+$/) { next }
  
  # Process each CSV row
  prop = $1
  domain = $2
  range = $3
  propLabel = $4
  domainLabel = $5
  
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
  
  # Extract datatype name for range
  rangeLabel = ""
  if (range != "") {
    if (match(range, /[#\/]([^#\/]+)$/)) {
      rangeLabel = substr(range, RSTART+1, RLENGTH-1)
    } else {
      rangeLabel = range
    }
  }
  
  # Remove quotes if present
  gsub(/^"|"$/, "", propLabel)
  gsub(/^"|"$/, "", domainLabel)
  
  # Ensure valid node names
  if (length(prop) > 0) {
    # Add property node with datatype if available
    if (rangeLabel != "") {
      print "  \"" prop "\" [label=\"" propLabel "\\n(" rangeLabel ")\", fillcolor=lightyellow];"
    } else {
      print "  \"" prop "\" [label=\"" propLabel "\", fillcolor=lightyellow];"
    }
    
    # Add domain if present
    if (domain != "") {
      print "  \"" domain "\" [label=\"" domainLabel "\", fillcolor=lightblue];"
      print "  \"" prop "\" -> \"" domain "\" [label=\"rdfs:domain\", style=\"dashed\"];"
    }
  }
}
' >> "$output_file"

# Create temporary subPropertyOf query for data properties
cat > /tmp/subprop_query.rq << 'SPARQL'
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
