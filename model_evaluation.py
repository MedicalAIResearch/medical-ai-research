from datasets import load_dataset, Dataset
from medical_session import GenAIMedicalSession, OpenAIMedicalSession, TogetherAIMedicalSession, MedicalSession
import pandas as pd
from tqdm import tqdm
import click
from typing import List
import re
import os


def clean_medical_phrase(keyword):
    # replace '_ ' with single space
    keyword = keyword.replace('_', ' ')
    keyword = keyword.strip()
    words = re.split(r'\s+', keyword)
    keyword = ' '.join(words)
    keyword = keyword.replace('diseae', 'disease')
    return keyword


def clean_symptom_keywords(keywords):
    keywords = [clean_medical_phrase(keyword) for keyword in keywords]
    return keywords


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
            symptoms = [symptom for symptom in medical_datasets.columns[:-2] if medical_datasets.loc[index, symptom]]
            expected_disease = medical_datasets.loc[index]['prognosis'].lower()
            for session in medical_sessions:
                symptom_string, response = self.eval_keyword_record(session,symptoms)
                results[session.model].append(response)

            results['symptom'].append(symptom_string)
            results['expected_disease'].append(expected_disease)
        result_df = pd.DataFrame(results)
        return result_df

    def rate(self, num_samples, result_df):
        accuracy = []
        for model in result_df.columns[2:]:
            accuracy.append({'model':model,
                        'first_line_accuracy':0,
                        'second_line_accuracy':0,
                        'overall_accuracy':0})
        for index in tqdm(range(num_samples)):
            disease = result_df.loc[index, 'expected_disease']
            disease = clean_medical_phrase(disease)
            if 'disease' in disease:
                words = disease.split(' ')
                words.remove('disease')
                disease = ' '.join(words)
            for i,model in enumerate(result_df.columns[2:]):
                response = result_df.loc[index,model]
                if disease in response.split('\n')[0]:
                    accuracy[i]['first_line_accuracy'] += 1/num_samples
                elif disease in response.split('\n')[1]:
                    accuracy[i]['second_line_accuracy'] += 1/num_samples
                if disease in response:
                    accuracy[i]['overall_accuracy'] += 1/num_samples
        accuracy_df = pd.DataFrame(accuracy)
        accuracy_df.set_index('model', inplace=True)
        return accuracy_df
    

def process_result(df, hub_org, hub_name, push):
    df.to_json(f'{hub_name}.temp.json')
    if push:
        Dataset.from_pandas(df).push_to_hub(hub_org + '/' + hub_name, private=True)


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

    if task == 'eval_symptom_dx':
        num_samples = 100

        medical_datasets = load_dataset("oldflag/symptom_dx_test", split='train').to_pandas()
        result_df = evaluator.eval_string_record(num_samples,medical_sessions,medical_datasets)
        process_result(result_df,'ezuruce', f'medical_eval_symptom_dx_{num_samples}s', push)
    elif task == 'eval_kaggle':
        num_samples = 10

        medical_datasets = load_dataset("ezuruce/medical-kaggle-dataset", split='train').to_pandas()
        result_df = evaluator.eval_keyword_records(num_samples,medical_sessions,medical_datasets)
        process_result(result_df,'ezuruce', f'medical_eval_kaggle_{num_samples}s', push)

    elif task == 'rate':
        result1_df = load_dataset(f'ezuruce/medical_eval_symptom_dx_100s', split='train').to_pandas()
        result2_df = load_dataset(f'ezuruce/medical_eval_kaggle_100s', split='train').to_pandas()
        result_df = pd.concat([result1_df, result2_df ], axis=1)
        ratings_df = evaluator.rate(result_df)
        print(ratings_df)


if __name__ == '__main__':
    main()