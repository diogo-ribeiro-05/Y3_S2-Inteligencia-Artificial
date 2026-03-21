# tests/test_solver/test_scorer.py
from src.models.photo import Photo
from src.models.slide import Slide
from src.solver.scorer import calculate_transition_score


def test_transition_score_common_only():
    # Both slides share tags, nothing unique
    s1 = Slide([Photo(0, 'H', {'a', 'b'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b'})])
    # common=2, only_s1=0, only_s2=0 -> min=0
    assert calculate_transition_score(s1, s2) == 0


def test_transition_score_balanced():
    # Balanced transition: equal common, s1-only, s2-only
    s1 = Slide([Photo(0, 'H', {'a', 'b', 'c'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b', 'd'})])
    # common={a,b}=2, only_s1={c}=1, only_s2={d}=1 -> min=1
    assert calculate_transition_score(s1, s2) == 1


def test_transition_score_different_tags():
    # Completely different tags
    s1 = Slide([Photo(0, 'H', {'cat', 'dog'})])
    s2 = Slide([Photo(1, 'H', {'sun', 'moon'})])
    # common=0, only_s1=2, only_s2=2 -> min=0
    assert calculate_transition_score(s1, s2) == 0


def test_transition_score_example_from_problem():
    # From the problem statement example
    s1 = Slide([Photo(3, 'H', {'garden', 'cat'})])
    s2 = Slide([
        Photo(1, 'V', {'selfie', 'smile'}),
        Photo(2, 'V', {'garden', 'selfie'})
    ])
    # s1 tags: {garden, cat}
    # s2 tags: {selfie, smile, garden}
    # common={garden}=1, only_s1={cat}=1, only_s2={selfie,smile}=2 -> min=1
    assert calculate_transition_score(s1, s2) == 1
