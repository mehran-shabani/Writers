import api from './api';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/auth';

export const authService = {
  /**
   * Logs in a user.
   * @param credentials - The user's login credentials.
   * @returns The authenticated user.
   */
  async login(credentials: LoginRequest): Promise<User> {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  /**
   * Registers a new user.
   * @param data - The user's registration data.
   * @returns The newly registered user.
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Logs out the current user.
   */
  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  /**
   * Retrieves the currently authenticated user.
   * @returns The current user, or null if not authenticated.
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      return null;
    }
  },

  /**
   * Refreshes the authentication token.
   * @returns True if the token was successfully refreshed, otherwise false.
   */
  async refreshToken(): Promise<boolean> {
    try {
      await api.post('/auth/refresh');
      return true;
    } catch (error) {
      return false;
    }
  },
};
