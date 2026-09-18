# Frogger

Frogger is a lightweight image-automation workflow built for variant-heavy product art. It reads a source folder, infers the product label from the file name, moves the original files into color or variant folders, and generates a second pass with a transparent-background suffix such as nobg.

This is useful for apparel and print workflows where a design team drops a folder of variant files and expects the system to sort them into clean, usable structure without manual file handling.

## What the workflow does

1. Reads a directory of raw product images
2. Extracts the product color or numeric variant from the title
3. Creates destination folders named by the inferred label
4. Moves the originals into those folders
5. Produces a no-background version using the suffix you choose

## Example

Original files:
- Navy Blue Hoodie.png
- Black - 04 shirt.png
- Variant_07.png

Result folders:
- Navy Blue/Navy Blue Hoodie.png
- Navy Blue/Navy Blue Hoodie_nobg.png
- Black/Black - 04 shirt.png
- Black/Black - 04 shirt_nobg.png
- 07/Variant_07.png
- 07/Variant_07_nobg.png

## Command example

python frogger.py --source "C:/images/variant-source" --destination "C:/images/organized" --move-suffix "" --no-bg-suffix "nobg" --variant-label-field "title"

## Why it matters

This solves a real production bottleneck: sorting dozens of color variations into folders and preparing clean transparent-background assets for mockups, Shopify uploads, and product configuration workflows.

## Resume blurb

Built Frogger, a Python image automation tool for organizing product-variant files by color or numeric label, moving originals into structured folders, and generating no-background asset variants for e-commerce and mockup workflows.

## Notes

- The script prefers known color names when they appear in the title.
- If no color is found, it falls back to a numeric token in the filename.
- If rembg is available, it uses that path for background removal; otherwise, it falls back to a built-in alpha-mask approach.

## Demo target

This foundation is intended for a future resume/demo workflow using Killer Bear and Bookworm clothing art folders, where each variant set can be organized, sorted, and prepared for product mockups quickly.
