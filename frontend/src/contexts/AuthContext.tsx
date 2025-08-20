import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types/api';
import { apiClient } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (userData: {
    email: string;
    password: string;
    full_name?: string;
    contact_number?: string;
    is_venue_owner: boolean;
  }) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        apiClient.setToken(token);
        const response = await apiClient.getProfile();
        if (response.ok && response.data) {
          setUser(response.data.profile);
        } else {
          // Token is invalid, clear it
          setToken(null);
          apiClient.setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (email: string, password: string) => {
    const response = await apiClient.login({ email, password });
    if (response.ok && response.data) {
      const { token: newToken, profile } = response.data;
      setToken(newToken);
      setUser(profile);
      apiClient.setToken(newToken);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const signup = async (userData: {
    email: string;
    password: string;
    full_name?: string;
    contact_number?: string;
    is_venue_owner: boolean;
  }) => {
    const response = await apiClient.signup(userData);
    if (response.ok && response.data) {
      const { token: newToken, profile } = response.data;
      setToken(newToken);
      setUser(profile);
      apiClient.setToken(newToken);
      return { success: true };
    }
    return { success: false, error: response.error };
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    apiClient.setToken(null);
  };

  const value = {
    user,
    token,
    login,
    signup,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};