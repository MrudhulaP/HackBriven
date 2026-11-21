import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { Customer } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search,
  UserPlus,
  Phone,
  MapPin,
  FileText,
  ChevronRight,
  Filter,
  X,
  Check,
  AlertCircle
} from 'lucide-react';

export const Customers: React.FC = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  const [searchTerm, setSearchTerm] = useState('');
  const [hasBalanceOnly, setHasBalanceOnly] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(searchParams.get('new') === 'true');

  // Add form fields
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [address, setAddress] = useState('');
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState('');

  // Fetch customers with live balances
  const { data: customers = [], isLoading } = useQuery({
    queryKey: ['customers', searchTerm, hasBalanceOnly],
    queryFn: () => api.getCustomers(searchTerm, hasBalanceOnly),
  });

  // Create customer mutation
  const createMutation = useMutation({
    mutationFn: (newCust: { name: string; mobile?: string; address?: string; notes?: string }) =>
      api.createCustomer(newCust),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      setIsAddModalOpen(false);
      setName('');
      setMobile('');
      setAddress('');
      setNotes('');
      navigate(`/customers/${created.id}`);
    },
    onError: (err: any) => {
      setFormError(err.message || 'Failed to create customer');
    }
  });

  const handleCreateCustomer = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setFormError('Customer name is required');
      return;
    }
    setFormError('');
    createMutation.mutate({
      name: name.trim(),
      mobile: mobile.trim() || undefined,
      address: address.trim() || undefined,
      notes: notes.trim() || undefined
    });
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
            {t.customers}
          </h1>
          <p className="text-xs sm:text-sm text-charcoal-600">
            Manage your customer khata, view outstanding dues, and generate payment statements.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2.5 bg-forest-800 hover:bg-forest-900 text-white rounded-xl text-xs font-bold shadow-md flex items-center justify-center gap-2 transition-all active:scale-95 self-start sm:self-auto"
        >
          <UserPlus className="w-4 h-4" />
          <span>{t.addCustomer}</span>
        </button>
      </div>

      {/* Search and Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-charcoal-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t.searchCustomers}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-cream-200 rounded-xl text-xs font-medium focus:ring-2 focus:ring-forest-600 outline-none shadow-2xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal-400 hover:text-charcoal-700"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setHasBalanceOnly(!hasBalanceOnly)}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold border transition-colors flex items-center justify-center gap-2 ${
            hasBalanceOnly
              ? 'bg-forest-100 border-forest-300 text-forest-900'
              : 'bg-white border-cream-200 text-charcoal-700 hover:bg-cream-50'
          }`}
        >
          <Filter className="w-3.5 h-3.5" />
          <span>Pending Dues Only</span>
        </button>
      </div>

      {/* Customers List */}
      <div className="bg-white rounded-2xl border border-cream-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-charcoal-500 font-medium">
            Loading customers...
          </div>
        ) : customers.length > 0 ? (
          <div className="divide-y divide-cream-200/80">
            {customers.map((cust) => {
              const balance = Number(cust.outstanding_balance || 0);
              const isDebtor = balance > 0;
              const isAdvance = balance < 0;

              return (
                <div
                  key={cust.id}
                  onClick={() => navigate(`/customers/${cust.id}`)}
                  className="p-4 sm:p-5 flex items-center justify-between hover:bg-cream-50 transition-colors cursor-pointer group"
                >
                  <div className="flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-2xl bg-forest-100 text-forest-800 flex items-center justify-center text-base font-black shrink-0 shadow-2xs group-hover:scale-105 transition-transform">
                      {cust.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-sm sm:text-base font-bold text-charcoal-900 group-hover:text-forest-800 transition-colors">
                        {cust.name}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2 text-2xs text-charcoal-500 mt-0.5">
                        {cust.mobile && (
                          <span className="flex items-center gap-1">
                            <Phone className="w-3 h-3 text-charcoal-400" />
                            {cust.mobile}
                          </span>
                        )}
                        <span>•</span>
                        <span>{cust.transaction_count} transactions</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p
                        className={`text-base sm:text-lg font-black ${
                          isDebtor
                            ? 'text-forest-900'
                            : isAdvance
                            ? 'text-amberGold-600'
                            : 'text-charcoal-500'
                        }`}
                      >
                        {isAdvance ? 'Advance ' : ''}₹{Math.abs(balance).toLocaleString('en-IN')}
                      </p>
                      <span
                        className={`text-3xs font-bold px-2 py-0.5 rounded-full ${
                          isDebtor
                            ? 'bg-forest-100 text-forest-800'
                            : isAdvance
                            ? 'bg-amber-100 text-amberGold-600'
                            : 'bg-cream-200 text-charcoal-600'
                        }`}
                      >
                        {isDebtor ? 'Due' : isAdvance ? 'Advance' : 'Settled'}
                      </span>
                    </div>
                    <ChevronRight className="w-5 h-5 text-charcoal-400 group-hover:text-forest-700 transition-colors hidden sm:block" />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="p-12 text-center space-y-2">
            <p className="text-sm font-bold text-charcoal-800">No customers found</p>
            <p className="text-xs text-charcoal-500">
              Try adjusting your search query or add a new customer to your ledger.
            </p>
          </div>
        )}
      </div>

      {/* Add Customer Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/60 backdrop-blur-xs animate-in fade-in">
          <form
            onSubmit={handleCreateCustomer}
            className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-cream-200 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-cream-200 pb-3">
              <h3 className="text-lg font-bold text-forest-900">Add New Customer</h3>
              <button
                type="button"
                onClick={() => setIsAddModalOpen(false)}
                className="p-1 rounded-lg text-charcoal-500 hover:bg-cream-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Ramesh Kumar"
                className="w-full text-xs font-semibold px-3 py-2.5 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Mobile Number (Optional)
              </label>
              <input
                type="tel"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                placeholder="e.g. 9876500001"
                className="w-full text-xs font-semibold px-3 py-2.5 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Address / Landmark (Optional)
              </label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="e.g. Gandhi Bazaar, Shop #12"
                className="w-full text-xs font-semibold px-3 py-2.5 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-charcoal-700 block mb-1">
                Notes
              </label>
              <textarea
                rows={2}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Regular items, settlement pattern, etc."
                className="w-full text-xs font-medium px-3 py-2 border border-cream-300 rounded-xl outline-none focus:ring-2 focus:ring-forest-600"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-cream-200">
              <button
                type="button"
                onClick={() => setIsAddModalOpen(false)}
                className="px-4 py-2 text-xs font-bold text-charcoal-600 hover:bg-cream-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-5 py-2.5 bg-forest-800 hover:bg-forest-900 text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-1.5"
              >
                {createMutation.isPending ? (
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Check className="w-4 h-4" />
                )}
                <span>Save Customer</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
