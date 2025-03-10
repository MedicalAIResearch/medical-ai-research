// app/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { Stethoscope } from "lucide-react";

interface Diagnosis {
  name: string;
  status: string;
}

interface RiskIndicator {
  condition: string;
  riskLevel: string;
}

interface Urgency {
  code: string;
  text: string
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [urgency, setUrgency] = useState<Urgency>();
  const [diagnosis, setDiagnosis] = useState<Diagnosis[]>([]);
  const [risks, setRisks] = useState<RiskIndicator[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const statusColors: { [key: string]: string } = {
    TRUE: 'bg-red-100 text-red-800',
    ALSO_POSSIBLE: 'bg-yellow-100 text-yellow-800',
    MORE_INFO: 'bg-blue-100 text-blue-800',
  };

  const urgencyColors: { [key: string]: string } = {
    'EMERGENCY': 'bg-red-500 text-white',
    'URGENT_CARE': 'bg-orange-500 text-white',
    'PRIMARY_CARE': 'bg-yellow-500 text-white',
    'MONITOR': 'bg-blue-400 text-white',
    'SAFE': 'bg-green-500 text-white'   };

  const riskColors: { [key: string]: string } = {
    '[LOW]': 'bg-green-100 text-green-800',
    '[MEDIUM]': 'bg-yellow-100 text-yellow-800',
    '[HIGH]': 'bg-red-100 text-red-800',
    '[MORE_INFO]': 'bg-gray-100 text-gray-800'
  }

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add initial greeting message when the component mounts
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello, I am Doctor Brandon. What brings you in today?'
      },
    ]);
  }, []);

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: userInput}
    const updatedMessages = [
      ...messages,
      userMessage,
    ];
    setMessages(updatedMessages);
    setUserInput('');
    setIsTyping(true);

    try {
      // Send the entire conversation history to the backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation: updatedMessages }),
      });

      const data = await response.json();

      // Update state with the backend response
      setUrgency(data.urgency);
      setDiagnosis(data.diagnosis);
      setRisks(data.risks);

      // Add assistant response to the conversation
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: data.text },
      ]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto max-w-6xl p-4 flex flex-col md:flex-row space-y-6 md:space-y-0 md:space-x-6">
        {/* Chatbox */}
        <div className="flex-1 bg-white rounded-2xl shadow-xl">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-2xl flex items-center space-x-3">
            <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center">
              <Stethoscope className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Medical Assistant</h1>
              <p className="text-sm opacity-90">AI-powered symptom assessment</p>
            </div>
          </div>

          {/* Chat Container */}
          <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex flex-col ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                <div
                  className={`p-4 rounded-2xl max-w-[80%] transition-all duration-300 ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white self-end rounded-tr-none'
                      : 'bg-gray-100 text-gray-800 self-start rounded-tl-none'
                  }`}
                >
                  {msg.content as string}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex space-x-2 items-center">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '-0.15s' }}
                />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '-0.3s' }}
                />
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <input
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Describe your symptoms..."
                className="flex-1 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 text-gray-800 bg-white"
              />
              <button
                onClick={sendMessage}
                className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              This is not a substitute for professional medical advice
            </p>
          </div>
        </div>

        {/* Sidebar for Indicators */}
        <div className="w-full md:w-80 bg-white rounded-2xl shadow-xl p-6">
          <h2 className="text-lg font-bold mb-4">Assessment Summary</h2>

          {/* Urgency Indicator */}
          {urgency && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Urgency</h3>
              <div
                className={`p-3 rounded-lg text-center font-semibold ${
                  urgencyColors[urgency.code]
                }`}
              >
                {urgency.text}
              </div>
            </div>
          )}

          {/* Diagnosis */}
          {diagnosis.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Diagnosis</h3>
              <div className="space-y-3">
                {diagnosis.map((disease, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 rounded-lg shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">
                        {disease.name}
                      </span>
                      <span
                        className={`px-2 py-1 rounded-full text-xs ${
                          statusColors[disease.status]
                        }`}
                      >
                        {disease.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Factors */}
          {risks.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Risk Factors</h3>
              <div className="space-y-3">
                {risks.map((risk, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-50 rounded-lg shadow-sm flex items-center justify-between"
                  >
                    <span className="font-medium">{risk.condition}</span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${
                        riskColors[risk.riskLevel]
                      }`}
                    >
                      {risk.riskLevel}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}