# AI Data Quality Checker - Micro App for ARTI Education
# Focus: "Vikten av data, datakvalitet för AI och val av data" (Level 1 curriculum)
# Usage: Run script with a CSV file path -> get a quality report
# Example: python data_quality_checker.py dataset.csv

import sys
import pandas as pd

def check_data_quality(file_path):
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        return

    print("\n=== AI Data Quality Report ===\n")
    print(f"📂 File: {file_path}")
    print(f"🔢 Rows: {len(data)}, Columns: {len(data.columns)}\n")

    # Missing values
    missing = data.isnull().sum()
    if missing.sum() > 0:
        print("⚠️ Missing values detected:")
        print(missing[missing > 0])
    else:
        print("✅ No missing values found.")

    print("\n---")

    # Duplicate rows
    duplicates = data.duplicated().sum()
    print(f"🔄 Duplicate rows: {duplicates}")

    print("\n---")

    # Basic stats
    print("📊 Column statistics:")
    print(data.describe(include='all', datetime_is_numeric=True).transpose())

    print("\n---")

    # Target balance check (if column named 'label' exists)
    if "label" in data.columns:
        print("🎯 Target label distribution:")
        print(data['label'].value_counts(normalize=True).round(2))
    else:
        print("ℹ️ No 'label' column found for balance check.")

    print("\n=== End of Report ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_quality_checker.py <csv_file>")
    else:
        check_data_quality(sys.argv[1])
