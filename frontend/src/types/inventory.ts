/**
 * Inventory-related types.
 */

export interface InventoryStock {
  item_id: string;
  location_id: string;
  quantity: string; // Decimal as string
  reserved_quantity: string;
  available_quantity: string;
  item_name: string;
  item_category: string | null;
  location_name: string;
  location_type: string;
  last_updated: string;
  updated_by_username: string | null;
}

export interface InventoryAdjust {
  item_id: string;
  location_id: string;
  quantity_change: string; // Decimal as string
  notes?: string;
}

export interface InventoryTransfer {
  item_id: string;
  from_location_id: string;
  to_location_id: string;
  quantity: string; // Decimal as string
  notes?: string;
}

export interface InventoryHistory {
  id: string;
  item_id: string;
  item_name: string;
  location_id: string;
  location_name: string;
  quantity_change: string; // Decimal as string
  transaction_type: "add" | "remove" | "transfer" | "craft" | "consume";
  performed_by_username: string;
  timestamp: string;
  notes: string | null;
}

export interface StockReservation {
  item_id: string;
  location_id: string;
  quantity: string; // Decimal as string
  notes?: string;
}

