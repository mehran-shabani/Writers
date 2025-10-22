'use client';

import { useAuth as useAuthContext } from '@/contexts/AuthContext';

/**
 * Custom hook for accessing the authentication context.
 * @returns The authentication context.
 */
export const useAuth = useAuthContext;

/**
 * Custom hook for accessing the current user and loading state.
 * @returns An object containing the current user and the loading state.
 */
export function useUser() {
  const { user, loading } = useAuthContext();
  return { user, loading };
}

/**
 * Custom hook that requires authentication.
 * If the user is not authenticated, it redirects to the login page.
 * @returns An object containing the current user and the loading state.
 */
export function useRequireAuth() {
  const { user, loading } = useAuthContext();
  
  if (!loading && !user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
  
  return { user, loading };
}
