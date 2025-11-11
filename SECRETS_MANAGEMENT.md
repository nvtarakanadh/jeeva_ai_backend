# Secrets Management Guide

## ⚠️ IMPORTANT: Never commit secrets to Git

This document explains how to manage secrets securely in this project.

## Current Setup

### 1. Environment Variables (.env file)

The `.env` file is **already in `.gitignore`** and will NOT be committed to Git.

**To set up your local environment:**
1. Copy `env_example.txt` to `.env`:
   ```bash
   cp env_example.txt .env
   ```
2. Fill in your actual secrets in `.env` (this file is git-ignored)

### 2. Production Secrets

For production deployments (Render, Railway, etc.):

#### Option A: Platform Environment Variables (Recommended)
- **Render**: Set environment variables in the dashboard
- **Railway**: Set environment variables in the project settings
- **Vercel**: Set environment variables in project settings

#### Option B: Platform Secret Management
- Use platform-specific secret management services
- Render: Environment variables in dashboard
- Railway: Environment variables in project settings

## Required Environment Variables

### Backend (.env)
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@jeeva.ai

# AI API Keys
GEMINI_API_KEY=your-key
FIRECRAWL_API_KEY=your-key
DR7_API_KEY=your-key

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Email Configuration

### Development (Local)
- **Default**: Uses console backend (emails print to terminal)
- No configuration needed
- Check your Django console output for password reset links

### Production
1. **Gmail Setup**:
   - Enable 2-Factor Authentication
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Use App Password (not regular password) in `EMAIL_HOST_PASSWORD`

2. **Other SMTP Providers**:
   - Update `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` accordingly
   - Use appropriate credentials

## If .env was accidentally committed

If you accidentally committed `.env` to Git:

1. **Remove from Git** (but keep local file):
   ```bash
   git rm --cached .env
   git commit -m "Remove .env from version control"
   ```

2. **If already pushed, rotate all secrets**:
   - Change all passwords, API keys, and tokens
   - Update them in production environments
   - Consider using `git filter-branch` or BFG Repo-Cleaner to remove from history

## Best Practices

1. ✅ **DO**: Use `.env` for local development
2. ✅ **DO**: Use platform environment variables for production
3. ✅ **DO**: Keep `env_example.txt` updated (without secrets)
4. ❌ **DON'T**: Commit `.env` files
5. ❌ **DON'T**: Put secrets in code
6. ❌ **DON'T**: Share secrets in chat/email

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `env_example.txt` has no real secrets
- [ ] Production secrets are in platform environment variables
- [ ] All team members know not to commit secrets
- [ ] Secrets are rotated if accidentally exposed

