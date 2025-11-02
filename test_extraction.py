#!/usr/bin/env python3
"""
Test script to validate the localization extraction.
"""

import json
import csv
from pathlib import Path


def test_extraction():
    """Run validation tests on the extraction."""
    base_path = Path(__file__).parent
    
    print("="*80)
    print("LOCALIZATION EXTRACTION TEST SUITE")
    print("="*80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Check JSON file exists and is valid
    print("\nTest 1: Validate JSON file...")
    try:
        with open(base_path / 'localizable_strings.json', 'r') as f:
            data = json.load(f)
        assert len(data) == 4, "Should have 4 files"
        total = sum(sum(len(strings) for strings in cats.values()) for cats in data.values())
        assert total == 169, f"Should have 169 strings, found {total}"
        print("  ✅ PASSED - JSON file is valid with 169 strings")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        tests_failed += 1
    
    # Test 2: Check CSV file exists and has correct structure
    print("\nTest 2: Validate CSV file...")
    try:
        with open(base_path / 'localizable_strings.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 169, f"Should have 169 rows, found {len(rows)}"
        assert 'English Text' in reader.fieldnames
        assert 'Translation' in reader.fieldnames
        print("  ✅ PASSED - CSV file has 169 rows with correct structure")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        tests_failed += 1
    
    # Test 3: Check translation template
    print("\nTest 3: Validate translation template...")
    try:
        with open(base_path / 'translation_template.json', 'r') as f:
            template = json.load(f)
        assert 'metadata' in template
        assert 'translations' in template
        assert template['metadata']['total_strings'] == 169
        assert len(template['translations']) == 169
        print("  ✅ PASSED - Translation template is valid")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        tests_failed += 1
    
    # Test 4: Check all categories are present
    print("\nTest 4: Validate categories...")
    try:
        expected_categories = {
            'titles_headers', 'messages', 'labels', 
            'markdown_content', 'help_text', 'other_ui_text'
        }
        found_categories = set()
        for file_data in data.values():
            found_categories.update(file_data.keys())
        assert found_categories == expected_categories, f"Missing categories: {expected_categories - found_categories}"
        print("  ✅ PASSED - All 6 categories present")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        tests_failed += 1
    
    # Test 5: Verify no empty strings
    print("\nTest 5: Check for empty strings...")
    try:
        empty_count = 0
        for file_data in data.values():
            for strings in file_data.values():
                for item in strings:
                    if not item['text'].strip():
                        empty_count += 1
        assert empty_count == 0, f"Found {empty_count} empty strings"
        print("  ✅ PASSED - No empty strings found")
        tests_passed += 1
    except Exception as e:
        print(f"  ❌ FAILED - {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests:  {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✅ All tests passed! Extraction is valid and complete.")
    else:
        print(f"\n❌ {tests_failed} test(s) failed!")
    
    print("="*80)
    
    return tests_failed == 0


if __name__ == '__main__':
    success = test_extraction()
    exit(0 if success else 1)
