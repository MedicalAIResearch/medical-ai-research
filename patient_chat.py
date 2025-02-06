from models import get_openai_response as get_model_response

doctor_name = 'Doctor Brandon'

chat_system_message = '''You are a medical AI assistant designed to gather patient data through conversation. Your goal is to ask relevant questions about factors such as age, family history, lifestyle habits, and medical test results to assess disease risk and provide preliminary insights.
1. Prioritize accuracy by tailoring questions based on the most likely conditions.
2. Ensure a natural, engaging, and respectful conversation while collecting data.
3. Clearly communicate that all assessments are preliminary and that users should consult a healthcare professional for a definitive diagnosis.
4. If data is incomplete, ask clarifying questions before making an assessment.
Maintain ethical, unbiased, and privacy-conscious responses at all times. Answer concisely and only ask one question at a time.'''

risk_system_message = '''You are a medical AI assistant trained to assess the risk of {disease} based on patient data. Your goal is to analyze information gathered from conversations, including age, family history, lifestyle factors, and medical test results, to provide a calculated risk factor for specific diseases.
Ensure risk assessments are based on reliable medical correlations and statistical models. Respond with [LOW], [MEDIUM] or [HIGH]
Example 1:
Patient: I have a rash
[LOW]
'''


def evaluate_risk(chat_messages, disease):
    messages = [{'role': 'system','content': risk_system_message.format(disease=disease)}, *chat_messages[1:]]
    risk_factor = get_model_response(messages)
    return risk_factor


def patient_chat():
    messages = []
    print(messages)
    first_message = f'\nDoctor:\nHello, I am {doctor_name}. What brings you in today?\n'
    print(first_message)
    messages.append({'role': 'system','content': chat_system_message})
    messages.append({'role':'assistant','content':first_message})

    while True:
        message = input('Patient:\n')

        messages.append({'role': 'user','content': message})
        response = get_model_response(messages)
        risk = evaluate_risk(messages,'stroke')
        print(f'\nDoctor:\n{response}')
        print(risk+'\n')
        messages.append({'role':'assistant','content':response})


patient_chat()