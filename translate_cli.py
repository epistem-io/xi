#!/usr/bin/env python3
"""
Command Line Interface for EpistemX Translation Tools

Usage examples:
    python translate_cli.py --test                    # Test the infrastructure
    python translate_cli.py --analyze home.py         # Analyze a file for translatable strings
    python translate_cli.py --translate home.py       # Translate a file
    python translate_cli.py --validate home.py        # Validate file syntax
    python translate_cli.py --check-missing *.py      # Check for missing translations
    python translate_cli.py --export-csv "*.py"       # Export all detected strings to CSV
    python translate_cli.py --export-csv "pages/*.py" --output module_strings.csv  # Export with custom filename
    python translate_cli.py --list-backups            # List available backups
"""

import argparse
import glob
import sys
from translation_utils import setup_translation_infrastructure, TranslationManager, StringReplacer, ValidationTools


def main():
    parser = argparse.ArgumentParser(description='EpistemX Translation Tools')
    parser.add_argument('--test', action='store_true', help='Test the translation infrastructure')
    parser.add_argument('--analyze', metavar='FILE', help='Analyze a file for translatable strings')
    parser.add_argument('--translate', metavar='FILE', help='Translate strings in a file')
    parser.add_argument('--validate', metavar='FILE', help='Validate Python file syntax')
    parser.add_argument('--check-missing', metavar='PATTERN', help='Check for missing translations in files')
    parser.add_argument('--export-csv', metavar='PATTERN', help='Export detected strings to CSV file')
    parser.add_argument('--output', metavar='FILE', help='Output file path for CSV export')
    parser.add_argument('--list-backups', action='store_true', help='List available backup files')
    parser.add_argument('--restore', nargs=2, metavar=('ORIGINAL', 'BACKUP'), help='Restore file from backup')
    parser.add_argument('--csv-path', default='i18n/20251102_EpistemX_localizable_strings.csv', 
                       help='Path to translation CSV file')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        # Setup translation infrastructure
        tm, replacer, validator = setup_translation_infrastructure(args.csv_path)
        
        if args.test:
            print("Running translation infrastructure test...")
            from translation_utils import test_translation_infrastructure
            success = test_translation_infrastructure()
            sys.exit(0 if success else 1)
        
        elif args.analyze:
            print(f"Analyzing {args.analyze} for translatable strings...")
            strings = replacer.find_translatable_strings(args.analyze)
            
            print(f"\nFound {len(strings)} translatable strings:")
            for i, string_info in enumerate(strings, 1):
                translation = tm.find_translation(string_info['original_text'])
                status = "✓ HAS TRANSLATION" if translation else "✗ NEEDS TRANSLATION"
                print(f"{i:3d}. Line {string_info['line_number']:3d}: '{string_info['original_text']}' [{status}]")
                if translation:
                    print(f"     -> '{translation}'")
        
        elif args.translate:
            print(f"Translating strings in {args.translate}...")
            result = replacer.replace_strings_in_file(args.translate)
            
            print(f"\nTranslation Results:")
            print(f"  File: {result['file_path']}")
            print(f"  Backup: {result['backup_path']}")
            print(f"  Total strings found: {result['total_found']}")
            print(f"  Successfully translated: {result['total_replaced']}")
            print(f"  Need manual review: {result['total_untranslated']}")
            
            if result['untranslated_strings']:
                print(f"\nStrings needing manual review:")
                for item in result['untranslated_strings']:
                    print(f"  Line {item['line']}: '{item['text']}'")
        
        elif args.validate:
            print(f"Validating syntax of {args.validate}...")
            is_valid, error = validator.validate_python_syntax(args.validate)
            
            if is_valid:
                print("✓ File syntax is valid")
            else:
                print(f"✗ Syntax error: {error}")
                sys.exit(1)
        
        elif args.check_missing:
            print(f"Checking for missing translations in files matching: {args.check_missing}")
            files = glob.glob(args.check_missing)
            
            if not files:
                print("No files found matching the pattern")
                return
            
            results = validator.check_missing_translations(files)
            
            print(f"\nMissing Translation Report:")
            print(f"Total files checked: {len(results['files'])}")
            print(f"Total missing translations: {results['total_missing']}")
            
            for file_path, file_result in results['files'].items():
                if 'error' in file_result:
                    print(f"\n{file_path}: ERROR - {file_result['error']}")
                else:
                    print(f"\n{file_path}:")
                    print(f"  Total strings: {file_result['total_strings']}")
                    print(f"  Missing translations: {file_result['missing_count']}")
                    
                    if file_result['missing_translations']:
                        for missing in file_result['missing_translations'][:5]:  # Show first 5
                            print(f"    Line {missing['line']}: '{missing['text']}'")
                        if len(file_result['missing_translations']) > 5:
                            print(f"    ... and {len(file_result['missing_translations']) - 5} more")
        
        elif args.export_csv:
            print(f"Exporting detected strings from files matching: {args.export_csv}")
            files = glob.glob(args.export_csv)
            
            if not files:
                print("No files found matching the pattern")
                return
            
            # Determine output file path
            output_path = args.output if args.output else "detected_strings.csv"
            
            # Export to CSV
            csv_path = validator.export_missing_translations_csv(files, output_path)
            
            print(f"\n✓ CSV export completed: {csv_path}")
            print(f"You can now:")
            print(f"  - Open {csv_path} in Excel or any spreadsheet application")
            print(f"  - Add translations to the 'Bahasa Indonesia' column")
            print(f"  - Use the CSV as reference for manual translation work")
        
        elif args.list_backups:
            print("Available backup files:")
            backups = tm.list_backups()
            
            if not backups:
                print("No backup files found")
            else:
                for backup in backups:
                    print(f"  {backup}")
        
        elif args.restore:
            original_path, backup_path = args.restore
            print(f"Restoring {original_path} from {backup_path}...")
            
            success = tm.restore_backup(original_path, backup_path)
            if success:
                print("✓ File restored successfully")
            else:
                print("✗ Failed to restore file")
                sys.exit(1)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()