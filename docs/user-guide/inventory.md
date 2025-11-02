# Inventory Management User Guide

This guide explains how to use the SCIMS inventory management system to track your items and resources across different locations.

## Overview

The inventory management system allows you to:
- Track item quantities across multiple locations (stations, ships, warehouses, player inventories)
- Adjust inventory levels (add or remove items)
- Transfer items between locations
- Reserve stock for planned operations
- View complete transaction history
- Filter and search your inventory

## Accessing Inventory

1. **Login** to your SCIMS account
2. Navigate to the **Inventory** page from the main navigation
3. You'll see all inventory items at locations you have access to

## Viewing Inventory

### Inventory Table

The inventory page displays:
- **Item**: Item name and category
- **Location**: Where the item is stored (station, ship, warehouse, etc.)
- **Quantity**: Total number of items
- **Reserved**: Items reserved for planned operations
- **Available**: Items available for use (Quantity - Reserved)
- **Last Updated**: When the stock was last modified and by whom

### Filtering Inventory

You can filter your inventory view using:
- **Search by item name**: Type in the search box to find specific items
- **Filter by item ID**: Enter a specific item UUID
- **Filter by location ID**: Enter a specific location UUID

### Pagination

If you have many inventory records, use the pagination controls at the bottom:
- **Previous/Next buttons**: Navigate between pages
- **Page indicator**: Shows current page and total pages

## Adjusting Inventory

To add or remove items from inventory:

1. Navigate to the **Inventory** page
2. Find the item and location you want to adjust
3. Use the inventory adjustment feature (when implemented)
4. Enter the quantity change:
   - **Positive number**: Adds items (e.g., `+10`)
   - **Negative number**: Removes items (e.g., `-5`)

### Access Requirements

- **User-owned locations**: Full control
- **Organization locations**: Requires "member" role or higher
- **Canonical locations**: Read-only (public reference data)

## Transferring Items

To move items between locations:

1. Select the source location and item
2. Select the destination location
3. Enter the quantity to transfer
4. Confirm the transfer

The system will:
- Remove items from the source location
- Add items to the destination location
- Create transaction history records for both operations

### Transfer Rules

- You must have "member" role or higher at both source and destination locations
- Cannot transfer more items than are available (after reserved quantity)
- Transfers create audit trail records for tracking

## Stock Reservations

Stock reservations allow you to set aside items for planned operations (like crafting):

### Reserving Stock

1. Select the item and location
2. Enter the quantity to reserve
3. The reserved quantity is deducted from available stock

### Unreserving Stock

1. Find the reserved stock entry
2. Use the unreserve feature
3. The quantity returns to available stock

### Reservation Benefits

- Prevents accidental use of items needed for planned operations
- Shows "Reserved" vs "Available" quantities clearly
- Helps with planning and resource allocation

## Transaction History

Every inventory change is recorded in the transaction history:

- **Adjustments**: When items are added or removed
- **Transfers**: When items move between locations
- **Reservations**: When stock is reserved or unreserved

### Viewing History

1. Navigate to the Inventory History view
2. Filter by:
   - Item ID
   - Location ID
   - Transaction type (adjust, transfer, reserve, etc.)
3. Review the complete audit trail

## Location Access

You can view inventory at:
- **Your locations**: Personal storage locations you own
- **Organization locations**: Locations owned by organizations you're a member of
- **Ship cargo**: Items in ships you own or have access to
- **Canonical locations**: Public reference locations (read-only)

Your access level determines what operations you can perform:
- **Viewer**: Can view inventory
- **Member**: Can adjust and transfer inventory
- **Owner**: Full administrative control

## Best Practices

1. **Regular Updates**: Keep inventory levels accurate by updating when items change
2. **Use Reservations**: Reserve stock for planned operations to prevent conflicts
3. **Check History**: Review transaction history to track changes and audit operations
4. **Location Organization**: Use descriptive location names to easily find items
5. **Category Filtering**: Use item categories to organize and filter large inventories

## Troubleshooting

### Can't see inventory at a location
- Verify you have access to that location
- Check that you're a member of the organization (for org-owned locations)
- Ensure the location has items stocked

### Can't adjust inventory
- Verify you have "member" role or higher at the location
- Check that sufficient items are available (for removals)
- Ensure you're not trying to remove reserved items

### Transfer fails
- Verify access at both source and destination
- Check available quantity (after reserved) at source
- Ensure destination location exists and is accessible

---

For API access, see the [Backend README](../backend/README.md#inventory-api) for endpoint documentation.

