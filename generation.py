import json
import argparse
import random
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from datasets import load_dataset
from fields import fields


def main(args):

    random.seed(args.seed)

    # Load the dataset
    dataset = []
    for field in fields:
        ds = load_dataset("BeatrizCanaverde/LegalBench.PT", subset=field.replace(" ", "_"), split="test")
        dataset.extend(ds)

    # Load the model and tokenizer
    model_path = args.model_path
    llm = LLM(model=model_path, seed=args.seed, max_model_len=args.max_len)

    messages = []
    for instance in dataset:
        messages.append([{"role": "user", "content": instance["Question"]}])

    sampling_params = SamplingParams(temperature=args.temperature, max_tokens=args.max_len)
    outputs = llm.chat(messages, sampling_params)

    for i, output in enumerate(outputs):
        out_txt = output.outputs[0].text
        dataset[i]["Prediction"] = out_txt
        
    with open(args.output_path, 'w') as out:
            out.write(json.dumps(dataset, ensure_ascii=False) + '\n')

    print(f"Model outputs saved to: {args.output_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate model outputs for LegalBench.PT.")

    parser.add_argument('--model_path', type=str, required=True, help='Path to the model.')
    parser.add_argument('--max_len', type=int, default=1000, help='Maximum length of input sequences.')
    parser.add_argument('--temperature', type=float, default=0.001, help='Sampling temperature.')
    parser.add_argument('--output_path', type=str, required=True, help='Path to the output file.')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility.')

    args = parser.parse_args()

    main(args)
