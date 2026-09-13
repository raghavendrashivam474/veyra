# Application Layer Architecture

## 1. Role & Responsibility

The Application layer orchestrates workflows between the Veyra Domain Model and future external systems (e.g. databases, VLMs, image generators).
```text
    API / CLI / UI
                  │
                  ▼
          APPLICATION LAYER
 ┌────────────────┼────────────────┐
 │                │                │
CharacterService Perception Representation
Service Service
│ │ │
└────────────────┼────────────────┘
│
APPLICATION PORTS
┌───────────┴───────────┐
│ │
Repository Perception
Ports Engine Port
│ │
▼ ▼
INFRASTRUCTURE INFRASTRUCTURE
(e.g. SQLite) (e.g. Future VLM)
```

### Key Principles

- **Thin Orchestration**: Application services do not hold visual domain modeling logic (which belongs in `domain`) nor raw I/O / DB queries / model inference (which belongs in `infrastructure`).
- **Dependency Inversion**: Services depend on abstract **Ports** (interfaces in `veyra.application.ports`). Concrete adapters in `infrastructure` implement these ports.
- **Pure Domain Boundary**: The domain layer remains completely agnostic of the application and infrastructure layers.

---

## 2. Application Services

| Service | Primary Responsibility | Collaborators / Ports |
|---|---|---|
| `CharacterService` | Orchestrates creation and retrieval of `Character` entities. | `CharacterRepository` |
| `PerceptionService` | Orchestrates visual analysis of a `Reference` for requested traits, persisting resulting observations. | `PerceptionEngine`, `ObservationRepository` |
| `RepresentationService` | Aggregates `Observation` models into `CharacterRepresentation` containers. | Domain models (`CharacterRepresentation`, `Observation`) |

---

## 3. Abstract Ports

Located in `veyra.application.ports`:

### Repositories (`repositories.py`)
- `CharacterRepository`: Protocol for storing/fetching `Character` entities.
- `ReferenceRepository`: Protocol for storing/fetching `Reference` entities.
- `ObservationRepository`: Protocol for storing/fetching `Observation` models (and querying by `ReferenceId`).

### Engines (`perception.py`)
- `PerceptionEngine`: Contract for visual inference models taking a `Reference` + list of `TraitName` and producing domain `Observation` instances.

---

## 4. Architectural Boundaries Protected

Architectural boundary tests in `tests/architecture/test_boundaries.py` enforce:
- `application` cannot import `infrastructure` or `api`.
- `application` cannot import external ML/DB drivers (`torch`, `transformers`, `cv2`, `sqlite3`, `sqlalchemy`).
- `domain` remains isolated from `application`, `infrastructure`, and `api`.

---

## 5. Explicit Non-Goals for S0.4

S0.4 strictly avoids premature implementations of:
- VLM integrations (e.g. Qwen, Transformers, Torch, Ollama, InsightFace).
- Character Genome / DNA / Mutation mechanics.
- Image generation or style conditioning.
- Real production databases (PostgreSQL, pgvector, Redis, MinIO).
- REST API / FastAPI endpoints.
