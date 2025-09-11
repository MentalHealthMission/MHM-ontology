# ODIM-MH (Ontology for Digital Markers in Mental Health)

## Introduction

The MHM ontology organizes data from participants, devices, and measurements into a formal structure for study integration and reasoning.

## Layers

### 1. Measurement Layer

This layer includes classes for the **raw measurements** collected from devices and apps. Measurements represent data points like heart rate, steps, sleep stages, and environmental factors.

- **Measurement**: The basic class for any measurement.
- **PhysiologicalMeasurement**: Subclass of Measurement, includes things like heart rate and respiratory rate.
- **BehavioralMeasurement**: Subclass of Measurement, includes activity and sleep stages.
- **EnvironmentalMeasurement**: Subclass of Measurement, includes things like ambient light or temperature.

### 2. Derived Feature Layer

This layer includes **features** derived from raw measurements. These are typically used for further analysis or modeling.

- **Feature**: The base class for any feature derived from measurements.
- **DerivedFeature**: Subclass of Feature, represents features like sleep regularity or activity patterns.

### 3. Computation Layer

This layer includes classes related to **computational processes** such as algorithms, models, and inference rules used to derive features from raw data.

- **Computation**: The base class for all computational processes.
- **AlgorithmicComputation**: Subclass of Computation, represents predefined algorithms.
- **ModelBasedComputation**: Subclass of Computation, represents model-based methods for feature extraction.
- **InferenceRule**: Subclass of Computation, represents rules that infer phenotypes based on features.

### 4. Contextual Layer

This layer includes classes for **contextual information** that provides meaning to measurements, like time intervals and situational context.

- **ObservationContext**: The base class for any context in which a measurement is observed.
- **TimeInterval**: Subclass of ObservationContext, represents intervals like hourly or daily intervals.
- **ContextualSituation**: Subclass of ObservationContext, represents specific situations like "NightTime" or "Weekend."

### 5. Questionnaire Layer

This layer defines the structure for **questionnaire data** collected from participants, such as responses to surveys.

- **QuestionnaireEntry**: The base class for questionnaire entries.
- **Question**: Represents individual questions in a survey.
- **ResponseItem**: Represents responses to specific questions.
- **ResponseFormat**: Represents the format in which responses are collected (e.g., Likert scale, multiple choice).

### 6. Provenance Layer

This layer tracks the **origin** of data and how it is associated with participants and devices.

- **Participant**: Represents an individual participating in the study.
- **Device**: Represents the devices used to collect data, such as smartphones or wearables.
- **DataSet**: Represents collections of data associated with a specific participant.
- **Interface**: Represents software interfaces used to collect or transmit data.

### 7. Digital Phenotype Layer

This layer includes classes for **digital phenotypes**, which are higher-level constructs derived from measurements and features to represent mental health or other conditions.

- **DigitalPhenotype**: The base class for any digital phenotype.
- **MoodPhenotype**: Subclass of DigitalPhenotype, represents mood-related conditions.
- **SleepPhenotype**: Subclass of DigitalPhenotype, represents sleep-related conditions.
- **ActivityPhenotype**: Subclass of DigitalPhenotype, represents activity-related conditions.
- **SocialPhenotype**: Subclass of DigitalPhenotype, represents social interaction patterns.

## Properties

The ontology defines a series of properties that establish relationships between the classes:

- **hasMeasurement**: Relates a feature to the measurements used to derive it.
- **hasContext**: Relates an entity (e.g., measurement, feature) to a specific context.
- **belongsToLayer**: Relates a class to a specific layer in the ontology.
- **wasGeneratedBy**: Relates a measurement to the device or interface that generated it.
- **wasReportedBy**: Relates questionnaire responses to the participant providing them.
- **wasCollectedFrom**: Relates a dataset to the participant from whom the data was collected.
## Namespaces

- `odim`: `http://connectdigitalstudy.com/ontology#` (recommended prefix; current base IRI)
- `connect`: `http://connectdigitalstudy.com/ontology#` (legacy alias; same IRI as `odim:`)
- `rdf`: `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
- `rdfs`: `http://www.w3.org/2000/01/rdf-schema#`
- `owl`: `http://www.w3.org/2002/07/owl#`
- `xsd`: `http://www.w3.org/2001/XMLSchema#`
- `prov`: `http://www.w3.org/ns/prov#` (referenced without import; see below)
- `sosa`: `http://www.w3.org/ns/sosa/` (DL-safe references; no import)
- `skos`: `http://www.w3.org/2004/02/skos/core#` (DL-safe references; no import)
- `dcterms`: `http://purl.org/dc/terms/` (annotations)
- `qudt`: `http://qudt.org/schema/qudt/` (DL-safe references; no import)
- `unit`: `http://qudt.org/vocab/unit/`

