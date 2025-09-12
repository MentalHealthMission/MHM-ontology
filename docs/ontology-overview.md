# ODIM-MH Overview

ODIM‑MH is an ontology for representing high‑level digital markers derived from wearable and mobile sensing in health studies. It models how raw measurements become derived features, how those computations are described and attributed, and how results are situated in time and context. It uses explicit units, aligns its observation and provenance patterns with web standards, and offers lightweight vocabularies to categorize properties and questionnaire domains.

## Overview

- **Goal:** provide an ontology for capturing high‑level features derived from wearable device data in health‑related studies. The model standardizes how features and their source measurements are described, records provenance of computations, uses explicit units, and aligns with common web standards to enable integration and reuse across projects.
- **Design:** a DL-safe core with lightweight references to external standards (SOSA, SKOS, QUDT) and a separate PROV-O alignment module for full provenance semantics.
- **Usage:** classes and properties for measurements, features, context, questionnaires, phenotypes, and provenance, with examples and validation scripts.

## Intended Users (non‑exhaustive)

- Researchers and data scientists analyzing wearable/device data in health studies.
- Clinicians and domain experts collaborating on study design and interpretation.
- Data engineers integrating multi‑source data with consistent semantics.
- Ontology/knowledge engineers extending mappings and validation.

## Layers

- **Measurement Layer:** raw observations from devices and apps (e.g., heart rate, steps, sleep stages, ambient light).
- **Derived Feature Layer:** features calculated from measurements (e.g., sleep regularity, activity duration).
- **Computation Layer:** processes that generate features or phenotypes (algorithms, models, rules).
- **Contextual Layer:** contextual information such as time intervals and situations.
- **Questionnaire Layer:** questions, response formats, and responses collected from participants.
- **Provenance Layer:** entities, activities, and agents describing origin and processing of data.
- **Digital Phenotype Layer:** higher-level constructs inferred from features.

## Top-level Classes

- **Measurement:** a single observation/data point; aligned to `sosa:Observation` and `prov:Entity`.
- **Feature:** an attribute computed from measurements; `prov:Entity`.
- **DerivedFeature:** a Feature computed from other features/measurements; `prov:Entity`.
- **Computation:** a process that computes features or infers phenotypes; `prov:Activity`.
- **SensingActivity:** an activity representing sensor data capture; `prov:Activity`.
- **DigitalPhenotype:** higher-level constructs derived from features; `prov:Entity`.
- **Participant:** study participant; `prov:Agent`.
- **Device:** hardware/software agent used to collect data; `prov:Agent`.
- **Interface:** software interfaces used for capture/transfer.
- **DataSet:** collections of data items (SensorDataSet, QuestionnaireDataSet, ParticipantDataSet); `prov:Entity`.
- **Context classes:** ObservationContext, TimeInterval (Hourly/Daily/Weekly), EventWindow, ContextualSituation.
- **Questionnaire classes:** QuestionnaireEntry, ResponseItem, Question, ResponseFormat (Slider/MultipleChoice/Text/Likert).

## Key Properties (selected)

- **hasMeasurement:** Feature → Measurement; inputs to feature computation.
- **observedProperty:** Measurement → resource; sub-property of `sosa:observedProperty`.
- **featureOfInterest:** Measurement → resource; sub-property of `sosa:hasFeatureOfInterest`.
- **resultTime:** Measurement → `xsd:dateTime`; sub-property of `sosa:resultTime`.
- **qudt:quantityValue:** Measurement → `qudt:QuantityValue`.
  - **qudt:numericValue / connect:numericValue:** QuantityValue → numeric literal.
  - **qudt:unit:** QuantityValue → `unit:...`.
- **wasGeneratedBy / wasComputedBy:** Entity → Activity; sub-property of `prov:wasGeneratedBy`.
- **wasDerivedFrom:** Entity → Entity; sub-property of `prov:wasDerivedFrom`.
- **usedDevice / usedAppInterface / usedDataInterface:** Activity/DataSet → Device/Interface; sub-properties of `prov:used`.
- **wasCollectedFrom / wasAttributedTo:** DataSet/Entity → Participant; sub-property of `prov:wasAttributedTo`.
- **hasTimestamp / hasStartTime / hasEndTime:** contextual timing utilities.

