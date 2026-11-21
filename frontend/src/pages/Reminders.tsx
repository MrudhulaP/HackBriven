import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { Customer, Language } from '../types';
import {
  BellRing,
  Share2,
  Copy,
  Check,
  MessageSquare,
  Users,
  Sparkles,
  Phone,
  Globe
} from 'lucide-react';

export const Reminders: React.FC = () => {
  const { t, language } = useLanguage();
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('');
  const [reminderLang, setReminderLang] = useState<Language>(language);
  const [copied, setCopied] = useState<boolean>(false);
  const [customMessage, setCustomMessage] = useState<string>('');

  // Fetch customers with pending balances
  const { data: customers = [], isLoading } = useQuery({
    queryKey: ['customers-with-balance'],
    queryFn: () => api.getCustomers(undefined, true),
  });

  const selectedCustomer = customers.find(c => c.id === selectedCustomerId);

  // Generate polite multilingual reminder message
  React.useEffect(() => {
    if (selectedCustomer) {
      const bal = Number(selectedCustomer.outstanding_balance || 0);
      const name = selectedCustomer.name;
      let msg = '';

      switch (reminderLang) {
        case 'kn':
          msg = `ನಮಸ್ಕಾರ ${name}, ನಿಮ್ಮ ಅಂಗಡಿ ಖಾತೆಯಲ್ಲಿ ₹${bal} ಬಾಕಿ ಉಳಿದಿದೆ. ದಯವಿಟ್ಟು ಪಾವತಿಸಿ. ಧನ್ಯವಾದಗಳು!`;
          break;
        case 'hi':
          msg = `नमस्ते ${name}, आपकी दुकान के खाते में ₹${bal} का बकाया बाकी है। कृपया जल्द भुगतान करें। धन्यवाद!`;
          break;
        case 'te':
          msg = `నమస్కారం ${name} గారు, మా దుకాణం ఖాతాలో మీ బాకీ ₹${bal} ఉంది. దయచేసి వీలైనంత త్వరగా చెల్లించండి. ధన్యవాదాలు!`;
          break;
        case 'ta':
          msg = `வணக்கம் ${name}, எங்கள் கடை கணக்கில் உங்கள் பாக்கித் தொகை ₹${bal} உள்ளது. தயவுசெய்து விரைவில் செலுத்தவும். நன்றி!`;
          break;
        default:
          msg = `Namaste ${name}, this is a gentle reminder that an outstanding balance of ₹${bal} is pending in your account. Thank you!`;
          break;
      }

      setCustomMessage(msg);
    } else {
      setCustomMessage('');
    }
  }, [selectedCustomerId, reminderLang, selectedCustomer]);

  const handleCopy = () => {
    if (!customMessage) return;
    navigator.clipboard.writeText(customMessage);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleWhatsAppShare = () => {
    if (!selectedCustomer || !customMessage) return;
    const phone = selectedCustomer.mobile ? selectedCustomer.mobile.replace(/\D/g, '') : '';
    const url = `https://wa.me/${phone ? '91' + phone : ''}?text=${encodeURIComponent(customMessage)}`;
    window.open(url, '_blank');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          {t.reminders}
        </h1>
        <p className="text-xs sm:text-sm text-charcoal-700 font-semibold">
          Generate polite, culturally appropriate payment reminders in your customer's preferred language.
        </p>
      </div>

      <div className="bg-white rounded-3xl border-2 border-cream-300 p-6 shadow-xs space-y-5">
        {/* Customer Select */}
        <div>
          <label className="text-xs font-black text-charcoal-800 block mb-1.5">
            Select Customer with Pending Dues
          </label>
          <select
            value={selectedCustomerId}
            onChange={(e) => setSelectedCustomerId(e.target.value)}
            className="w-full text-xs font-bold px-3.5 py-2.5 bg-cream-50 border-2 border-cream-300 rounded-xl text-charcoal-900 focus:ring-2 focus:ring-forest-600 outline-none cursor-pointer"
          >
            <option value="">-- Choose a customer ({customers.length} with dues) --</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} — Due: ₹{Number(c.outstanding_balance).toLocaleString('en-IN')} {c.mobile ? `(${c.mobile})` : ''}
              </option>
            ))}
          </select>
        </div>

        {selectedCustomer && (
          <div className="space-y-4 pt-2 border-t border-cream-200 animate-in fade-in">
            {/* Customer Summary Chip */}
            <div className="p-3.5 rounded-xl bg-forest-50 border-2 border-forest-200 flex items-center justify-between">
              <div>
                <p className="text-xs font-black text-forest-900">{selectedCustomer.name}</p>
                <p className="text-2xs text-charcoal-700 font-bold">
                  {selectedCustomer.mobile || 'No mobile saved'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm sm:text-base font-black text-forest-900">
                  ₹{Number(selectedCustomer.outstanding_balance).toLocaleString('en-IN')}
                </p>
                <span className="text-3xs text-forest-800 font-extrabold uppercase">Pending Due</span>
              </div>
            </div>

            {/* Reminder Language Selector */}
            <div>
              <label className="text-2xs font-black text-charcoal-800 uppercase tracking-wider block mb-1.5 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 text-forest-700" />
                <span>Customer's Preferred Language</span>
              </label>
              <div className="grid grid-cols-5 gap-2">
                {[
                  { code: 'hi', label: 'हिंदी' },
                  { code: 'kn', label: 'ಕನ್ನಡ' },
                  { code: 'te', label: 'తెలుగు' },
                  { code: 'ta', label: 'தமிழ்' },
                  { code: 'en', label: 'English' },
                ].map((l) => (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => setReminderLang(l.code as Language)}
                    className={`py-1.5 px-2 rounded-xl text-xs font-black border transition-all ${
                      reminderLang === l.code
                        ? 'bg-forest-800 text-white border-forest-900 shadow-2xs'
                        : 'bg-white text-charcoal-800 border-cream-300 hover:bg-cream-100'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Editable Reminder Message */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-black text-charcoal-800">
                  Polite Payment Reminder Message
                </label>
                <span className="text-3xs text-charcoal-600 font-bold">Editable</span>
              </div>
              <textarea
                rows={4}
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                className="w-full text-xs font-bold p-3 border-2 border-charcoal-300 rounded-2xl bg-white text-charcoal-900 focus:ring-2 focus:ring-forest-600 outline-none leading-relaxed"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-2">
              <button
                type="button"
                onClick={handleCopy}
                className="flex-1 py-2.5 px-4 bg-white border-2 border-charcoal-300 hover:bg-cream-100 text-charcoal-900 text-xs font-black rounded-xl shadow-2xs flex items-center justify-center gap-2 transition-colors"
              >
                {copied ? <Check className="w-4 h-4 text-forest-700" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? 'Copied!' : 'Copy Message'}</span>
              </button>

              <button
                type="button"
                onClick={handleWhatsAppShare}
                className="flex-1 py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white text-xs font-black rounded-xl shadow-md flex items-center justify-center gap-2 transition-transform active:scale-95"
              >
                <Share2 className="w-4 h-4 text-forest-200" />
                <span>Share via WhatsApp</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
