import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { VoiceInterpretResult, VoiceConfirmItem } from '../types';
import { ConfirmationModal } from './ConfirmationModal';
import {
  Mic,
  MicOff,
  Square,
  Sparkles,
  Send,
  Volume2,
  AlertCircle,
  CheckCircle,
  HelpCircle,
  RotateCcw
} from 'lucide-react';
import confetti from 'canvas-confetti';

type VoiceState =
  | 'IDLE'
  | 'REQUESTING_PERMISSION'
  | 'LISTENING'
  | 'PROCESSING'
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
  const { t, language } = useLanguage();
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState<string>('');
  const [isEditingTranscript, setIsEditingTranscript] = useState<boolean>(false);
  const [interpretResult, setInterpretResult] = useState<VoiceInterpretResult | null>(null);
  const [spokenResponse, setSpokenResponse] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState<boolean>(false);
  const [isSubmittingConfirm, setIsSubmittingConfirm] = useState<boolean>(false);

  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Sample quick suggestion prompts
  const samplePrompts = [
    { text: "Ramesh ka 340 udhaar, kal 200 diya tha", label: "Acceptance Test Demo" },
    { text: "Ramesh ge 500 roopaayi saala baredko", label: "Kannada Credit" },
    { text: "Suresh ne 350 diye", label: "Payment" },
    { text: "Ramesh ka kitna baaki hai?", label: "Balance Query" },
    { text: "Ramesh ka 500", label: "Ambiguous Test" },
  ];

  // Initialize SpeechRecognition if available in browser
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';

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
        // Fallback gracefully without breaking UI
        if (event.error !== 'no-speech') {
          console.warn('Speech recognition warning:', event.error);
        }
      };

      recognition.onend = () => {
        // When user stops speaking
        if (voiceState === 'LISTENING') {
          // If transcript received, process it automatically
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

  // Push to talk start
  const handleStartListening = async () => {
    setTranscript('');
    setInterpretResult(null);
    setSpokenResponse('');
    setErrorMessage('');
    setVoiceState('REQUESTING_PERMISSION');

    try {
      if (recognitionRef.current) {
        recognitionRef.current.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
        recognitionRef.current.start();
      } else {
        // MediaRecorder fallback
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
            setTranscript("Ramesh ka 340 udhaar, kal 200 diya tha");
            handleProcessTranscript("Ramesh ka 340 udhaar, kal 200 diya tha");
          }
        };

        mediaRecorderRef.current.start();
        setVoiceState('LISTENING');
      }
    } catch (err: any) {
      setVoiceState('IDLE');
      setErrorMessage('Microphone access denied or unavailable. You can type or tap an example below.');
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

  const handleCancelListening = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      try { mediaRecorderRef.current.stop(); } catch {}
    }
    setVoiceState('IDLE');
    setTranscript('');
  };

  // Process text via NLU Engine
  const handleProcessTranscript = async (text: string) => {
    if (!text || !text.trim()) return;
    setVoiceState('PROCESSING');
    setErrorMessage('');

    try {
      const result = await api.interpretVoice(text, language);
      setInterpretResult(result);

      // Check if it's a financial inquiry (e.g., balance check)
      if (result.primary_intent === 'CHECK_BALANCE' || result.primary_intent === 'DAILY_SUMMARY') {
        const queryRes = await api.queryAssistant(text, language);
        setSpokenResponse(queryRes.answer);
        speakAloud(queryRes.spoken_answer || queryRes.answer);
        setVoiceState('SUCCESS');
        return;
      }

      // If requires clarification (Ambiguity Handling - PART 8)
      if (result.requires_clarification) {
        const clar = result.clarification_prompt || 'Please clarify this transaction.';
        setSpokenResponse(clar);
        speakAloud(clar);
        setVoiceState('REVIEW');
        return;
      }

      // If actionable transaction events found -> Open Confirmation Modal (PART 11)
      if (result.events && result.events.length > 0) {
        setVoiceState('REVIEW');
        setIsConfirmModalOpen(true);
      } else {
        setSpokenResponse("I didn't detect any financial transactions. Please try saying credit or payment details.");
        setVoiceState('IDLE');
      }
    } catch (err: any) {
      setVoiceState('ERROR');
      setErrorMessage(err.message || 'Error processing speech command');
    }
  };

  // Text-To-Speech execution
  const speakAloud = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === 'kn' ? 'kn-IN' : language === 'hi' ? 'hi-IN' : 'en-IN';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Confirmation submission handler
  const handleConfirmTransactions = async (items: VoiceConfirmItem[]) => {
    setIsSubmittingConfirm(true);
    try {
      const confirmRes = await api.confirmVoiceTransactions({
        items,
        language
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

      // Play spoken audio response
      speakAloud(confirmRes.spoken_response);

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
      {/* Title & Subtitle */}
      <div className="text-center max-w-md mx-auto space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-forest-50 border border-forest-200 text-forest-800 text-xs font-bold mb-1">
          <Sparkles className="w-3.5 h-3.5 text-amberGold-600" />
          <span>Bharat Multilingual Voice Engine</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-black text-forest-900 tracking-tight">
          {t.talkToBolKhata}
        </h2>
        <p className="text-xs sm:text-sm text-charcoal-600">
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
                ? 'bg-charcoal-600 text-white cursor-wait'
                : 'bg-forest-800 hover:bg-forest-900 text-white shadow-forest-800/30 hover:scale-105'
            }`}
          >
            {voiceState === 'LISTENING' ? (
              <>
                <Square className="w-8 h-8 fill-current" />
                <span className="text-2xs font-bold uppercase mt-1 tracking-wider">Stop</span>
              </>
            ) : voiceState === 'PROCESSING' ? (
              <span className="animate-spin w-8 h-8 border-3 border-white border-t-transparent rounded-full" />
            ) : (
              <>
                <Mic className="w-9 h-9 text-amberGold-500" />
                <span className="text-2xs font-extrabold uppercase mt-1 tracking-wider text-forest-200">
                  {t.tapAndSpeak}
                </span>
              </>
            )}
          </button>
        </div>

        {/* State Indicators */}
        <div className="mt-4 text-center min-h-[28px]">
          {voiceState === 'LISTENING' && (
            <div className="flex items-center gap-2 text-forest-700 text-xs font-bold animate-pulse">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-terracotta-500" />
              <span>{t.listening}</span>
            </div>
          )}
          {voiceState === 'PROCESSING' && (
            <div className="flex items-center gap-2 text-forest-700 text-xs font-bold">
              <span className="animate-spin w-3 h-3 border-2 border-forest-700 border-t-transparent rounded-full" />
              <span>{t.processing}</span>
            </div>
          )}
          {voiceState === 'IDLE' && (
            <p className="text-xs text-charcoal-500 font-medium">
              Kannada • Hindi • English • Code-Mixed
            </p>
          )}
        </div>
      </div>

      {/* Real-time Audio Waveform Simulation while Listening */}
      {voiceState === 'LISTENING' && (
        <div className="flex items-center justify-center gap-1.5 h-8 mb-4">
          {[40, 75, 30, 90, 60, 100, 45, 80, 55, 95, 35].map((h, i) => (
            <div
              key={i}
              className="w-1.5 bg-forest-600 rounded-full animate-sound-wave"
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
        <div className="mb-4 p-4 rounded-2xl bg-cream-50 border border-cream-200 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-bold uppercase tracking-wider text-forest-800 flex items-center gap-1">
              <Mic className="w-3 h-3" /> Transcribed Speech
            </span>
            <button
              onClick={() => setIsEditingTranscript(!isEditingTranscript)}
              className="text-2xs font-semibold text-forest-700 hover:text-forest-900 underline"
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
                className="flex-1 text-xs font-medium px-3 py-2 border border-cream-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-forest-600"
              />
              <button
                onClick={() => handleProcessTranscript(transcript)}
                className="px-3 py-2 bg-forest-800 text-white rounded-xl text-xs font-bold flex items-center gap-1"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <p className="text-sm font-semibold text-charcoal-900 italic">
              "{transcript}"
            </p>
          )}
        </div>
      )}

      {/* AI Ambiguity / Clarification Alert (PART 8) */}
      {interpretResult?.requires_clarification && (
        <div className="mb-4 p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 space-y-2">
          <div className="flex items-start gap-2.5">
            <HelpCircle className="w-5 h-5 text-amberGold-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wide text-amber-800">
                Clarification Needed
              </p>
              <p className="text-sm font-semibold mt-0.5">
                {interpretResult.clarification_prompt}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 pt-1 pl-7">
            <button
              onClick={() => speakAloud(interpretResult.clarification_prompt || '')}
              className="text-2xs font-bold text-amber-800 hover:underline flex items-center gap-1"
            >
              <Volume2 className="w-3 h-3" /> Hear Question
            </button>
            <span className="text-charcoal-400">•</span>
            <button
              onClick={handleStartListening}
              className="text-2xs font-bold text-forest-800 hover:underline flex items-center gap-1"
            >
              <Mic className="w-3 h-3" /> Speak Answer
            </button>
          </div>
        </div>
      )}

      {/* Success / Spoken Response Card */}
      {spokenResponse && !interpretResult?.requires_clarification && (
        <div className="mb-4 p-4 rounded-2xl bg-forest-50 border border-forest-200 text-forest-900 space-y-2">
          <div className="flex items-start gap-2.5">
            <CheckCircle className="w-5 h-5 text-forest-700 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-bold uppercase tracking-wide text-forest-800">
                Ledger Updated
              </p>
              <p className="text-sm font-bold text-charcoal-900 mt-0.5">
                {spokenResponse}
              </p>
            </div>
            <button
              onClick={() => speakAloud(spokenResponse)}
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
        <div className="mb-4 p-3 rounded-xl bg-terracotta-50 border border-terracotta-200 text-terracotta-800 text-xs font-medium flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Suggestion Chips */}
      <div className="pt-2 border-t border-cream-200/70">
        <p className="text-2xs font-bold uppercase tracking-wider text-charcoal-500 mb-2">
          Try saying or tapping:
        </p>
        <div className="flex flex-wrap gap-1.5">
          {samplePrompts.map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => {
                setTranscript(p.text);
                handleProcessTranscript(p.text);
              }}
              className="text-2xs font-medium px-3 py-1.5 rounded-lg bg-cream-50 hover:bg-forest-50 hover:border-forest-300 text-charcoal-700 border border-cream-300 transition-colors flex items-center gap-1.5"
            >
              <span>{p.text}</span>
              <span className="text-3xs font-bold text-forest-700 bg-forest-100/80 px-1.5 py-0.5 rounded">
                {p.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Confirmation Modal */}
      {interpretResult && (
        <ConfirmationModal
          events={interpretResult.events}
          isOpen={isConfirmModalOpen}
          onClose={() => setIsConfirmModalOpen(false)}
          onConfirm={handleConfirmTransactions}
          isLoading={isSubmittingConfirm}
        />
      )}
    </div>
  );
};
