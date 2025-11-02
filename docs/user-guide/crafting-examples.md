# Crafting Examples

This document provides practical examples of using the crafting system in SCIMS.

## Example 1: Simple Single Craft

**Scenario:** You want to craft a Quantum Drive Component using a blueprint you found.

**Steps:**
1. Browse to Blueprints page and find "Quantum Drive Component" blueprint
2. View the blueprint details to see it requires:
   - 10x Quantum Crystals
   - 5x Refined Metal
   - Crafting time: 120 minutes (2 hours)
3. Click "Create Craft" from the blueprint detail page (or go to Crafts → Create Craft)
4. Select the "Quantum Drive Component" blueprint
5. Choose your station warehouse as the output location
6. Set priority to 50 (medium priority)
7. Enable "Reserve Ingredients on Creation"
8. Click "Create Craft"
9. The craft is created with status "Planned" and ingredients are reserved
10. Navigate to the craft detail page and click "Start Craft"
11. The craft begins and will automatically complete in 2 hours
12. When complete, 1x Quantum Drive Component is added to your station warehouse

**Key Points:**
- Reserving ingredients ensures they're available when you start
- The craft runs automatically once started
- Output is delivered to your chosen location

## Example 2: Batch Crafting

**Scenario:** You need 5x Quantum Drive Components. You can create multiple crafts.

**Steps:**
1. Create the first craft as in Example 1
2. Repeat the creation process 4 more times with the same blueprint
3. All 5 crafts appear in your queue as "Planned"
4. Start them one by one (or wait if you want to stagger them)
5. Each craft runs independently with its own timer
6. After 2 hours per craft, you'll have 5x Quantum Drive Components total

**Tips:**
- Set different priorities if some are more urgent
- Consider staggering start times if you want them to complete at different times
- Monitor ingredient availability - batch crafting requires 5x the ingredients

## Example 3: Scheduled Crafting

**Scenario:** You want to start a long craft (4 hours) tomorrow morning, but set it up now.

**Steps:**
1. Create a craft as usual
2. In the "Scheduled Start" field, set tomorrow's date and 8:00 AM
3. Leave "Reserve Ingredients" enabled
4. Create the craft - it appears as "Planned"
5. Ingredients are reserved immediately
6. Tomorrow at 8 AM, navigate to the craft and start it manually
7. The craft begins and completes 4 hours later (noon)

**Notes:**
- Scheduled start is informational only - crafts don't auto-start
- Use it to plan your crafting workflow
- Ingredients are reserved when you create, not when scheduled

## Example 4: Managing Ingredient Sources

**Scenario:** Your ingredients are in different locations (station inventory and ship cargo).

**Steps:**
1. Create a craft as usual
2. The system defaults all ingredients to use the output location
3. Before starting, review ingredient sources on the craft detail page
4. If needed, you may need to transfer items to a single location
5. Start the craft when all ingredients are accessible

**Current Behavior:**
- Ingredients default to the output location
- All ingredients must be available when starting
- Future versions may support multi-location ingredient sourcing

## Example 5: Priority Management

**Scenario:** You have 3 crafts: one urgent, one normal, one low priority.

**Steps:**
1. Create Craft A (urgent): Priority 90
2. Create Craft B (normal): Priority 50
3. Create Craft C (low priority): Priority 10
4. In the Crafts queue, sort by Priority (descending)
5. Craft A appears first, then B, then C
6. Start them in priority order or all at once
7. High priority crafts get attention first

**Benefits:**
- Visual organization in the queue
- Helps manage multiple simultaneous crafts
- Priority doesn't affect completion time, just organization

## Example 6: Monitoring Progress

**Scenario:** You want to track a long-running craft (6 hours).

