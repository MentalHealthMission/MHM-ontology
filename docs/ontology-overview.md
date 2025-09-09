# MHM Ontology Overview

This document provides a concise overview of the ontology’s goals, main layers, core terms, and how external standards are used.

## Overview

- Bold goal: represent participant/device data for health studies in a consistent, computable model that supports integration, basic reasoning, and provenance.
- Bold design: a DL-safe core with lightweight references to external standards (SOSA, SKOS, QUDT) and a separate PROV-O alignment module for full provenance semantics.
- Bold usage: classes and properties for measurements, features, context, questionnaires, phenotypes, and provenance, with examples and validation scripts.

## Layers

- Bold Measurement Layer: raw observations from devices and apps (e.g., heart rate, steps, sleep stages, ambient light).
- Bold Derived Feature Layer: features calculated from measurements (e.g., sleep regularity, activity duration).
- Bold Computation Layer: processes that generate features or phenotypes (algorithms, models, rules).
- Bold Contextual Layer: contextual information such as time intervals and situations.
- Bold Questionnaire Layer: questions, response formats, and responses collected from participants.
- Bold Provenance Layer: entities, activities, and agents describing origin and processing of data.
- Bold Digital Phenotype Layer: higher-level constructs inferred from features.

## Top-level Classes

- Bold Measurement: a single observation/data point; aligned to `sosa:Observation` and `prov:Entity`.
- Bold Feature: an attribute computed from measurements; `prov:Entity`.
- Bold DerivedFeature: a Feature computed from other features/measurements; `prov:Entity`.
- Bold Computation: a process that computes features or infers phenotypes; `prov:Activity`.
- Bold SensingActivity: an activity representing sensor data capture; `prov:Activity`.
- Bold DigitalPhenotype: higher-level constructs derived from features; `prov:Entity`.
- Bold Participant: study participant; `prov:Agent`.
- Bold Device: hardware/software agent used to collect data; `prov:Agent`.
- Bold Interface: software interfaces used for capture/transfer.
- Bold DataSet: collections of data items (SensorDataSet, QuestionnaireDataSet, ParticipantDataSet); `prov:Entity`.
- Bold Context classes: ObservationContext, TimeInterval (Hourly/Daily/Weekly), EventWindow, ContextualSituation.
- Bold Questionnaire classes: QuestionnaireEntry, ResponseItem, Question, ResponseFormat (Slider/MultipleChoice/Text/Likert).

## Key Properties (selected)

- Bold hasMeasurement: Feature → Measurement; inputs to feature computation.
- Bold observedProperty: Measurement → resource; sub-property of `sosa:observedProperty`.
- Bold featureOfInterest: Measurement → resource; sub-property of `sosa:hasFeatureOfInterest`.
- Bold resultTime: Measurement → `xsd:dateTime`; sub-property of `sosa:resultTime`.
- Bold qudt:quantityValue: Measurement → `qudt:QuantityValue`.
  - Bold qudt:numericValue / connect:numericValue: QuantityValue → numeric literal.
  - Bold qudt:unit: QuantityValue → `unit:...`.
- Bold wasGeneratedBy / wasComputedBy: Entity → Activity; sub-property of `prov:wasGeneratedBy`.
- Bold wasDerivedFrom: Entity → Entity; sub-property of `prov:wasDerivedFrom`.
- Bold usedDevice / usedAppInterface / usedDataInterface: Activity/DataSet → Device/Interface; sub-properties of `prov:used`.
- Bold wasCollectedFrom / wasAttributedTo: DataSet/Entity → Participant; sub-property of `prov:wasAttributedTo`.
- Bold hasTimestamp / hasStartTime / hasEndTime: contextual timing utilities.

## External Ontologies and Usage

The ontology references well-known standards to improve interoperability. The core keeps DL profile compliance by using minimal declarations and avoids importing large external ontologies, except for an explicit PROV-O alignment module.

### PROV-O (W3C Provenance)

Provenance describes where data comes from, who created it, and how it was produced. PROV-O provides a common vocabulary for entities (data), activities (processes), and agents (people/software/devices).

- Bold Delivery: provided via an alignment module `alignments/mhm-prov-align.owl` that imports PROV-O.
- Bold Mappings: Measurement/Feature/DerivedFeature/DataSet/DigitalPhenotype ⊑ `prov:Entity`; Computation/SensingActivity ⊑ `prov:Activity`; Participant/Device ⊑ `prov:Agent`.
- Bold Properties: `wasGeneratedBy`, `wasComputedBy` ⊑ `prov:wasGeneratedBy`; `wasDerivedFrom` ⊑ `prov:wasDerivedFrom`; `used*` ⊑ `prov:used`; `wasCollectedFrom`/`wasAttributedTo` ⊑ `prov:wasAttributedTo`.

### SOSA/SSN (W3C Observations)

SOSA models observations and sampling. It defines observations, what property was observed, the feature-of-interest, and timing. Using SOSA terms makes measurement data easier to integrate with other observation datasets.

- Bold In core: DL-safe references; no import.
- Bold Mapping: `connect:Measurement` ⊑ `sosa:Observation`; convenience properties `connect:observedProperty`/`connect:featureOfInterest`; timing via `connect:resultTime` ⊑ `sosa:resultTime`.
- Bold FOI: participant by default for person-centred measures; device or context for device/environmental measures.

### QUDT (Units of Measure)

QUDT provides a structured way to represent quantities, numeric values, and units. This avoids ambiguity and supports consistent processing of measurements across systems.

- Bold In core: DL-safe references; no import.
- Bold Pattern: link Measurement to `qudt:QuantityValue` via `qudt:quantityValue`, then use `qudt:numericValue` and `qudt:unit` (with `unit:` IRIs).
- Bold Legacy: `connect:hasValue`/`connect:hasUnit` retained, marked deprecated for compatibility.

### SKOS (Simple Knowledge Organization System)

SKOS provides simple concept schemes (controlled vocabularies) with labels, definitions, and broader/narrower relations. It is used for lightweight vocabularies such as property categories and questionnaire domains.

- Bold Vocabularies: defined in `vocab/` (`property-categories.ttl`, `question-domains.ttl`) with `skos:prefLabel` (language-tagged), optional `skos:altLabel`, and `skos:definition`.
- Bold Top concepts: schemes declare roots via `skos:hasTopConcept`/`skos:topConceptOf`.
- Bold Tagging: ontology classes can be annotated with `connect:skosTag` pointing to SKOS concepts (DL-safe, non-normative).

### Dublin Core Terms (DCTERMS)

Dublin Core Terms provide standard metadata fields (title, description, license) used for ontology-level annotations.

- Bold Usage: `dcterms:title`, `dcterms:description`, `dcterms:license` as annotation properties in the ontology header.

### IAO (Information Artifact Ontology)

IAO offers common annotations for definitions and editorial notes. Only the definition property is used currently to enhance term documentation.

- Bold Usage: `IAO:0000115` declared as an annotation property for textual definitions.

## Validation & Tooling

- Bold Profile (DL): `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`.
- Bold QA report: `tooling/run_ontology_tools.sh report mhm_ontology.owl`.
- Bold PROV checks: `tooling/run_ontology_tools.sh validate-prov`.
- Bold Units checks: `tooling/run_ontology_tools.sh validate-units`.
- Bold SOSA checks: `tooling/run_ontology_tools.sh validate-sosa`.
- Bold SKOS checks: `tooling/run_ontology_tools.sh validate-skos`.
