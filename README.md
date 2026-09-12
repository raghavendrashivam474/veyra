# Project Veyra

> **Visual Identity Intelligence Platform**

Project Veyra is a research-oriented visual identity intelligence platform designed to computationally represent, preserve, transform, manipulate, and verify visual identity across visual modalities.

---

## Vision

Veyra investigates the foundational question:

> *How can visual identity be represented computationally so that important characteristics can be preserved, transformed, manipulated, verified, and eventually carried across different visual modalities?*

The end-to-end pipeline:

```text
Reference Image
      ↓
Visual Perception
      ↓
Fine-Grained Character Representation
      ↓
Character DNA / Genome
      ↓
Controlled Abstraction
      ↓
New Fictional Character
      ↓
Generation
      ↓
Consistency Verification
      ↓
Persistent Visual Identity
      ↓
Modality Progression: Image → Video → 3D → Interactive Persona
```
> Veyra is not a simple avatar generator. It is an identity representation and            consistency     engine.

## Current Status: Sprint S0.1 (Foundation)

> Sprint S0.1 establishes the repository root, architectural boundaries, dependency baseline, safe data management, and the minimal health-check runtime.

## Architecture Principles

>Local-First Development: Lightweight local development using SQLite, local filesystem asset storage, and NumPy vector representations for zero infrastructure friction during early research.
>Replaceable Infrastructure: Strict separation between domain/application logic and persistence/asset stores. Core domain models do not depend directly on SQLite, S3, or specific vector databases.

### Clean Boundaries:
```text
src/veyra/domain: Pure entity definitions, invariants, and conceptual genomes.
src/veyra/application: Use-case orchestration and application workflows.
src/veyra/infrastructure: Concrete adapters (database, local assets, embeddings, model runtimes).
src/veyra/api: External entrypoints (CLI, REST, SDK).
src/veyra/core: Cross-cutting primitives (config, logging, errors).
```

## Roadmap
```text
Sprint / Phase    Focus
S0 Foundation    Repository layout, architectural boundaries, runtime baseline
S1 Perception    Visual perception, feature extraction, landmark/face/body analysis
S2 Character Representation    Fine-Grained character representation, Character DNA / Genome schema
S3 Character Engine    Abstraction mechanisms, controlled character mutation
S4 Identity Engine    Visual generation orchestration, consistency verification
S5 Character Intelligence    Memory, visual consistency tracking across scenes/prompts
S6 Multimodal Identity    Video & 3D representation integration
S7 Persona Engine    Interactive visual persona integration
```

## Quick Start

### Prerequisites
>Python 3.11+
>uv (recommended) or standard pip
>Installation
```Bash
# Sync dependencies and install package in editable mode
uv sync --extra dev
```
## Health Check
Verify your local environment and foundational infrastructure:
```Bash
uv run veyra health
```
## Running Tests
```Bash
uv run pytest
```
## Repository Structure
```text
veyra/
├── src/
│   └── veyra/
│       ├── api/               # CLI / REST entrypoints
│       ├── application/       # Use-case orchestration
│       ├── core/              # Config, logging, common primitives
│       ├── domain/            # Pure business & character models
│       └── infrastructure/    # Database, asset, embedding adapters
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── data/                      # Local runtime data (ignored from git)
│   ├── database/
│   ├── assets/
│   ├── references/
│   └── experiments/
├── configs/                   # System & model configuration files
├── scripts/                   # Development and utility scripts
├── docs/                      # Architectural specs & ADRs
└── migrations/                # Database schema migrations
```
## License
>MIT