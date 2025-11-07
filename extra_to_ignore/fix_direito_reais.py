#!/usr/bin/env python3
"""
Script to replace 'Direito Reais' with 'Direitos Reais' in the 'Field of Law' field
of all JSONL files in the outputs directory.
"""

import json
import os
from pathlib import Path


def fix_field_of_law(input_file, output_file):
    """
    Read a JSONL file, replace 'Direito Reais' with 'Direitos Reais' in 'Field of Law',
    and write to output file.
    """
    changes_count = 0
    total_lines = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            total_lines += 1
            try:
                data = json.loads(line.strip())
                
                # Check if 'Field of Law' exists and equals 'Direito Reais'
                if 'Field of Law' in data and data['Field of Law'] == 'Direito Reais':
                    data['Field of Law'] = 'Direitos Reais'
                    changes_count += 1
                
                # Write the (possibly modified) line
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {total_lines} in {input_file}: {e}")
                # Write the original line if there's an error
                outfile.write(line)
    
    return changes_count, total_lines


def main():
    outputs_dir = Path('/mnt/data-artemis/beatriz/LegalBench.PT/outputs')
    
    if not outputs_dir.exists():
        print(f"Error: Directory {outputs_dir} does not exist")
        return
    
    # Find all .jsonl files in the outputs directory
    jsonl_files = list(outputs_dir.glob('*.jsonl'))
    
    if not jsonl_files:
        print(f"No .jsonl files found in {outputs_dir}")
        return
    
    print(f"Found {len(jsonl_files)} JSONL files to process\n")
    
    total_changes = 0
    
    for jsonl_file in sorted(jsonl_files):
        print(f"Processing: {jsonl_file.name}")
        
        # Create a temporary output file
        temp_file = jsonl_file.with_suffix('.jsonl.tmp')
        
        try:
            changes, total = fix_field_of_law(jsonl_file, temp_file)
            
            # Replace the original file with the modified one
            temp_file.replace(jsonl_file)
            
            print(f"  - Modified {changes} entries out of {total} total lines")
            total_changes += changes
            
        except Exception as e:
            print(f"  - Error processing file: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
    
    print(f"\n✓ Done! Total changes made: {total_changes}")


if __name__ == '__main__':
    main()
