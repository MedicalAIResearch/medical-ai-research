from datasets import load_dataset, Dataset
from medical_session import GenAIMedicalSession, OpenAIMedicalSession, TogetherAIMedicalSession, MedicalSession
import pandas as pd
from tqdm import tqdm
import click
from typing import List
import re


def clean_prognosis(keyword):
    # replace '_ ' with single space
    keyword = keyword.replace('_', ' ')
    keyword = keyword.strip()
    words = re.split(r'\s+', keyword)
    keyword = ' '.join(words)
    keyword = keyword.replace('diseae', 'disease')
    keyword = keyword.replace('AIDS','hiv')
    keyword = keyword.replace('(vertigo) Paroymsal Positional Vertigo','paroxysmal positional vertigo')
    keyword = keyword.replace('Allergy','allergi')
    keyword = keyword.replace('Chicken pox','chickenpox')
    keyword = keyword.replace('Dimorphic hemmorhoids(piles)','hemorrhoids')
    keyword = keyword.replace('Osteoarthristis','osteoarthritis')
    keyword = keyword.replace('Paralysis (brain hemorrhage)','stroke')
    keyword = keyword.replace('Heart attack','mycordial infarction')
    return keyword


def clean_medical_phrase(keyword):
    # replace '_ ' with single space
    keyword = keyword.replace('_', ' ')
    keyword = keyword.strip()
    words = re.split(r'\s+', keyword)
    keyword = ' '.join(words)
    return keyword


def clean_symptom_keywords(keywords):
    keywords = [clean_medical_phrase(keyword) for keyword in keywords]
    return keywords


PROGNOSIS_COLUMN = 132

class MedicalSessionEvaluator():

    def __init__(self):
        pass

    def evaluate_symptoms(self, medical_session, symptom):
        response = medical_session.diagnose_disease([],{'role': 'user', 'content': symptom},None)
        return response


    def eval_string_record(self, model_session: MedicalSession, symptom_string: str) -> str:
        response = self.evaluate_symptoms(model_session,symptom_string).lower()
        return symptom_string, response
        

    def eval_keyword_record(self, model_session: MedicalSession, symptom_keywords: List[str]) -> str:
        symptom_string = f'I have {", ".join(clean_symptom_keywords(symptom_keywords))}.'
        response = self.evaluate_symptoms(model_session,symptom_string).lower()
        return symptom_string, response


    def eval_string_records(self, num_samples, medical_sessions, medical_datasets):
        results = {'symptom':[], 'expected_disease':[]}
        for session in medical_sessions:
            results[session.model] = []
        for index in tqdm(range(num_samples)):
            for session in medical_sessions:
                symptom = medical_datasets.loc[index,'input_text']
                expected_disease = medical_datasets.loc[index,'output_text'].lower()
                for session in medical_sessions:
                    symptom_string, response = self.eval_string_record(session,symptom)
                    results[session.model].append(response)

                results['symptom'].append(symptom_string)
                results['expected_disease'].append(expected_disease)
        result_df = pd.DataFrame(results)
        return result_df
    

    def eval_keyword_records(self, num_samples, medical_sessions, medical_datasets):
        results = {'symptom':[],'expected_disease':[]}
        for session in medical_sessions:
            results[session.model] = []
        for index in tqdm(range(num_samples)):
            symptoms = [symptom for symptom in medical_datasets.columns[:PROGNOSIS_COLUMN] if medical_datasets.loc[index, symptom]]
            expected_disease = medical_datasets.loc[index]['prognosis'].lower()
            for session in medical_sessions:
                symptom_string, response = self.eval_keyword_record(session,symptoms)
                results[session.model].append(response)

            results['symptom'].append(symptom_string)
            results['expected_disease'].append(expected_disease)
        result_df = pd.DataFrame(results)
        return result_df

    def rate(self, result_df):
        num_samples = len(result_df)
        accuracy = []
        result_detail_df = result_df.copy()
        for model in result_df.columns[2:]:
            accuracy.append({'model':model,
                        'accuracy1':0,
                        'accuracy2':0,
                        'accuracy_overall':0})
            result_detail_df[f'{model}_accuracy1'] = 0
            result_detail_df[f'{model}_accuracy2'] = 0
            result_detail_df[f'{model}_accuracy_overall'] = 0
        for index in tqdm(range(num_samples)):
            disease = result_df.loc[index, 'expected_disease']
            if 'disease' in disease:
                words = disease.split(' ')
                words.remove('disease')
                disease = ' '.join(words)
            for i,model in enumerate(result_df.columns[2:]):
                response = result_df.loc[index,model]
                if disease in response.split('\n')[0]:
                    accuracy[i]['accuracy1'] += 1/num_samples
                    result_detail_df.loc[index, f'{model}_accuracy1'] = 1
                if disease in '\n'.join(response.split('\n')[:2]):
                    accuracy[i]['accuracy2'] += 1 / num_samples
                    result_detail_df.loc[index, f'{model}_accuracy2'] = 1
                if disease in response:
                    accuracy[i]['accuracy_overall'] += 1/num_samples
                    result_detail_df.loc[index, f'{model}_accuracy_overall'] = 1
        for i,model in enumerate(result_df.columns[2:]):
            overall_proportion = accuracy[i]['accuracy_overall']
            accuracy[i]['Standard Deviation'] = (overall_proportion * (1-overall_proportion) / num_samples)**0.5
            
        accuracy_df = pd.DataFrame(accuracy)
        accuracy_df.set_index('model', inplace=True)
        return accuracy_df,result_detail_df
    

