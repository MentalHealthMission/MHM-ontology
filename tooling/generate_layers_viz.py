#!/usr/bin/env python3
"""
Generate a Layers overview DOT from OWL by grouping classes annotated with connect:belongsToLayer.
"""
import sys, subprocess, csv, io, argparse

CONNECT = "http://connectdigitalstudy.com/ontology#"

def run_sparql(data_file, query):
    with open('/tmp/query_layers.rq', 'w') as f:
        f.write(query)
    p = subprocess.run(['sparql','--data',data_file,'--query','/tmp/query_layers.rq','--results=CSV'], capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(2)
    return list(csv.DictReader(io.StringIO(p.stdout)))

def local(name):
    return name.split('#')[-1].split('/')[-1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('owl_file')
    ap.add_argument('dot_out')
    ap.add_argument('--namespace', help='Restrict to IRIs under this namespace')
    args = ap.parse_args()

    ns = args.namespace
    filter_ns = f"FILTER(STRSTARTS(STR(?cls), \"{ns}\"))" if ns else ""

    q = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl:  <http://www.w3.org/2002/07/owl#>
    PREFIX connect: <{CONNECT}>
    SELECT ?cls ?layer ?clsLabelEn ?clsLabelAny ?layerLabelEn ?layerLabelAny WHERE {{
      ?cls a owl:Class ; connect:belongsToLayer ?layer .
      {filter_ns}
      OPTIONAL {{ ?cls rdfs:label ?clsLabelEn FILTER(langMatches(lang(?clsLabelEn),'en')) }}
      OPTIONAL {{ ?cls rdfs:label ?clsLabelAny }}
      OPTIONAL {{ ?layer rdfs:label ?layerLabelEn FILTER(langMatches(lang(?layerLabelEn),'en')) }}
      OPTIONAL {{ ?layer rdfs:label ?layerLabelAny }}
    }}
    """
    rows = run_sparql(args.owl_file, q)

    # Group classes by layer
    clusters = {}
    layer_labels = {}
    for r in rows:
        layer = r['layer']
        cls = r['cls']
        clusters.setdefault(layer, set()).add(cls)
        ll = r.get('layerLabelEn') or r.get('layerLabelAny') or local(layer)
        layer_labels[layer] = ll
    
    with open(args.dot_out, 'w') as f:
        f.write('digraph "Layers Overview" {\n')
        f.write('  rankdir=LR;\n')
        f.write('  graph [splines=true, nodesep=0.8, ranksep=1.2];\n')
        f.write('  node [shape=box, style=filled, fillcolor=white, fontname="Helvetica"];\n')
        # Clusters per layer
        cid = 0
        for layer, classes in sorted(clusters.items(), key=lambda kv: layer_labels[kv[0]]):
            f.write(f'  subgraph cluster_{cid} {{\n')
            label = layer_labels[layer].replace('"','\\"')
            f.write(f'    label="{label}"; style=filled; color=lightgrey; fillcolor="#f7f7f7";\n')
            count = 0
            extra = 0
            for cls in sorted(classes, key=lambda x: local(x)):
                label_cls = local(cls)
                # Show up to 6 exemplars to keep concise
                if count < 6:
                    f.write(f'    "{local(cls)}" [label="{label_cls}"];\n')
                    count += 1
                else:
                    extra += 1
            if extra > 0:
                f.write(f'    "{local(layer)}_more" [label="+{extra} more", shape=plaintext, fontcolor=gray50];\n')
            f.write('  }\n')
            cid += 1
        f.write('}\n')

if __name__ == '__main__':
    main()

