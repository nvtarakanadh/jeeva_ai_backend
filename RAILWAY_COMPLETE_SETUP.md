# 🚂 Complete Railway Setup Guide

## Your Backend URL
**Backend**: `https://web-production-95239.up.railway.app`

---

## 📋 Step-by-Step Setup

### Step 1: Add PostgreSQL Database to Railway

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Sign in to your account
   - Open your project (the one with your backend)

2. **Create PostgreSQL Database**
   - Click **"+ New"** button (top right or in the project)
   - Select **"Database"** → **"Add PostgreSQL"**
   - Railway will automatically create a PostgreSQL database
   - Wait 1-2 minutes for it to provision

3. **Get Database Connection String**
   - Click on the **PostgreSQL** service you just created
   - Go to **"Variables"** tab
   - Find **`DATABASE_URL`** variable
   - **Copy the entire value** (it looks like: `postgresql://postgres:password@host:port/railway`)
   - ⚠️ **Keep this safe** - you'll need it in the next step

---

### Step 2: Link Database to Backend

1. **Go to Backend Service**
   - Go back to your **backend service** (`web-production-95239`)
   - Click on it to open

2. **Add Database URL**
   - Click **"Variables"** tab
   - Click **"+ New Variable"** button
   - Add:
     - **Key**: `DATABASE_URL`
     - **Value**: Paste the `DATABASE_URL` you copied from PostgreSQL service
   - Click **"Add"** or **"Save"**

3. **Railway will automatically redeploy** your backend with the new database connection

---

### Step 3: Add Required Environment Variables

Add these variables to your **backend service** → **"Variables"** tab:

#### Essential Variables (Required):

1. **`SECRET_KEY`**
   - **Key**: `SECRET_KEY`
   - **Value**: Generate one using:
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   - Or use a temporary one: `django-insecure-change-this-to-random-key-12345`

2. **`DEBUG`**
   - **Key**: `DEBUG`
   - **Value**: `False`

3. **`CORS_ALLOWED_ORIGINS`**
   - **Key**: `CORS_ALLOWED_ORIGINS`
   - **Value**: `https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000`

4. **`FRONTEND_URL`**
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://jeevaai.vercel.app`

#### Optional Variables (For Email):

5. **`EMAIL_BACKEND`** = `django.core.mail.backends.smtp.EmailBackend`
6. **`EMAIL_HOST`** = `smtp.gmail.com`
7. **`EMAIL_PORT`** = `587`
8. **`EMAIL_USE_TLS`** = `True`
9. **`EMAIL_HOST_USER`** = Your Gmail address (e.g., `your-email@gmail.com`)
10. **`EMAIL_HOST_PASSWORD`** = Your Gmail App Password (16 characters)
11. **`DEFAULT_FROM_EMAIL`** = Your Gmail address

#### Optional Variables (For AI Features):

12. **`GEMINI_API_KEY`** = Your Gemini API key (if you have one)
13. **`FIRECRAWL_API_KEY`** = Your Firecrawl API key (if you have one)
14. **`DR7_API_KEY`** = Your Dr7 API key (if you have one)

---

### Step 4: Run Database Migrations

1. **Check if Migrations Run Automatically**
   - Go to backend service → **"Deployments"** tab
   - Click on the latest deployment
   - Check the logs for migration output
   - Look for: `Running migrations...` or `Applying migrations...`

2. **If Migrations Don't Run Automatically**
   - Go to backend service → **"Settings"** tab
   - Look for **"Deploy Command"** or **"Start Command"**
   - Update it to:
     ```bash
     python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
     ```
   - Save and redeploy

---

### Step 5: Update Frontend Environment Variable

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com
   - Sign in to your account
   - Open your frontend project: `jeeva_ai_frontend`

2. **Update API Base URL**
   - Go to **"Settings"** → **"Environment Variables"**
   - Find **`VITE_API_BASE_URL`** in the list
   - Click **"Edit"** (or add it if it doesn't exist)
   - Update the value to: `https://web-production-95239.up.railway.app`
   - Make sure it's set for **Production**, **Preview**, and **Development** environments
   - Click **"Save"**

3. **Redeploy Frontend**
   - Go to **"Deployments"** tab
   - Click **"..."** (three dots) on the latest deployment
   - Click **"Redeploy"**
   - Or push a new commit to trigger automatic redeploy

---

### Step 6: Verify Everything Works

1. **Test Backend**
   - Open: `https://web-production-95239.up.railway.app`
   - You should see a Django page or API response
   - If you see an error page, that's okay - it means the backend is running

2. **Test Frontend**
   - Go to: `https://jeevaai.vercel.app`
   - Open browser console (F12)
   - Check for: `🔧 API Base URL: https://web-production-95239.up.railway.app`
   - Try logging in or registering

3. **Test Database Connection**
   - Try creating a new user account
   - If registration works, database is connected!
   - Check Railway logs for any database errors

---

## ✅ Checklist

- [ ] PostgreSQL database created on Railway
- [ ] `DATABASE_URL` added to backend variables
- [ ] `SECRET_KEY` added to backend variables
- [ ] `DEBUG=False` added to backend variables
- [ ] `CORS_ALLOWED_ORIGINS` added to backend variables
- [ ] `FRONTEND_URL` added to backend variables
- [ ] Database migrations run successfully
- [ ] `VITE_API_BASE_URL` updated in Vercel
- [ ] Frontend redeployed
- [ ] Backend is accessible
- [ ] Frontend can connect to backend
- [ ] Login/Registration works

---

## 🚨 Troubleshooting

### Database Connection Error
**Symptoms**: Backend logs show database connection errors

**Solution**:
- Verify `DATABASE_URL` is correctly set in backend variables
- Check PostgreSQL service is running (should show "Active")
- Make sure `DATABASE_URL` from PostgreSQL service is copied exactly

### CORS Errors
**Symptoms**: Browser console shows CORS errors

**Solution**:
- Verify `CORS_ALLOWED_ORIGINS` includes `https://jeevaai.vercel.app`
- Make sure there are no extra spaces in the value
- Redeploy backend after adding CORS variable

### Frontend Can't Connect to Backend
**Symptoms**: Frontend shows "Failed to fetch" or timeout errors

**Solution**:
- Verify `VITE_API_BASE_URL` is set correctly in Vercel
- Check backend is accessible: `https://web-production-95239.up.railway.app`
- Check browser console for the actual API URL being used
- Make sure frontend is redeployed after updating environment variable

### Migrations Not Running
**Symptoms**: Database tables don't exist

**Solution**:
- Check Railway deployment logs
- Add migration command to deploy command (see Step 4)
- Manually trigger a redeploy

---

## 🎯 Quick Reference

**Backend URL**: `https://web-production-95239.up.railway.app`

**API Endpoints**:
- Login: `https://web-production-95239.up.railway.app/api/auth/login/`
- Register: `https://web-production-95239.up.railway.app/api/auth/register/`
- Password Reset: `https://web-production-95239.up.railway.app/api/auth/password/reset/request/`

**Frontend URL**: `https://jeevaai.vercel.app`

---

## 📝 Notes

- Railway free tier is faster than Render and doesn't have the 15-minute sleep issue
- Database is automatically backed up by Railway
- You can monitor usage in Railway dashboard
- Railway provides better logs and debugging tools

---

**Once you complete all steps, your Railway backend should be fully connected and working!** 🎉

