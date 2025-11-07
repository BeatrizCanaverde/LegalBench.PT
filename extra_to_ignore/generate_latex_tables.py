import json
import os
from pathlib import Path
from fields import fields_mapping

# Model name mapping to match the table format
MODEL_NAME_MAPPING = {
    "gpt_4o_2024_05_13": "GPT-4o",
    "gpt_4o_mini": "GPT-4o-mini",
    "claude_3_opus_20240229": "Claude-3-Opus",
    "claude_3_5_sonnet_20240620": "Claude-3.5-Sonnet",
    "Meta_Llama_3_1_8B_Instruct_Turbo": "Llama-3.1-8B",
    "Meta_Llama_3_1_70B_Instruct_Turbo": "Llama-3.1-70B",
    "Meta_Llama_3_1_405B_Instruct_Turbo": "Llama-3.1-405B",
    "mistralai__Mixtral_8x7B_Instruct_v0_1": "Mixtral-8x7B"
}

# English to Portuguese field names
FIELD_TRANSLATIONS = {
    "Direito do Ambiente": "Environmental Law",
    "Direito Administrativo": "Administrative Law",
    "Direito Constitucional": "Constitutional Law",
    "Direito da Energia": "Energy Law",
    "Direito das Finanças Públicas": "Public Finance Law",
    "Direito Financeiro": "Financial Law",
    "Direito Fiscal": "Tax Law",
    "Direito Penal": "Criminal Law",
    "Direito Processual Administrativo": "Administrative Procedure Law",
    "Direito Processual Civil": "Civil Procedure Law",
    "Direito Processual Penal": "Criminal Procedure Law",
    "Direito Processual do Trabalho": "Labor Procedure Law",
    "Direito do Urbanismo": "Urban Planning Law",
    "Direito dos Contratos": "Contract Law",
    "Direito da Família": "Family Law",
    "Direito das Obrigações": "Law of Obligations",
    "Direitos Reais": "Property Law",
    "Direito das Sucessões": "Succession Law",
    "Direito Comercial": "Commercial Law",
    "Direito Bancário": "Banking Law",
    "Direito Marítimo": "Maritime Law",
    "Direito das Sociedades Comerciais": "Corporate Law",
    "Direito dos Valores Mobiliários": "Securities Law",
    "Direito dos Transportes": "Transportation Law",
    "Direito Aéreo": "Aviation Law",
    "Direito da Insolvência": "Insolvency Law",
    "Direito Internacional Privado": "Private International Law",
    "Direito do Trabalho": "Labor Law",
    "Direito da Concorrência": "Competition Law",
    "Direito Internacional Público": "Public International",
    "Direito da UE e Comunitário": "EU and Community"
}

# Question types mapping
TYPE_TRANSLATIONS = {
    "Multiple Choice": "Multiple-choice",
    "Cloze Tasks": "Cloze tasks",
    "Case Analysis Questions": "Case analysis",
    "True/False": "True/False",
    "Multiple Selection Questions": "Multiple selection",
    "Matching Questions": "Matching questions"
}


