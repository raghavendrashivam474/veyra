# S1 — Perception Problem Definition

**Sprint:** S1
**Status:** Active
**Created:** 2026-09-13

---

## Research Objective

Determine what visual information Veyra can reliably extract from a
reference image and which of that information is useful for representing
persistent character identity.

## Candidate Perception Categories

The following are **candidate categories** to be evaluated, not final
ontology commitments.

| Category       | Candidate Traits (examples)                              |
| -------------- | -------------------------------------------------------- |
| identity       | facial_structure, eye_structure, nose_structure          |
| appearance     | hair_color, hair_length, hair_texture, skin_appearance   |
| body           | body_build, apparent_height, proportions                 |
| clothing       | garment_type, dominant_colors, accessories               |
| style          | rendering_style, visual_aesthetic                        |
| state          | pose, expression                                         |

## Stable vs Variable — Initial Hypotheses

**Hypothesized stable (identity-relevant):**
- Facial structure / proportions
- Eye shape and structure
- Hair structure (not color, which can change)
- Body proportions

**Hypothesized variable (context-dependent):**
- Pose
- Expression
- Clothing
- Lighting
- Background

**To be evaluated:** Whether these hypotheses hold under real perception.

## Expected Observation Format

Each perception run should produce Observation[] where each observation
contains:

- 	rait — candidate trait name (e.g. ppearance.hair_color)
- alue — perceived value (e.g. "dark brown")
- confidence — model-reported confidence (interpretation TBD)
- source — model identifier
- evidence — structured metadata about the perception

## Initial Evaluation Questions

1. Can the model produce structured trait/value pairs at all?
2. Are confidence scores meaningful or arbitrary?
3. Does the same image produce consistent observations across runs?
4. Which traits are perceived accurately vs. hallucinated?
5. Which observations are useful for identity vs. merely descriptive?

## Known Unknowns

- Whether VLM structured output is reliable enough for trait extraction
- Whether specialized CV models outperform general VLMs for face/body
- How confidence calibration varies across trait categories
- Whether perception quality degrades with stylized/illustrated characters
- What hardware constraints limit local model selection

## Explicit Non-Goals

- Finalizing the Character Genome (S2)
- Implementing image generation (S3+)
- Building identity verification metrics (S4+)
- Freezing the trait ontology
- Adding enterprise infrastructure
