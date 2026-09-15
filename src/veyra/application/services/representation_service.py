"""Representation application service.

Aggregates observations to construct, update, reconcile, assess,
and classify CharacterRepresentation aggregates.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from veyra.domain.evidence import (
    BaselineEvidenceAggregator,
    EvidenceAggregationStrategy,
    TraitAssessment,
)
from veyra.domain.ids import CharacterId
from veyra.domain.observations import Observation
from veyra.domain.persistence import (
    BaselinePersistenceClassifier,
    ClassifiedTraitAssessment,
    PersistenceClassifier,
)
from veyra.domain.reconciliation import (
    ConfidenceWeightedStrategy,
    ReconciledTrait,
    TraitReconciliationStrategy,
)
from veyra.domain.representation import CharacterRepresentation
from veyra.domain.traits import TraitName


class RepresentationService:
    """Orchestrates CharacterRepresentation updates, reconciliation, and assessment."""

    def __init__(
        self,
        default_strategy: TraitReconciliationStrategy | None = None,
        default_aggregator: EvidenceAggregationStrategy | None = None,
        default_classifier: PersistenceClassifier | None = None,
    ) -> None:
        self._default_strategy = default_strategy or ConfidenceWeightedStrategy()
        self._default_aggregator = default_aggregator or BaselineEvidenceAggregator()
        self._default_classifier = default_classifier or BaselinePersistenceClassifier()

    def create_representation(
        self, character_id: CharacterId, observations: list[Observation]
    ) -> CharacterRepresentation:
        """Construct a CharacterRepresentation from a list of Observations."""
        representation = CharacterRepresentation(character_id=character_id)
        for observation in observations:
            representation.add_observation(observation)
        return representation

    def reconcile_observations(
        self,
        observations: Sequence[Observation],
        strategy: TraitReconciliationStrategy | None = None,
    ) -> dict[TraitName, ReconciledTrait]:
        """Group observations by trait and reconcile each group into a ReconciledTrait.

        Returns:
            Dictionary mapping each TraitName to its ReconciledTrait.
        """
        if not observations:
            return {}

        active_strategy = strategy or self._default_strategy

        grouped: dict[TraitName, list[Observation]] = defaultdict(list)
        for obs in observations:
            grouped[obs.trait].append(obs)

        reconciled: dict[TraitName, ReconciledTrait] = {}
        for trait, trait_obs in sorted(grouped.items(), key=lambda item: item[0].value):
            reconciled[trait] = active_strategy.reconcile(trait, trait_obs)

        return reconciled

    def reconcile_traits(
        self,
        representation: CharacterRepresentation,
        strategy: TraitReconciliationStrategy | None = None,
    ) -> dict[TraitName, ReconciledTrait]:
        """Reconcile all observations within a CharacterRepresentation aggregate."""
        return self.reconcile_observations(representation.observations, strategy=strategy)

    def assess_observations(
        self,
        observations: Sequence[Observation],
        reconciliation_strategy: TraitReconciliationStrategy | None = None,
        aggregation_strategy: EvidenceAggregationStrategy | None = None,
    ) -> dict[TraitName, TraitAssessment]:
        """Reconcile observations and aggregate structured evidence into TraitAssessments.

        Returns:
            Dictionary mapping TraitName to explainable TraitAssessment.
        """
        if not observations:
            return {}

        reconciled_map = self.reconcile_observations(observations, strategy=reconciliation_strategy)
        aggregator = aggregation_strategy or self._default_aggregator

        assessments: dict[TraitName, TraitAssessment] = {}
        for trait, reconciled in reconciled_map.items():
            assessments[trait] = aggregator.assess(reconciled)

        return assessments

    def assess_traits(
        self,
        representation: CharacterRepresentation,
        reconciliation_strategy: TraitReconciliationStrategy | None = None,
        aggregation_strategy: EvidenceAggregationStrategy | None = None,
    ) -> dict[TraitName, TraitAssessment]:
        """Assess all traits within a CharacterRepresentation aggregate with explainability."""
        return self.assess_observations(
            representation.observations,
            reconciliation_strategy=reconciliation_strategy,
            aggregation_strategy=aggregation_strategy,
        )

    def classify_observations(
        self,
        observations: Sequence[Observation],
        reconciliation_strategy: TraitReconciliationStrategy | None = None,
        aggregation_strategy: EvidenceAggregationStrategy | None = None,
        classifier: PersistenceClassifier | None = None,
    ) -> dict[TraitName, ClassifiedTraitAssessment]:
        """Reconcile, assess, and classify observations into persistence categories.

        Returns:
            Dictionary mapping TraitName to ClassifiedTraitAssessment.
        """
        if not observations:
            return {}

        assessments = self.assess_observations(
            observations,
            reconciliation_strategy=reconciliation_strategy,
            aggregation_strategy=aggregation_strategy,
        )
        active_classifier = classifier or self._default_classifier

        classified: dict[TraitName, ClassifiedTraitAssessment] = {}
        for trait, assessment in assessments.items():
            classified[trait] = active_classifier.classify(assessment)

        return classified

    def classify_traits(
        self,
        representation: CharacterRepresentation,
        reconciliation_strategy: TraitReconciliationStrategy | None = None,
        aggregation_strategy: EvidenceAggregationStrategy | None = None,
        classifier: PersistenceClassifier | None = None,
    ) -> dict[TraitName, ClassifiedTraitAssessment]:
        """Classify all traits within a CharacterRepresentation aggregate by persistence."""
        return self.classify_observations(
            representation.observations,
            reconciliation_strategy=reconciliation_strategy,
            aggregation_strategy=aggregation_strategy,
            classifier=classifier,
        )