def load_scores(scores_path: Path):
    """Load all score files from the scores directory."""
    scores_data = {}
    
    for file_name in os.listdir(scores_path):
        if not file_name.lower().endswith(".jsonl"):
            continue
        
        # Extract model name from filename
        model_key = file_name.replace(".jsonl", "")
        
        # Skip if not in our mapping
        if model_key not in MODEL_NAME_MAPPING:
            continue
        
        file_path = os.path.join(scores_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content.startswith('['):
                data = json.loads(content)
            else:
                data = json.loads(content)
        
        model_name = MODEL_NAME_MAPPING[model_key]
        scores_data[model_name] = data
    
    return scores_data


def generate_latex_fields_table(scores_data, output_file):
    """Generate LaTeX code for Table 2: Model performance across different fields of law."""
    
    # Model order as in the image
    model_order = ["GPT-4o", "GPT-4o-mini", "Claude-3-Opus", "Claude-3.5-Sonnet", 
                   "Llama-3.1-8B", "Llama-3.1-70B", "Llama-3.1-405B", "Mixtral-8x7B"]
    
    latex = []
    latex.append("% Table 2: Model performance (%) across the different fields of law")
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\small")
    latex.append("\\begin{tabular}{l" + "c" * len(model_order) + "}")
    latex.append("\\toprule")
    
    # Header
    header = "\\textbf{Fields of Law}"
    for model in model_order:
        if model in scores_data:
            header += f" & \\textbf{{{model}}}"
    header += " \\\\"
    latex.append(header)
    latex.append("\\midrule")
    
    # Public section
    line = "\\textbf{Public}"
    for model in model_order:
        if model in scores_data and "Public" in scores_data[model]:
            score = scores_data[model]["Public"]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    # Individual public fields
    for field in fields_mapping["Public"]:
        field_name = FIELD_TRANSLATIONS.get(field, field)
        line = f"~~{field_name}"
        for model in model_order:
            if model in scores_data and field in scores_data[model]:
                score = scores_data[model][field]["Score"] * 100
                line += f" & {score:.1f}"
            else:
                line += " & --"
        line += " \\\\"
        latex.append(line)
    
    latex.append("\\midrule")
    
    # Private section
    line = "\\textbf{Private}"
    for model in model_order:
        if model in scores_data and "Private" in scores_data[model]:
            score = scores_data[model]["Private"]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    # Individual private fields
    for field in fields_mapping["Private"]:
        # Check if any model has data for this field
        has_data = any(field in scores_data.get(model, {}) for model in model_order)
        if not has_data:
            continue
            
        field_name = FIELD_TRANSLATIONS.get(field, field)
        line = f"~~{field_name}"
        for model in model_order:
            if model in scores_data and field in scores_data[model]:
                score = scores_data[model][field]["Score"] * 100
                line += f" & {score:.1f}"
            else:
                line += " & --"
        line += " \\\\"
        latex.append(line)
    
    latex.append("\\midrule")
    
    # Public-Private (Competition Law)
    line = "\\textbf{Public-Private (Competition Law)}"
    for model in model_order:
        if model in scores_data and "Public-Private" in scores_data[model]:
            score = scores_data[model]["Public-Private"]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    latex.append("\\midrule")
    
    # Public International
    line = "\\textbf{Public International}"
    for model in model_order:
        if model in scores_data and "Public Int." in scores_data[model]:
            score = scores_data[model]["Public Int."]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    latex.append("\\midrule")
    
    # EU and Community
    line = "\\textbf{EU and Community}"
    for model in model_order:
        if model in scores_data and "UE" in scores_data[model]:
            score = scores_data[model]["UE"]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    latex.append("\\midrule")
    
    # Overall
    line = "\\textbf{Overall}"
    for model in model_order:
        if model in scores_data and "LegalBench.PT" in scores_data[model]:
            score = scores_data[model]["LegalBench.PT"]["Score"] * 100
            line += f" & {score:.1f}"
        else:
            line += " & --"
    line += " \\\\"
    latex.append(line)
    
    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\caption{Model performance (\\%) across the different fields of law.}")
    latex.append("\\label{tab:fields_performance}")
    latex.append("\\end{table}")
    
    output_file.write("\n".join(latex))
    output_file.write("\n\n")


def generate_latex_types_table(scores_data, output_file):
    """Generate LaTeX code for Table 19: Model performance across different types of questions."""
    
    # Model order as in the image
    model_order = ["GPT-4o", "GPT-4o-mini", "Claude-3-Opus", "Claude-3.5-Sonnet", 
                   "Llama-3.1-8B", "Llama-3.1-70B", "Llama-3.1-405B", "Mixtral-8x7B"]
    
    # Question types order
    question_types = ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", 
                      "True/False", "Multiple Selection Questions", "Matching Questions"]
    
    latex = []
    latex.append("% Table 19: Model performance (%) across the different types of questions")
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\small")
    latex.append("\\begin{tabular}{l" + "c" * len(question_types) + "}")
    latex.append("\\toprule")
    
    # Header
    header = "\\textbf{Models}"
    for qtype in question_types:
        type_name = TYPE_TRANSLATIONS.get(qtype, qtype)
        header += f" & \\textbf{{{type_name}}}"
    header += " \\\\"
    latex.append(header)
    latex.append("\\midrule")
    
    # Data rows
    for model in model_order:
        if model not in scores_data:
            continue
        
        line = model
        for qtype in question_types:
            if qtype in scores_data[model]:
                score = scores_data[model][qtype]["Score"] * 100
                line += f" & {score:.1f}"
            else:
                line += " & --"
        line += " \\\\"
        latex.append(line)
    
    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\caption{Model performance (\\%) across the different types of questions.}")
    latex.append("\\label{tab:types_performance}")
    latex.append("\\end{table}")
    
    output_file.write("\n".join(latex))
    output_file.write("\n\n")


def main():
    scores_path = Path("/mnt/data-artemis/beatriz/LegalBench.PT/scores")
    output_path = Path("/mnt/data-artemis/beatriz/LegalBench.PT/latex_tables.txt")
    
    # Load all scores
    scores_data = load_scores(scores_path)
    
    if not scores_data:
        print("No score files found!")
        return
    
    # Generate LaTeX tables
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write("% LaTeX Tables for LegalBench.PT Results\n")
        output_file.write("% Remember to include \\usepackage{booktabs} in your preamble\n\n")
        
        generate_latex_fields_table(scores_data, output_file)
        generate_latex_types_table(scores_data, output_file)
    
    print(f"\nLaTeX tables generated successfully!")
    print(f"Saved to: {output_path}")
    print(f"Found data for {len(scores_data)} models")
    print("\nRemember to add to your LaTeX preamble:")
    print("  \\usepackage{booktabs}")


if __name__ == "__main__":
    main()
