/**
 * Inventory service methods.
 */

import { ApiClient } from "./client";
import type {
  InventoryStock,
  InventoryAdjust,
  InventoryTransfer,
  InventoryHistory,
  StockReservation,
} from "../types/inventory";
import type { PaginatedResponse } from "../types/common";

export class InventoryService extends ApiClient {
  async getInventory(
    skip = 0,
    limit = 50,
    item_id?: string,
    location_id?: string,
    search?: string
  ): Promise<PaginatedResponse<InventoryStock>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (item_id) params.append("item_id", item_id);
    if (location_id) params.append("location_id", location_id);
    if (search) params.append("search", search);

    const response = await this.client.get<PaginatedResponse<InventoryStock>>(
      `/inventory?${params}`
    );
    return response.data;
  }

  async adjustInventory(data: InventoryAdjust): Promise<InventoryStock> {
    const response = await this.client.post<InventoryStock>("/inventory/adjust", data);
    return response.data;
  }

  async transferInventory(data: InventoryTransfer): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>("/inventory/transfer", data);
    return response.data;
  }

  async reserveStock(data: StockReservation): Promise<InventoryStock> {
    const response = await this.client.post<InventoryStock>("/inventory/reserve", data);
    return response.data;
  }

  async unreserveStock(data: StockReservation): Promise<InventoryStock> {
    const response = await this.client.post<InventoryStock>("/inventory/unreserve", data);
    return response.data;
  }

  async getInventoryHistory(
    skip = 0,
    limit = 50,
    item_id?: string,
    location_id?: string,
    transaction_type?: string
  ): Promise<PaginatedResponse<InventoryHistory>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (item_id) params.append("item_id", item_id);
    if (location_id) params.append("location_id", location_id);
    if (transaction_type) params.append("transaction_type", transaction_type);

    const response = await this.client.get<PaginatedResponse<InventoryHistory>>(
      `/inventory/history?${params}`
    );
    return response.data;
  }
}

