# src/models/slide.py
from dataclasses import dataclass
from src.models.photo import Photo


@dataclass
class Slide:
    photos: list[Photo]

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.photos) == 0:
            raise ValueError("Slide must contain at least one photo")

        if len(self.photos) == 1:
            if self.photos[0].is_vertical:
                raise ValueError("Vertical photos must be paired (2 per slide)")
            return

        if len(self.photos) == 2:
            if self.photos[0].is_horizontal and self.photos[1].is_horizontal:
                raise ValueError("Cannot combine two horizontal photos in one slide")
            if self.photos[0].is_horizontal or self.photos[1].is_horizontal:
                raise ValueError("Cannot mix horizontal and vertical photos in one slide")
            return

        raise ValueError("Slide cannot contain more than 2 photos")

    @property
    def tags(self) -> set[str]:
        result = set()
        for photo in self.photos:
            result.update(photo.tags)
        return result

    @property
    def is_horizontal_slide(self) -> bool:
        return len(self.photos) == 1 and self.photos[0].is_horizontal

    @property
    def is_vertical_slide(self) -> bool:
        return len(self.photos) == 2

    @property
    def photo_ids(self) -> list[int]:
        return [p.id for p in self.photos]
