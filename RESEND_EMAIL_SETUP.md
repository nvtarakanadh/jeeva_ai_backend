# Professional Email Setup with Resend

## Why Resend?

Resend is a modern, reliable email service that:
- ✅ **Free tier**: 3,000 emails/month (perfect for startups)
- ✅ **99.9% deliverability**: Better than SMTP
- ✅ **Simple API**: Easy to set up
- ✅ **Fast**: Emails delivered in seconds
- ✅ **Automatic fallback**: Falls back to SMTP if Resend is not configured

## Quick Setup (Recommended)

### Step 1: Sign up for Resend (Free)

1. Go to https://resend.com
2. Sign up for a free account
3. Verify your email

### Step 2: Get your API Key

1. Go to https://resend.com/api-keys
2. Click "Create API Key"
3. Name it "Jeeva AI Production"
4. Copy the API key (starts with `re_`)

### Step 3: Add Domain (Optional but Recommended)

1. Go to https://resend.com/domains
2. Click "Add Domain"
3. Add your domain (e.g., `jeeva.ai`)
4. Add the DNS records provided by Resend to your domain
5. Wait for verification (usually takes a few minutes)

**Note**: You can use Resend's default domain for testing, but using your own domain improves deliverability.

### Step 4: Configure Railway

1. Go to your Railway project dashboard
2. Select your backend service
3. Go to "Variables" tab
4. Add these environment variables:

```bash
# Resend Configuration (Recommended)
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=noreply@yourdomain.com
# OR use Resend's default domain:
# RESEND_FROM_EMAIL=onboarding@resend.dev

# Frontend URL
FRONTEND_URL=https://jeevaai.vercel.app

# Optional: Keep SMTP as fallback
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Step 5: Deploy

The code will automatically:
1. Try Resend first (if `RESEND_API_KEY` is set)
2. Fall back to SMTP if Resend fails or is not configured
3. Log everything for debugging

## How It Works

The email service automatically:
- ✅ Tries Resend API first (fast, reliable)
- ✅ Falls back to SMTP if Resend is not configured
- ✅ Logs all attempts for debugging
- ✅ Never blocks the request (emails sent in background)

## Testing

1. Request a password reset from your app
2. Check your email inbox
3. Check Railway logs to see which service was used:
   - `✅ Email sent successfully via Resend` = Resend worked
   - `✅ Email sent successfully via SMTP` = SMTP fallback used

## Troubleshooting

### Emails not arriving?

1. **Check Railway logs** - Look for email sending messages
2. **Check spam folder** - Resend emails usually don't go to spam, but check anyway
3. **Verify API key** - Make sure `RESEND_API_KEY` is set correctly
4. **Check domain verification** - If using custom domain, make sure it's verified
5. **Check Resend dashboard** - Go to https://resend.com/emails to see email status

### Using Resend's default domain?

If you haven't added your own domain, you can use:
```
RESEND_FROM_EMAIL=onboarding@resend.dev
```

This works immediately but emails come from `resend.dev` domain.

## Cost

- **Free tier**: 3,000 emails/month
- **Paid plans**: Start at $20/month for 50,000 emails

For most applications, the free tier is more than enough!

## Benefits Over SMTP

| Feature | Resend | SMTP |
|---------|--------|------|
| Setup | 2 minutes | 10+ minutes |
| Deliverability | 99.9% | ~95% |
| Speed | < 1 second | 2-5 seconds |
| Spam rate | < 0.1% | 5-10% |
| Monitoring | Built-in dashboard | None |
| Free tier | 3,000/month | Limited |

## Support

- Resend Docs: https://resend.com/docs
- Resend Support: support@resend.com

