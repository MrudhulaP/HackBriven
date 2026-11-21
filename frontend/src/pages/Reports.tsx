import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import {
  BarChart3,
  Calendar,
  ArrowUpRight,
  ArrowDownLeft,
  Users,
  Coins,
  TrendingUp,
  PieChart
} from 'lucide-react';

export const Reports: React.FC = () => {
  const { t } = useLanguage();
  const [tab, setTab] = useState<'daily' | 'monthly'>('daily');

  const todayStr = new Date().toISOString().split('T')[0];
  const [selectedDate, setSelectedDate] = useState(todayStr);

  // Daily Report query
  const { data: dailyReport, isLoading: isDailyLoading } = useQuery({
    queryKey: ['daily-report', selectedDate],
    queryFn: () => api.getDailyReport(selectedDate),
  });

  // Monthly Report query
  const { data: monthlyReport, isLoading: isMonthlyLoading } = useQuery({
    queryKey: ['monthly-report'],
    queryFn: () => api.getMonthlyReport(),
  });

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in max-w-5xl mx-auto">
      {/* Header & Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            {t.reports} & Analytics
          </h1>
          <p className="text-xs sm:text-sm text-charcoal-600">
            Real-time financial analytics, daily revenue collections, and credit trends.
          </p>
        </div>

        <div className="flex items-center gap-1 p-1 bg-white border border-cream-200 rounded-xl shadow-2xs self-start sm:self-auto">
          <button
            onClick={() => setTab('daily')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-colors ${
              tab === 'daily'
                ? 'bg-forest-800 text-white'
                : 'text-charcoal-600 hover:text-charcoal-900'
            }`}
          >
            Daily Report
          </button>
          <button
            onClick={() => setTab('monthly')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-colors ${
              tab === 'monthly'
                ? 'bg-forest-800 text-white'
                : 'text-charcoal-600 hover:text-charcoal-900'
            }`}
          >
            Monthly Trends
          </button>
        </div>
      </div>

      {/* DAILY REPORT TAB */}
      {tab === 'daily' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Date Picker Bar */}
          <div className="bg-white p-4 rounded-2xl border border-cream-200 shadow-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-forest-700" />
              <span className="text-xs font-bold text-charcoal-900">Select Report Date:</span>
            </div>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="text-xs font-bold px-3 py-1.5 bg-cream-50 border border-cream-300 rounded-lg text-forest-900 cursor-pointer"
            />
          </div>

          {/* Daily KPI Metrics */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-forest-800 flex items-center gap-1 mb-1">
                <ArrowUpRight className="w-3.5 h-3.5" /> Credit Given Today
              </span>
              <p className="text-2xl font-black text-forest-900">
                ₹{Number(dailyReport?.total_credit || 0).toLocaleString('en-IN')}
              </p>
            </div>

            <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-amberGold-600 flex items-center gap-1 mb-1">
                <ArrowDownLeft className="w-3.5 h-3.5" /> Payments Collected
              </span>
              <p className="text-2xl font-black text-amberGold-600">
                ₹{Number(dailyReport?.total_payment || 0).toLocaleString('en-IN')}
              </p>
            </div>

            <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500 flex items-center gap-1 mb-1">
                <Coins className="w-3.5 h-3.5" /> Net Change
              </span>
              <p
                className={`text-2xl font-black ${
                  Number(dailyReport?.net_change || 0) > 0 ? 'text-forest-800' : 'text-charcoal-700'
                }`}
              >
                ₹{Number(dailyReport?.net_change || 0).toLocaleString('en-IN')}
              </p>
            </div>

            <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500 flex items-center gap-1 mb-1">
                <Users className="w-3.5 h-3.5" /> Customers Served
              </span>
              <p className="text-2xl font-black text-charcoal-900">
                {dailyReport?.customers_served ?? 0}
              </p>
            </div>
          </div>

          {/* Visual Ratio Bar */}
          <div className="bg-white p-6 rounded-2xl border border-cream-200 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-forest-900">
              Daily Credit vs Payment Ratio
            </h3>
            {(() => {
              const cred = Number(dailyReport?.total_credit || 0);
              const pay = Number(dailyReport?.total_payment || 0);
              const total = cred + pay;
              const credPct = total > 0 ? Math.round((cred / total) * 100) : 50;
              const payPct = total > 0 ? 100 - credPct : 50;

              return (
                <div className="space-y-2">
                  <div className="h-6 w-full bg-cream-200 rounded-full overflow-hidden flex shadow-inner">
                    <div
                      style={{ width: `${credPct}%` }}
                      className="bg-forest-700 h-full flex items-center justify-center text-3xs font-extrabold text-white transition-all"
                    >
                      {cred > 0 ? `${credPct}% Credit` : ''}
                    </div>
                    <div
                      style={{ width: `${payPct}%` }}
                      className="bg-amberGold-500 h-full flex items-center justify-center text-3xs font-extrabold text-white transition-all"
                    >
                      {pay > 0 ? `${payPct}% Cash/UPI` : ''}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-2xs text-charcoal-600 font-semibold px-1">
                    <span className="flex items-center gap-1.5 text-forest-800">
                      <span className="w-2.5 h-2.5 rounded-full bg-forest-700" />
                      Credit: ₹{cred.toLocaleString('en-IN')}
                    </span>
                    <span className="flex items-center gap-1.5 text-amberGold-600">
                      <span className="w-2.5 h-2.5 rounded-full bg-amberGold-500" />
                      Collections: ₹{pay.toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* MONTHLY REPORT TAB */}
      {tab === 'monthly' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Monthly KPI Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500">
                Monthly Credit Given
              </span>
              <p className="text-2xl font-black text-forest-900 mt-1">
                ₹{Number(monthlyReport?.total_credit || 0).toLocaleString('en-IN')}
              </p>
              <span className="text-3xs text-charcoal-400">Total in {monthlyReport?.month_name}</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500">
                Monthly Collections
              </span>
              <p className="text-2xl font-black text-amberGold-600 mt-1">
                ₹{Number(monthlyReport?.total_payment || 0).toLocaleString('en-IN')}
              </p>
              <span className="text-3xs text-charcoal-400">Cash & UPI collected</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-cream-200 shadow-xs">
              <span className="text-2xs font-bold uppercase tracking-wider text-charcoal-500">
                Total Shop Outstanding
              </span>
              <p className="text-2xl font-black text-forest-800 mt-1">
                ₹{Number(monthlyReport?.current_total_outstanding || 0).toLocaleString('en-IN')}
              </p>
              <span className="text-3xs text-forest-600 font-medium">Across all customers</span>
            </div>
          </div>

          {/* Top Debtors List (PART 15) */}
          <div className="bg-white rounded-2xl border border-cream-200 shadow-xs p-5 sm:p-6 space-y-4">
            <h3 className="text-sm font-bold text-forest-900 flex items-center gap-2">
              <Users className="w-4 h-4 text-forest-700" />
              <span>Top Customers by Outstanding Balance</span>
            </h3>

            {monthlyReport?.top_debtors && monthlyReport.top_debtors.length > 0 ? (
              <div className="space-y-3">
                {monthlyReport.top_debtors.map((deb, index) => (
                  <div
                    key={deb.customer_id}
                    className="p-3 rounded-xl bg-cream-50 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-full bg-forest-800 text-white text-xs font-bold flex items-center justify-center">
                        {index + 1}
                      </span>
                      <span className="text-xs font-bold text-charcoal-900">
                        {deb.customer_name}
                      </span>
                    </div>
                    <p className="text-sm font-black text-forest-900">
                      ₹{Number(deb.outstanding_balance).toLocaleString('en-IN')}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-charcoal-500">No pending customer balances.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
