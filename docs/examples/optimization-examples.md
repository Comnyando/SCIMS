# Optimization Examples

This document provides practical examples of using the optimization features in real-world scenarios.

---

## Example 1: Finding Sources for Crafting Materials

**Scenario**: You need 100 units of Iron Ore for a craft, and want to find the cheapest reliable sources.

### Step 1: Find Sources

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/find-sources" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "550e8400-e29b-41d4-a716-446655440000",
    "required_quantity": 100.0,
    "max_sources": 10,
    "min_reliability": 0.7
  }'
```

### Response

The response will show:
1. Your own stock first (if available, cost = 0)
2. Player stocks (if any, with costs)
3. Universe locations sorted by reliability and cost

### Step 2: Choose a Source

Based on the response, you might find:
- **Warehouse Alpha** (own stock): 50 units available, cost = 0
- **Crusader Mining Outpost** (universe): 500 units available, 5.0 per unit, reliability = 0.85

**Decision**: Use 50 from warehouse (free) + 50 from Crusader (250 total cost) = 250 credits total

---

## Example 2: Planning a Multi-Item Craft

**Scenario**: You want to craft 50 Advanced Components and need to plan ingredient acquisition.

### Step 1: Get Craft Suggestions

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/suggest-crafts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_item_id": "advanced-component-uuid",
    "target_quantity": 50.0,
    "max_suggestions": 5
  }'
```

### Response Analysis

The response might show:
- **Blueprint A**: 10 per craft, needs 5 crafts, all ingredients available ✅
- **Blueprint B**: 5 per craft, needs 10 crafts, missing 2 ingredients ⚠️

**Decision**: Use Blueprint A if you have time, or acquire missing ingredients for Blueprint B

### Step 2: Check Resource Gaps

Create the craft, then check gaps:

```bash
curl -X GET "http://localhost:8000/api/v1/optimization/resource-gap/{craft_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will show exactly what you're missing and where to get it.

---

## Example 3: Organization Resource Planning

**Scenario**: Your organization needs 500 units of Quantum Fuel. You want to check all organization locations.

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/find-sources" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "quantum-fuel-uuid",
    "required_quantity": 500.0,
    "organization_id": "your-org-id",
    "max_sources": 20
  }'
```

### Analysis

The response aggregates stock from:
- Your personal locations
- Organization warehouses
- Organization ships' cargo holds

You can see total available across the organization and plan distribution accordingly.

---

## Example 4: Building a Resource Acquisition Plan

**Scenario**: You have 5 crafts planned and need to efficiently acquire all missing ingredients.

### Workflow

1. **Get all craft gaps**:

```python
import requests

crafts = ["craft-id-1", "craft-id-2", "craft-id-3", "craft-id-4", "craft-id-5"]
all_gaps = {}

for craft_id in crafts:
    response = requests.get(
        f"http://localhost:8000/api/v1/optimization/resource-gap/{craft_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    gaps = response.json()["gaps"]
    
    for gap in gaps:
        item_id = gap["item_id"]
        if item_id not in all_gaps:
            all_gaps[item_id] = 0
        if gap["gap_quantity"] > 0:
            all_gaps[item_id] += gap["gap_quantity"]
```

2. **Find sources for aggregated gaps**:

```python
acquisition_plan = {}

for item_id, total_needed in all_gaps.items():
    response = requests.post(
        "http://localhost:8000/api/v1/optimization/find-sources",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "item_id": item_id,
            "required_quantity": total_needed,
            "min_reliability": 0.7
        }
    )
    sources = response.json()["sources"]
    
    # Group by location for efficient travel
    by_location = {}
    for source in sources:
        loc_id = source.get("location_id")
        if loc_id:
            if loc_id not in by_location:
                by_location[loc_id] = []
            by_location[loc_id].append({
                "item_id": item_id,
                "source": source
            })
    
    acquisition_plan[item_id] = {
        "needed": total_needed,
        "sources": sources,
        "by_location": by_location
    }
```

3. **Generate travel plan**:

Now you can see which locations have multiple items, minimizing travel:
- **Location A**: Iron Ore, Copper Wire, Carbon Fiber
- **Location B**: Quantum Fuel only
- **Location C**: Titanium, Gold

