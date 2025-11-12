#!/usr/bin/env python3
"""
Translate home.py file with Bahasa Indonesia equivalents
"""

from translation_utils import setup_translation_infrastructure
import re

def translate_home_py():
    # Setup translation infrastructure
    tm, replacer, validator = setup_translation_infrastructure()
    
    # Create backup first
    backup_path = tm.create_backup('home.py')
    print(f"Created backup: {backup_path}")
    
    # Read the current file
    with open('home.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define manual translations based on the CSV and current content
    translations = {
        # Streamlit function calls
        "Earth Engine initialized successfully!": "Earth Engine berhasil diinisialisasi!",
        "Failed to initialize Earth Engine. Please check your authentication.": "Gagal menginisialisasi Earth Engine. Mohon periksa autentikasi Anda.",
        "About": "Tentang",
        
        # HTML content translations
        "🛰️ EpistemX Land Cover Mapping Platform": "🛰️ Platform Pemetaan Tutupan Lahan EpistemX",
        "Advanced Earth Observation Data Processing & Analysis": "Pemrosesan & Analisis Data Observasi Bumi Lanjutan",
        "🌍 Welcome to EpistemX": "🌍 Selamat Datang di EpistemX",
        "This multipage platform demonstrates EpistemX's powerful land cover mapping capabilities, \n    featuring automated Landsat imagery processing for your area of interest.": "Platform multi-halaman ini mendemonstrasikan kemampuan pemetaan tutupan lahan EpistemX yang canggih, \n    dengan fitur pemrosesan citra Landsat otomatis untuk area minat Anda.",
        "📋 Instructions": "📋 Instruksi",
        "🚀 Getting Started": "🚀 Memulai",
        "Define Area of Interest:": "Tentukan Area Minat:",
        "Draw a rectangle on the map or upload a shapefile (zip)": "Gambar persegi panjang di peta atau unggah shapefile (zip)",
        "Set Acquisition Date:": "Tentukan Tanggal Akuisisi:",
        "Specify the year - images will be filtered from January 1 to December 31": "Tentukan tahun - citra akan difilter dari 1 Januari hingga 31 Desember",
        "Configure Parameters:": "Konfigurasi Parameter:",
        "Set cloud cover percentage and sensor type (Landsat 5 TM - Landsat 9 OLI2)": "Tentukan persentase tutupan awan dan tipe sensor (Landsat 5 TM - Landsat 9 OLI2)",
        "Generate Mosaic:": "Buat Mozaik:",
        "Click run to create your satellite imagery mosaic": "Klik jalankan untuk membuat mozaik citra satelit Anda",
        "✅ Earth Engine Ready - You can proceed with analysis": "✅ Earth Engine Siap - Anda dapat melanjutkan analisis",
        "⚠️ Earth Engine Not Initialized - Please check authentication": "⚠️ Earth Engine Belum Diinisialisasi - Mohon periksa autentikasi",
        
        # Markdown content
        "An working example module 1 and 3 of Epistem land cover mapping platform. Adapted from:": "Contoh kerja modul 1 dan 3 dari platform pemetaan tutupan lahan Epistem. Diadaptasi dari:"
    }
    
    # Apply translations
    translated_count = 0
    untranslated_strings = []
    
    for english_text, bahasa_text in translations.items():
        if english_text in content:
            content = content.replace(english_text, bahasa_text)
            translated_count += 1
            print(f"✓ Translated: '{english_text[:50]}...' -> '{bahasa_text[:50]}...'")
        else:
            # Check if it's a partial match or needs different handling
            print(f"⚠ Not found in file: '{english_text[:50]}...'")
    
    # Write the translated content back
    with open('home.py', 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Validate syntax
    is_valid, error = validator.validate_python_syntax('home.py')
    if not is_valid:
        print(f"❌ Syntax error detected: {error}")
        print("Restoring backup...")
        tm.restore_backup('home.py', backup_path)
        return False
    
    print(f"\n✅ Translation completed successfully!")
    print(f"   - Translated {translated_count} strings")
    print(f"   - Backup saved to: {backup_path}")
    print(f"   - Syntax validation: PASSED")
    
    return True

if __name__ == "__main__":
    translate_home_py()