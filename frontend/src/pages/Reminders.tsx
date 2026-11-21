import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { Customer } from '../types';
import {
  BellRing,
  Share2,
  Copy,
  Check,
  MessageSquare,
  Users,
  Sparkles,
  Phone
} from 'lucide-react';

export const Reminders: React.FC = () => {
  const { t, language } = useLanguage();
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);
  const [customMessage, setCustomMessage] = useState<string>('');

  // Fetch customers with pending balances
  const { data: customers = [], isLoading } = useQuery({
    queryKey: ['customers-with-balance'],
    queryFn: () => api.getCustomers(undefined, true),
  });

  const selectedCustomer = customers.find(c => c.id === selectedCustomerId);

  // Generate reminder message whenever customer or language changes
  React.useEffect(() => {
    if (selectedCustomer) {
      const bal = Number(selectedCustomer.outstanding_balance || 0);
      const name = selectedCustomer.name;
      let msg = '';
      if (language === 'kn') {
        msg = `ನಮಸ್ಕಾರ ${name}, ನಿಮ್ಮ ಅಂಗಡಿ ಖಾತೆಯಲ್ಲಿ ₹${bal} ಬಾಕಿ ಉಳಿದಿದೆ. ದಯವಿಟ್ಟು ಪಾವತಿಸಿ. ಧನ್ಯವಾದಗಳು!`;
      } else if (language === 'hi') {
        msg = `नमस्ते ${name}, आपकी दुकान के खाते में ₹${bal} का बकाया बाकी है। कृपया जल्द भुगतान करें। धन्यवाद!`;
      } else {
        msg = `Hello ${name}, this is a gentle reminder that ₹${bal} is pending in your account at our shop. Thank you!`;
      }
      setCustomMessage(msg);
    } else {
      setCustomMessage('');
    }
  }, [selectedCustomerId, language, selectedCustomer]);

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
        <p className="text-xs sm:text-sm text-charcoal-600">
          Generate polite, culturally appropriate payment reminders in your customer's preferred language.
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-cream-200 p-6 shadow-xs space-y-5">
        {/* Customer Select */}
        <div>
          <label className="text-xs font-bold text-charcoal-700 block mb-1.5">
            Select Customer with Pending Dues
          </label>
          <select
            value={selectedCustomerId}
            onChange={(e) => setSelectedCustomerId(e.target.value)}
            className="w-full text-xs font-bold px-3.5 py-2.5 bg-cream-50 border border-cream-300 rounded-xl text-charcoal-900 focus:ring-2 focus:ring-forest-600 outline-none cursor-pointer"
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
            <div className="p-3 rounded-xl bg-forest-50 border border-forest-100 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-forest-900">{selectedCustomer.name}</p>
                <p className="text-3xs text-charcoal-500">
                  {selectedCustomer.mobile || 'No mobile saved'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-black text-forest-900">
                  ₹{Number(selectedCustomer.outstanding_balance).toLocaleString('en-IN')}
                </p>
                <span className="text-3xs text-forest-700 font-semibold">Pending Due</span>
              </div>
            </div>

            {/* Editable Reminder Message */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-bold text-charcoal-700">
                  Polite Payment Reminder Message
                </label>
                <span className="text-3xs text-charcoal-500 font-medium">Editable</span>
              </div>
              <textarea
                rows={4}
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                className="w-full text-xs font-semibold p-3 border border-cream-300 rounded-2xl bg-cream-50 focus:bg-white focus:ring-2 focus:ring-forest-600 outline-none leading-relaxed"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-3 pt-2">
              <button
                type="button"
                onClick={handleCopy}
                className="flex-1 py-2.5 px-4 bg-white border border-cream-300 hover:bg-cream-100 text-charcoal-800 text-xs font-bold rounded-xl shadow-2xs flex items-center justify-center gap-2 transition-colors"
              >
                {copied ? <Check className="w-4 h-4 text-forest-600" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? 'Copied!' : 'Copy Message'}</span>
              </button>

              <button
                type="button"
                onClick={handleWhatsAppShare}
                className="flex-1 py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-md flex items-center justify-center gap-2 transition-transform active:scale-95"
              >
                <Share2 className="w-4 h-4 text-forest-300" />
                <span>Share via WhatsApp</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