**Steps:**
1. Create and start a craft as usual
2. Navigate to the craft detail page
3. Watch the progress bar update automatically
4. Monitor:
   - Elapsed time (how long it's been running)
   - Estimated completion (time remaining)
   - Progress percentage
5. The page refreshes every 5 seconds automatically
6. You can navigate away and return - progress is always current

**Features:**
- Real-time progress updates
- Automatic refresh for in-progress crafts
- Detailed timing information

## Example 7: Early Completion

**Scenario:** Your craft has 30 minutes remaining, but you need the items now.

**Steps:**
1. Navigate to an in-progress craft
2. View the progress - it shows "~30 minutes remaining"
3. Click the "Complete Craft" button
4. Confirm the early completion
5. Ingredients are immediately consumed
6. Output items are added to the output location
7. Craft status changes to "Completed"

**Use Cases:**
- Need items before timer expires
- Want to free up ingredient reservations
- Manual testing or verification

## Example 8: Craft Cleanup

**Scenario:** You created several test crafts and want to clean them up.

**Steps:**
1. Go to Crafts page
2. Filter by status "Planned" to see unstarted crafts
3. For each craft you don't need:
   - Click to view detail page
   - Click "Delete"
   - Choose to unreserve ingredients
   - Confirm deletion
4. Optionally filter by "Completed" to review finished crafts
5. Completed crafts remain in history but don't clutter the active queue

**Best Practices:**
- Delete planned crafts you won't use
- Keep completed crafts for reference/history
- Unreserve ingredients when deleting to free up stock

## Example 9: Ingredient Reservation Workflow

**Scenario:** You want to secure ingredients for future crafts without starting them yet.

**Steps:**
1. Create Craft 1 with "Reserve Ingredients" enabled
   - Ingredients are immediately reserved
   - Craft status: Planned
   - Stock shows as reserved
2. Create Craft 2 without reserving
   - Ingredients are not reserved
   - You can start it later when ready
3. When starting Craft 2, it will reserve missing ingredients
4. If you delete Craft 1, choose to unreserve ingredients
   - Ingredients return to available stock
   - Can now be used for other crafts

**Reservation Strategy:**
- Reserve early if you're worried about stock availability
- Don't reserve if you're just planning - reserve when starting
- Unreserve when deleting to prevent stock lockup

## Example 10: Viewing Craft History

**Scenario:** You want to see what you've crafted recently.

**Steps:**
1. Go to Crafts page
2. Filter by status "Completed"
3. Sort by "Completed" date (descending)
4. View completed crafts with their completion times
5. Click any craft to see full details including:
   - What was produced
   - When it completed
   - Which blueprint was used
   - Ingredient consumption

**Benefits:**
- Track your crafting activity
- Review successful crafts
- Reference past crafting sessions

---

## Common Workflows

### Daily Crafting Routine
1. Review your craft queue in the morning
2. Start any planned crafts you want running
3. Check in-progress crafts for completion
4. Create new crafts from your blueprint library
5. Reserve ingredients for tomorrow's crafts

### Preparation Workflow
1. Browse blueprints for items you need
2. Create multiple planned crafts
3. Reserve ingredients for all of them
4. Review and prioritize
5. Start crafts as needed throughout the day

### Batch Production
1. Create multiple crafts from the same blueprint
2. Set appropriate priorities
3. Start them all at once (or stagger as desired)
4. Monitor progress across all crafts
5. Collect outputs as they complete

---

## Tips for Efficient Crafting

1. **Plan Ahead**: Create crafts during downtime, start them when needed
2. **Monitor Stock**: Ensure you have sufficient ingredients before creating crafts
3. **Use Priorities**: Organize your queue with priority levels
4. **Batch Similar Crafts**: Group similar crafts together for easier management
5. **Check Progress Regularly**: Especially for long-running crafts
6. **Clean Up Queue**: Remove completed or unwanted crafts to keep queue manageable
7. **Reserve Strategically**: Reserve ingredients when you're sure about the craft
8. **Learn from History**: Review completed crafts to understand timing and requirements

