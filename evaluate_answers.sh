#!/bin/bash


LOGDIR="/mnt/data-artemis/beatriz/LegalBench.PT/evals/logs"
mkdir -p "$LOGDIR"


# Ensure output directories exist
# mkdir -p outputs evals outputs/logs


# Activate your Python environment
source /mnt/scratch-dionysus/beatriz/venvs/draft/bin/activate


python evaluation.py evaluate_model_answers \
    --input_path /mnt/data-artemis/beatriz/LegalBench.PT/outputs \
    --output_path /mnt/data-artemis/beatriz/LegalBench.PT/evals \
    "$LOGDIR/evaluation.stdout" 2>"$LOGDIR/evaluation.stderr"

