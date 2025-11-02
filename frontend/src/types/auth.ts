/**
 * Authentication and user-related types.
 */

export interface User {
  id: string;
  email: string;
  username: string | null;
  is_active: boolean;
  is_verified: boolean;
  analytics_consent: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterRequest {
  email: string;
  username?: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends Token {
  user: User;
}

export interface RegisterResponse extends Token {
  user: User;
}
