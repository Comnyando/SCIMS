/**
 * Item-related types.
 */

export interface Item {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  subcategory: string | null;
  rarity: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface ItemCreate {
  name: string;
  description?: string;
  category?: string;
  subcategory?: string;
  rarity?: string;
  metadata?: Record<string, unknown>;
}

export interface ItemUpdate {
  name?: string;
  description?: string;
  category?: string;
  subcategory?: string;
  rarity?: string;
  metadata?: Record<string, unknown>;
}

