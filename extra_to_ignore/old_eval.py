#####################################################
############ AVALIAR PERGUNTAS-RESPOSTAS ############
#####################################################

import os, json, re, sys
import csv
from collections import defaultdict

import warnings
warnings.filterwarnings("ignore")

#WHAT = "ULisboa - Faculdade Direito - GPT"
#WHAT = "regimes_juridicos_gpt"

#if len(sys.argv)==2:
#    MODELO = sys.argv[1]
#else:
#    MODELO = None


#### MODELOS
# "Meta-Llama-3.1-8B-Instruct-Turbo"
# "mistralai/Mistral-7B-Instruct-v0.3"
# "mistralai/Mixtral-8x7B-Instruct-v0.1"
# "gpt-4o"
# "claude-3-5-sonnet-20240620"
# "claude-3-opus-20240229"


#start_path = "/home/beatrizcanaverde/{}/tudo/{}_answers/".format(WHAT, MODELO)
#base_dir = "/home/beatrizcanaverde/ULisboa - Faculdade Direito - GPT/tudo/avaliacao/models_answers"
#base_dir = "/home/beatrizcanaverde/ULisboa - Faculdade Direito - GPT/tudo/avaliacao/models_answers" # _3_DADOS
#irrelevantes_path = "/home/beatrizcanaverde/ULisboa - Faculdade Direito - GPT/tudo/avaliacao/irrelevantes_gpt"


    

def delete_idx(lst,idx):
    if idx == 0:
        return lst[1:]
    elif idx == len(lst)-1:
        return lst[:-1]
    else:
        return lst[:idx]+lst[idx+1:]
    

def delete_element(lst, number):
    for i,s in enumerate(lst):
        if number == s:
            if i==0:
                return lst[1:]
            elif i==len(lst)-1:
                return lst[:-1]
            else:
                return lst[:i]+lst[i+1:]    


def evaluate_f1(GUESS, TRUTH): #  """For SSLA evaluation tasks, we measure F1."""

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

    #if tp + fn == 0:
    #    recall = 0
    #else:
    recall = tp/(tp + fn)

    if precision + recall == 0:
        return precision, recall, 0
    else:
        f1 = 2 * precision * recall / (precision + recall)
        return precision, recall, f1


def unique_list(original_list):
    unique = []
    for i in original_list:
        if i not in unique:
            unique.append(i)
    return unique


#results = {"Meta-Llama-3.1-8B-Instruct-Turbo":[]}
types = ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]

#for model in list(results.keys()):
#    for tp in types:
#        results[model][tp] = [0,0]

#results = {"Multiple Choice": [0,0], "Cloze Tasks": [0,0], "True/False": [0,0], "Matching Questions": [0,0], "Multiple Selection Questions": [0,0], "Case Analysis Questions": [0,0]}

#results = {"sem":{}, "meio":{}, "chat":{}}

#for cs in list(results.keys()):
#    for tp in types:
#        results[cs][tp] = [0,0]

#number_of_correct_questions = 0
#number_of_total_questions = 0
#questions_by_folder = {}

#pattern1 = re.compile(r'(?<!^)\d+(?![\.\)])', re.IGNORECASE)
#pattern2 = re.compile(r'n\.º|nº|[^a-zA-Z]artigo[^a-zA-Z]|[^a-zA-Z]artigos[^a-zA-Z]|[^a-zA-Z]art[^a-zA-Z]|[^a-zA-Z]reg[^a-zA-Z]', re.IGNORECASE)

question_id_counter = 0
#results_csv = []

# ['Direito dos Contratos', 'Direito da Família', 'Direito Processual Administrativo']: #
# ['Direito dos Contratos', 'Direito da Família', 'Direito das Obrigações', 'Direito Reais', 'Direito das Sucessões']: #
# ['Direito dos Contratos', 'Direito da Família', 'Direito das Obrigações', 'Direito Reais', 'Direito das Sucessões', 'Direito Processual Administrativo']: # 

