// app/page.tsx
'use client';

import { useState, useRef, useEffect } from 'react';

interface Diagnosis {
  disease: string;
  status: string;
  matched_symptoms: string[];
}

interface ChatMessage {
  sender: 'user' | 'bot';
  type: 'text' | 'diagnosis' | 'recommendation';
  content: string | { diagnoses: Diagnosis[]; recommendation: string };
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const statusColors: { [key: string]: string } = {
    Diagnosed: 'bg-red-100 text-red-800',
    Likely: 'bg-yellow-100 text-yellow-800',
    'More information needed': 'bg-blue-100 text-blue-800',
  };

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    // Add user message
    setMessages(prev => [
      ...prev,
      { sender: 'user', type: 'text', content: userInput },
    ]);

    const currentInput = userInput;
    setUserInput('');
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });

      const data = await response.json();

      // Add bot responses
      setMessages(prev => [
        ...prev,
        { sender: 'bot', type: 'diagnosis', content: data },
        { sender: 'bot', type: 'recommendation', content: data.recommendation },
      ]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto max-w-2xl p-4">
        <div className="bg-white rounded-2xl shadow-xl">
          {/* Header */}
          <div className="bg-blue-600 text-white p-4 rounded-t-2xl flex items-center space-x-3">
            <div className="h-12 w-12 bg-white rounded-full flex items-center justify-center">
              🩺
            </div>
            <div>
              <h1 className="text-xl font-bold">MedChat Assistant</h1>
              <p className="text-sm opacity-90">AI-powered symptom assessment</p>
            </div>
          </div>

          {/* Chat Container */}
          <div className="h-[60vh] overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex flex-col ${
                  msg.sender === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                {msg.type === 'text' && (
                  <div
                    className={`p-4 rounded-2xl max-w-[80%] transition-all duration-300 ${
                      msg.sender === 'user'
                        ? 'bg-blue-500 text-white self-end rounded-tr-none'
                        : 'bg-gray-100 text-gray-800 self-start rounded-tl-none'
                    }`}
                  >
                    { "msg_content_stub" /*msg.content */ }
                  </div>
                )}

                {msg.type === 'diagnosis' && (
                  <div className="w-full space-y-4">
                    {(msg.content as { diagnoses: Diagnosis[] }).diagnoses.map(
                      (disease, idx) => (
                        <div
                          key={idx}
                          className="p-4 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow"
                        >
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-lg capitalize">
                              {disease.disease.replace('_', ' ')}
                            </h3>
                            <span
                              className={`px-3 py-1 rounded-full text-sm ${
                                statusColors[disease.status]
                              }`}
                            >
                              {disease.status}
                            </span>
                          </div>
                          <div className="mt-2 text-sm text-gray-600">
                            Matched symptoms: {disease.matched_symptoms.join(', ')}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                )}

                {msg.type === 'recommendation' && (
                  <div className="p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg w-full">
                    <h3 className="font-bold text-yellow-800 mb-2">
                      Healthcare Recommendation
                    </h3>
                    <p className="text-yellow-700">
                      {msg.content as string}
                    </p>
                  </div>
                )}
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
                className="flex-1 p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400"
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
      </div>
    </div>
  );
}