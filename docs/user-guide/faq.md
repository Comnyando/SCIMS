# Frequently Asked Questions (FAQ)

Common questions and answers about using SCIMS.

## General

### What is SCIMS?

SCIMS (Star Citizen Inventory Management System) is a web-based inventory management system designed for Star Citizen organizations. It helps players track resources, plan crafting operations, optimize resource acquisition, and integrate with external tools.

### Is SCIMS free to use?

Yes, SCIMS is open-source and free to use. You can self-host it or use a hosted instance if available.

### Do I need to be part of an organization to use SCIMS?

No, you can use SCIMS as an individual player. Organizations are optional but provide additional features like shared inventory and collaborative goal tracking.

## Account & Authentication

### How do I register an account?

Use the registration page or API endpoint `/api/v1/auth/register` with your email, optional username, and password (minimum 8 characters).

### I forgot my password. How do I reset it?

Password reset functionality is planned for a future release. For now, contact your system administrator if you need password reset.

### Can I change my email address?

Email change functionality is planned for a future release. Contact your system administrator if you need to update your email.

### Why do I need to provide consent for analytics?

Analytics are completely optional and require your explicit consent. If you consent, your usage data helps improve the system. If you don't consent, no analytics data is collected. You can change your consent at any time in your account settings.

## Inventory Management

### How do I add items to my inventory?

1. First, create the item definition (if it doesn't exist)
2. Create or select a location
3. Use the "Adjust Inventory" feature to add stock

### Can I track items across multiple locations?

Yes! SCIMS is designed for multi-location tracking. You can create locations for stations, ships, and other storage locations, then track inventory at each location separately.

### What happens when I transfer items between locations?

The transfer operation:
- Deducts items from the source location
- Adds items to the destination location
- Creates a history record for audit purposes
- Requires access to both locations

### How do I reserve stock for a craft?

When creating a craft, use the `reserve_ingredients=true` parameter. This will automatically reserve the required ingredients from your available stock.

### Can I unreserve stock?

Yes, you can unreserve stock manually using the unreserve endpoint, or it will be automatically unreserved when you delete a planned craft (if you use the `unreserve_ingredients=true` parameter).

## Crafting

### How do I create a blueprint?

1. Navigate to Blueprints
2. Click "Create Blueprint"
3. Define the output item and quantity
4. Add required ingredients with quantities
5. Set crafting time
6. Choose if it should be public or private

### Can I share my blueprints with others?

Yes! When creating or editing a blueprint, you can set it to "public" to share it with the community. Public blueprints appear in search results for other users.

### How do I start a craft?

1. Create a craft from a blueprint
2. Ensure you have the required ingredients (or reserve them during creation)
3. Click "Start Craft" or use the API endpoint
4. The craft will be marked as "in progress"

### How do I complete a craft?

Once a craft is in progress, you can complete it manually using the "Complete Craft" button or API endpoint. The system will:
- Deduct reserved ingredients from stock
- Add the output items to the specified location
- Mark the craft as completed

### Can crafts complete automatically?

Yes, if you set a completion time when creating the craft, it can be automatically completed by the Celery task system. This requires the Celery worker to be running.

## Goals

### How do I create a goal?

1. Navigate to Goals
2. Click "Create Goal"
3. Select one or more target items
4. Set target quantities
5. Optionally set a target date
6. Choose if it's personal or organizational

### How is goal progress calculated?

Progress is calculated based on:
- Available stock (quantity - reserved quantity)
- Stock at accessible locations
- Stock in your organization (if it's an org goal)

### Can I track multiple items in one goal?

Yes! Goals support multiple target items. The goal is considered complete when all items reach their target quantities.

## Optimization

### How does the optimization engine work?

The optimization engine:
1. Checks your current stock first
2. Checks other players' shared stocks (with permissions)
3. Checks universe sources (mining locations, shops, etc.)
4. Calculates costs and benefits
5. Prioritizes sources by reliability and cost

### How do I add resource sources?

Use the Sources API or UI to add resource sources. Include:
- Item that can be found
- Location or source type
- Cost (if applicable)
- Reliability information

### Can I verify source accuracy?

Yes! After using a source, you can verify it. Accurate verifications increase reliability, while inaccurate ones decrease it.

## Integrations

### What integrations are supported?

SCIMS supports webhook-based integrations. You can:
- Receive webhooks for inventory changes
- Receive webhooks for craft completions
- Send data to external systems
- Import/export data via CSV or JSON

### How do I set up a webhook?

1. Create an integration in the Integrations section
2. Provide your webhook URL
3. Configure which events to receive
4. Test the integration

### Can I import my existing inventory data?

Yes! Use the Import/Export feature to import items and inventory from CSV or JSON files. See the [Integrations Guide](integrations.md) for format details.

## Public Commons

### What is the Public Commons?

The Public Commons is a community-curated database of items, recipes, and locations that all users can access. It's moderated to ensure accuracy and quality.

### How do I submit content to the Commons?

1. Navigate to the Public Commons section
2. Click "Submit" for the type of content (item, recipe, location)
3. Fill in the required information
4. Submit for moderation

### How long does moderation take?

Moderation time varies, but typically submissions are reviewed within a few days. You'll be notified when your submission is approved, rejected, or if changes are requested.

### Can I update my submission?

Yes, you can update pending submissions. Once approved and published, updates require a new submission.

## Troubleshooting

### I can't log in. What should I do?

- Verify your email and password are correct
- Check that your account is active
- Ensure you're using the correct API endpoint
- Check browser console for errors (if using web UI)

### My inventory adjustments aren't showing up. Why?

- Verify you have access to the location
- Check that the item exists
- Ensure you're looking at the correct location
- Check the inventory history for the transaction

### Crafts aren't completing automatically. Why?

- Ensure Celery worker is running
- Check that the craft has a completion time set
- Verify the craft status is "in progress"
- Check Celery logs for errors

### I'm getting rate limit errors. What should I do?

Rate limits are:
- Default: 60 requests per minute
- Public endpoints: 120 requests per minute
- Submission endpoints: 10 requests per minute

If you're hitting limits, reduce request frequency or contact your administrator about increasing limits.

### How do I report a bug?

Report bugs through:
- GitHub Issues (if self-hosting)
- Your system administrator (if using hosted instance)
- Include: steps to reproduce, expected behavior, actual behavior, and any error messages

## Privacy & Security

### Is my data secure?

Yes, SCIMS uses:
- JWT tokens for authentication
- Password hashing (Argon2)
- HTTPS in production
- Database encryption for sensitive fields (API keys)

### What data is collected if I consent to analytics?

If you consent, we collect:
- Feature usage (which features you use)
- Blueprint usage statistics
- Goal creation and completion
- No personally identifiable information beyond what you provide

### Can I delete my account?

Account deletion is planned for a future release. Contact your system administrator if you need to delete your account.

### Who can see my inventory?

- You can see your own inventory
- Organization members can see organization inventory (based on role)
- Other users cannot see your personal inventory unless you explicitly share it

---

**Still have questions?** Check the relevant user guide or contact your system administrator.

