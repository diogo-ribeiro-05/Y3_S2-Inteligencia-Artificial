# src/io/parser.py
from src.models.photo import Photo


def parse_input(content: str) -> list[Photo]:
    """Parse input file content into Photo objects."""
    lines = content.strip().split('\n')

    if not lines:
        raise ValueError("Empty input")

    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError("First line must be number of photos")

    photos = []
    for i, line in enumerate(lines[1:n+1]):
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid photo format on line {i+1}")

        orientation = parts[0]
        tag_count = int(parts[1])
        tags = set(parts[2:2+tag_count])

        photos.append(Photo(id=i, orientation=orientation, tags=tags))

    return photos


def write_output(slideshow, filepath: str) -> None:
    """Write slideshow to output file."""
    with open(filepath, 'w') as f:
        f.write(slideshow.to_output_string())
