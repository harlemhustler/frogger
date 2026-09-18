from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from PIL import Image

remove = None
try:
    from rembg import remove as rembg_remove
    remove = rembg_remove
except Exception:  # pragma: no cover - optional dependency
    remove = None

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
COLOR_WORDS = [
    "black", "white", "navy", "navy blue", "blue", "brown", "burnt brown", "red",
    "pink", "purple", "lavender", "silver", "grey", "gray", "green", "moss", "olive",
    "teal", "orange", "gold", "yellow", "beige", "cream", "tan", "maroon", "cyan",
    "magenta", "indigo", "aqua", "rose", "mustard", "coral"
]


def clean_name(value: str) -> str:
    value = value.strip()
    value = value.replace("_", " ")
    value = re.sub(r"\s+", " ", value)
    return value


def infer_variant_label(filename: str, fallback: str = "Unknown") -> str:
    """Infer the variant label from a file name.

    Examples:
      - 'Navy Blue Hoodie.png' -> 'Navy Blue'
      - 'Black - 04 shirt.png' -> 'Black'
      - 'Variant_07.png' -> '07'
    """
    name = Path(filename).stem
    cleaned = clean_name(name)
    text = cleaned.lower()

    # Prefer explicit color phrase match.
    for color in sorted(COLOR_WORDS, key=len, reverse=True):
        if color in text:
            match = re.search(re.escape(color), text)
            if match:
                start = match.start()
                end = match.end()
                candidate = cleaned[start:end]
                return candidate.strip()

    # Prefer a number from the title when there is no color match.
    number_match = re.search(r"\b(\d{1,4})\b", cleaned)
    if number_match:
        return number_match.group(1)

    # Otherwise use the packed title front piece before common separators.
    for separator in ["-", "_", "(", "]", "["]:
        if separator in cleaned:
            prefix = cleaned.split(separator, 1)[0].strip()
            if prefix:
                return prefix

    return fallback if not cleaned else cleaned


def build_output_name(filename: str, suffix: str = "") -> str:
    path = Path(filename)
    if not suffix:
        return path.name
    stem = path.stem
    return f"{stem}_{suffix}{path.suffix}"


def remove_background_from_image(image_path: Path, tolerance: int = 245) -> Path:
    """Create a transparent-background copy using a simple white-background removal heuristic.

    For simple mockup folders and product art, near-white background pixels become transparent.
    If rembg is installed, it prefers that more robust pipeline.
    """
    original = Image.open(image_path).convert("RGBA")
    width, height = original.size
    pixels = original.load()

    if remove is not None:
        try:
            result = remove(original)
            if result is not None:
                output_path = image_path.with_name(build_output_name(image_path.name, "nobg"))
                result.save(output_path)
                return output_path
        except Exception:
            pass

    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r >= tolerance and g >= tolerance and b >= tolerance:
                new_img.putpixel((x, y), (255, 255, 255, 0))
            else:
                new_img.putpixel((x, y), (r, g, b, a))

    output_path = image_path.with_name(build_output_name(image_path.name, "nobg"))
    new_img.save(output_path)
    return output_path


def process_variant_folder(
    source_dir: str | Path,
    destination_root: str | Path,
    move_suffix: str = "",
    no_bg_suffix: str = "nobg",
    variant_label_field: str = "title",
    background_tolerance: int = 245,
) -> Dict[str, List[str]]:
    """Move image files into color/variant folders and generate no-background variants.

    Example:
      process_variant_folder(
          source_dir='C:/images/variants',
          destination_root='C:/images/organized',
          move_suffix='',
          no_bg_suffix='nobg',
      )
    """
    source_dir = Path(source_dir)
    destination_root = Path(destination_root)

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    moved_files: List[str] = []
    no_bg_files: List[str] = []

    for file_path in sorted(source_dir.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        label = infer_variant_label(file_path.name)
        if variant_label_field.lower() == "number":
            number_match = re.search(r"\b(\d{1,4})\b", file_path.stem)
            label = number_match.group(1) if number_match else label

        destination_folder = destination_root / label
        destination_folder.mkdir(parents=True, exist_ok=True)

        moved_name = build_output_name(file_path.name, move_suffix)
        final_path = destination_folder / moved_name
        shutil.move(str(file_path), str(final_path))
        moved_files.append(str(final_path))

        no_bg_name = build_output_name(final_path.name, no_bg_suffix)
        no_bg_path = final_path.with_name(no_bg_name)

        out = remove_background_from_image(final_path, tolerance=background_tolerance)
        if out.exists():
            no_bg_path = out
            no_bg_files.append(str(no_bg_path))

    return {"moved_files": moved_files, "no_bg_files": no_bg_files}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frogger: sort variants into folders and generate no-background versions.")
    parser.add_argument("--source", required=True, help="Directory containing the original variant images.")
    parser.add_argument("--destination", required=True, help="Root destination to organize variant folders.")
    parser.add_argument("--move-suffix", default="", help="Suffix to append to the moved original files, e.g. 'base' or '' for none.")
    parser.add_argument("--no-bg-suffix", default="nobg", help="Suffix to append to generated no-background copies.")
    parser.add_argument("--variant-label-field", default="title", choices=["title", "number"], help="How labels should be inferred from filenames.")
    parser.add_argument("--background-tolerance", type=int, default=245, help="White/near-white threshold used when removing backgrounds.")
    args = parser.parse_args()

    results = process_variant_folder(
        source_dir=args.source,
        destination_root=args.destination,
        move_suffix=args.move_suffix,
        no_bg_suffix=args.no_bg_suffix,
        variant_label_field=args.variant_label_field,
        background_tolerance=args.background_tolerance,
    )

    print(f"Moved {len(results['moved_files'])} files.")
    print(f"Created {len(results['no_bg_files'])} no-background variants.")
    for path in results["moved_files"]:
        print(f"- {path}")
