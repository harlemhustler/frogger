import os
import tempfile
import unittest
from pathlib import Path

from frogger import infer_variant_label, process_variant_folder


class FroggerTestCase(unittest.TestCase):
    def test_infer_variant_label_from_title(self):
        self.assertEqual(infer_variant_label("Navy Blue Hoodie.png"), "Navy Blue")
        self.assertEqual(infer_variant_label("Black - 04 shirt.png"), "Black")
        self.assertEqual(infer_variant_label("Variant_07.png"), "07")

    def test_process_variant_folder_creates_moved_and_no_bg_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source"
            source.mkdir()
            dest = Path(tmpdir) / "output"

            # Make small color-bearing images using Pillow data.
            from PIL import Image

            for name in ["Navy Blue Hoodie.png", "Black Hoodie.png"]:
                img = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
                for x in range(5, 15):
                    for y in range(5, 15):
                        img.putpixel((x, y), (0, 0, 0, 255))
                img.save(source / name)

            results = process_variant_folder(
                source_dir=source,
                destination_root=dest,
                move_suffix="",
                no_bg_suffix="nobg",
                variant_label_field="title",
                background_tolerance=245,
            )

            self.assertTrue(results["moved_files"])
            self.assertTrue(results["no_bg_files"])
            self.assertTrue((dest / "Navy Blue" / "Navy Blue Hoodie.png").exists())
            self.assertTrue((dest / "Navy Blue" / "Navy Blue Hoodie_nobg.png").exists())
            self.assertTrue((dest / "Black" / "Black Hoodie.png").exists())
            self.assertTrue((dest / "Black" / "Black Hoodie_nobg.png").exists())


if __name__ == "__main__":
    unittest.main()
