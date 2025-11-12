#!/usr/bin/env python3
"""
Translation Report Generator for Module 7: Thematic Accuracy
Analyzes the translated file and generates a report of all translations applied.
"""

import re
import pandas as pd

def analyze_module7_translations():
    """Analyze Module 7 translations and generate report"""
    
    # Read the translated file
    with open('pages/6_Module_7_Thematic_Accuracy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define patterns to find translatable strings
    patterns = {
        'st.title': r'st\.title\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.subheader': r'st\.subheader\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.error': r'st\.error\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.warning': r'st\.warning\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.success': r'st\.success\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.info': r'st\.info\s*\(\s*["\']([^"\']+)["\']\s*\)',
        'st.button': r'st\.button\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.selectbox': r'st\.selectbox\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.number_input': r'st\.number_input\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.slider': r'st\.slider\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.file_uploader': r'st\.file_uploader\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.metric': r'st\.metric\s*\(\s*["\']([^"\']+)["\']\s*',
        'st.download_button': r'label\s*=\s*["\']([^"\']+)["\']\s*',
        'help_text': r'help\s*=\s*["\']([^"\']+)["\']\s*',
        'page_title': r'page_title\s*=\s*["\']([^"\']+)["\']\s*',
    }
    
    # Find all translatable strings
    found_strings = []
    
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            found_strings.append({
                'Type': pattern_name,
                'Text': match,
                'Status': 'Translated' if is_indonesian(match) else 'Needs Review'
            })
    
    # Check for markdown content
    markdown_pattern = r'st\.markdown\s*\(\s*["\']([^"\']+)["\']\s*\)'
    markdown_matches = re.findall(markdown_pattern, content, re.MULTILINE)
    for match in markdown_matches:
        if match not in ['---', '**', '*']:  # Skip formatting-only markdown
            found_strings.append({
                'Type': 'st.markdown',
                'Text': match,
                'Status': 'Translated' if is_indonesian(match) else 'Needs Review'
            })
    
    # Check for f-string content
    fstring_pattern = r'f["\']([^"\']*\{[^}]*\}[^"\']*)["\']'
    fstring_matches = re.findall(fstring_pattern, content, re.MULTILINE)
    for match in fstring_matches:
        found_strings.append({
            'Type': 'f-string',
            'Text': match,
            'Status': 'Translated' if is_indonesian(match) else 'Needs Review'
        })
    
    return found_strings

def is_indonesian(text):
    """Simple heuristic to check if text is likely Indonesian"""
    # Indonesian indicators
    indonesian_words = [
        'dan', 'atau', 'dengan', 'untuk', 'dari', 'ke', 'di', 'pada', 'dalam',
        'yang', 'adalah', 'akan', 'dapat', 'tidak', 'jika', 'juga', 'ini', 'itu',
        'akurasi', 'penilaian', 'data', 'kelas', 'hasil', 'modul', 'langkah',
        'unggah', 'pilih', 'konfigurasi', 'validasi', 'lapangan', 'referensi',
        'matriks', 'konfusi', 'kinerja', 'unduh', 'kembali', 'tingkat'
    ]
    
    # English indicators (should not be present in translated text)
    english_words = [
        'the', 'and', 'or', 'with', 'for', 'from', 'to', 'in', 'on', 'at',
        'that', 'is', 'will', 'can', 'not', 'if', 'also', 'this', 'that',
        'accuracy', 'assessment', 'data', 'class', 'result', 'module', 'step',
        'upload', 'choose', 'configuration', 'validation', 'field', 'reference'
    ]
    
    text_lower = text.lower()
    
    # Count Indonesian vs English words
    indonesian_count = sum(1 for word in indonesian_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    # If text contains Indonesian words or no English words, consider it translated
    return indonesian_count > 0 or english_count == 0

def generate_report():
    """Generate and save translation report"""
    
    print("🔍 Analyzing Module 7 translations...")
    
    # Analyze translations
    strings = analyze_module7_translations()
    
    # Create DataFrame
    df = pd.DataFrame(strings)
    
    # Generate summary
    total_strings = len(df)
    translated_count = len(df[df['Status'] == 'Translated'])
    needs_review_count = len(df[df['Status'] == 'Needs Review'])
    
    # Create report
    report = f"""
# Module 7 Translation Report
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total strings found**: {total_strings}
- **Translated**: {translated_count} ({translated_count/total_strings*100:.1f}%)
- **Needs review**: {needs_review_count} ({needs_review_count/total_strings*100:.1f}%)

## Translation Status by Type
{df.groupby(['Type', 'Status']).size().unstack(fill_value=0).to_string()}

## Strings Needing Review
"""
    
    # Add strings that need review
    needs_review = df[df['Status'] == 'Needs Review']
    if not needs_review.empty:
        report += "\n"
        for _, row in needs_review.iterrows():
            report += f"- **{row['Type']}**: {row['Text']}\n"
    else:
        report += "\n✅ All strings appear to be translated!\n"
    
    report += f"""

## All Translated Strings
"""
    
    # Add all translated strings
    translated = df[df['Status'] == 'Translated']
    if not translated.empty:
        report += "\n"
        for _, row in translated.iterrows():
            report += f"- **{row['Type']}**: {row['Text']}\n"
    
    # Save report
    with open('module7_translation_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Save detailed CSV
    df.to_csv('module7_translation_details.csv', index=False, encoding='utf-8')
    
    print(f"✅ Translation report generated!")
    print(f"📊 Summary: {translated_count}/{total_strings} strings translated ({translated_count/total_strings*100:.1f}%)")
    
    if needs_review_count > 0:
        print(f"⚠️  {needs_review_count} strings need review")
        print("📄 Check module7_translation_report.md for details")
    else:
        print("🎉 All strings appear to be translated!")
    
    return df

if __name__ == "__main__":
    generate_report()