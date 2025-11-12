# Design Document

## Overview

This design outlines the systematic approach for translating all user-facing English strings in the EpistemX application to Bahasa Indonesia. The translation will be performed module by module using the existing translation reference file `i18n/20251102_EpistemX_localizable_strings.csv` as the authoritative source for all translations.

The application follows a Streamlit-based architecture with multiple page modules, each containing various types of user-facing strings including titles, labels, messages, help text, and markdown content.

## Architecture

### Application Structure
The EpistemX application consists of:
- **Main Application**: `home.py` - Landing page with navigation
- **Module Pages**: Located in `pages/` directory
  - `1_Module_1_Generate_Image_Mosaic.py`
  - `2_Module_2_Classification_scheme.py` 
  - `3_Module_3_Generate_ROI.py`
  - `4_Module_4_Analyze_ROI.py`
  - `5_Module_6_Classification_and_LULC_Creation.py`
  - `6_Module_7_Thematic_Accuracy.py`

### Translation Reference System
- **Source File**: `i18n/20251102_EpistemX_localizable_strings.csv`
- **Structure**: Contains ID, File, Category, Line, Context, English Text, Bahasa Indonesia columns
- **Coverage**: 485+ translation entries covering all user-facing strings

## Components and Interfaces

### String Categories
Based on the translation reference file, strings are categorized as:

1. **Titles Headers**: Page titles, section headers, subheaders
2. **Labels**: Form inputs, buttons, selectboxes, file uploaders
3. **Messages**: Success, error, warning, info notifications
4. **Markdown Content**: Instructional text, descriptions, help content
5. **Help Text**: Tooltips and contextual help
6. **Other UI Text**: Metrics, previews, navigation elements

### Translation Mapping Strategy
Each string replacement will follow this pattern:
- **Input**: English string in Python code
- **Lookup**: Match against `English Text` column in CSV
- **Output**: Replace with corresponding `Bahasa Indonesia` value
- **Validation**: Ensure context and functionality preservation

### Module Processing Order
Translation will proceed in the specified sequence:
1. `home.py` (Home page)
2. `pages/1_Module_1_Generate_Image_Mosaic.py`
3. `pages/2_Module_2_Classification_scheme.py`
4. `pages/3_Module_3_Generate_ROI.py`
5. `pages/4_Module_4_Analyze_ROI.py`
6. `pages/5_Module_6_Classification_and_LULC_Creation.py`
7. `pages/6_Module_7_Thematic_Accuracy.py`

## Data Models

### Translation Entry Model
```
TranslationEntry {
  id: number
  file: string
  category: string
  line: number
  context: string
  english_text: string
  bahasa_indonesia: string
}
```

### String Replacement Model
```
StringReplacement {
  file_path: string
  line_number: number
  original_text: string
  translated_text: string
  context: string (st.title, st.button, etc.)
}
```

## Error Handling

### Translation Lookup Failures
- **Missing Translation**: Flag and report to user, do NOT attempt to translate independently
- **Context Mismatch**: Manual review required for ambiguous cases
- **Special Characters**: Preserve formatting and escape sequences
- **Untranslated Strings**: Create a report of all strings found in code but missing from CSV reference

### Code Integrity Preservation
- **Syntax Validation**: Ensure Python syntax remains valid after replacement
- **String Interpolation**: Preserve f-string formatting and variable placeholders
- **Function Parameters**: Only translate user-visible string literals, not parameter names

### Streamlit Component Compatibility
- **Length Constraints**: Ensure translated text fits within UI components
- **Special Formatting**: Preserve markdown syntax, HTML tags, and links
- **Interactive Elements**: Maintain button functionality and form validation

## Testing Strategy

### Validation Approach
1. **Syntax Testing**: Python syntax validation after each file modification
2. **Functional Testing**: Streamlit application startup and navigation testing
3. **Visual Testing**: UI layout and text display verification
4. **Content Testing**: Translation accuracy and context appropriateness

### Test Cases per Module
- **Navigation**: Verify all page links and routing work correctly
- **Forms**: Test input validation and submission processes
- **Interactive Elements**: Confirm buttons, dropdowns, and uploads function
- **Error Handling**: Validate error messages display correctly in Bahasa Indonesia

### Rollback Strategy
- **File Backup**: Create backup copies before modification
- **Version Control**: Commit changes incrementally per module
- **Validation Gates**: Stop process if critical errors detected

## Implementation Considerations

### String Identification Patterns
Common Streamlit string patterns to translate:
- `st.title("English Text")` → `st.title("Bahasa Indonesia")`
- `st.button("English Text")` → `st.button("Bahasa Indonesia")`
- `st.markdown("English Text")` → `st.markdown("Bahasa Indonesia")`
- `st.error("English Text")` → `st.error("Bahasa Indonesia")`
- `label="English Text"` → `label="Bahasa Indonesia"`
- `help="English Text"` → `help="Bahasa Indonesia"`

### Preservation Rules
Elements to keep in English:
- Variable names and function names
- Code comments and docstrings
- Import statements and module references
- Configuration keys and technical identifiers
- Backend processing logic and error handling code

### Special Handling Cases
- **F-strings**: Preserve variable interpolation while translating text portions
- **Multi-line strings**: Maintain formatting and line breaks
- **URLs and links**: Keep functional while translating display text
- **Technical terms**: Use provided translations or keep English if no translation exists