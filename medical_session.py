from models import get_openai_response, get_genai_response, get_togetherai_response



class MedicalSession():

    chat_system_message = '''You are a medical AI assistant designed to gather patient data through conversation. Your goal is to ask relevant questions about factors such as age, family history, lifestyle habits, and medical test results to assess disease risk and provide preliminary insights.
    1. Prioritize accuracy by tailoring questions based on the most likely conditions.
    2. Ensure a natural, engaging, and respectful conversation while collecting data.
    3. Clearly communicate that all assessments are preliminary and that users should consult a healthcare professional for a definitive diagnosis.
    4. If data is incomplete, ask clarifying questions before making an assessment.
    Maintain ethical, unbiased, and privacy-conscious responses at all times. Answer concisely and only ask one question at a time.'''

    risk_system_message = '''You are a medical AI assistant trained to assess the risk of {disease} based on patient data. Your goal is to analyze information gathered from conversations, including age, family history, lifestyle factors, and medical test results, to provide a calculated risk factor for specific diseases.
    Ensure risk assessments are based on reliable medical correlations and statistical models. Respond with [LOW], [MEDIUM] or [HIGH] or [MOREINFO] if you need more information. Do not ask any questions, only respond with these four answers.
    Example Response 1:
    [LOW]
    Example Response 2:
    [MEDIUM]
    Example Response 3:
    [HIGH]
    Example Response 4:
    [MOREINFO]
    '''

    diagnosis_system_message = '''Select a diseases that you feel will be of utmost importance and are the most risky.
    Respond with only the diseases and a [TRUE] or [FALSE] if they have been confirmed or not confirmed to have the disease or [MORE_INFO] if you do not have enough information.
    You are a medical AI assistant trained to analyze patient data and suggest potential conditions based on symptoms, medical history, and lifestyle factors. Your goal is to evaluate given conversational data as well as the diagnosis at that point and provide a new diagnosis based off new data if there is any.
    If more then one is [TRUE] you must set one as [ALSO_POSSIBLE]
    1. Base assessments on medical correlations and established patterns. When these similar diseases are no longer possible change them to [FALSE].
    Example Response:
        1. Disease A - [TRUE]
        2. Disease B - [FALSE]
        3. Disease C - [MORE_INFO]
    '''

    urgency_system_message = """You are a medical AI assistant assessing whether a patient's symptoms are urgent or not. 
    Base your response on medical patterns and provide clear guidance based on the symptoms provided.
    Return one of the following responses:
    [EMERGENCY] → Go to the hospital immediately (life-threatening).
    [URGENT_CARE] → Seek urgent care soon (serious but not life-threatening).
    [PRIMARY_CARE] → Schedule an appointment with a doctor (non-urgent concern).
    [MONITOR] → Watch symptoms and seek care if they worsen.
    [SAFE] → No medical attention needed.
    Example:
    User: I have a rash.
    Response: [MONITOR] → Watch symptoms and seek care if they worsen"""

    def __init__(self, get_model_response, doctor_name='Doctor Brandon'):
        self.get_model_response = get_model_response
        self.doctor_name = doctor_name

    def _get_model_response(self, system_prompt, messages):
        return self.get_model_response([{'role':'system', 'content':system_prompt}, *messages])

    def diagnose_disease(self, history, new_message, previous_diagnosis):
        diagnosis_messages = [] if previous_diagnosis is None else [previous_diagnosis]
        messages = [*history, *diagnosis_messages, new_message]
        diagnosis = self._get_model_response(self.diagnosis_system_message, messages)
        return diagnosis

    def evaluate_risk(self, next_history, disease):
        risk_factor = self._get_model_response(self.risk_system_message.format(disease=disease), next_history)
        return risk_factor

    def evaluate_urgency(self, next_history):
        urgency = self._get_model_response(self.urgency_system_message,next_history)
        return urgency

    def chat(self):
        first_message = f'\nDoctor:\nHello, I am {self.doctor_name}. What brings you in today?\n'
        
        print(first_message)
        history = [{'role':'assistant','content':first_message}]

        running = True
        previous_diagnosis = None
        while running:
            new_message = {'role': 'user', 'content': input('Patient:\n')}
            next_history = [*history, new_message]
            response = self._get_model_response(self.chat_system_message, next_history)
            print(f'\nDoctor:\n{response}\n')
            
            diagnosis = self.diagnose_disease(history, new_message, previous_diagnosis)
            print('Diagnosis Message:\n'+diagnosis+'\n')

            urgency = self.evaluate_urgency(next_history)
            print(f'Urgency: {urgency}\n')

            risk = self.evaluate_risk(next_history, 'stroke')
            print('Risk for stroke: ' + risk +'\n')

            history = next_history
            previous_diagnosis = {'role':'assistant','content':diagnosis}
            # if diagnosis.count('[MOREINFO]') and risk.count('[MOREINFO]')== 0:
            #     running = False


class OpenAIMedicalSession(MedicalSession):
    model = 'gpt-4o-mini'
    def __init__(self):
        MedicalSession.__init__(self,get_openai_response)


class GenAIMedicalSession(MedicalSession):
    model = 'gemini-1.5-flash'
    def __init__(self):
        MedicalSession.__init__(self,get_genai_response)


class TogetherAIMedicalSession(MedicalSession):
    def __init__(self):
        MedicalSession.__init__(self,get_togetherai_response)


if __name__ == '__main__':
    medical_session = OpenAIMedicalSession()
    medical_session.chat()