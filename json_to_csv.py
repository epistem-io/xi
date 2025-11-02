#!/usr/bin/env python3
"""
Convert the localizable strings JSON to CSV format for easier review and translation.
"""

import json
import csv
from pathlib import Path


def json_to_csv():
    """Convert localizable_strings.json to CSV format."""
    base_path = Path(__file__).parent
    json_file = base_path / 'localizable_strings.json'
    csv_file = base_path / 'localizable_strings.csv'
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV data
    rows = []
    string_id = 1
    
    for filename, categories in data.items():
        for category, strings in categories.items():
            for item in strings:
                rows.append({
                    'ID': string_id,
                    'File': filename,
                    'Category': category.replace('_', ' ').title(),
                    'Line': item['line'],
                    'Context': item['context'],
                    'English Text': item['text'].strip(),
                    'Translation': '',  # Empty column for translation
                    'Notes': ''  # Empty column for translator notes
                })
                string_id += 1
    
    # Write to CSV
    fieldnames = ['ID', 'File', 'Category', 'Line', 'Context', 'English Text', 'Translation', 'Notes']
    
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"CSV file created: {csv_file}")
    print(f"Total rows: {len(rows)}")
    print(f"\nThe CSV can be used for:")
    print("  - Easy review in spreadsheet applications")
    print("  - Distribution to translators")
    print("  - Translation management")


if __name__ == '__main__':
    json_to_csv()
