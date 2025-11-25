/**
 * Constants for Location Modal components.
 */

import { LocationType, OwnerType } from "../../../types/enums";

export const LOCATION_TYPES = [
  { value: LocationType.STATION, label: "Station" },
  { value: LocationType.SHIP, label: "Ship" },
  { value: LocationType.PLAYER_INVENTORY, label: "Player Inventory" },
  { value: LocationType.WAREHOUSE, label: "Warehouse" },
  {
    value: LocationType.STRUCTURE,
    label: "Structure (Moon/Planet/Star System)",
  },
] as const;

export const OWNER_TYPES = [
  { value: OwnerType.USER, label: "User" },
  { value: OwnerType.ORGANIZATION, label: "Organization" },
  { value: OwnerType.SHIP, label: "Ship" },
  { value: OwnerType.WORLD, label: "World (Universe)" },
] as const;