# ['Direito dos Contratos', 'Direito da Família', 'Direito das Obrigações', 'Direito Reais', 'Direito das Sucessões']: #
# ['Direito Administrativo', 'Direito Processual Civil', 'Direito da Família', 'Direito Comercial', 'Direito Internacional Público', 'Direito da UE e Comunitário']: #

#v = 0
#f = 0

#type_stats = defaultdict(lambda: defaultdict(int)) 





from sklearn.metrics import balanced_accuracy_score


category_mapping = {'Public':['Direito do Ambiente',
                        'Direito Administrativo',
                        'Direito Constitucional',
                        'Direito da Energia',
                        'Direito das Finanças Públicas',
                        'Direito Financeiro',
                        'Direito Fiscal',
                        'Direito Penal',
                        'Direito Processual Administrativo',
                        'Direito Processual Civil',
                        'Direito Processual Penal',
                        'Direito Processual do Trabalho',
                        'Direito do Urbanismo'],
                    'Private':['Direito dos Contratos',
                            'Direito da Família',
                            'Direito das Obrigações',
                            'Direito Reais',
                            'Direito das Sucessões',
                            'Direito Comercial',
                            'Direito Bancário',
                            'Direito Marítimo',
                            'Direito das Sociedades Comerciais',
                            'Direito dos Valores Mobiliários',
                            'Direito dos Transportes',	
                            'Direito Aéreo',
                            'Direito da Insolvência',
                            'Direito Internacional Privado',
                            'Direito do Trabalho'],
                    'Public-Private':['Direito da Concorrência'],
                    'Public Int.':['Direito Internacional Público'],
                    'UE':['Direito da UE e Comunitário']}

categories = ['Direito do Ambiente',
            'Direito Administrativo',
            'Direito Constitucional',
            'Direito da Energia',
            'Direito das Finanças Públicas',
            'Direito Financeiro',
            'Direito Fiscal',
            'Direito Penal',
            'Direito Processual Administrativo',
            'Direito Processual Civil',
            'Direito Processual Penal',
            'Direito Processual do Trabalho',
            'Direito do Urbanismo',
            'Direito dos Contratos',
            'Direito da Família',
            'Direito das Obrigações',
            'Direito Reais',
            'Direito das Sucessões',
            'Direito Comercial',
            'Direito Bancário',
            'Direito Marítimo',
            'Direito das Sociedades Comerciais',
            'Direito dos Valores Mobiliários',
            'Direito dos Transportes',	
            'Direito Aéreo',
            'Direito da Insolvência',
            'Direito Internacional Privado',
            'Direito do Trabalho',
            'Direito da Concorrência',
            'Direito Internacional Público',
            'Direito da UE e Comunitário']


CLAUDE_CATEGORIES = ['Direito Administrativo',
                     'Direito Processual Civil',
                     'Direito da Família',
                     'Direito Comercial',
                     'Direito Internacional Público',
                     'Direito da UE e Comunitário']


MODELS_LIST = ["gpt-4o-2024-05-13",
            "gpt-4o-mini",
            "claude-3-opus-20240229",
            "claude-3-5-sonnet-20240620",
            "Meta-Llama-3.1-8B-Instruct-Turbo",
            "Meta-Llama-3.1-70B-Instruct-Turbo",
            "Meta-Llama-3.1-405B-Instruct-Turbo",
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
            ]


#category_mapping = {'Total': ['Direito Administrativo', 'Direito Processual Civil', 'Direito da Família', 'Direito Comercial', 'Direito Internacional Público', 'Direito da UE e Comunitário']}

# for something in ['a list of somethings']:
#for key, value in category_mapping.items(): # for category in category_mapping['Total']: #

base_dir = "/home/beatrizcanaverde/ULisboa - Faculdade Direito - GPT/tudo/avaliacao/models_answers" # _3_DADOS

type_stats = defaultdict(lambda: defaultdict(int)) 
TYPES = True

