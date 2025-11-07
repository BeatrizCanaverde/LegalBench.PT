#!/usr/bin/env python3
"""
Script to match questions from the consolidated JSONL with the HuggingFace dataset,
add ID fields, and verify data consistency.
"""

import json
from pathlib import Path
from datasets import load_dataset, get_dataset_config_names
from typing import Dict, List, Set


def normalize_field_name(field_name: str) -> str:
    """
    Normalize field of law name to match HF config naming convention.
    
    Args:
        field_name: Field of law name from JSONL
    
    Returns:
        Normalized name matching HF config
    """
    # Replace spaces with underscores
    normalized = field_name.replace(" ", "_")
    
    # Special case: handle legacy "Direito Reais" -> "Direitos_Reais" in HF
    if normalized == "Direito_Reais":
        normalized = "Direitos_Reais"
    
    return normalized


def denormalize_field_name(field_name: str) -> str:
    """
    Convert HF config name back to original field name.
    
    Args:
        field_name: HF config name
    
    Returns:
        Original field name
    """
    # Special case: "Direitos_Reais" remains "Direitos Reais" (correct form)
    if field_name == "Direitos_Reais":
        return "Direitos Reais"
    
    # Replace underscores with spaces
    return field_name.replace("_", " ")


def load_jsonl_data(jsonl_path: Path) -> List[Dict]:
    """
    Load data from consolidated JSONL file.
    
    Args:
        jsonl_path: Path to JSONL file
    
    Returns:
        List of question dictionaries
    """
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def load_hf_dataset(dataset_name: str) -> Dict[str, List[Dict]]:
    """
    Load all configs from HuggingFace dataset.
    
    Args:
        dataset_name: Name of the HF dataset
    
    Returns:
        Dictionary mapping field names to lists of questions
    """
    configs = get_dataset_config_names(dataset_name)
    print(f"Loading {len(configs)} configs from HuggingFace dataset...")
    
    hf_data = {}
    for config in configs:
        print(f"  Loading {config}...")
        ds = load_dataset(dataset_name, config, split='test')
        
        # Convert to original field name
        original_field = denormalize_field_name(config)
        hf_data[original_field] = [dict(item) for item in ds]
    
    return hf_data


def normalize_field_for_matching(field_name: str) -> str:
    """
    Normalize field name for matching purposes.
    Legacy "Direito Reais" (incorrect) should match "Direitos Reais" (correct).
    
    Args:
        field_name: Field of law name
    
    Returns:
        Normalized name for matching
    """
    # Normalize legacy "Direito Reais" to correct "Direitos Reais" for matching
    if field_name == "Direito Reais":
        return "Direitos Reais"
    return field_name


def create_question_key(question_dict: Dict) -> str:
    """
    Create a unique key for matching questions.
    Uses Field of Law, Type, Question, and Answer.
    
    Args:
        question_dict: Question dictionary
    
    Returns:
        Unique string key
    """
    # Normalize the field name for consistent matching
    normalized_field = normalize_field_for_matching(question_dict['Field of Law'])
    return f"{normalized_field}||{question_dict['Type']}||{question_dict['Question']}||{str(question_dict['Answer'])}"


