import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import {
  ArrowLeft,
  Phone,
  MapPin,
  FileText,
  PlusCircle,
  Receipt,
  MessageSquare,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  X,
  Check,
  Share2
} from 'lucide-react';
import confetti from 'canvas-confetti';

export const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t, language } = useLanguage();
  const queryClient = useQueryClient();

  const [isAddTxModalOpen, setIsAddTxModalOpen] = useState(false);
  const [txType, setTxType] = useState<'CREDIT' | 'PAYMENT'>('CREDIT');
  const [txAmount, setTxAmount] = useState('');
  const [txDesc, setTxDesc] = useState('');
  const [txDate, setTxDate] = useState(new Date().toISOString().split('T')[0]);

  // Fetch Customer Details and Full Ledger
  const { data: ledger, isLoading } = useQuery({
    queryKey: ['customer-ledger', id],
    queryFn: () => api.getCustomerLedger(id!),
    enabled: !!id,
  });

  const { data: customer } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => api.getCustomer(id!),
    enabled: !!id,
  });

  // Create Transaction Mutation
  const txMutation = useMutation({
    mutationFn: (data: any) => api.createTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-ledger', id] });
      queryClient.invalidateQueries({ queryKey: ['customer', id] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      setIsAddTxModalOpen(false);
      setTxAmount('');
      setTxDesc('');

      confetti({ particleCount: 50, spread: 50, origin: { y: 0.7 } });
    }
  });

  const handleCreateTx = (e: React.FormEvent) => {
    e.preventDefault();
    if (!txAmount || Number(txAmount) <= 0) return;
    txMutation.mutate({
      customer_id: id!,
      type: txType,
      amount: Number(txAmount),
      transaction_date: txDate,
      description: txDesc || (txType === 'CREDIT' ? 'Goods given on credit' : 'Cash/UPI payment'),
      input_method: 'MANUAL'
    });
  };

  const handleShareWhatsAppReminder = () => {
    if (!customer) return;
    const bal = Number(ledger?.outstanding_balance || 0);
    const msg = language === 'kn'
      ? `ನಮಸ್ಕಾರ ${customer.name}, ನಿಮ್ಮ ಅಂಗಡಿ ಖಾತೆಯಲ್ಲಿ ₹${bal} ಬಾಕಿ ಉಳಿದಿದೆ. ದಯವಿಟ್ಟು ಪಾವತಿಸಿ. ಧನ್ಯವಾದಗಳು!`
      : language === 'hi'
      ? `नमस्ते ${customer.name}, आपकी दुकान के खाते में ₹${bal} का बकाया बाकी है। कृपया जल्द भुगतान करें। धन्यवाद!`
      : `Hello ${customer.name}, this is a gentle reminder that ₹${bal} is pending in your account at our shop. Thank you!`;

    const phone = customer.mobile ? customer.mobile.replace(/\D/g, '') : '';
    const url = `https://wa.me/${phone ? '91' + phone : ''}?text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
  };

  if (isLoading) {
    return <div className="p-8 text-center text-xs text-charcoal-500">Loading ledger...</div>;
  }

  const balance = Number(ledger?.outstanding_balance || 0);
  const totalCredit = Number(ledger?.total_credit || 0);
  const totalPayment = Number(ledger?.total_payment || 0);

  return (
    <div className="space-y-6 animate-in fade-in max-w-4xl mx-auto">
      {/* Back button & Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/customers')}
          className="p-2 rounded-xl bg-white border border-cream-200 text-charcoal-700 hover:bg-cream-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-black text-forest-900 leading-tight">
            {ledger?.customer_name || 'Customer Khata'}
          </h1>
          <p className="text-xs text-charcoal-500">Individual Customer Ledger & Dues</p>
        </div>
      </div>

      {/* Customer Header Card */}
      <div className="bg-white rounded-3xl border border-cream-200 p-5 sm:p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-14 h-14 rounded-2xl bg-forest-800 text-white flex items-center justify-center text-2xl font-black shrink-0 shadow-md">
              {ledger?.customer_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-charcoal-900">{ledger?.customer_name}</h2>
              <div className="flex flex-wrap items-center gap-3 text-xs text-charcoal-600 mt-1">
                {customer?.mobile && (
                  <span className="flex items-center gap-1 font-medium">
                    <Phone className="w-3.5 h-3.5 text-forest-700" />
                    {customer.mobile}
                  </span>
                )}
                {customer?.address && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-charcoal-400" />
                    {customer.address}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Outstanding Balance Badge */}
          <div className="sm:text-right bg-cream-50 sm:bg-transparent p-3 sm:p-0 rounded-2xl border sm:border-0 border-cream-200">
            <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500 block">
              Net Outstanding Balance
            </span>
            <p
              className={`text-2xl sm:text-3xl font-black ${
                balance > 0 ? 'text-forest-900' : balance < 0 ? 'text-amberGold-600' : 'text-charcoal-600'
              }`}
            >
              ₹{Math.abs(balance).toLocaleString('en-IN')}
            </p>
            <span className="text-3xs font-semibold text-charcoal-500">
              {balance > 0 ? 'Customer owes shop' : balance < 0 ? 'Advance credit balance' : 'Zero balance settled'}
            </span>
          </div>
        </div>

        {/* Credit vs Payments KPI Bar */}
        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-cream-200">
          <div className="p-3 rounded-2xl bg-forest-50/70 border border-forest-100">
            <span className="text-2xs font-bold uppercase tracking-wide text-forest-800 flex items-center gap-1">
              <ArrowUpRight className="w-3.5 h-3.5" /> Total Credit Given
            </span>
            <p className="text-lg font-black text-forest-900 mt-0.5">
              ₹{totalCredit.toLocaleString('en-IN')}
            </p>
          </div>

          <div className="p-3 rounded-2xl bg-amber-50/70 border border-amber-100">
            <span className="text-2xs font-bold uppercase tracking-wide text-amberGold-600 flex items-center gap-1">
              <ArrowDownLeft className="w-3.5 h-3.5" /> Total Payments Received
            </span>
            <p className="text-lg font-black text-amberGold-600 mt-0.5">
              ₹{totalPayment.toLocaleString('en-IN')}
            </p>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="flex flex-wrap gap-2.5 pt-1">
          <button
            onClick={() => { setTxType('CREDIT'); setIsAddTxModalOpen(true); }}
            className="flex-1 py-2.5 px-4 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-xs flex items-center justify-center gap-2 transition-transform active:scale-95"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Give Credit (+)</span>
          </button>

          <button
            onClick={() => { setTxType('PAYMENT'); setIsAddTxModalOpen(true); }}
            className="flex-1 py-2.5 px-4 bg-amberGold-600 hover:bg-amberGold-500 text-white text-xs font-bold rounded-xl shadow-xs flex items-center justify-center gap-2 transition-transform active:scale-95"
          >
            <Receipt className="w-4 h-4" />
            <span>Record Payment (-)</span>
          </button>

          {balance > 0 && (
            <button
              onClick={handleShareWhatsAppReminder}
              className="py-2.5 px-4 bg-white border border-forest-300 text-forest-800 text-xs font-bold rounded-xl shadow-2xs hover:bg-forest-50 flex items-center justify-center gap-2 transition-colors"
            >
              <Share2 className="w-4 h-4 text-forest-700" />
              <span>Send WhatsApp Reminder</span>
            </button>
          )}
        </div>
      </div>

      {/* Transaction Statement Table */}
      <div className="bg-white rounded-2xl border border-cream-200 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-cream-200">
          <h3 className="text-sm sm:text-base font-bold text-forest-900">
            Ledger Transaction Statement
          </h3>
          <p className="text-xs text-charcoal-500">Every confirmed credit and payment entry</p>
        </div>

        {ledger?.transactions && ledger.transactions.length > 0 ? (
          <div className="divide-y divide-cream-200/80">
            {ledger.transactions.map((t) => {
              const isCredit = t.type === 'CREDIT';
              return (
                <div key={t.id} className="p-4 flex items-center justify-between hover:bg-cream-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                        isCredit ? 'bg-forest-100 text-forest-800' : 'bg-amber-100 text-amberGold-600'
                      }`}
                    >
                      {isCredit ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownLeft className="w-4 h-4" />}
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm font-bold text-charcoal-900">
                        {t.description || (isCredit ? 'Credit given' : 'Payment received')}
                      </p>
                      <p className="text-2xs text-charcoal-500 flex items-center gap-1.5">
                        <Calendar className="w-3 h-3 text-charcoal-400" />
                        <span>{t.transaction_date}</span>
                        <span>•</span>
                        <span className="capitalize">{t.input_method.toLowerCase()}</span>
                        {t.status === 'REVERSED' && (
                          <span className="text-terracotta-500 font-bold">(Reversed)</span>
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <p
                      className={`text-sm sm:text-base font-extrabold ${
                        isCredit ? 'text-forest-800' : 'text-amberGold-600'
                      }`}
                    >
                      {isCredit ? '+' : '-'} ₹{Number(t.amount).toLocaleString('en-IN')}
                    </p>
                    <span className="text-3xs text-charcoal-500 font-medium">
                      {isCredit ? 'Credit' : 'Payment'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-charcoal-500">
            No transactions found for this customer yet.
          </div>
        )}
      </div>

      {/* Add Transaction Modal */}
      {isAddTxModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-xs animate-in fade-in">
          <form
            onSubmit={handleCreateTx}
            className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-cream-200 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-cream-200 pb-3">
              <h3 className="text-base font-bold text-forest-900">
                {txType === 'CREDIT' ? 'Record Credit Given' : 'Record Payment Received'}
              </h3>
              <button
                type="button"
                onClick={() => setIsAddTxModalOpen(false)}
                className="p-1 rounded-lg text-charcoal-500 hover:bg-cream-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Amount (₹) *
              </label>
              <input
                type="number"
                step="0.01"
                required
                autoFocus
                value={txAmount}
                onChange={(e) => setTxAmount(e.target.value)}
                placeholder="e.g. 500"
                className="w-full text-base font-bold px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Date
              </label>
              <input
                type="date"
                required
                value={txDate}
                onChange={(e) => setTxDate(e.target.value)}
                className="w-full text-xs font-semibold px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Description / Items
              </label>
              <input
                type="text"
                value={txDesc}
                onChange={(e) => setTxDesc(e.target.value)}
                placeholder="e.g. 5kg Rice, Oil, Spices"
                className="w-full text-xs font-medium px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-cream-200">
              <button
                type="button"
                onClick={() => setIsAddTxModalOpen(false)}
                className="px-4 py-2 text-xs font-bold text-charcoal-600 hover:bg-cream-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={txMutation.isPending}
                className="px-5 py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-1.5"
              >
                {txMutation.isPending ? (
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Check className="w-4 h-4" />
                )}
                <span>Record in Ledger</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