def process_result(df, hub_org, hub_name, push):
    df.to_json(f'{hub_name}.temp.json')
    if push:
        Dataset.from_pandas(df).push_to_hub(hub_org + '/' + hub_name, private=True)

import hashlib


def get_signature(row):
    num_str = ''
    for symptom, value in row.to_dict().items():
        if symptom == 'prognosis':
            break
        else:
            num_str += str(value)
    md5_hash = hashlib.md5()
    md5_hash.update(num_str.encode('utf-8'))
    md5_hash = md5_hash.hexdigest()[:7]
    return md5_hash


@click.command()
@click.argument('task', type=click.Choice(['eval_symptom_dx','eval_kaggle', 'rate']))
@click.option('--push', is_flag=True, help="Enable push mode")
def main(task, push):
    evaluator = MedicalSessionEvaluator()
    medical_sessions = [
        OpenAIMedicalSession(),
        GenAIMedicalSession(),
        # TogetherAIMedicalSession()
    ]

    if task == 'clean_dataset':
        # read medical kaggle dataset, write medical kaggle dataset cleaned\
        df = load_dataset("ezuruce/medical-kaggle-dataset", split='train').to_pandas()
        df['prognosis'] = df.apply(lambda row: clean_prognosis(row.prognosis), axis=1)
        df['signature'] = df.apply(lambda row: get_signature(row),axis = 1)

        process_result(df,'ezuruce', 'medical-kaggle-dataset-cleaned', push)
        
    elif task == 'eval_symptom_dx':
        num_samples = 212

        medical_datasets = load_dataset("oldflag/symptom_dx_test", split='train').to_pandas()
        result_df = evaluator.eval_string_records(num_samples,medical_sessions,medical_datasets)
        process_result(result_df,'ezuruce', f'medical-eval-symptom-dx-{num_samples}s', push=True)
    elif task == 'eval_kaggle':
        df = load_dataset("ezuruce/medical-kaggle-dataset-cleaned", split='train').to_pandas()
        assert df.columns.to_list()[PROGNOSIS_COLUMN] == 'prognosis'
        df = df[df.batch == 1].reset_index(drop=True)
        num_samples = 1
        result_df = evaluator.eval_keyword_records(num_samples,medical_sessions,df)
        process_result(result_df,'ezuruce', f'medical-eval-kaggle-{num_samples}s', push)

    elif task == 'rate':
        result1_df = load_dataset(f'ezuruce/medical-eval-symptom-dx-212s', split='train').to_pandas()
        result2_df = load_dataset(f'ezuruce/medical-eval-kaggle-400s', split='train').to_pandas()
        result_df = pd.concat([result1_df, result2_df ], axis=0, ignore_index=True)
        ratings_df = evaluator.rate(result_df)
        print(ratings_df)
        push = True
        if push:
            Dataset.from_pandas(ratings_df).push_to_hub('ezuruce/medical_eval_ratings_0219_v1')

        process_result(result_df,'ezuruce', 'medical_eval_ratings_0219_v1', push)


if __name__ == '__main__':
    main()