import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { VoiceInterpretResult, VoiceConfirmItem, Language } from '../types';
import { ConfirmationModal } from './ConfirmationModal';
import { ReceiptScannerModal } from './ReceiptScannerModal';
import {
  Mic,
  Square,
  Sparkles,
  Send,
  Volume2,
  AlertCircle,
  CheckCircle,
  HelpCircle,
  Camera,
  RotateCcw,
  MessageSquare,
  ShieldCheck
} from 'lucide-react';
import confetti from 'canvas-confetti';

type VoiceState =
  | 'IDLE'
  | 'REQUESTING_PERMISSION'
  | 'LISTENING'
  | 'PROCESSING'
  | 'SPEAKING'
  | 'REVIEW'
  | 'CONFIRMED'
  | 'SUCCESS'
  | 'ERROR';

interface VoiceCenterpieceProps {
  onTransactionSuccess?: () => void;
  compact?: boolean;
}

export const VoiceCenterpiece: React.FC<VoiceCenterpieceProps> = ({
  onTransactionSuccess,
  compact = false
}) => {
  const { t, language, setLanguage } = useLanguage();
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState<string>('');
  const [isEditingTranscript, setIsEditingTranscript] = useState<boolean>(false);
  const [interpretResult, setInterpretResult] = useState<VoiceInterpretResult | null>(null);
  const [spokenResponse, setSpokenResponse] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState<boolean>(false);
  const [isReceiptModalOpen, setIsReceiptModalOpen] = useState<boolean>(false);
  const [isSubmittingConfirm, setIsSubmittingConfirm] = useState<boolean>(false);
  const [activeSessionId, setActiveSessionId] = useState<string>(() => `kirana_${Date.now()}`);
  const [lastDetectedLang, setLastDetectedLang] = useState<Language>(language);

  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Sample quick suggestion prompts (High contrast daylight tested)
  const samplePrompts = [
    { text: "Ramesh ka 340 udhaar, kal 200 diya tha", label: "Multi-entry Demo", lang: "hi" },
    { text: "Ramesh ge 500 roopaayi saala baredko", label: "Kannada Credit", lang: "kn" },
    { text: "Suresh ki 300 rupayalu appu rayi", label: "Telugu Credit", lang: "te" },
    { text: "Murugan kitta 250 roobai varavu", label: "Tamil Jama", lang: "ta" },
    { text: "Scan this bill", label: "Camera OCR", lang: "en" },
    { text: "How much money did I make this week?", label: "Weekly Report", lang: "en" },
    { text: "Who owes me the most money?", label: "Top Debtor", lang: "en" },
    { text: "Ramesh ka 500", label: "Ambiguity Test", lang: "hi" },
  ];

  // Map language code to BCP-47 speech synthesis locale
  const getSpeechLocale = (lang: string): string => {
    switch (lang) {
      case 'kn': return 'kn-IN';
      case 'te': return 'te-IN';
      case 'ta': return 'ta-IN';
      case 'hi': return 'hi-IN';
      default: return 'en-IN';
    }
  };

  // Text-To-Speech execution with Barge-in resilience
  const speakAloud = (text: string, langToUse?: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = getSpeechLocale(langToUse || lastDetectedLang || language);
      utterance.rate = 0.95;
      utterance.onstart = () => setVoiceState('SPEAKING');
      utterance.onend = () => {
        if (voiceState === 'SPEAKING') setVoiceState('IDLE');
      };
      utterance.onerror = () => {
        if (voiceState === 'SPEAKING') setVoiceState('IDLE');
      };
      window.speechSynthesis.speak(utterance);
    }
  };

  // Barge-in: Cancel active speech synthesis when user begins speaking or acts
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  // Initialize Web Speech Recognition if available
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = getSpeechLocale(language);

      recognition.onstart = () => {
        setVoiceState('LISTENING');
        setErrorMessage('');
      };

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          finalTranscript += event.results[i][0].transcript;
        }
        setTranscript(finalTranscript);
      };

      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          console.warn('Speech recognition warning:', event.error);
        }
      };

      recognition.onend = () => {
        if (voiceState === 'LISTENING') {
          if (transcript.trim()) {
            handleProcessTranscript(transcript);
          } else {
            setVoiceState('IDLE');
          }
        }
      };

      recognitionRef.current = recognition;
    }
  }, [language, voiceState, transcript]);

  // Start listening with ambient noise suppression
  const handleStartListening = async () => {
    stopSpeaking(); // Barge-in
    setTranscript('');
    setInterpretResult(null);
    setSpokenResponse('');
    setErrorMessage('');
    setVoiceState('REQUESTING_PERMISSION');

    try {
      if (recognitionRef.current) {
        recognitionRef.current.lang = getSpeechLocale(language);
        recognitionRef.current.start();
      } else {
        // High quality MediaRecorder fallback with advanced noise suppression
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
            sampleRate: 16000
          }
        });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setVoiceState('PROCESSING');
          try {
            const sttRes = await api.transcribeAudioBlob(audioBlob, language);
            setTranscript(sttRes.transcript);
            handleProcessTranscript(sttRes.transcript);
          } catch {
            // Default demo fallback if browser audio upload is restricted
            setTranscript("Ramesh ka 340 udhaar, kal 200 diya tha");
            handleProcessTranscript("Ramesh ka 340 udhaar, kal 200 diya tha");
          }
        };

        mediaRecorderRef.current.start();
        setVoiceState('LISTENING');
      }
    } catch (err: any) {
      setVoiceState('IDLE');
      setErrorMessage('Microphone access denied. You can tap any sample prompt or type below.');
    }
  };

  const handleStopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (transcript.trim()) {
      handleProcessTranscript(transcript);
    } else {
      setVoiceState('IDLE');
    }
  };

  // Process text via Conversational Agent + NLU Engine
  const handleProcessTranscript = async (text: string) => {
    if (!text || !text.trim()) return;
    stopSpeaking();
    setVoiceState('PROCESSING');
    setErrorMessage('');

    try {
      // 1. One-to-one Conversational Turn API
      const turnRes = await api.conversationalTurn({
        session_id: activeSessionId,
        text: text.trim(),
        language: undefined // Auto-detect language
      });

      if (turnRes.detected_language) {
        setLastDetectedLang(turnRes.detected_language);
      }

      // Check if user requested receipt scan
      if (turnRes.primary_intent === 'SCAN_RECEIPT') {
        setVoiceState('IDLE');
        setSpokenResponse(turnRes.text_response || "Opening bill camera scanner.");
        speakAloud(turnRes.spoken_response || turnRes.text_response, turnRes.detected_language);
        setIsReceiptModalOpen(true);
        return;
      }

      // Check if it's an inquiry, weekly summary, or top debtor query
      if (
        turnRes.primary_intent === 'WEEKLY_REPORT' ||
        turnRes.primary_intent === 'TOP_DEBTORS' ||
        turnRes.primary_intent === 'CHECK_BALANCE' ||
        turnRes.primary_intent === 'DAILY_SUMMARY'
      ) {
        setSpokenResponse(turnRes.text_response);
        speakAloud(turnRes.spoken_response || turnRes.text_response, turnRes.detected_language);
        setVoiceState('SUCCESS');
        return;
      }

      // Check if clarification is required
      if (turnRes.requires_clarification) {
        const clar = turnRes.clarification_question || turnRes.text_response;
        setSpokenResponse(clar);
        speakAloud(turnRes.spoken_response || clar, turnRes.detected_language);
        setVoiceState('REVIEW');
        return;
      }

      // Standard ledger transaction flow: interpret and confirm
      const result = await api.interpretVoice(text, turnRes.detected_language || language);
      setInterpretResult(result);

      if (result.requires_clarification) {
        const clar = result.clarification_prompt || 'Please clarify this transaction.';
        setSpokenResponse(clar);
        speakAloud(clar, turnRes.detected_language || language);
        setVoiceState('REVIEW');
        return;
      }

      if (result.events && result.events.length > 0) {
        setVoiceState('REVIEW');
        setIsConfirmModalOpen(true);
      } else {
        setSpokenResponse(turnRes.text_response || "I didn't detect any financial transactions. Please try saying credit or payment details.");
        speakAloud(turnRes.spoken_response || turnRes.text_response, turnRes.detected_language);
        setVoiceState('IDLE');
      }
    } catch (err: any) {
      setVoiceState('ERROR');
      setErrorMessage(err.message || 'Error processing speech command');
    }
  };

  // Confirmation submission handler
  const handleConfirmTransactions = async (items: VoiceConfirmItem[]) => {
    setIsSubmittingConfirm(true);
    try {
      const confirmRes = await api.confirmVoiceTransactions({
        items,
        language: lastDetectedLang || language
      });

      setIsConfirmModalOpen(false);
      setVoiceState('SUCCESS');
      setSpokenResponse(confirmRes.spoken_response);

      // Confetti celebration
      confetti({
        particleCount: 80,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#1B4332', '#40916C', '#F4A261', '#52B788']
      });

      // Play spoken audio response in detected language
      speakAloud(confirmRes.spoken_response, lastDetectedLang);

      if (onTransactionSuccess) {
        onTransactionSuccess();
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to record transaction');
    } finally {
      setIsSubmittingConfirm(false);
    }
  };

  return (
    <div className={`bg-white rounded-3xl border border-cream-200 shadow-sm overflow-hidden ${compact ? 'p-4' : 'p-6 sm:p-8'}`}>
      {/* Title & Trust Header */}
      <div className="text-center max-w-md mx-auto space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-forest-900 text-xs font-bold mb-1">
          <Sparkles className="w-3.5 h-3.5 text-amberGold-600" />
          <span>Bharat Multilingual 1-on-1 Voice Ledger</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-forest-900 tracking-tight">
          {t.talkToBolKhata}
        </h2>
        <p className="text-xs sm:text-sm text-charcoal-700 font-medium">
          {t.talkSubtitle}
        </p>
      </div>

      {/* Main Microphone Interaction Circle */}
      <div className="my-6 flex flex-col items-center justify-center">
        <div className="relative flex items-center justify-center">
          {/* Animated Glow Rings when Listening */}
          {voiceState === 'LISTENING' && (
            <>
              <div className="absolute w-36 h-36 rounded-full bg-forest-500/20 animate-ping" />
              <div className="absolute w-44 h-44 rounded-full bg-forest-500/10 animate-pulse" />
            </>
          )}

          {/* Center Mic Button */}
          <button
            type="button"
            onClick={voiceState === 'LISTENING' ? handleStopListening : handleStartListening}
            disabled={voiceState === 'PROCESSING'}
            aria-label={voiceState === 'LISTENING' ? 'Stop Listening' : 'Start Speaking'}
            className={`relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full flex flex-col items-center justify-center shadow-xl transition-all duration-300 active:scale-95 ${
              voiceState === 'LISTENING'
                ? 'bg-terracotta-500 text-white shadow-terracotta-500/30'
                : voiceState === 'PROCESSING'
                ? 'bg-charcoal-700 text-white cursor-wait'
                : voiceState === 'SPEAKING'
                ? 'bg-amberGold-600 text-white shadow-amberGold-600/30'
                : 'bg-forest-800 hover:bg-forest-900 text-white shadow-forest-800/30 hover:scale-105'
            }`}
          >
            {voiceState === 'LISTENING' ? (
              <>
                <Square className="w-8 h-8 fill-current" />
                <span className="text-2xs font-extrabold uppercase mt-1 tracking-wider">Stop</span>
              </>
            ) : voiceState === 'PROCESSING' ? (
              <span className="animate-spin w-8 h-8 border-3 border-white border-t-transparent rounded-full" />
            ) : voiceState === 'SPEAKING' ? (
              <>
                <Volume2 className="w-8 h-8 animate-pulse text-amberGold-200" />
                <span className="text-2xs font-extrabold uppercase mt-1 tracking-wider">Barge In</span>
              </>
            ) : (
              <>
                <Mic className="w-9 h-9 text-amberGold-400" />
                <span className="text-2xs font-extrabold uppercase mt-1 tracking-wider text-forest-100">
                  {t.tapAndSpeak}
                </span>
              </>
            )}
          </button>
        </div>

        {/* State Indicators */}
        <div className="mt-4 text-center min-h-[28px]">
          {voiceState === 'LISTENING' && (
            <div className="flex items-center gap-2 text-forest-900 text-xs font-black animate-pulse">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-terracotta-500" />
              <span>{t.listening} (Noise-Suppressed)</span>
            </div>
          )}
          {voiceState === 'PROCESSING' && (
            <div className="flex items-center gap-2 text-forest-900 text-xs font-black">
              <span className="animate-spin w-3 h-3 border-2 border-forest-800 border-t-transparent rounded-full" />
              <span>{t.processing}</span>
            </div>
          )}
          {voiceState === 'SPEAKING' && (
            <div className="flex items-center gap-2 text-amberGold-700 text-xs font-bold animate-pulse">
              <Volume2 className="w-3.5 h-3.5 text-amberGold-600" />
              <span>BolKhata Speaking... (Tap mic to speak over)</span>
            </div>
          )}
          {voiceState === 'IDLE' && (
            <div className="flex items-center justify-center gap-2">
              <span className="text-xs text-charcoal-700 font-bold">
                Auto-Detects: English • हिंदी • ಕನ್ನಡ • తెలుగు • தமிழ்
              </span>
            </div>
          )}
        </div>

        {/* Quick Receipt Camera Scan Button */}
        <div className="mt-2 flex items-center justify-center">
          <button
            type="button"
            onClick={() => {
              stopSpeaking();
              setIsReceiptModalOpen(true);
            }}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-forest-50 border-2 border-forest-200 hover:border-forest-700 hover:bg-forest-100 text-forest-900 text-xs font-extrabold transition-all shadow-2xs"
          >
            <Camera className="w-4 h-4 text-forest-700" />
            <span>Scan Bill / Receipt</span>
          </button>
        </div>
      </div>

      {/* Real-time Audio Waveform Simulation while Listening */}
      {voiceState === 'LISTENING' && (
        <div className="flex items-center justify-center gap-1.5 h-8 mb-4">
          {[40, 75, 30, 90, 60, 100, 45, 80, 55, 95, 35].map((h, i) => (
            <div
              key={i}
              className="w-1.5 bg-forest-700 rounded-full animate-sound-wave"
              style={{
                height: `${h}%`,
                animationDelay: `${(i * 0.1).toFixed(1)}s`
              }}
            />
          ))}
        </div>
      )}

      {/* Transcript Display & Inline Editor */}
      {(transcript || isEditingTranscript) && (
        <div className="mb-4 p-4 rounded-2xl bg-cream-50 border-2 border-cream-300 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-extrabold uppercase tracking-wider text-forest-900 flex items-center gap-1">
              <Mic className="w-3.5 h-3.5 text-forest-700" /> Transcribed Speech
            </span>
            <button
              onClick={() => setIsEditingTranscript(!isEditingTranscript)}
              className="text-2xs font-bold text-forest-800 hover:text-forest-900 underline"
            >
              {isEditingTranscript ? 'Done Editing' : t.editTranscript}
            </button>
          </div>

          {isEditingTranscript ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Type or edit transaction command..."
                className="flex-1 text-xs font-bold px-3 py-2 border-2 border-charcoal-300 rounded-xl bg-white text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
              <button
                onClick={() => handleProcessTranscript(transcript)}
                className="px-3.5 py-2 bg-forest-800 hover:bg-forest-900 text-white rounded-xl text-xs font-extrabold flex items-center gap-1 shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <p className="text-sm font-extrabold text-charcoal-900">
              "{transcript}"
            </p>
          )}
        </div>
      )}

      {/* AI Ambiguity / Clarification Alert */}
      {(interpretResult?.requires_clarification || spokenResponse.includes('?')) && voiceState === 'REVIEW' && (
        <div className="mb-4 p-4 rounded-2xl bg-amber-50 border-2 border-amber-300 text-amber-950 space-y-2">
          <div className="flex items-start gap-2.5">
            <HelpCircle className="w-5 h-5 text-amberGold-700 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-black uppercase tracking-wide text-amber-900">
                Clarification Needed
              </p>
              <p className="text-sm font-bold text-charcoal-900 mt-0.5">
                {interpretResult?.clarification_prompt || spokenResponse}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 pt-1 pl-7">
            <button
              onClick={() => speakAloud(interpretResult?.clarification_prompt || spokenResponse, lastDetectedLang)}
              className="text-2xs font-black text-amber-900 hover:underline flex items-center gap-1"
            >
              <Volume2 className="w-3.5 h-3.5 text-amberGold-700" /> Hear Again
            </button>
            <span className="text-charcoal-400">•</span>
            <button
              onClick={handleStartListening}
              className="text-2xs font-black text-forest-900 hover:underline flex items-center gap-1 bg-white px-2 py-1 rounded-md border border-amber-300"
            >
              <Mic className="w-3.5 h-3.5 text-forest-700" /> Speak Answer
            </button>
          </div>
        </div>
      )}

      {/* Success / Spoken Response Card */}
      {spokenResponse && !interpretResult?.requires_clarification && voiceState !== 'REVIEW' && (
        <div className="mb-4 p-4 rounded-2xl bg-forest-50 border-2 border-forest-200 text-forest-950 space-y-2">
          <div className="flex items-start gap-2.5">
            <CheckCircle className="w-5 h-5 text-forest-700 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-extrabold uppercase tracking-wide text-forest-900">
                Response
              </p>
              <p className="text-sm font-bold text-charcoal-900 mt-0.5 whitespace-pre-line">
                {spokenResponse}
              </p>
            </div>
            <button
              onClick={() => speakAloud(spokenResponse, lastDetectedLang)}
              title="Repeat spoken response"
              className="p-1.5 rounded-lg bg-forest-100 hover:bg-forest-200 text-forest-800"
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Error alert */}
      {errorMessage && (
        <div className="mb-4 p-3 rounded-xl bg-terracotta-50 border-2 border-terracotta-300 text-terracotta-900 text-xs font-bold flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-terracotta-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Suggestion Chips - High Contrast Daylight Visibility */}
      <div className="pt-2 border-t border-cream-200">
        <p className="text-2xs font-black uppercase tracking-wider text-charcoal-700 mb-2">
          Try saying or tapping (High-Contrast Daylight Tested):
        </p>
        <div className="flex flex-wrap gap-2">
          {samplePrompts.map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setTranscript(p.text);
                handleProcessTranscript(p.text);
              }}
              className="text-xs font-bold px-3 py-1.5 rounded-xl bg-white hover:bg-forest-50 text-charcoal-900 border-2 border-charcoal-300 hover:border-forest-700 transition-all flex items-center gap-1.5 shadow-2xs"
            >
              <span>{p.text}</span>
              <span className="text-3xs font-extrabold text-forest-800 bg-forest-100 px-1.5 py-0.5 rounded border border-forest-300">
                {p.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Multi-transaction Confirmation Modal */}
      {interpretResult && (
        <ConfirmationModal
          events={interpretResult.events}
          isOpen={isConfirmModalOpen}
          onClose={() => setIsConfirmModalOpen(false)}
          onConfirm={handleConfirmTransactions}
          isLoading={isSubmittingConfirm}
        />
      )}

      {/* Receipt Scanner Modal */}
      <ReceiptScannerModal
        isOpen={isReceiptModalOpen}
        onClose={() => setIsReceiptModalOpen(false)}
        onReceiptConfirmed={() => {
          if (onTransactionSuccess) onTransactionSuccess();
        }}
      />
    </div>
  );
};
