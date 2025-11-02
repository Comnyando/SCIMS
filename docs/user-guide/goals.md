# Goals Guide

This guide explains how to use the Goals system in SCIMS to track your inventory objectives.

## Overview

The Goals System allows you to:
- Set targets for acquiring specific quantities of items
- Track progress toward your goals automatically
- Monitor goal completion status
- Set deadlines for goal achievement
- Create personal or organization-wide goals

## What are Goals?

Goals help you track inventory objectives, such as:
- Stockpiling resources for upcoming crafting projects
- Building up supplies of rare materials
- Meeting quantity targets for organization operations
- Planning resource acquisition timelines

Each goal tracks:
- **Goal Items**: One or more target items with quantities you want to acquire
- **Target Date**: Optional deadline for completion
- **Progress**: Automatically calculated based on current inventory for all items
- **Status**: Active, Completed, or Cancelled

**Multi-Item Goals**: Goals can track multiple items simultaneously. The goal is completed when ALL items reach their target quantities.

## Creating a Goal

1. Navigate to the **Goals** page from the main navigation
2. Click the **"Create Goal"** button
3. Fill in the goal details:
   - **Goal Name**: A descriptive name for your goal (e.g., "Stockpile Resources for Crafting")
   - **Description**: Optional description explaining the goal's purpose
   - **Organization**: Optional - leave empty for personal goals, or enter organization UUID
   - **Goal Items**: Add one or more items to track:
     - Click **"Add Item"** to add multiple items
     - For each item, select the item from the dropdown
     - Set the target quantity (must be positive)
     - Remove items using the X button (must have at least one item)
   - **Target Date**: Optional deadline for when you want to complete this goal
4. Click **"Create Goal"** to save

The system will immediately calculate your current progress based on your accessible inventory.

## Viewing Goals

### Goal List Page

The Goals page shows all goals you have access to:
- Goals you created (personal goals)
- Goals for organizations you belong to (organization goals)

You can filter goals by:
- **Status**: Show only Active, Completed, or Cancelled goals
- **Sort**: Sort by creation date, target date, or name
- **Order**: Ascending or descending

Each goal displays:
- Goal name
- Current status (Active, Completed, Cancelled)
- Target items summary (single item name, or "N items (X total)" for multiple)
- Progress bar showing overall completion percentage
- Target date (if set)

### Goal Detail Page

Click on any goal name in the list to view its full details:
- Complete goal information
- Overall progress visualization (aggregated across all items)
- Individual item progress (for multi-item goals):
  - Progress bar for each item
  - Current vs target quantity for each item
  - Completion status per item
- Overall progress percentage
- Days remaining (if target date is set)
- Creation and update timestamps

