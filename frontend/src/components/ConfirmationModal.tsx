import React, { useState } from 'react';
import { ParsedEvent, VoiceConfirmItem } from '../types';
import { CheckCircle2, Edit3, X, Calendar, ArrowUpRight, ArrowDownLeft, AlertCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface ConfirmationModalProps {
  events: ParsedEvent[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (confirmedItems: VoiceConfirmItem[]) => Promise<void>;
  isLoading: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  events,
  isOpen,
  onClose,
  onConfirm,
  isLoading
}) => {
  const { t } = useLanguage();
  const [editableEvents, setEditableEvents] = useState<ParsedEvent[]>(events);
  const [activeEditingId, setActiveEditingId] = useState<string | null>(null);

  // Sync state if events change
  React.useEffect(() => {
    setEditableEvents(events);
  }, [events]);

  if (!isOpen) return null;

  const handleFieldChange = (eventId: string, field: keyof ParsedEvent, value: any) => {
    setEditableEvents(prev =>
      prev.map(ev => (ev.event_id === eventId ? { ...ev, [field]: value } : ev))
    );
  };

  const handleFinalConfirm = async () => {
    const items: VoiceConfirmItem[] = editableEvents.map(e => ({
      customer_id: e.customer_id || '',
      customer_name: e.customer_name || 'Unknown',
      type: (e.intent === 'ADD_CREDIT' ? 'CREDIT' : 'PAYMENT'),
      amount: Number(e.amount || 0),
      transaction_date: e.transaction_date,
      description: e.description || `${e.intent === 'ADD_CREDIT' ? 'Credit' : 'Payment'} recorded via voice`,
    }));
    await onConfirm(items);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-xs animate-in fade-in">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-cream-200 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cream-200 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-forest-100 flex items-center justify-center text-forest-800">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-forest-900 leading-tight">
                {t.confirmTransactions}
              </h3>
              <p className="text-xs text-charcoal-600">Review & confirm before writing to ledger</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-charcoal-500 hover:bg-cream-100 hover:text-charcoal-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List of Detected Events (Can be 2 events for "Ramesh ka 340 udhaar, kal 200 diya tha") */}
        <div className="space-y-3.5 max-h-[60vh] overflow-y-auto pr-1">
          {editableEvents.map((ev, index) => {
            const isCredit = ev.intent === 'ADD_CREDIT';
            const isEditing = activeEditingId === ev.event_id;

            return (
              <div
                key={ev.event_id}
                className={`p-4 rounded-xl border transition-all ${
                  isCredit ? 'bg-forest-50/50 border-forest-200' : 'bg-amber-50/50 border-amber-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-2xs font-extrabold uppercase tracking-wide flex items-center gap-1 ${
                        isCredit
                          ? 'bg-forest-800 text-white'
                          : 'bg-amberGold-600 text-white'
                      }`}
                    >
                      {isCredit ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownLeft className="w-3 h-3" />}
                      Event {index + 1}: {isCredit ? t.credit : t.payment}
                    </span>
                    <span className="text-xs text-charcoal-600 flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5" />
                      {ev.date_label} ({ev.transaction_date})
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => setActiveEditingId(isEditing ? null : ev.event_id)}
                    className="text-xs font-semibold text-forest-700 hover:text-forest-900 flex items-center gap-1"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    {isEditing ? 'Done' : 'Edit'}
                  </button>
                </div>

                {isEditing ? (
                  <div className="mt-3 space-y-2 pt-2 border-t border-cream-200/60">
                    <div>
                      <label className="text-2xs font-bold text-charcoal-700 block">Customer Name</label>
                      <input
                        type="text"
                        value={ev.customer_name || ''}
                        onChange={e => handleFieldChange(ev.event_id, 'customer_name', e.target.value)}
                        className="w-full text-xs font-semibold px-2 py-1.5 border border-cream-300 rounded-lg bg-white"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-2xs font-bold text-charcoal-700 block">Amount (₹)</label>
                        <input
                          type="number"
                          value={ev.amount || ''}
                          onChange={e => handleFieldChange(ev.event_id, 'amount', e.target.value)}
                          className="w-full text-xs font-semibold px-2 py-1.5 border border-cream-300 rounded-lg bg-white"
                        />
                      </div>
                      <div>
                        <label className="text-2xs font-bold text-charcoal-700 block">Type</label>
                        <select
                          value={ev.intent}
                          onChange={e => handleFieldChange(ev.event_id, 'intent', e.target.value)}
                          className="w-full text-xs font-semibold px-2 py-1.5 border border-cream-300 rounded-lg bg-white"
                        >
                          <option value="ADD_CREDIT">Credit (Udhaar)</option>
                          <option value="RECORD_PAYMENT">Payment (Jama)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="mt-2.5 flex items-baseline justify-between">
                    <div>
                      <p className="text-base font-bold text-charcoal-900">
                        {ev.customer_name || 'Customer'}
                      </p>
                      <p className="text-xs text-charcoal-600">
                        {isCredit ? 'Credit given' : 'Payment received'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p
                        className={`text-xl font-extrabold ${
                          isCredit ? 'text-forest-800' : 'text-amberGold-600'
                        }`}
                      >
                        {isCredit ? '+' : '-'} ₹{ev.amount}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-cream-200">
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-xs font-bold text-charcoal-600 hover:bg-cream-100 rounded-xl transition-colors"
          >
            {t.cancel}
          </button>
          <button
            type="button"
            onClick={handleFinalConfirm}
            disabled={isLoading}
            className="px-5 py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-md flex items-center gap-2 transition-all active:scale-95 disabled:opacity-50"
          >
            {isLoading ? (
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            <span>{t.confirm}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
