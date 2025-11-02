/**
 * Analytics-related types.
 */

export interface ConsentResponse {
  analytics_consent: boolean;
  updated_at: string;
}

export interface ConsentUpdate {
  analytics_consent: boolean;
}

export interface UsageStatsResponse {
  total_events: number;
  events_by_type: Record<string, number>;
  top_blueprints: Array<{
    blueprint_id: string;
    name: string;
    uses: number;
  }>;
  top_goals: Array<{
    goal_id: string;
    created_count: number;
  }>;
  period_start: string | null;
  period_end: string | null;
}

export interface RecipeStatsResponse {
  blueprint_id: string;
  blueprint_name: string | null;
  period_start: string;
  period_end: string;
  period_type: string;
  total_uses: number;
  unique_users: number;
  completed_count: number;
  cancelled_count: number;
  completion_rate: number;
}
