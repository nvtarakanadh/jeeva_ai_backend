# 🔧 Fix: Railway Migration Error During Build

## Problem
Railway is trying to run migrations during the Docker build phase, but `DATABASE_URL` is not available at build time. This causes the error:
```
django.db.utils.OperationalError: [Errno -2] Name or service not known
```

## ✅ Solution: Configure Railway to Run Migrations at Runtime

### Option 1: Use Railway Start Command (Recommended)

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your backend service**: `web-production-95239`
3. **Go to "Settings"** tab
4. **Find "Start Command"** or **"Deploy Command"**
5. **Update it to**:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300
   ```
6. **Save** - Railway will redeploy

This ensures migrations run **after** the build, when `DATABASE_URL` is available.

---

### Option 2: Use Procfile (Already Configured)

The `Procfile` already has:
```
release: python manage.py migrate
web: gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300
```

**But Railway might not be using the Procfile**. To fix:

1. **Go to Railway Dashboard** → Your backend service
2. **Go to "Settings"** tab
3. **Make sure "Build Command"** is empty or just: `pip install -r requirements.txt`
4. **Make sure "Start Command"** is empty (so it uses Procfile)
5. **Or set "Start Command"** to: `python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT`

---

### Option 3: Use nixpacks.toml (Created)

I've created `nixpacks.toml` that configures Railway to:
- **Build phase**: Only install dependencies (no migrations)
- **Start phase**: Run migrations then start server

This file is already in your repo. Railway should use it automatically.

---

## 🎯 Quick Fix (Do This Now)

1. **Go to Railway Dashboard**: https://railway.app
2. **Open backend service**: `web-production-95239`
3. **Go to "Settings"** tab
4. **Find "Start Command"** or **"Deploy Command"**
5. **Set it to**:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 300
   ```
6. **Make sure "Build Command"** does NOT include `migrate`
7. **Save** and wait for redeploy

---

## ✅ Verify It Works

1. **Check Railway Logs**:
   - Go to "Deployments" tab
   - Click latest deployment
   - Look for: `Running migrations...` in the **start** phase (not build phase)

2. **Test Database**:
   - Try registering a new user
   - If it works, migrations ran successfully!

---

## 🚨 Why This Happens

- **Build phase**: Runs during Docker image creation, environment variables not available
- **Start phase**: Runs when container starts, environment variables available
- **Solution**: Run migrations in start phase, not build phase

---

## 📝 What Changed

1. ✅ Created `nixpacks.toml` to configure Railway build process
2. ✅ `Procfile` already has `release` phase for migrations
3. ✅ You need to configure Railway's Start Command

---

**After updating the Start Command, Railway will run migrations at the right time and your deployment should succeed!** 🎉

