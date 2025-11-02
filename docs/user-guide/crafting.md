# Crafting and Blueprints Guide

This guide explains how to use the Crafting and Blueprints system in SCIMS.

## Overview

The Crafting System allows you to:
- Create and manage crafting blueprints that define how to produce items
- Share blueprints with the community (public blueprints)
- Keep private blueprints for personal use
- Browse popular blueprints created by other players
- Find blueprints that produce specific items

## Blueprints

### What are Blueprints?

Blueprints define the recipe for crafting items. Each blueprint specifies:
- **Output**: What item is produced and in what quantity
- **Ingredients**: What items are needed and in what quantities
- **Crafting Time**: How long it takes to craft (in minutes)
- **Metadata**: Name, description, and category for organization
- **Visibility**: Public (visible to all) or Private (only you)

### Creating a Blueprint

1. Navigate to the **Blueprints** page from the main navigation
2. Click the **"Create Blueprint"** button
3. Fill in the blueprint details:
   - **Name**: A descriptive name for your blueprint
   - **Description**: Optional description explaining the blueprint
   - **Category**: Organize blueprints (Weapons, Components, Food, Materials, etc.)
   - **Crafting Time**: Time required in minutes (0 for instant)
   - **Output Item**: Select the item this blueprint produces
   - **Output Quantity**: How many of the output item are produced
4. Add **Ingredients**:
   - Click **"Add Ingredient"** for each required material
   - Select the item needed
   - Specify the quantity required
   - Mark as optional if the ingredient isn't strictly required
5. Set **Visibility**:
   - **Public**: All users can see and use your blueprint
   - **Private**: Only you can see and use this blueprint
6. Click **"Create Blueprint"** to save

### Viewing Blueprints

#### Browse All Blueprints

The Blueprints page shows all blueprints you have access to:
- Your own blueprints (both public and private)
- Public blueprints created by other users

You can filter blueprints by:
- **Search**: Search by name or description
- **Category**: Filter by blueprint category
- **Visibility**: Show only public or private blueprints
- **Sort**: Sort by name, usage count, or creation date

#### View Blueprint Details

Click on any blueprint name in the list to view its full details:
- Complete ingredient list with quantities
- Output item and quantity
- Crafting time
- Visibility status
- Usage statistics

