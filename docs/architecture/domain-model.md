# Veyra Domain Model

## Purpose

The domain model provides Veyra's **technology-independent vocabulary**
for visual identity research. It describes *what Veyra knows*, not
*how Veyra stores, analyzes, or generates it*.

This separation ensures that research in S1/S2 can evolve perception
models, storage backends, and generation systems without destabilizing
the core concepts.

## Dependency Direction
```text

                Veyra Domain
                     |
      +--------------+--------------+
      v              v              v
  Perception     Generation      Storage
  adapters       adapters        adapters
```

 The domain **never** imports infrastructure, ML frameworks,
database drivers, or API libraries.

## Core Concepts

### Identifiers (Value Objects)

| Type | Purpose |
|---|---|
| `CharacterId` | Unique identity for a character |
| `ReferenceId` | Unique identity for a reference |
| `ObservationId` | Unique identity for an observation |

All identifiers are frozen value objects wrapping a string.
They carry no infrastructure meaning (no SQLite row IDs).

### TraitName (Value Object)

A namespaced trait identifier using the format `namespace.name`.

Examples: `facial.eye_shape`, `hair.texture`, `silhouette.shoulder_width`

The taxonomy is **intentionally open**. S0.3 establishes the
abstraction; S1/S2 research determines the real ontology.

### TraitValue (Value Object)

The observed value of a trait. Accepts `str`, `float`, or `int`.
Kept deliberately simple for S0.3.

### Confidence (Value Object)

Normalized confidence score in `[0.0, 1.0]`.
Model-agnostic - does not assume any particular VLM's mechanism.

### Reference (Entity)

Source material for visual identity analysis.
Reference
|-- id: ReferenceId
|-- asset_id: str (opaque handle, not a file path)
|-- source_type: enum
|-- created_at: datetime
-- metadata: dict


- A Reference is **not** a Character. Multiple references may
  contribute to a single CharacterRepresentation.

### Character (Entity)

The persistent fictional identity being developed.
Character
|-- id: CharacterId
|-- name: str
|-- description: str
-- created_at: datetime


Deliberately minimal at S0.3. The full Character Genome
is a research deliverable for S2.

### Observation (Value Object)

A single perception result about a reference.
Observation
|-- id: ObservationId
|-- reference_id: ReferenceId
|-- trait: TraitName
|-- value: TraitValue
|-- confidence: Confidence
|-- source: str (e.g. 'qwen-vl-72b')
|-- evidence: dict
-- created_at: datetime


Key distinction: an Observation is *what a model reported*,
not an absolute truth.

### CharacterRepresentation (Aggregate)

The structured visual identity knowledge about a character.
CharacterRepresentation
|-- character_id: CharacterId
|-- observations: list[Observation]
|-- version: str
|-- metadata: dict
-- updated_at: datetime

text


This is the **container**, not the final Genome.

## Relationships
```text
Reference
|
v (produces)
Observation
|
+-- TraitName
+-- TraitValue
-- Confidence
|
v (collected into)
CharacterRepresentation
|
v (belongs to)
Character
```

## Explicitly Open Questions

The following are **deliberately not frozen** at S0.3:

- Complete Character Genome schema
- Final trait ontology / taxonomy
- DNA representation format
- Embedding dimensions or fusion strategy
- VLM response schema
- Facial landmark schema
- Generation parameters
- Identity similarity metrics
- Persistence / database schema
- API request/response formats

These will be determined by research evidence in S1/S2,
not by architectural assumptions in S0.

## Design Decisions

- **dataclasses over Pydantic** for domain objects: keeps the domain
  layer free of external dependencies. Pydantic remains available for
  API and infrastructure boundaries.
- **Frozen value objects** for identifiers, traits, confidence,
  and observations: these are immutable by domain semantics.
- **Mutable Character and Representation**: these evolve over time
  as new observations arrive.
