#!/usr/bin/env python3
"""
Script to consolidate model answers from multiple JSON files into a single JSONL file.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Union


def process_json_file(json_path: Path, field_of_law: str) -> List[Dict]:
    """
    Process a single JSON file and extract questions with model answers.
    
    Args:
        json_path: Path to the JSON file
        field_of_law: The field of law (folder name)
    
    Returns:
        List of dictionaries containing question data
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = []
        
        for item in data:
            # Skip empty items or items with insufficient data
            if not item or len(item) < 4:
                continue
            
            question_type = item[0]
            question_text = item[1]
            answer = item[2]
            model_answers = item[3] if len(item) > 3 else {}
            
            # Create the output dictionary
            question_dict = {
                "Field of Law": field_of_law,
                "Type": question_type,
                "Question": question_text,
                "Answer": answer,
                "Model Answers": model_answers
            }
            
            questions.append(question_dict)
        
        return questions
    
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return []


def main():
    """
    Main function to iterate through all JSON files and create a consolidated JSONL.
    """
    # Define paths
    models_answers_dir = Path("/mnt/data-artemis/beatriz/avaliacao/models_answers")
    output_dir = Path("/mnt/data-artemis/beatriz/LegalBench.PT")
    output_file = output_dir / "consolidated_model_answers.jsonl"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_questions = []
    
    # Iterate through all subdirectories (fields of law)
    for field_dir in sorted(models_answers_dir.iterdir()):
        if not field_dir.is_dir():
            continue
        
        field_of_law = field_dir.name
        print(f"Processing {field_of_law}...")
        
        # Find all JSON files in this field directory (recursively)
        json_files = list(field_dir.rglob("*.json"))
        
        # Filter out :Zone.Identifier files
        json_files = [f for f in json_files if not f.name.endswith(":Zone.Identifier")]
        
        # Process each JSON file
        for json_file in sorted(json_files):
            questions = process_json_file(json_file, field_of_law)
            all_questions.extend(questions)
            print(f"  Processed {json_file.name}: {len(questions)} questions")
    
    # Write all questions to JSONL file
    print(f"\nWriting {len(all_questions)} questions to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for question in all_questions:
            f.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    print(f"Done! Total questions processed: {len(all_questions)}")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total questions: {len(all_questions)}")
    
    # Count by field of law
    fields = {}
    for q in all_questions:
        field = q["Field of Law"]
        fields[field] = fields.get(field, 0) + 1
    
    print(f"\nQuestions by Field of Law:")
    for field, count in sorted(fields.items()):
        print(f"  {field}: {count}")
    
    # Count by question type
    types = {}
    for q in all_questions:
        q_type = q["Type"]
        types[q_type] = types.get(q_type, 0) + 1
    
    print(f"\nQuestions by Type:")
    for q_type, count in sorted(types.items()):
        print(f"  {q_type}: {count}")


if __name__ == "__main__":
    main()
