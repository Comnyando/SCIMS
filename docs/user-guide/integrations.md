# Integrations Guide

## Overview

The SCIMS Integration Framework allows you to connect your inventory management system with external services through webhooks and API integrations. This enables automated workflows, data synchronization, and notifications.

## Integration Types

### Webhook Integrations

Webhook integrations send events from SCIMS to external services when certain actions occur (e.g., inventory changes, craft completions).

**Features:**
- HTTP POST requests to configured webhook URLs
- Event logging for debugging and auditing
- Connection testing

**Use Cases:**
- Discord/Slack notifications for inventory alerts
- External inventory tracking systems
- Custom automation workflows

### API Integrations

API integrations allow SCIMS to authenticate and interact with external APIs using encrypted credentials.

**Features:**
- Secure credential storage (encrypted API keys/secrets)
- Custom configuration data
- Connection testing

**Use Cases:**
- External item databases
- Third-party marketplace APIs
- Custom service integrations

## Creating an Integration

### Via Web Interface

1. Navigate to **Integrations** in the main menu
2. Click **Create Integration**
3. Enter a descriptive name
4. Select the integration type:
   - **Webhook**: For outgoing HTTP webhooks
   - **API**: For API-based integrations
5. Configure integration-specific settings:
   - **Webhook**: Enter the webhook URL
   - **API**: Enter API key and secret (encrypted on storage)
6. (Optional) Add configuration data as JSON
7. Click **Create Integration**

### Via API

```bash
# Create a webhook integration
curl -X POST "http://localhost:8000/api/v1/integrations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Discord Notifications",
    "type": "webhook",
    "webhook_url": "https://discord.com/api/webhooks/...",
    "config_data": {
      "channel": "inventory-updates"
    }
  }'

# Create an API integration
curl -X POST "http://localhost:8000/api/v1/integrations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "External Item API",
    "type": "api",
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
    "config_data": {
      "base_url": "https://api.example.com"
    }
  }'
```

## Managing Integrations

### Viewing Integrations

The Integrations page displays:
- Integration name and type
- Current status (active/inactive/error)
- Last test timestamp
- Creation date

You can filter by:
- Status (active, inactive, error)
- Type (webhook, api)

### Editing an Integration

1. Click on an integration to view details
2. Click **Edit**
3. Update the fields as needed
4. For API integrations, leave API key/secret empty to keep existing values, or enter new values to update
5. Click **Update Integration**

### Testing an Integration

1. Navigate to the integration detail page
2. Click **Test Integration**
3. Review the test result message

The test will:
- Verify the webhook URL is reachable (for webhooks)
- Test API credentials (for API integrations)
- Log the test result in the integration logs

### Viewing Integration Logs

Integration logs track all events related to an integration:
- Test requests
- Webhook deliveries (sent/received)
- API calls
- Errors and execution times

To view logs:
1. Navigate to the integration detail page
2. Scroll to the **Logs** section
3. Review the log entries with timestamps, status, and details

### Deleting an Integration

1. Navigate to the integration detail page
2. Click **Delete**
3. Confirm deletion

**Warning:** Deleting an integration permanently removes all associated logs and configuration. This action cannot be undone.

## Integration Status

Integrations can have the following statuses:

- **Active**: Integration is enabled and operational
- **Inactive**: Integration is disabled (no events will be sent)
- **Error**: Integration encountered an error (check logs for details)

## Security Considerations

### API Credentials

- API keys and secrets are encrypted at rest using Fernet symmetric encryption
- Credentials are never returned in API responses
- When updating credentials, leave fields empty to keep existing values

### Webhook URLs

- Ensure webhook URLs use HTTPS in production
- Validate webhook endpoints support HTTP POST requests
- Consider implementing webhook signature verification for sensitive data

### Access Control

- Users can only manage integrations they created
- Organization members can view/manage integrations belonging to their organization
- Integration logs are only visible to authorized users

## Webhook Configuration Examples

### Discord Webhook

```json
{
  "name": "Discord Inventory Alerts",
  "type": "webhook",
  "webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN",
  "config_data": {
    "channel": "#inventory",
    "notify_on": ["low_stock", "craft_complete"]
  }
}
```

### Slack Webhook

```json
{
  "name": "Slack Notifications",
  "type": "webhook",
  "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
  "config_data": {
    "channel": "#scims-alerts",
    "username": "SCIMS Bot"
  }
}
```

## Receiving Webhooks

SCIMS can also receive incoming webhooks from external services:

**Endpoint:** `POST /api/v1/webhooks/receive/{integration_id}`

The webhook handler logs incoming requests to the integration logs for processing by integration-specific handlers.

## Troubleshooting

### Integration Test Fails

1. **Check webhook URL**: Verify the URL is correct and accessible
2. **Verify API credentials**: Ensure API key/secret are valid
3. **Review logs**: Check the integration logs for detailed error messages
4. **Network connectivity**: Ensure SCIMS can reach external services

### Webhooks Not Being Sent

1. **Check integration status**: Ensure status is "active"
2. **Verify webhook URL**: Test the URL manually with curl
3. **Review logs**: Check for error entries in the logs
4. **Configuration**: Verify config_data is valid JSON

### API Integration Errors

1. **Credentials**: Verify API key/secret are correct
2. **Base URL**: Check config_data for correct base_url
3. **Permissions**: Ensure API credentials have required permissions
4. **Rate limits**: Check if external API rate limits are being hit

## Best Practices

1. **Naming**: Use descriptive names for integrations (e.g., "Discord - Inventory Alerts")
2. **Testing**: Test integrations after creation and after configuration changes
3. **Monitoring**: Regularly review integration logs for errors
4. **Security**: Use HTTPS for all webhook URLs, rotate API credentials periodically
5. **Organization**: Group related integrations under organizations for better management
6. **Documentation**: Document integration purposes in the name or config_data

---

## Import/Export Guide

SCIMS supports importing and exporting data in CSV and JSON formats for backup, migration, and integration with external tools.

## Exporting Data

### Via Web Interface

1. Navigate to **Import/Export** in the main menu
2. In the **Export Data** section:
   - Select the data type (Items, Inventory, or Blueprints)
   - Choose format (CSV or JSON)
   - (Optional) Apply filters (e.g., category for items)
3. Click **Export**
4. The file will download automatically

### Via API

```bash
# Export items as CSV
curl -X GET "http://localhost:8000/api/v1/import-export/items.csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o items_export.csv

# Export items as JSON with category filter
curl -X GET "http://localhost:8000/api/v1/import-export/items.json?category=Materials" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o items_materials.json

# Export inventory as CSV
curl -X GET "http://localhost:8000/api/v1/import-export/inventory.csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o inventory_export.csv

# Export blueprints as JSON
curl -X GET "http://localhost:8000/api/v1/import-export/blueprints.json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o blueprints_export.json
```

## Importing Data

### Via Web Interface

1. Navigate to **Import/Export** in the main menu
2. In the **Import Data** section:
   - Select the data type (Items, Inventory, or Blueprints)
   - Choose the file (CSV or JSON)
3. Click **Import**
4. Review the import results:
   - Number of items successfully imported
   - Number of items that failed
   - Detailed error messages for failures

### Via API

```bash
# Import items from CSV
curl -X POST "http://localhost:8000/api/v1/import-export/items/import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@items.csv" \
  -F "update_existing=true"

# Import items from JSON
curl -X POST "http://localhost:8000/api/v1/import-export/items/import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@items.json" \
  -F "update_existing=true"
```

### Import Parameters

- **update_existing**: If `true`, items with matching IDs or names will be updated. If `false`, duplicates will cause errors or be skipped.

## File Formats

### Items CSV Format

```csv
id,name,description,category,subcategory,rarity,metadata
550e8400-e29b-41d4-a716-446655440000,Quantum Drive,Q5 Quantum Drive,Components,Quantum Drives,Q5,"{""volume"": 1.0}"
```

**Columns:**
- `id` (optional): UUID - If omitted, a new UUID will be generated
- `name` (required): Item name
- `description` (optional): Item description
- `category` (optional): Item category
- `subcategory` (optional): Item subcategory
- `rarity` (optional): Item rarity
- `metadata` (optional): JSON string with additional metadata

