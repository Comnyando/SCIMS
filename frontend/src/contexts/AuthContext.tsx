/**
 * Authentication context for managing user state and auth operations.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../services";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Load user from localStorage on mount and sync with React Query cache
  useEffect(() => {
    const loadUser = async () => {
      // First, check React Query cache
      const cachedUser = queryClient.getQueryData<User>(["user", "current"]);
      if (cachedUser) {
        setUser(cachedUser);
        setLoading(false);
        return;
      }

      // Fall back to localStorage
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
          // Verify token is still valid by fetching current user
          const currentUser = await apiClient.getCurrentUser();
          setUser(currentUser);
          // Update React Query cache
          queryClient.setQueryData(["user", "current"], currentUser);
        } catch (error) {
          // Token invalid, clear storage
          apiClient.logout();
          setUser(null);
          queryClient.removeQueries({ queryKey: ["user"] });
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [queryClient]);

  // Subscribe to React Query cache changes for user
  useEffect(() => {
    const unsubscribe = queryClient.getQueryCache().subscribe((event) => {
      if (event?.query?.queryKey[0] === "user" && event?.query?.queryKey[1] === "current") {
        const cachedUser = queryClient.getQueryData<User>(["user", "current"]);
        if (cachedUser) {
          setUser(cachedUser);
        }
      }
    });

    return unsubscribe;
  }, [queryClient]);

  const logout = () => {
    apiClient.logout();
    setUser(null);
    // Clear React Query cache
    queryClient.removeQueries({ queryKey: ["user"] });
    navigate("/login");
  };

  const refreshUser = async () => {
    try {
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);
      // Update React Query cache
      queryClient.setQueryData(["user", "current"], currentUser);
    } catch (error) {
      // If refresh fails, logout
      logout();
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

