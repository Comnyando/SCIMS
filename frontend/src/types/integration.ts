/**
 * Integration-related types.
 */

export type IntegrationStatus = "active" | "inactive" | "error";
export type IntegrationType = "webhook" | "api" | string;

export interface Integration {
  id: string;
  name: string;
  type: IntegrationType;
  status: IntegrationStatus;
  user_id: string;
  organization_id: string | null;
  webhook_url: string | null;
  config_data: Record<string, unknown> | null;
  last_tested_at: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface IntegrationCreate {
  name: string;
  type: IntegrationType;
  organization_id?: string | null;
  webhook_url?: string | null;
  api_key?: string | null;
  api_secret?: string | null;
  config_data?: Record<string, unknown> | null;
}

export interface IntegrationUpdate {
  name?: string;
  status?: IntegrationStatus;
  webhook_url?: string | null;
  config_data?: Record<string, unknown> | null;
  api_key?: string | null;
  api_secret?: string | null;
}

export interface IntegrationTestResponse {
  success: boolean;
  message: string;
  data?: Record<string, unknown> | null;
}

export type IntegrationLogStatus = "success" | "error" | "pending";

export interface IntegrationLog {
  id: string;
  integration_id: string;
  event_type: string;
  status: IntegrationLogStatus;
  request_data: Record<string, unknown> | null;
  response_data: Record<string, unknown> | null;
  error_message: string | null;
  execution_time_ms: number | null;
  timestamp: string;
}

export interface IntegrationLogsResponse {
  logs: IntegrationLog[];
  total: number;
  skip: number;
  limit: number;
  pages: number;
}
