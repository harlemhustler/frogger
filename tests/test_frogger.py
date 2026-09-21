import os
import tempfile
import unittest
from pathlib import Path

from frogger import infer_variant_label, process_variant_folder, run_secondary_job


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

    def test_process_variant_folder_matches_explicit_destination_subfolder_and_custom_second_job(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source"
            source.mkdir()
            dest = Path(tmpdir) / "organized"
            secondary = Path(tmpdir) / "secondary"
            for folder in ["Black", "Navy Blue"]:
                (dest / folder).mkdir(parents=True, exist_ok=True)
                (secondary / folder).mkdir(parents=True, exist_ok=True)

            from PIL import Image
            img = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
            for x in range(5, 15):
                for y in range(5, 15):
                    img.putpixel((x, y), (0, 0, 0, 255))
            img.save(source / "Navy Blue Hoodie.png")

            results = process_variant_folder(
                source_dir=source,
                destination_root=dest,
                move_suffix="",
                no_bg_suffix="nobg",
                match_tag="navy blue",
                secondary_destination_root=secondary,
                secondary_script="background_remover",
                secondary_suffix="nobg",
            )

            self.assertTrue((dest / "Navy Blue" / "Navy Blue Hoodie.png").exists())
            self.assertTrue((secondary / "Navy Blue" / "Navy Blue Hoodie_nobg.png").exists())
            self.assertIn("Navy Blue", results["matched_folders"])
            self.assertTrue(results["secondary_outputs"])

    def test_run_secondary_job_supports_button_actions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "variant.png"
            dest = Path(tmpdir) / "secondary"
            from PIL import Image
            img = Image.new("RGBA", (40, 40), (255, 255, 255, 255))
            img.save(source)

            duplicate = run_secondary_job(source, dest, script_name="duplicate", suffix="copy")
            thumbnail = run_secondary_job(source, dest, script_name="thumbnail", suffix="thumb")
            compress = run_secondary_job(source, dest, script_name="compress", suffix="compressed")

            self.assertTrue(duplicate)
            self.assertTrue(thumbnail)
            self.assertTrue(compress)
            self.assertTrue((dest / source.parent.name / "variant_copy.png").exists())
            self.assertTrue((dest / source.parent.name / "variant_thumb.png").exists())
            self.assertTrue((dest / source.parent.name / "variant_compressed.png").exists())


if __name__ == "__main__":
    unittest.main()
