/**
 * Authentication-related types.
 */

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username?: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    username?: string | null;
    is_active: boolean;
    is_verified: boolean;
  };
}

export interface RegisterResponse extends LoginResponse {}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountRequest {
  password: string;
  confirm: boolean;
}

export interface User {
  id: string;
  email: string;
  username?: string | null;
  is_active: boolean;
  is_verified: boolean;
}
