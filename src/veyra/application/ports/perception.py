"""Perception engine port for Veyra application.

Defines the contract for visual perception analysis models (e.g. VLMs).
The port expects a Reference domain object and produces Observation models.
"""

from abc import ABC, abstractmethod

from veyra.domain.observations import Observation
from veyra.domain.reference import Reference
from veyra.domain.traits import TraitName


class PerceptionEngine(ABC):
    """Port for running vision/multimodal models on references."""

    @abstractmethod
    def observe(self, reference: Reference, traits: list[TraitName]) -> list[Observation]:
        """Analyze a reference and produce observations for the requested traits."""
        pass
