import React from 'react';
import { NavLink } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Mic,
  Users,
  ReceiptText,
  BarChart3,
  BellRing,
  Settings,
  LogOut,
  Sparkles
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { t } = useLanguage();
  const { logout } = useAuth();

  const navItems = [
    { to: '/', label: t.dashboard, icon: LayoutDashboard },
    { to: '/voice', label: t.voiceAssistant, icon: Mic, highlight: true },
    { to: '/customers', label: t.customers, icon: Users },
    { to: '/transactions', label: t.transactions, icon: ReceiptText },
    { to: '/reports', label: t.reports, icon: BarChart3 },
    { to: '/reminders', label: t.reminders, icon: BellRing },
    { to: '/settings', label: t.settings, icon: Settings },
  ];

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-forest-900 text-white min-h-screen border-r border-forest-800 shrink-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-forest-800/80">
        <div className="flex items-center gap-3">
          <img src="/favicon.svg" alt="BolKhata Logo" className="w-9 h-9 rounded-xl shadow-md" />
          <div>
            <h2 className="text-xl font-extrabold tracking-tight text-white leading-tight">
              Bol<span className="text-forest-400">Khata</span>
            </h2>
            <p className="text-2xs text-forest-300 font-medium tracking-wide">
              The Ledger You Talk To.
            </p>
          </div>
        </div>
        <div className="mt-3 px-2.5 py-1 bg-forest-800/60 rounded-md border border-forest-700/50 flex items-center justify-between text-3xs text-forest-300">
          <span>Team: Neural Nomads</span>
          <span>NHCE</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-forest-700 text-white shadow-sm ring-1 ring-forest-500/30'
                    : 'text-forest-200/80 hover:bg-forest-800 hover:text-white'
                } ${item.highlight ? 'relative' : ''}`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              <span>{item.label}</span>
              {item.highlight && (
                <span className="ml-auto flex items-center gap-1 text-3xs bg-amberGold-500/20 text-amberGold-500 px-2 py-0.5 rounded-full font-bold border border-amberGold-500/30">
                  <Sparkles className="w-2.5 h-2.5" /> Voice
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Footer & Logout */}
      <div className="p-4 border-t border-forest-800/80 space-y-3">
        <div className="bg-forest-800/50 rounded-xl p-3 border border-forest-700/40">
          <p className="text-xs text-forest-200 font-medium">Bharat Voice AI 2026</p>
          <p className="text-3xs text-forest-400">Kannada • Hindi • English</p>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-forest-300 hover:bg-forest-800 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span>Logout / Exit Demo</span>
        </button>
      </div>
    </aside>
  );
};
