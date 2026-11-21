import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { VoiceCenterpiece } from '../components/VoiceCenterpiece';
import { useNavigate } from 'react-router-dom';
import {
  Wallet,
  ArrowUpRight,
  ArrowDownLeft,
  Users,
  PlusCircle,
  Receipt,
  UserPlus,
  BookOpen,
  Calendar,
  Sparkles,
  ChevronRight,
  ShieldCheck,
  Mic,
  Camera,
  Edit3
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Dynamic Date Formatting
  const todayDateFormatted = new Intl.DateTimeFormat('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date());

  // Real-time Dashboard Summary from DB
  const { data: summary, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.getDashboardSummary(),
  });

  // Real-time Recent Transactions from DB
  const { data: recentTransactions, refetch: refetchTransactions } = useQuery({
    queryKey: ['recent-transactions'],
    queryFn: () => api.getTransactions({ limit: 6, sort: 'newest' }),
  });

  const handleRefresh = () => {
    refetchSummary();
    refetchTransactions();
    queryClient.invalidateQueries({ queryKey: ['customers'] });
  };

  const totalCustomersDisplay =
    summary?.total_customers ??
    (summary as any)?.total_customers_count ??
    0;

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in">
      {/* Top Greeting Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-cream-200/80 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight flex items-center gap-2">
            <span>{t.namaste}, {user?.name || 'Shopkeeper'}!</span>
          </h1>
          <p className="text-xs sm:text-sm text-charcoal-700 font-semibold mt-0.5">
            {t.subGreeting}
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold text-forest-900 bg-white px-3.5 py-1.5 rounded-xl border-2 border-cream-300 shadow-2xs self-start sm:self-auto">
          <Calendar className="w-4 h-4 text-forest-700" />
          <span>{todayDateFormatted}</span>
        </div>
      </div>

      {/* Trust & Encryption Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3.5 rounded-2xl bg-forest-900/5 border-2 border-forest-900/10 text-forest-950 gap-2">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-5 h-5 text-forest-800 shrink-0" />
          <span className="text-xs font-black">
            🛡️ SQLCipher Encrypted • 100% Private On-Device Ledger
          </span>
        </div>
        <span className="text-2xs font-bold text-forest-800">
          Your kirana ledger is encrypted with hardware keys and belongs entirely to you.
        </span>
      </div>

      {/* 4 Summary Cards (Directly from Live Database) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Card 1: Total Outstanding */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border-2 border-cream-300 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-700 mb-2">
            <span className="text-2xs sm:text-xs font-black uppercase tracking-wider">
              {t.totalOutstanding}
            </span>
            <div className="w-8 h-8 rounded-xl bg-forest-100 flex items-center justify-center text-forest-800">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-forest-900">
            ₹{summary?.total_outstanding?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-charcoal-600 font-bold">Net unpaid credit</span>
        </div>

        {/* Card 2: Today's Credit */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border-2 border-cream-300 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-700 mb-2">
            <span className="text-2xs sm:text-xs font-black uppercase tracking-wider">
              {t.todayCredit}
            </span>
            <div className="w-8 h-8 rounded-xl bg-forest-100 flex items-center justify-center text-forest-800">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-forest-900">
            ₹{summary?.today_credit?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-forest-700 font-bold">Goods given on udhaar</span>
        </div>

        {/* Card 3: Today's Collections */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border-2 border-cream-300 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-700 mb-2">
            <span className="text-2xs sm:text-xs font-black uppercase tracking-wider">
              {t.todayCollections}
            </span>
            <div className="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center text-amberGold-700">
              <ArrowDownLeft className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-amberGold-700">
            ₹{summary?.today_payment?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-amberGold-700 font-bold">Cash/UPI payments</span>
        </div>

        {/* Card 4: Total Customers */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border-2 border-cream-300 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-700 mb-2">
            <span className="text-2xs sm:text-xs font-black uppercase tracking-wider">
              {t.totalCustomers}
            </span>
            <div className="w-8 h-8 rounded-xl bg-cream-200 flex items-center justify-center text-charcoal-800">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-charcoal-900">
            {totalCustomersDisplay}
          </p>
          <span className="text-3xs text-charcoal-600 font-bold">
            {summary?.total_customers_with_balance ?? 0} with active dues
          </span>
        </div>
      </div>

      {/* Voice Assistant Centerpiece */}
      <VoiceCenterpiece onTransactionSuccess={handleRefresh} />

      {/* Quick Actions (All Functional) */}
      <div className="space-y-3">
        <h2 className="text-xs font-black uppercase tracking-wider text-charcoal-800">
          Quick Ledger Actions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <button
            onClick={() => navigate('/customers')}
            className="p-3.5 rounded-2xl bg-white hover:bg-forest-50 border-2 border-cream-300 hover:border-forest-700 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-forest-100 text-forest-800 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <PlusCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-forest-900 leading-tight">{t.addCredit}</p>
              <p className="text-3xs text-charcoal-600 font-bold">Record udhaar</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/customers')}
            className="p-3.5 rounded-2xl bg-white hover:bg-amber-50 border-2 border-cream-300 hover:border-amberGold-600 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amberGold-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Receipt className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-charcoal-900 leading-tight">{t.recordPayment}</p>
              <p className="text-3xs text-charcoal-600 font-bold">Record jama</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/customers?new=true')}
            className="p-3.5 rounded-2xl bg-white hover:bg-cream-50 border-2 border-cream-300 hover:border-charcoal-400 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-cream-200 text-charcoal-800 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-charcoal-900 leading-tight">{t.addCustomer}</p>
              <p className="text-3xs text-charcoal-600 font-bold">New customer</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/transactions')}
            className="p-3.5 rounded-2xl bg-white hover:bg-cream-50 border-2 border-cream-300 hover:border-charcoal-400 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-charcoal-900 leading-tight">{t.viewLedger}</p>
              <p className="text-3xs text-charcoal-600 font-bold">All transactions</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-white rounded-2xl border-2 border-cream-300 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-cream-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm sm:text-base font-black text-forest-900">
              {t.recentTransactions}
            </h2>
            <p className="text-xs text-charcoal-600 font-semibold">Live feed from database</p>
          </div>
          <button
            onClick={() => navigate('/transactions')}
            className="text-xs font-black text-forest-800 hover:text-forest-950 flex items-center gap-1"
          >
            <span>View All</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {recentTransactions && recentTransactions.length > 0 ? (
          <div className="divide-y divide-cream-200/80">
            {recentTransactions.map((tx) => {
              const isCredit = tx.type === 'CREDIT';
              const isVoice = tx.input_method === 'VOICE';
              const isReceipt = tx.input_method === 'SCAN_BILL' || (tx.description && tx.description.toLowerCase().includes('bill'));

              return (
                <div
                  key={tx.id}
                  className="p-3.5 sm:p-4 flex items-center justify-between hover:bg-cream-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                        isCredit
                          ? 'bg-forest-100 text-forest-800'
                          : 'bg-amber-100 text-amberGold-700'
                      }`}
                    >
                      {isCredit ? (
                        <ArrowUpRight className="w-5 h-5" />
                      ) : (
                        <ArrowDownLeft className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm font-black text-charcoal-900">
                        {tx.customer_name || 'Customer'}
                      </p>
                      <div className="text-2xs text-charcoal-600 font-semibold flex items-center gap-1.5 mt-0.5">
                        <span>{tx.transaction_date}</span>
                        <span>•</span>
                        {/* Source Badge */}
                        <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-cream-100 text-charcoal-800 font-bold border border-cream-300">
                          {isReceipt ? (
                            <>
                              <Camera className="w-3 h-3 text-forest-700" />
                              <span>Bill Scan</span>
                            </>
                          ) : isVoice ? (
                            <>
                              <Mic className="w-3 h-3 text-amberGold-600" />
                              <span>Voice</span>
                            </>
                          ) : (
                            <>
                              <Edit3 className="w-3 h-3 text-charcoal-600" />
                              <span>Manual</span>
                            </>
                          )}
                        </span>
                        {tx.status === 'REVERSED' && (
                          <span className="text-terracotta-600 font-extrabold">(Reversed)</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <p
                      className={`text-sm sm:text-base font-black ${
                        isCredit ? 'text-forest-900' : 'text-amberGold-700'
                      }`}
                    >
                      {isCredit ? '+' : '-'} ₹{Number(tx.amount).toLocaleString('en-IN')}
                    </p>
                    <span
                      className={`text-3xs font-extrabold px-1.5 py-0.5 rounded ${
                        isCredit
                          ? 'bg-forest-100 text-forest-900 border border-forest-200'
                          : 'bg-amber-100 text-amberGold-800 border border-amber-200'
                      }`}
                    >
                      {isCredit ? 'Credit (Udhaar)' : 'Payment (Jama)'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-charcoal-600 font-bold">
            {t.noTransactions}
          </div>
        )}
      </div>
    </div>
  );
};
