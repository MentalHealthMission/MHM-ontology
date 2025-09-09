# MHM Ontology: Classes, Properties, and External Alignments

This document summarizes the core classes and properties in the MHM ontology and explains how external ontologies are used.

## Top-level Classes

- Measurement: A single observation/data point. Also aligned to `sosa:Observation` and `prov:Entity`.
- Feature: An attribute computed from measurements. `prov:Entity`.
- DerivedFeature: A Feature computed from other features/measurements. `prov:Entity`.
- Computation: A process that computes features or infers phenotypes. `prov:Activity`.
- SensingActivity: A computation sub-class representing capture of sensor data. `prov:Activity`.
- DigitalPhenotype (+ subtypes): Higher-level constructs derived from features. `prov:Entity`.
- Participant: Study participant. `prov:Agent`.
- Device (+ subtypes): Hardware/software agent used to collect data. `prov:Agent`.
- Interface (+ AppInterface, DataInterface): Software interfaces for data capture/transfer.
- DataSet (+ SensorDataSet, QuestionnaireDataSet, ParticipantDataSet): Collections of data items. `prov:Entity`.
- Context classes: ObservationContext, TimeInterval (Hourly/Daily/Weekly), EventWindow, ContextualSituation (Weekend, NightTime, etc.).
- Questionnaire classes: QuestionnaireEntry, ResponseItem, Question, ResponseFormat (+ Slider/MultipleChoice/Text/Likert), QuestionDomain (+ Mood/Sleep/Stress/Paranoia).

## Key Properties (selected)

- hasMeasurement (Feature → Measurement): Inputs to feature computation.
- observedProperty (Measurement → resource): Sub-property of `sosa:observedProperty`.
- featureOfInterest (Measurement → resource): Sub-property of `sosa:hasFeatureOfInterest`.
- resultTime (Measurement → xsd:dateTime): Sub-property of `sosa:resultTime`.
- qudt:quantityValue (Measurement → qudt:QuantityValue): Link to quantity value.
  - qudt:numericValue / connect:numericValue (QuantityValue → numeric literal)
  - qudt:unit (QuantityValue → unit:...)
- wasGeneratedBy (Entity → Computation): Sub-property of `prov:wasGeneratedBy`.
- wasComputedBy (DerivedFeature → Computation): Sub-property of `prov:wasGeneratedBy`.
- wasDerivedFrom (Entity → Thing): Sub-property of `prov:wasDerivedFrom`.
- usedDevice (Activity → Device), usedAppInterface (Activity → AppInterface), usedDataInterface (DataSet → DataInterface): Sub-properties of `prov:used`.
- wasCollectedFrom (DataSet → Participant), wasAttributedTo (Entity → Participant): Sub-property of `prov:wasAttributedTo`.
- hasTimestamp / hasStartTime / hasEndTime: Contextual timing (legacy utilities).

## External Ontologies and Usage

- PROV-O (Provenance)
  - Provided via an alignment module: `alignments/mhm-prov-align.owl` (imports PROV-O).
  - Core mappings: Measurement/Feature/DerivedFeature/DataSet/DigitalPhenotype ⊑ `prov:Entity`; Computation/SensingActivity ⊑ `prov:Activity`; Participant/Device ⊑ `prov:Agent`.
  - Properties mapped: wasGeneratedBy, wasComputedBy ⊑ `prov:wasGeneratedBy`; wasDerivedFrom ⊑ `prov:wasDerivedFrom`; used* ⊑ `prov:used`; wasCollectedFrom/wasAttributedTo ⊑ `prov:wasAttributedTo`.
  - Rationale: keep core in OWL DL; full PROV semantics live in the alignment module.

- SOSA/SSN (Observations)
  - DL-safe references in core; no import.
  - Measurement ⊑ `sosa:Observation`; convenience properties observedProperty/featureOfInterest; timing via `resultTime`.
  - Feature-of-interest strategy: participant by default for person-centred measures; device or context for device/environmental measures.

- QUDT (Units)
  - DL-safe references in core; no import.
  - Use `qudt:QuantityValue` linked from Measurement via `qudt:quantityValue` with `qudt:numericValue` and `qudt:unit` (and convenience `connect:numericValue`).
  - Legacy `connect:hasValue` and `connect:hasUnit` are deprecated but retained for compatibility.

- Dublin Core Terms (dcterms)
  - Used for ontology metadata (title, description, license) as annotation properties.

- IAO (Information Artifact Ontology)
  - `IAO:0000115` declared as an annotation property for definitions. To be used progressively to enrich documentation and reduce QA warnings.

## Validation & Tooling

- Core DL profile: `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`.
- QA report: `tooling/run_ontology_tools.sh report mhm_ontology.owl`.
- PROV alignment checks: `tooling/run_ontology_tools.sh validate-prov`.
- Units checks: `tooling/run_ontology_tools.sh validate-units`.
- SOSA checks: `tooling/run_ontology_tools.sh validate-sosa`.

