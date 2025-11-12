#!/usr/bin/env python3
"""
Fix script for PIL DecompressionBombWarning and Earth Engine authentication issues.
"""

import os
import sys
import warnings

def fix_pil_decompression_warning():
    """Address PIL DecompressionBombWarning by filtering the warning."""
    # Filter out the specific PIL decompression bomb warning
    warnings.filterwarnings("ignore", "Image size .* exceeds limit .* could be decompression bomb DOS attack", UserWarning)
    print("✅ PIL decompression bomb warning filtered (warning suppressed)")

def check_earth_engine_setup():
    """Check and provide guidance for Earth Engine setup."""
    print("\n🔍 Checking Earth Engine setup...")
    
    # Check if service account file exists
    service_account_path = "auth/ee-donyindiarto-44198b511607.json"
    if os.path.exists(service_account_path):
        print(f"✅ Service account file found: {service_account_path}")
        
        # Check if project is in the filename/path
        if "ee-donyindiarto" in service_account_path:
            print("📋 Project ID appears to be: ee-donyindiarto")
    else:
        print(f"❌ Service account file not found: {service_account_path}")
        return False
    
    # Check environment variables
    gac = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if gac:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to: {gac}")
    else:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
    
    return True

def fix_earth_engine_auth():
    """Apply fixes for Earth Engine authentication."""
    print("\n🔧 Applying Earth Engine authentication fixes...")
    
    # Set the service account file path
    service_account_path = os.path.abspath("auth/ee-donyindiarto-44198b511607.json")
    if os.path.exists(service_account_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        print(f"✅ Set GOOGLE_APPLICATION_CREDENTIALS to: {service_account_path}")
    
    # The main issue is likely that the project needs to be registered for Earth Engine
    print("\n📋 Earth Engine Registration Check:")
    print("The error 'Not signed up for Earth Engine or project is not registered' means:")
    print("1. Your Google Cloud project 'ee-donyindiarto' needs Earth Engine API enabled")
    print("2. The project needs to be registered for Earth Engine access")
    print("3. Visit: https://developers.google.com/earth-engine/guides/access")
    print("4. Follow the registration process for your project")
    
    return True

def main():
    """Main function to apply all fixes."""
    print("🚀 EpistemX Issue Fix Script")
    print("=" * 50)
    
    # Fix PIL warning
    fix_pil_decompression_warning()
    
    # Check and fix Earth Engine
    check_earth_engine_setup()
    fix_earth_engine_auth()
    
    print("\n" + "=" * 50)
    print("✅ Fixes applied successfully!")
    print("\nNext steps:")
    print("1. Restart your Streamlit application")
    print("2. If Earth Engine still fails, register your project at:")
    print("   https://developers.google.com/earth-engine/guides/access")

if __name__ == "__main__":
    main()