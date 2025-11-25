# API Usage Examples

Practical examples for using the SCIMS API to accomplish common tasks.

## Table of Contents

- [Authentication](#authentication)
- [Inventory Management](#inventory-management)
- [Crafting Workflows](#crafting-workflows)
- [Goals & Progress](#goals--progress)
- [Optimization](#optimization)
- [Integrations](#integrations)

## Authentication

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "newuser",
    "is_active": true,
    "is_verified": false
  }
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Using Authentication Token

```bash
TOKEN="your-access-token-here"

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## Inventory Management

### Create an Item

```bash
curl -X POST "http://localhost:8000/api/v1/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Iron Ore",
    "description": "Raw iron ore extracted from asteroids",
    "category": "Materials",
    "subcategory": "Ore",
    "rarity": "Common"
  }'
```

### Create a Location

```bash
curl -X POST "http://localhost:8000/api/v1/locations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Port Tressler",
    "type": "station",
    "owner_type": "user",
    "owner_id": "your-user-id"
  }'
```

### Add Inventory

```bash
curl -X POST "http://localhost:8000/api/v1/inventory/adjust" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "item-uuid",
    "location_id": "location-uuid",
    "quantity_change": 100.0,
    "reason": "Initial stock"
  }'
```

### Transfer Inventory

```bash
curl -X POST "http://localhost:8000/api/v1/inventory/transfer" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "item-uuid",
    "source_location_id": "source-location-uuid",
    "destination_location_id": "dest-location-uuid",
    "quantity": 50.0,
    "reason": "Moving to ship"
  }'
```

### List Inventory

```bash
# All inventory
curl -X GET "http://localhost:8000/api/v1/inventory" \
  -H "Authorization: Bearer $TOKEN"

# Filter by location
curl -X GET "http://localhost:8000/api/v1/inventory?location_id=location-uuid" \
  -H "Authorization: Bearer $TOKEN"

# Filter by item
curl -X GET "http://localhost:8000/api/v1/inventory?item_id=item-uuid" \
  -H "Authorization: Bearer $TOKEN"

# Search
curl -X GET "http://localhost:8000/api/v1/inventory?search=iron" \
  -H "Authorization: Bearer $TOKEN"
```

## Crafting Workflows

### Create a Blueprint

```bash
curl -X POST "http://localhost:8000/api/v1/blueprints" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Steel Ingot Recipe",
    "description": "Refine iron ore into steel ingots",
    "category": "Refining",
    "crafting_time_minutes": 60,
    "output_item_id": "steel-ingot-uuid",
    "output_quantity": 1.0,
    "blueprint_data": {
      "ingredients": [
        {
          "item_id": "iron-ore-uuid",
          "quantity": 10.0,
          "optional": false
        }
      ]
    },
    "is_public": false
  }'
```

### Create a Craft

```bash
# Without reservation
curl -X POST "http://localhost:8000/api/v1/crafts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "blueprint_id": "blueprint-uuid",
    "output_location_id": "location-uuid"
  }'

# With ingredient reservation
curl -X POST "http://localhost:8000/api/v1/crafts?reserve_ingredients=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "blueprint_id": "blueprint-uuid",
    "output_location_id": "location-uuid"
  }'
```

### Start a Craft

```bash
curl -X POST "http://localhost:8000/api/v1/crafts/craft-uuid/start" \
  -H "Authorization: Bearer $TOKEN"
```

### Complete a Craft

```bash
curl -X POST "http://localhost:8000/api/v1/crafts/craft-uuid/complete" \
  -H "Authorization: Bearer $TOKEN"
```

### Check Craft Progress

```bash
curl -X GET "http://localhost:8000/api/v1/crafts/craft-uuid/progress" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "in_progress",
  "elapsed_minutes": 30,
  "estimated_completion_minutes": 30,
  "ingredients_status": {
    "total": 2,
    "pending": 0,
    "reserved": 2,
    "fulfilled": 0
  }
}
```

## Goals & Progress

### Create a Goal

```bash
curl -X POST "http://localhost:8000/api/v1/goals" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Build 10 Ships",
    "description": "Craft 10 ships for the fleet",
    "goal_items": [
      {
        "item_id": "ship-uuid",
        "target_quantity": 10.0
      }
    ],
    "target_date": "2025-12-31T23:59:59Z"
  }'
