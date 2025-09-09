# Plan: MHM Ontology cleanup and provenance extension

This checklist proceeds in a sensible, sequential order. We’ll keep changes minimal-but-correct per step and validate with a reasoner after major milestones.

## Core hygiene and metadata

- [ ] Add ontology header: `owl:Ontology` with base IRI, version IRI, `rdfs:label`, `dcterms:creator/date`.
- [ ] Normalize prefixes: declare `rdf`, `rdfs`, `owl`, `xsd`, `connect`, `prov`, `sosa`, `ssn`, `skos`, and `qudt`/`om` (choose one units model).
- [ ] Add `owl:imports`: PROV-O, SOSA (and SSN if needed), SKOS, and chosen units ontology (QUDT or OM); document versions.

## Modeling consistency and deduplication

- [ ] Convert `connect:belongsToLayer` to `owl:AnnotationProperty` (used on classes). Remove the meta-modeling `domain/range` on `owl:Class`.
- [ ] Deduplicate class/property definitions (e.g., `TimeInterval`, `EventWindow`, `ContextualSituation`). Keep one authoritative declaration each.
- [ ] Replace `rdf:Property` usages with proper `owl:ObjectProperty`/`owl:DatatypeProperty` (e.g., `hasMeasurement`).
- [ ] Remove duplicate `hasResponseFormat` declaration; keep one.
- [ ] Fix incorrect layer reference: change `FeatureLayer` to `DerivedFeatureLayer` where used (e.g., `ActivityAndSleepFeature`).
- [ ] Review and narrow broad domains/ranges (e.g., avoid `owl:Thing` for `hasTimestamp/hasStartTime/hasEndTime` unless intentional).

## Labels, comments, and documentation

- [ ] Add `rdfs:label` and `rdfs:comment` to core classes and properties (Measurement, Feature, DerivedFeature, Computation, Context, Question/Response, Phenotype).
- [ ] Add usage notes where modeling choices are non-obvious (e.g., how layers are annotated, alignment intents).

## Units and values

- [ ] Align measurement values with a units ontology: introduce `qudt:Quantity`/`qudt:QuantityValue` or OM equivalents.
- [ ] Deprecate `connect:hasUnit` (string) in favor of units concepts; keep temporarily for backward compatibility.

## Logical structure

- [ ] Consider disjointness axioms among major measurement branches (Physiological, Behavioral, Environmental) if semantically valid.
- [ ] Review global constraints to avoid unintended inferences and keep reasoning decidable (DL profile where possible).

## SOSA/SSN alignment

- [ ] Map `connect:Measurement` to `sosa:Observation` (as subclass) and adopt SOSA terms where beneficial.
- [ ] Introduce `connect:observedProperty` (subPropertyOf `sosa:observedProperty`) and `connect:featureOfInterest` (subPropertyOf `sosa:hasFeatureOfInterest`).
- [ ] Decide FOI strategy (e.g., participant, environment segment, or a domain entity) and document.

## ABox separation and modularization

- [ ] Move example individuals out of `mhm_ontology.owl` into `examples.ttl` (or `examples.owl`), referenced in README.
- [ ] (Optional, later) Split ontology into modules (`mhm-core.owl`, `mhm-measurement.owl`, `mhm-feature.owl`, `mhm-context.owl`, `mhm-questionnaire.owl`, `mhm-phenotype.owl`) and have an umbrella ontology import them.

## PROV-O alignment (sketch and phased implementation)

- [ ] Document mapping in README: 
  - Participant → `prov:Agent` (subClass or `rdf:type` alignment)
  - Device → `prov:Agent` (or `prov:SoftwareAgent`/`prov:Agent` per policy)
  - DataSet/Measurement/Feature → `prov:Entity`
  - Computation → `prov:Activity`
- [ ] Add bridging classes (as needed): 
  - `connect:SensingActivity` ⊑ `prov:Activity`
  - `connect:DataTransferEvent` ⊑ `prov:Activity`
  - `connect:NotificationEvent` ⊑ `prov:Activity`
  - (Option) align existing `connect:Computation` ⊑ `prov:Activity`
- [ ] Align object properties with PROV-O: 
  - Declare `connect:wasGeneratedBy` ⊑ `prov:wasGeneratedBy` (domain: Entities like Measurement/Feature/DataSet; range: `prov:Activity`).
  - Declare `connect:wasDerivedFrom` ⊑ `prov:wasDerivedFrom`.
  - Add `connect:wasAttributedTo` ⊑ `prov:wasAttributedTo` (Entity → Agent) for linking Measurements/DataSets to Participant/Device.
  - Add `connect:associatedWithDevice` ⊑ `prov:wasAssociatedWith` (domain: `prov:Activity`, range: Device) for activity↔agent association.
  - Declare `connect:usedAppInterface` ⊑ `prov:used` (domain: `prov:Activity`, range: Interface) and review `connect:usedDevice` similarly.
- [ ] Verify referenced activity classes exist for property domains (`DataTransferEvent`, `NotificationEvent`); add if missing or adjust domains accordingly.
- [ ] Add minimal examples (in `examples.ttl`) showing PROV chains: Measurement (Entity) → wasGeneratedBy SensingActivity; SensingActivity wasAssociatedWith Device/Participant; DerivedFeature (Entity) wasGeneratedBy Computation; DerivedFeature wasDerivedFrom Measurement; DataSet wasAttributedTo Participant, used DataInterface.

## README updates

- [ ] Add Namespaces section listing all prefixes and base IRIs used.
- [ ] Add Imports section explaining why each external ontology is used.
- [ ] Add Modeling Principles section (layers via annotation; SOSA for observations; QUDT/OM for units; PROV-O for provenance).
- [ ] Add Contribution workflow: branch naming, editing in Protégé, reasoning checks, PR checklist.
- [ ] Add Versioning: version IRI strategy and release tags.
- [ ] Link to `examples.ttl` for quick starts.

