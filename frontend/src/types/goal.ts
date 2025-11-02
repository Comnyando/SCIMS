/**
 * Goal-related types.
 */

export type GoalStatus = "active" | "completed" | "cancelled";

export interface GoalItem {
  id: string;
  item_id: string;
  target_quantity: number;
  item?: {
    id: string;
    name: string;
    description: string | null;
    category: string | null;
  } | null;
}

export interface GoalItemCreate {
  item_id: string;
  target_quantity: number;
}

export interface GoalItemProgress {
  item_id: string;
  current_quantity: number;
  target_quantity: number;
  progress_percentage: number;
  is_completed: boolean;
}

export interface GoalProgress {
  current_quantity: number;
  target_quantity: number;
  progress_percentage: number;
  is_completed: boolean;
  days_remaining: number | null;
  item_progress: GoalItemProgress[];
}

export interface Goal {
  id: string;
  name: string;
  description: string | null;
  organization_id: string | null;
  created_by: string;
  goal_items: GoalItem[];
  target_date: string | null;
  status: GoalStatus;
  created_at: string;
  updated_at: string;
  progress_data: Record<string, unknown> | null;
  organization?: {
    id: string;
    name: string;
    slug: string;
  } | null;
  creator?: {
    id: string;
    username: string;
    email: string;
  } | null;
}

export interface GoalCreate {
  name: string;
  description?: string | null;
  organization_id?: string | null;
  goal_items: GoalItemCreate[];
  target_date?: string | null;
}

export interface GoalUpdate {
  name?: string;
  description?: string | null;
  organization_id?: string | null;
  goal_items?: GoalItemCreate[];
  target_date?: string | null;
  status?: GoalStatus;
}

export interface GoalProgressResponse {
  goal_id: string;
  status: GoalStatus;
  progress: GoalProgress;
  last_calculated_at: string | null;
}
