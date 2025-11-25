# Email Provider Setup Guide

Complete guide for configuring email services with SCIMS, including SPF, DKIM, DMARC setup, webhook configuration, and environment variables.

## Table of Contents

- [Overview](#overview)
- [Email Service Providers](#email-service-providers)
- [SPF Configuration](#spf-configuration)
- [DKIM Configuration](#dkim-configuration)
- [DMARC Configuration](#dmarc-configuration)
- [Webhook Configuration](#webhook-configuration)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

SCIMS can send emails for various purposes (notifications, password resets, etc.). To ensure deliverability and security, proper email authentication is essential. This guide covers:

- **SPF (Sender Policy Framework)**: Authorizes which servers can send email for your domain
- **DKIM (DomainKeys Identified Mail)**: Cryptographically signs emails to verify authenticity
- **DMARC (Domain-based Message Authentication)**: Policy framework for email authentication

## Email Service Providers

### Recommended Providers

- **SendGrid**: Easy setup, good deliverability, free tier available
- **Mailgun**: Developer-friendly, good API, free tier available
- **Amazon SES**: Cost-effective, scalable, requires AWS account
- **Postmark**: Excellent deliverability, focused on transactional emails
- **SMTP Server**: Self-hosted or third-party SMTP

### Provider Selection

Consider:
- **Volume**: Expected email volume
- **Cost**: Free tier limits vs. paid plans
- **Deliverability**: Reputation and inbox placement rates
- **Features**: Webhooks, analytics, templates
- **Integration**: API vs. SMTP support

## SPF Configuration

### What is SPF?

SPF (Sender Policy Framework) tells receiving mail servers which servers are authorized to send email for your domain.

### Setting Up SPF

1. **Identify Sending Servers**

   For third-party providers, check their documentation:
   - **SendGrid**: `include:sendgrid.net`
   - **Mailgun**: `include:mailgun.org`
   - **Amazon SES**: `include:amazonses.com`
   - **SMTP**: Your server's IP address

2. **Create SPF Record**

   Add a TXT record to your DNS:

   ```
   Type: TXT
   Name: @ (or your domain)
   Value: v=spf1 include:sendgrid.net ~all
   ```

   **Common SPF Record Examples:**

   ```dns
   # SendGrid only
   v=spf1 include:sendgrid.net ~all

   # Mailgun only
   v=spf1 include:mailgun.org ~all

   # Amazon SES only
   v=spf1 include:amazonses.com ~all

   # Multiple providers
   v=spf1 include:sendgrid.net include:mailgun.org ~all

   # SMTP server with IP
   v=spf1 ip4:192.0.2.1 ~all

   # Combined (provider + SMTP)
   v=spf1 include:sendgrid.net ip4:192.0.2.1 ~all
   ```

3. **SPF Qualifiers**

   - `+all`: Allow all (not recommended)
   - `~all`: Soft fail (recommended for testing)
   - `-all`: Hard fail (recommended for production)
   - `?all`: Neutral

4. **Verify SPF Record**

   ```bash
   # Using dig
   dig TXT yourdomain.com

   # Using online tools
   # - mxtoolbox.com/spf
   # - dmarcian.com/spf-survey
   ```

## DKIM Configuration

### What is DKIM?

DKIM (DomainKeys Identified Mail) adds a cryptographic signature to emails, allowing receiving servers to verify the email came from your domain and wasn't tampered with.

### Setting Up DKIM

1. **Generate DKIM Keys** (if using SMTP)

   ```bash
   # Generate private key
   openssl genrsa -out dkim_private.pem 2048

   # Generate public key
   openssl rsa -in dkim_private.pem -pubout -out dkim_public.pem
   ```

2. **Provider-Specific Setup**

   **SendGrid:**
   - Go to Settings → Sender Authentication
   - Add domain and verify ownership
   - Copy DKIM records provided
   - Add CNAME records to DNS

   **Mailgun:**
   - Go to Sending → Domain Settings
   - Add domain and verify
   - Copy DKIM records (TXT records)
   - Add to DNS

   **Amazon SES:**
   - Go to Verified Identities → Create Identity
   - Add domain and verify
   - Copy DKIM records (CNAME records)
   - Add to DNS

3. **Add DKIM Records to DNS**

   **For CNAME records (SendGrid, SES):**
   ```
   Type: CNAME
   Name: s1._domainkey (or provider-specific)
   Value: s1.domainkey.sendgrid.net
   ```

   **For TXT records (Mailgun, SMTP):**
   ```
   Type: TXT
   Name: default._domainkey (or selector._domainkey)
   Value: v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
   ```

4. **Verify DKIM**

   ```bash
   # Check DNS records
   dig TXT default._domainkey.yourdomain.com

   # Use online tools
   # - dkimvalidator.com
   # - mxtoolbox.com/dkim
   ```

## DMARC Configuration

### What is DMARC?

DMARC (Domain-based Message Authentication, Reporting & Conformance) provides a policy framework for email authentication and reporting.

### Setting Up DMARC

1. **Create DMARC Policy**

   Start with a monitoring policy:

   ```
   Type: TXT
   Name: _dmarc
   Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
   ```

   **DMARC Policy Options:**

   - `p=none`: Monitor only (recommended for initial setup)
   - `p=quarantine`: Quarantine failures
   - `p=reject`: Reject failures (recommended for production)

2. **DMARC Record Components**

   ```
   v=DMARC1;                    # Version
   p=none;                      # Policy (none/quarantine/reject)
   rua=mailto:dmarc@yourdomain.com;  # Aggregate reports
   ruf=mailto:dmarc@yourdomain.com;  # Forensic reports
   pct=100;                     # Percentage of emails to apply policy
   sp=none;                     # Subdomain policy
   aspf=r;                      # SPF alignment (strict/relaxed)
   adkim=r;                     # DKIM alignment (strict/relaxed)
   ```

3. **Example DMARC Records**

   **Monitoring (Initial):**
   ```
   v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
   ```

   **Quarantine (Testing):**
   ```
   v=DMARC1; p=quarantine; pct=10; rua=mailto:dmarc@yourdomain.com
   ```

   **Reject (Production):**
   ```
   v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc@yourdomain.com
   ```

4. **Add DMARC Record to DNS**

   ```
   Type: TXT
   Name: _dmarc
   Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
   ```

5. **Verify DMARC**

   ```bash
   dig TXT _dmarc.yourdomain.com

   # Online tools
   # - dmarcian.com/dmarc-inspector
   # - mxtoolbox.com/dmarc
   ```

## Webhook Configuration

### Email Provider Webhooks

Many email providers support webhooks for:
- **Bounces**: Failed deliveries
- **Complaints**: Spam reports
- **Opens/Clicks**: Engagement tracking
- **Deliveries**: Successful sends

### Setting Up Webhooks

1. **Configure Webhook URL**

   In your email provider dashboard:
   - **SendGrid**: Settings → Mail Settings → Event Webhook
   - **Mailgun**: Webhooks → Add Webhook
   - **Amazon SES**: Use SNS for notifications

2. **SCIMS Webhook Endpoint**

   ```
   POST /api/v1/webhooks/email/{provider}
   ```

   Where `{provider}` is: `sendgrid`, `mailgun`, `ses`, etc.

3. **Webhook Payload Handling**

   SCIMS processes webhook events:
   - **Bounces**: Updates suppression list
   - **Complaints**: Adds to suppression list
   - **Deliveries**: Logs delivery status

4. **Security**

   - Verify webhook signatures
   - Use HTTPS for webhook URLs
   - Validate payload structure
   - Rate limit webhook endpoints

## Environment Variables

### SMTP Configuration

```env
# SMTP Settings
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=SCIMS
SMTP_USE_TLS=true
```

### Provider-Specific Configuration

**SendGrid:**
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
EMAIL_FROM=noreply@yourdomain.com
EMAIL_FROM_NAME=SCIMS
```

**Mailgun:**
```env
MAILGUN_API_KEY=key-xxxxxxxxxxxxx
MAILGUN_DOMAIN=mg.yourdomain.com
EMAIL_FROM=noreply@yourdomain.com
```

**Amazon SES:**
```env
AWS_ACCESS_KEY_ID=xxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxx
AWS_REGION=us-east-1
EMAIL_FROM=noreply@yourdomain.com
```

### Webhook Configuration

```env
# Webhook secret for verification
EMAIL_WEBHOOK_SECRET=your-webhook-secret

# Enable webhook processing
ENABLE_EMAIL_WEBHOOKS=true
```

## Testing

### Test Email Sending

```bash
# Using curl to test API
curl -X POST "http://localhost:8000/api/v1/test-email" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to": "test@example.com", "subject": "Test", "body": "Test email"}'
```

### Verify DNS Records

```bash
# SPF
dig TXT yourdomain.com | grep spf

# DKIM
dig TXT default._domainkey.yourdomain.com

# DMARC
dig TXT _dmarc.yourdomain.com
```

### Online Testing Tools

- **MXToolbox**: https://mxtoolbox.com/
- **DMARCIAN**: https://dmarcian.com/
- **DKIM Validator**: https://dkimvalidator.com/
- **Mail Tester**: https://www.mail-tester.com/

## Troubleshooting

### Emails Not Sending

1. **Check SMTP Configuration**
   - Verify host, port, credentials
   - Test connection: `telnet smtp.host.com 587`
   - Check firewall rules

2. **Check Logs**
   ```bash
   docker compose logs backend | grep -i email
   ```

3. **Verify Provider Status**
   - Check provider status page
   - Verify API keys are valid
   - Check account limits

### Emails Going to Spam

1. **Verify SPF Record**
   - Check DNS propagation
   - Verify record syntax
   - Test with mxtoolbox.com

2. **Verify DKIM**
   - Check DNS records exist
   - Verify signature in email headers
   - Test with dkimvalidator.com

3. **Check DMARC Policy**
   - Start with `p=none` for monitoring
   - Review DMARC reports
   - Gradually tighten policy

4. **Sender Reputation**
   - Warm up new domains/IPs gradually
   - Maintain low bounce rates
   - Avoid spam trigger words

### Webhook Not Receiving Events

1. **Verify Webhook URL**
   - Check URL is accessible
   - Verify HTTPS certificate
   - Test with webhook.site

2. **Check Authentication**
   - Verify webhook secret
   - Check signature validation
   - Review provider documentation

3. **Check Logs**
   ```bash
   docker compose logs backend | grep webhook
   ```

### DNS Propagation Issues

- DNS changes can take 24-48 hours to propagate
- Use `dig` to check current DNS values
- Clear DNS cache: `sudo systemd-resolve --flush-caches` (Linux)

## Best Practices

1. **Start with Monitoring**
   - Use `p=none` for DMARC initially
   - Monitor reports for 1-2 weeks
   - Gradually tighten policies

2. **Maintain Records**
   - Document all DNS records
   - Keep backup of configurations
   - Version control environment files

3. **Regular Testing**
   - Test email sending regularly
   - Monitor bounce rates
   - Review DMARC reports weekly

4. **Security**
   - Rotate API keys regularly
   - Use strong webhook secrets
   - Enable TLS for SMTP

---

For more information, see:
- [Deployment Guide](../deployment/README.md)
- [Backend README](../../backend/README.md)

