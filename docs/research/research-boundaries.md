# Research Boundaries

> Defined during S0.5 Phase-0 Architecture Review.
> Governs where S1+ research artifacts belong.

---

## 1. Experiment Documentation

**Location**: `docs/experiments/`

- **Purpose**: Experiment definitions, methodology, hypotheses, and findings.
- **Naming convention**: `EXP-NNN-short-name.md`
- **Version control**: Tracked in Git.

Example structure:
```text
docs/experiments/
├── EXP-001-qwen-vl-hair-color.md
├── EXP-002-insightface-age-estimation.md
└── EXP-003-multi-reference-conflict-resolution.md
```

## 2. Experiment Data & Artifacts

Location: data/experiments/

- **Purpose**: Local experiment outputs, intermediate results, generated artifacts.
- **Version control**: Gitignored. Artifacts here are ephemeral and reproducible.

```text
data/experiments/
├── embeddings/     # Embedding vectors from perception runs
├── outputs/        # Raw model outputs
└── cache/          # Model caches, intermediate files
```

## 3. Reference Assets

Location: data/references/

- **Purpose**: Source images and media used as perception input.
- **Version control**: Gitignored. Reference images must never be committed.

## 4. Perception Model Implementations

Location: src/veyra/infrastructure/models/

- **Purpose**: Concrete PerceptionEngine implementations (e.g. Qwen-VL adapter, InsightFace adapter).
- **Contract**: Implements PerceptionEngine port from application/ports/perception.py.
- **Constraint**: ML dependencies (torch, transformers, cv2, etc.) are strictly confined to infrastructure/.

## 5. Architectural Seam Guarantees

1. No ML imports in Domain or Application: Enforced by tests/architecture/test_boundaries.py.
2. No binary image bytes in Domain entities: Reference.asset_id remains an opaque string identifier.
3. Model-neutral Configuration: Settings in core/config.py remains free of vendor-specific knobs.
4. Data Isolation: All data/ runtime directories are excluded via .gitignore.
5. Flexible Evidence: Observation.evidence: dict[str, Any] encapsulates model-specific outputs without leaking schema dependencies to the domain.
