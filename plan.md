# Plan: ODIM‑MH Cleanup and Provenance Extension

This document lists development tasks for the ODIM‑MH ontology. It is intended for contributors implementing cleanup, alignment (SOSA/PROV-O), provenance integration, and tooling. Tasks are ordered for sequential execution; tick items as they are completed.

## Core hygiene and metadata

- [x] Add ontology header and metadata (base IRI, version IRI, title/description/license).
- [x] Normalize prefixes: `rdf`, `rdfs`, `owl`, `xsd`, `connect`, `prov`, `sosa`, `skos`, `dcterms`.
- [x] Add alignment module importing PROV-O (core remains DL); defer SOSA/SKOS/units imports to later tasks.

## Modeling consistency and deduplication

- [x] Convert `connect:belongsToLayer` to `owl:AnnotationProperty` (used on classes). Remove the meta-modeling `domain/range` on `owl:Class`.
- [x] Deduplicate class/property definitions (e.g., `TimeInterval`, `EventWindow`, `ContextualSituation`). Keep one authoritative declaration each.
- [x] Replace `rdf:Property` usages with proper `owl:ObjectProperty`/`owl:DatatypeProperty` (e.g., `hasMeasurement`).
- [x] Remove duplicate `hasResponseFormat` declaration; keep one.
- [x] Fix incorrect layer reference: change `FeatureLayer` to `DerivedFeatureLayer` where used (e.g., `ActivityAndSleepFeature`).
- [ ] Review and narrow broad domains/ranges (e.g., avoid `owl:Thing` for `hasTimestamp/hasStartTime/hasEndTime` unless intentional).

## Labels, comments, and documentation

- [x] Add `rdfs:label` (and comments where useful) to public terms; target zero `missing_label` in ROBOT `report.tsv`.
- [ ] Add usage notes where modeling choices are non-obvious (e.g., how layers are annotated, alignment intents).

## Units and values (QUDT first)

- [x] Introduce QUDT pattern: allow `connect:Measurement` to use `qudt:quantityValue` with `qudt:numericValue` and `qudt:unit`.
- [x] Add minimal QUDT declarations in core (DL-safe): `qudt:QuantityValue` (Class), `qudt:quantityValue` (ObjectProperty), `qudt:numericValue` (DatatypeProperty), `qudt:unit` (ObjectProperty); add `unit:` prefix.
- [x] Deprecate legacy `connect:hasUnit` and `connect:hasValue` (keep for compatibility) and document deprecation in README.
- [x] Update examples in `examples.ttl` to include QUDT quantity values for common measurements (HR BPM, HRV ms, activity minutes, sleep hours).

## Logical structure

- [ ] Consider disjointness axioms among major measurement branches (Physiological, Behavioral, Environmental) if semantically valid.
- [ ] Review global constraints to avoid unintended inferences and keep reasoning decidable (DL profile where possible).

## SOSA/SSN alignment (after units)

- [x] Add DL-safe SOSA declarations in core: `sosa:Observation` (Class), `sosa:observedProperty` (ObjectProperty), `sosa:hasFeatureOfInterest` (ObjectProperty), and (optionally) `sosa:resultTime` (DatatypeProperty) without imports.
- [x] Map `connect:Measurement` ⊑ `sosa:Observation`.
- [x] Introduce `connect:observedProperty` ⊑ `sosa:observedProperty` and `connect:featureOfInterest` ⊑ `sosa:hasFeatureOfInterest` with sensible domains/ranges.
- [x] Decide and document FOI strategy (Participant as default FOI for person-centred measures; allow Device/Context for device/environment measures).
- [x] Update examples to include `connect:observedProperty` and `connect:featureOfInterest` for key measurements (HR, HRV, activity duration, sleep duration).
- [x] Add SPARQL checks for SOSA alignment and examples; add `validate-sosa` target to tooling.

## SKOS alignment (vocabularies)

- [x] Add DL-safe SKOS references in core: `skos:Concept`, `skos:ConceptScheme`, `skos:inScheme`, `skos:broader`/`narrower`/`related`, and `skos:prefLabel`/`skos:altLabel`.
- [x] Provide SKOS vocabularies in `vocab/` (`property-categories.ttl`, `question-domains.ttl`) with concepts, labels, definitions, and top concepts.
- [x] Add SPARQL checks for SKOS schemes/concepts; add `validate-skos` target to tooling.
- [x] Add `connect:skosTag` annotation and initial class→concept tags in `vocab/skos-tags.ttl`.
- [x] Add validation for label language tags, scheme top concepts, tag targets, and broader-cycle prevention.
- [ ] Expand SKOS vocabularies with additional concepts and relationships as needed.
- [ ] Tag additional classes with `connect:skosTag` where useful; keep to lightweight, non-normative tagging.
- [ ] Add short query examples demonstrating retrieval by SKOS tags.