### Items JSON Format

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Quantum Drive",
    "description": "Q5 Quantum Drive",
    "category": "Components",
    "subcategory": "Quantum Drives",
    "rarity": "Q5",
    "metadata": {
      "volume": 1.0
    }
  }
]
```

### Inventory CSV Format

```csv
item_id,location_id,quantity,reserved_quantity
550e8400-e29b-41d4-a716-446655440000,660e8400-e29b-41d4-a716-446655440000,100.0,10.0
```

**Columns:**
- `item_id` (required): UUID of the item
- `location_id` (required): UUID of the location
- `quantity` (required): Total quantity (must be >= 0)
- `reserved_quantity` (required): Reserved quantity (must be >= 0 and <= quantity)

### Inventory JSON Format

```json
[
  {
    "item_id": "550e8400-e29b-41d4-a716-446655440000",
    "location_id": "660e8400-e29b-41d4-a716-446655440000",
    "quantity": 100.0,
    "reserved_quantity": 10.0
  }
]
```

### Blueprints CSV Format

```csv
id,name,description,category,crafting_time_minutes,output_item_id,output_quantity,is_public,blueprint_data
770e8400-e29b-41d4-a716-446655440000,Quantum Drive Craft,Description,Crafting,15,550e8400-e29b-41d4-a716-446655440000,1.0,false,"{""ingredients"": [{""item_id"": ""550e8400-e29b-41d4-a716-446655440000"", ""quantity"": 2.0, ""optional"": false}]}"
```

**Columns:**
- `id` (optional): UUID - If omitted, a new UUID will be generated
- `name` (required): Blueprint name
- `description` (optional): Blueprint description
- `category` (optional): Blueprint category
- `crafting_time_minutes` (required): Crafting time in minutes (must be >= 0)
- `output_item_id` (required): UUID of the output item
- `output_quantity` (required): Quantity produced (must be > 0)
- `is_public` (required): `true` or `false`
- `blueprint_data` (required): JSON string containing `ingredients` array

**Blueprint Data Format:**
```json
{
  "ingredients": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440000",
      "quantity": 2.0,
      "optional": false
    }
  ]
}
```

### Blueprints JSON Format

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "name": "Quantum Drive Craft",
    "description": "Description",
    "category": "Crafting",
    "crafting_time_minutes": 15,
    "output_item_id": "550e8400-e29b-41d4-a716-446655440000",
    "output_quantity": "1.0",
    "is_public": false,
    "blueprint_data": {
      "ingredients": [
        {
          "item_id": "550e8400-e29b-41d4-a716-446655440000",
          "quantity": 3.0,
          "optional": false
        }
      ]
    }
  }
]
```

## Import Validation

The import process validates all data before importing:

### Validation Rules

**Items:**
- `name` is required and must be <= 255 characters
- `id` must be a valid UUID if provided
- `metadata` must be valid JSON if provided

**Inventory:**
- `item_id` and `location_id` must be valid UUIDs
- `quantity` and `reserved_quantity` must be numbers >= 0
- `reserved_quantity` cannot exceed `quantity`
- Item and location must exist in the database

**Blueprints:**
- `name` is required and must be <= 255 characters
- `output_item_id` must be a valid UUID and exist
- `crafting_time_minutes` must be an integer >= 0
- `output_quantity` must be a number > 0
- `blueprint_data.ingredients` must be an array
- Each ingredient must have valid `item_id` (UUID, exists), `quantity` (number > 0), and `optional` (boolean)

### Error Reporting

Import errors are reported with:
- Row number where the error occurred
- Field name causing the error
- Detailed error message

Example error response:
```json
{
  "success": false,
  "imported_count": 5,
  "failed_count": 2,
  "errors": [
    {
      "row_number": 3,
      "field": "item_id",
      "message": "Invalid UUID format for item_id: invalid-uuid"
    },
    {
      "row_number": 7,
      "field": "quantity",
      "message": "quantity must be >= 0, got -5"
    }
  ]
}
```

## Best Practices

1. **Backup**: Always export your data before importing to ensure you have a backup
2. **Validation**: Review exported files to understand the format before creating imports
3. **Testing**: Test imports with a small subset of data first
4. **UUIDs**: Include UUIDs in exports to maintain referential integrity on re-import
5. **Updates**: Use `update_existing=true` when importing updated data
6. **Error Review**: Always review import errors and fix data issues before re-importing
7. **CSV Encoding**: Ensure CSV files are UTF-8 encoded to handle special characters
8. **JSON Formatting**: Use proper JSON formatting - validated JSON parsers can help

## Common Use Cases

### Data Migration

1. Export data from the source system
2. Transform data to match SCIMS format
3. Import into SCIMS with `update_existing=false` for initial import
4. Verify imported data
5. Import updates with `update_existing=true` as needed

### Backup and Restore

1. Export all data types regularly
2. Store exports securely
3. In case of data loss, import from backups
4. Use `update_existing=true` to restore

### Bulk Updates

1. Export current data
2. Edit in spreadsheet or text editor
3. Import with `update_existing=true` to update existing records

### Integration with External Tools

1. Export SCIMS data
2. Process with external tools (spreadsheets, scripts, etc.)
3. Import results back into SCIMS