models_dict = defaultdict(lambda: defaultdict(dict))

#categories = CLAUDE_CATEGORIES
category_mapping['Tudo'] = categories
categories_dict = {name: 0 for name in categories}

distribution_categories_types = defaultdict(lambda: defaultdict(int))

for MODELO in MODELS_LIST:
        
    for folder_name in categories: #category_mapping['Total']: #value: # os.listdir(base_dir): # category_mapping['Total']: #

        #results = {"sem":{}, "meio":{}, "chat":{}}

        #for cs in list(results.keys()):
        #    for tp in types:
        #        results[cs][tp] = [0,0]

        #number_of_correct_questions = 0
        number_of_total_questions = 0
        #questions_by_folder = {}

        #results_csv = []

        correct_answers = {
            "Multiple Choice": [],
            "Cloze Tasks": [],
            "Case Analysis Questions": [],
            "True/False": [],
            "Multiple Selection Questions": [],
            "Matching Questions": []
        }

        guess_answers = {
            "Multiple Choice": [],
            "Cloze Tasks": [],
            "Case Analysis Questions": [],
            "True/False": [],
            "Multiple Selection Questions": [],
            "Matching Questions": []
        }

        #questions_by_folder[folder_name] = [number_of_total_questions, number_of_correct_questions]
        folder_path = os.path.join(base_dir, folder_name)

        for cs in os.listdir(folder_path):

            model_answers_path = os.path.join(folder_path, cs)

            for filename in os.listdir(model_answers_path):
                #print(folder_name, filename)

                # "chat", "com", "meio", "sem"
                #if exclude(filename, "sem"): # pôr aqui como argumento o que eu quero avaliar
                #    continue

                #if MODELO == "Meta-Llama-3.1-405B-Instruct-Turbo":
                #    file_path = os.path.join(model_answers_path.replace("models_answers/", "models_answers_3_DADOS/"), filename)
                #else:
                file_path = os.path.join(model_answers_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                #for tuple in data:
                #    q = extract_question(tuple[1])
                #    if pattern1.search(q):
                #        if pattern2.search(q):
                #            print(q)
                #            print()

                #irrelevantes_file_path = os.path.join(os.path.join(os.path.join(irrelevantes_path, folder_name), cs), filename)
                #list_questions, irrelevantes = update_irrelevantes(data, cs, irrelevantes_file_path)
                #data = list_questions
                #data = irrelevantes

                position = 0
                for tp, question, answer, models_dictionary in data:
                    
                    #try:
                    model_answer = models_dictionary[MODELO]
                    #except:
                    #    model_answer = ''

                    #for model, model_answer in models_dictionary.items():
                        
                    #if model not in MODELS_LIST:
                    #    continue
                    #print('HEY!')
                    
                    #if MODELO:
                    #    if model != MODELO:
                    #        continue
                    #else:
                        #if model not in ["claude-3-opus-20240229", "gpt-4o"]: # ["mistralai/Mistral-7B-Instruct-v0.3"]: # "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    #    if model in ["mistralai/Mistral-7B-Instruct-v0.3"]: # "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    #        continue
                        
                    if "Multiple Choice" == tp:
                        #print(filename, "Multiple Choice")

                        #type_stats[tp][answer] += 1

                        #if answer == "a":
                        #    continue

                        pattern = r'A resposta correta é:?\s*([A-Za-z])'
                        match = re.search(pattern, model_answer)
                        if match:
                            guess = match.group(1).lower()
                        else:
                            guess = ""
                        
                        number_of_total_questions += 1
                        #results[cs]["Multiple Choice"][1] += 1

                        #if answer == guess:
                        #    number_of_correct_questions += 1
                        #    results[cs]["Multiple Choice"][0] += 1  

                        correct_answers["Multiple Choice"].append(answer.lower())
                        guess_answers["Multiple Choice"].append(guess.lower())

                        if TYPES:
                            type_stats[tp][answer.lower()] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1


                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, answer == guess])
                        #if not answer == guess:
                        #    print(answer, '--', guess, answer == guess)
                        #print(answer, guess, answer == guess)
                        #print(model_answer, guess)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)


                    elif "Cloze Tasks" == tp:                        
                        #print(filename, "Cloze Tasks")

                        #type_stats[tp][answer] += 1

                        #if answer == "a":
                        #    continue

                        pattern = r'A resposta correta é:?\s*([A-Za-z])'
                        match = re.search(pattern, model_answer)
                        if match:
                            guess = match.group(1).lower()
                        else:
                            guess = ""
                        
                        number_of_total_questions += 1
                        #results[cs]["Cloze Tasks"][1] += 1

                        #if answer == guess:
                        #    number_of_correct_questions += 1
                        #    results[cs]["Cloze Tasks"][0] += 1

                        correct_answers["Cloze Tasks"].append(answer.lower())
                        guess_answers["Cloze Tasks"].append(guess.lower())

                        if TYPES:
                            type_stats[tp][answer.lower()] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1
    
                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, answer == guess])
                        #if not answer == guess:
                        #    print(answer, '--', guess, answer == guess)
                        #print(answer, guess, answer == guess)
                        #print(model_answer, guess)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)

                    elif "True/False" == tp:
                        #print(filename, "True/False")

                        #type_stats[tp][answer] += 1
                        #if answer == "Falso":
                        #    continue
                        pattern = r'A afirmação é \s*(falsa|verdadeira)'
                        match = re.search(pattern, model_answer) #, re.IGNORECASE)
                        if match:
                            guess = match.group(1).lower()
                        else:
                            guess = ""
                        
                        if guess == "falsa":
                            guess = "Falso"
                            #f += 1
                        elif guess == "verdadeira":
                            guess = "Verdadeiro"
                            #v += 1

                        number_of_total_questions += 1
                        #results[cs]["True/False"][1] += 1
                        
                        #if answer == guess:
                        #    number_of_correct_questions += 1
                        #    results[cs]["True/False"][0] += 1

                        correct_answers["True/False"].append(answer)
                        guess_answers["True/False"].append(guess)

                        if TYPES:
                            type_stats[tp][answer.lower()] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1

                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, answer == guess])
                        #if not answer == guess:
                        #    print(answer, '--', guess, answer == guess)
                        #print(answer, guess, answer == guess)
                        #print(model_answer, guess)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)

                    elif "Matching Questions" == tp:
                        #print(filename, "Matching Questions")

                        #type_stats[tp][0] += 1

                        #print(model_answer)
                        pattern = re.compile(r'([a-zA-Z])\s*[-)]?\s*(\d)|(\d)\s*[-)]?\s*([a-zA-Z])') #   r'([a-z])\s*-\s*(\d)'   r'(\d)-?([a-z])|([a-z])-?(\d)'
                        matches = pattern.findall(model_answer) #.lower())
                        guess = []
                        for match in matches:
                            letter1, digit, digit2, letter2 = match
                            if letter1 and digit:
                                guess.append([letter1.lower(), digit])
                            elif digit2 and letter2:
                                guess.append([letter2.lower(), digit2])
                        guess = unique_list(guess)                        
                        #guess = [list(item) for item in guess]
                        #guess = [list(t) for t in set(tuple(pair) for pair in guess)]
                        #a)3, b)2, c)2, d)4
                        number_of_total_questions += 1
                        #results[cs]["Matching Questions"][1] += 1

                        #if sorted(answer) == sorted(guess):
                        #    number_of_correct_questions += 1
                        #    results[cs]["Matching Questions"][0] += 1

                        correct_answers["Matching Questions"].append(sorted(answer))
                        guess_answers["Matching Questions"].append(sorted(guess))

                        if TYPES:
                        #    type_stats[tp]['number of questions'] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1

                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, sorted(answer) == sorted(guess)])
                        #if not sorted(answer) == sorted(guess):
                        #    print(answer, '--', guess, sorted(answer) == sorted(guess))
                        #print(answer, guess, sorted(answer) == sorted(guess))
                        #print(model_answer, guess)
                        #print(model_answer, ' - ', guess, ' - ', answer)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)

                    elif "Multiple Selection Questions" == tp:
                        #print(filename, "Multiple Selection Questions")

                        #type_stats[tp][str(answer)] += 1

                        #print(model_answer)
                        pattern = re.compile(r'[^A-Za-z]([A-Za-z])\)')
                        guess = pattern.findall(model_answer) #.lower())
                        guess = list(set(guess))

                        number_of_total_questions += 1
                        #results[cs]["Multiple Selection Questions"][1] += 1

                        #print(answer, '--', guess, sorted(answer) == sorted(guess))
                        
                        #if sorted(answer) == sorted(guess):
                        #    number_of_correct_questions += 1
                        #    results[cs]["Multiple Selection Questions"][0] += 1

                        correct_answers["Multiple Selection Questions"].append(sorted([i.lower() for i in answer]))
                        guess_answers["Multiple Selection Questions"].append(sorted([i.lower() for i in guess]))

                        if TYPES:
                            for i in answer:
                                type_stats[tp][i.lower()] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1

                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, sorted(answer) == sorted(guess)])
                        #if not sorted(answer) == sorted(guess):
                        #    print(answer, '--', guess, sorted(answer) == sorted(guess))
                        #print(answer, guess, sorted(answer) == sorted(guess))
                        #print(model_answer, guess)
                        #print(model_answer, ' - ', guess, ' - ', answer)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)

                    elif "Case Analysis Questions" == tp:
                        #print(filename, "Case Analysis Questions")

                        #type_stats[tp][answer] += 1

                        #if answer == "a":
                        #    continue

                        pattern = r'A resposta correta é:?\s*([A-Za-z])'
                        match = re.search(pattern, model_answer)
                        if match:
                            guess = match.group(1).lower()
                        else:
                            guess = ""

                        number_of_total_questions += 1
                        #results[cs]["Case Analysis Questions"][1] += 1
                        
                        #if answer == guess:
                        #    number_of_correct_questions += 1
                        #    results[cs]["Case Analysis Questions"][0] += 1

                        correct_answers["Case Analysis Questions"].append(answer.lower())
                        guess_answers["Case Analysis Questions"].append(guess.lower())

                        if TYPES:
                            type_stats[tp][answer.lower()] += 1
                            type_stats[tp]['Total Perguntas'] += 1
                            categories_dict[folder_name] += 1
                            distribution_categories_types[folder_name][tp] += 1
                            distribution_categories_types[folder_name]['Total'] += 1

                        #results_csv.append([question_id_counter, folder_name, cs, filename, position, tp, question, answer, model, answer == guess])
                        #if not answer == guess:
                        #    print(answer, '--', guess, answer == guess)
                        #print(answer, guess, answer == guess)
                        #print(model_answer, guess)

                        #if folder_name == 'Direito dos Transportes':
                        #    print(model_answer, ' - ', guess, ' - ', answer)

                    question_id_counter += 1
                    position += 1

        #questions_by_folder[folder_name][0] = number_of_total_questions - questions_by_folder[folder_name][0]
        #questions_by_folder[folder_name][1] = number_of_correct_questions - questions_by_folder[folder_name][1]



        # Variables to store total score and total number of questions
        weighted_sum = 0
        total_questions = 0
        types_summary = defaultdict(dict)

        # Balanced Accuracy for first set of question types
        for q_type in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False"]:
            if correct_answers[q_type]:
                # Calculate balanced accuracy
                bal_acc = balanced_accuracy_score(correct_answers[q_type], guess_answers[q_type])
                #print(f"Balanced Accuracy for {q_type}: {round(bal_acc, 3)*100}")
                
                # Number of questions for this type
                num_questions = len(correct_answers[q_type])
                #print(num_questions)
                # Add weighted score to the total
                weighted_sum += bal_acc * num_questions
                total_questions += num_questions
                types_summary[q_type]['Balanced Accuracy'] = bal_acc
                types_summary[q_type]['Total Perguntas'] = num_questions

        # F1 Score for Multiple Selection Questions
        precision_list = []
        recall_list = []
        f1_list = []
        if correct_answers["Multiple Selection Questions"]:
            for i in range(len(correct_answers["Multiple Selection Questions"])):
                precision, recall, f1 = evaluate_f1(guess_answers["Multiple Selection Questions"][i], correct_answers["Multiple Selection Questions"][i])
                precision_list.append(precision)
                recall_list.append(recall)
                f1_list.append(f1)
            
            # Calculate average F1 score
            precision_avg = sum(precision_list) / len(precision_list)
            recall_avg = sum(recall_list) / len(recall_list)
            f1_avg = sum(f1_list) / len(f1_list)
            #print(f"F1 Score for Multiple Selection Questions: {round(f1_avg, 3)*100}")
            
            # Number of questions for this type
            num_questions = len(correct_answers["Multiple Selection Questions"])
            #print(num_questions)

            # Add weighted F1 score to the total
            weighted_sum += f1_avg * num_questions
            total_questions += num_questions
            types_summary["Multiple Selection Questions"]['Precision'] = precision_avg
            types_summary["Multiple Selection Questions"]['Recall'] = recall_avg
            types_summary["Multiple Selection Questions"]['F1'] = f1_avg
            types_summary["Multiple Selection Questions"]['Total Perguntas'] = num_questions


       # F1 Score for Matching Questions
        precision_list = []
        recall_list = []
        f1_list = []
        if correct_answers["Matching Questions"]:
            for i in range(len(correct_answers["Matching Questions"])):
                precision, recall, f1 = evaluate_f1(guess_answers["Matching Questions"][i], correct_answers["Matching Questions"][i])
                precision_list.append(precision)
                recall_list.append(recall)
                f1_list.append(f1)
            
            # Calculate average F1 score
            precision_avg = sum(precision_list) / len(precision_list)
            recall_avg = sum(recall_list) / len(recall_list)
            f1_avg = sum(f1_list) / len(f1_list)
            #print(f"F1 Score for Multiple Selection Questions: {round(f1_avg, 3)*100}")
            
            # Number of questions for this type
            num_questions = len(correct_answers["Matching Questions"])
            #print(num_questions)

            # Add weighted F1 score to the total
            weighted_sum += f1_avg * num_questions
            total_questions += num_questions
            types_summary["Matching Questions"]['Precision'] = precision_avg
            types_summary["Matching Questions"]['Recall'] = recall_avg
            types_summary["Matching Questions"]['F1'] = f1_avg
            types_summary["Matching Questions"]['Total Perguntas'] = num_questions

        # Accuracy for Matching Questions
        #total = 0
        #correct = 0
        #for cs in list(results.keys()):
        #    total += results[cs]["Matching Questions"][1]
        #    correct += results[cs]["Matching Questions"][0]

        #if total > 0:
        #    matching_acc = correct / total
            #print(f"Matching Questions Accuracy: {round(matching_acc, 3)*100}")
            
            # Add weighted accuracy to the total
        #    weighted_sum += matching_acc * total
        #    total_questions += total

        # Calculate the overall balanced average score
        if total_questions > 0:
            overall_score = weighted_sum / total_questions
            #print(total_questions)
            #print(f"Overall Balanced Average Score: {round(overall_score, 3)*100}")
            #print(f"{folder_name}: {round(overall_score*100, 1)}")
            #print(f"{round(overall_score*100, 1)}")
            types_summary["Overall"]['Weighted Average'] = overall_score
            types_summary["Overall"]['Total Perguntas'] = total_questions
        else:
            print("No questions found across the types.")


        #print(type(models_dict[MODELO]))

        models_dict[MODELO][folder_name] = types_summary

    TYPES = False


