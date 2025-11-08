import re
import ast
import os
import json
from collections import defaultdict
from sklearn.metrics import balanced_accuracy_score
import jsonargparse
from fields import fields_mapping, reverse_mapping


def load_jsonl(jsonl_path):
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        content = fh.read().strip()
        # Check if it's a JSON array (starts with '[')
        if content.startswith('['):
            # It's a JSON array, parse it directly
            return json.loads(content)
        else:
            # It's proper JSONL format (one JSON object per line)
            results = []
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                results.append(obj)
            return results
        

def evaluate_model_answers(input_path, output_path):
    for file_name in os.listdir(input_path):
        if not file_name.lower().endswith(".jsonl"):
            continue
        file_path = os.path.join(input_path, file_name)
        content = load_jsonl(file_path)
        for line in content:
            type = line["Type"]
            target_answer = line["Answer"]
            predicted_answer = line["Prediction"]
            if type in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions"]:
                score = eval_multiple_choice(target_answer, predicted_answer)
            elif type == "True/False":
                score = eval_true_false(target_answer, predicted_answer)
            elif type == "Multiple Selection Questions":
                score = eval_multiple_selection_questions(target_answer, predicted_answer)
            else:
                score = eval_matching_questions(target_answer, predicted_answer)
            line["Score"] = score

        os.makedirs(output_path, exist_ok=True)
        out_file = os.path.join(output_path, file_name)
        with open(out_file, 'w', encoding='utf-8') as out:
            json.dump(content, out, ensure_ascii=False, indent=4)
        print(f"Evaluated: {file_name}")


def compute_model_scores(input_path, output_path):
    for file_name in os.listdir(input_path):
        if not file_name.lower().endswith(".jsonl"):
            continue
        file_path = os.path.join(input_path, file_name)
        content = load_jsonl(file_path)

        weighted_sum = 0.0
        stats = defaultdict(lambda: {"Weighted Average": 0.0, "Total Questions": 0})
        pairs_fields_types = sorted({(item["Field of Law"], item["Type"]) for item in content})

        for field, type in pairs_fields_types:
            subset = [f for f in content if f["Field of Law"] == field and f["Type"] == type]

            if type in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False"]:
                target_answers = [f["Answer"] for f in subset]
                predicted_answers = [process(f["Prediction"], type) for f in subset]
                avg_score = balanced_accuracy_score(target_answers, predicted_answers)

            if type in ["Multiple Selection Questions", "Matching Questions"]:
                scores = [f["Score"] for f in subset]
                avg_score = sum(scores) / len(scores) if scores else 0.0

            group = reverse_mapping.get(field)
            num_questions = len(subset)
            weighted_sum = avg_score * num_questions

            stats[field][type] = avg_score
            stats[field]["Weighted Average"] += weighted_sum
            stats[field]["Total Questions"] += num_questions
            stats[type]["Weighted Average"] += weighted_sum
            stats[type]["Total Questions"] += num_questions
            stats[group]["Weighted Average"] += weighted_sum
            stats[group]["Total Questions"] += num_questions
            stats["LegalBench.PT"]["Weighted Average"] += weighted_sum
            stats["LegalBench.PT"]["Total Questions"] += num_questions

        fields = [i[0] for i in pairs_fields_types]
        types = [i[1] for i in pairs_fields_types]
        
        for field in set(fields):
            stats[field]["Score"] = stats[field]["Weighted Average"] / stats[field]["Total Questions"] if stats[field]["Total Questions"] > 0 else 0.0
        
        for type in set(types):
            stats[type]["Score"] = stats[type]["Weighted Average"] / stats[type]["Total Questions"] if stats[type]["Total Questions"] > 0 else 0.0

        for group in fields_mapping.keys():
            stats[group]["Score"] = stats[group]["Weighted Average"] / stats[group]["Total Questions"] if stats[group]["Total Questions"] > 0 else 0.0

        stats["LegalBench.PT"]["Score"] = stats["LegalBench.PT"]["Weighted Average"] / stats["LegalBench.PT"]["Total Questions"] if stats["LegalBench.PT"]["Total Questions"] > 0 else 0.0
        
        out_file = os.path.join(output_path, file_name)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)

        print(f"Scores saved for: {file_name}")


