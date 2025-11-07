#!/usr/bin/env python3
"""
Convert consolidated_with_ids.jsonl into separate files for each model.

This script reads the consolidated file where each entry contains a "Model Answers" 
dictionary with answers from multiple models, and creates separate .jsonl files 
for each model in the outputs/ directory.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


def convert_answer_to_string(answer):
    """
    Convert answer to string format expected by evaluation script.
    
    Args:
        answer: The answer which can be a string, list, or other type
        
    Returns:
        str: String representation of the answer
    """
    if isinstance(answer, str):
        return answer
    elif isinstance(answer, list):
        # Convert list to string representation that can be parsed by ast.literal_eval
        return str(answer)
    else:
        # For any other type, convert to string
        return str(answer)


def sanitize_filename(model_name: str) -> str:
    """Convert model name to a safe filename."""
    # Replace special characters that might cause issues in filenames
    safe_name = model_name.replace("/", "__").replace("-", "_").replace(".", "_")
    return safe_name


def convert_consolidated_to_individual_files(input_file: str, output_dir: str):
    """
    Convert consolidated answers file to individual model files.
    
    Args:
        input_file: Path to consolidated_with_ids.jsonl
        output_dir: Directory to save individual model files
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Dictionary to store file handles for each model
    model_files = {}
    model_data_counts = {}
    
    try:
        print(f"Reading from: {input_file}")
        print(f"Output directory: {output_dir}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 1000 == 0:
                    print(f"Processed {line_num} lines...")
                
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping malformed JSON at line {line_num}: {e}")
                    continue
                
                # Extract model answers
                model_answers = data.get('Model Answers', {})
                
                if not model_answers:
                    print(f"Warning: No Model Answers found at line {line_num}")
                    continue
                
                # Process each model
                for model_name, model_answer in model_answers.items():
                    # Create new entry for this model
                    model_entry = data.copy()
                    
                    # Convert Answer to string if it's not already a string
                    model_entry["Answer"] = convert_answer_to_string(data.get("Answer"))
                    
                    # Remove the original Model Answers key completely
                    if "Model Answers" in model_entry:
                        del model_entry["Model Answers"]
                    
                    # Add only this model's answer as Prediction
                    model_entry["Prediction"] = model_answer
                    
                    # Get or create file handle for this model
                    if model_name not in model_files:
                        safe_model_name = sanitize_filename(model_name)
                        output_filename = f"{safe_model_name}.jsonl"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        print(f"Creating file for model: {model_name} -> {output_filename}")
                        model_files[model_name] = open(output_path, 'w', encoding='utf-8')
                        model_data_counts[model_name] = 0
                    
                    # Write the entry to the model's file
                    json.dump(model_entry, model_files[model_name], ensure_ascii=False)
                    model_files[model_name].write('\n')
                    model_data_counts[model_name] += 1
        
        print(f"\nProcessing complete! Total lines processed: {line_num}")
        print("\nSummary:")
        for model_name, count in model_data_counts.items():
            safe_model_name = sanitize_filename(model_name)
            print(f"  {model_name}: {count} entries -> {safe_model_name}_85549.jsonl")
            
    finally:
        # Close all file handles
        for f in model_files.values():
            if not f.closed:
                f.close()
    
    print(f"\nAll files saved to: {output_dir}")


def main():
    """Main function to run the conversion."""
    # Define input and output paths
    script_dir = Path(__file__).parent
    input_file = script_dir / "consolidated_with_ids.jsonl"
    output_dir = script_dir / "outputs"
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found!")
        return 1
    
    print("Converting consolidated answers to individual model files...")
    convert_consolidated_to_individual_files(str(input_file), str(output_dir))
    
    return 0


if __name__ == "__main__":
    exit(main())