From the detail page, you can:
- **Edit**: Modify your own blueprints (if you're the creator)
- **Delete**: Remove your own blueprints (if you're the creator)

#### Find Blueprints by Output Item

Use the "Blueprints by Item" feature to find all blueprints that produce a specific item. This is useful when you want to see different ways to obtain an item.

#### Popular Blueprints

The popular blueprints section shows the most-used blueprints, sorted by usage count. This helps you discover:
- Community-favorite blueprints
- Efficient crafting methods
- Well-tested recipes

### Editing a Blueprint

1. Navigate to a blueprint you created
2. Click the **"Edit"** button
3. Modify any fields as needed
4. Click **"Update Blueprint"** to save changes

Note: Only the blueprint creator can edit or delete a blueprint.

### Blueprint Sharing

#### Public Blueprints

Public blueprints are visible to all authenticated users. This allows:
- Community sharing of crafting knowledge
- Collaboration on optimal recipes
- Discovery of new crafting methods

When creating or editing a blueprint, enable **"Make this blueprint public"** to share it.

#### Private Blueprints

Private blueprints are only visible to you. Use private blueprints for:
- Personal notes and experiments
- Organization-specific recipes
- Work-in-progress blueprints

### Best Practices

1. **Descriptive Names**: Use clear, descriptive names that indicate what the blueprint produces
2. **Categories**: Use categories consistently to help organization
3. **Accurate Quantities**: Ensure ingredient quantities match actual crafting requirements
4. **Community Sharing**: Share useful blueprints publicly to help other players
5. **Documentation**: Use descriptions to explain special requirements or tips

## Crafts Management

Crafts represent actual crafting instances where you use a blueprint to produce items. The crafting system allows you to manage the entire lifecycle of crafting operations from planning to completion.

### Creating a Craft

1. Navigate to the **Crafts** page from the main navigation
2. Click the **"Create Craft"** button
3. Select a blueprint to craft:
   - Choose from your available blueprints (both public and private)
   - The blueprint preview shows ingredients, output, and crafting time
4. Configure the craft:
   - **Output Location**: Where the crafted items will be placed when complete
   - **Priority**: Set priority (0-100) to help manage multiple crafts
   - **Scheduled Start** (optional): Schedule the craft to start at a specific time
   - **Reserve Ingredients**: Optionally reserve ingredients immediately upon creation
5. Click **"Create Craft"** to add it to your craft queue

**Tips:**
- Reserving ingredients on creation ensures the materials are available when you start the craft
- Higher priority crafts will appear first in your queue
- Scheduled crafts won't start automatically - you still need to start them manually

### Craft Queue

The Craft Queue page shows all your crafts with their current status:

**Status Types:**
- **Planned**: Craft is created but not yet started
- **In Progress**: Craft is currently being worked on (time is counting down)
- **Completed**: Craft has finished and output items have been added to inventory
- **Cancelled**: Craft was cancelled (ingredients may be unreserved)

**Filtering and Sorting:**
- Filter by status (planned, in_progress, completed, cancelled)
- Sort by: creation date, priority, start date, or scheduled date
- View progress percentage for in-progress crafts

### Starting a Craft

1. Navigate to a craft in **Planned** status
2. Click the **"Start Craft"** button
3. If ingredients aren't already reserved, you'll be prompted to reserve missing ingredients
4. The craft status changes to **In Progress** and the crafting timer begins

**Important Notes:**
- Starting a craft reserves any unreserved ingredients automatically
- The blueprint usage count increases when a craft starts
- Crafts will automatically complete when the crafting time elapses (via background automation)

### Tracking Progress

For in-progress crafts, you can monitor:

- **Progress Bar**: Visual indicator showing completion percentage
- **Elapsed Time**: How long the craft has been running
- **Estimated Completion**: Time remaining until the craft completes
- **Ingredient Status**: View which ingredients are pending, reserved, or fulfilled

The progress updates automatically every few seconds while viewing the craft detail page.

### Completing a Craft

Crafts can be completed in two ways:

**Automatic Completion:**
- When the crafting time elapses, the system automatically completes the craft
- Reserved ingredient stock is deducted
- Output items are added to the specified output location
- Craft status changes to **Completed**

**Manual Completion:**
- For in-progress crafts, you can click **"Complete Craft"** to finish early
- All reserved ingredients are consumed
- Output items are immediately added to the output location
- Useful when you want to complete a craft before the timer expires

### Craft Detail Page

View detailed information about any craft:

**Craft Information:**
- Blueprint details (name, ingredients, output)
- Status and priority
- Timeline (created, scheduled, started, completed dates)

**Progress Tracking:**
- Real-time progress bar for in-progress crafts
- Elapsed and remaining time
- Ingredient status summary

**Ingredient Details:**
- List of all required ingredients
- Status of each ingredient (pending, reserved, fulfilled)
- Source location for each ingredient
- Quantity required

**Actions:**
- **Start Craft**: Begin a planned craft
- **Complete Craft**: Manually finish an in-progress craft
- **Delete Craft**: Remove a planned craft (can unreserve ingredients)
- **View Blueprint**: Navigate to the blueprint used for this craft

### Managing Crafts

**Deleting a Craft:**
- Planned crafts can be deleted
- Choose to unreserve ingredients when deleting
- In-progress crafts cannot be deleted (complete them instead)

**Priority Management:**
- Set priority (0-100) when creating or editing crafts
- Higher priority crafts appear first in sorted lists
- Useful for managing multiple crafts based on importance

**Scheduled Crafts:**
- Set a scheduled start time when creating a craft
- Crafts won't auto-start at the scheduled time - you still need to start them manually
- Useful for planning ahead when you'll be available to manage crafts

### Ingredient Reservation

**Automatic Reservation:**
- Ingredients can be reserved when creating or starting a craft
- Reserved stock is set aside and not available for other uses
- Reservation ensures materials are available when needed

**Reservation Status:**
- **Pending**: Ingredient not yet reserved
- **Reserved**: Stock has been reserved for this craft
- **Fulfilled**: Ingredient has been consumed in the craft

**Managing Reservations:**
- If you delete a craft, you can choose to unreserve ingredients
- Unreserved ingredients return to available stock
- If a craft completes, reserved ingredients are automatically fulfilled

### Best Practices

1. **Reserve Ingredients Early**: Reserve ingredients when creating crafts to ensure availability
2. **Set Priorities**: Use priority to organize important crafts
3. **Monitor Progress**: Check in-progress crafts regularly to track completion
4. **Plan Ahead**: Use scheduled start times to plan your crafting workflow
5. **Manage Queue**: Delete or cancel crafts you no longer need to keep your queue organized

## Tips and Tricks

1. **Browse Popular Blueprints**: Check popular blueprints to find well-tested recipes
2. **Search by Category**: Use category filters to find blueprints for specific item types
3. **Check Multiple Blueprints**: An item may have multiple blueprint options - compare to find the most efficient
4. **Use Descriptions**: Read blueprint descriptions for helpful tips from creators
5. **Organize with Categories**: Create your own category system for personal organization

## Troubleshooting

**I can't see a blueprint I created:**
- Check that you're logged in with the account that created it
- Verify the blueprint wasn't deleted
- Check filters - you may have visibility filters applied

**I can't edit a blueprint:**
- Only the blueprint creator can edit blueprints
- Make sure you're logged in as the creator
- Check that the blueprint exists and wasn't deleted

**Blueprint creation fails:**
- Ensure all required fields are filled
- Verify that all ingredient items exist in the system
- Check that output quantities are positive numbers
- Make sure crafting time is 0 or positive

**Can't find a specific blueprint:**
- Try different search terms
- Check if it's a private blueprint (only visible to creator)
- Verify you're looking in the correct category

**Craft won't start:**
- Ensure all required ingredients are available
- Check that ingredient reservation succeeded
- Verify you have access to the output location

**Ingredients not reserving:**
- Check that sufficient stock exists at the source location
- Verify you have access to the source location
- Some ingredients may need to be sourced from different locations

**Craft not completing automatically:**
- Background automation runs every 60 seconds
- Very short crafts may complete within the polling interval
- Manual completion is always available for in-progress crafts

**Can't delete a craft:**
- Only planned or cancelled crafts can be deleted
- In-progress crafts must be completed first
- Ensure you're the owner of the craft
- Clear filters and browse all blueprints
- Check if the blueprint might be private (only visible to creator)

