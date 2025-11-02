#!/usr/bin/env python3
"""
Script to extract localizable/translation strings from Streamlit application files.

This script scans home.py and all Python files in the pages directory to extract
user-facing strings that should be localized for different languages.

Output: A JSON file containing all extracted strings organized by file and category.
"""

import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Set


class LocalizableStringExtractor(ast.NodeVisitor):
    """AST visitor to extract localizable strings from Python code."""
    
    # Streamlit functions that contain user-facing text
    STREAMLIT_TEXT_FUNCTIONS = {
        'title', 'header', 'subheader', 'markdown', 'text', 'caption',
        'info', 'success', 'warning', 'error', 'exception',
        'write', 'code', 'latex', 'divider'
    }
    
    # Streamlit functions with label parameters
    STREAMLIT_LABEL_FUNCTIONS = {
        'button', 'checkbox', 'radio', 'selectbox', 'multiselect',
        'slider', 'select_slider', 'text_input', 'number_input',
        'text_area', 'date_input', 'time_input', 'file_uploader',
        'color_picker', 'form_submit_button', 'download_button',
        'metric'
    }
    
    def __init__(self, filename: str):
        self.filename = filename
        self.strings: Dict[str, List[Dict]] = {
            'titles_headers': [],
            'messages': [],
            'labels': [],
            'markdown_content': [],
            'help_text': [],
            'other_ui_text': []
        }
        self.seen_strings: Set[str] = set()
    
    def add_string(self, category: str, text: str, line_no: int, context: str = ""):
        """Add a string to the collection if it's not already seen."""
        if text and isinstance(text, str) and text.strip():
            # Skip very short strings that are likely not translatable
            if len(text.strip()) < 2:
                return
            
            # Create a unique key for deduplication
            key = f"{category}:{text}"
            if key not in self.seen_strings:
                self.seen_strings.add(key)
                self.strings[category].append({
                    'text': text,
                    'line': line_no,
                    'context': context,
                    'file': self.filename
                })
    
    def visit_Call(self, node: ast.Call):
        """Visit function call nodes to extract strings."""
        # Check if it's a streamlit call
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            
            # Extract from text display functions
            if func_name in self.STREAMLIT_TEXT_FUNCTIONS:
                category = self._categorize_function(func_name)
                
                # Get the first positional argument (usually the text content)
                if node.args:
                    self._extract_from_arg(node.args[0], category, node.lineno, func_name)
            
            # Extract from functions with label parameter
            elif func_name in self.STREAMLIT_LABEL_FUNCTIONS:
                # First arg is usually the label
                if node.args:
                    self._extract_from_arg(node.args[0], 'labels', node.lineno, func_name)
                
                # Check for 'help' keyword argument
                for keyword in node.keywords:
                    if keyword.arg == 'help':
                        self._extract_from_arg(keyword.value, 'help_text', node.lineno, f"{func_name}.help")
                    elif keyword.arg == 'label':
                        self._extract_from_arg(keyword.value, 'labels', node.lineno, f"{func_name}.label")
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign):
        """Visit assignment nodes to catch markdown variables."""
        # Check if assigning to a variable named 'markdown'
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'markdown':
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    self.add_string('markdown_content', node.value.value, node.lineno, 'markdown variable')
        
        self.generic_visit(node)
    
    def _extract_from_arg(self, arg_node, category: str, line_no: int, context: str):
        """Extract string from an argument node."""
        if isinstance(arg_node, ast.Constant) and isinstance(arg_node.value, str):
            self.add_string(category, arg_node.value, line_no, context)
        elif isinstance(arg_node, ast.JoinedStr):  # f-string
            # For f-strings, we extract the static parts
            for value in arg_node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    self.add_string(category, value.value, line_no, f"{context} (f-string part)")
    
    def _categorize_function(self, func_name: str) -> str:
        """Categorize the function based on its name."""
        if func_name in {'title', 'header', 'subheader'}:
            return 'titles_headers'
        elif func_name == 'markdown':
            return 'markdown_content'
        elif func_name in {'info', 'success', 'warning', 'error', 'exception'}:
            return 'messages'
        else:
            return 'other_ui_text'


def extract_strings_from_file(filepath: Path) -> Dict:
    """Extract localizable strings from a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code, filename=str(filepath))
        extractor = LocalizableStringExtractor(str(filepath.name))
        extractor.visit(tree)
        
        return extractor.strings
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return {}


def main():
    """Main function to extract strings from all relevant files."""
    base_path = Path(__file__).parent
    
    # Files to process
    files_to_process = [
        base_path / 'home.py',
    ]
    
    # Add all Python files from pages directory
    pages_dir = base_path / 'pages'
    if pages_dir.exists():
        files_to_process.extend(sorted(pages_dir.glob('*.py')))
    
    # Extract strings from all files
    all_strings = {}
    total_count = 0
    
    for filepath in files_to_process:
        if filepath.exists():
            print(f"Processing: {filepath.name}")
            strings = extract_strings_from_file(filepath)
            
            # Count strings in this file
            file_count = sum(len(items) for items in strings.values())
            total_count += file_count
            
            if file_count > 0:
                all_strings[str(filepath.name)] = strings
                print(f"  Found {file_count} localizable strings")
        else:
            print(f"Warning: {filepath} not found")
    
    # Save to JSON file
    output_file = base_path / 'localizable_strings.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_strings, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"Total files processed: {len(all_strings)}")
    print(f"Total localizable strings found: {total_count}")
    print(f"Output saved to: {output_file}")
    print(f"{'='*60}")
    
    # Generate a summary report
    generate_summary_report(all_strings, base_path)


def generate_summary_report(all_strings: Dict, base_path: Path):
    """Generate a human-readable summary report."""
    report_file = base_path / 'localizable_strings_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("LOCALIZABLE STRINGS EXTRACTION REPORT\n")
        f.write("="*80 + "\n\n")
        
        for filename, categories in all_strings.items():
            f.write(f"\n{'='*80}\n")
            f.write(f"FILE: {filename}\n")
            f.write(f"{'='*80}\n\n")
            
            total_in_file = sum(len(items) for items in categories.values())
            f.write(f"Total strings in this file: {total_in_file}\n\n")
            
            for category, strings in categories.items():
                if strings:
                    f.write(f"\n{'-'*80}\n")
                    f.write(f"{category.upper().replace('_', ' ')} ({len(strings)} items)\n")
                    f.write(f"{'-'*80}\n\n")
                    
                    for item in strings:
                        f.write(f"Line {item['line']}: {item['context']}\n")
                        # Truncate very long strings for readability
                        text = item['text']
                        if len(text) > 200:
                            text = text[:200] + "..."
                        f.write(f"  \"{text}\"\n\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    print(f"Summary report saved to: {report_file}")


if __name__ == '__main__':
    main()