models_overleaf = defaultdict(str)
for model, model_dict in models_dict.items():
    print(model)
    total_perguntas = 0
    for folder_name, types_summary in model_dict.items():
        print(folder_name, ' - ', round(types_summary["Overall"]['Weighted Average']*100, 1))
        total_perguntas += types_summary["Overall"]['Total Perguntas']
    print(total_perguntas)
    print()


#### NÚMEROS PERGUNTAS POR CATEGORIA
print('NÚMEROS PERGUNTAS POR CATEGORIA')
total = 0
for category, number in categories_dict.items():
    print(category, ' - ', number)
    total += number
print(total)
print()


#### TABELA: CATEGORIAS VS MODELOS (check order in MODELS_LIST)
print('CATEGORIAS VS MODELOS')
categories_overleaf = defaultdict(str)
for category in categories:
    for model in MODELS_LIST:
        categories_overleaf[category] += " & " + str(round(models_dict[model][category]["Overall"]['Weighted Average']*100, 1))
for category, line in categories_overleaf.items():
    print(f"{category}: {line}")
    #pass
print()


#tp = None
#### TABELA: PUBLIC, PRIVATE VS MODELS (check order in MODELS_LIST)
print('PUBLIC, PRIVATE VS MODELS')
groups_overleaf = defaultdict(str)
for model in MODELS_LIST:
    for group, group_list in category_mapping.items():
        if group not in ['Public', 'Private', 'Tudo']:
            continue
        weighted_sum = 0
        total_questions = 0
        for category in group_list:
            for tp in types:
                if models_dict[model][category]:
                    if models_dict[model][category][tp]:
                        #print(tp)
                        num_questions = models_dict[model][category][tp]['Total Perguntas']
                        if tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False"]:
                            weighted_sum += models_dict[model][category][tp]['Balanced Accuracy'] * num_questions
                        else:
                            weighted_sum += models_dict[model][category][tp]['F1'] * num_questions
                        total_questions += num_questions
        groups_overleaf[group] += " & " + str(round((weighted_sum / total_questions) * 100, 1))
