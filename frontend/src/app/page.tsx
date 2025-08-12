// frontend/app/page.tsx

'use client';

import { useState } from 'react';

// Simple SVG spinner component for loading states
const Spinner = () => (
  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

export default function Home() {
  // Use TypeScript to define state types
  const [farmLocation, setFarmLocation] = useState<string>('Stellenbosch');
  const [cropType, setCropType] = useState<string>('Chenin Blanc Grapes');
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const getAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setAnalysisResult('');
    setError('');

    const loadingMessages = [
        "Analyzing weather patterns... 🌦️",
        "Querying satellite imagery... 🛰️",
        "Synthesizing soil data from TiDB... 🌱",
        "Compiling risk assessment... �",
    ];
    let messageIndex = 0;
    const interval = setInterval(() => {
        setAnalysisResult(loadingMessages[messageIndex % loadingMessages.length]);
        messageIndex++;
    }, 1500);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

    try {
      const response = await fetch(`${apiUrl}/api/get-farm-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farm_location: farmLocation,
          crop_type: cropType,
        }),
      });

      clearInterval(interval);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data.analysis);

    } catch (err) {
      clearInterval(interval);
      console.error('Fetch Error:', err);
      setError('Failed to connect to the Agri-Intel agent. Please ensure it is running and accessible.');
      setAnalysisResult('');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 p-4 sm:p-8 transition-colors duration-300">
      <div className="w-full max-w-3xl bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="p-8 sm:p-12">
          {/* Header Section */}
          <div className="text-center mb-10">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-800 dark:text-white">
              Agri-Intel Agent 🌱
            </h1>
            <p className="mt-3 text-lg text-gray-600 dark:text-gray-400">
              Your AI Agronomist for Precision Farming
            </p>
          </div>

          {/* Input Form Section */}
          <form onSubmit={getAnalysis} className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label htmlFor="farm_location" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Farm Location
                </label>
                <input
                  type="text"
                  id="farm_location"
                  value={farmLocation}
                  onChange={(e) => setFarmLocation(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition"
                  placeholder="e.g., Stellenbosch"
                  required
                />
              </div>
              <div>
                <label htmlFor="crop_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Crop Type
                </label>
                <input
                  type="text"
                  id="crop_type"
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition"
                  placeholder="e.g., Chenin Blanc Grapes"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center px-6 py-4 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-all duration-300 ease-in-out transform hover:scale-105"
            >
              {isLoading ? <Spinner /> : null}
              {isLoading ? 'Analyzing...' : 'Run Farm Risk Analysis'}
            </button>
          </form>

          {/* Results Section */}
          <div className="mt-10">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Analysis Report</h2>
            <div className="p-6 bg-gray-100 dark:bg-gray-900/50 rounded-lg min-h-[14rem] text-left whitespace-pre-wrap font-mono text-gray-700 dark:text-gray-300 overflow-y-auto">
              {error && <p className="text-red-500 font-semibold">{error}</p>}
              {!error && (analysisResult || <p className="text-gray-500 dark:text-gray-400">Your farm analysis will appear here once generated.</p>)}
            </div>
          </div>
        </div>
      </div>
       <footer className="text-center mt-8 text-gray-500 dark:text-gray-400 text-sm">
           <p>Powered by TiDB, Vercel, and Google AI</p>
       </footer>
    </main>
  );
}
