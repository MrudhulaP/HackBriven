import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useNavigate } from 'react-router-dom';
import { Store, Mic, ArrowRight, ShieldCheck, Sparkles, UserPlus, LogIn } from 'lucide-react';

export const Welcome: React.FC = () => {
  const { login, register, demoLogin } = useAuth();
  const { language, setLanguage, languagesList } = useLanguage();
  const navigate = useNavigate();

  const [mode, setMode] = useState<'welcome' | 'login' | 'register'>('welcome');
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [shopName, setShopName] = useState('');
  const [prefLang, setPrefLang] = useState('hi');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDemo = async () => {
    setIsLoading(true);
    setError('');
    try {
      await demoLogin();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await login({ mobile, password });
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await register({
        name,
        shop_name: shopName,
        mobile,
        password,
        preferred_language: prefLang,
        currency: 'INR'
      });
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col justify-between p-4 sm:p-8 font-sans">
      {/* Top Bar */}
      <div className="max-w-5xl mx-auto w-full flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img src="/favicon.svg" alt="BolKhata" className="w-10 h-10 rounded-2xl shadow-sm" />
          <div>
            <h1 className="text-xl font-black text-forest-900 leading-none">
              Bol<span className="text-forest-600">Khata</span>
            </h1>
            <p className="text-3xs text-charcoal-500 font-semibold tracking-wide">
              The Ledger You Talk To.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as any)}
            className="text-xs font-bold px-3 py-1.5 bg-white border border-cream-300 rounded-xl text-forest-900 shadow-2xs cursor-pointer"
          >
            {languagesList.map((l) => (
              <option key={l.code} value={l.code}>
                {l.native}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Content Hero */}
      <div className="max-w-md mx-auto w-full my-auto py-8">
        {mode === 'welcome' && (
          <div className="text-center space-y-6 animate-in fade-in">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forest-100 text-forest-800 text-xs font-bold border border-forest-200">
              <Sparkles className="w-3.5 h-3.5 text-amberGold-600" />
              <span>Voice AI for Bharat Retail</span>
            </div>

            <div className="space-y-2">
              <h2 className="text-3xl sm:text-4xl font-black text-forest-900 tracking-tight">
                BolKhata
              </h2>
              <p className="text-lg font-bold text-forest-700">
                "The Ledger You Talk To."
              </p>
              <p className="text-sm text-charcoal-600">
                Your shop. Your language. Your voice.
              </p>
            </div>

            <div className="p-4 bg-white rounded-2xl border border-cream-200 shadow-xs text-left space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-forest-800">
                <ShieldCheck className="w-4 h-4 text-forest-600" />
                <span>Instant Kirana Digital Udhaar Register</span>
              </div>
              <p className="text-xs text-charcoal-600 leading-relaxed">
                Replace handwritten notebooks with natural voice commands. Record credit & payments in Hindi, Kannada, and English.
              </p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-medium">
                {error}
              </div>
            )}

            {/* Main Action Buttons */}
            <div className="space-y-3 pt-2">
              {/* One Click Demo Access */}
              <button
                onClick={handleDemo}
                disabled={isLoading}
                className="w-full py-3.5 px-6 rounded-2xl bg-forest-800 hover:bg-forest-900 text-white font-extrabold text-sm shadow-md flex items-center justify-center gap-2.5 transition-all active:scale-98"
              >
                {isLoading ? (
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Sparkles className="w-4 h-4 text-amberGold-500" />
                )}
                <span>Explore in Demo Mode (Sharma Kirana)</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="grid grid-cols-2 gap-2.5">
                <button
                  onClick={() => setMode('login')}
                  className="py-3 px-4 rounded-xl bg-white hover:bg-cream-50 border border-cream-300 text-forest-900 font-bold text-xs shadow-2xs flex items-center justify-center gap-1.5"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Login</span>
                </button>
                <button
                  onClick={() => setMode('register')}
                  className="py-3 px-4 rounded-xl bg-white hover:bg-cream-50 border border-cream-300 text-forest-900 font-bold text-xs shadow-2xs flex items-center justify-center gap-1.5"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Register Shop</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Login Screen */}
        {mode === 'login' && (
          <form onSubmit={handleLoginSubmit} className="bg-white p-6 rounded-3xl border border-cream-200 shadow-sm space-y-4 animate-in fade-in">
            <div className="flex items-center justify-between border-b border-cream-200 pb-3">
              <h3 className="text-lg font-bold text-forest-900">Shopkeeper Login</h3>
              <button
                type="button"
                onClick={() => setMode('welcome')}
                className="text-xs text-charcoal-500 hover:underline"
              >
                Back
              </button>
            </div>

            {error && <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl">{error}</div>}

            <div className="space-y-1">
              <label className="text-xs font-bold text-charcoal-700">Mobile Number</label>
              <input
                type="tel"
                required
                value={mobile}
                onChange={e => setMobile(e.target.value)}
                placeholder="e.g. 9876543210"
                className="w-full px-3 py-2 text-sm border border-cream-300 rounded-xl focus:ring-2 focus:ring-forest-600 outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-charcoal-700">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 text-sm border border-cream-300 rounded-xl focus:ring-2 focus:ring-forest-600 outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-forest-800 hover:bg-forest-900 text-white font-bold text-xs rounded-xl shadow-sm flex items-center justify-center gap-2"
            >
              {isLoading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <LogIn className="w-4 h-4" />}
              <span>Sign In</span>
            </button>

            <p className="text-center text-xs text-charcoal-500 pt-2">
              Demo credentials: <strong className="text-forest-800">9876543210 / demo1234</strong>
            </p>
          </form>
        )}

        {/* Register Screen */}
        {mode === 'register' && (
          <form onSubmit={handleRegisterSubmit} className="bg-white p-6 rounded-3xl border border-cream-200 shadow-sm space-y-3.5 animate-in fade-in">
            <div className="flex items-center justify-between border-b border-cream-200 pb-3">
              <h3 className="text-lg font-bold text-forest-900">Register New Shop</h3>
              <button
                type="button"
                onClick={() => setMode('welcome')}
                className="text-xs text-charcoal-500 hover:underline"
              >
                Back
              </button>
            </div>

            {error && <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl">{error}</div>}

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-2xs font-bold text-charcoal-700">Shopkeeper Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={e => setName(e.target.value)}
                  placeholder="e.g. Ramesh Patel"
                  className="w-full px-3 py-2 text-xs border border-cream-300 rounded-xl"
                />
              </div>
              <div>
                <label className="text-2xs font-bold text-charcoal-700">Shop Name</label>
                <input
                  type="text"
                  required
                  value={shopName}
                  onChange={e => setShopName(e.target.value)}
                  placeholder="e.g. Patel Provision Store"
                  className="w-full px-3 py-2 text-xs border border-cream-300 rounded-xl"
                />
              </div>
            </div>

            <div>
              <label className="text-2xs font-bold text-charcoal-700">Mobile Number</label>
              <input
                type="tel"
                required
                value={mobile}
                onChange={e => setMobile(e.target.value)}
                placeholder="10-digit mobile"
                className="w-full px-3 py-2 text-xs border border-cream-300 rounded-xl"
              />
            </div>

            <div>
              <label className="text-2xs font-bold text-charcoal-700">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Choose password"
                className="w-full px-3 py-2 text-xs border border-cream-300 rounded-xl"
              />
            </div>

            <div>
              <label className="text-2xs font-bold text-charcoal-700">Preferred Language</label>
              <select
                value={prefLang}
                onChange={e => setPrefLang(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-cream-300 rounded-xl bg-white"
              >
                <option value="hi">Hindi (हिंदी)</option>
                <option value="kn">Kannada (ಕನ್ನಡ)</option>
                <option value="en">English</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-forest-800 hover:bg-forest-900 text-white font-bold text-xs rounded-xl shadow-sm flex items-center justify-center gap-2"
            >
              {isLoading ? <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <UserPlus className="w-4 h-4" />}
              <span>Create Account</span>
            </button>
          </form>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center text-3xs text-charcoal-500 space-y-1">
        <p>BolKhata • Neural Nomads • New Horizon College of Engineering</p>
        <p>Theme: Voice AI for Bharat – Financial Record-Keeping for Informal Retail</p>
      </footer>
    </div>
  );
};
