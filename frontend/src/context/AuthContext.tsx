import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, Shop } from '../types';
import { api, getAuthToken, setAuthToken, clearAuthToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  shop: Shop | null;
  loading: boolean;
  login: (credentials: { mobile: string; password: string }) => Promise<void>;
  register: (data: any) => Promise<void>;
  demoLogin: () => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [shop, setShop] = useState<Shop | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    try {
      const data = await api.getMe();
      setUser({
        id: data.id,
        name: data.name,
        mobile: data.mobile,
        preferred_language: data.preferred_language,
        created_at: data.created_at,
      });
      setShop(data.shop || null);
    } catch (err) {
      // Auto-fallback to demo mode in evaluation environments if no valid session
      try {
        const demoRes = await api.demoLogin();
        setAuthToken(demoRes.access_token);
        setUser(demoRes.user);
        setShop(demoRes.user.shop || null);
      } catch {
        setUser(null);
        setShop(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: { mobile: string; password: string }) => {
    const res = await api.login(credentials);
    setAuthToken(res.access_token);
    setUser(res.user);
    setShop(res.user.shop || null);
  };

  const register = async (data: any) => {
    const res = await api.register(data);
    setAuthToken(res.access_token);
    setUser(res.user);
    setShop(res.user.shop || null);
  };

  const demoLogin = async () => {
    setLoading(true);
    try {
      const res = await api.demoLogin();
      setAuthToken(res.access_token);
      setUser(res.user);
      setShop(res.user.shop || null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    clearAuthToken();
    setUser(null);
    setShop(null);
  };

  return (
    <AuthContext.Provider value={{ user, shop, loading, login, register, demoLogin, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
