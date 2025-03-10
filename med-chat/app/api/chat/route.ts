// app/api/chat/route.ts
import { NextResponse } from 'next/server';


const chatSystemText = `You are a medical AI assistant designed to gather patient data through conversation. Your goal is to ask relevant questions about factors such as age, family history, lifestyle habits, and medical test results to assess disease risk and provide preliminary insights.
1. Prioritize accuracy by tailoring questions based on the most likely conditions.
2. Ensure a natural, engaging, and respectful conversation while collecting data.
3. Clearly communicate that all assessments are preliminary and that users should consult a healthcare professional for a definitive diagnosis.
4. If data is incomplete, ask clarifying questions before making an assessment.
Maintain ethical, unbiased, and privacy-conscious responses at all times. Answer concisely and only ask one question at a time.`

const chatSystemMessage = {'role': 'system','content': chatSystemText}


function getRiskSystemText(condition: string): ChatMessage {
  const riskSystemText = `You are a medical AI assistant trained to assess the risk of ${condition} or being diagnosed with ${condition} which ever is more likely based on patient data. Your goal is to analyze information gathered from conversations, including age, family history, lifestyle factors, and medical test results, to provide a calculated risk factor for specific diseases.
Ensure risk assessments are based on reliable medical correlations and statistical models. Respond with [LOW], [MEDIUM] or [HIGH] or [MORE_INFO]. If you need more information. Do not ask any questions, only respond with these four answers.
Example Response 1:
[LOW]
Example Response 2:
[MEDIUM]
Example Response 3:
[HIGH]
Example Response 4:
[MORE_INFO]
`
  const riskSystemMessage = {role: 'system', content: riskSystemText}
  return riskSystemMessage as ChatMessage
}

const diagnosisSystemText = `
Select a diseases that you feel will be of utmost importance and are the most risky.
Respond with only the diseases and a [TRUE] or [FALSE] if they have been confirmed or not confirmed to have the disease or [MORE_INFO] if you do not have enough information.
You are a medical AI assistant trained to analyze patient data and suggest potential conditions based on symptoms, medical history, and lifestyle factors. Your goal is to evaluate given conversational data as well as the diagnosis at that point and provide a new diagnosis based off new data if there is any.
If more then one is [TRUE] you must set one as [ALSO_POSSIBLE]
1. Base assessments on medical correlations and established patterns. When these similar diseases are no longer possible change them to [FALSE].
Example Response:
1. Disease A - [TRUE]
2. Disease B - [FALSE]
3. Disease C - [MORE_INFO]`


const diagnosisSystemMessage = {role:'system',content: diagnosisSystemText}

const urgencySystemText = `You are a medical AI assistant assessing whether a patient's symptoms are urgent or not. 
Base your response on medical patterns and provide clear guidance based on the symptoms provided.

### **STRICT RESPONSE FORMAT**
You MUST return one of the following responses EXACTLY as written (do NOT generate any other text):
- [EMERGENCY] Go to Emergency Room (life-threatening).
- [URGENT_CARE] Seek urgent care soon (serious but not life-threatening).
- [PRIMARY_CARE] Schedule an appointment (non-urgent concern).
- [MONITOR] Watch symptoms and seek care if they worsen.
- [SAFE] No medical attention needed.

### **Example Responses**
User: I have a rash.  
Response: [MONITOR] Watch symptoms and seek care if they worsen.  

User: I have 42C fever for 10 days.  
Response: [EMERGENCY] Go to Emergency Room (life-threatening).  

User: I have a cough.  
Response: [MONITOR] Watch symptoms and seek care if they worsen.  
`

const urgencySystemMessage = {role: 'system', content:urgencySystemText}


const AZURE_OPENAI_HOST = process.env.AZURE_OPENAI_HOST as string
const AZURE_OPENAI_KEY = process.env.AZURE_OPENAI_KEY as string

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}


async function get_model_response(messages: ChatMessage[], stop=null, max_tokens=512) {
  const api_key = AZURE_OPENAI_KEY
  const headers = {"api-key": api_key, 'Content-Type': 'application/json'}
  
  const url = AZURE_OPENAI_HOST
  const generation_params = {
      "frequency_penalty": 0.,
      "presence_penalty": 0., 
      "max_tokens": max_tokens,
      "stop": stop,
      "temperature": 0,
      "top_p": 1,
      "n": 1
  }
  const method = 'POST';
  const body =JSON.stringify({messages: messages, ...generation_params})
  const response = await fetch(url, {method, headers, body})
  const data = await response.json()
  const content = data["choices"][0]["message"]["content"]
  const cleaned_content = content.trim()
  return cleaned_content
}


function getUrgency(urgencyResponse: string) {
  const match = urgencyResponse.match(/\[(.*?)\] (.*)/);

  // Get the extracted code and text separately
  const code = match ? match[1] : null;
  const text = urgencyResponse
  return {code, text}
}

async function getRisk(condition: string, messages: ChatMessage[]) {
  const riskSystemMessage = getRiskSystemText(condition)
  const riskMessages = [riskSystemMessage, ...messages];
  let riskLevel = await get_model_response(riskMessages);
  if(!['[LOW]', '[MEDIUM]', '[HIGH]'].includes(riskLevel)) {
    riskLevel = '[MORE_INFO]'
  }
  const risk = {condition, riskLevel}
  return risk
}


export async function POST(request: Request) {
  const request_json = await request.json()
  const messages = request_json.conversation;
  const chatMessages = [chatSystemMessage, ...messages];
  const urgencyMessages = [urgencySystemMessage, ...messages];
  const diagnosisMessages = [diagnosisSystemMessage, ...messages.slice(0,-1), messages[messages.length-1]];
  const text = await get_model_response(chatMessages);
  const risks = [await getRisk('Hypertension', messages), await getRisk('Diabetes', messages), await getRisk('Depression', messages)]
  const urgencyResponse = await get_model_response(urgencyMessages);
  const urgency = getUrgency(urgencyResponse)
  const diagnosisResponse = await get_model_response(diagnosisMessages);
  const diagnosis = diagnosisResponse.split("\n").map(
    (line:string) => {
      const match = line.match(/(\d+)\. (.+?) - \[(.+?)\]/);
      return match ? {name: match[2], status: match[3]} : null;
  }).filter(Boolean);
  const response = {urgency, diagnosis, risks, text}
  console.log({response: JSON.stringify(response)})
  return NextResponse.json(response);
}
