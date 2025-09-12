#!/usr/bin/env bash
# Script to generate a DOT file representing the class hierarchy from an OWL file
# Usage: generate_class_hierarchy.sh input.owl output.dot

set -euo pipefail

# Input and output files
input_file=$1
output_file=$2

# Generate DOT header with better layout
cat > "$output_file" << 'EOT'
digraph "Class Hierarchy" {
  rankdir=TB;
  node [shape=box, style=filled, fillcolor=lightblue];
  edge [fontsize=10];
  
  // Layout settings for better hierarchy visualization
  ranksep=1.5;
  nodesep=0.5;
  
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

# Extract rdfs:subClassOf relationships using SPARQL in CSV format
sparql --data "$input_file" --query /tmp/class_query.rq --results=CSV > /tmp/class_results.csv

# Function to extract local name from URI
extract_local_name() {
  local uri="$1"
  # Remove < > if present
  uri=$(echo "$uri" | sed 's/^<\|>$//g')
  # Extract local name after # or /
  echo "$uri" | sed 's/.*[#\/]//'
}

# Process CSV output - skip header line
tail -n +2 /tmp/class_results.csv | while IFS=',' read -r child parent childLabel parentLabel; do
  # Remove quotes from CSV fields
  child=$(echo "$child" | sed 's/^"\|"$//g')
  parent=$(echo "$parent" | sed 's/^"\|"$//g')
  childLabel=$(echo "$childLabel" | sed 's/^"\|"$//g')
  parentLabel=$(echo "$parentLabel" | sed 's/^"\|"$//g')
  
  # Skip empty rows
  [ -z "$child" ] || [ -z "$parent" ] && continue
  
  # Use label if available, otherwise extract local name
  if [ -z "$childLabel" ]; then
    childLabel=$(extract_local_name "$child")
  fi
  
  if [ -z "$parentLabel" ]; then
    parentLabel=$(extract_local_name "$parent")
  fi
  
  # Create safer node names by using local names
  childNode=$(extract_local_name "$child")
  parentNode=$(extract_local_name "$parent")
  
  # Escape quotes in labels
  childLabel=$(echo "$childLabel" | sed 's/"/\\"/g')
  parentLabel=$(echo "$parentLabel" | sed 's/"/\\"/g')
  
  # Output DOT statements
  echo "  \"$childNode\" [label=\"$childLabel\"];" >> "$output_file"
  echo "  \"$parentNode\" [label=\"$parentLabel\"];" >> "$output_file"
  echo "  \"$childNode\" -> \"$parentNode\";" >> "$output_file"
  echo "" >> "$output_file"
done

# Close DOT file
echo "}" >> "$output_file"
