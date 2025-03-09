// app/api/chat/route.ts
import { NextResponse } from 'next/server';

interface DiseaseData {
  symptoms: string[];
  emergency: boolean;
  urgency: string;
}

const DISEASE_DB: Record<string, DiseaseData> = {
  flu: {
    symptoms: ['fever', 'cough', 'fatigue', 'body aches'],
    emergency: false,
    urgency: 'primary_care',
  },
  heart_attack: {
    symptoms: ['chest pain', 'shortness of breath', 'nausea', 'sweating'],
    emergency: true,
    urgency: 'emergency',
  },
  migraine: {
    symptoms: ['headache', 'nausea', 'sensitivity to light'],
    emergency: false,
    urgency: 'urgent_care',
  },
};

export async function POST(request: Request) {
  const request_json = await request.json()
  console.log(request_json)
  const response = {
    urgency: 'Visit emergency room',
    diagnoses: [{disease: 'flu', status: 'diagnosed'}],
    risks: [{condition: 'diabete', riskLevel: 'high'}],
    text: 'text,'
  }
  return NextResponse.json(response);
}
