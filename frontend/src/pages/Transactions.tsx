import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Transaction } from '../types';
import { useLanguage } from '../context/LanguageContext';
import {
  Search,
  Filter,
  ArrowUpRight,
  ArrowDownLeft,
  Calendar,
  RotateCcw,
  Edit2,
  X,
  Check,
  AlertTriangle,
  History
} from 'lucide-react';

export const Transactions: React.FC = () => {
  const { t } = useLanguage();
  const queryClient = useQueryClient();

  const [typeFilter, setTypeFilter] = useState<string>('');
  const [periodFilter, setPeriodFilter] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<string>('newest');

  // Correction / Reversal Modals
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [actionType, setActionType] = useState<'CORRECT' | 'REVERSE' | null>(null);
  const [newAmount, setNewAmount] = useState<string>('');
  const [reason, setReason] = useState<string>('');

  // Fetch Transactions from API
  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions', typeFilter, periodFilter, sortOrder],
    queryFn: () => api.getTransactions({
      type: typeFilter || undefined,
      period: periodFilter || undefined,
      sort: sortOrder,
      limit: 100
    }),
  });

  // Reversal Mutation
  const reverseMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.reverseTransaction(id, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['customer-ledger'] });
      closeActionModal();
    }
  });

  // Correction Mutation
  const correctMutation = useMutation({
    mutationFn: ({ id, amount, reason }: { id: string; amount: number; reason: string }) =>
      api.correctTransaction(id, { corrected_amount: amount, reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['customer-ledger'] });
      closeActionModal();
    }
  });

  const openActionModal = (tx: Transaction, type: 'CORRECT' | 'REVERSE') => {
    setSelectedTx(tx);
    setActionType(type);
    setNewAmount(String(tx.amount));
    setReason(type === 'CORRECT' ? 'Shopkeeper correction' : 'Undo transaction request');
  };

  const closeActionModal = () => {
    setSelectedTx(null);
    setActionType(null);
    setNewAmount('');
    setReason('');
  };

  const handleActionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTx) return;

    if (actionType === 'CORRECT') {
      correctMutation.mutate({
        id: selectedTx.id,
        amount: Number(newAmount),
        reason
      });
    } else if (actionType === 'REVERSE') {
      reverseMutation.mutate({
        id: selectedTx.id,
        reason
      });
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          {t.transactions}
        </h1>
        <p className="text-xs sm:text-sm text-charcoal-600">
          Complete audit trail of all credit and payment entries across your entire shop.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-cream-200 shadow-xs flex flex-wrap gap-2.5 items-center justify-between">
        <div className="flex flex-wrap items-center gap-2">
          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="text-xs font-bold px-3 py-2 bg-cream-50 border border-cream-200 rounded-xl text-charcoal-800 cursor-pointer"
          >
            <option value="">All Types (Credit & Payments)</option>
            <option value="CREDIT">Credits Only (Udhaar)</option>
            <option value="PAYMENT">Payments Only (Jama)</option>
          </select>

          {/* Period Filter */}
          <select
            value={periodFilter}
            onChange={(e) => setPeriodFilter(e.target.value)}
            className="text-xs font-bold px-3 py-2 bg-cream-50 border border-cream-200 rounded-xl text-charcoal-800 cursor-pointer"
          >
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
          </select>
        </div>

        {/* Sort Order */}
        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          className="text-xs font-bold px-3 py-2 bg-cream-50 border border-cream-200 rounded-xl text-charcoal-800 cursor-pointer"
        >
          <option value="newest">Sort: Newest First</option>
          <option value="oldest">Sort: Oldest First</option>
          <option value="amount_desc">Sort: Amount (High to Low)</option>
          <option value="amount_asc">Sort: Amount (Low to High)</option>
        </select>
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-2xl border border-cream-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-charcoal-500">Loading ledger records...</div>
        ) : transactions.length > 0 ? (
          <div className="divide-y divide-cream-200/80">
            {transactions.map((tx) => {
              const isCredit = tx.type === 'CREDIT';
              const isReversed = tx.status === 'REVERSED';

              return (
                <div
                  key={tx.id}
                  className={`p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-cream-50 transition-colors ${
                    isReversed ? 'opacity-60 bg-cream-50/40' : ''
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                        isCredit ? 'bg-forest-100 text-forest-800' : 'bg-amber-100 text-amberGold-600'
                      }`}
                    >
                      {isCredit ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownLeft className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-charcoal-900">
                          {tx.customer_name || 'Customer'}
                        </span>
                        {isReversed && (
                          <span className="text-3xs font-extrabold uppercase bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                            Reversed
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-charcoal-600 mt-0.5">
                        {tx.description || (isCredit ? 'Credit given' : 'Payment received')}
                      </p>
                      <p className="text-2xs text-charcoal-400 flex items-center gap-2 mt-1">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" /> {tx.transaction_date}
                        </span>
                        <span>•</span>
                        <span className="capitalize">{tx.input_method.toLowerCase()}</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-4 self-end sm:self-auto">
                    <div className="text-right">
                      <p
                        className={`text-base font-black ${
                          isCredit ? 'text-forest-800' : 'text-amberGold-600'
                        } ${isReversed ? 'line-through text-charcoal-400' : ''}`}
                      >
                        {isCredit ? '+' : '-'} ₹{Number(tx.amount).toLocaleString('en-IN')}
                      </p>
                      <span className="text-3xs font-medium text-charcoal-500">
                        {isCredit ? 'Credit (Udhaar)' : 'Payment (Jama)'}
                      </span>
                    </div>

                    {!isReversed && (
                      <div className="flex items-center gap-1 border-l border-cream-200 pl-3">
                        <button
                          onClick={() => openActionModal(tx, 'CORRECT')}
                          title="Correct amount with audit log"
                          className="p-1.5 rounded-lg text-charcoal-500 hover:bg-cream-100 hover:text-forest-800 transition-colors"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openActionModal(tx, 'REVERSE')}
                          title="Reverse transaction"
                          className="p-1.5 rounded-lg text-charcoal-500 hover:bg-cream-100 hover:text-terracotta-600 transition-colors"
                        >
                          <RotateCcw className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-12 text-center text-xs text-charcoal-500">
            No transactions match the selected filters.
          </div>
        )}
      </div>

      {/* Correction / Reversal Modal */}
      {selectedTx && actionType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-xs animate-in fade-in">
          <form
            onSubmit={handleActionSubmit}
            className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-cream-200 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-cream-200 pb-3">
              <h3 className="text-base font-bold text-forest-900">
                {actionType === 'CORRECT' ? 'Correct Transaction Amount' : 'Reverse Transaction'}
              </h3>
              <button
                type="button"
                onClick={closeActionModal}
                className="p-1 rounded-lg text-charcoal-500 hover:bg-cream-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-3 rounded-xl bg-cream-50 border border-cream-200 text-xs space-y-1">
              <p className="font-bold text-charcoal-900">Customer: {selectedTx.customer_name}</p>
              <p className="text-charcoal-600">Current Amount: ₹{selectedTx.amount}</p>
              <p className="text-charcoal-600">Type: {selectedTx.type}</p>
            </div>

            {actionType === 'CORRECT' && (
              <div>
                <label className="text-xs font-bold text-charcoal-700 block mb-1">
                  Corrected Amount (₹) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  autoFocus
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  className="w-full text-base font-bold px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
                />
              </div>
            )}

            {actionType === 'REVERSE' && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amberGold-600 shrink-0 mt-0.5" />
                <p>
                  Reversing will neutralize this ledger entry by creating a compensating audit record. Confirmed records are never permanently deleted.
                </p>
              </div>
            )}

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Audit Reason *
              </label>
              <input
                type="text"
                required
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g. Typo by shopkeeper / customer returned goods"
                className="w-full text-xs font-semibold px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-cream-200">
              <button
                type="button"
                onClick={closeActionModal}
                className="px-4 py-2 text-xs font-bold text-charcoal-600 hover:bg-cream-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={correctMutation.isPending || reverseMutation.isPending}
                className={`px-5 py-2.5 text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-1.5 ${
                  actionType === 'CORRECT' ? 'bg-forest-800 hover:bg-forest-900' : 'bg-terracotta-500 hover:bg-terracotta-600'
                }`}
              >
                <Check className="w-4 h-4" />
                <span>Confirm {actionType === 'CORRECT' ? 'Correction' : 'Reversal'}</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
