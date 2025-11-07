#!/bin/bash


# Ensure output directories exist
# mkdir -p outputs evals outputs/logs


# Activate your Python environment
source /mnt/scratch-dionysus/beatriz/venvs/draft/bin/activate


python evaluation.py evaluate_model_answers \
    --input_path /mnt/data-artemis/beatriz/LegalBench.PT/outputs \
    --output_path /mnt/data-artemis/beatriz/LegalBench.PT/evals


python evaluation.py compute_model_scores \
    --input_path /mnt/data-artemis/beatriz/LegalBench.PT/evals \
    --output_path /mnt/data-artemis/beatriz/LegalBench.PT/scores



