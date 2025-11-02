# Quick Start Guide - Localization

This guide will help you quickly get started with the localization files.

## What Was Done

We've extracted **169 localizable strings** from:
- `home.py` (6 strings)
- `pages/1_Module_1_Generate_Image_Mosaic.py` (64 strings)
- `pages/2_Module_2_Classification_scheme.py` (28 strings)
- `pages/3_Module_3-4_Analyze_ROI.py` (71 strings)

## Quick Start

### For a Quick Overview
```bash
# View the human-readable report
cat localizable_strings_report.txt | less

# Or just see the statistics
grep -A 20 "EXTRACTION STATISTICS" EXTRACTION_SUMMARY.md
```

### For Translators (Easy Way)
1. Open `localizable_strings.csv` in Excel or Google Sheets
2. Fill in the "Translation" column
3. Save and return the file

### For Developers (Structured Way)
```bash
# Create a Spanish translation
cp translation_template.json translation_es.json

# Edit translation_es.json:
# - Update metadata (target_language: "es")
# - Fill in "translation" fields
# - Update "status" to "translated"
```

### To Re-run Extraction
```bash
# Extract all strings
python extract_localizable_strings.py

# Generate CSV
python json_to_csv.py

# Generate translation template
python create_translation_template.py
```

## Files You'll Use Most

1. **`localizable_strings.csv`** - Share with translators
2. **`EXTRACTION_SUMMARY.md`** - Statistics and overview
3. **`LOCALIZATION_README.md`** - Complete documentation

## Sample Strings Extracted

**Page Titles:**
- "Epistem land cover mapping platform demo"
- "Search and Generate Landsat Image Mosaic"
- "Define Land Cover Land Use Classification Scheme"

**Messages:**
- "Shapefile loaded successfully!"
- "AOI conversion completed!"
- "Export task submitted successfully!"

**Labels:**
- "Upload a zipped shapefile (.zip)"
- "Select Landsat Sensor:"
- "Choose date selection mode:"

**Help Text:**
- "The output will be saved as GeoTIFF (.tif)"
- "Google Drive Folder to stored the result"

## Next Steps

1. **Review** the extracted strings in your preferred format
2. **Decide** which languages to support
3. **Translate** using CSV or JSON template
4. **Implement** i18n in the application code
5. **Re-run** extraction after any code changes

## Questions?

See `LOCALIZATION_README.md` for detailed documentation.
