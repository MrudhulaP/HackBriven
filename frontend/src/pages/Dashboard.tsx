import React, { useState } from 'react';
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
  ChevronRight
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

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in">
      {/* Top Greeting Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-cream-200/80 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight flex items-center gap-2">
            <span>{t.namaste}, {user?.name || 'Shopkeeper'}!</span>
          </h1>
          <p className="text-xs sm:text-sm text-charcoal-600 mt-0.5">
            {t.subGreeting}
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-forest-800 bg-white px-3 py-1.5 rounded-xl border border-cream-200 shadow-2xs self-start sm:self-auto">
          <Calendar className="w-3.5 h-3.5 text-forest-600" />
          <span>{todayDateFormatted}</span>
        </div>
      </div>

      {/* 4 Summary Cards (Directly from Database) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Card 1: Total Outstanding */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-500 mb-2">
            <span className="text-2xs sm:text-xs font-bold uppercase tracking-wider">
              {t.totalOutstanding}
            </span>
            <div className="w-7 h-7 rounded-lg bg-forest-50 flex items-center justify-center text-forest-700">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-forest-900">
            ₹{summary?.total_outstanding?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-charcoal-500 font-medium">Net unpaid credit</span>
        </div>

        {/* Card 2: Today's Credit */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-500 mb-2">
            <span className="text-2xs sm:text-xs font-bold uppercase tracking-wider">
              {t.todayCredit}
            </span>
            <div className="w-7 h-7 rounded-lg bg-forest-50 flex items-center justify-center text-forest-700">
              <ArrowUpRight className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-forest-800">
            ₹{summary?.today_credit?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-forest-600 font-medium">Goods given on udhaar</span>
        </div>

        {/* Card 3: Today's Collections */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-500 mb-2">
            <span className="text-2xs sm:text-xs font-bold uppercase tracking-wider">
              {t.todayCollections}
            </span>
            <div className="w-7 h-7 rounded-lg bg-amber-50 flex items-center justify-center text-amberGold-600">
              <ArrowDownLeft className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-amberGold-600">
            ₹{summary?.today_payment?.toLocaleString('en-IN') ?? '0'}
          </p>
          <span className="text-3xs text-amberGold-600 font-medium">Cash/UPI payments</span>
        </div>

        {/* Card 4: Total Customers */}
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-cream-200 shadow-xs relative overflow-hidden">
          <div className="flex items-center justify-between text-charcoal-500 mb-2">
            <span className="text-2xs sm:text-xs font-bold uppercase tracking-wider">
              {t.totalCustomers}
            </span>
            <div className="w-7 h-7 rounded-lg bg-cream-100 flex items-center justify-center text-charcoal-700">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <p className="text-xl sm:text-2xl font-black text-charcoal-900">
            {summary?.total_customers ?? 0}
          </p>
          <span className="text-3xs text-charcoal-500 font-medium">Registered khatas</span>
        </div>
      </div>

      {/* Voice Assistant Centerpiece */}
      <VoiceCenterpiece onTransactionSuccess={handleRefresh} />

      {/* Quick Actions (All Functional) */}
      <div className="space-y-3">
        <h2 className="text-xs font-extrabold uppercase tracking-wider text-charcoal-600">
          Quick Ledger Actions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <button
            onClick={() => navigate('/customers')}
            className="p-3.5 rounded-2xl bg-white hover:bg-forest-50 border border-cream-200 hover:border-forest-200 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-forest-100 text-forest-800 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <PlusCircle className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-forest-900 leading-tight">{t.addCredit}</p>
              <p className="text-3xs text-charcoal-500">Record udhaar</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/customers')}
            className="p-3.5 rounded-2xl bg-white hover:bg-amber-50 border border-cream-200 hover:border-amber-200 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-amber-100 text-amberGold-600 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Receipt className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-charcoal-900 leading-tight">{t.recordPayment}</p>
              <p className="text-3xs text-charcoal-500">Record jama</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/customers?new=true')}
            className="p-3.5 rounded-2xl bg-white hover:bg-cream-50 border border-cream-200 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-cream-200 text-charcoal-800 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-charcoal-900 leading-tight">{t.addCustomer}</p>
              <p className="text-3xs text-charcoal-500">New customer</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/transactions')}
            className="p-3.5 rounded-2xl bg-white hover:bg-cream-50 border border-cream-200 text-left transition-all shadow-2xs flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-charcoal-900 leading-tight">{t.viewLedger}</p>
              <p className="text-3xs text-charcoal-500">All transactions</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="bg-white rounded-2xl border border-cream-200 shadow-xs overflow-hidden">
        <div className="p-4 sm:p-5 border-b border-cream-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm sm:text-base font-bold text-forest-900">
              {t.recentTransactions}
            </h2>
            <p className="text-xs text-charcoal-500">Live feed from database</p>
          </div>
          <button
            onClick={() => navigate('/transactions')}
            className="text-xs font-bold text-forest-700 hover:text-forest-900 flex items-center gap-1"
          >
            <span>View All</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {recentTransactions && recentTransactions.length > 0 ? (
          <div className="divide-y divide-cream-200/80">
            {recentTransactions.map((tx) => {
              const isCredit = tx.type === 'CREDIT';
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
                          : 'bg-amber-100 text-amberGold-600'
                      }`}
                    >
                      {isCredit ? (
                        <ArrowUpRight className="w-5 h-5" />
                      ) : (
                        <ArrowDownLeft className="w-5 h-5" />
                      )}
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm font-bold text-charcoal-900">
                        {tx.customer_name || 'Customer'}
                      </p>
                      <p className="text-2xs text-charcoal-500 flex items-center gap-1.5">
                        <span>{tx.transaction_date}</span>
                        <span>•</span>
                        <span className="capitalize">{tx.input_method.toLowerCase()}</span>
                        {tx.status === 'REVERSED' && (
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
                      {isCredit ? '+' : '-'} ₹{Number(tx.amount).toLocaleString('en-IN')}
                    </p>
                    <span
                      className={`text-3xs font-bold px-1.5 py-0.5 rounded ${
                        isCredit
                          ? 'bg-forest-50 text-forest-700'
                          : 'bg-amber-50 text-amberGold-600'
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
          <div className="p-8 text-center text-xs text-charcoal-500">
            {t.noTransactions}
          </div>
        )}
      </div>
    </div>
  );
};