for model, line in groups_overleaf.items():
    print(f"{model}: {line}")
    #pass
print()


#### TABELA: MODELOS VS TYPES (check order in types)
print('MODELOS VS TYPES')
types_overleaf = defaultdict(str)
precision_dict = defaultdict(lambda: defaultdict(str))
recall_dict = defaultdict(dict)
for model in MODELS_LIST:
    for tp in types:
        weighted_sum = 0
        total_questions = 0
        precision_weighted = 0
        precision_total = 0
        recall_weighted = 0
        recall_total = 0
        for category in categories:
            if models_dict[model][category][tp]:
                num_questions = models_dict[model][category][tp]['Total Perguntas']
                if tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False"]:
                    weighted_sum += models_dict[model][category][tp]['Balanced Accuracy'] * num_questions
                else:
                    weighted_sum += models_dict[model][category][tp]['F1'] * num_questions
                    precision_weighted += models_dict[model][category][tp]['Precision'] * num_questions
                    recall_weighted += models_dict[model][category][tp]['Recall'] * num_questions
                total_questions += num_questions
                precision_total += num_questions
                recall_total += num_questions
        types_overleaf[model] += " & " + str(round((weighted_sum / total_questions) * 100, 1))
        if tp in ["Multiple Selection Questions", "Matching Questions"]:
            precision_dict[model][tp] += " & " + str(round((precision_weighted / precision_total) * 100, 1))
            precision_dict[model][tp] += " & " + str(round((recall_weighted / recall_total) * 100, 1))