Plan your route: Location A → Location B → Location C

---

## Example 5: Cost Optimization

**Scenario**: You need 200 units of Rare Metal. You want to minimize cost while ensuring reliability.

### Step 1: Find All Sources

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/find-sources" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "rare-metal-uuid",
    "required_quantity": 200.0,
    "max_sources": 50,
    "min_reliability": 0.6
  }'
```

### Step 2: Calculate Optimal Purchase

Analyze the response to find the combination with lowest total cost:

**Sources Found:**
- Own Stock: 30 units (free) ✅
- Player Stock A: 100 units @ 8.0/unit = 800 credits
- Player Stock B: 50 units @ 7.5/unit = 375 credits
- Trading Post: 200 units @ 9.0/unit = 1800 credits

**Optimal Plan:**
- Use 30 from own stock (free)
- Buy 100 from Player Stock A (800)
- Buy 50 from Player Stock B (375)
- Buy 20 from Trading Post (180)
- **Total Cost**: 1,355 credits

Alternative: Buy all 170 needed from Trading Post = 1,530 credits (more expensive)

---

## Example 6: Reliability-First Strategy

**Scenario**: You're preparing for an important craft and want only the most reliable sources.

### Request

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/find-sources" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "critical-component-uuid",
    "required_quantity": 50.0,
    "max_sources": 10,
    "min_reliability": 0.9
  }'
```

This filters to only highly reliable sources (0.9+), ensuring you don't waste time on unreliable locations.

---

## Example 7: Blueprint Comparison

**Scenario**: Multiple blueprints produce the same item. You want to choose the most efficient one.

### Get Suggestions

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/suggest-crafts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_item_id": "target-item-uuid",
    "target_quantity": 100.0,
    "max_suggestions": 10
  }'
```

### Compare Options

**Blueprint A:**
- Output: 10 per craft
- Crafts needed: 10
- Time: 60 min each = 600 minutes total
- All ingredients available ✅

**Blueprint B:**
- Output: 20 per craft
- Crafts needed: 5
- Time: 90 min each = 450 minutes total
- Missing 1 ingredient ⚠️

**Decision**: If you can acquire the missing ingredient quickly, Blueprint B is more time-efficient. Otherwise, use Blueprint A.

---

## Example 8: Real-Time Craft Readiness Check

**Scenario**: Before starting a craft, verify you have everything needed.

### Check Resource Gap

```bash
curl -X GET "http://localhost:8000/api/v1/optimization/resource-gap/{craft_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Interpret Response

```json
{
  "can_proceed": true,
  "total_gaps": 0,
  "gaps": [
    {
      "item_id": "xxx",
      "gap_quantity": -10.0,  // Negative = have extra
      "sources": []
    }
  ]
}
```

**can_proceed: true** means you're ready! All gaps are filled or have available sources.

If **can_proceed: false**, review the gaps and use the provided sources to fill them.

---

## Best Practices from Examples

1. **Always check own stock first** - It's free!
2. **Use organization_id** for org-wide planning
3. **Set min_reliability** based on importance (0.7+ for critical items)
4. **Group acquisitions by location** to minimize travel
5. **Verify can_proceed** before starting crafts
6. **Compare multiple blueprints** for the same output
7. **Calculate total costs** when choosing between sources
8. **Check resource gaps** immediately after creating crafts

---

## Integration Examples

### Python Script: Automated Resource Checker