## Imports

The core ontology (`mhm_ontology.owl`) is kept in OWL DL. External vocabularies are referenced DL‑safely without imports (SOSA, SKOS, QUDT). A separate alignment module brings in PROV‑O for full provenance mapping. The public name is ODIM‑MH; the current base IRI remains under the CONNECT domain and is exposed via the `odim:` prefix:

- Core (DL): `mhm_ontology.owl` (no external imports; DL‑safe references to `sosa:`, `skos:`, `qudt:`)
- Alignment (OWL Full via PROV‑O): `alignments/mhm-prov-align.owl` imports `mhm_ontology.owl` and `http://www.w3.org/ns/prov-o`

## Modeling Principles

- Layers are indicated via the annotation `connect:belongsToLayer` on classes.
- Measurements loosely align with SOSA Observations (future import), but are modeled as `connect:Measurement` now.
- Units: measurements can link to a `qudt:QuantityValue` via `qudt:quantityValue`, with `qudt:numericValue` and a `qudt:unit` (from the `unit:` vocabulary). Legacy `connect:hasUnit`/`connect:hasValue` remain for compatibility and are marked deprecated.
- SOSA alignment: `connect:Measurement` is aligned to `sosa:Observation`. Convenience properties `connect:observedProperty` and `connect:featureOfInterest` are provided as sub-properties of the SOSA terms.
- FOI strategy: by default, the feature of interest is the study Participant for person‑centred measures (e.g., heart rate, activity, sleep). Device or context may be the FOI for device or environment measures (e.g., ambient light).
- Timing: measurements can carry a `connect:resultTime` (subPropertyOf `sosa:resultTime`) with an `xsd:dateTime` value.
- SKOS vocabularies: lightweight concept schemes (e.g., Property Categories, Question Domains) model project vocabularies using `skos:Concept`/`skos:ConceptScheme`, with `skos:prefLabel` (language‑tagged) and `skos:definition`. Schemes define roots via `skos:hasTopConcept`/`skos:topConceptOf`. Where linking classes to SKOS concepts is useful, use annotations (e.g., `rdfs:seeAlso`) to stay DL‑safe.
  - Class tagging: use `connect:skosTag` (AnnotationProperty) to tag ontology classes with SKOS concepts. Tags live in `vocab/skos-tags.ttl` for manageability.
- Provenance alignment:
  - Core uses PROV classes/props as references (DL-safe declarations). Properties/types are aligned in `alignments/mhm-prov-align.owl`, which imports PROV-O.
  - Entities: Measurement, Feature, DerivedFeature, DataSet, DigitalPhenotype ⊑ `prov:Entity`.
  - Activities: Computation, SensingActivity, DataTransferEvent, NotificationEvent ⊑ `prov:Activity`.
  - Agents: Participant, Device ⊑ `prov:Agent`.
  - Properties: `wasGeneratedBy`, `wasComputedBy` ⊑ `prov:wasGeneratedBy`; `wasDerivedFrom` ⊑ `prov:wasDerivedFrom`; `usedDevice`/`usedAppInterface`/`usedDataInterface` ⊑ `prov:used`; `wasCollectedFrom`/`wasAttributedTo` ⊑ `prov:wasAttributedTo`; `associatedWithDevice` ⊑ `prov:wasAssociatedWith`.

## Examples

Example individuals have been moved to `examples.ttl` to keep the main ontology (TBox) clean and OWL DL compliant.

## Tooling

Use the Dockerized tooling in `tooling/`:

- Build image: `tooling/run_ontology_tools.sh build`
- Syntax check: `tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl`
- OWL DL profile (core): `tooling/run_ontology_tools.sh profile mhm_ontology.owl DL`
- PROV alignment syntax: `tooling/run_ontology_tools.sh check-syntax alignments/mhm-prov-align.owl`
- PROV alignment profile: `tooling/run_ontology_tools.sh profile alignments/mhm-prov-align.owl DL` (expected to fail DL due to PROV-O; this is normal)
- QA report: `tooling/run_ontology_tools.sh report mhm_ontology.owl` (writes `report.tsv`)
- Validate units examples: `tooling/run_ontology_tools.sh validate-units`
- Validate SOSA alignment: `tooling/run_ontology_tools.sh validate-sosa`
- Validate SKOS vocabularies: `tooling/run_ontology_tools.sh validate-skos` (merges `vocab/*.ttl` + examples)
