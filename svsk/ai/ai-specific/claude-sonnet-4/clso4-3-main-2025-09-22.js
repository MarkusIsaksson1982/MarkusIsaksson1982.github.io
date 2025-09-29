import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Brain, Scale, Users } from 'lucide-react';

const ARTIEthicsAnalyzer = () => {
  const [selectedScenario, setSelectedScenario] = useState('');
  const [userAnalysis, setUserAnalysis] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [currentStep, setCurrentStep] = useState('scenario');

  // Scenarios based on ARTI curriculum ethical dilemmas
  const scenarios = {
    healthcare: {
      title: "AI i Sjukvården",
      description: "Ett AI-system används för att diagnostisera cancer från röntgenbilder. Systemet har 95% träffsäkerhet men kan inte förklara sina beslut (black box). Läkare börjar lita mer på AI än sin egen expertis.",
      stakeholders: ["Patienter", "Läkare", "Sjukhusledning", "AI-utvecklare"],
      ethicalIssues: ["Transparens", "Ansvar", "Mänsklig autonomi", "Säkerhet"],
      questions: [
        "Vem är ansvarig om AI:n gör fel diagnos?",
        "Ska patienter informeras om att AI använts?",
        "Vad händer med läkarnas kompetens?"
      ]
    },
    surveillance: {
      title: "Övervakning i Skolan",
      description: "En skola installerar AI-kameror som analyserar elevers beteende för att förutsäga våld eller mobbning. Systemet reducerar incidenter med 40% men registrerar allt eleverna gör.",
      stakeholders: ["Elever", "Föräldrar", "Lärare", "Skolledning"],
      ethicalIssues: ["Integritet", "Övervakning", "Förutsägelse vs verklighet", "Barnperspektiv"],
      questions: [
        "Är det etiskt att övervaka barn konstant?",
        "Vad händer med data om elevernas beteende?",
        "Kan AI-förutsägelser bli självuppfyllande profetior?"
      ]
    },
    employment: {
      title: "AI och Arbetslöshet",
      description: "Ett företag ersätter 200 kundtjänstmedarbetare med en AI-chatbot som fungerar 24/7 och kostar 90% mindre. Chatboten löser 80% av kundproblemen men missar nyanserade situationer.",
      stakeholders: ["Anställda", "Kunder", "Företagsledning", "Samhälle"],
      ethicalIssues: ["Arbetslöshet", "Ekonomisk effektivitet", "Kundservice", "Social påverkan"],
      questions: [
        "Har företag ansvar för anställdas framtid?",
        "Är det etiskt att prioritera vinst över arbetstillfällen?",
        "Vem hjälper de som förlorar jobben?"
      ]
    }
  };

  const analysisFramework = {
    stakeholders: "Vilka påverkas av detta AI-system?",
    benefits: "Vilka fördelar ger AI-systemet?",
    risks: "Vilka risker och nackdelar finns?",
    values: "Vilka värden kommer i konflikt?",
    alternatives: "Finns det andra lösningar?",
    responsibility: "Vem bär ansvaret för konsekvenserna?"
  };

  const handleAnalysisSubmit = () => {
    if (userAnalysis.trim()) {
      setShowFeedback(true);
      setCurrentStep('feedback');
    }
  };

  const resetAnalysis = () => {
    setSelectedScenario('');
    setUserAnalysis('');
    setShowFeedback(false);
    setCurrentStep('scenario');
  };

  const getAnalysisScore = (analysis) => {
    const keywords = ['ansvar', 'etisk', 'konsekvens', 'transparens', 'integritet', 'säkerhet', 'påverka', 'risk', 'fördel'];
    const foundKeywords = keywords.filter(keyword => 
      analysis.toLowerCase().includes(keyword.toLowerCase())
    );
    return Math.min(foundKeywords.length, 5);
  };

  if (currentStep === 'scenario') {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <Brain className="w-10 h-10 text-blue-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-800">AI Etik Analysator</h1>
            </div>
            <p className="text-gray-600">ARTI Kurs - Etiska Dilemman inom Artificiell Intelligens</p>
          </div>

          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Scale className="w-5 h-5 mr-2 text-purple-600" />
              Välj ett etiskt scenario att analysera:
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4">
              {Object.entries(scenarios).map(([key, scenario]) => (
                <div
                  key={key}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedScenario === key
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                  }`}
                  onClick={() => setSelectedScenario(key)}
                >
                  <h3 className="font-semibold text-lg mb-2">{scenario.title}</h3>
                  <p className="text-sm text-gray-600 mb-3">{scenario.description.substring(0, 100)}...</p>
                  <div className="flex flex-wrap gap-1">
                    {scenario.ethicalIssues.slice(0, 2).map((issue, index) => (
                      <span key={index} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                        {issue}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {selectedScenario && (
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">{scenarios[selectedScenario].title}</h3>
              <p className="text-gray-700 mb-4">{scenarios[selectedScenario].description}</p>
              
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Users className="w-4 h-4 mr-1" />
                    Intressenter:
                  </h4>
                  <ul className="text-sm space-y-1">
                    {scenarios[selectedScenario].stakeholders.map((stakeholder, index) => (
                      <li key={index} className="flex items-center">
                        <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                        {stakeholder}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    Etiska Frågor:
                  </h4>
                  <ul className="text-sm space-y-1">
                    {scenarios[selectedScenario].ethicalIssues.map((issue, index) => (
                      <li key={index} className="flex items-center">
                        <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                        {issue}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <button
                onClick={() => setCurrentStep('analysis')}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Starta Etisk Analys
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (currentStep === 'analysis') {
    return (
      <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">{scenarios[selectedScenario].title} - Etisk Analys</h2>
          
          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <p className="text-gray-700 font-medium mb-4">Scenario:</p>
            <p className="text-gray-600">{scenarios[selectedScenario].description}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4">Analysram - Fundera över följande:</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(analysisFramework).map(([key, question]) => (
                <div key={key} className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-800">{question}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4">Reflektionsfrågor:</h3>
            <ul className="space-y-2">
              {scenarios[selectedScenario].questions.map((question, index) => (
                <li key={index} className="flex items-start">
                  <div className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">
                    {index + 1}
                  </div>
                  <p className="text-gray-700">{question}</p>
                </li>
              ))}
            </ul>
          </div>

          <div className="mb-6">
            <label className="block text-lg font-semibold mb-3">
              Din Etiska Analys:
            </label>
            <textarea
              value={userAnalysis}
              onChange={(e) => setUserAnalysis(e.target.value)}
              className="w-full h-40 p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Skriv din analys här... Fundera över intressenterna, riskerna, fördelarna, alternativa lösningar och vem som bär ansvaret."
            />
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleAnalysisSubmit}
              disabled={!userAnalysis.trim()}
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            >
              Skicka Analys
            </button>
            <button
              onClick={() => setCurrentStep('scenario')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Tillbaka
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'feedback') {
    const score = getAnalysisScore(userAnalysis);
    const maxScore = 5;
    
    return (
      <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">Feedback på din Etiska Analys</h2>
          
          <div className="mb-6">
            <div className="flex items-center mb-4">
              <div className="flex items-center">
                {score >= 4 ? (
                  <CheckCircle className="w-8 h-8 text-green-500 mr-3" />
                ) : score >= 2 ? (
                  <AlertCircle className="w-8 h-8 text-yellow-500 mr-3" />
                ) : (
                  <XCircle className="w-8 h-8 text-red-500 mr-3" />
                )}
                <div>
                  <p className="text-lg font-semibold">
                    Analysdjup: {score}/{maxScore}
                  </p>
                  <div className="w-48 h-3 bg-gray-200 rounded-full mt-1">
                    <div 
                      className={`h-3 rounded-full ${
                        score >= 4 ? 'bg-green-500' : score >= 2 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${(score / maxScore) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Din Analys:</h3>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-700 whitespace-pre-wrap">{userAnalysis}</p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Utvecklingsområden:</h3>
            <div className="space-y-3">
              {score < 3 && (
                <div className="p-3 bg-yellow-50 border-l-4 border-yellow-400">
                  <p className="text-yellow-800">
                    <strong>Fördjupa analysen:</strong> Försök identifiera fler etiska aspekter som transparens, ansvarsskyldighet och påverkan på olika intressenter.
                  </p>
                </div>
              )}
              
              <div className="p-3 bg-blue-50 border-l-4 border-blue-400">
                <p className="text-blue-800">
                  <strong>ARTI-koppling:</strong> Din analys visar {score >= 3 ? 'god' : 'grundläggande'} förståelse för AI:s samhällspåverkan enligt ARTI-kursplanen.
                </p>
              </div>

              <div className="p-3 bg-green-50 border-l-4 border-green-400">
                <p className="text-green-800">
                  <strong>Nästa steg:</strong> Fundera över konkreta lösningsförslag och hur olika val påverkar samhällets förtroende för AI.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={resetAnalysis}
              className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Analysera Nytt Scenario
            </button>
            <button
              onClick={() => setCurrentStep('analysis')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Förbättra Analys
            </button>
          </div>
        </div>
      </div>
    );
  }
};

export default ARTIEthicsAnalyzer;
