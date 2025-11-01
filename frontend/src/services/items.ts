/**
 * Items service methods.
 */

import { ApiClient } from "./client";
import type { Item, ItemCreate, ItemUpdate } from "../types/item";
import type { PaginatedResponse } from "../types/common";

export class ItemsService extends ApiClient {
  async getItems(
    skip = 0,
    limit = 50,
    search?: string,
    category?: string
  ): Promise<PaginatedResponse<Item>> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (search) params.append("search", search);
    if (category) params.append("category", category);

    const response = await this.client.get<PaginatedResponse<Item>>(`/items?${params}`);
    return response.data;
  }

  async getItem(id: string): Promise<Item> {
    const response = await this.client.get<Item>(`/items/${id}`);
    return response.data;
  }

  async createItem(data: ItemCreate): Promise<Item> {
    const response = await this.client.post<Item>("/items", data);
    return response.data;
  }

  async updateItem(id: string, data: ItemUpdate): Promise<Item> {
    const response = await this.client.put<Item>(`/items/${id}`, data);
    return response.data;
  }

  async deleteItem(id: string): Promise<void> {
    await this.client.delete(`/items/${id}`);
  }
}

