from functools import cache
from datasets import load_dataset
import re


@cache
def _get_standardized_diseases():
    df = load_dataset("ezuruce/medical-kaggle-dataset-cleaned", split='train').to_pandas()
    diseases = df.prognosis.unique()
    diseases = [disease.lower() for disease in diseases]
    return diseases


def extract_disease_name(text):
    # This pattern looks for text after a number and period, and before a parenthesis
    pattern = r'\d+\.\s+(.*)\s*\-\s*\['
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return None
    

def standardize_disease(diagnosis_line):
    result = None
    standardize_diseases = _get_standardized_diseases()
    for disease in standardize_diseases:
        if disease in diagnosis_line:
            result = disease
            break
    result = result or extract_disease_name(diagnosis_line)
    return result


def get_probability(line):
    probability = 0
    line = line.lower()
    if '[true]' in line:
        probability = 1
    elif '[also_possible]' in line:
        probability = 0.75
    elif '[more_info]' in line:
        probability = 0.25
    return probability
        

def standardize_disease_lines(diagnose_response):
    # let's say lines are "1. cold [True]\n 2. flu [more info]", return {'cold': 1, 'flu': 0.25}
    lines = diagnose_response.split('\n')
    result_dict = {
        standardize_disease(line): get_probability(line)
        for line in lines if line
    }
    return result_dict


def get_disease_line(index,disease,probability):
    if probability > 0.85:
        status = '[true]'
    elif probability > 0.5:
        status = '[also_possible]'
    elif probability > 0.25:
        status = '[more_info]'
    else:
        status = '[false]'
    
    return f'{index+1}. {disease} - {status}'


def disease_dict_to_lines(disease_dict):

    lines = [
        get_disease_line(index, disease, disease_dict[disease])
        for index, disease in enumerate(disease_dict.keys())
    ]
    return '\n'.join(lines)


def combine_disease_lines(response1,response2):
    dict1 = standardize_disease_lines(response1)
    dict2 = standardize_disease_lines(response2)
    all_keys = set(dict1.keys()) | set(dict2.keys())
    
    result_dict = {
        key: (dict1.get(key, 0.25) + dict2.get(key, 0.25)) / 2
        for key in all_keys
    }
    result_dict = dict(sorted(result_dict.items(),key = lambda x: x[1], reverse=True))
    return disease_dict_to_lines(result_dict)

