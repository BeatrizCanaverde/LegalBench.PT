#!/bin/bash
#SBATCH --job-name=legalbench_pt
#SBATCH --output=outputs/logs/%j.out
#SBATCH --error=outputs/logs/%j.err
#SBATCH --gres=gpu:1
#SBATCH --qos=gpu-debug
#SBATCH --time=01:00:00
#SBATCH --partition=h100


# Activate your Python environment
source /mnt/scratch-dionysus/beatriz/venvs/draft/bin/activate


# Pass SLURM job ID to downstream scripts
export JOB_ID=${SLURM_JOB_ID}


# Define arguments
model_path=meta-llama/Llama-3.1-8B-Instruct
sanitized_model_path=${model_path//\//__}
max_len=1000
temperature=0.001
out_path=outputs/${sanitized_model_path}_${JOB_ID}.jsonl
seed=2025


echo model_path: $model_path
echo max_len: $max_len
echo temperature: $temperature
echo out_path: $out_path
echo seed: $seed


PYTHONPATH=. python generation.py --model_path $model_path --max_len $max_len --temperature $temperature --output_path $out_path --seed $seed