## External Ontologies and Usage

The ontology references well-known standards to improve interoperability. The core keeps DL profile compliance by using minimal declarations and avoids importing large external ontologies, except for an explicit PROV-O alignment module.

### PROV-O (W3C Provenance)

Provenance describes where data comes from, who created it, and how it was produced. PROV-O provides a common vocabulary for entities (data), activities (processes), and agents (people/software/devices).

- **Delivery:** provided via an alignment module `alignments/mhm-prov-align.owl` that imports PROV-O.
- **Mappings:** Measurement/Feature/DerivedFeature/DataSet/DigitalPhenotype ⊑ `prov:Entity`; Computation/SensingActivity ⊑ `prov:Activity`; Participant/Device ⊑ `prov:Agent`.
- **Properties:** `wasGeneratedBy`, `wasComputedBy` ⊑ `prov:wasGeneratedBy`; `wasDerivedFrom` ⊑ `prov:wasDerivedFrom`; `used*` ⊑ `prov:used`; `wasCollectedFrom`/`wasAttributedTo` ⊑ `prov:wasAttributedTo`.

### SOSA/SSN (W3C Observations)

SOSA models observations and sampling. It defines observations, what property was observed, the feature-of-interest, and timing. Using SOSA terms makes measurement data easier to integrate with other observation datasets.

- **In core:** DL-safe references; no import.
- **Mapping:** `connect:Measurement` ⊑ `sosa:Observation`; convenience properties `connect:observedProperty`/`connect:featureOfInterest`; timing via `connect:resultTime` ⊑ `sosa:resultTime`.
- **FOI:** participant by default for person-centred measures; device or context for device/environmental measures.

### QUDT (Units of Measure)

QUDT provides a structured way to represent quantities, numeric values, and units. This avoids ambiguity and supports consistent processing of measurements across systems.

- **In core:** DL-safe references; no import.
- **Pattern:** link Measurement to `qudt:QuantityValue` via `qudt:quantityValue`, then use `qudt:numericValue` and `qudt:unit` (with `unit:` IRIs).
- **Legacy:** `connect:hasValue`/`connect:hasUnit` retained, marked deprecated for compatibility.

### SKOS (Simple Knowledge Organization System)

SKOS provides simple concept schemes (controlled vocabularies) with labels, definitions, and broader/narrower relations. It is used for lightweight vocabularies such as property categories and questionnaire domains.

- **Vocabularies:** defined in `vocab/` (`property-categories.ttl`, `question-domains.ttl`) with `skos:prefLabel` (language-tagged), optional `skos:altLabel`, and `skos:definition`.
- **Top concepts:** schemes declare roots via `skos:hasTopConcept`/`skos:topConceptOf`.
- **Tagging:** ontology classes can be annotated with `connect:skosTag` pointing to SKOS concepts (DL-safe, non-normative).

### Dublin Core Terms (DCTERMS)

Dublin Core Terms provide standard metadata fields (title, description, license) used for ontology-level annotations.

- **Usage:** `dcterms:title`, `dcterms:description`, `dcterms:license` as annotation properties in the ontology header.

### IAO (Information Artifact Ontology)

IAO offers common annotations for definitions and editorial notes. Only the definition property is used currently to enhance term documentation.

- **Usage:** `IAO:0000115` declared as an annotation property for textual definitions.

## Validation & Tooling

- **Profile (DL):** `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`.
- **QA report:** `tooling/run_ontology_tools.sh report mhm_ontology.owl`.
- **PROV checks:** `tooling/run_ontology_tools.sh validate-prov`.
- **Units checks:** `tooling/run_ontology_tools.sh validate-units`.
- **SOSA checks:** `tooling/run_ontology_tools.sh validate-sosa`.
- **SKOS checks:** `tooling/run_ontology_tools.sh validate-skos`.

## Visualizations

Canonical diagrams (auto-generated; refreshed via `tooling/run_ontology_tools.sh visualize-all mhm_ontology.owl`):

- Class hierarchy: `docs/visualizations/class-hierarchy.svg`
- Object properties: `docs/visualizations/object-properties.svg`
- Data properties: `docs/visualizations/data-properties.svg`
