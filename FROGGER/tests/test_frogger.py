from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image
from frogger import run_frogger


class WorkflowTest(unittest.TestCase):
    def test_two_phases_and_repeat_run(self):
        with TemporaryDirectory() as work:
            root = Path(work)
            blue, navy = root / "Blue", root / "Navy Blue"
            existing = blue / "no bg"
            existing.mkdir(parents=True)
            navy.mkdir()
            original = Image.new("RGB", (2, 2), "red")
            original.save(root / "Killer Bear Navy Blue.png")
            original.save(blue / "Bookworm Blue.png")
            original.save(root / "Unmatched.png")
            original.save(root / "Old Blue_nobg.png")
            (root / "Broken Blue.png").write_bytes(b"corrupt")
            events = []

            def process(data):
                self.assertEqual(events[-1]["phase"], "background_removal")
                self.assertTrue((navy / "Killer Bear Navy Blue.png").exists())
                self.assertTrue((blue / "Broken Blue.png").exists())
                png = BytesIO()
                Image.new("RGBA", (2, 2), (255, 0, 0, 0)).save(png, format="PNG")
                return png.getvalue()

            result = run_frogger(root, events.append, processor_factory=lambda: process)
            self.assertEqual(result["status"], "completed_with_errors")
            self.assertEqual(len(result["sorted"]), 2)
            self.assertEqual(len(result["generated"]), 2)
            self.assertEqual(len(result["errors"]), 1)
            self.assertTrue((root / "Unmatched.png").exists())
            self.assertTrue((root / "Old Blue_nobg.png").exists())
            with Image.open(existing / "Bookworm Blue_nobg.png") as png:
                self.assertEqual(png.getpixel((0, 0))[3], 0)
            self.assertFalse((existing / "No BG").exists())
            progress = [event["progress"] for event in events]
            self.assertEqual(progress, sorted(progress))
            self.assertEqual(progress[-1], 100)
            repeat = run_frogger(root, processor_factory=lambda: self.fail("Unexpected model setup"))
            self.assertFalse(repeat["generated"])
            self.assertFalse(repeat["sorted"])
            self.assertEqual(len(repeat["errors"]), 1)
