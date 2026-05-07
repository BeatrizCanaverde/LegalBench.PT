# LegalBench.PT

LegalBench.PT is the first comprehensive legal benchmark specifically designed for the European Portuguese context. It assesses large language models' legal knowledge and reasoning abilities across key areas of the Portuguese law.

📄 Paper: https://arxiv.org/abs/2502.16357

🤗 Dataset: https://huggingface.co/datasets/BeatrizCanaverde/LegalBench.PT

## About

LegalBench.PT provides a rigorous evaluation framework that:

- **Covers 31 fields of law**, grouped into 5 main/broader areas
- **Includes 6 diverse question types** that allow for an automated evaluation:
  - **Multiple-Choice**: Questions with only one correct option
  - **Cloze Tasks**: Fill-in-the-blank exercises formulated as multiple-choice
  - **Case Analysis**: Multiple-choice questions. The difference from the former type is solely related to the exam questions used to create them. Case analysis questions were created from theoretical exercises, while multiple-choice were created from practical problems.
  - **True/False**: Classification of statements as either "True" or "False"
  - **Multiple Selection**: Multiple-choice questions where more than one option can be correct
  - **Matching Questions**: Require respondents to pair items from two columns


## Installation

Install the required dependencies:

```
pip install -r requirements.txt
```


## Usage

### 1. Generate Model Predictions

Run your model on LegalBench.PT to generate predictions:

```
python generation.py \
    --model_path <path_to_your_model> \
    --max_len 1000 \
    --temperature 0.001 \
    --output_path <path_to_save_predictions.jsonl> \
    --seed 42
```

`max_len`, `temperature`, and `seed` can be omitted above.


### 2. Evaluate Model Answers

Evaluate the generated predictions against the ground truth:

```
python evaluation.py evaluate_model_answers \
    --input_path <folder_path_with_predictions> \
    --output_path <folder_path_to_save_evaluations>
```

### 3. Compute Model Scores

Calculate aggregate scores across all evaluations:

```
python evaluation.py compute_model_scores \
    --input_path <folder_path_to_save_evaluations> \
    --output_path <folder_path_to_save_aggregated_scores>
```

## Citation

Please cite the following paper if you use LegalBench.PT in your work:
```bibtex
@misc{canaverde2025legalbenchptbenchmarkportugueselaw,
      title={LegalBench.PT: A Benchmark for Portuguese Law}, 
      author={Beatriz Canaverde and Telmo Pessoa Pires and Leonor Melo Ribeiro and André F. T. Martins},
      year={2025},
      eprint={2502.16357},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={}, 
}
```