```

### Get Goal Progress

```bash
curl -X GET "http://localhost:8000/api/v1/goals/goal-uuid/progress" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "goal_id": "goal-uuid",
  "status": "active",
  "progress_percentage": 60.0,
  "items_progress": [
    {
      "item_id": "ship-uuid",
      "target_quantity": 10.0,
      "current_quantity": 6.0,
      "progress_percentage": 60.0
    }
  ],
  "estimated_completion_date": "2025-11-15T00:00:00Z"
}
```

## Optimization

### Find Resource Sources

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/find-sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "iron-ore-uuid",
    "required_quantity": 100.0,
    "min_reliability": 0.7
  }'
```

**Response:**
```json
{
  "item_id": "iron-ore-uuid",
  "required_quantity": 100.0,
  "sources": [
    {
      "source_id": "source-uuid",
      "source_type": "stock",
      "location_id": "location-uuid",
      "available_quantity": 50.0,
      "cost": 0.0,
      "reliability": 1.0
    },
    {
      "source_id": "source-uuid-2",
      "source_type": "universe",
      "location_name": "Arial Mining Outpost",
      "available_quantity": 1000.0,
      "cost": 500.0,
      "reliability": 0.85
    }
  ],
  "total_available": 1050.0
}
```

### Get Resource Gap for Craft

```bash
curl -X GET "http://localhost:8000/api/v1/optimization/resource-gap/craft-uuid" \
  -H "Authorization: Bearer $TOKEN"
```

### Suggest Crafts

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/suggest-crafts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_item_id": "ship-uuid",
    "target_quantity": 1.0
  }'
```

## Integrations

### Create an Integration

```bash
curl -X POST "http://localhost:8000/api/v1/integrations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Webhook Integration",
    "type": "webhook",
    "status": "active",
    "webhook_url": "https://example.com/webhook",
    "config": {
      "events": ["inventory.updated", "craft.completed"],
      "retry_count": 3
    }
  }'
```

### Test an Integration

```bash
curl -X POST "http://localhost:8000/api/v1/integrations/integration-uuid/test" \
  -H "Authorization: Bearer $TOKEN"
```

### Export Data

```bash
# Export items as CSV
curl -X GET "http://localhost:8000/api/v1/import-export/items.csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o items_export.csv

# Export inventory as JSON
curl -X GET "http://localhost:8000/api/v1/import-export/inventory.json" \
  -H "Authorization: Bearer $TOKEN" \
  -o inventory_export.json
```

### Import Data

```bash
# Import items from CSV
curl -X POST "http://localhost:8000/api/v1/import-export/items/import" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@items.csv"
```

## Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not enough permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Item not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

**429 Rate Limited:**
```json
{
  "detail": "Rate limit exceeded"
}
```

Headers include:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp
- `Retry-After`: Seconds to wait

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your-token-here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get inventory
response = requests.get(f"{BASE_URL}/inventory", headers=headers)
inventory = response.json()

# Create a craft
craft_data = {
    "blueprint_id": "blueprint-uuid",
    "output_location_id": "location-uuid"
}
response = requests.post(
    f"{BASE_URL}/crafts?reserve_ingredients=true",
    headers=headers,
    json=craft_data
)
craft = response.json()
```

## JavaScript/TypeScript Example

```typescript
const BASE_URL = "http://localhost:8000/api/v1";
const TOKEN = "your-token-here";

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  "Content-Type": "application/json",
};

// Get inventory
const inventoryResponse = await fetch(`${BASE_URL}/inventory`, { headers });
const inventory = await inventoryResponse.json();

// Create a craft
const craftData = {
  blueprint_id: "blueprint-uuid",
  output_location_id: "location-uuid",
};

const craftResponse = await fetch(
  `${BASE_URL}/crafts?reserve_ingredients=true`,
  {
    method: "POST",
    headers,
    body: JSON.stringify(craftData),
  }
);
const craft = await craftResponse.json();
```

## Best Practices

1. **Token Management**
   - Store tokens securely
   - Refresh tokens before expiry
   - Handle token expiration gracefully

2. **Error Handling**
   - Always check response status codes
   - Handle rate limiting (429 errors)
   - Implement retry logic with exponential backoff

3. **Pagination**
   - Use `skip` and `limit` for large datasets
   - Process results in batches
   - Respect `total` and `pages` in responses

4. **Rate Limiting**
   - Monitor rate limit headers
   - Implement request queuing
   - Cache responses when possible

5. **Data Validation**
   - Validate data before sending
   - Handle validation errors (422)
   - Provide user-friendly error messages

---

For complete API reference, see:
- [Swagger UI](http://localhost:8000/docs) (when backend is running)
- [ReDoc](http://localhost:8000/redoc)
- [OpenAPI JSON](http://localhost:8000/openapi.json)

