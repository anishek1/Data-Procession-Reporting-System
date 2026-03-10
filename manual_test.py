import sys
import os

# Add the parent directory to sys.path so that 'dprs' can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from core.data_processor import load_file, compute_statistics, get_loaded_data
from core.validator import Schema, validate_schema, clean_data, check_missing_values

# 1. Define schema for weight-height.csv
my_schema = Schema({
    'Gender': {'type': 'string', 'required': True},
    'Height': {'type': 'float', 'required': True},
    'Weight': {'type': 'float', 'required': True}
})

try:
    print("--- 1. LOADING DATA ---")
    result = load_file("input/weight-height.csv")
    print(f"Successfully loaded file: {result['file']}")
    print(f"Rows: {result['rows']}, Columns: {result['columns']}")
    print(f"Headers: {result['headers']}\n")

    data = get_loaded_data()

    print("--- 2. CHECKING MISSING VALUES ---")
    missing = check_missing_values(data['rows'])
    print(json.dumps(missing, indent=2), "\n")

    print("--- 3. VALIDATING SCHEMA ---")
    try:
        val_result = validate_schema(data, my_schema)
        print("Validation Passed!")
    except Exception as e:
        print(f"Validation Error Caught: {e}")
        
    print("\n--- 4. CLEANING DATA ---")
    cleaned_rows = clean_data(data['rows'], my_schema)
    data['rows'] = cleaned_rows 
    print(f"Data remaining after cleaning: {len(cleaned_rows)} rows\n")
    
    print("--- 5. COMPUTING STATISTICS ---")
    stats = compute_statistics()
    print(json.dumps(stats, indent=2))

except Exception as e:
    print(f"An error occurred: {e}")
