// frontend/app/page.js

'use client';

import { useState } from 'react';

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // This function calls our new AI agent endpoint
  const getAnalysis = async () => {
    setIsLoading(true);
    setAnalysisResult('The agent is thinking... synthesizing data from weather, satellite, and TiDB...');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/get-farm-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          farm_location: 'Stellenbosch', // Sending mock data from frontend
          crop_type: 'Chenin Blanc Grapes',
        }),
      });
      const data = await response.json();
      setAnalysisResult(data.analysis);

    } catch (error) {
      setAnalysisResult('Failed to connect to the backend agent. Is it running?');
    }

    setIsLoading(false);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-900 text-white">
      <div className="text-center w-full max-w-2xl">
        <h1 className="text-4xl font-bold mb-4">Agri-Intel Agent</h1>
        <p className="text-lg text-gray-400 mb-8">
          Your AI Agronomist for Precision Farming
        </p>

        <button
          onClick={getAnalysis}
          disabled={isLoading}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Analyzing...' : 'Run Farm Risk Analysis'}
        </button>

        <div className="mt-8 p-6 bg-gray-800 rounded-lg min-h-[12rem] text-left whitespace-pre-wrap">
          <p className="text-md font-mono text-gray-300">
            {analysisResult || 'Click the button to get your farm analysis.'}
          </p>
        </div>
      </div>
    </main>
  );
}