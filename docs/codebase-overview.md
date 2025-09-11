# Codebase Overview

This document summarizes the repository structure and the purpose of key files and directories.

## Top-level

- `README.md`: Project introduction, namespaces, imports strategy, modeling principles, and tooling commands.
- `plan.md`: Development plan and checklist of tasks across modeling, alignment, tooling, and docs.
- `catalog-v001.xml`: XML catalog for resolving imports and local resources during tooling runs.
- `mhm_ontology.owl`: Core ontology (DL-safe). Declares classes and properties, minimal references to external vocabularies, and avoids importing large ontologies. Public name: ODIM‑MH.
- `examples.ttl`: Example individuals (ABox) illustrating measurements, features, context, and provenance usage.
- `classified-elk.owl`: Reasoned ontology output produced by tooling (generated artifact).
- `profile.txt`: Results of OWL profile validation (generated artifact).
- `report.tsv`: QA report produced by ROBOT (generated artifact).

## Alignments

- `alignments/mhm-prov-align.owl`: Alignment module that imports PROV-O and the core ontology to provide full provenance semantics and property mappings.

## Vocabularies (SKOS)

- `vocab/property-categories.ttl`: SKOS ConceptScheme for property categories (Physiological, Behavioral, Environmental) with labels, definitions, and top concepts.
- `vocab/question-domains.ttl`: SKOS ConceptScheme for questionnaire domains (Mood, Sleep, Stress, Paranoia) with labels, definitions, and top concepts.
- `vocab/skos-tags.ttl`: DL-safe annotations linking ontology classes to SKOS concepts via `connect:skosTag`.

## Queries

- `queries/prov_*`: ASK queries validating PROV class/property mappings and example chains.
- `queries/units_*`: ASK queries ensuring quantity values and expected units in examples.
- `queries/sosa_*`: ASK queries for SOSA alignment and example usage.
- `queries/skos_*`: ASK queries for SKOS schemes, labels (with language tags), top concepts, hierarchy hygiene, and tag validity.

## Tooling

- `tooling/run_ontology_tools.sh`: Wrapper script for building and running the Dockerized tooling, profile validation, reasoning, QA report, and validation tasks.
- `tooling/Dockerfile`: Multi-arch Docker image with ROBOT and Apache Jena CLI tools.
- `tooling/README.md`: Usage instructions and command reference for the tooling script.

## Documentation

- `docs/ontology-overview.md`: Overview of the ontology’s goals, layers, core terms, and the use of external ontologies.
- `docs/codebase-overview.md`: This file. Summarizes repository structure and artifact roles.

## Build outputs

- `build/`: Temporary outputs from merged graphs used during validation runs (created by tooling; safe to delete).
