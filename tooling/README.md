# Ontology Tooling (Docker)

This directory provides a multi-arch (Apple Silicon-ready) Docker image with OWL tooling:
- ROBOT (reasoning, profile, QA report)
- Apache Jena `riot` (RDF/XML syntax validation)
- Openllet (reasoner)

Use the wrapper script to build the image once and run ephemeral containers without polluting your host.

## Prerequisites
- Docker Desktop (Apple Silicon supported)
- Internet access for the first build (to download tools)

## Quick start

- Build the image (cached for reuse):
  - `tooling/run_ontology_tools.sh build`
- Check RDF/XML syntax:
  - `tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl`
- Validate OWL 2 profile (DL by default):
  - `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`
- Reason and classify (ELK or HermiT):
  - `tooling/run_ontology_tools.sh reason mhm_ontology.owl elk`
  - `tooling/run_ontology_tools.sh reason mhm_ontology.owl hermit`
- Generate QA report:
  - `tooling/run_ontology_tools.sh report mhm_ontology.owl` (writes `report.tsv`)
- Validate PROV alignment and examples:
  - `tooling/run_ontology_tools.sh validate-prov`
  - Merges `alignments/mhm-prov-align.owl` + `examples.ttl` and runs SPARQL ASK queries in `queries/` to verify class/property mappings and provenance chains. Uses `catalog-v001.xml` to resolve local imports.
- Validate units alignment and examples:
  - `tooling/run_ontology_tools.sh validate-units`
  - Merges `mhm_ontology.owl` + `examples.ttl` and runs SPARQL ASK queries in `queries/units_*.rq` to ensure quantity values are present and units are set for examples.
- Validate SOSA alignment and examples:
  - `tooling/run_ontology_tools.sh validate-sosa`
  - Merges `mhm_ontology.owl` + `examples.ttl` and runs SPARQL ASK queries in `queries/sosa_*.rq` to ensure class/property mappings and example FOI/observedProperty are present.
 - Validate SKOS schemes and concepts:
  - `tooling/run_ontology_tools.sh validate-skos`
  - Merges `mhm_ontology.owl` + `examples.ttl` and runs SPARQL ASK queries in `queries/skos_*.rq` to ensure a ConceptScheme exists, concepts are in a scheme, and each concept has a `skos:prefLabel`.
- Open interactive shell:
  - `tooling/run_ontology_tools.sh shell`

## Commands reference

- `build`: Build the image using `tooling/Dockerfile`. The script auto-detects platform (arm64 vs amd64) and caches the image as `mhm-ontology-tools:latest`.
- `shell`: Run `/bin/bash` inside the container with the repo mounted at `/work`.
- `check-syntax <file.owl>`: Jena `riot --validate`.
- `profile <file.owl> [DL|EL]`: `robot validate-profile` writes `profile.txt`.
- `reason <file.owl> [elk|hermit]`: `robot reason --consistency true` writes `classified-<reasoner>.owl`.
- `report <file.owl>`: `robot report` writes `report.tsv`.
- `openllet-consistency <file.owl>`: Openllet consistency check.
- `exec -- <args...>`: Run an arbitrary command in the container (e.g., `robot --help`).
- `validate-prov`: Merge PROV alignment + examples, then run SPARQL checks. Fails non‑zero if any check fails.
- `validate-units`: Merge core + examples, then run unit SPARQL checks. Fails non‑zero if any check fails.
- `validate-sosa`: Merge core + examples, then run SOSA SPARQL checks. Fails non‑zero if any check fails.
 - `validate-skos`: Merge core + examples, then run SKOS SPARQL checks. Fails non‑zero if any check fails.

## Notes

- The image is multi-arch friendly. On Apple Silicon, the script builds for `linux/arm64` automatically.
- Memory for ROBOT can be adjusted via `ROBOT_JAVA_ARGS` (default `-Xmx4G`). To override: `tooling/run_ontology_tools.sh exec -- env ROBOT_JAVA_ARGS='-Xmx8G' robot reason ...`.
- First build downloads tool distributions; subsequent runs are instant unless the Dockerfile or versions change.
- Versions can be pinned by editing build args in `tooling/Dockerfile` (`ROBOT_VERSION`, `JENA_VERSION`, `OPENLLET_VERSION`).

## Typical workflow

1) Build: `tooling/run_ontology_tools.sh build`
2) Syntax check: `tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl`
3) Profile: `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`
4) Reason: `tooling/run_ontology_tools.sh reason mhm_ontology.owl elk`
5) QA report: `tooling/run_ontology_tools.sh report mhm_ontology.owl`
6) PROV mapping checks: `tooling/run_ontology_tools.sh validate-prov`
7) Units checks: `tooling/run_ontology_tools.sh validate-units`
8) SOSA checks: `tooling/run_ontology_tools.sh validate-sosa`

These steps align with the cleanup plan in `plan.md` and will help verify each structural change.
