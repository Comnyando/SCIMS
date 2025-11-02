# Optimization Guide

The Optimization Engine helps you efficiently find resources and plan crafts by analyzing available sources, costs, and reliability. This guide covers how to use the optimization features to maximize your resource acquisition efficiency.

---

## Overview

The optimization system provides three main capabilities:

1. **Source Finding**: Discover where to obtain specific items, prioritized by cost and reliability
2. **Craft Suggestions**: Get recommendations on which blueprints to craft to produce target items
3. **Resource Gap Analysis**: Identify missing ingredients for crafts and find sources to fill the gaps

---

## Source Finding

The source finding feature searches across your inventory, other players' stocks, and universe locations to find the best sources for obtaining items.

### How It Works

The algorithm prioritizes sources in this order:

1. **Own Stock** (Highest Priority)
   - Checks your user-owned locations
   - Checks organization locations you have access to
   - Cost: **Free** (you already own it)

2. **Player Stocks** (Medium Priority)
   - Checks other players' shared stock information
   - May have associated costs for trading
   - Reliability score indicates trustworthiness

3. **Universe Sources** (Lower Priority, but important for missing items)
   - Trading posts
   - Universe locations (mining outposts, stations, etc.)
   - Sorted by reliability score and cost

### Using Source Finding

#### API Endpoint

```
POST /api/v1/optimization/find-sources
```

#### Request Example

```json
{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "required_quantity": 50.0,
  "max_sources": 10,
  "include_player_stocks": true,
  "min_reliability": 0.5,
  "organization_id": "optional-org-id"
}
```

#### Response Example

```json
{
  "item_id": "550e8400-e29b-41d4-a716-446655440000",
  "item_name": "Iron Ore",
  "required_quantity": 50.0,
  "sources": [
    {
      "source_type": "stock",
      "location_id": "abc123...",
      "location_name": "Warehouse Alpha",
      "available_quantity": 100.0,
      "cost_per_unit": 0.0,
      "total_cost": 0.0,
      "reliability_score": null
    },
    {
      "source_type": "universe_location",
      "location_id": "def456...",
      "location_name": "Crusader Mining Outpost",
      "source_id": "ghi789...",
      "source_identifier": "Crusader_Mining_Outpost",
      "available_quantity": 500.0,
      "cost_per_unit": 5.0,
      "total_cost": 250.0,
      "reliability_score": 0.85
    }
  ],
  "total_available": 600.0,
  "has_sufficient": true
}
```

#### Key Parameters

- **item_id** (required): UUID of the item to find sources for
- **required_quantity** (required): How much you need (must be > 0)
- **max_sources** (optional, default: 10): Maximum number of source options to return
- **include_player_stocks** (optional, default: true): Whether to include other players' stocks
- **min_reliability** (optional): Minimum reliability score (0.0-1.0) for universe sources
- **organization_id** (optional): Limit search to specific organization's locations

#### Understanding Reliability Scores

Reliability scores range from 0.0 to 1.0 and indicate how trustworthy a source is:

- **0.8-1.0**: Highly reliable, recently verified
- **0.5-0.8**: Moderately reliable, somewhat recent
- **0.0-0.5**: Less reliable, may be outdated

Scores are calculated based on:
- Verification history (how many times verified, accuracy rate)
- Recency of verifications (more recent = higher weight)
- Staleness penalty (sources not verified in 30+ days get penalized)

---

## Craft Suggestions

The craft suggestion feature analyzes blueprints that produce a target item and recommends which ones to craft based on ingredient availability and efficiency.

### How It Works

1. Finds all blueprints that produce the target item
2. For each blueprint:
   - Checks ingredient availability in your stock
   - Calculates how many times to craft to reach target quantity
   - Estimates total output
3. Sorts suggestions by:
   - **Feasibility first**: Blueprints with all ingredients available are prioritized
   - **Crafting time**: Shorter crafting times preferred

### Using Craft Suggestions

#### API Endpoint

```
POST /api/v1/optimization/suggest-crafts
```

#### Request Example

```json
{
  "target_item_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_quantity": 100.0,
  "organization_id": "optional-org-id",
  "max_suggestions": 10
}
```

#### Response Example

```json
{
  "target_item_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_item_name": "Advanced Component",
  "target_quantity": 100.0,
  "suggestions": [
    {
      "blueprint_id": "660e8400-e29b-41d4-a716-446655440000",
      "blueprint_name": "Advanced Component Blueprint",
      "output_item_id": "550e8400-e29b-41d4-a716-446655440000",
      "output_item_name": "Advanced Component",
      "output_quantity": 10.0,
      "crafting_time_minutes": 60,
      "suggested_count": 10,
      "total_output": 100.0,
      "ingredients": [
        {
          "item_id": "xxx...",
          "quantity": 5.0,
          "available": 100.0
        },
        {
          "item_id": "yyy...",
          "quantity": 2.0,
          "available": 50.0
        }
      ],
      "all_ingredients_available": true
    }
  ]
}
```