```python
import requests
from typing import List, Dict

class ResourceOptimizer:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def find_sources(self, item_id: str, quantity: float, min_reliability: float = 0.5):
        """Find sources for an item."""
        response = requests.post(
            f"{self.base_url}/api/v1/optimization/find-sources",
            headers=self.headers,
            json={
                "item_id": item_id,
                "required_quantity": quantity,
                "min_reliability": min_reliability
            }
        )
        return response.json()
    
    def check_craft_readiness(self, craft_id: str) -> bool:
        """Check if a craft is ready to proceed."""
        response = requests.get(
            f"{self.base_url}/api/v1/optimization/resource-gap/{craft_id}",
            headers=self.headers
        )
        data = response.json()
        return data["can_proceed"]
    
    def get_acquisition_plan(self, craft_ids: List[str]) -> Dict:
        """Get acquisition plan for multiple crafts."""
        plan = {}
        for craft_id in craft_ids:
            response = requests.get(
                f"{self.base_url}/api/v1/optimization/resource-gap/{craft_id}",
                headers=self.headers
            )
            gaps = response.json()["gaps"]
            
            for gap in gaps:
                if gap["gap_quantity"] > 0:
                    item_id = gap["item_id"]
                    if item_id not in plan:
                        plan[item_id] = {"needed": 0, "sources": []}
                    plan[item_id]["needed"] += gap["gap_quantity"]
                    
                    # Get sources
                    sources = self.find_sources(item_id, gap["gap_quantity"])
                    plan[item_id]["sources"] = sources["sources"]
        
        return plan

# Usage
optimizer = ResourceOptimizer("http://localhost:8000", "your-token")
plan = optimizer.get_acquisition_plan(["craft-1", "craft-2", "craft-3"])
```

---

## UI Workflow Examples

### Workflow 1: Planning a Craft from Scratch

1. **Create a Blueprint** (if needed):
   - Go to Blueprints → Create Blueprint
   - Define ingredients and output

2. **Create a Craft**:
   - Go to Crafts → Create Craft
   - Select your blueprint
   - Choose output location

3. **Review Resource Gaps**:
   - The craft detail page automatically shows Resource Gap Analysis
   - Review each ingredient's availability
   - Note which items have gaps

4. **Find Sources for Missing Items**:
   - Click on source cards in the gap view
   - Or manually find sources using the API/UI
   - Purchase or acquire missing items

5. **Verify Readiness**:
   - Refresh the gap analysis
   - Confirm all gaps are filled or have sources
   - Status should show "Ready to proceed"

6. **Start the Craft**:
   - Click "Start Craft" when ready
   - Monitor progress on the craft detail page

### Workflow 2: Finding Sources for Multiple Items

1. **Identify Needed Items**:
   - Review your inventory needs
   - List items you need to acquire

2. **Use Source Finding**:
   - For each item, find sources using the API or UI
   - Note locations and costs

3. **Plan Acquisition Route**:
   - Group items by location
   - Plan efficient travel route
   - Consider total costs

4. **Acquire Items**:
   - Travel to locations
   - Purchase items
   - Update stock levels in SCIMS

5. **Verify**:
   - Check inventory levels
   - Confirm all items acquired

### Workflow 3: Comparing Craft Options

1. **Identify Target Item**:
   - Know what item you want to produce
   - Determine target quantity

2. **Get Craft Suggestions**:
   - Use suggest-crafts API or UI
   - Review multiple blueprint options

3. **Compare Options**:
   - **Blueprint A**: Fast, needs ingredient X
   - **Blueprint B**: Slower, all ingredients available
   - Consider: time, ingredient availability, efficiency

4. **Choose Best Option**:
   - If ingredients available: choose faster blueprint
   - If ingredients missing: evaluate acquisition cost vs. time saved

5. **Execute Plan**:
   - Acquire missing ingredients if needed
   - Create craft with chosen blueprint
   - Monitor progress

### Workflow 4: Organization Resource Planning

1. **Set Organization Context**:
   - Ensure you're viewing organization resources
   - Use organization_id parameter in queries

2. **Inventory Overview**:
   - Review organization inventory
   - Identify shortages

3. **Batch Source Finding**:
   - Find sources for multiple items
   - Group by location for efficiency

4. **Plan Distribution**:
   - Allocate resources to organization members
   - Coordinate acquisitions

5. **Track and Update**:
   - Update inventory as items are acquired
   - Maintain source reliability through verification

## Next Steps

- Review the [Optimization Guide](./optimization.md) for detailed algorithm explanations
- Check the [API Reference](../development/api-reference.md) for complete endpoint documentation
- Explore the [Crafting Guide](./crafting.md) to understand the crafting system
- Visit **Settings → Optimization** in the UI to configure your preferences