## ABox separation and modularization

- [x] Move example individuals out of `mhm_ontology.owl` into `examples.ttl` and reference in README.
- [ ] (Optional, later) Split ontology into modules (`mhm-core.owl`, `mhm-measurement.owl`, `mhm-feature.owl`, `mhm-context.owl`, `mhm-questionnaire.owl`, `mhm-phenotype.owl`) and have an umbrella ontology import them.

## PROV-O alignment (sketch and phased implementation)

- [x] Document mapping in README: 
  - Participant → `prov:Agent` (subClass or `rdf:type` alignment)
  - Device → `prov:Agent` (or `prov:SoftwareAgent`/`prov:Agent` per policy)
  - DataSet/Measurement/Feature → `prov:Entity`
  - Computation → `prov:Activity`
- [x] Add bridging classes (as needed): 
  - `connect:SensingActivity` ⊑ `prov:Activity`
  - `connect:DataTransferEvent` ⊑ `prov:Activity`
  - `connect:NotificationEvent` ⊑ `prov:Activity`
  - (Option) align existing `connect:Computation` ⊑ `prov:Activity`
- [x] Align object properties with PROV-O: 
  - Declare `connect:wasGeneratedBy` ⊑ `prov:wasGeneratedBy` (domain: Entities like Measurement/Feature/DataSet; range: `prov:Activity`).
  - Declare `connect:wasDerivedFrom` ⊑ `prov:wasDerivedFrom`.
  - Add `connect:wasAttributedTo` ⊑ `prov:wasAttributedTo` (Entity → Agent) for linking Measurements/DataSets to Participant/Device.
  - Add `connect:associatedWithDevice` ⊑ `prov:wasAssociatedWith` (domain: `prov:Activity`, range: Device) for activity↔agent association.
  - Declare `connect:usedAppInterface` ⊑ `prov:used` (domain: `prov:Activity`, range: Interface) and review `connect:usedDevice` similarly.
- [x] Verify referenced activity classes exist for property domains (`DataTransferEvent`, `NotificationEvent`); add if missing or adjust domains accordingly.
- [x] Add minimal examples (in `examples.ttl`) showing PROV chains: Measurement (Entity) → wasGeneratedBy SensingActivity; SensingActivity wasAssociatedWith Device/Participant; DerivedFeature (Entity) wasComputedBy Computation; DerivedFeature wasDerivedFrom Measurement; DataSet wasAttributedTo Participant and used DataInterface.

## Tooling-driven QA fixes

- [x] Run `tooling/run_ontology_tools.sh report mhm_ontology.owl` and address all ERROR-level items (labels, duplicates) before deeper refactors.
- [x] Re-run `profile` for OWL DL after converting `belongsToLayer` to an annotation property and deduping.
- [ ] Keep `report.tsv` updated during PRs for quick review.

## Tooling and CI

- [ ] Add GitHub Actions workflow to run: syntax check, DL profile, QA report, validate-units, validate-sosa, validate-skos, validate-prov on PRs.
- [ ] Fail CI on any validation failure; publish `report.tsv` as an artifact.

## README updates

- [x] Add Namespaces section listing all prefixes and base IRIs used.
- [x] Add Imports section (DL core vs PROV alignment module).
- [x] Add Modeling Principles section (layers via annotation; PROV alignment; future SOSA + units).
- [ ] Add Contribution workflow: branch naming, editing in Protégé, reasoning checks, PR checklist.
- [ ] Add Versioning: version IRI strategy and release tags.
- [x] Link to `examples.ttl` for quick starts.

## Documentation

- [ ] Update `docs/ontology-overview.md` with concise sections for Units (QUDT), SOSA alignment, SKOS vocabularies, and class tagging with `connect:skosTag`.
- [ ] Add a brief SPARQL examples page in `docs/` showing SKOS lookups and SOSA/units checks.
- [ ] Add ontology visualization using Graphviz to generate static diagrams of class hierarchies and object properties. (Issue #15)
