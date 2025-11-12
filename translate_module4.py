#!/usr/bin/env python3
"""
Translation script for Module 4: Analyze ROI
Translates all user-facing strings from English to Bahasa Indonesia
"""

import sys
import os
from translation_utils import setup_translation_infrastructure

def translate_module4():
    """Translate Module 4: Analyze ROI to Bahasa Indonesia."""
    
    print("=== Module 4 Translation Process ===")
    print("Translating: pages/4_Module_4_Analyze_ROI.py")
    
    try:
        # Setup translation infrastructure
        print("Setting up translation infrastructure...")
        tm, replacer, validator = setup_translation_infrastructure()
        
        # Define the file to translate
        file_path = "pages/4_Module_4_Analyze_ROI.py"
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return False
        
        # Validate syntax before translation
        print("Validating original file syntax...")
        is_valid, error = validator.validate_python_syntax(file_path)
        if not is_valid:
            print(f"ERROR: Original file has syntax errors: {error}")
            return False
        print("✓ Original file syntax is valid")
        
        # Perform translation
        print("Performing translation...")
        result = replacer.replace_strings_in_file(file_path, create_backup=True)
        
        # Validate syntax after translation
        print("Validating translated file syntax...")
        is_valid, error = validator.validate_python_syntax(file_path)
        if not is_valid:
            print(f"ERROR: Translated file has syntax errors: {error}")
            print("Restoring from backup...")
            if result['backup_path']:
                tm.restore_backup(file_path, result['backup_path'])
            return False
        print("✓ Translated file syntax is valid")
        
        # Display results
        print("\n=== Translation Results ===")
        print(f"File: {result['file_path']}")
        print(f"Backup created: {result['backup_path']}")
        print(f"Total strings found: {result['total_found']}")
        print(f"Strings translated: {result['total_replaced']}")
        print(f"Strings needing review: {result['total_untranslated']}")
        
        if result['replacements_made']:
            print(f"\n✓ Successfully translated {len(result['replacements_made'])} strings:")
            for i, replacement in enumerate(result['replacements_made'][:10], 1):  # Show first 10
                print(f"  {i}. Line {replacement['line']}: '{replacement['original']}' -> '{replacement['translation']}'")
            if len(result['replacements_made']) > 10:
                print(f"  ... and {len(result['replacements_made']) - 10} more")
        
        if result['untranslated_strings']:
            print(f"\n⚠ Strings requiring manual review ({len(result['untranslated_strings'])}):")
            for i, untranslated in enumerate(result['untranslated_strings'][:10], 1):  # Show first 10
                print(f"  {i}. Line {untranslated['line']}: '{untranslated['text']}'")
            if len(result['untranslated_strings']) > 10:
                print(f"  ... and {len(result['untranslated_strings']) - 10} more")
        
        # Generate detailed report
        report_path = f"module4_translation_report.json"
        validator.generate_translation_report([result], report_path)
        print(f"\nDetailed report saved to: {report_path}")
        
        print("\n=== Module 4 Translation Completed Successfully! ===")
        return True
        
    except Exception as e:
        print(f"ERROR during translation: {str(e)}")
        return False

if __name__ == "__main__":
    success = translate_module4()
    sys.exit(0 if success else 1)