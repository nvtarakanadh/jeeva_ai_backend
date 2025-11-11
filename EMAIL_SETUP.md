ok then first remove all the .env important # Email Setup Guide

## Development Mode (Default)

**By default, emails are NOT sent in development mode.** They are printed to the Django console instead.

### To see password reset links in development:
1. Request password reset from frontend
2. Check your Django server console (terminal where you run `python manage.py runserver`)
3. Look for the reset link printed there
4. Copy and use that link

## To Enable Real Email Sending (Development)

If you want to receive actual emails during development, you need to configure SMTP.

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Jeeva AI Development"
   - Copy the 16-character password

3. **Update your `.env` file**:
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

4. **Restart your Django server**

### Option 2: Other SMTP Providers

#### Outlook/Hotmail:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

#### SendGrid (Free tier available):
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

#### Mailtrap (For testing - emails go to Mailtrap inbox):
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailtrap-username
EMAIL_HOST_PASSWORD=your-mailtrap-password
```

## Production Setup

For production, use environment variables on your hosting platform:

### Render:
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Add environment variables:
   - `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
   - `EMAIL_HOST=smtp.gmail.com`
   - `EMAIL_PORT=587`
   - `EMAIL_USE_TLS=True`
   - `EMAIL_HOST_USER=your-email@gmail.com`
   - `EMAIL_HOST_PASSWORD=your-app-password`
   - `DEFAULT_FROM_EMAIL=your-email@gmail.com`

### Railway:
1. Go to your project dashboard
2. Navigate to "Variables" tab
3. Add the same environment variables as above

## Quick Test

After setting up email, test it by:
1. Requesting a password reset
2. Check your email inbox (or Mailtrap inbox if using Mailtrap)
3. You should receive the password reset email

## Troubleshooting

### Gmail "Less secure app access" error:
- Use App Password instead of regular password
- Make sure 2FA is enabled

### Connection timeout:
- Check firewall settings
- Verify EMAIL_HOST and EMAIL_PORT are correct
- Try different port (465 with SSL instead of 587 with TLS)

### Authentication failed:
- Double-check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- For Gmail, make sure you're using App Password, not regular password
- Check if account has 2FA enabled

