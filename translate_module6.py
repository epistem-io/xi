#!/usr/bin/env python3
"""
Translate Module 6: Classification and LULC Creation to Bahasa Indonesia
"""

from translation_utils import setup_translation_infrastructure
import os

def main():
    """Main translation function for Module 6."""
    
    # Setup translation infrastructure
    print("Setting up translation infrastructure...")
    tm, replacer, validator = setup_translation_infrastructure()
    
    # Process Module 6 file
    file_path = 'pages/5_Module_6_Classification_and_LULC_Creation.py'
    print(f'Processing {file_path}...')
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        return False
    
    try:
        # Translate the file
        result = replacer.replace_strings_in_file(file_path, create_backup=True)
        
        print(f'\n=== Translation Results ===')
        print(f'Total strings found: {result["total_found"]}')
        print(f'Total strings replaced: {result["total_replaced"]}')
        print(f'Total untranslated: {result["total_untranslated"]}')
        print(f'Backup created at: {result["backup_path"]}')
        
        if result['untranslated_strings']:
            print(f'\n=== Untranslated Strings ({len(result["untranslated_strings"])}) ===')
            for i, untranslated in enumerate(result['untranslated_strings'], 1):
                print(f'{i:2d}. Line {untranslated["line"]:3d}: "{untranslated["text"]}"')
        
        # Validate syntax
        print(f'\n=== Syntax Validation ===')
        is_valid, error = validator.validate_python_syntax(file_path)
        print(f'Syntax validation: {"PASSED" if is_valid else "FAILED"}')
        if error:
            print(f'Error: {error}')
            return False
        
        print(f'\n=== Summary ===')
        print(f'✅ Module 6 translation completed successfully!')
        print(f'📁 Original file backed up to: {result["backup_path"]}')
        print(f'🔄 {result["total_replaced"]} strings translated')
        if result["total_untranslated"] > 0:
            print(f'⚠️  {result["total_untranslated"]} strings need manual review')
        
        return True
        
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)