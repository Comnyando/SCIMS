# Analytics & Privacy Guide

This guide explains SCIMS's analytics features and privacy management.

## Overview

SCIMS includes optional analytics features to help improve the system. All analytics data collection requires your explicit consent and respects your privacy.

## Analytics Features

The analytics system tracks:
- **Usage Statistics**: How features are used (blueprint usage, goal creation, inventory updates)
- **Recipe Statistics**: Popular blueprints and their usage patterns
- **Event Tracking**: Anonymous events to understand feature adoption

All data collection is:
- **Consent-Based**: Only collected if you explicitly enable analytics
- **Anonymous**: No personally identifiable information is collected
- **Privacy-Focused**: IP addresses are anonymized, user agents are truncated
- **Transparent**: You can see exactly what data is collected and revoke consent anytime

## Managing Analytics Consent

### Enabling Analytics

1. Navigate to **Analytics** → **Privacy Settings** (or visit `/analytics/consent`)
2. Review what data will be collected (see "What We Collect" below)
3. Toggle **"Enable Analytics"** to ON
4. Your consent preference is saved immediately

### Disabling Analytics

1. Navigate to **Analytics** → **Privacy Settings**
2. Toggle **"Enable Analytics"** to OFF
3. No new analytics events will be logged
4. Existing events remain in the system (aggregated, not personally identifiable)

**Note**: Revoking consent immediately stops new event logging. Your existing usage data may still be used in aggregated statistics, but it cannot be linked back to you.

## What We Collect

### Usage Events

The following events are logged (only if consent is enabled):

- **Blueprint Used**: When you create a craft from a blueprint
- **Goal Created**: When you create a new goal
- **Goal Updated**: When you modify an active goal
- **Item Stock Updated**: When you adjust inventory quantities
- **Blueprint Created**: When you create a new blueprint

### Data Collected Per Event

Each event includes:
- **Event Type**: What action was performed
- **Entity Type**: Type of resource (blueprint, goal, item)
- **Entity ID**: Identifier for the specific resource
- **Event Data**: Additional context (e.g., blueprint ID used in craft)
- **Timestamp**: When the event occurred
- **Anonymized IP**: IP address with last octet removed (IPv4) or last 64 bits removed (IPv6)
- **Truncated User Agent**: Browser/client information (limited to 500 characters)

### What We DON'T Collect

- Personal information (name, email, username)
- Location data (beyond anonymized IP)
- Payment or financial information
- Passwords or authentication tokens
- Content of your goals, blueprints, or inventory items (only usage metadata)

## Privacy & Security

### IP Address Anonymization

IP addresses are automatically anonymized before storage:
- **IPv4**: Last octet removed (e.g., `192.168.1.123` → `192.168.1.0`)
- **IPv6**: Last 64 bits removed (e.g., `2001:0db8:85a3:0000:0000:8a2e:0370:7334` → `2001:0db8:85a3`)

This prevents identification of specific devices or locations while still allowing basic geographic analysis.

### User Agent Truncation

User agent strings are truncated to 500 characters to limit fingerprinting while preserving basic browser/OS information for compatibility analysis.

### Data Retention

- **Usage Events**: Retained for up to 1 year, then automatically deleted
- **Aggregated Statistics**: Retained indefinitely (contains no personally identifiable information)
- **You can revoke consent at any time**: Stops new logging immediately

## Viewing Analytics

### Analytics Dashboard

If you have analytics enabled, you can view:

1. Navigate to **Analytics** from the main menu
2. View usage statistics for different time periods:
   - Last 7 days
   - Last 30 days
   - Last 90 days
   - Last year
3. See breakdowns by event type
4. View top blueprints by usage
5. View most-created goals

### Recipe Statistics

View detailed statistics for specific blueprints:

- Total uses
- Number of unique users
- Completion rates
- Cancellation rates
- Usage trends over time

Access recipe statistics from:
- Blueprint detail pages (if implemented)
- Analytics dashboard
- Direct API calls

## How We Use Analytics Data

Analytics data helps us:

1. **Improve Features**: Understand which features are most useful
2. **Prioritize Development**: Focus on features that users actually use
3. **Identify Issues**: Detect problems or underutilized features
4. **Understand Patterns**: Learn how the community uses SCIMS
5. **Guide Decisions**: Make data-driven decisions about future development

All analysis is done on aggregated, anonymized data. Individual user behavior is never analyzed or shared.

## Your Rights

You have the right to:

- **Enable or Disable Analytics**: Control data collection at any time
- **View Your Data**: See what analytics data exists (if any can be linked to you)
- **Revoke Consent**: Stop data collection immediately
- **Request Deletion**: Contact administrators to request deletion of existing data (though it's already anonymized)

## Best Practices

1. **Make an Informed Decision**: Read the privacy information before enabling analytics
2. **Review Periodically**: Check your analytics settings if privacy preferences change
3. **Share Feedback**: If you have concerns about data collection, contact the development team
4. **Understand Impact**: Disabling analytics means you won't contribute to improving the system, but your privacy is respected either way

## Technical Details

### Event Logging

Events are logged via:
- **Middleware**: Automatic logging for API requests
- **Route Handlers**: Explicit logging for specific actions with full context

Events are only logged if:
- You have `analytics_consent = true` in your user profile
- The API request was successful (2xx status)
- The event matches tracked action types

### Statistics Aggregation

Aggregated statistics are calculated:
- **Daily**: For recent data (last 24 hours)
- **Weekly**: For weekly trends
- **Monthly**: For monthly summaries

Aggregation tasks run automatically via Celery:
- Reduces database load
- Provides fast query performance
- Enables historical analysis

### Privacy Safeguards in Code

- Consent is checked before every event log
- IP addresses are anonymized in middleware before storage
- User agents are truncated to prevent fingerprinting
- No sensitive data is included in event payloads

## Troubleshooting

### Analytics Dashboard Shows "No Data"

- Ensure analytics consent is enabled in Privacy Settings
- Wait a few minutes for events to be logged and aggregated
- Check that you've performed actions that generate events (create goals, use blueprints, etc.)

### Consent Toggle Not Working

- Try refreshing the page
- Check your browser console for errors
- Ensure you're logged in
- Verify the API is accessible

### Want to Delete All Analytics Data

- Revoke consent to stop future logging
- Contact administrators about existing data deletion
- Note: Aggregated statistics cannot be fully deleted as they contain no personally identifiable information

## Questions?

If you have questions about analytics or privacy:
- Review this guide
- Check the [Architecture Documentation](../planning/architecture.md) for technical details
- Contact the development team via GitHub issues

---

**Remember**: Analytics is completely optional. SCIMS works perfectly fine without analytics enabled. The choice is yours!

