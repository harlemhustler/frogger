import base64
from io import BytesIO
import unittest
from zipfile import ZipFile
from PIL import Image
from server import run_sort


class SortTests(unittest.TestCase):
    def image(self, name):
        data = BytesIO()
        Image.new("RGB", (4, 4), "red").save(data, format="PNG")
        return {"name": name, "data": base64.b64encode(data.getvalue()).decode("ascii")}

    def test_sort_and_keep_unmatched(self):
        payload = {"operation": "sort", "folders": ["Red", "Blue"],
                   "files": [self.image("red-art.png"), self.image("unknown.png")]}
        result = run_sort(payload)
        with ZipFile(BytesIO(base64.b64decode(result["archive"]))) as archive:
            self.assertIn("Red/red-art.png", archive.namelist())
            self.assertIn("Unsorted/unknown.png", archive.namelist())
            with Image.open(BytesIO(archive.read("Red/red-art.png"))) as image:
                self.assertEqual(image.size, (4, 4))
        self.assertEqual(result["sorted"], 1)

    def test_multiword_variant_handles_and_longest_match(self):
        result = run_sort({"operation": "sort", "folders": ["Blue", "Navy Blue", "Olive Green"],
                           "files": [self.image("shirt_navy-blue.png"), self.image("olive_green-shirt.png")]})
        with ZipFile(BytesIO(base64.b64decode(result["archive"]))) as archive:
            self.assertIn("Navy Blue/shirt_navy-blue.png", archive.namelist())
            self.assertIn("Olive Green/olive_green-shirt.png", archive.namelist())
        self.assertEqual(result["sorted"], 2)

    def test_reject_paths_and_unsupported_operations(self):
        for name in ["../escape.png", "folder/file.png", "a\\b.png"]:
            with self.assertRaises(ValueError):
                run_sort({"operation": "sort", "folders": ["Red"], "files": [self.image(name)]})
        with self.assertRaises(ValueError):
            run_sort({"operation": "background_removal", "folders": ["Red"], "files": [self.image("red.png")]})


if __name__ == "__main__":
    unittest.main()
