/**
 * Authentication service methods.
 */

import { ApiClient } from "./client";
import type { LoginRequest, RegisterRequest, LoginResponse, RegisterResponse, User } from "../types/auth";

export class AuthService extends ApiClient {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>("/auth/login", credentials);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    localStorage.setItem("user", JSON.stringify(response.data.user));
    return response.data;
  }

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.client.post<RegisterResponse>("/auth/register", data);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    localStorage.setItem("user", JSON.stringify(response.data.user));
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>("/auth/me");
    localStorage.setItem("user", JSON.stringify(response.data));
    return response.data;
  }
}

