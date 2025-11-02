/**
 * Unified API client that combines all services.
 * Provides a single instance with all API methods.
 * All services share the same axios client instance and token state.
 */

import { ApiClient } from "./client";
import { AuthService } from "./auth";
import { ItemsService } from "./items";
import { LocationsService } from "./locations";
import { InventoryService } from "./inventory";
import { BlueprintsService } from "./blueprints";
import { CraftsService } from "./crafts";
import { OptimizationService } from "./optimization";

// Create a single base client instance to share
const baseClient = new ApiClient();

// Create service instances that share the same client
const authService = new AuthService();
const itemsService = new ItemsService();
const locationsService = new LocationsService();
const inventoryService = new InventoryService();
const blueprintsService = new BlueprintsService();
const craftsService = new CraftsService();
const optimizationService = new OptimizationService();

// Share the client instance across all services
authService.client = baseClient.client;
itemsService.client = baseClient.client;
locationsService.client = baseClient.client;
inventoryService.client = baseClient.client;
blueprintsService.client = baseClient.client;
craftsService.client = baseClient.client;
optimizationService.client = baseClient.client;

// Unified API client that combines all services
class UnifiedApiClient extends AuthService {
  constructor() {
    super();
    // Use the shared client
    this.client = baseClient.client;
    // Share token management methods
    this.setTokens = baseClient.setTokens.bind(baseClient);
    this.logout = baseClient.logout.bind(baseClient);
  }

  items = itemsService;
  locations = locationsService;
  inventory = inventoryService;
  blueprints = blueprintsService;
  crafts = craftsService;
  optimization = optimizationService;
}

export const apiClient = new UnifiedApiClient();
