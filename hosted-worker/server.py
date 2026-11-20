"""Bounded hosted sorting adapter. Files only exist in a per-request workspace."""
import base64
from binascii import Error as Base64Error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from threading import Lock
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "FROGGER"))
from frogger import run_frogger

MAX_BYTES = 8 * 1024 * 1024
MAX_BODY = 12 * 1024 * 1024
LOCK = Lock()


def safe_name(name, limit=160):
    if (not isinstance(name, str) or not 1 <= len(name) <= limit
            or name in {".", ".."} or name.startswith(".")
            or re.search(r'[\x00-\x1f/\\:]', name)):
        raise ValueError("Use simple file and folder names without path separators.")
    return name


def run_sort(payload):
    if not isinstance(payload, dict) or payload.get("operation") != "sort":
        raise ValueError("This hosted worker supports Sort.")
    files = payload.get("files")
    colors = payload.get("folders")
    if not isinstance(files, list) or not 1 <= len(files) <= 20:
        raise ValueError("Choose between 1 and 20 images.")
    if not isinstance(colors, list) or not 1 <= len(colors) <= 30:
        raise ValueError("Choose between 1 and 30 destination color folders.")
    colors = [safe_name(color, 80) for color in colors]
    if len({color.casefold() for color in colors}) != len(colors):
        raise ValueError("Destination folder names must be unique.")
    if any(color.casefold() in {"no bg", "unsorted"} for color in colors):
        raise ValueError("No BG and Unsorted are reserved folder names.")
    with TemporaryDirectory(prefix="frogger-job-") as workspace:
        root = Path(workspace)
        source = root / "source"
        destination = root / "output"
        source.mkdir()
        destination.mkdir()
        for color in colors:
            (destination / color).mkdir()
        total = 0
        names = set()
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("Invalid image upload.")
            name = safe_name(item.get("name"))
            if name.casefold() in names:
                raise ValueError("Source file names must be unique.")
            names.add(name.casefold())
            if Path(name).suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError("Use PNG, JPEG or WebP images.")
            try:
                data = base64.b64decode(item.get("data", ""), validate=True)
            except (Base64Error, TypeError):
                raise ValueError("Invalid image data.") from None
            total += len(data)
            if not data or total > MAX_BYTES:
                raise ValueError("The combined image size must be at most 8 MiB.")
            try:
                with Image.open(BytesIO(data)) as image:
                    if image.width * image.height > 20_000_000:
                        raise ValueError("Each image must be at most 20 megapixels.")
                    image.verify()
            except (OSError, SyntaxError):
                raise ValueError("An uploaded image could not be read.") from None
            (source / name).write_bytes(data)
        report = run_frogger(source, destination_folder=destination, operations=["sort"])
        if report["errors"]:
            raise ValueError("Sorting failed. Downloadable output was not created.")
        archive = BytesIO()
        entries = []
        with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
            for file in sorted(destination.rglob("*")):
                if file.is_file():
                    relative = file.relative_to(destination).as_posix()
                    zipped.write(file, relative)
                    entries.append(relative)
            for file in sorted(source.iterdir()):
                if file.is_file():
                    relative = "Unsorted/" + file.name
                    zipped.write(file, relative)
                    entries.append(relative)
            summary = {"sorted": len(report["sorted"]), "unsorted": len(report["skipped"]), "entries": entries}
            zipped.writestr("frogger-report.json", json.dumps(summary, indent=2))
        return {"jobId": str(uuid4()), "status": "completed", **summary,
                "archive": base64.b64encode(archive.getvalue()).decode("ascii")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.reply(200 if self.path == "/health" else 404,
                   {"status": "ready"} if self.path == "/health" else {"error": "Not found."})

    def do_POST(self):
        if self.path != "/run":
            self.reply(404, {"error": "Not found."})
            return
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_BODY:
            self.reply(413, {"error": "Upload exceeds the size limit."})
            return
        if not LOCK.acquire(blocking=False):
            self.reply(409, {"error": "Frogger is busy. Retry shortly."})
            return
        try:
            self.connection.settimeout(30)
            result = run_sort(json.loads(self.rfile.read(length)))
            self.reply(200, result)
        except (ValueError, TypeError, Image.DecompressionBombError):
            self.reply(400, {"error": "Invalid upload. Use up to 20 images totaling 8 MiB and valid color folders."})
        except Exception:
            self.reply(500, {"error": "Frogger could not complete this job."})
        finally:
            LOCK.release()


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