for model, line in types_overleaf.items():
    print(f"{model}: {line}")
    #pass
print(total_questions)
print()

print('MATCHING: PREC, REC')
for model, line in precision_dict.items():
    print(model)
    print(dict(line))
    #pass
print(total_questions)
print()

#print('MULTIPLE: PREC, REC')
#for model, line in recall_dict.items():
#    print(f"{model}: {line}")
    #pass
#print(total_questions)
#print()


#### TYPES: CLASS DISTRIBUTION
print('TYPES: CLASS DISTRIBUTION')
for q_type, answer_counts in type_stats.items():
    print(f"\nType: {q_type}")
    for answer, count in answer_counts.items():
        if answer == "Total Perguntas":
            continue
        print(f"Answer: {answer}, Count: {count}")
        #pass
    print(answer_counts['Total Perguntas'])
print()



print('DISTRIBUIÇÃO CATEGORIAS X TIPOS')
types_categories = defaultdict(str)
public = defaultdict(int)
private = defaultdict(int)
totaltotal = defaultdict(int)
for folder_name, folder_dict in distribution_categories_types.items():
    for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
        if tp in folder_dict.keys():
            types_categories[folder_name] += " & " + str(round((folder_dict[tp] / folder_dict['Total']) * 100, 1))
        else:
            types_categories[folder_name] += " & " + str(0)
        totaltotal[tp] += folder_dict[tp]
        totaltotal['Total'] += folder_dict[tp]
    if folder_name in category_mapping['Public']:
        for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
            if tp in folder_dict.keys():
                public[tp] += folder_dict[tp]
                public['Total'] += folder_dict[tp]
    if folder_name in category_mapping['Private']:
        for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
            if tp in folder_dict.keys():
                private[tp] += folder_dict[tp]
                private['Total'] += folder_dict[tp]
    print(folder_name, ' - ', types_categories[folder_name])

