import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Plus, Minus, Download, Upload, Save, Eye, EyeOff, 
  Star, Users, BookOpen, Settings, Sun, Moon,
  Check, AlertCircle, FileText, Share2
} from 'lucide-react';

// Multilingual support
const translations = {
  sv: {
    // Navigation
    rubricBuilder: 'Bedömningsmatris',
    selfAssessment: 'Självbedömning',
    peerFeedback: 'Kamratbedömning',
    portfolio: 'Portfolio',
    settings: 'Inställningar',
    
    // Rubric Builder
    createRubric: 'Skapa Bedömningsmatris',
    rubricTitle: 'Titel på bedömningsmatris',
    addCriteria: 'Lägg till kriterium',
    criteriaName: 'Kriteriumnamn',
    addLevel: 'Lägg till nivå',
    levelName: 'Nivånamn',
    levelDescription: 'Nivåbeskrivning',
    saveRubric: 'Spara bedömningsmatris',
    exportData: 'Exportera data',
    
    // Self Assessment
    confidenceLevel: 'Konfidensnivå',
    veryUnsure: 'Mycket osäker',
    verySure: 'Mycket säker',
    submitAssessment: 'Skicka bedömning',
    
    // Peer Feedback
    selectPeer: 'Välj kamrat',
    feedbackFor: 'Feedback till',
    strengths: 'Styrkor',
    improvements: 'Förbättringsområden',
    
    // Portfolio
    addEvidence: 'Lägg till bevis',
    evidenceTitle: 'Bevis titel',
    evidenceType: 'Typ av bevis',
    reflection: 'Reflektion',
    
    // Common
    save: 'Spara',
    cancel: 'Avbryt',
    delete: 'Ta bort',
    edit: 'Redigera',
    view: 'Visa',
    close: 'Stäng'
  },
  en: {
    // Navigation
    rubricBuilder: 'Rubric Builder',
    selfAssessment: 'Self Assessment',
    peerFeedback: 'Peer Feedback',
    portfolio: 'Portfolio',
    settings: 'Settings',
    
    // Rubric Builder
    createRubric: 'Create Rubric',
    rubricTitle: 'Rubric Title',
    addCriteria: 'Add Criteria',
    criteriaName: 'Criteria Name',
    addLevel: 'Add Level',
    levelName: 'Level Name',
    levelDescription: 'Level Description',
    saveRubric: 'Save Rubric',
    exportData: 'Export Data',
    
    // Self Assessment
    confidenceLevel: 'Confidence Level',
    veryUnsure: 'Very Unsure',
    verySure: 'Very Sure',
    submitAssessment: 'Submit Assessment',
    
    // Peer Feedback
    selectPeer: 'Select Peer',
    feedbackFor: 'Feedback for',
    strengths: 'Strengths',
    improvements: 'Areas for Improvement',
    
    // Portfolio
    addEvidence: 'Add Evidence',
    evidenceTitle: 'Evidence Title',
    evidenceType: 'Evidence Type',
    reflection: 'Reflection',
    
    // Common
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    view: 'View',
    close: 'Close'
  }
};

// Theme configurations
const themes = {
  default: {
    primary: 'bg-blue-600',
    primaryHover: 'hover:bg-blue-700',
    secondary: 'bg-gray-100',
    accent: 'bg-green-500',
    background: 'bg-white',
    surface: 'bg-gray-50',
    text: 'text-gray-900',
    textSecondary: 'text-gray-600',
    border: 'border-gray-200'
  },
  school1: {
    primary: 'bg-purple-600',
    primaryHover: 'hover:bg-purple-700',
    secondary: 'bg-purple-50',
    accent: 'bg-yellow-500',
    background: 'bg-white',
    surface: 'bg-purple-25',
    text: 'text-gray-900',
    textSecondary: 'text-purple-600',
    border: 'border-purple-200'
  },
  school2: {
    primary: 'bg-emerald-600',
    primaryHover: 'hover:bg-emerald-700',
    secondary: 'bg-emerald-50',
    accent: 'bg-orange-500',
    background: 'bg-white',
    surface: 'bg-emerald-25',
    text: 'text-gray-900',
    textSecondary: 'text-emerald-600',
    border: 'border-emerald-200'
  }
};

