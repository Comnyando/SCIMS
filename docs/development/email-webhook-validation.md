# Email Webhook Validation Guide

This guide documents how to validate email bounce/complaint webhook handling and suppression list behavior.

## Overview

Email providers (SendGrid, Mailgun, SES, Brevo) send webhooks for:
- **Bounces**: Failed email deliveries
- **Complaints**: Spam reports
- **Deliveries**: Successful sends
- **Opens/Clicks**: Engagement tracking

SCIMS should:
1. Receive webhook events
2. Update suppression lists
3. Prevent future emails to suppressed addresses

## Webhook Endpoints

### Current Implementation

Webhook endpoint structure:
```
POST /api/v1/webhooks/email/{provider}
```

Where `{provider}` is: `sendgrid`, `mailgun`, `ses`, `brevo`

### Expected Payload Formats

#### SendGrid

**Bounce Event:**
```json
[
  {
    "email": "bounced@example.com",
    "timestamp": 1234567890,
    "event": "bounce",
    "reason": "550 5.1.1 User unknown",
    "type": "bounce"
  }
]
```

**Complaint Event:**
```json
[
  {
    "email": "complaint@example.com",
    "timestamp": 1234567890,
    "event": "spamreport",
    "type": "spamreport"
  }
]
```

#### Mailgun

**Bounce Event:**
```json
{
  "event-data": {
    "event": "failed",
    "recipient": "bounced@example.com",
    "timestamp": 1234567890,
    "reason": "bounce"
  },
  "signature": {
    "token": "...",
    "timestamp": "1234567890",
    "signature": "..."
  }
}
```

#### Amazon SES

**Bounce Event (SNS):**
```json
{
  "Type": "Notification",
  "Message": "{\"notificationType\":\"Bounce\",\"bounce\":{\"bounceType\":\"Permanent\",\"bouncedRecipients\":[{\"emailAddress\":\"bounced@example.com\"}]}}"
}
```

## Suppression List Model

### Database Schema

```python
class EmailSuppression(Base, UUIDPrimaryKeyMixin):
    """Email suppression list for bounces and complaints."""
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    reason: Mapped[str] = mapped_column(String(50))  # 'bounce', 'complaint', 'unsubscribe'
    provider: Mapped[Optional[str]] = mapped_column(String(50))
    suppressed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
```

### Suppression List Behavior

1. **On Bounce/Complaint:**
   - Add email to suppression list
   - Mark reason (bounce/complaint)
   - Store provider and timestamp

2. **Before Sending Email:**
   - Check suppression list
   - Skip sending if email is suppressed
   - Log suppression reason

3. **Suppression Reasons:**
   - `bounce`: Hard bounce (permanent failure)
   - `complaint`: Spam complaint
   - `unsubscribe`: User unsubscribed
   - `manual`: Manually added

## Validation Tests

### Manual Testing

1. **Test Bounce Webhook:**

```bash
# Send bounce event to webhook
curl -X POST http://localhost:8000/api/v1/webhooks/email/sendgrid \
  -H "Content-Type: application/json" \
  -d '[
    {
      "email": "bounced@example.com",
      "timestamp": 1234567890,
      "event": "bounce",
      "reason": "550 5.1.1 User unknown",
      "type": "bounce"
    }
  ]'

# Verify email is in suppression list
curl http://localhost:8000/api/v1/admin/suppressions?email=bounced@example.com \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. **Test Complaint Webhook:**

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/email/sendgrid \
  -H "Content-Type: application/json" \
  -d '[
    {
      "email": "complaint@example.com",
      "timestamp": 1234567890,
      "event": "spamreport",
      "type": "spamreport"
    }
  ]'
```

3. **Test Email Sending with Suppression:**

```bash
# Try to send email to suppressed address
curl -X POST http://localhost:8000/api/v1/emails/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "bounced@example.com",
    "subject": "Test",
    "body": "Test email"
  }'

# Should return error or skip sending
```

### Automated Testing

Create integration tests:

```python
def test_bounce_webhook_adds_suppression(client, db_session):
    """Test that bounce webhook adds email to suppression list."""
    # Send bounce webhook
    response = client.post(
        "/api/v1/webhooks/email/sendgrid",
        json=[{
            "email": "bounced@example.com",
            "event": "bounce",
            "type": "bounce"
        }]
    )
    assert response.status_code == 200
    
    # Verify suppression
    suppression = db_session.query(EmailSuppression).filter(
        EmailSuppression.email == "bounced@example.com"
    ).first()
    assert suppression is not None
    assert suppression.reason == "bounce"

def test_suppressed_email_not_sent(client, db_session):
    """Test that emails to suppressed addresses are not sent."""
    # Add suppression
    suppression = EmailSuppression(
        email="suppressed@example.com",
        reason="bounce"
    )
    db_session.add(suppression)
    db_session.commit()
    
    # Try to send email
    response = client.post(
        "/api/v1/emails/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "to": "suppressed@example.com",
            "subject": "Test",
            "body": "Test"
        }
    )
    # Should skip sending or return error
    assert response.status_code in [400, 422]
```

## Webhook Security

### Signature Verification

Verify webhook signatures to prevent spoofing:

```python
import hmac
import hashlib

def verify_sendgrid_signature(payload, signature, secret):
    """Verify SendGrid webhook signature."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Rate Limiting

Webhook endpoints should have rate limiting:
- Per-IP limits
- Provider-specific limits
- Fail gracefully if rate limited

## Monitoring

### Metrics to Track

- Webhook events received
- Suppressions added
- Emails blocked by suppression
- Webhook failures

### Alerts

- High bounce rate (>5%)
- High complaint rate (>0.1%)
- Webhook endpoint failures
- Suppression list growth

## Troubleshooting

### Webhooks Not Received

1. **Check Webhook URL:**
   - Verify URL is accessible
   - Check HTTPS certificate
   - Test with webhook.site

2. **Check Provider Configuration:**
   - Verify webhook URL in provider dashboard
   - Check webhook is enabled
   - Review provider logs

3. **Check Application Logs:**
   ```bash
   docker compose logs backend | grep webhook
   ```

### Suppressions Not Working

1. **Check Database:**
   ```sql
   SELECT * FROM email_suppressions WHERE email = 'test@example.com';
   ```

2. **Check Email Sending Logic:**
   - Verify suppression check is called
   - Check logs for suppression hits

3. **Test Manually:**
   - Add suppression via API
   - Try sending email
   - Verify email is blocked

## Implementation Checklist

- [ ] Create EmailSuppression model
- [ ] Implement webhook endpoints for each provider
- [ ] Add signature verification
- [ ] Implement suppression check in email sending
- [ ] Add admin API for viewing suppressions
- [ ] Create integration tests
- [ ] Add monitoring and alerts
- [ ] Document webhook configuration

---

For more information:
- [Email Setup Guide](../user-guide/email-setup.md)
- [Performance Optimization](performance-optimization.md)