#### Key Parameters

- **target_item_id** (required): UUID of the item you want to produce
- **target_quantity** (required): How much you want to produce (must be > 0)
- **organization_id** (optional): Check stock in specific organization
- **max_suggestions** (optional, default: 10): Maximum number of suggestions to return

#### Understanding Suggestions

- **suggested_count**: Number of times to craft this blueprint
- **total_output**: Total quantity produced if you craft suggested_count times
- **all_ingredients_available**: Whether you have all required ingredients in stock
- **ingredients**: List showing required vs. available quantities for each ingredient

---

## Resource Gap Analysis

Resource gap analysis identifies missing ingredients for a craft and finds sources to fill those gaps.

### How It Works

For each ingredient in a craft:

1. Calculates required quantity
2. Checks available quantity in your accessible locations
3. Calculates the gap (required - available)
4. If there's a gap, finds sources to fill it using the source finding algorithm

### Using Resource Gap Analysis

#### API Endpoint

```
GET /api/v1/optimization/resource-gap/{craft_id}
```

#### Response Example

```json
{
  "craft_id": "880e8400-e29b-41d4-a716-446655440000",
  "craft_status": "planned",
  "blueprint_name": "Advanced Component Blueprint",
  "gaps": [
    {
      "item_id": "xxx...",
      "item_name": "Iron Ore",
      "required_quantity": 100.0,
      "available_quantity": 30.0,
      "gap_quantity": 70.0,
      "sources": [
        {
          "source_type": "universe_location",
          "location_id": "def456...",
          "location_name": "Crusader Mining Outpost",
          "available_quantity": 500.0,
          "cost_per_unit": 5.0,
          "total_cost": 350.0,
          "reliability_score": 0.85
        }
      ]
    },
    {
      "item_id": "yyy...",
      "item_name": "Copper Wire",
      "required_quantity": 50.0,
      "available_quantity": 60.0,
      "gap_quantity": -10.0,
      "sources": []
    }
  ],
  "total_gaps": 1,
  "can_proceed": true
}
```

#### Understanding Gap Analysis

- **gap_quantity**: 
  - Positive = missing quantity (need to acquire)
  - Zero or negative = sufficient stock available
- **sources**: Available sources to fill the gap (empty if no gap)
- **total_gaps**: Number of ingredients with positive gaps
- **can_proceed**: Whether the craft can proceed (all gaps have available sources or are filled)

Gaps are sorted by severity (largest gaps first) to help prioritize acquisition.

---

## Optimization Algorithms

### Source Prioritization Algorithm

Sources are sorted by:

1. **Cost** (ascending): Own stock (0) always comes first
2. **Reliability** (descending): Higher reliability preferred for universe sources
3. **Availability**: Sources with sufficient quantity prioritized

### Reliability Scoring Algorithm

Reliability scores are calculated using:

1. **Base Accuracy Rate**: Percentage of accurate verifications
2. **Recency Weighting**: More recent verifications weighted more heavily
   - Weight = 1.0 / (1 + days_ago / 7)
   - Today's verification: weight = 1.0
   - 7 days ago: weight = 0.5
   - 14 days ago: weight = 0.33
3. **Staleness Penalty**: Sources not verified in 30+ days get penalized
   - 10% penalty per 30 days beyond 30 days
   - Maximum 50% penalty

**Example Calculation:**
- Source verified 5 days ago as accurate: 0.91 weight
- Source verified 20 days ago as accurate: 0.59 weight
- Source verified 60 days ago: 0.5 base - 0.1 staleness = 0.4 final

### Craft Suggestion Algorithm

1. Find all blueprints producing target item
2. For each blueprint:
   - Check each ingredient's availability
   - Calculate suggested_count = ceil(target_quantity / output_per_craft)
   - Mark as available if all ingredients >= required quantities
3. Sort by:
   - All ingredients available (boolean, true first)
   - Crafting time (ascending)

---

## Best Practices

### 1. Regular Source Verification

- Verify universe sources regularly to maintain high reliability scores
- Use the source verification endpoint (`POST /api/v1/sources/{source_id}/verify`) after checking sources in-game

### 2. Organization Context

- Specify `organization_id` when searching for organization-wide resources
- This limits searches to organization locations you have access to

### 3. Reliability Filtering

- Use `min_reliability` to filter out unreliable sources
- Recommended minimum: 0.5 for casual use, 0.7+ for critical crafts

