/**
 * Base Axios API client with authentication interceptors.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

export class ApiClient {
  public client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshed = await this.refreshAccessToken();
            if (refreshed && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${this.getAccessToken()}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            this.logout();
            window.location.href = "/login";
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Token management
  protected getAccessToken(): string | null {
    return localStorage.getItem("access_token");
  }

  protected getRefreshToken(): string | null {
    return localStorage.getItem("refresh_token");
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  }

  logout(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  }

  protected async refreshAccessToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const response = await axios.post<{ access_token: string; refresh_token: string }>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken }
      );
      this.setTokens(response.data.access_token, response.data.refresh_token);
      return true;
    } catch (error) {
      return false;
    }
  }
}

