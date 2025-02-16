from datasets import load_dataset, Dataset
from medical_session import GenAIMedicalSession, OpenAIMedicalSession, TogetherAIMedicalSession
import pandas as pd
from tqdm import tqdm


class MedicalSessionEvaluator():

    def __init__(self):
        pass

    def evaluate_symptoms(self, medical_session, symptom):
        response = medical_session.diagnose_disease([],{'role': 'user', 'content': symptom},None)
        return response

    def evaluate(self, num_samples, medical_sessions, medical_datasets):
        results = {'symptom':[],'expected_disease':[]}
        for session in medical_sessions:
            results[session.model] = []
        for index in tqdm(range(num_samples)):
            symptom = medical_datasets[index]['input_text']
            expected_disease = medical_datasets[index]['output_text'].lower()
            for session in medical_sessions:
                response = self.evaluate_symptoms(session,symptom).lower()
                results[session.model].append(response)
            results['symptom'].append(symptom)
            results['expected_disease'].append(expected_disease)

        result_df = pd.DataFrame(results)
        return result_df

        

def main():
    num_samples = 100
    medical_datasets = load_dataset("oldflag/symptom_dx_test", split='train')
    evaluator = MedicalSessionEvaluator()
    medical_sessions = [OpenAIMedicalSession(),
                        GenAIMedicalSession(),
                        #TogetherAIMedicalSession()
                        ]
    result_df = evaluator.evaluate(num_samples,medical_sessions,medical_datasets)
    ds = Dataset.from_pandas(result_df)
    #ds.push_to_hub(f'ezuruce/medical_session_eval_2m{num_samples}',private=True)

if __name__ == '__main__':
    main()