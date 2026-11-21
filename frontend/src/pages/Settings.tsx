import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import { getPendingOfflineItems } from '../utils/indexedDB';
import { OfflineQueueItem } from '../types';
import {
  Settings as SettingsIcon,
  Store,
  User,
  Globe,
  RotateCcw,
  Wifi,
  CloudSync,
  LogOut,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user, shop, logout, refreshUser } = useAuth();
  const { language, setLanguage, languagesList, t } = useLanguage();

  const [offlineItems, setOfflineItems] = useState<OfflineQueueItem[]>([]);
  const [isResetting, setIsResetting] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    getPendingOfflineItems().then(items => setOfflineItems(items)).catch(() => {});
  }, []);

  const handleResetDemoData = async () => {
    if (confirm('Are you sure you want to reset the demo data to its clean initial state? Ramesh will be reset to ₹0 balance.')) {
      setIsResetting(true);
      setResetSuccess(false);
      try {
        await api.resetDemoData();
        await refreshUser();
        setResetSuccess(true);
        setTimeout(() => setResetSuccess(false), 3000);
      } catch (err: any) {
        alert('Failed to reset demo data: ' + err.message);
      } finally {
        setIsResetting(false);
      }
    }
  };

  const handleSyncNow = async () => {
    if (offlineItems.length === 0) return;
    setIsSyncing(true);
    try {
      await api.pushOfflineQueue(offlineItems);
      const remaining = await getPendingOfflineItems();
      setOfflineItems(remaining);
      alert('Offline transactions successfully synchronized with the cloud ledger!');
    } catch (err: any) {
      alert('Sync failed: ' + err.message);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 sm:space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-2xl sm:text-3xl font-black text-forest-900 tracking-tight">
          {t.settings} & Profile
        </h1>
        <p className="text-xs sm:text-sm text-charcoal-600">
          Manage your kirana shop profile, vernacular preferences, and offline synchronization.
        </p>
      </div>

      {/* Shop Profile Card */}
      <div className="bg-white rounded-3xl border border-cream-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-bold text-forest-900 flex items-center gap-2 border-b border-cream-200 pb-3">
          <Store className="w-4 h-4 text-forest-700" />
          <span>Shop & Shopkeeper Profile</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-cream-50 border border-cream-200">
            <span className="text-3xs uppercase font-bold text-charcoal-500 block">Shopkeeper</span>
            <p className="text-sm font-bold text-charcoal-900 mt-0.5">{user?.name || 'Rajesh Sharma'}</p>
            <p className="text-3xs text-charcoal-500">{user?.mobile || '9876543210'}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-cream-50 border border-cream-200">
            <span className="text-3xs uppercase font-bold text-charcoal-500 block">Shop Name</span>
            <p className="text-sm font-bold text-charcoal-900 mt-0.5">{shop?.shop_name || 'Sharma Kirana Store'}</p>
            <p className="text-3xs text-forest-700 font-semibold">Currency: INR (₹)</p>
          </div>
        </div>
      </div>

      {/* Language Preference Card */}
      <div className="bg-white rounded-3xl border border-cream-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-bold text-forest-900 flex items-center gap-2 border-b border-cream-200 pb-3">
          <Globe className="w-4 h-4 text-forest-700" />
          <span>Language Preference</span>
        </h2>

        <div className="grid grid-cols-3 gap-2.5">
          {languagesList.map((l) => (
            <button
              key={l.code}
              type="button"
              onClick={() => setLanguage(l.code)}
              className={`p-3 rounded-2xl border text-center transition-all ${
                language === l.code
                  ? 'bg-forest-800 text-white border-forest-800 shadow-sm'
                  : 'bg-cream-50 hover:bg-cream-100 text-charcoal-800 border-cream-200'
              }`}
            >
              <p className="text-sm font-black">{l.native}</p>
              <p className={`text-3xs font-medium ${language === l.code ? 'text-forest-200' : 'text-charcoal-500'}`}>
                {l.label}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Offline Sync Status (PART 17) */}
      <div className="bg-white rounded-3xl border border-cream-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-cream-200 pb-3">
          <h2 className="text-sm font-bold text-forest-900 flex items-center gap-2">
            <CloudSync className="w-4 h-4 text-forest-700" />
            <span>Offline Sync Queue (IndexedDB)</span>
          </h2>
          <span className="text-2xs font-bold text-forest-700 bg-forest-50 px-2 py-0.5 rounded">
            PWA Ready
          </span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <div>
            <p className="font-bold text-charcoal-900">
              {offlineItems.length} transactions waiting in local offline queue
            </p>
            <p className="text-3xs text-charcoal-500">
              When disconnected, entries are stored in IndexedDB and synchronized automatically.
            </p>
          </div>
          {offlineItems.length > 0 && (
            <button
              onClick={handleSyncNow}
              disabled={isSyncing}
              className="px-3.5 py-1.5 bg-forest-800 text-white text-xs font-bold rounded-xl shadow-xs"
            >
              {isSyncing ? 'Syncing...' : 'Sync Now'}
            </button>
          )}
        </div>
      </div>

      {/* Demonstration Reset & Evaluation (PART 21) */}
      <div className="bg-white rounded-3xl border border-cream-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-bold text-forest-900 flex items-center gap-2 border-b border-cream-200 pb-3">
          <RotateCcw className="w-4 h-4 text-forest-700" />
          <span>Demo Data Management</span>
        </h2>

        <p className="text-xs text-charcoal-600">
          Reset the database to initial clean demo condition (Ramesh ₹0 balance, Suresh ₹850, Priya ₹420, Anjali ₹0, Kumar ₹1,200). Use this to re-run acceptance tests.
        </p>

        {resetSuccess && (
          <div className="p-3 bg-forest-50 border border-forest-200 text-forest-800 rounded-xl text-xs font-bold flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>Demo data successfully reset! Ramesh is at ₹0 balance.</span>
          </div>
        )}

        <button
          onClick={handleResetDemoData}
          disabled={isResetting}
          className="px-4 py-2.5 rounded-xl border border-cream-300 text-charcoal-800 hover:bg-cream-100 text-xs font-bold flex items-center gap-2 transition-colors"
        >
          <RotateCcw className={`w-4 h-4 ${isResetting ? 'animate-spin' : ''}`} />
          <span>{isResetting ? 'Resetting...' : 'Reset Demo Data to Initial State'}</span>
        </button>
      </div>

      {/* Logout */}
      <div className="pt-2">
        <button
          onClick={logout}
          className="w-full py-3 rounded-2xl bg-white border border-red-200 text-red-600 font-bold text-xs hover:bg-red-50 flex items-center justify-center gap-2 transition-colors shadow-2xs"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out of Shop Account</span>
        </button>
      </div>
    </div>
  );
};
