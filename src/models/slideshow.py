# src/models/slideshow.py
from dataclasses import dataclass
from src.models.slide import Slide


@dataclass
class Slideshow:
    slides: list[Slide]

    def __len__(self) -> int:
        return len(self.slides)
