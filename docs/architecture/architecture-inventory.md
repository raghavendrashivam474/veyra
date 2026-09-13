# Architecture Inventory

> Generated during S0.5 Phase-0 Architecture Review.
> Baseline: v0.4.0a0 (commit 415f81e)
> Status: Validated, no structural changes required for S1.

---

## 1. Layer Map

```text
src/veyra/
├── api/                  # External interaction boundary
│   └── cli.py            # CLI entry point (veyra command)
├── application/          # Workflow orchestration
│   ├── ports/            # Abstract contracts (dependency inversion)
│   │   ├── perception.py # PerceptionEngine port
│   │   └── repositories.py # CharacterRepository, ReferenceRepository, ObservationRepository
│   └── services/         # Use-case orchestration
│       ├── character_service.py
│       ├── perception_service.py
│       └── representation_service.py
├── core/                 # Cross-cutting foundation
│   └── config.py         # Settings (pydantic-settings, VEYRA_ env prefix)
├── domain/               # Pure domain model (zero infrastructure)
│   ├── character.py      # Character entity
│   ├── ids.py            # CharacterId, ReferenceId, ObservationId
│   ├── observations.py   # Observation value object
│   ├── reference.py      # Reference entity + ReferenceSourceType
│   ├── representation.py # CharacterRepresentation aggregate
│   └── traits.py         # TraitName, TraitValue, Confidence
└── infrastructure/       # Concrete external implementations
    ├── assets/
    │   └── local.py      # LocalAssetStore (filesystem)
    ├── database/
    │   └── sqlite.py     # SQLiteDatabase (connectivity/ping)
    ├── embeddings/       # Placeholder for S1+ embedding storage
    └── models/           # Placeholder for S1+ model adapters
```

## 2. Layer Responsibilities

Layer    Owns    Must NOT import
domain    Entities, value objects, invariants, domain IDs    infrastructure, application, api, sqlalchemy, sqlite3, torch, transformers, cv2
application    Use-case orchestration, port abstractions    infrastructure, api, sqlalchemy, sqlite3, torch, transformers, cv2
core    Configuration, cross-cutting utilities    domain, application, infrastructure, api
infrastructure    Concrete adapters (DB, filesystem, future ML)    api (should not reach upward)
api    CLI, future REST/SDK    (top of dependency chain)

## 3. Dependency Direction
```text
api --> application --> domain <-- infrastructure
                            ^
                           core (used by all layers)
```

Infrastructure implements application ports. Application never imports infrastructure.
This is enforced by tests/architecture/test_boundaries.py.

## 4. Application Ports (Research Seams)

### PerceptionEngine (S1 research seam)
```Python
class PerceptionEngine(ABC):
    @abstractmethod
    def observe(self, reference: Reference, traits: list[TraitName]) -> list[Observation]:
        ...
```
- Location: application/ports/perception.py
- Purpose: Abstract contract for any visual perception model (VLM, face analyzer, etc.)
- S1 readiness: A real VLM implementation can be placed in infrastructure/models/ and injected into PerceptionService
  without any ML imports leaking into application or domain layers.
- Key property: The Observation.evidence: dict[str, Any] field provides a domain-agnostic container for rich perception
  output (bounding boxes, attention maps, etc.) without coupling the domain to any specific model output format.

### Repository Ports
```Python
CharacterRepository   -> save(Character), get(CharacterId)
ReferenceRepository   -> save(Reference), get(ReferenceId)
ObservationRepository -> save(Observation), get(ObservationId), get_by_reference(ReferenceId)
```

- Location: application/ports/repositories.py
- Purpose: Persistence abstraction. Currently implemented by in-memory fakes for testing.
- S1 readiness: S1 can add SQLite-backed implementations in infrastructure/database/ without changing application services.

## 5. Domain Model
```text
Concept    Type    Key Properties
Character    Entity (mutable)    id, name, description
Reference    Entity (frozen)    id, asset_id (opaque string), source_type, metadata
Observation    Value Object (frozen)    id, reference_id, trait, value, confidence, source, evidence, created_at
CharacterRepresentation    Aggregate (mutable)    character_id, observations[], version, metadata
TraitName    Value Object (frozen)    namespaced string (e.g. "appearance.hair_color")
TraitValue    Value Object (frozen)    raw value (str/int/float)
Confidence    Value Object (frozen)    score 0.0 to 1.0
```

## 6. Configuration

- Mechanism: pydantic-settings with VEYRA_ environment variable prefix
- File: core/config.py then Settings class
- Key fields: env, debug, base_dir, data_dir, database_url, asset_storage_dir, embedding_storage_dir
- Extensibility: extra="ignore" allows S1 to add perception/experiment config fields without breaking existing code.
- Model neutrality: No ML-specific configuration exists. This is intentional and correct for Phase 0.

## 7. Data Layout

```text
data/
├── assets/         # Binary assets (images, etc.) -- gitignored
├── database/       # SQLite files -- gitignored
├── experiments/    # Experiment outputs/artifacts -- gitignored
│   └── embeddings/ # Embedding experiment outputs
└── references/     # Reference images --
```

All data directories are excluded from Git via .gitignore. Only .gitkeep files are tracked.

## 8. Infrastructure Placeholders

The following directories exist as empty packages (__init__.py only):

- infrastructure/embeddings/ -- Reserved for S1+ embedding storage adapters
- infrastructure/models/ -- Reserved for S1+ perception model adapters

These are intentional placeholders. They should not be populated until S1 research produces concrete implementations.
