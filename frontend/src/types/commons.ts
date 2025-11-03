/**
 * TypeScript types for Commons system.
 */

export type EntityType =
  | "item"
  | "blueprint"
  | "location"
  | "ingredient"
  | "taxonomy";

export type SubmissionStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "needs_changes"
  | "merged";

export type ModerationAction =
  | "approve"
  | "reject"
  | "request_changes"
  | "merge"
  | "edit";

export interface CommonsSubmissionBase {
  entity_type: EntityType;
  entity_payload: Record<string, unknown>;
  source_reference?: string | null;
}

export interface CommonsSubmissionCreate extends CommonsSubmissionBase {}

export interface CommonsSubmissionUpdate {
  entity_payload?: Record<string, unknown>;
  source_reference?: string | null;
}

export interface CommonsSubmissionResponse extends CommonsSubmissionBase {
  id: string;
  submitter_id: string;
  status: SubmissionStatus;
  review_notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommonsSubmissionsListResponse {
  submissions: CommonsSubmissionResponse[];
  total: number;
  skip: number;
  limit: number;
  pages: number;
}

export interface CommonsModerationActionCreate {
  action: ModerationAction;
  action_payload?: Record<string, unknown>;
  notes?: string | null;
}

export interface CommonsModerationActionResponse {
  id: string;
  submission_id: string;
  moderator_id: string;
  action: ModerationAction;
  action_payload?: Record<string, unknown> | null;
  notes?: string | null;
  created_at: string;
}

export interface CommonsEntityResponse {
  id: string;
  entity_type: EntityType;
  canonical_id?: string | null;
  data: Record<string, unknown>;
  version: number;
  is_public: boolean;
  created_by: string;
  created_at: string;
  tags?: string[] | null;
}

export interface CommonsEntitiesListResponse {
  entities: CommonsEntityResponse[];
  total: number;
  skip: number;
  limit: number;
  pages: number;
}

export interface TagCreate {
  name: string;
  description?: string | null;
}

export interface TagResponse {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
}

export interface TagsListResponse {
  tags: TagResponse[];
  total: number;
}
