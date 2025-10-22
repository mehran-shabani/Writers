/**
 * @interface User
 * @description Represents a user object.
 */
export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * @interface LoginRequest
 * @description Represents the request payload for a login attempt.
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * @interface RegisterRequest
 * @description Represents the request payload for a user registration.
 */
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

/**
 * @interface AuthTokenResponse
 * @description Represents the response returned after authentication-related requests.
 */
export interface AuthTokenResponse {
  user: User;
  token_type: string;
}
