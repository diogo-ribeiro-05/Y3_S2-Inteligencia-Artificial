# src/solver/scorer.py
from src.models.slide import Slide


def calculate_transition_score(s1: Slide, s2: Slide) -> int:
    """
    Calculate interest factor between two consecutive slides.
    Interest factor = min(common_tags, tags_only_in_s1, tags_only_in_s2)
    """
    tags1 = s1.tags
    tags2 = s2.tags

    common = len(tags1 & tags2)
    only_s1 = len(tags1 - tags2)
    only_s2 = len(tags2 - tags1)

    return min(common, only_s1, only_s2)
