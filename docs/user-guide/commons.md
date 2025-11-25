# Public Commons Guide

## Overview

The SCIMS Public Commons is a curated repository where users can submit items, blueprints, locations, and other game data for public sharing. All submissions go through a moderation workflow to ensure data quality before being published.

## Key Concepts

### Submissions

Submissions are proposed additions or updates to the public commons. Users create submissions with:
- **Entity Type**: What kind of data (item, blueprint, location, ingredient, taxonomy)
- **Entity Payload**: The actual data (JSON format)
- **Source Reference**: Optional URL or notes about where the data came from

### Moderation Workflow

All submissions go through a moderation process:
1. **Pending**: Initial status when submitted
2. **Needs Changes**: Moderator requested modifications
3. **Approved**: Accepted and published to the commons
4. **Rejected**: Not suitable for publication
5. **Merged**: Combined with an existing entity

### Public Entities

Once approved, submissions become public entities that are:
- Visible to everyone (no authentication required)
- Versioned and immutable
- Cached for performance
- Searchable and taggable

## Submitting Content

### Creating a Submission

You can submit content to the commons via the API:

```bash
curl -X POST "http://localhost:8000/api/v1/commons/submit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "item",
    "entity_payload": {
      "name": "Quantum Drive Q5",
      "description": "Advanced quantum drive for long-range travel",
      "category": "Components",
      "rarity": "Q5"
    },
    "source_reference": "https://starcitizen.fandom.com/wiki/Quantum_Drive"
  }'
```

### Submission Guidelines

When submitting content:
- **Accuracy**: Ensure data is correct and verified
- **Completeness**: Include all relevant fields
- **Source Reference**: Provide URLs or references when available
- **Format**: Follow the standard entity payload format
- **No Duplicates**: Check existing commons before submitting

### Updating Submissions

If a moderator requests changes, you can update your pending submission:

```bash
curl -X PATCH "http://localhost:8000/api/v1/commons/submissions/{submission_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_payload": {
      "name": "Quantum Drive Q5",
      "description": "Updated description with more details",
      "category": "Components",
      "rarity": "Q5"
    }
  }'
```

**Note**: Only pending submissions can be updated. Once approved or rejected, submissions cannot be modified.

### Viewing Your Submissions

Check the status of your submissions:

```bash
curl -X GET "http://localhost:8000/api/v1/commons/my-submissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You can filter by status or entity type using query parameters:
- `status`: Filter by submission status (pending, approved, rejected, etc.)
- `entity_type`: Filter by entity type (item, blueprint, location, etc.)

## Accessing Public Content

### Public API Endpoints

All public endpoints require **no authentication**:

#### List Public Items
```bash
GET /public/items?skip=0&limit=50&tag=weapons&search=quantum
```

#### List Public Recipes (Blueprints)
```bash
GET /public/recipes?skip=0&limit=50
```

#### List Public Locations
```bash
GET /public/locations?search=Stanton
```

#### Get Specific Entity
```bash
GET /public/items/{entity_id}
GET /public/recipes/{entity_id}
GET /public/locations/{entity_id}
```

#### Search All Entities
```bash
GET /public/search?q=quantum&entity_type=item
```

#### List Tags
```bash
GET /public/tags
```

### Query Parameters

- **skip**: Number of records to skip (pagination)
- **limit**: Maximum number of records (1-100, default 50)
- **search**: Search term (searches name and description)
- **tag**: Filter by tag name
- **entity_type**: Filter by entity type (for search endpoint)

### Response Format

Public endpoints return paginated results:

```json
{
  "entities": [
    {
      "id": "uuid",
      "entity_type": "item",
      "canonical_id": null,
      "data": {
        "name": "Quantum Drive Q5",
        "description": "...",
        "category": "Components"
      },
      "version": 1,
      "is_public": true,
      "created_by": "user_uuid",
      "created_at": "2025-01-01T00:00:00Z",
      "tags": ["weapons", "components"]
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 50,
  "pages": 2
}
```

## Caching

Public endpoints are cached in Redis for 1 hour to improve performance. When moderators approve new submissions, the cache is automatically invalidated to ensure fresh data.

## Rate Limiting

The public API has rate limits to prevent abuse:
- **Public endpoints**: 120 requests per minute per IP
- **Submission endpoints**: 10 requests per minute per user
- **Default endpoints**: 60 requests per minute per user/IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

If you exceed the limit, you'll receive a `429 Too Many Requests` response with a `Retry-After` header.

## Moderation (For Moderators)

### Viewing Submissions Queue

Moderators can view all submissions:

```bash
GET /api/v1/admin/commons/submissions?status=pending
```

### Moderation Actions

#### Approve
Approve a submission and publish it to the commons:

```bash
POST /api/v1/admin/commons/submissions/{id}/approve
{
  "notes": "Looks good, approved for publication"
}
```

This creates a public entity and logs the moderation action.

#### Reject
Reject a submission:

```bash
POST /api/v1/admin/commons/submissions/{id}/reject
{
  "notes": "Does not meet quality standards"
}
```

#### Request Changes
Request the submitter to make changes:

```bash
POST /api/v1/admin/commons/submissions/{id}/request-changes
{
  "notes": "Please add a description and source reference"
}
```

The submission status changes to "needs_changes", allowing the submitter to update it.

#### Merge
Merge a submission into an existing entity:

```bash
POST /api/v1/admin/commons/submissions/{id}/merge
{
  "action_payload": {
    "target_entity_id": "existing_entity_uuid"
  },
  "notes": "Duplicate, merged with existing entity"
}
```

## Data Model

### Commons Submission

```json
{
  "id": "uuid",
  "submitter_id": "user_uuid",
  "entity_type": "item|blueprint|location|ingredient|taxonomy",
  "entity_payload": {},
  "source_reference": "url or notes",
  "status": "pending|approved|rejected|needs_changes|merged",
  "review_notes": "moderator notes",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Commons Entity (Published)

```json
{
  "id": "uuid",
  "entity_type": "item|blueprint|location|ingredient|taxonomy",
  "canonical_id": "uuid|null",
  "data": {},
  "version": 1,
  "is_public": true,
  "created_by": "user_uuid",
  "created_at": "timestamp",
  "superseded_by": "uuid|null",
  "tags": ["tag1", "tag2"]
}
```

### Entity Types

- **item**: Game items (weapons, components, materials, etc.)
- **blueprint**: Crafting recipes
- **location**: Game locations (stations, planets, etc.)
- **ingredient**: Ingredient definitions
- **taxonomy**: Classification/taxonomy data

## Tags

Tags are used to categorize and filter commons entities. All tags are publicly visible and can be used in search and filtering operations.

## Best Practices

### For Submitters

1. **Verify Data**: Double-check all information before submitting
2. **Complete Fields**: Fill in all relevant fields for better quality
3. **Source References**: Always include source references when available
4. **Check Existing**: Search the commons before submitting to avoid duplicates
5. **Respond Promptly**: Address moderator feedback quickly

### For Moderators

1. **Be Consistent**: Apply the same standards to all submissions
2. **Clear Feedback**: Provide specific, actionable feedback
3. **Check Quality**: Verify data accuracy before approving
4. **Merge Duplicates**: Merge duplicates rather than rejecting
5. **Document Decisions**: Leave clear notes explaining your actions

## Takedown Procedures

### Requesting a Takedown

If you believe content in the Public Commons violates copyright, contains incorrect information, or should be removed for other reasons:

1. **Contact Administrators**: Reach out to system administrators with:
   - Entity ID or URL
   - Reason for takedown request
   - Your relationship to the content (original creator, copyright holder, etc.)

2. **Moderator Review**: Administrators will review the request and may:
   - Unpublish the entity (set `is_public` to `false`)
   - Delete the entity (if it violates terms)
   - Request more information

### Unpublishing Entities (Moderators)

Moderators can unpublish entities without deleting them:

```bash
# Unpublish an entity (via admin interface or direct database update)
# This removes it from public access but preserves the data
```

**When to Unpublish:**
- Copyright violations
- Incorrect or outdated information
- User requests (with verification)
- Policy violations

**When to Delete:**
- Spam or malicious content
- Repeated violations
- Legal requirements

### Entity Versioning

When an entity needs correction:
- **Option 1**: Unpublish the old version and approve a new submission
- **Option 2**: Create a new version that supersedes the old one
- **Option 3**: Merge corrections into the existing entity (for minor updates)

Entities maintain version history, so previous versions remain accessible for reference.

## Troubleshooting

### Submission Not Appearing

- Check submission status via `/api/v1/commons/my-submissions`
- If status is "needs_changes", update the submission
- If rejected, review moderator notes for reasons

### Public Entity Not Visible

- Verify the entity's `is_public` field is `true`
- Check cache - wait a few minutes for cache to update
- Verify entity_type matches the endpoint (e.g., items vs blueprints)

### Rate Limit Errors

- Wait for the rate limit window to reset (check `X-RateLimit-Reset` header)
- Reduce request frequency
- Use caching in your application

### Cache Issues

- Cache is automatically invalidated when new entities are published
- If you need to force a refresh, wait up to 1 hour for natural expiry
- Contact an administrator if persistent cache issues occur

## Frontend User Interface

### My Submissions

Access your submissions via **My Submissions** in the navigation menu. This page allows you to:
- View all your submissions and their status
- Filter submissions by status
- Edit pending or "needs changes" submissions
- Create new submissions

### Creating a Submission

1. Navigate to **My Submissions** and click **New Submission**
2. Select the entity type (Item, Blueprint, Location, etc.)
3. Enter the entity data as JSON in the payload field
4. (Optional) Add a source reference (URL or notes)
5. Click **Submit**

**Example Payload for an Item:**
```json
{
  "name": "Quantum Drive Q5",
  "description": "Advanced quantum drive for long-range travel",
  "category": "Components",
  "rarity": "Q5",
  "mass": 2500,
  "power_draw": 3500
}
```

### Editing a Submission

If a moderator requests changes, you'll see your submission with status "Needs Changes". You can:
1. Click **Edit** on the submission
2. Update the entity payload or source reference
3. Click **Update Submission**

Only pending or "needs changes" submissions can be edited.

### Public Commons

Browse the public commons via **Public Commons** in the navigation menu. You can:
- View all public items, recipes (blueprints), and locations
- Search by name or description
- Filter by tags
- View detailed information about any public entity

### Moderation (For Moderators)

Moderators have access to additional pages:

#### Moderation Dashboard

Access via **Moderation** in the navigation menu. This dashboard shows:
- All submissions in the queue
- Filter by status (pending, needs changes, etc.)
- Filter by entity type
- Quick access to review each submission

#### Submission Review

Click on any submission to review:
- Full entity payload (formatted JSON)
- Submission metadata (who submitted, when, source reference)
- Review notes from previous actions
- Moderation actions: Approve, Reject, Request Changes, Merge

**Moderation Actions:**
- **Approve**: Publishes the entity to the public commons
- **Reject**: Rejects the submission with optional notes
- **Request Changes**: Sends feedback to the submitter
- **Merge**: Merges into an existing entity (requires target entity ID)

#### Tag Manager

Access via **Tag Manager** in the navigation menu. This allows moderators to:
- View all tags in the system
- Create new tags with name and description
- Edit existing tags
- Delete unused tags (only if not in use by entities)

**Tag Guidelines:**
- Use lowercase, descriptive names (e.g., "weapons", "components")
- Keep tag names consistent
- Add descriptions for clarity
- Don't delete tags that are in use

#### Duplicate Finder

Access via **Duplicate Finder** (coming soon). This will help identify and merge duplicate entities in the commons.

## API Reference

For complete API documentation, see:
- Submission API: `/docs#tag/commons`
- Admin API: `/docs#tag/admin`
- Public API: `/docs#tag/public`

## Frontend-Specific Tips

1. **JSON Formatting**: Use the formatted JSON display in the submission detail pages to easily review entity data
2. **Tag Filters**: Use tag filters in the Public Commons to quickly find related entities
3. **Search**: The search function searches both names and descriptions across all public entities
4. **Status Tracking**: Monitor your submissions via the My Submissions page to see moderator feedback
5. **Quick Actions**: Use moderation action buttons on the submission detail page for efficient review workflow