print('PUBLIC')
for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
    print(tp, ' - ', round((public[tp] / public['Total']) * 100, 1))

print('PRIVATE')
for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
    print(tp, ' - ', round((private[tp] / private['Total']) * 100, 1))

print('OVERALL')
for tp in ["Multiple Choice", "Cloze Tasks", "Case Analysis Questions", "True/False", "Multiple Selection Questions", "Matching Questions"]:
    print(tp, ' - ', round((totaltotal[tp] / totaltotal['Total']) * 100, 1))















def exclude(filename, wanted):
    all_list = ["chat", "meio", "sem"]
    list_to_exclude = [item for item in all_list if item != wanted]
    for item in list_to_exclude:
        if item in filename:
            return True
    return False

def extract_question(text):
    pattern = r'Pergunta:\n(.*?)\n\n\nO output'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        pattern = r'Pergunta:\n(.*?)\n\n\nO teu output'
        match = re.search(pattern, text, re.DOTALL)        
        if not match:
            pattern = r'Afirmação:\n(.*?)\n\n\nO output'
            match = re.search(pattern, text, re.DOTALL)
            return match.group(1).strip()
        else:
            return match.group(1).strip()
    else:
        return match.group(1).strip()

def extract_from_irrelevantes(data, cs):
    list_questions = []
    if cs == "sem":
        for t,q,a in data:
            list_questions.append(q.strip())
    elif cs == "meio":
        qa = data['QA']
        for t,q,a in qa:
            list_questions.append(q.strip())
    elif cs == "chat":
        perguntas = data['Perguntas']
        for pergunta in perguntas:
            qa = pergunta['QA']            
            for t,q,a in qa:
                list_questions.append(q.strip())
    return list_questions   

def update_irrelevantes(data, cs, file_path):
    if cs == "sem":
        return data, []
    elif not os.path.exists(file_path):
        return [], data
    else:
        list_questions = []
        irrelevantes = []
        with open(file_path, 'r', encoding='utf-8') as file:
            data_irrelevantes = json.load(file)
        data_irrelevantes = extract_from_irrelevantes(data_irrelevantes, cs)
        for tuple in data:
            if extract_question(tuple[1]) in data_irrelevantes:
                list_questions.append(tuple)
            else:
                irrelevantes.append(tuple)
        return list_questions, irrelevantes