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
  const { message } = await request.json();
  const symptoms = extractSymptoms(message);
  const analysis = analyzeSymptoms(symptoms);
  
  return NextResponse.json(analysis);
}

function extractSymptoms(text: string): string[] {
  const symptoms: string[] = [];
  const textLower = text.toLowerCase();
  
  for (const disease of Object.values(DISEASE_DB)) {
    for (const symptom of disease.symptoms) {
      if (textLower.includes(symptom)) {
        symptoms.push(symptom);
      }
    }
  }
  return [...new Set(symptoms)];
}

function analyzeSymptoms(userSymptoms: string[]): {
  diagnoses: Array<{
    disease: string;
    status: string;
    matched_symptoms: string[];
  }>;
  recommendation: string;
} {
  // ... same analysis logic as previous Flask version ...
  return {
    diagnoses: [{
      disease: "disease_stub",
      status: "status_stub",
      matched_symptoms: [],
    }],
    recommendation: "recommendation_stub"
  }
}
