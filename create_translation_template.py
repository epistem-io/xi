#!/usr/bin/env python3
"""
Create a translation template from extracted strings.
This generates a JSON file that can be used as a translation template.
"""

import json
from pathlib import Path


def create_translation_template():
    """Create a translation template JSON file."""
    base_path = Path(__file__).parent
    source_file = base_path / 'localizable_strings.json'
    template_file = base_path / 'translation_template.json'
    
    # Load source strings
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create template structure
    template = {
        "metadata": {
            "source_language": "en",
            "target_language": "LANGUAGE_CODE",  # e.g., "es", "fr", "de"
            "translator": "TRANSLATOR_NAME",
            "date": "YYYY-MM-DD",
            "total_strings": 0
        },
        "translations": {}
    }
    
    # Generate unique string IDs and create translation entries
    string_count = 0
    string_index = 0  # Add index for duplicate line numbers
    seen_keys = {}  # Track seen keys
    
    for filename, categories in data.items():
        for category, strings in categories.items():
            for item in strings:
                # Create a unique key for this string
                # Format: filename.category.line_number or filename.category.line_number_N for duplicates
                base_key = f"{filename.replace('.py', '')}.{category}.{item['line']}"
                
                # Handle duplicates by adding an index
                if base_key in seen_keys:
                    seen_keys[base_key] += 1
                    key = f"{base_key}_{seen_keys[base_key]}"
                else:
                    seen_keys[base_key] = 0
                    key = base_key
                
                template["translations"][key] = {
                    "source": item['text'],
                    "translation": "",  # Empty, to be filled by translator
                    "context": item['context'],
                    "file": item['file'],
                    "line": item['line'],
                    "category": category,
                    "status": "untranslated",  # Can be: untranslated, translated, reviewed
                    "notes": ""
                }
                string_count += 1
    
    template["metadata"]["total_strings"] = string_count
    
    # Write template
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Translation template created: {template_file}")
    print(f"   Total strings: {string_count}")
    print(f"\nInstructions for translators:")
    print(f"1. Copy {template_file.name} to a new file (e.g., translation_es.json)")
    print(f"2. Update metadata: target_language, translator, date")
    print(f"3. Fill in the 'translation' field for each entry")
    print(f"4. Update 'status' to 'translated' when complete")
    print(f"5. Add any notes if needed")


if __name__ == '__main__':
    create_translation_template()
