"""Representation application service.

Aggregates observations to construct, update, and reconcile CharacterRepresentation aggregates.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from veyra.domain.ids import CharacterId
from veyra.domain.observations import Observation
from veyra.domain.reconciliation import (
    ConfidenceWeightedStrategy,
    ReconciledTrait,
    TraitReconciliationStrategy,
)
from veyra.domain.representation import CharacterRepresentation
from veyra.domain.traits import TraitName


class RepresentationService:
    """Orchestrates CharacterRepresentation updates and trait reconciliation."""

    def __init__(
        self,
        default_strategy: TraitReconciliationStrategy | None = None,
    ) -> None:
        self._default_strategy = default_strategy or ConfidenceWeightedStrategy()

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

        # Group observations by TraitName
        grouped: dict[TraitName, list[Observation]] = defaultdict(list)
        for obs in observations:
            grouped[obs.trait].append(obs)

        # Reconcile each trait group deterministically
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