// Local storage utilities for offline functionality
const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      setStoredValue(value);
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue];
};

// Export utilities
const exportToCSV = (data, filename) => {
  const csvContent = data.map(row => 
    Object.values(row).map(field => 
      typeof field === 'string' ? `"${field.replace(/"/g, '""')}"` : field
    ).join(',')
  ).join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Rubric Builder Component
const RubricBuilder = ({ language, theme, onSave }) => {
  const t = translations[language];
  const [rubric, setRubric] = useLocalStorage('currentRubric', {
    title: '',
    criteria: []
  });

  const addCriteria = () => {
    setRubric({
      ...rubric,
      criteria: [...rubric.criteria, {
        id: Date.now(),
        name: '',
        levels: [
          { id: Date.now() + 1, name: '', description: '', points: 1 },
          { id: Date.now() + 2, name: '', description: '', points: 2 },
          { id: Date.now() + 3, name: '', description: '', points: 3 },
          { id: Date.now() + 4, name: '', description: '', points: 4 }
        ]
      }]
    });
  };

  const updateCriteria = (criteriaId, field, value) => {
    setRubric({
      ...rubric,
      criteria: rubric.criteria.map(c => 
        c.id === criteriaId ? { ...c, [field]: value } : c
      )
    });
  };

  const updateLevel = (criteriaId, levelId, field, value) => {
    setRubric({
      ...rubric,
      criteria: rubric.criteria.map(c => 
        c.id === criteriaId ? {
          ...c,
          levels: c.levels.map(l => 
            l.id === levelId ? { ...l, [field]: value } : l
          )
        } : c
      )
    });
  };

  const deleteCriteria = (criteriaId) => {
    setRubric({
      ...rubric,
      criteria: rubric.criteria.filter(c => c.id !== criteriaId)
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${theme.text}`}>{t.createRubric}</h2>
        <div className="flex gap-2">
          <button
            onClick={() => onSave(rubric)}
            className={`px-4 py-2 ${theme.primary} ${theme.primaryHover} text-white rounded-lg flex items-center gap-2`}
            aria-label={t.saveRubric}
          >
            <Save size={16} />
            {t.save}
          </button>
          <button
            onClick={() => exportToCSV([rubric], 'rubric.csv')}
            className={`px-4 py-2 ${theme.secondary} ${theme.text} rounded-lg flex items-center gap-2`}
            aria-label={t.exportData}
          >
            <Download size={16} />
            {t.exportData}
          </button>
        </div>
      </div>

      <div className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
        <label className={`block text-sm font-medium ${theme.text} mb-2`}>
          {t.rubricTitle}
        </label>
        <input
          type="text"
          value={rubric.title}
          onChange={(e) => setRubric({ ...rubric, title: e.target.value })}
          className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
          aria-label={t.rubricTitle}
        />
      </div>

      <div className="space-y-4">
        {rubric.criteria.map((criteria, criteriaIndex) => (
          <div key={criteria.id} className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
            <div className="flex items-center justify-between mb-4">
              <input
                type="text"
                value={criteria.name}
                onChange={(e) => updateCriteria(criteria.id, 'name', e.target.value)}
                placeholder={t.criteriaName}
                className={`text-lg font-semibold bg-transparent border-b-2 border-dashed ${theme.border} focus:border-blue-500 outline-none flex-1`}
                aria-label={`${t.criteriaName} ${criteriaIndex + 1}`}
              />
              <button
                onClick={() => deleteCriteria(criteria.id)}
                className="text-red-500 hover:text-red-700 p-2"
                aria-label={`${t.delete} ${t.criteriaName} ${criteriaIndex + 1}`}
              >
                <Minus size={16} />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {criteria.levels.map((level, levelIndex) => (
                <div key={level.id} className={`${theme.background} p-4 rounded-lg border ${theme.border}`}>
                  <input
                    type="text"
                    value={level.name}
                    onChange={(e) => updateLevel(criteria.id, level.id, 'name', e.target.value)}
                    placeholder={`${t.levelName} ${level.points}`}
                    className={`w-full font-medium mb-2 bg-transparent border-b ${theme.border} focus:border-blue-500 outline-none`}
                    aria-label={`${t.levelName} ${levelIndex + 1}`}
                  />
                  <textarea
                    value={level.description}
                    onChange={(e) => updateLevel(criteria.id, level.id, 'description', e.target.value)}
                    placeholder={t.levelDescription}
                    rows={3}
                    className={`w-full text-sm ${theme.textSecondary} bg-transparent resize-none outline-none`}
                    aria-label={`${t.levelDescription} ${levelIndex + 1}`}
                  />
                  <div className="mt-2">
                    <span className={`text-xs ${theme.textSecondary}`}>
                      {level.points} {level.points === 1 ? 'poäng' : 'poäng'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <button
          onClick={addCriteria}
          className={`w-full p-4 border-2 border-dashed ${theme.border} rounded-lg ${theme.textSecondary} hover:${theme.secondary} flex items-center justify-center gap-2 transition-colors`}
          aria-label={t.addCriteria}
        >
          <Plus size={20} />
          {t.addCriteria}
        </button>
      </div>
    </div>
  );
};

// Self Assessment Component
const SelfAssessment = ({ language, theme, rubrics }) => {
  const t = translations[language];
  const [selectedRubric, setSelectedRubric] = useState(null);
  const [assessments, setAssessments] = useLocalStorage('selfAssessments', {});
  const [currentAssessment, setCurrentAssessment] = useState({});

  const updateAssessment = (criteriaId, levelId, confidence) => {
    setCurrentAssessment({
      ...currentAssessment,
      [criteriaId]: { levelId, confidence }
    });
  };

  const submitAssessment = () => {
    if (selectedRubric) {
      const assessmentData = {
        rubricId: selectedRubric.id,
        rubricTitle: selectedRubric.title,
        timestamp: new Date().toISOString(),
        assessments: currentAssessment
      };
      
      setAssessments({
        ...assessments,
        [Date.now()]: assessmentData
      });
      
      setCurrentAssessment({});
      alert(language === 'sv' ? 'Bedömning sparad!' : 'Assessment saved!');
    }
  };

  return (
    <div className="space-y-6">
      <h2 className={`text-2xl font-bold ${theme.text}`}>{t.selfAssessment}</h2>

      {!selectedRubric ? (
        <div className="grid gap-4">
          {rubrics.map(rubric => (
            <button
              key={rubric.id}
              onClick={() => setSelectedRubric(rubric)}
              className={`p-4 ${theme.surface} border ${theme.border} rounded-lg text-left hover:${theme.secondary} transition-colors`}
            >
              <h3 className={`font-semibold ${theme.text}`}>{rubric.title}</h3>
              <p className={`text-sm ${theme.textSecondary} mt-1`}>
                {rubric.criteria.length} kriterier
              </p>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className={`text-xl font-semibold ${theme.text}`}>{selectedRubric.title}</h3>
            <button
              onClick={() => setSelectedRubric(null)}
              className={`px-4 py-2 ${theme.secondary} ${theme.text} rounded-lg`}
            >
              {t.close}
            </button>
          </div>

          {selectedRubric.criteria.map(criteria => (
            <div key={criteria.id} className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
              <h4 className={`font-semibold ${theme.text} mb-4`}>{criteria.name}</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
                {criteria.levels.map(level => (
                  <button
                    key={level.id}
                    onClick={() => updateAssessment(criteria.id, level.id, currentAssessment[criteria.id]?.confidence || 50)}
                    className={`p-3 rounded-lg border-2 text-left transition-all ${
                      currentAssessment[criteria.id]?.levelId === level.id
                        ? `${theme.primary.replace('bg-', 'border-')} ${theme.primary} text-white`
                        : `${theme.border} ${theme.background} hover:${theme.secondary}`
                    }`}
                    aria-pressed={currentAssessment[criteria.id]?.levelId === level.id}
                  >
                    <div className="font-medium">{level.name}</div>
                    <div className="text-sm mt-1 opacity-90">{level.description}</div>
                  </button>
                ))}
              </div>

              {currentAssessment[criteria.id] && (
                <div className="mt-4">
                  <label className={`block text-sm font-medium ${theme.text} mb-2`}>
                    {t.confidenceLevel}: {currentAssessment[criteria.id].confidence}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={currentAssessment[criteria.id].confidence}
                    onChange={(e) => updateAssessment(criteria.id, currentAssessment[criteria.id].levelId, parseInt(e.target.value))}
                    className="w-full"
                    aria-label={`${t.confidenceLevel} för ${criteria.name}`}
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{t.veryUnsure}</span>
                    <span>{t.verySure}</span>
                  </div>
                </div>
              )}
            </div>
          ))}

          <button
            onClick={submitAssessment}
            disabled={Object.keys(currentAssessment).length === 0}
            className={`w-full py-3 ${theme.primary} ${theme.primaryHover} text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
          >
            <Check size={16} />
            {t.submitAssessment}
          </button>
        </div>
      )}
    </div>
  );
};

// Peer Feedback Component
const PeerFeedback = ({ language, theme }) => {
  const t = translations[language];
  const [peers] = useLocalStorage('peers', [
    { id: 1, name: 'Anna Andersson' },
    { id: 2, name: 'Erik Johansson' },
    { id: 3, name: 'Sara Lindberg' },
  ]);
  const [feedback, setFeedback] = useLocalStorage('peerFeedback', {});
  const [selectedPeer, setSelectedPeer] = useState(null);
  const [currentFeedback, setCurrentFeedback] = useState({
    strengths: '',
    improvements: '',
    generalComments: ''
  });

  const submitFeedback = () => {
    if (selectedPeer && currentFeedback.strengths) {
      const feedbackData = {
        peerId: selectedPeer.id,
        peerName: selectedPeer.name,
        timestamp: new Date().toISOString(),
        ...currentFeedback
      };
      
      setFeedback({
        ...feedback,
        [Date.now()]: feedbackData
      });
      
      setCurrentFeedback({ strengths: '', improvements: '', generalComments: '' });
      setSelectedPeer(null);
      alert(language === 'sv' ? 'Feedback skickad!' : 'Feedback submitted!');
    }
  };

  return (
    <div className="space-y-6">
      <h2 className={`text-2xl font-bold ${theme.text}`}>{t.peerFeedback}</h2>

      {!selectedPeer ? (
        <div>
          <h3 className={`text-lg font-semibold ${theme.text} mb-4`}>{t.selectPeer}</h3>
          <div className="grid gap-3">
            {peers.map(peer => (
              <button
                key={peer.id}
                onClick={() => setSelectedPeer(peer)}
                className={`p-4 ${theme.surface} border ${theme.border} rounded-lg text-left hover:${theme.secondary} transition-colors flex items-center gap-3`}
              >
                <Users size={20} className={theme.textSecondary} />
                <span className={`font-medium ${theme.text}`}>{peer.name}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className={`text-xl font-semibold ${theme.text}`}>
              {t.feedbackFor}: {selectedPeer.name}
            </h3>
            <button
              onClick={() => setSelectedPeer(null)}
              className={`px-4 py-2 ${theme.secondary} ${theme.text} rounded-lg`}
            >
              {t.close}
            </button>
          </div>

          <div className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
            <label className={`block text-sm font-medium ${theme.text} mb-2`}>
              {t.strengths} *
            </label>
            <textarea
              value={currentFeedback.strengths}
              onChange={(e) => setCurrentFeedback({ ...currentFeedback, strengths: e.target.value })}
              rows={4}
              className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              placeholder={language === 'sv' ? 'Vad gjorde din kamrat bra?' : 'What did your peer do well?'}
              required
            />
          </div>

          <div className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
            <label className={`block text-sm font-medium ${theme.text} mb-2`}>
              {t.improvements}
            </label>
            <textarea
              value={currentFeedback.improvements}
              onChange={(e) => setCurrentFeedback({ ...currentFeedback, improvements: e.target.value })}
              rows={4}
              className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              placeholder={language === 'sv' ? 'Vad kan förbättras?' : 'What could be improved?'}
            />
          </div>

          <div className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
            <label className={`block text-sm font-medium ${theme.text} mb-2`}>
              {language === 'sv' ? 'Allmänna kommentarer' : 'General Comments'}
            </label>
            <textarea
              value={currentFeedback.generalComments}
              onChange={(e) => setCurrentFeedback({ ...currentFeedback, generalComments: e.target.value })}
              rows={3}
              className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              placeholder={language === 'sv' ? 'Övriga kommentarer...' : 'Additional comments...'}
            />
          </div>

          <button
            onClick={submitFeedback}
            disabled={!currentFeedback.strengths.trim()}
            className={`w-full py-3 ${theme.primary} ${theme.primaryHover} text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
          >
            <Share2 size={16} />
            {language === 'sv' ? 'Skicka Feedback' : 'Submit Feedback'}
          </button>
        </div>
      )}
    </div>
  );
};

// Portfolio Component
const Portfolio = ({ language, theme }) => {
  const t = translations[language];
  const [portfolio, setPortfolio] = useLocalStorage('portfolio', []);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEvidence, setNewEvidence] = useState({
    title: '',
    type: 'assignment',
    description: '',
    reflection: '',
    files: []
  });

  const addEvidence = () => {
    const evidence = {
      id: Date.now(),
      ...newEvidence,
      timestamp: new Date().toISOString()
    };
    
    setPortfolio([...portfolio, evidence]);
    setNewEvidence({
      title: '',
      type: 'assignment',
      description: '',
      reflection: '',
      files: []
    });
    setShowAddForm(false);
  };

  const evidenceTypes = [
    { value: 'assignment', label: language === 'sv' ? 'Uppgift' : 'Assignment' },
    { value: 'project', label: language === 'sv' ? 'Projekt' : 'Project' },
    { value: 'reflection', label: language === 'sv' ? 'Reflektion' : 'Reflection' },
    { value: 'presentation', label: language === 'sv' ? 'Presentation' : 'Presentation' },
    { value: 'other', label: language === 'sv' ? 'Annat' : 'Other' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${theme.text}`}>{t.portfolio}</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className={`px-4 py-2 ${theme.primary} ${theme.primaryHover} text-white rounded-lg flex items-center gap-2`}
        >
          <Plus size={16} />
          {t.addEvidence}
        </button>
      </div>

      {showAddForm && (
        <div className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
          <h3 className={`text-lg font-semibold ${theme.text} mb-4`}>{t.addEvidence}</h3>
          
          <div className="space-y-4">
            <div>
              <label className={`block text-sm font-medium ${theme.text} mb-2`}>
                {t.evidenceTitle} *
              </label>
              <input
                type="text"
                value={newEvidence.title}
                onChange={(e) => setNewEvidence({ ...newEvidence, title: e.target.value })}
                className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                required
              />
            </div>

            <div>
              <label className={`block text-sm font-medium ${theme.text} mb-2`}>
                {t.evidenceType}
              </label>
              <select
                value={newEvidence.type}
                onChange={(e) => setNewEvidence({ ...newEvidence, type: e.target.value })}
                className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              >
                {evidenceTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className={`block text-sm font-medium ${theme.text} mb-2`}>
                {language === 'sv' ? 'Beskrivning' : 'Description'}
              </label>
              <textarea
                value={newEvidence.description}
                onChange={(e) => setNewEvidence({ ...newEvidence, description: e.target.value })}
                rows={3}
                className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
              />
            </div>

            <div>
              <label className={`block text-sm font-medium ${theme.text} mb-2`}>
                {t.reflection}
              </label>
              <textarea
                value={newEvidence.reflection}
                onChange={(e) => setNewEvidence({ ...newEvidence, reflection: e.target.value })}
                rows={4}
                className={`w-full p-3 border ${theme.border} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                placeholder={language === 'sv' ? 'Vad lärde du dig? Hur utvecklades du?' : 'What did you learn? How did you develop?'}
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={addEvidence}
                disabled={!newEvidence.title.trim()}
                className={`px-4 py-2 ${theme.primary} ${theme.primaryHover} text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {t.save}
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className={`px-4 py-2 ${theme.secondary} ${theme.text} rounded-lg`}
              >
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {portfolio.map(evidence => (
          <div key={evidence.id} className={`${theme.surface} p-6 rounded-lg border ${theme.border}`}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className={`font-semibold ${theme.text}`}>{evidence.title}</h3>
                <p className={`text-sm ${theme.textSecondary} mt-1`}>
                  {evidenceTypes.find(t => t.value === evidence.type)?.label
