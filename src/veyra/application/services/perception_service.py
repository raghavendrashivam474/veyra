"""Perception application service.

Orchestrates the analysis of source materials (References) using
the perception engine port, and persists the resulting Observations.
"""

from veyra.application.ports.perception import PerceptionEngine
from veyra.application.ports.repositories import ObservationRepository
from veyra.domain.observations import Observation
from veyra.domain.reference import Reference
from veyra.domain.traits import TraitName


class PerceptionService:
    """Orchestrates perception workflows."""

    def __init__(
        self,
        perception_engine: PerceptionEngine,
        observation_repo: ObservationRepository,
    ) -> None:
        self._perception_engine = perception_engine
        self._observation_repo = observation_repo

    def perceive(self, reference: Reference, traits: list[TraitName]) -> list[Observation]:
        """Examine a Reference for specific traits, persist, and return Observations."""
        observations = self._perception_engine.observe(reference, traits)
        for observation in observations:
            self._observation_repo.save(observation)
        return observations
