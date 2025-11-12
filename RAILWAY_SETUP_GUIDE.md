# 🚂 Railway Deployment Setup Guide

## Current Status
- ✅ Backend deployed on Railway: `web-production-95239.up.railway.app`
- ⏳ Need to: Add database, link it, update frontend

---

## Step 1: Add PostgreSQL Database to Railway

### 1.1 Go to Railway Dashboard
1. Visit: **https://railway.app**
2. Sign in to your account
3. Open your project (the one with your backend)

### 1.2 Create PostgreSQL Database
1. Click **"+ New"** button (top right)
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. Wait for it to provision (usually 1-2 minutes)

### 1.3 Get Database Connection String
1. Click on the **PostgreSQL** service you just created
2. Go to **"Variables"** tab
3. Find **`DATABASE_URL`** variable
4. **Copy the entire value** (it looks like: `postgresql://postgres:password@host:port/railway`)

---

## Step 2: Link Database to Backend

### 2.1 Add Database URL to Backend
1. Go back to your **backend service** (`web-production-95239`)
2. Click on **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the `DATABASE_URL` you copied from the PostgreSQL service
5. Click **"Add"**

### 2.2 Add Other Required Environment Variables
Add these variables to your backend service:

#### Required Variables:
1. **`SECRET_KEY`**
   - Generate a new secret key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Or use: `django-insecure-your-random-secret-key-here`

2. **`DEBUG`**
   - Value: `False` (for production)

3. **`ALLOWED_HOSTS`**
   - Value: `web-production-95239.up.railway.app,*.railway.app,*.up.railway.app,jeevaai.vercel.app`

4. **`CORS_ALLOWED_ORIGINS`**
   - Value: `https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000`

5. **`FRONTEND_URL`**
   - Value: `https://jeevaai.vercel.app`

#### Optional (for email):
6. **`EMAIL_BACKEND`**
   - Value: `django.core.mail.backends.smtp.EmailBackend`

7. **`EMAIL_HOST`**
   - Value: `smtp.gmail.com`

8. **`EMAIL_PORT`**
   - Value: `587`

9. **`EMAIL_USE_TLS`**
   - Value: `True`

10. **`EMAIL_HOST_USER`**
    - Value: Your Gmail address

11. **`EMAIL_HOST_PASSWORD`**
    - Value: Your Gmail App Password

12. **`DEFAULT_FROM_EMAIL`**
    - Value: Your Gmail address

#### AI API Keys (if you have them):
13. **`GEMINI_API_KEY`** (optional)
14. **`FIRECRAWL_API_KEY`** (optional)
15. **`DR7_API_KEY`** (optional)

### 2.3 Redeploy Backend
1. Railway will automatically redeploy when you add variables
2. Or go to **"Deployments"** tab → Click **"Redeploy"**
3. Wait for deployment to complete (2-3 minutes)

---

## Step 3: Run Database Migrations

### 3.1 Connect to Railway CLI (Optional)
You can run migrations via Railway CLI or through the Railway dashboard.

### 3.2 Run Migrations via Railway Dashboard
1. Go to your backend service
2. Click **"Deployments"** tab
3. Find the latest deployment
4. Click on it to see logs
5. Migrations should run automatically if you have a startup script

### 3.3 Or Add Migration Command to Railway
1. Go to backend service → **"Settings"** tab
2. Look for **"Deploy Command"** or **"Start Command"**
3. Update it to:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## Step 4: Update Frontend to Use Railway Backend

### 4.1 Update Frontend Environment Variable
1. Go to **Vercel Dashboard**: https://vercel.com
2. Open your frontend project: `jeeva_ai_frontend`
3. Go to **"Settings"** → **"Environment Variables"**
4. Find **`VITE_API_BASE_URL`**
5. Update it to: `https://web-production-95239.up.railway.app`
6. If it doesn't exist, add it:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://web-production-95239.up.railway.app`
7. Click **"Save"**

### 4.2 Redeploy Frontend
1. Go to **"Deployments"** tab in Vercel
2. Click **"Redeploy"** on the latest deployment
3. Or push a new commit to trigger redeploy

---

## Step 5: Verify Everything Works

### 5.1 Test Backend
1. Open: `https://web-production-95239.up.railway.app`
2. You should see a Django page or API response

### 5.2 Test Frontend
1. Go to: `https://jeevaai.vercel.app`
2. Try logging in
3. Check browser console for any errors

### 5.3 Test Database Connection
1. Check Railway logs for any database connection errors
2. Try creating a new user account
3. If it works, database is connected!

---

## Quick Reference: Railway Backend URL
**Backend URL**: `https://web-production-95239.up.railway.app`

**API Endpoints**:
- Login: `https://web-production-95239.up.railway.app/api/auth/login/`
- Register: `https://web-production-95239.up.railway.app/api/auth/register/`
- Password Reset: `https://web-production-95239.up.railway.app/api/auth/password/reset/request/`

---

## Troubleshooting

### Database Connection Error
- Check `DATABASE_URL` is correctly set in backend variables
- Verify PostgreSQL service is running
- Check Railway logs for connection errors

### CORS Errors
- Make sure `CORS_ALLOWED_ORIGINS` includes your Vercel domain
- Redeploy backend after adding CORS variable

### Frontend Can't Connect
- Verify `VITE_API_BASE_URL` is set correctly in Vercel
- Check backend is accessible: `https://web-production-95239.up.railway.app`
- Check browser console for errors

---

## Next Steps After Setup

1. ✅ Test login/registration
2. ✅ Test password reset
3. ✅ Verify database is storing data
4. ✅ Check Railway logs for any errors
5. ✅ Monitor Railway usage (free tier has limits)

---

**Note**: Railway free tier is faster than Render and doesn't have the 15-minute sleep issue. Your backend should respond much faster now!

