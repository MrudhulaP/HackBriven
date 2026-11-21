import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import {
  LayoutDashboard,
  Users,
  Mic,
  ReceiptText,
  BarChart3
} from 'lucide-react';

export const BottomNav: React.FC = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur border-t border-cream-200 px-3 py-2 flex items-center justify-around shadow-lg">
      <NavLink
        to="/"
        end
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 text-2xs font-semibold ${
            isActive ? 'text-forest-800' : 'text-charcoal-500 hover:text-forest-700'
          }`
        }
      >
        <LayoutDashboard className="w-5 h-5" />
        <span>{t.dashboard}</span>
      </NavLink>

      <NavLink
        to="/customers"
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 text-2xs font-semibold ${
            isActive ? 'text-forest-800' : 'text-charcoal-500 hover:text-forest-700'
          }`
        }
      >
        <Users className="w-5 h-5" />
        <span>{t.customers}</span>
      </NavLink>

      {/* Prominent Center Voice Action Button */}
      <button
        onClick={() => navigate('/voice')}
        aria-label="Talk to BolKhata"
        className="-top-5 relative w-14 h-14 rounded-full bg-forest-800 text-white flex items-center justify-center shadow-lg border-4 border-white active:scale-95 transition-transform"
      >
        <Mic className="w-6 h-6 text-amberGold-500" />
      </button>

      <NavLink
        to="/transactions"
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 text-2xs font-semibold ${
            isActive ? 'text-forest-800' : 'text-charcoal-500 hover:text-forest-700'
          }`
        }
      >
        <ReceiptText className="w-5 h-5" />
        <span>{t.transactions}</span>
      </NavLink>

      <NavLink
        to="/reports"
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 text-2xs font-semibold ${
            isActive ? 'text-forest-800' : 'text-charcoal-500 hover:text-forest-700'
          }`
        }
      >
        <BarChart3 className="w-5 h-5" />
        <span>{t.reports}</span>
      </NavLink>
    </div>
  );
};
