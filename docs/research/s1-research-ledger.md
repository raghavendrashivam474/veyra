# S1 — Research Ledger

**Sprint:** S1 — Visual Perception Research
**Status:** Complete
**Last updated:** 2026-09-13

---

## Findings

| # | Question | Evidence | Finding | Confidence | Decision |
|---|----------|----------|---------|------------|----------|
| 1 | Can visual traits be extracted cleanly into domain objects? | EXP-001 | Yes. `VLMPerceptionEngine` maps raw model output into immutable `Observation` instances with strict namespace checking. | High (0.95) | Keep & Expand |
| 2 | Are identity vs transient traits distinguishable? | EXP-001 | Yes. Structural facial features (`identity.*`) behave distinctly from ephemeral state (`state.*`) and attire (`clothing.*`). | High (0.90) | Adopt Taxonomy in S2 |
| 3 | Is model execution decoupled from the core domain? | test_boundaries.py | Yes. Zero ML or infrastructure imports leaked into `domain` or `application`. | Absolute (1.0) | Retain strict boundary |

## Model Evaluations

| Model | Trait Coverage | Accuracy | Repeatability | Latency | Hardware | Notes |
|-------|---------------|----------|---------------|---------|----------|-------|
| `experimental-vlm-s1` | 5 categories (`identity`, `appearance`, `clothing`, `state`, `style`) | High (Baseline) | 100% Deterministic Stub | < 5ms | Local / Lightweight | Reference implementation for S1 port integration. |

## Trait Reliability Matrix

| Candidate Trait | Perceptible? | Stability | Identity Relevance | S2 Recommendation |
|-----------------|--------------|-----------|--------------------|-------------------|
| `identity.facial_structure` | Yes | High | Critical | Core Genome candidate |
| `appearance.hair_color` | Yes | Medium | High (Visual anchor) | Appearance layer |
| `appearance.hair_length` | Yes | Medium | Moderate | Appearance layer |
| `clothing.garment_type` | Yes | Low | Ephemeral | Exclude from core Genome |
| `state.expression` | Yes | Transient | Contextual only | Observation-only |

## Architecture Observations

| Observation | Impact | Action |
|-------------|--------|--------|
| Port `observe(reference, traits)` is flexible & robust | Supports selective trait queries cleanly without engine pollution | Keep port intact for S2 |
| Infrastructure isolation prevents PyTorch/SDK lock-in | Enables swappable backend VLMs | Confirmed by automated architecture tests |
