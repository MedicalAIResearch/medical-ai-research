import requests
import google.generativeai as genai
from retry import retry
from datasets import load_dataset, Dataset
from dotenv import load_dotenv
import os
import random
load_dotenv()


AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
AZURE_OPENAI_HOST = os.getenv('AZURE_OPENAI_HOST')
GOOGLE_GENAI_KEY = os.getenv('GOOGLE_GENAI_KEY')
TOGETHER_AI_KEY = os.getenv('TOGETHER_AI_KEY')

@retry(tries=2, delay=5)
def get_openai_response(messages, stop=None, max_tokens= 512):
    api_key = AZURE_OPENAI_KEY
    headers = {"api-key": api_key}
    url = AZURE_OPENAI_HOST
    generation_params = {
        "frequency_penalty": 0.,
        "presence_penalty": 0., 
        "max_tokens": max_tokens,
        "stop": stop,
        "temperature": 0,
        "top_p": 1,
        "n": 1
    }
    payload = {"messages": messages, **generation_params}
    response = requests.post(url, json=payload, headers=headers).json()
    content = response["choices"][0]["message"]["content"]
    content = content.strip('`')
    content = content.lstrip('json')
    return content


def _get_google_role(role):
    role = role if role != 'system' else 'user'
    return role


def get_genai_response(messages):
    chat_history = [
        {'role': _get_google_role(message['role']),'parts':[message['content']]}
        for message in messages
    ]
    
    genai.configure(api_key=GOOGLE_GENAI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(chat_history)
    return response.text


def get_togetherai_response(messages,stop=None, max_tokens= 512):
    url = "https://api.together.xyz/v1/chat/completions"
    api_key = TOGETHER_AI_KEY
    headers = {"Authorization": f"Bearer {api_key}"}
    generation_params = {
        "frequency_penalty": 0.,
        "presence_penalty": 0., 
        "max_tokens": max_tokens,
        "stop": stop,
        "temperature": 0,
        "top_p": 1,
        "n": 1
    }
    model = 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'
    payload = {"messages": messages, "model": model, **generation_params}
    response = requests.post(url, json=payload, headers=headers).json()
    content = response["choices"][0]["message"]["content"]
    content = content.strip('`')
    content = content.lstrip('json')
    return content


def test_case(instruction, input, output):
    messages = [{'role': 'system','content': instruction},{'role':'user','content': input}]
    openai_response = get_openai_response(messages)
    genai_response = get_genai_response(messages)
    togetherai_response = get_togetherai_response(messages)
    print(f'OpenAI Response: {openai_response}')
    print(f'Gemini Response: {genai_response}')
    print(f'Llama Response: {togetherai_response}')
    print(f'Real Output: {output}')
    return {'instruction':instruction,'input':input,'gpt-4o-mini': openai_response, 'gemini-1.5-flash':genai_response,'llama-3.1-8b':togetherai_response,'output':output}

def test(samples, dataset_name='ezuruce/medical-ai-evaluation'):
    random.seed(76)
    
    ds = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k", split='train')
    sample_indexes = [random.randint(0,len(ds)-1) for _ in range(samples)]
    ds = ds.select(sample_indexes)

    new_data = [test_case(**row) for row in ds]

    new_ds = Dataset.from_list(new_data)
    new_ds.push_to_hub(dataset_name, private=True)


def find_kw(ds, word):
    df = ds.to_pandas()
    filtered_df = df[df['Output'].str.contains(word, case=False, na=False)]
    return filtered_df

#test(2, 'ezuruce/test')
#test(15, 'ezuruce/run')