/**
 * Shared enums and constants for type definitions.
 */

/**
 * Location type enum - defines all valid location types.
 */
export enum LocationType {
  STATION = "station",
  SHIP = "ship",
  PLAYER_INVENTORY = "player_inventory",
  WAREHOUSE = "warehouse",
  STRUCTURE = "structure", // For celestial bodies: moons, planets, star systems, etc.
}

/**
 * Owner type enum - defines all valid owner types for locations.
 */
export enum OwnerType {
  USER = "user",
  ORGANIZATION = "organization",
  SHIP = "ship",
  WORLD = "world", // For universe-owned structures (moons, planets, star systems, etc.)
}
