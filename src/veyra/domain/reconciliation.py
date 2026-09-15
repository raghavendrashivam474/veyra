"""Veyra domain Observation Reconciliation models and strategies.

Reconciliation resolves multiple (potentially conflicting or agreeing)
observations for the same trait into a coherent trait-level state,
without destroying observation provenance.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from veyra.domain.observations import Observation
from veyra.domain.traits import Confidence, TraitName, TraitValue


@dataclass(frozen=True, slots=True)
class ReconciledTrait:
    """The reconciled outcome of one or more observations for a single trait.

    Attributes:
        trait: The trait that was reconciled.
        selected_value: The chosen trait value resulting from reconciliation.
        confidence: Reconciled confidence score in range [0.0, 1.0].
        supporting_observations: Observations agreeing with selected_value.
        conflicting_observations: Observations offering an alternative value.
    """

    trait: TraitName
    selected_value: TraitValue
    confidence: Confidence
    supporting_observations: tuple[Observation, ...]
    conflicting_observations: tuple[Observation, ...]

    def __post_init__(self) -> None:
        if not self.supporting_observations:
            raise ValueError("ReconciledTrait must have at least one supporting observation.")

        for obs in self.supporting_observations:
            if obs.trait != self.trait:
                raise ValueError(
                    f"Supporting observation trait '{obs.trait}' does not match '{self.trait}'."
                )
            if obs.value != self.selected_value:
                raise ValueError(
                    f"Supporting observation value '{obs.value}' does not match "
                    f"selected value '{self.selected_value}'."
                )

        for obs in self.conflicting_observations:
            if obs.trait != self.trait:
                raise ValueError(
                    f"Conflicting observation trait '{obs.trait}' does not match '{self.trait}'."
                )
            if obs.value == self.selected_value:
                raise ValueError(
                    f"Conflicting observation has value '{obs.value}' identical to "
                    f"selected value '{self.selected_value}'."
                )

    @property
    def total_observations(self) -> int:
        """Total count of all observations considered."""
        return len(self.supporting_observations) + len(self.conflicting_observations)

    @property
    def has_conflict(self) -> bool:
        """True if there is any conflicting observation."""
        return len(self.conflicting_observations) > 0

    @property
    def agreement_ratio(self) -> float:
        """Proportion of observations that agree with the selected value (0.0 to 1.0)."""
        total = self.total_observations
        if total == 0:
            return 0.0
        return len(self.supporting_observations) / total


class TraitReconciliationStrategy(Protocol):
    """Protocol for trait-level observation reconciliation algorithms."""

    def reconcile(self, trait: TraitName, observations: Sequence[Observation]) -> ReconciledTrait:
        """Reconcile multiple observations for a given trait into a ReconciledTrait."""
        ...


class HighestConfidenceStrategy:
    """Reconciliation strategy: highest individual confidence observation wins.

    Deterministic tie-breaking:
    1. Highest confidence (descending)
    2. Alphabetical trait value string (ascending)
    3. Alphabetical observation ID (ascending)
    """

    def reconcile(self, trait: TraitName, observations: Sequence[Observation]) -> ReconciledTrait:
        if not observations:
            raise ValueError(f"Cannot reconcile empty observations for trait '{trait}'.")

        for obs in observations:
            if obs.trait != trait:
                raise ValueError(
                    f"Observation trait '{obs.trait}' does not match target trait '{trait}'."
                )

        # Deterministic sorting key
        sorted_obs = sorted(
            observations,
            key=lambda o: (-o.confidence.score, str(o.value.raw), o.id.value),
        )

        winner = sorted_obs[0]
        selected_value = winner.value
        confidence = winner.confidence

        supporting = tuple(o for o in sorted_obs if o.value == selected_value)
        conflicting = tuple(o for o in sorted_obs if o.value != selected_value)

        return ReconciledTrait(
            trait=trait,
            selected_value=selected_value,
            confidence=confidence,
            supporting_observations=supporting,
            conflicting_observations=conflicting,
        )


class ConfidenceWeightedStrategy:
    """Default S2.1 Baseline Strategy: Confidence-weighted voting across values.

    Calculates total confidence support for each distinct value.
    Confidence of the winner is calculated as:
        net_confidence = (support_winner - support_conflicts) / total_support
    bounded in [0.0, 1.0], or winner's max confidence when no conflict.

    Deterministic tie-breaking:
    1. Highest accumulated confidence weight (descending)
    2. Highest individual maximum confidence (descending)
    3. Alphabetical trait value string (ascending)
    """

    def reconcile(self, trait: TraitName, observations: Sequence[Observation]) -> ReconciledTrait:
        if not observations:
            raise ValueError(f"Cannot reconcile empty observations for trait '{trait}'.")

        for obs in observations:
            if obs.trait != trait:
                raise ValueError(
                    f"Observation trait '{obs.trait}' does not match target trait '{trait}'."
                )

        # Group observations by TraitValue
        value_groups: dict[TraitValue, list[Observation]] = defaultdict(list)
        for obs in observations:
            value_groups[obs.value].append(obs)

        # Calculate scores and deterministic sorting
        ranked_values = []
        for val, group in value_groups.items():
            total_weight = sum(o.confidence.score for o in group)
            max_conf = max(o.confidence.score for o in group)
            # Deterministic sorting key: (-total_weight, -max_conf, str(val))
            ranked_values.append((total_weight, max_conf, str(val.raw), val, group))

        ranked_values.sort(key=lambda item: (-item[0], -item[1], item[2]))

        winner_tuple = ranked_values[0]
        winner_val = winner_tuple[3]
        winner_group = winner_tuple[4]

        total_all_weight = sum(item[0] for item in ranked_values)
        winner_weight = winner_tuple[0]
        conflict_weight = total_all_weight - winner_weight

        if total_all_weight <= 0:
            calc_conf = 0.0
        elif conflict_weight == 0:
            # Full agreement: use the highest observed confidence among agreeing observations
            calc_conf = winner_tuple[1]
        else:
            # Conflict penalty: scaled by proportion of support
            penalty = 0.5 * conflict_weight
            calc_conf = max(0.0, min(1.0, (winner_weight - penalty) / total_all_weight))

        # Sort supporting and conflicting observations deterministically
        supporting = tuple(sorted(winner_group, key=lambda o: (-o.confidence.score, o.id.value)))
        conflicting_list = []
        for item in ranked_values[1:]:
            conflicting_list.extend(item[4])
        conflicting = tuple(
            sorted(conflicting_list, key=lambda o: (-o.confidence.score, o.id.value))
        )

        return ReconciledTrait(
            trait=trait,
            selected_value=winner_val,
            confidence=Confidence(round(calc_conf, 4)),
            supporting_observations=supporting,
            conflicting_observations=conflicting,
        )
