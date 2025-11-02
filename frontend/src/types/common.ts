/**
 * Common shared types.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiError {
  detail: string | Record<string, unknown>;
}
