import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from 'react'
import { getCurrentUser } from "../utils/auth";
import type { TokenPayload } from "../types/tokenyPayload";

interface UserContextType {
  user: TokenPayload | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
}

export function UserProvider({ children }: UserProviderProps) {
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUserFromAPI = async (): Promise<TokenPayload | null> => {
    const token = localStorage.getItem('access_token');
    if (!token) return null;

    try {
      const response = await fetch('http://localhost:80/auth/verify-token', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        localStorage.removeItem('access_token');
        return null;
      }

      const data = await response.json();
      return data.user;
    } catch {
      localStorage.removeItem('access_token');
      return null;
    }
  };

  const refreshUser = async () => {
    setLoading(true);
    try {
      const tokenUser = getCurrentUser();
      if (tokenUser) {
        const apiUser = await fetchUserFromAPI();
        setUser(apiUser || tokenUser);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    // window.location.href = "/auth";
    window.location.href = "/";
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, refreshUser, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}