# Frogger

Frogger is the internal name for the variant-image workflow that:

1. reads a folder of original product art
2. infers a color or number label from each filename
3. moves files into color/variant subfolders
4. creates a second pass with a no-background suffix such as `nobg`
5. keeps the workflow simple enough to run from a path-based input

## Example usage

```bash
python frogger.py --source "C:/images/variant-source" --destination "C:/images/organized" --move-suffix "" --no-bg-suffix "nobg" --variant-label-field "title"
```

## Example of file naming behavior

Original files:
- Navy Blue Hoodie.png
- Black - 04 shirt.png
- Variant_07.png

Result folders:
- `Navy Blue/Navy Blue Hoodie.png`
- `Navy Blue/Navy Blue Hoodie_nobg.png`
- `Black/Black - 04 shirt.png`
- `Black/Black - 04 shirt_nobg.png`
- `07/Variant_07.png`
- `07/Variant_07_nobg.png`

## Input flow for a human operator

The script is intentionally easy to drive from a UI or a single terminal run. For a manual pass, the operator provides:
- source folder containing original variant art
- destination root for organized color folders
- suffix to add to the moved files (usually blank or a brand tag)
- suffix to add to the generated no-background copy (for this project: `nobg`)

## For tomorrow's demo

Planned workflow:
- source: Killer Bear / Bookworm clothing art folders
- destination: separate color-named folders
- generated pass: transparent-background copies with `nobg` suffix
- output: clean variant folders ready for product mockups and Shopify uploads

## Notes

- The script prefers color names when a title contains a known color.
- If no color is found, it falls back to a numeric token present in the filename.
- If the environment has `rembg` installed, it uses that pipeline first; otherwise it falls back to a built-in alpha-mask background removal heuristic.
