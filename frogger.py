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


def duplicate_image(source_file: str | Path, destination_root: str | Path, suffix: str = "copy") -> Path:
    """Create a duplicate image copy in a secondary destination folder."""
    source_file = Path(source_file)
    destination_root = Path(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    target_folder = destination_root / source_file.parent.name
    target_folder.mkdir(parents=True, exist_ok=True)
    target_path = target_folder / build_output_name(source_file.name, suffix)
    shutil.copy2(str(source_file), str(target_path))
    return target_path


def create_thumbnail(source_file: str | Path, destination_root: str | Path, suffix: str = "thumb", max_size: int = 512) -> Path:
    """Create a thumbnail-sized copy while preserving aspect ratio."""
    source_file = Path(source_file)
    destination_root = Path(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    target_folder = destination_root / source_file.parent.name
    target_folder.mkdir(parents=True, exist_ok=True)

    with Image.open(source_file) as img:
        img = img.convert("RGBA")
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        target_path = target_folder / build_output_name(source_file.name, suffix)
        img.save(target_path)
        return target_path


def compress_image(source_file: str | Path, destination_root: str | Path, suffix: str = "compressed", quality: int = 70) -> Path:
    """Create a compressed version of the image for lighter file sizes."""
    source_file = Path(source_file)
    destination_root = Path(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)
    target_folder = destination_root / source_file.parent.name
    target_folder.mkdir(parents=True, exist_ok=True)

    with Image.open(source_file) as img:
        converted = img.convert("RGB") if img.mode in {"RGBA", "LA", "P"} else img.copy()
        target_path = target_folder / build_output_name(source_file.name, suffix)
        converted.save(target_path, quality=quality, optimize=True)
        return target_path


def resolve_destination_label(
    file_name: str,
    destination_root: str | Path,
    match_tag: str | None = None,
    variant_label_field: str = "title",
) -> str:
    """Resolve which variant folder a file belongs in.

    If a match tag is supplied, prefer the destination subfolder whose name appears in the
    file title. This supports workflows where a folder set like 'Black' or 'Navy Blue' is
    already defined and files are dumped into a source folder for processing.
    """
    destination_root = Path(destination_root)
    file_text = clean_name(Path(file_name).stem).lower()

    if match_tag:
        tag = clean_name(match_tag).lower()
        if tag:
            if tag in file_text:
                for folder in sorted(destination_root.iterdir(), key=lambda p: len(p.name), reverse=True):
                    if folder.is_dir():
                        folder_text = clean_name(folder.name).lower()
                        if folder_text in file_text:
                            return folder.name

    label = infer_variant_label(file_name)
    if variant_label_field.lower() == "number":
        number_match = re.search(r"\b(\d{1,4})\b", Path(file_name).stem)
        label = number_match.group(1) if number_match else label

    return label


def run_secondary_job(
    source_file: str | Path,
    destination_root: str | Path,
    script_name: str = "background_remover",
    suffix: str = "nobg",
    background_tolerance: int = 245,
) -> List[str]:
    """Run a secondary processing pass into a second destination folder.

    Supported scripts:
      - background_remover / remove_background / rembg
      - duplicate / copy
      - custom / other -> copies file to the destination with the chosen suffix
    """
    source_file = Path(source_file)
    destination_root = Path(destination_root)
    script_key = (script_name or "background_remover").strip().lower().replace("_", " ").replace("-", " ")

    if not destination_root.exists():
        destination_root.mkdir(parents=True, exist_ok=True)

    if "background" in script_key or "rembg" in script_key or "remove" in script_key:
        output_path = remove_background_from_image(source_file, tolerance=background_tolerance)
        if not output_path.exists():
            return []
        target_folder = destination_root / source_file.parent.name
        target_folder.mkdir(parents=True, exist_ok=True)
        target_path = target_folder / output_path.name
        shutil.copy2(str(output_path), str(target_path))
        return [str(target_path)]

    if "duplicate" in script_key or "copy" in script_key:
        target_path = duplicate_image(source_file, destination_root, suffix=suffix or "copy")
        return [str(target_path)]

    if "thumbnail" in script_key or "thumb" in script_key:
        target_path = create_thumbnail(source_file, destination_root, suffix=suffix or "thumb")
        return [str(target_path)]

    if "compress" in script_key or "quality" in script_key:
        target_path = compress_image(source_file, destination_root, suffix=suffix or "compressed")
        return [str(target_path)]

    target_path = duplicate_image(source_file, destination_root, suffix=suffix or "copy")
    return [str(target_path)]


def process_variant_folder(
    source_dir: str | Path,
    destination_root: str | Path,
    move_suffix: str = "",
    no_bg_suffix: str = "nobg",
    variant_label_field: str = "title",
    background_tolerance: int = 245,
    match_tag: str | None = None,
    secondary_destination_root: str | Path | None = None,
    secondary_script: str = "background_remover",
    secondary_suffix: str | None = None,
) -> Dict[str, List[str]]:
    """Move image files into folder matches and optionally run a second custom job.

    Example:
      process_variant_folder(
          source_dir='C:/images/variants',
          destination_root='C:/images/organized',
          match_tag='Navy Blue',
          secondary_destination_root='C:/images/secondary',
          secondary_script='background_remover',
          secondary_suffix='nobg',
      )
    """
    source_dir = Path(source_dir)
    destination_root = Path(destination_root)

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    destination_root.mkdir(parents=True, exist_ok=True)
    if secondary_destination_root is not None:
        secondary_destination_root = Path(secondary_destination_root)
        secondary_destination_root.mkdir(parents=True, exist_ok=True)

    moved_files: List[str] = []
    no_bg_files: List[str] = []
    matched_folders: List[str] = []
    secondary_outputs: List[str] = []

    for file_path in sorted(source_dir.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        label = resolve_destination_label(file_path.name, destination_root, match_tag=match_tag, variant_label_field=variant_label_field)

        destination_folder = destination_root / label
        destination_folder.mkdir(parents=True, exist_ok=True)
        matched_folders.append(str(destination_folder))

        moved_name = build_output_name(file_path.name, move_suffix)
        final_path = destination_folder / moved_name
        shutil.move(str(file_path), str(final_path))
        moved_files.append(str(final_path))

        if no_bg_suffix:
            no_bg_name = build_output_name(final_path.name, no_bg_suffix)
            no_bg_path = final_path.with_name(no_bg_name)
            out = remove_background_from_image(final_path, tolerance=background_tolerance)
            if out.exists():
                no_bg_path = out
                no_bg_files.append(str(no_bg_path))

        if secondary_destination_root is not None:
            job_suffix = secondary_suffix if secondary_suffix else no_bg_suffix
            job_outputs = run_secondary_job(
                source_file=final_path,
                destination_root=secondary_destination_root,
                script_name=secondary_script,
                suffix=job_suffix,
                background_tolerance=background_tolerance,
            )
            secondary_outputs.extend(job_outputs)

    return {
        "moved_files": moved_files,
        "no_bg_files": no_bg_files,
        "matched_folders": matched_folders,
        "secondary_outputs": secondary_outputs,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frogger: sort variants into folders and generate no-background versions.")
    parser.add_argument("--source", required=True, help="Directory containing the original variant images.")
    parser.add_argument("--destination", required=True, help="Root destination to organize variant folders.")
    parser.add_argument("--move-suffix", default="", help="Suffix to append to the moved original files, e.g. 'base' or '' for none.")
    parser.add_argument("--no-bg-suffix", default="nobg", help="Suffix to append to generated no-background copies.")
    parser.add_argument("--variant-label-field", default="title", choices=["title", "number"], help="How labels should be inferred from filenames.")
    parser.add_argument("--background-tolerance", type=int, default=245, help="White/near-white threshold used when removing backgrounds.")
    parser.add_argument("--match-tag", default=None, help="Title phrase used to match an existing destination subfolder, e.g. 'Navy Blue'.")
    parser.add_argument("--secondary-destination", default=None, help="Optional second destination folder for a custom follow-up job.")
    parser.add_argument("--secondary-script", default="background_remover", help="Optional second-job script type, e.g. background_remover, duplicate, copy.")
    parser.add_argument("--secondary-suffix", default=None, help="Suffix to use for output titles in the second job.")
    args = parser.parse_args()

    results = process_variant_folder(
        source_dir=args.source,
        destination_root=args.destination,
        move_suffix=args.move_suffix,
        no_bg_suffix=args.no_bg_suffix,
        variant_label_field=args.variant_label_field,
        background_tolerance=args.background_tolerance,
        match_tag=args.match_tag,
        secondary_destination_root=args.secondary_destination,
        secondary_script=args.secondary_script,
        secondary_suffix=args.secondary_suffix,
    )

    print(f"Moved {len(results['moved_files'])} files.")
    print(f"Created {len(results['no_bg_files'])} no-background variants.")
    if results.get("secondary_outputs"):
        print(f"Secondary job created {len(results['secondary_outputs'])} outputs.")
    for path in results["moved_files"]:
        print(f"- {path}")
