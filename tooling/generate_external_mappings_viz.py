#!/usr/bin/env python3
"""
Generate External mappings DOT showing ODIM classes/properties mapped to external standards.
"""
import sys, subprocess, csv, io, argparse

EXTERNAL_PREFIXES = [
  'http://www.w3.org/ns/prov#',
  'http://www.w3.org/ns/sosa/',
  'http://www.w3.org/2004/02/skos/core#',
  'http://qudt.org/schema/qudt/',
  'http://purl.org/dc/terms/',
  'http://purl.obolibrary.org/obo/'  # IAO
]

def run_sparql(data_file, query):
    with open('/tmp/query_map.rq','w') as f:
        f.write(query)
    p = subprocess.run(['sparql','--data',data_file,'--query','/tmp/query_map.rq','--results=CSV'], capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(2)
    return list(csv.DictReader(io.StringIO(p.stdout)))

def local(u):
    return u.split('#')[-1].split('/')[-1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('merged_owl', help='Merged ontology file (core + alignments)')
    ap.add_argument('dot_out')
    ap.add_argument('--namespace', help='ODIM namespace (to detect internal terms)')
    args = ap.parse_args()

    ns = args.namespace or 'http://connectdigitalstudy.com/ontology#'
    extern_filters = ' || '.join([f"STRSTARTS(STR(?ext), \"{p}\")" for p in EXTERNAL_PREFIXES])

    q = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:  <http://www.w3.org/2002/07/owl#>
    SELECT ?odim ?ext ?kind ?odimLabelEn ?odimLabelAny ?extLabelEn ?extLabelAny WHERE {{
      {{ ?odim rdfs:subClassOf ?ext . BIND('class' AS ?kind) }}
      UNION 
      {{ ?odim rdfs:subPropertyOf ?ext . BIND('property' AS ?kind) }}
      FILTER(STRSTARTS(STR(?odim), \"{ns}\"))
      FILTER({extern_filters})
      OPTIONAL {{ ?odim rdfs:label ?odimLabelEn FILTER(langMatches(lang(?odimLabelEn),'en')) }}
      OPTIONAL {{ ?odim rdfs:label ?odimLabelAny }}
      OPTIONAL {{ ?ext rdfs:label ?extLabelEn FILTER(langMatches(lang(?extLabelEn),'en')) }}
      OPTIONAL {{ ?ext rdfs:label ?extLabelAny }}
    }}
    """
    rows = run_sparql(args.merged_owl, q)

    odim_nodes = set(); ext_nodes = set(); edges = []
    labels = {}
    for r in rows:
        o = r['odim']; e = r['ext']; kind = r['kind']
        odim_nodes.add(o); ext_nodes.add(e)
        labels[o] = r.get('odimLabelEn') or r.get('odimLabelAny') or local(o)
        labels[e] = r.get('extLabelEn') or r.get('extLabelAny') or local(e)
        edges.append((o,e,kind))

    with open(args.dot_out,'w') as f:
        f.write('digraph "External Mappings" {\n')
        f.write('  rankdir=LR;\n')
        f.write('  graph [splines=true, nodesep=0.9, ranksep=1.2];\n')
        f.write('  node [fontname="Helvetica", shape=box, style=filled, fillcolor=white];\n')
        f.write('  edge [fontname="Helvetica", fontsize=10];\n')
        # Left cluster: ODIM
        f.write('  subgraph cluster_odim {\n    label="ODIM-MH"; style=filled; color=lightgrey; fillcolor="#f7f7f7";\n')
        for o in sorted(odim_nodes, key=local):
            lbl = labels[o].replace('"','\\"')
            f.write(f'    "{local(o)}" [label="{lbl}"];\n')
        f.write('  }\n')
        # Right cluster: External
        f.write('  subgraph cluster_ext {\n    label="External"; style=filled; color=lightgrey; fillcolor="#f7f7f7";\n')
        for e in sorted(ext_nodes, key=local):
            lbl = labels[e].replace('"','\\"')
            f.write(f'    "{local(e)}" [label="{lbl}"];\n')
        f.write('  }\n')
        # Edges
        for o,e,kind in edges:
            style = 'solid' if kind=='class' else 'dashed'
            f.write(f'  "{local(o)}" -> "{local(e)}" [style={style}];\n')
        f.write('}\n')

if __name__ == '__main__':
    main()

