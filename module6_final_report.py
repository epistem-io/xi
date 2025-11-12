#!/usr/bin/env python3
"""
Final validation and report for Module 6 translation
"""

import os
import ast
from datetime import datetime

def validate_module6_translation():
    """Validate the Module 6 translation and generate final report."""
    
    file_path = 'pages/5_Module_6_Classification_and_LULC_Creation.py'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validate Python syntax
        ast.parse(content)
        print("✅ Python syntax validation: PASSED")
        
        # Check for key translated strings
        key_translations = {
            'Pembuatan Peta Tutupan Lahan': 'Main title',
            'Tentang': 'Sidebar title',
            'Cek Prasyarat': 'Prerequisites section',
            'Ekstrak Fitur': 'Extract Features button',
            'Membuat Model Klasifikasi': 'Model training section',
            'Ulasan Model Klasifikasi': 'Model review section',
            'Ekstraksi Fitur/Nilai Piksel': 'Tab 1 title',
            'Latih Model Klasifikasi': 'Tab 2 title',
            'Ringkasan Hasil Latih dan Evaluasi Model Klasifikasi': 'Tab 3 title',
            'Visualisasi': 'Tab 4 title',
            'Unduh Hasil Klasifikasi': 'Tab 5 title'
        }
        
        found_translations = 0
        missing_translations = []
        
        print("\n=== Key Translation Check ===")
        for translation, description in key_translations.items():
            if translation in content:
                found_translations += 1
                print(f"✅ {description}: '{translation}'")
            else:
                missing_translations.append((translation, description))
                print(f"❌ {description}: '{translation}' - NOT FOUND")
        
        # Check for remaining English strings that should be translated
        english_patterns = [
            'Feature Extraction Configuration',
            'Data Split Options',
            'Extraction Parameters',
            'Training Data Ratio',
            'Class ID',
            'Pixel Size (meters)',
            'Extract Features',
            'Feature extraction complete',
            'Model Training',
            'Number of Trees',
            'Variables per Split',
            'Minimum Leaf Size',
            'Train Classification Model',
            'Feature Importance Analysis',
            'Model Accuracy Assessment'
        ]
        
        remaining_english = []
        print("\n=== Remaining English Strings Check ===")
        for pattern in english_patterns:
            if pattern in content:
                remaining_english.append(pattern)
                print(f"⚠️  Still in English: '{pattern}'")
        
        # Generate summary
        print(f"\n=== Translation Summary ===")
        print(f"File: {file_path}")
        print(f"Syntax validation: PASSED")
        print(f"Key translations found: {found_translations}/{len(key_translations)}")
        print(f"Translation coverage: {(found_translations/len(key_translations)*100):.1f}%")
        
        if missing_translations:
            print(f"\nMissing key translations ({len(missing_translations)}):")
            for translation, description in missing_translations:
                print(f"  - {description}: '{translation}'")
        
        if remaining_english:
            print(f"\nRemaining English strings ({len(remaining_english)}):")
            for pattern in remaining_english[:10]:  # Show first 10
                print(f"  - '{pattern}'")
            if len(remaining_english) > 10:
                print(f"  ... and {len(remaining_english) - 10} more")
        
        # Overall assessment
        if found_translations >= len(key_translations) * 0.8:  # 80% threshold
            print(f"\n✅ TRANSLATION STATUS: GOOD")
            print(f"   Most critical interface elements have been translated.")
            if remaining_english:
                print(f"   Some secondary strings may still need translation.")
        else:
            print(f"\n⚠️  TRANSLATION STATUS: NEEDS WORK")
            print(f"   Several critical interface elements are missing translations.")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ Python syntax validation: FAILED")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    print("=== Module 6 Translation Validation ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = validate_module6_translation()
    
    if success:
        print(f"\n🎉 Module 6 translation validation completed!")
    else:
        print(f"\n❌ Module 6 translation validation failed!")
    
    exit(0 if success else 1)