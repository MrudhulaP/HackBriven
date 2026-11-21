import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Globe, Store, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const { user, shop, refreshUser } = useAuth();
  const { language, setLanguage, languagesList } = useLanguage();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleResetDemo = async () => {
    if (confirm('Reset demo ledger to clean state (Ramesh ₹0 balance)?')) {
      setIsResetting(true);
      try {
        await api.resetDemoData();
        await refreshUser();
        window.location.reload();
      } catch (err) {
        alert('Could not reset demo data');
      } finally {
        setIsResetting(false);
      }
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-cream-200 px-4 lg:px-8 py-3 flex items-center justify-between shadow-xs">
      {/* Left: Shop Branding & Identity */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-forest-800 flex items-center justify-center text-white shadow-xs">
          <Store className="w-5 h-5 text-forest-300" />
        </div>
        <div>
          <h1 className="text-base font-bold text-forest-900 leading-tight">
            {shop?.shop_name || 'BolKhata Kirana'}
          </h1>
          <p className="text-xs text-charcoal-600 flex items-center gap-1.5">
            <span>{user?.name || 'Shopkeeper'}</span>
            <span className="inline-block w-1 h-1 rounded-full bg-forest-500"></span>
            <span className="font-medium text-forest-700">₹ INR</span>
          </p>
        </div>
      </div>

      {/* Right: Language Selector, Online/Offline, Demo Reset */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Offline / Online Pill */}
        <div
          className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            isOnline
              ? 'bg-forest-50 border-forest-200 text-forest-700'
              : 'bg-amber-50 border-amber-200 text-amber-700 animate-pulse'
          }`}
        >
          {isOnline ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          <span>{isOnline ? 'Online' : 'Offline'}</span>
        </div>

        {/* Demo Reset button */}
        <button
          onClick={handleResetDemo}
          disabled={isResetting}
          title="Reset sample ledger to default"
          className="text-xs font-semibold px-2.5 py-1.5 rounded-lg border border-cream-300 text-charcoal-700 hover:bg-cream-100 flex items-center gap-1 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
          <span className="hidden md:inline">Reset Demo</span>
        </button>

        {/* Language Selector Dropdown */}
        <div className="relative flex items-center">
          <label htmlFor="lang-select" className="sr-only">Language</label>
          <Globe className="w-4 h-4 text-forest-700 absolute left-2.5 pointer-events-none" />
          <select
            id="lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value as any)}
            className="pl-8 pr-7 py-1.5 text-xs font-semibold bg-cream-50 border border-cream-300 rounded-lg text-forest-900 focus:outline-none focus:ring-2 focus:ring-forest-600 cursor-pointer appearance-none shadow-2xs"
          >
            {languagesList.map((l) => (
              <option key={l.code} value={l.code}>
                {l.native} ({l.label})
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute right-2 text-forest-700 text-2xs">▼</div>
        </div>
      </div>
    </header>
  );
};
