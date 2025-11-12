#!/usr/bin/env python3
"""
Translation Infrastructure and Validation Tools for EpistemX Bahasa Indonesia Translation

This module provides utilities for:
- Loading and parsing the CSV translation reference file
- String matching and replacement functions
- Validation functions to check for missing translations
- Backup and rollback utilities for safe file modification
"""

import csv
import os
import shutil
import re
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import json


class TranslationManager:
    """Main class for managing translations and file operations."""
    
    def __init__(self, csv_path: str = "i18n/20251102_EpistemX_localizable_strings.csv"):
        """
        Initialize the translation manager.
        
        Args:
            csv_path: Path to the CSV translation reference file
        """
        self.csv_path = csv_path
        self.translations = {}
        self.backup_dir = "translation_backups"
        self.load_translations()
        
    def load_translations(self) -> None:
        """Load translations from the CSV reference file."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Translation CSV file not found: {self.csv_path}")
            
        self.translations = {}
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(self.csv_path, 'r', encoding=encoding) as file:
                        file_content = file.read()
                        break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                raise Exception("Could not decode CSV file with any supported encoding")
            
            # Parse CSV from string content
            import io
            csv_file = io.StringIO(file_content)
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                    english_text = row['English Text'].strip()
                    bahasa_text = row['Bahasa Indonesia'].strip()
                    
                    # Skip empty translations or "no change" entries
                    if bahasa_text and bahasa_text.lower() not in ['no change', '']:
                        self.translations[english_text] = {
                            'translation': bahasa_text,
                            'file': row['File'],
                            'category': row['Category'],
                            'context': row['Context'],
                            'line': row.get('Line', ''),
                            'id': row.get('ID', '')
                        }
                        
            print(f"Loaded {len(self.translations)} translations from {self.csv_path}")
            
        except Exception as e:
            raise Exception(f"Error loading translations: {str(e)}")
    
    def find_translation(self, english_text: str) -> Optional[str]:
        """
        Find the Bahasa Indonesia translation for an English text.
        
        Args:
            english_text: The English text to translate
            
        Returns:
            The Bahasa Indonesia translation or None if not found
        """
        # Direct match first
        if english_text in self.translations:
            return self.translations[english_text]['translation']
            
        # Try with stripped whitespace
        stripped_text = english_text.strip()
        if stripped_text in self.translations:
            return self.translations[stripped_text]['translation']
            
        return None
    
    def get_translation_info(self, english_text: str) -> Optional[Dict]:
        """
        Get full translation information for an English text.
        
        Args:
            english_text: The English text to look up
            
        Returns:
            Dictionary with translation info or None if not found
        """
        if english_text in self.translations:
            return self.translations[english_text]
        
        stripped_text = english_text.strip()
        if stripped_text in self.translations:
            return self.translations[stripped_text]
            
        return None 
   
    def create_backup(self, file_path: str) -> str:
        """
        Create a backup of a file before modification.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File to backup not found: {file_path}")
            
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Copy the file
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        
        return backup_path
    
    def restore_backup(self, original_path: str, backup_path: str) -> bool:
        """
        Restore a file from its backup.
        
        Args:
            original_path: Path where the file should be restored
            backup_path: Path to the backup file
            
        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                print(f"Backup file not found: {backup_path}")
                return False
                
            shutil.copy2(backup_path, original_path)
            print(f"Restored {original_path} from backup {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {str(e)}")
            return False
    
    def list_backups(self) -> List[str]:
        """
        List all available backup files.
        
        Returns:
            List of backup file paths
        """
        if not os.path.exists(self.backup_dir):
            return []
            
        backups = []
        for filename in os.listdir(self.backup_dir):
            if '.backup_' in filename:
                backups.append(os.path.join(self.backup_dir, filename))
                
        return sorted(backups)


class StringReplacer:
    """Handles string replacement operations in Python files."""
    
    def __init__(self, translation_manager: TranslationManager):
        """
        Initialize the string replacer.
        
        Args:
            translation_manager: Instance of TranslationManager
        """
        self.tm = translation_manager
        
    def find_translatable_strings(self, file_path: str) -> List[Dict]:
        """
        Find all translatable strings in a Python file.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            List of dictionaries containing string information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        translatable_strings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Find Streamlit function calls with string parameters
                patterns = [
                    r'st\.title\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.header\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.subheader\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.button\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.selectbox\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.text_input\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.file_uploader\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.slider\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.radio\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.date_input\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.number_input\s*\(\s*["\']([^"\']+)["\']\s*',
                    r'st\.markdown\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.success\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.error\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.warning\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'st\.info\s*\(\s*["\']([^"\']+)["\']\s*\)',
                    r'label\s*=\s*["\']([^"\']+)["\']',
                    r'help\s*=\s*["\']([^"\']+)["\']',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        string_text = match.group(1)
                        translatable_strings.append({
                            'file': file_path,
                            'line_number': line_num,
                            'original_text': string_text,
                            'full_line': line.strip(),
                            'pattern': pattern,
                            'start_pos': match.start(),
                            'end_pos': match.end()
                        })
                        
        except Exception as e:
            raise Exception(f"Error analyzing file {file_path}: {str(e)}")
            
        return translatable_strings 
   
    def replace_strings_in_file(self, file_path: str, create_backup: bool = True) -> Dict:
        """
        Replace translatable strings in a Python file with Bahasa Indonesia equivalents.
        
        Args:
            file_path: Path to the Python file to process
            create_backup: Whether to create a backup before modification
            
        Returns:
            Dictionary with replacement statistics and results
        """
        if create_backup:
            backup_path = self.tm.create_backup(file_path)
        else:
            backup_path = None
            
        try:
            # Find all translatable strings
            translatable_strings = self.find_translatable_strings(file_path)
            
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Track replacements
            replacements_made = []
            untranslated_strings = []
            
            # Sort strings by position (reverse order to maintain positions during replacement)
            translatable_strings.sort(key=lambda x: x['start_pos'], reverse=True)
            
            # Process each string
            for string_info in translatable_strings:
                original_text = string_info['original_text']
                translation = self.tm.find_translation(original_text)
                
                if translation:
                    # Perform the replacement
                    old_pattern = f'"{original_text}"'
                    new_pattern = f'"{translation}"'
                    
                    # Also try single quotes
                    if old_pattern not in content:
                        old_pattern = f"'{original_text}'"
                        new_pattern = f"'{translation}'"
                    
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern, 1)
                        replacements_made.append({
                            'original': original_text,
                            'translation': translation,
                            'line': string_info['line_number'],
                            'file': file_path
                        })
                else:
                    untranslated_strings.append({
                        'text': original_text,
                        'line': string_info['line_number'],
                        'file': file_path
                    })
            
            # Write the modified content back to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            result = {
                'file_path': file_path,
                'backup_path': backup_path,
                'replacements_made': replacements_made,
                'untranslated_strings': untranslated_strings,
                'total_found': len(translatable_strings),
                'total_replaced': len(replacements_made),
                'total_untranslated': len(untranslated_strings)
            }
            
            print(f"Processed {file_path}:")
            print(f"  - Found {result['total_found']} translatable strings")
            print(f"  - Replaced {result['total_replaced']} strings")
            print(f"  - {result['total_untranslated']} strings need manual review")
            
            return result
            
        except Exception as e:
            # Restore backup if something went wrong
            if backup_path and os.path.exists(backup_path):
                self.tm.restore_backup(file_path, backup_path)
            raise Exception(f"Error processing file {file_path}: {str(e)}")


class ValidationTools:
    """Tools for validating translations and file integrity."""
    
    def __init__(self, translation_manager: TranslationManager):
        """
        Initialize validation tools.
        
        Args:
            translation_manager: Instance of TranslationManager
        """
        self.tm = translation_manager
        
    def validate_python_syntax(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a Python file has correct syntax.
        
        Args:
            file_path: Path to the Python file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Try to compile the code
            compile(content, file_path, 'exec')
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def check_missing_translations(self, file_paths: List[str]) -> Dict:
        """
        Check for strings in files that don't have translations in the CSV.
        
        Args:
            file_paths: List of Python file paths to check
            
        Returns:
            Dictionary with missing translation information
        """
        all_missing = []
        file_results = {}
        
        replacer = StringReplacer(self.tm)
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
                
            try:
                translatable_strings = replacer.find_translatable_strings(file_path)
                missing_in_file = []
                
                for string_info in translatable_strings:
                    original_text = string_info['original_text']
                    if not self.tm.find_translation(original_text):
                        missing_in_file.append({
                            'text': original_text,
                            'line': string_info['line_number'],
                            'context': string_info['full_line']
                        })
                        
                file_results[file_path] = {
                    'total_strings': len(translatable_strings),
                    'missing_translations': missing_in_file,
                    'missing_count': len(missing_in_file)
                }
                
                all_missing.extend(missing_in_file)
                
            except Exception as e:
                file_results[file_path] = {
                    'error': str(e)
                }
        
        return {
            'files': file_results,
            'total_missing': len(all_missing),
            'all_missing_strings': all_missing
        }
    
    def generate_translation_report(self, results: List[Dict], output_path: str = "translation_report.json") -> str:
        """
        Generate a comprehensive translation report.
        
        Args:
            results: List of translation results from file processing
            output_path: Path where to save the report
            
        Returns:
            Path to the generated report file
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files_processed': len(results),
                'total_strings_found': sum(r.get('total_found', 0) for r in results),
                'total_strings_replaced': sum(r.get('total_replaced', 0) for r in results),
                'total_untranslated': sum(r.get('total_untranslated', 0) for r in results)
            },
            'file_details': results,
            'untranslated_strings': []
        }
        
        # Collect all untranslated strings
        for result in results:
            if 'untranslated_strings' in result:
                report['untranslated_strings'].extend(result['untranslated_strings'])
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
            
        print(f"Translation report saved to: {output_path}")
        return output_path
    
    def export_missing_translations_csv(self, file_paths: List[str], output_path: str = "missing_translations.csv") -> str:
        """
        Export missing translations to a CSV file for easy tracking and management.
        
        Args:
            file_paths: List of Python file paths to analyze
            output_path: Path where to save the CSV file
            
        Returns:
            Path to the generated CSV file
        """
        missing_data = []
        replacer = StringReplacer(self.tm)
        
        # Collect all missing translations with detailed information
        for file_path in file_paths:
            if not os.path.exists(file_path):
                continue
                
            try:
                translatable_strings = replacer.find_translatable_strings(file_path)
                
                for string_info in translatable_strings:
                    original_text = string_info['original_text']
                    translation = self.tm.find_translation(original_text)
                    
                    # Determine category based on the pattern used
                    category = self._categorize_string_pattern(string_info.get('pattern', ''))
                    
                    # Determine context from the pattern
                    context = self._extract_context_from_pattern(string_info.get('pattern', ''))
                    
                    missing_data.append({
                        'ID': '',  # Will be filled sequentially
                        'File': os.path.basename(file_path),
                        'Category': category,
                        'Line': string_info['line_number'],
                        'Context': context,
                        'English Text': original_text,
                        'Bahasa Indonesia': translation if translation else '',
                        'Status': 'Translated' if translation else 'Needs Translation',
                        'Full Line': string_info['full_line'].strip(),
                        'Pattern': string_info.get('pattern', '')
                    })
                    
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        # Sort by file and line number
        missing_data.sort(key=lambda x: (x['File'], x['Line']))
        
        # Assign sequential IDs
        for i, item in enumerate(missing_data, 1):
            item['ID'] = i
        
        # Write to CSV
        if missing_data:
            fieldnames = ['ID', 'File', 'Category', 'Line', 'Context', 'English Text', 
                         'Bahasa Indonesia', 'Status', 'Full Line', 'Pattern']
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(missing_data)
        
        print(f"Exported {len(missing_data)} strings to {output_path}")
        print(f"  - {sum(1 for item in missing_data if item['Status'] == 'Translated')} already translated")
        print(f"  - {sum(1 for item in missing_data if item['Status'] == 'Needs Translation')} need translation")
        
        return output_path
    
    def _categorize_string_pattern(self, pattern: str) -> str:
        """Categorize a string based on its regex pattern."""
        if 'title' in pattern or 'header' in pattern or 'subheader' in pattern:
            return 'Titles Headers'
        elif 'button' in pattern:
            return 'Labels'
        elif 'success' in pattern or 'error' in pattern or 'warning' in pattern or 'info' in pattern:
            return 'Messages'
        elif 'selectbox' in pattern or 'text_input' in pattern or 'file_uploader' in pattern or 'slider' in pattern or 'radio' in pattern or 'date_input' in pattern or 'number_input' in pattern:
            return 'Labels'
        elif 'markdown' in pattern:
            return 'Markdown Content'
        elif 'label=' in pattern:
            return 'Labels'
        elif 'help=' in pattern:
            return 'Help Text'
        else:
            return 'Other UI Text'
    
    def _extract_context_from_pattern(self, pattern: str) -> str:
        """Extract context information from regex pattern."""
        if 'title' in pattern:
            return 'title'
        elif 'header' in pattern:
            return 'header'
        elif 'subheader' in pattern:
            return 'subheader'
        elif 'button' in pattern:
            return 'button'
        elif 'selectbox' in pattern:
            return 'selectbox'
        elif 'text_input' in pattern:
            return 'text_input'
        elif 'file_uploader' in pattern:
            return 'file_uploader'
        elif 'slider' in pattern:
            return 'slider'
        elif 'radio' in pattern:
            return 'radio'
        elif 'date_input' in pattern:
            return 'date_input'
        elif 'number_input' in pattern:
            return 'number_input'
        elif 'markdown' in pattern:
            return 'markdown'
        elif 'success' in pattern:
            return 'success'
        elif 'error' in pattern:
            return 'error'
        elif 'warning' in pattern:
            return 'warning'
        elif 'info' in pattern:
            return 'info'
        elif 'label=' in pattern:
            return 'label'
        elif 'help=' in pattern:
            return 'help'
        else:
            return 'unknown'


# Convenience functions for easy usage
def setup_translation_infrastructure(csv_path: str = "i18n/20251102_EpistemX_localizable_strings.csv") -> Tuple[TranslationManager, StringReplacer, ValidationTools]:
    """
    Set up all translation infrastructure components.
    
    Args:
        csv_path: Path to the CSV translation reference file
        
    Returns:
        Tuple of (TranslationManager, StringReplacer, ValidationTools)
    """
    tm = TranslationManager(csv_path)
    replacer = StringReplacer(tm)
    validator = ValidationTools(tm)
    
    return tm, replacer, validator


def test_translation_infrastructure():
    """Test the translation infrastructure with sample operations."""
    print("Testing Translation Infrastructure...")
    
    try:
        # Setup
        tm, replacer, validator = setup_translation_infrastructure()
        
        # Test translation lookup
        test_strings = ["About", "Instructions", "Search Landsat Imagery"]
        print("\nTesting translation lookup:")
        for test_string in test_strings:
            translation = tm.find_translation(test_string)
            print(f"  '{test_string}' -> '{translation}'")
        
        # Test file analysis (if home.py exists)
        if os.path.exists("home.py"):
            print("\nTesting string detection in home.py:")
            strings = replacer.find_translatable_strings("home.py")
            print(f"  Found {len(strings)} translatable strings")
            for i, string_info in enumerate(strings[:3]):  # Show first 3
                print(f"    {i+1}. Line {string_info['line_number']}: '{string_info['original_text']}'")
        
        # Test validation
        print("\nTesting validation tools:")
        if os.path.exists("home.py"):
            is_valid, error = validator.validate_python_syntax("home.py")
            print(f"  home.py syntax valid: {is_valid}")
            if error:
                print(f"    Error: {error}")
        
        print("\nTranslation infrastructure test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_translation_infrastructure()