# src/models/slideshow.py
from dataclasses import dataclass
from src.models.slide import Slide
from src.solver.scorer import calculate_transition_score


@dataclass
class Slideshow:
    slides: list[Slide]

    def __len__(self) -> int:
        return len(self.slides)

    def calculate_score(self) -> int:
        """Calculate total score as sum of all transition scores."""
        if len(self.slides) < 2:
            return 0

        total = 0
        for i in range(len(self.slides) - 1):
            total += calculate_transition_score(self.slides[i], self.slides[i + 1])
        return total

    def to_output_string(self) -> str:
        """Generate output string for submission file format."""
        lines = [str(len(self.slides))]
        for slide in self.slides:
            lines.append(' '.join(str(pid) for pid in slide.photo_ids))
        return '\n'.join(lines) + '\n'