def process(prediction, type):
    if type in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions"]:
        pattern = r'A resposta correta é:?\s*([A-Za-z])'
        match = re.search(pattern, prediction)
        if match:
            guess = match.group(1)
        else:
            guess = ""
        return guess
    elif type == "True/False":
        pattern = r'A afirmação é \s*(falsa|verdadeira)'
        match = re.search(pattern, prediction)
        if match:
            guess = match.group(1).lower()
        else:
            guess = ""
        if guess == "falsa":
            guess = "Falso"
        elif guess == "verdadeira":
            guess = "Verdadeiro"
        return guess
    else:
        return prediction


def eval_matching_questions(target_answer, predicted_answer):
    pattern = re.compile(r'([a-zA-Z])\s*[-)]?\s*(\d)|(\d)\s*[-)]?\s*([a-zA-Z])')
    matches = pattern.findall(predicted_answer)
    guess = []
    target_answer = ast.literal_eval(target_answer)
    for match in matches:
        letter1, digit, digit2, letter2 = match
        if letter1 and digit:
            guess.append([letter1.lower(), digit])
        elif digit2 and letter2:
            guess.append([letter2.lower(), digit2])
    guess = unique_list(guess)
    target_answer = sorted(target_answer)
    guess = sorted(guess)
    f1_score = evaluate_f1(guess, target_answer)
    return f1_score


def eval_multiple_selection_questions(target_answer, predicted_answer):
    pattern = re.compile(r'[^A-Za-z]([A-Za-z])\)')
    guess = pattern.findall(predicted_answer)
    guess = list(set(guess))
    target_answer = ast.literal_eval(target_answer)
    target_answer = sorted([i.lower() for i in target_answer])
    guess = sorted([i.lower() for i in guess])
    f1_score = evaluate_f1(guess, target_answer)
    return f1_score


def eval_multiple_choice(target_answer, predicted_answer):
    pattern = r'A resposta correta é:?\s*([A-Za-z])'
    match = re.search(pattern, predicted_answer)
    if match:
        guess = match.group(1)
    else:
        guess = ""
    if target_answer.lower() == guess.lower():
        return 1
    else:
        return 0


def eval_true_false(target_answer, predicted_answer):
    pattern = r'A afirmação é \s*(falsa|verdadeira)'
    match = re.search(pattern, predicted_answer)
    if match:
        guess = match.group(1).lower()
    else:
        guess = ""
    if guess == "falsa":
        guess = "Falso"
    elif guess == "verdadeira":
        guess = "Verdadeiro"
    if target_answer == guess:
        return 1
    else:
        return 0


def delete_element(lst, number):
    for i,s in enumerate(lst):
        if number == s:
            if i==0:
                return lst[1:]
            elif i==len(lst)-1:
                return lst[:-1]
            else:
                return lst[:i]+lst[i+1:]    
            

def evaluate_f1(GUESS, TRUTH):
    tp = 0
    fp = 0
    fn = 0
    for a in GUESS:
        if a in TRUTH:
            TRUTH = delete_element(TRUTH, a)
            tp += 1
        else:
            fp += 1
    fn = len(TRUTH)
    if tp + fp == 0:
        precision = 0
    else:
        precision = tp/(tp + fp)
    recall = tp/(tp + fn)
    if precision + recall == 0:
        return 0
    else:
        f1 = 2 * precision * recall / (precision + recall)
        return f1
    

def unique_list(original_list):
    unique = []
    for i in original_list:
        if i not in unique:
            unique.append(i)
    return unique




if __name__ == "__main__":
    jsonargparse.CLI(
        [evaluate_model_answers, 
         compute_model_scores
         ], 
        as_positional=False,
    )