/**
 * Authentication service for user account management.
 */

import { ApiClient } from "./client";
import type {
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  RegisterResponse,
  ChangePasswordRequest,
  DeleteAccountRequest,
  User,
} from "../types/auth";

export class AuthService extends ApiClient {
  /**
   * Login with email and password.
   * Stores tokens in localStorage and returns user data.
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>(
      "/auth/login",
      credentials
    );
    // Store tokens
    this.setTokens(response.data.access_token, response.data.refresh_token);
    // Store user data
    localStorage.setItem("user", JSON.stringify(response.data.user));
    return response.data;
  }

  /**
   * Register a new user account.
   * Stores tokens in localStorage and returns user data.
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.client.post<RegisterResponse>(
      "/auth/register",
      data
    );
    // Store tokens
    this.setTokens(response.data.access_token, response.data.refresh_token);
    // Store user data
    localStorage.setItem("user", JSON.stringify(response.data.user));
    return response.data;
  }

  /**
   * Change the current user's password.
   */
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await this.client.post("/auth/change-password", data);
  }

  /**
   * Delete the current user's account.
   */
  async deleteAccount(data: DeleteAccountRequest): Promise<void> {
    await this.client.post("/auth/account/delete", data);
  }

  /**
   * Get the current authenticated user.
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>("/auth/me");
    return response.data;
  }
}
