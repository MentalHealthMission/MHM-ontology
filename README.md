 MHM Ontology Structure

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