From the detail page, you can:
- **Edit**: Modify active goals (only if you're the creator)
- **Delete**: Remove active or cancelled goals (only if you're the creator)

## Progress Tracking

### Automatic Progress Calculation

Progress is automatically calculated based on:
- **Multi-Item Goals**: Current stock of each target item across all your accessible locations (user-owned, organization-owned, ship cargo, etc.)
- Individual item progress is calculated separately
- Overall goal progress is aggregated from all items

The progress calculation:
- For each goal item, sums available quantities (quantity - reserved_quantity) across all accessible locations
- Calculates per-item progress percentage
- Aggregates overall goal progress from all items
- Updates when inventory changes
- Refreshes every 30 seconds for active goals
- Can be manually recalculated using the progress endpoint

### Progress Indicators

- **Overall Progress Bar**: Visual representation of aggregated completion percentage
- **Individual Item Progress**: Separate progress bars for each item in multi-item goals
- **Percentage**: Exact completion percentage (0-100%) for overall and per-item
- **Current vs Target**: Shows current quantity achieved vs target quantity for each item
- **Completion Status**: Per-item completion indicators (completed when item reaches target)
- **Days Remaining**: Countdown to target date (if set)

### Completion Detection

Goals are automatically marked as **Completed** when:
- **ALL** goal items have current quantity >= target quantity
- Status changes from Active to Completed automatically
- Completion timestamp is recorded
- Individual items may show as completed before the overall goal completes

## Editing Goals

1. Navigate to a goal you created
2. Click the **"Edit"** button (only available for active goals)
3. Modify any fields as needed:
   - Goal name and description
   - Goal items (add, remove, or modify items and quantities)
   - Target date (can update or remove)
   - Organization assignment
4. Click **"Update Goal"** to save changes

**Note**: Updating goal items will replace the entire list of items. Ensure you include all items you want to track.

**Note**: Progress is recalculated automatically when you update an active goal.

**Restrictions**:
- Completed goals cannot be edited
- Cancelled goals cannot be edited
- Only the goal creator can edit a goal

## Deleting Goals

1. Navigate to a goal you created
2. Click the **"Delete"** button (only available for active or cancelled goals)
3. Confirm deletion

**Note**: Completed goals cannot be deleted (to preserve historical records).

## Goal Statuses

### Active
- Goal is in progress
- Progress is tracked and updated automatically
- Can be edited or deleted by the creator
- Automatically transitions to Completed when target is met

### Completed
- Goal has been achieved (current quantity >= target quantity)
- No longer tracked automatically
- Cannot be edited or deleted
- Preserves completion history

### Cancelled
- Goal was manually cancelled
- No longer tracked
- Can be deleted by the creator
- Preserves cancellation record

## Personal vs Organization Goals

### Personal Goals
- Created without an organization assignment
- Only visible to the creator
- Useful for individual planning and tracking

### Organization Goals
- Created for a specific organization
- Visible to all members of that organization
- Useful for team planning and coordination
- Progress calculated based on organization's accessible inventory

## Best Practices

1. **Set Realistic Targets**: Use target dates that account for your play time and resource availability
2. **Monitor Progress**: Regularly check active goals to see how you're progressing
3. **Use Descriptions**: Add descriptions to goals to remember their purpose later
4. **Organization Planning**: Create organization goals for team objectives
5. **Review Completed Goals**: Use completed goals to track your achievements and plan future goals

## Examples

### Example 1: Single Resource Stockpiling
**Goal**: Stockpile 1000 units of Iron for upcoming weapon crafting
- **Name**: "Iron Stockpile for Weapon Crafting"
- **Goal Items**: 
  - Iron: 1000
- **Target Date**: End of month
- **Description**: "Building up iron reserves for upcoming weapon production run"

### Example 2: Multi-Item Crafting Preparation
**Goal**: Gather all ingredients for weapon crafting
- **Name**: "Weapon Crafting Materials"
- **Goal Items**:
  - Iron: 500
  - Carbon: 200
  - Silicon: 150
- **Target Date**: End of week
- **Description**: "Collect all materials needed for weapon blueprint"

### Example 3: Organization Supply Target
**Goal**: Ensure organization has medical and repair supplies
- **Name**: "Medical & Repair Supply Reserve"
- **Organization**: Your Organization
- **Goal Items**:
  - Medical Supplies: 500
  - Repair Kits: 300
- **Description**: "Maintain minimum supply reserves for operations"

## Troubleshooting

### Progress Not Updating
- Progress updates automatically every 30 seconds for active goals
- If progress seems incorrect, ensure you're checking the right locations
- Progress is calculated based on accessible inventory (locations you own or have access to)
- Organization goals only count inventory in organization-accessible locations

### Goal Not Completing
- Verify that your current quantity actually meets or exceeds the target
- Check that the goal status is Active
- Ensure the target item matches the item in your inventory
- Progress is calculated automatically - completion should happen within 30 seconds of reaching the target

### Can't Edit or Delete Goal
- Only the goal creator can edit or delete goals
- Completed goals cannot be edited or deleted
- Ensure you're logged in as the goal creator
- Check the goal status (only Active and Cancelled goals can be deleted)

