#!/usr/bin/env python3
"""
Generate detailed translation report for Module 6
"""

from translation_utils import setup_translation_infrastructure
import json
from datetime import datetime

def generate_module6_report():
    """Generate a detailed report for Module 6 translation."""
    
    # Setup translation infrastructure
    tm, replacer, validator = setup_translation_infrastructure()
    
    file_path = 'pages/5_Module_6_Classification_and_LULC_Creation.py'
    
    # Find all translatable strings
    translatable_strings = replacer.find_translatable_strings(file_path)
    
    # Categorize strings
    translated = []
    untranslated = []
    
    for string_info in translatable_strings:
        original_text = string_info['original_text']
        translation = tm.find_translation(original_text)
        
        if translation:
            translated.append({
                'line': string_info['line_number'],
                'original': original_text,
                'translation': translation,
                'context': string_info['full_line'].strip()
            })
        else:
            untranslated.append({
                'line': string_info['line_number'],
                'original': original_text,
                'context': string_info['full_line'].strip()
            })
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'file': file_path,
        'summary': {
            'total_strings': len(translatable_strings),
            'translated': len(translated),
            'untranslated': len(untranslated),
            'completion_percentage': round((len(translated) / len(translatable_strings)) * 100, 1)
        },
        'translated_strings': translated,
        'untranslated_strings': untranslated
    }
    
    # Save detailed report
    with open('module6_translation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Create markdown report for easy reading
    markdown_report = f"""# Module 6 Translation Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **File:** {file_path}
- **Total Strings:** {report['summary']['total_strings']}
- **Translated:** {report['summary']['translated']} ({report['summary']['completion_percentage']}%)
- **Untranslated:** {report['summary']['untranslated']}

## Untranslated Strings Requiring Manual Translation

"""
    
    for i, item in enumerate(untranslated, 1):
        markdown_report += f"### {i}. Line {item['line']}\n"
        markdown_report += f"**Original:** `{item['original']}`\n\n"
        markdown_report += f"**Context:** `{item['context']}`\n\n"
        markdown_report += f"**Suggested Translation:** _[Manual translation needed]_\n\n"
        markdown_report += "---\n\n"
    
    with open('module6_translation_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"Reports generated:")
    print(f"- JSON: module6_translation_report.json")
    print(f"- Markdown: module6_translation_report.md")
    print(f"\nSummary: {report['summary']['translated']}/{report['summary']['total_strings']} strings translated ({report['summary']['completion_percentage']}%)")

if __name__ == "__main__":
    generate_module6_report()