def main():
    """
    Main function to match JSONL with HF dataset and create enriched output.
    """
    # Paths
    jsonl_path = Path("/mnt/data-artemis/beatriz/LegalBench.PT/consolidated_model_answers.jsonl")
    output_path = Path("/mnt/data-artemis/beatriz/LegalBench.PT/consolidated_with_ids.jsonl")
    dataset_name = "BeatrizCanaverde/LegalBench.PT"
    
    print("=" * 80)
    print("Loading data...")
    print("=" * 80)
    
    # Load JSONL data
    print(f"\nLoading JSONL from {jsonl_path}...")
    jsonl_data = load_jsonl_data(jsonl_path)
    print(f"Loaded {len(jsonl_data)} questions from JSONL")
    
    # Load HF dataset
    print(f"\nLoading HuggingFace dataset: {dataset_name}")
    hf_data = load_hf_dataset(dataset_name)
    
    # Count total HF questions
    total_hf = sum(len(questions) for questions in hf_data.values())
    print(f"\nLoaded {total_hf} questions from HuggingFace dataset")
    
    print("\n" + "=" * 80)
    print("Creating question indexes...")
    print("=" * 80)
    
    # Create indexes for matching
    jsonl_index = {}
    for item in jsonl_data:
        key = create_question_key(item)
        jsonl_index[key] = item
    
    hf_index = {}
    for field, questions in hf_data.items():
        for item in questions:
            key = create_question_key(item)
            hf_index[key] = item
    
    print(f"\nJSONL unique questions: {len(jsonl_index)}")
    print(f"HF unique questions: {len(hf_index)}")
    
    print("\n" + "=" * 80)
    print("Matching questions...")
    print("=" * 80)
    
    # Find questions only in JSONL
    only_in_jsonl = set(jsonl_index.keys()) - set(hf_index.keys())
    
    # Find questions only in HF
    only_in_hf = set(hf_index.keys()) - set(jsonl_index.keys())
    
    # Find matching questions
    matching = set(jsonl_index.keys()) & set(hf_index.keys())
    
    print(f"\nMatching questions: {len(matching)}")
    print(f"Only in JSONL: {len(only_in_jsonl)}")
    print(f"Only in HF: {len(only_in_hf)}")
    
    # Show sample of mismatches if any
    if only_in_jsonl:
        print("\n⚠️  WARNING: Questions found only in JSONL:")
        for i, key in enumerate(list(only_in_jsonl)[:3]):
            item = jsonl_index[key]
            print(f"\n  {i+1}. Field: {item['Field of Law']}, Type: {item['Type']}")
            print(f"     Question preview: {item['Question'][:100]}...")
        if len(only_in_jsonl) > 3:
            print(f"     ... and {len(only_in_jsonl) - 3} more")
    
    if only_in_hf:
        print("\n⚠️  WARNING: Questions found only in HF:")
        for i, key in enumerate(list(only_in_hf)[:3]):
            item = hf_index[key]
            print(f"\n  {i+1}. Field: {item['Field of Law']}, Type: {item['Type']}, ID: {item['ID']}")
            print(f"     Question preview: {item['Question'][:100]}...")
        if len(only_in_hf) > 3:
            print(f"     ... and {len(only_in_hf) - 3} more")
    
    print("\n" + "=" * 80)
    print("Creating enriched dataset...")
    print("=" * 80)
    
    # Create enriched data by adding IDs to JSONL data
    enriched_data = []
    matched_count = 0
    unmatched_count = 0
    
    for item in jsonl_data:
        key = create_question_key(item)
        
        # Create enriched item with all JSONL fields
        enriched_item = item.copy()
        
        # Try to add ID from HF dataset
        if key in hf_index:
            enriched_item['ID'] = hf_index[key]['ID']
            matched_count += 1
        else:
            enriched_item['ID'] = None
            unmatched_count += 1
        
        enriched_data.append(enriched_item)
    
    print(f"\nEnriched {matched_count} questions with IDs")
    if unmatched_count > 0:
        print(f"⚠️  {unmatched_count} questions could not be matched (ID set to None)")
    
    # Save enriched data
    print(f"\nSaving enriched data to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in enriched_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✓ Saved {len(enriched_data)} questions")
    
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    # Summary by field
    print("\nQuestions by Field of Law:")
    field_stats = {}
    for item in enriched_data:
        field = item['Field of Law']
        field_stats[field] = field_stats.get(field, 0) + 1
    
    for field, count in sorted(field_stats.items()):
        hf_count = len(hf_data.get(field, []))
        match_symbol = "✓" if count == hf_count else "⚠️"
        print(f"  {match_symbol} {field}: {count} (HF: {hf_count})")
    
    # Overall summary
    print("\n" + "=" * 80)
    print("Overall Summary")
    print("=" * 80)
    print(f"Total questions in JSONL: {len(jsonl_data)}")
    print(f"Total questions in HF: {total_hf}")
    print(f"Questions matched: {matched_count}")
    print(f"Questions unmatched: {unmatched_count}")
    
    if matched_count == len(jsonl_data) == total_hf:
        print("\n✓ SUCCESS: All questions matched perfectly!")
    else:
        print("\n⚠️  WARNING: Some questions could not be matched. Please review the output above.")
    
    print("\n" + "=" * 80)
    print(f"Output saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
