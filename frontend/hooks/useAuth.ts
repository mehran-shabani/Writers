'use client';

import { useAuth as useAuthContext } from '@/contexts/AuthContext';

export const useAuth = useAuthContext;

export function useUser() {
  const { user, loading } = useAuthContext();
  return { user, loading };
}

export function useRequireAuth() {
  const { user, loading } = useAuthContext();
  
  if (!loading && !user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
  
  return { user, loading };
}
