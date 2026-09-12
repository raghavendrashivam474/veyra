# ADR-001: Local-First Storage and Replaceable Infrastructure

- **Status:** Accepted
- **Date:** 2025-05-01
- **Deciders:** Veyra Core Architecture Team
- **Sprint:** S0.1

---

## Context

Project Veyra is in an active research phase exploring visual identity representation, Character DNA genomes, and consistency verification. Introducing distributed services (PostgreSQL, pgvector, MinIO, Redis, S3) early introduces setup friction, operational overhead, and slows iteration speed.

At the same time, hardcoding the codebase to local SQLite paths or filesystem operations risks major refactoring costs when scaling up later.

---

## Decision

1. **Local-First Persistence:** Use SQLite for relational metadata and local filesystem storage for binary assets during early research sprints.
2. **Separation of Blob and Metadata:** Binary assets (reference images, intermediate latent representations, synthesized outputs) will **never** be stored directly inside the relational database.
3. **Decoupled Interfaces:** Persistence and asset operations must go through clean infrastructure adapters (`SQLiteDatabase`, `LocalAssetStore`).
4. **NumPy Vector Search Baseline:** High-dimensional embeddings will initially be handled locally with NumPy arrays before adopting dedicated vector search engines (e.g., pgvector).

---

## Consequences

### Positive
- Zero infrastructure dependencies: can run immediately on developer laptops and local GPU environments.
- Fast iteration cycles for experimental models and genome schema designs.
- Clear migration path to PostgreSQL / S3 / pgvector without touching domain logic.

### Negative / Trade-offs
- Concurrency is limited by SQLite file-locking under high parallel write loads.
- Large embedding collections will eventually require a vector indexing service when scale exceeds local memory efficiency.

---

## Migration Path

When moving to multi-node or production deployments:
1. Replace `SQLiteDatabase` with a PostgreSQL adapter (`infrastructure/database/postgres.py`).
2. Replace `LocalAssetStore` with an S3/MinIO adapter (`infrastructure/assets/s3.py`).
3. Replace NumPy vector arrays with pgvector/Milvus.
