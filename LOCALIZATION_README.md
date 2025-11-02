# Localizable Strings Extraction

This directory contains tools and results for extracting localizable/translatable strings from the Epistem land cover mapping platform.

## Overview

The `extract_localizable_strings.py` script analyzes Python files in the Streamlit application to identify all user-facing strings that should be localized for different languages.

## Files Generated

1. **`localizable_strings.json`** - Structured JSON file containing all extracted strings
2. **`localizable_strings_report.txt`** - Human-readable report of all strings
3. **`localizable_strings.csv`** - CSV format for spreadsheet applications and translators
4. **`translation_template.json`** - Ready-to-use template for translation workflows

## What Strings are Extracted?

The script identifies and categorizes the following types of localizable strings:

### Categories

1. **Titles & Headers**
   - `st.title()`, `st.header()`, `st.subheader()` content
   - Main page titles and section headings

2. **Messages**
   - `st.info()`, `st.success()`, `st.warning()`, `st.error()` messages
   - User feedback and status messages

3. **Labels**
   - Button labels (`st.button()`)
   - Form field labels (`st.text_input()`, `st.selectbox()`, etc.)
   - Download button labels
   - Metric labels

4. **Markdown Content**
   - Content passed to `st.markdown()`
   - Markdown variables used in the application
   - Rich text descriptions

5. **Help Text**
   - Tooltip text from `help` parameters
   - Instructional text in form fields

6. **Other UI Text**
   - `st.text()`, `st.write()` content
   - Other user-facing strings

## Usage

### Running the Extraction

```bash
python extract_localizable_strings.py
```

This will:
- Scan `home.py`
- Scan all Python files in the `pages/` directory
- Generate `localizable_strings.json`
- Generate `localizable_strings_report.txt`

### Generating CSV Format

For easier review in spreadsheet applications or distribution to translators:

```bash
python json_to_csv.py
```

This creates `localizable_strings.csv` with columns for translation and notes.

### Creating Translation Template

To generate a structured translation template:

```bash
python create_translation_template.py
```

This creates `translation_template.json` which translators can copy and fill in.

### Output Format

The JSON file is structured as follows:

```json
{
  "filename.py": {
    "titles_headers": [
      {
        "text": "The actual text to translate",
        "line": 42,
        "context": "title",
        "file": "filename.py"
      }
    ],
    "messages": [...],
    "labels": [...],
    "markdown_content": [...],
    "help_text": [...],
    "other_ui_text": [...]
  }
}
```

## Extraction Results

**Total Files Processed:** 4
- `home.py`
- `1_Module_1_Generate_Image_Mosaic.py`
- `2_Module_2_Classification_scheme.py`
- `3_Module_3-4_Analyze_ROI.py`

**Total Localizable Strings Found:** 169

### Breakdown by File

| File | Strings Extracted |
|------|-------------------|
| home.py | 6 |
| 1_Module_1_Generate_Image_Mosaic.py | 64 |
| 2_Module_2_Classification_scheme.py | 28 |
| 3_Module_3-4_Analyze_ROI.py | 71 |

## Next Steps for Localization

1. **Review the extracted strings** in `localizable_strings.json`
2. **Create translation files** for each target language (e.g., `translations_es.json`, `translations_fr.json`)
3. **Implement i18n system** to load and use translations at runtime
4. **Update the code** to use translation keys instead of hardcoded strings

## Example Translation Workflow

### Option 1: Using CSV (Recommended for most translators)

1. Use `localizable_strings.csv` as the base template
2. Share with translators using Excel, Google Sheets, or similar
3. Translators fill in the "Translation" column
4. Return completed CSV for integration

### Option 2: Using JSON Template (Recommended for developers)

1. Generate translation template:
   ```bash
   python create_translation_template.py
   ```

2. Create language-specific files:
   ```bash
   cp translation_template.json translation_es.json  # Spanish
   cp translation_template.json translation_fr.json  # French
   ```

3. Update metadata in each file:
   ```json
   {
     "metadata": {
       "source_language": "en",
       "target_language": "es",
       "translator": "John Doe",
       "date": "2025-11-02",
       "total_strings": 169
     }
   }
   ```

4. Fill in translations for each entry:
   ```json
   {
     "home.titles_headers.12": {
       "source": "About",
       "translation": "Acerca de",
       "status": "translated"
     }
   }
   ```

### Option 3: Direct JSON editing

Use `localizable_strings.json` directly to create translation mappings.

## Technical Details

### Extraction Method

The script uses Python's Abstract Syntax Tree (AST) to parse source files and identify:
- Streamlit function calls with text parameters
- String literals in relevant contexts
- F-string components
- Variable assignments containing UI text

### Supported Streamlit Functions

**Text Display:**
- `title`, `header`, `subheader`
- `markdown`, `text`, `caption`
- `info`, `success`, `warning`, `error`, `exception`

**Interactive Widgets:**
- `button`, `checkbox`, `radio`
- `selectbox`, `multiselect`
- `slider`, `text_input`, `number_input`
- `file_uploader`, `download_button`
- And more...

## Notes

- The script automatically deduplicates identical strings
- Very short strings (< 2 characters) are filtered out
- F-strings are partially supported (static parts only)
- Context information helps translators understand usage

## Maintenance

To update the extracted strings after code changes:
```bash
python extract_localizable_strings.py
```

This will regenerate both output files with the latest strings from the codebase.
