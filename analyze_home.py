#!/usr/bin/env python3
"""
Analyze home.py for translatable strings
"""

from translation_utils import setup_translation_infrastructure

def analyze_home_py():
    # Setup translation infrastructure
    tm, replacer, validator = setup_translation_infrastructure()
    
    # Find translatable strings in home.py
    strings = replacer.find_translatable_strings('home.py')
    print(f'Found {len(strings)} translatable strings in home.py:')
    print()
    
    found_translations = 0
    missing_translations = 0
    
    for i, string_info in enumerate(strings, 1):
        translation = tm.find_translation(string_info['original_text'])
        status = 'FOUND' if translation else 'MISSING'
        
        print(f'{i:2d}. Line {string_info["line_number"]:2d}: "{string_info["original_text"]}"')
        print(f'    Status: {status}')
        if translation:
            print(f'    Translation: "{translation}"')
            found_translations += 1
        else:
            missing_translations += 1
        print()
    
    print(f'Summary:')
    print(f'  Total strings: {len(strings)}')
    print(f'  Found translations: {found_translations}')
    print(f'  Missing translations: {missing_translations}')

if __name__ == "__main__":
    analyze_home_py()