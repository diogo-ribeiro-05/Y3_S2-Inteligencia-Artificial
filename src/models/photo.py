# src/models/photo.py
from dataclasses import dataclass


@dataclass
class Photo:
    id: int
    orientation: str
    tags: set[str]

    @property
    def is_horizontal(self) -> bool:
        return self.orientation == 'H'

    @property
    def is_vertical(self) -> bool:
        return self.orientation == 'V'

    @property
    def tag_count(self) -> int:
        return len(self.tags)