### 4. Resource Gap Workflow

1. Create a craft for your blueprint
2. Check resource gaps immediately
3. Use source recommendations to plan acquisition
4. Verify sources before traveling
5. Update stock levels after acquisition
6. Re-check gaps before starting the craft

### 5. Batch Operations

- For multiple crafts, check resource gaps for all before starting
- Group items by source location to minimize travel time
- Prioritize high-reliability sources for critical ingredients

---

## Performance Considerations

The optimization algorithms are designed for performance:

- **Single queries**: < 1 second for 100+ items
- **Sequential queries**: Optimized for batch processing
- **Large datasets**: Handles 100+ items, 100+ sources efficiently
- **Database indexes**: Properly indexed for fast lookups

For best performance:
- Use `max_sources` and `max_suggestions` to limit results
- Filter by `min_reliability` to reduce computation
- Cache results for frequently queried items

---

## Examples

See [optimization-examples.md](../examples/optimization-examples.md) for detailed usage examples and common workflows.

---

## User Interface Guide

The optimization features are integrated into the SCIMS web interface to provide a seamless experience for finding resources and planning crafts.

### Accessing Optimization Features

#### Resource Gap Analysis
Resource gap analysis is automatically displayed on craft detail pages for crafts in the "planned" status. To view gaps:

1. Navigate to **Crafts** from the main menu
2. Open a craft in "planned" status
3. The **Resource Gap Analysis** section appears automatically at the top of the craft details
4. Review gaps and available sources for each ingredient
5. Click **Refresh** to update gap data

The gap analysis shows:
- **Status indicator**: Green if ready to proceed, yellow if gaps exist
- **Ingredient cards**: Each showing available vs. required quantities
- **Source recommendations**: Up to 3 best sources per ingredient with gaps
- **Progress bars**: Visual representation of availability

#### Finding Sources (UI Integration)
Source finding can be accessed from:

1. **Resource Gap Analysis**: Click on source cards in the gap view
2. **Item Detail Pages**: (When implemented) Find sources button on item pages
3. **Direct API calls**: Use the API endpoints programmatically

#### Craft Suggestions (UI Integration)
Craft suggestions can be accessed from:

1. **Item Detail Pages**: (When implemented) "Find Blueprints" button
2. **Blueprint Browser**: When searching for ways to produce an item
3. **Direct API calls**: Use the API endpoints programmatically

### Optimization Settings

Configure your optimization preferences:

1. Navigate to **Settings** → **Optimization** (or `/settings/optimization`)
2. Configure default preferences:
   - **Source Finding**: Max sources, reliability threshold, include player stocks
   - **Craft Suggestions**: Max suggestions to return
   - **Display**: Auto-refresh gaps, refresh interval
   - **Prioritization**: Cost vs. reliability preferences
3. Click **Save Settings** to store preferences
4. Settings are stored locally in your browser

### Visual Indicators

The UI uses color coding and icons to convey information:

#### Source Cards
- **Green tag (Own Stock)**: Free, from your inventory
- **Blue tag (Player Stock)**: From other players, may have cost
- **Gray tag (Universe Location)**: Universe sources, neutral
- **Orange tag (Trading Post)**: Trading posts, usually costs money
- **Reliability badge**: Shield icon with percentage (green/yellow/red based on score)

#### Resource Gaps
- **Green**: Sufficient stock available
- **Yellow**: Small gap (≤10 units)
- **Red**: Large gap (>10 units)
- **Progress bars**: Show available/required ratio visually

#### Craft Suggestions
- **Green checkmark**: All ingredients available
- **Yellow warning**: Some ingredients missing
- **Ingredient tags**: Color-coded by availability (green/yellow/red)

### Keyboard Shortcuts
(To be implemented in future releases)

## Troubleshooting

### No Sources Found

- Verify the item_id is correct
- Check if you have access to locations (organization membership)
- Ensure resource sources exist in the database
- Try lowering `min_reliability` or removing it

### Craft Suggestions Not Available

- Verify blueprints exist for the target item
- Check blueprint `output_item_id` matches target
- Ensure blueprints have ingredient data

### Resource Gap Shows No Sources

- The gap may be small enough to ignore
- Try using find-sources directly for the specific item
- Check if sources exist and have sufficient reliability

### Slow Performance

- Reduce `max_sources` or `max_suggestions`
- Filter by `min_reliability`
- Ensure database indexes are created
- Check database query performance

---

## Related Documentation

- [Inventory Guide](./inventory.md) - Managing stock levels
- [Crafting Guide](./crafting.md) - Creating and managing crafts
- [API Reference](../development/api-reference.md) - Complete API documentation

