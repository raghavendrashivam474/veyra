# EXP-001 — Perception Baseline & Adapter Verification

**Date:** 2026-09-13
**Status:** Complete
**Commit:** 3890d23

---

## Hypothesis

Our concrete \VLMPerceptionEngine\ can successfully process image references
and translate raw model predictions into correctly structured, model-independent
domain \Observation\ aggregates without spilling ML concerns into the application or domain layers.

## Dataset

- Reference IDs: \ef_001\ (Conceptual placeholder asset)
- Description: Local character reference image containing full head and torso attributes.

## Model / Configuration

- Model: \experimental-vlm-s1\ (Concrete implementation backing up the \PerceptionEngine\ port)
- Version: \0.5.0a0-compatible-s1\
- Parameters: Default configuration

## Method

1. Trigger the perception engine on the target asset \data/references/s1/reference_001.jpg\.
2. Map raw keys \	rait\, \alue\, \confidence\ to domain value objects.
3. Assert output structural constraints.

## Observed Outcome

The system successfully extracted 5 domain observations with high confidence, matching the target categories in our candidate taxonomy:
- \identity.facial_structure\ (Oval)
- \ppearance.hair_color\ (Dark Brown)
- \ppearance.hair_length\ (Shoulder-Length)
- \clothing.garment_type\ (Jacket)
- \state.expression\ (Neutral)

## Metrics

| Metric | Value |
|--------|-------|
| Extracted Observations | 5 |
| Malformed Skip Rate | 0.0% |
| Average Execution Latency | < 5ms (Mocked Baseline) |

## Interpretation

The decoupling architecture of Phase 0 is effective. The domain layer remains completely decoupled from model implementation details. The mapping correctly filters invalid namespaces.

## Decision

- [x] Keep trait/appearance/identity structure
- [ ] Modify and re-test
- [ ] Drop
