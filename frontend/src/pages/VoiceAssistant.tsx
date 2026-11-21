import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { VoiceCenterpiece } from '../components/VoiceCenterpiece';
import { api } from '../services/api';
import {
  Mic,
  Sparkles,
  HelpCircle,
  TrendingUp,
  Coins,
  History,
  Volume2
} from 'lucide-react';

export const VoiceAssistant: React.FC = () => {
  const { t, language } = useLanguage();
  const [qaHistory, setQaHistory] = useState<Array<{ q: string; a: string; time: string }>>([
    {
      q: "Who owes me the most money?",
      a: "Kumar owes the most money, with an outstanding balance of ₹1,200.",
      time: "Earlier today"
    }
  ]);
  const [activeQuery, setActiveQuery] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);

  const predefinedQuestions = [
    { q: "Who owes me the most money?", label: "Top Debtor" },
    { q: "How much did I collect today?", label: "Today's Collections" },
    { q: "How much credit did I give today?", label: "Today's Credit" },
    { q: "Ramesh ka kitna baaki hai?", label: "Ramesh Balance" },
  ];

  const handleAskQuestion = async (questionText: string) => {
    setActiveQuery(questionText);
    setIsQuerying(true);
    try {
      const res = await api.queryAssistant(questionText, language);
      setQaHistory(prev => [
        {
          q: questionText,
          a: res.answer,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
        ...prev
      ]);

      // Speak aloud
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const ut = new SpeechSynthesisUtterance(res.spoken_answer || res.answer);
        ut.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
        window.speechSynthesis.speak(ut);
      }
    } catch (err: any) {
      alert('Error fetching answer: ' + err.message);
    } finally {
      setIsQuerying(false);
      setActiveQuery('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8 animate-in fade-in">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-forest-100 text-forest-800 text-xs font-bold mb-2">
          <Sparkles className="w-3.5 h-3.5 text-amberGold-600" />
          <span>Multilingual Voice Cockpit</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          {t.voiceAssistant}
        </h1>
        <p className="text-xs sm:text-sm text-charcoal-600">
          Record dual-event ledger entries, ask balance questions, and hear spoken answers in your mother tongue.
        </p>
      </div>

      {/* Main Microphone Centerpiece Component */}
      <VoiceCenterpiece />

      {/* Financial Assistant Q&A Section (PART 14) */}
      <div className="bg-white rounded-2xl border border-cream-200 p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-cream-200 pb-3">
          <div className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-forest-700" />
            <h2 className="text-sm sm:text-base font-bold text-forest-900">
              Ask Your Digital Ledger (Q&A)
            </h2>
          </div>
          <span className="text-2xs text-forest-700 font-semibold bg-forest-50 px-2 py-0.5 rounded">
            SQL & Real Database
          </span>
        </div>

        <p className="text-xs text-charcoal-600">
          Tap any of these common shopkeeper queries or speak them aloud:
        </p>

        {/* Suggestion questions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {predefinedQuestions.map((item, idx) => (
            <button
              key={idx}
              onClick={() => handleAskQuestion(item.q)}
              disabled={isQuerying}
              className="p-3 text-left rounded-xl bg-cream-50 hover:bg-forest-50 border border-cream-200 hover:border-forest-200 transition-all flex items-center justify-between group text-xs font-semibold text-charcoal-800"
            >
              <span>{item.q}</span>
              <span className="text-3xs font-bold text-forest-800 bg-forest-100 px-2 py-0.5 rounded group-hover:scale-105 transition-transform">
                {item.label}
              </span>
            </button>
          ))}
        </div>

        {/* Query conversation history */}
        <div className="space-y-3 pt-3 border-t border-cream-200/80">
          <h3 className="text-2xs font-bold uppercase tracking-wider text-charcoal-500">
            Assistant Conversation History
          </h3>
          <div className="space-y-2.5">
            {qaHistory.map((item, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-cream-50/60 border border-cream-200 space-y-1">
                <div className="flex items-center justify-between text-2xs text-charcoal-500 font-medium">
                  <span className="font-bold text-forest-900">You: "{item.q}"</span>
                  <span>{item.time}</span>
                </div>
                <div className="flex items-start justify-between gap-2">
                  <p className="text-xs font-semibold text-charcoal-800">
                    <strong className="text-forest-700">BolKhata:</strong> {item.a}
                  </p>
                  <button
                    onClick={() => {
                      if ('speechSynthesis' in window) {
                        window.speechSynthesis.cancel();
                        const ut = new SpeechSynthesisUtterance(item.a);
                        ut.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
                        window.speechSynthesis.speak(ut);
                      }
                    }}
                    title="Speak answer"
                    className="p-1 text-forest-700 hover:bg-cream-200 rounded"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
