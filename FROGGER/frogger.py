"""Standalone two-phase artwork processor."""
from datetime import datetime, timezone
from io import BytesIO
import os
from pathlib import Path
import re
from uuid import uuid4

from PIL import Image


def now():
    return datetime.now(timezone.utc).isoformat()


def normalize(value):
    return " ".join(re.sub(r"[_-]+", " ", value.casefold()).split())


def source(path):
    return (not path.is_symlink() and path.is_file()
            and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
            and not normalize(path.stem).endswith((" nobg", " no bg"))
            and normalize(path.stem) not in {"nobg", "no bg"})


def entries(path):
    return sorted(path.iterdir(), key=lambda p: (p.name.casefold(), p.name))


def free_destination(path):
    candidate = path
    counter = 2
    while candidate.exists() or candidate.is_symlink():
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        counter += 1
    return candidate


def rembg_processor():
    from rembg import new_session, remove

    session = new_session("u2net")
    return lambda data: remove(data, session=session)


def move_without_overwrite(source_path, destination):
    if os.name == "nt":
        source_path.rename(destination)
        return
    destination.hardlink_to(source_path)
    try:
        source_path.unlink()
    except OSError:
        destination.unlink()
        raise


def run_frogger(root_folder, on_event=None, *, destination_folder=None, job_id=None,
                processor_factory=None, operations=("sort", "background_removal")):
    root = Path(root_folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Source folder does not exist.")
    destination_root = Path(destination_folder).resolve() if destination_folder else root
    folders = [p for p in entries(destination_root) if not p.is_symlink() and p.is_dir()
               and not getattr(p, "is_junction", lambda: False)()
               and not p.name.startswith(".") and normalize(p.name) not in {"", "no bg"}]
    if not folders:
        raise ValueError("No target color folders found.")

    report = dict(schema_version="1.0", bot_id="frogger", job_id=job_id or str(uuid4()),
                  status="running", started_at=now(), finished_at=None, root=str(root),
                  phase="sorting", progress=0, sorted=[], generated=[], skipped=[], errors=[])
    report["destination"] = str(destination_root)
    report["operations"] = list(operations)
    sorting = "sort" in operations
    removing = "background_removal" in operations
    sort_end = 50 if removing else 100
    report["phase"] = "sorting" if sorting else "background_removal"

    def emit(event):
        if on_event:
            on_event(dict(event=event, timestamp=now(), **{
                k: report[k] for k in ("bot_id", "job_id", "status", "phase", "progress")
            }))

    def error(path, exc):
        report["errors"].append(dict(file=str(path), phase=report["phase"], error=str(exc)))

    def skip(path, reason):
        report["skipped"].append(dict(file=str(path), phase=report["phase"], reason=reason))

    def match(image):
        matches = [p for p in folders if f" {normalize(p.name)} " in f" {normalize(image.stem)} "]
        return max(matches, key=lambda p: len(normalize(p.name)), default=None)

    emit("job.started")
    originals = [p for p in entries(root) if source(p)] if sorting else []
    for index, image in enumerate(originals, 1):
        try:
            target = match(image)
            if target is None:
                skip(image, "No matching color folder")
            else:
                destination = free_destination(target / image.name)
                move_without_overwrite(image, destination)
                report["sorted"].append(dict(source=image.name, destination=str(destination)))
        except Exception as exc:
            error(image, exc)
        report["progress"] = sort_end * index // len(originals)
        emit("job.progress")

    images = []
    start = 50 if sorting else 0
    if removing:
        report.update(phase="background_removal", progress=start)
        if sorting:
            emit("job.phase_changed")
        for target in folders:
            input_folder = target if sorting or root == destination_root else root / target.name
            if input_folder.is_dir() and not input_folder.is_symlink():
                try:
                    images.extend((p, target) for p in entries(input_folder) if source(p))
                except OSError as exc:
                    error(input_folder, exc)
        if not sorting:
            for image in entries(root):
                if source(image):
                    target = match(image)
                    if target is None:
                        skip(image, "No matching destination color folder")
                    else:
                        images.append((image, target))

    processor = None
    setup_error = None
    claimed = set()
    for index, (image, target) in enumerate(images, 1):
        temporary = None
        try:
            folder = next((p for p in entries(target) if p.name.casefold() == "no bg"),
                          target / "No BG")
            output = folder / f"{image.stem}_nobg.png"
            if str(output).casefold() in claimed:
                output = folder / f"{image.name}_nobg.png"
                counter = 2
                while str(output).casefold() in claimed:
                    output = folder / f"{image.name}_{counter}_nobg.png"
                    counter += 1
            claimed.add(str(output).casefold())
            if folder.is_symlink() or getattr(folder, "is_junction", lambda: False)():
                raise ValueError("No BG must be a local directory.")
            if output.is_file() and not output.is_symlink():
                skip(image, "No BG output already exists")
            else:
                if output.exists() or output.is_symlink():
                    raise FileExistsError(str(output))
                data = image.read_bytes()
                with Image.open(BytesIO(data)) as original:
                    original.load()
                if processor is None and setup_error is None:
                    try:
                        processor = (processor_factory or rembg_processor)()
                    except Exception as exc:
                        setup_error = str(exc)
                if setup_error is not None:
                    raise RuntimeError(f"Background model setup failed: {setup_error}")
                folder.mkdir(exist_ok=True)
                temporary = folder / f".{uuid4()}.tmp"
                with Image.open(BytesIO(processor(data))) as result:
                    result.convert("RGBA").save(temporary, format="PNG")
                move_without_overwrite(temporary, output)
                report["generated"].append(dict(source=str(image), output=str(output)))
        except Exception as exc:
            error(image, exc)
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError as exc:
                    error(temporary, exc)
        report["progress"] = start + (100 - start) * index // len(images)
        emit("job.progress")

    report.update(phase="finished", progress=100, finished_at=now(),
                  status="completed_with_errors" if report["errors"] else "completed")
    emit("job.finished")
    return report
