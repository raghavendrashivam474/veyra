# S1 Perception Readiness Checklist

> Gate document for entering S1 Perception.
> Created during S0.5 Phase-0 Architecture Review.
> All items must be checked before S1 work begins.

---

## Architecture

- [x] Domain boundary stable — entities, value objects, and invariants frozen at v0.3.0a0
- [x] Application boundary stable — services and ports frozen at v0.4.0a0
- [x] Infrastructure boundary stable — local-first adapters in place
- [x] PerceptionEngine port exists at `application/ports/perception.py`
- [x] Architecture boundary tests pass (`tests/architecture/test_boundaries.py`)
- [x] Dependency direction verified: domain <-- application <-- api, infrastructure --> domain

## Engineering

- [x] All 53 tests passing
- [x] Ruff lint clean
- [x] Ruff format clean
- [x] CI configuration valid (`.pre-commit-config.yaml`, GitHub Actions)
- [x] Import sorting enforced (I001 rule active)

## Data

- [x] Reference asset handling understood — `Reference.asset_id` is opaque handle, `LocalAssetStore` manages bytes
- [x] Local data excluded from Git — `.gitignore` covers all `data/` subdirectories
- [x] Experiment artifact location defined — `data/experiments/` (gitignored)
- [x] Reference image location defined — `data/references/` (gitignored)
- [x] ML model artifacts excluded — `.gitignore` covers `*.pt`, `*.safetensors`, `huggingface/`, `torch_cache/`

## Research

- [x] Perception experiment documentation location defined — `docs/experiments/`
- [x] Model provider can remain behind PerceptionEngine port — no ML imports in app/domain
- [x] Observations can enter the domain — `Observation` model supports trait, value, confidence, source, evidence
- [x] Experiment results can be documented — `docs/experiments/` with naming convention
- [x] Observation evidence field is extensible — `dict[str, Any]` accepts arbitrary model output
- [x] Configuration is model-neutral — `Settings` has no vendor-specific fields

## Scope (Negative Checklist — Things NOT Prematurely Decided)

- [x] No Character Genome prematurely frozen — `CharacterRepresentation` is a container, not a schema
- [x] No identity metric prematurely frozen — no similarity/distance functions in domain
- [x] No VLM vendor hard-coded into domain/application — `PerceptionEngine` is abstract
- [x] No generation architecture prematurely introduced — no FLUX/SD/IP-Adapter references
- [x] No embedding ontology frozen — `infrastructure/embeddings/` is a placeholder
- [x] No trait ontology expansion beyond S0.3 — `TraitName` namespace format is the only constraint

## S1 Entry Flow

When S1 begins, the expected perception flow is already architecturally supported:

```text
Reference Image (data/references/)
      │
      ▼
LocalAssetStore.save_bytes() --> asset_id
      │
      ▼
Reference(asset_id=..., source_type=IMAGE_FILE)
      │
      ▼
PerceptionService.perceive(reference, traits)
      │
      ▼
PerceptionEngine.observe(reference, traits)  <-- S1 implements this
      │
      ▼
Real VLM implementation (infrastructure/models/)
      │
      ▼
Observation[] (with evidence dict for rich output)
      │
      ▼
ObservationRepository.save() --> persistence
      │
      ▼
CharacterRepresentation.add_observation()
```

The exact VLM, trait ontology, and perception schema remain S1 research decisions.
