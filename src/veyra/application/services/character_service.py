"""Character application service.

Coordinates character-related operations, decoupling domain creation
from persistence mechanics.
"""

from veyra.application.ports.repositories import CharacterRepository
from veyra.domain.character import Character
from veyra.domain.ids import CharacterId


class CharacterService:
    """Orchestrates workflows for Character entities."""

    def __init__(self, character_repo: CharacterRepository) -> None:
        self._character_repo = character_repo

    def create_character(self, name: str, description: str = "") -> Character:
        """Create, persist, and return a new Character."""
        character_id = CharacterId.generate()
        character = Character(
            id=character_id,
            name=name,
            description=description,
        )
        self._character_repo.save(character)
        return character

    def get_character(self, character_id: CharacterId) -> Character | None:
        """Retrieve a Character by its ID."""
        return self._character_repo.get(character_id)
