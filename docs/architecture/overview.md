# Architecture Overview

## 1. System Layers and Dependency Direction

Project Veyra adheres to a clean layered architecture with explicit dependency inversion:

```text
       ┌──────────────┐
       │   API / CLI  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │ Application  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │    Domain    │
       └──────────────┘
              ▲
              │ consumes abstractions
       ┌──────┴───────┐
       │Infrastructure│
       └──────────────┘
              │
              ▼
       ┌──────────────┐
       │     Core     │ (Cross-cutting: Settings, logging, errors)
       └──────────────┘
```
### Layer Responsibilities

- **domain/**: Independent of frameworks, databases, and I/O. Contains character identity models, genome descriptors, trait definitions, and verification invariants.
- **application/**: Coordinates business use cases (e.g., identity extraction, genome synthesis, verification checks). Interacts with domain objects and interface ports.
- **infrastructure/**: Implements interface ports with concrete technologies (SQLite, local filesystem asset store, NumPy embeddings, model runtimes).
- **api/**: Delivery mechanisms (CLI, REST API endpoints, SDK handlers).
- **core/**: Shared foundation containing immutable configuration, logging infrastructure, custom exception hierarchies, and utilities.

## 2. Storage & Asset Separation

>To keep the platform performant and scalable:

1. Relational Data (Metadata & Entities): Stored in SQLite for local research, migrating to PostgreSQL for production. Stores character IDs, genome records, asset hashes, dimensions, timestamps, and metadata tags.
2. Binary Assets (Images, Latents, Checkpoints): Stored in data/assets/ locally via LocalAssetStore, separating binary blobs from relational tables.

```text
[ Application ]
       │
 ┌─────┴────────────────┐
 │                      │
 ▼                      ▼
[ Metadata Repository ] [ Asset Store ]
       │                      │
       ▼                      ▼
 SQLite / Postgres     Local FS / S3 / MinIO
```

## 3. Replaceability Strategy

>Every infrastructure adapter implements a well-defined boundary. Swapping SQLite for PostgreSQL or local filesystem for S3 requires adding a new concrete implementation in infrastructure/ without changing domain or application services.
