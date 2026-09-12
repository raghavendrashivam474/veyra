# Contributing to Project Veyra

Thank you for contributing to Veyra! This document outlines our engineering standards, local development workflows, and automated quality gates.

---

## 1. Core Development Philosophy

Before modifying any code, remember our primary rule:
> **Understand first. Preserve existing work. Change only what is necessary.**

We value clean code, strong architectural boundaries, and extensive test coverage.

---

## 2. Environment Setup

Veyra uses `uv` for lightning-fast, reproducible dependency management.

### Prerequisites
- Python 3.12 or 3.13
- [uv](https://github.com/astral-sh/uv) installed on your system

### Quick Start
Clone the repository and synchronize the environment:
```bash
git clone https://github.com/raghavendrashivam474/veyra.git
cd veyra
uv sync
```
## 3. Local Verification Gates

Before committing or pushing any code, you must run the local quality suite:

```bash
# 1. Check linting and formatting
uv run ruff check .

# 2. Run the test suite (unit, integration, and architecture)
uv run pytest

# 3. Verify the platform runtime health
uv run veyra health
```
### 4. Branching & Commit Style

## Branch Naming Convention

Create scoped branches from the current target milestone branch (e.g., main or active sprint branches):

```text
veyra/s<sprint>-<feature-description>
```
Example: veyra/s0.2-foundation-hardening

### Commit Message Conventions

We follow structured commit messaging:

- feat(scope): New capabilities or integrations.
- fix(scope): Bug fixes.
- test(scope): Adding or correcting tests.
- docs(scope): Documentation additions or adjustments.
- build(scope): Dependency changes, configuration updates.
- chore(scope): General maintenance tasks.

Example:

```text
feat(S0.2): add architectural boundary protection tests
```

## 5. Architectural Boundaries

Veyra enforces a strict dependency-inversion architecture.

- Domain & Application layers must never import or instantiate concrete items from the Infrastructure layer.
- Dependencies flow inward toward the domain logic.
- Architectural boundary checks run automatically on every test run (tests/architecture/test_boundaries.py). Any boundary violation will fail the test suite and block CI.
