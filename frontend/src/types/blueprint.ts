/**
 * Blueprint-related types.
 */

export interface BlueprintIngredient {
  item_id: string;
  quantity: number;
  optional?: boolean;
}

export interface Blueprint {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  crafting_time_minutes: number;
  output_item_id: string;
  output_quantity: number;
  blueprint_data: {
    ingredients: BlueprintIngredient[];
  };
  created_by: string;
  is_public: boolean;
  usage_count: number;
  created_at: string;
  output_item?: {
    id: string;
    name: string;
    category: string | null;
  } | null;
  creator?: {
    id: string;
    username: string;
    email: string;
  } | null;
}

export interface BlueprintCreate {
  name: string;
  description?: string;
  category?: string;
  crafting_time_minutes: number;
  output_item_id: string;
  output_quantity: number;
  blueprint_data: {
    ingredients: BlueprintIngredient[];
  };
  is_public?: boolean;
}

export interface BlueprintUpdate {
  name?: string;
  description?: string;
  category?: string;
  crafting_time_minutes?: number;
  output_item_id?: string;
  output_quantity?: number;
  blueprint_data?: {
    ingredients: BlueprintIngredient[];
  };
  is_public?: boolean;
}
