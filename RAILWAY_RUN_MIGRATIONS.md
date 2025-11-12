# 🗄️ How to Run Database Migrations on Railway

## Problem
The database is created, but the tables are not created automatically. You need to run Django migrations.

---

## ✅ Solution: Run Migrations on Railway

### Method 1: Using Railway CLI (Recommended)

#### Step 1: Install Railway CLI
1. **Download Railway CLI**:
   - Windows: Download from https://railway.app/cli/windows
   - Mac: `brew install railway`
   - Or visit: https://docs.railway.app/develop/cli

2. **Login to Railway**:
   ```bash
   railway login
   ```

#### Step 2: Link Your Project
1. **Navigate to your backend directory**:
   ```bash
   cd D:\Jeeva_AI_pro_Dr7_ai\Jeeva_AI_BackEnd
   ```

2. **Link to Railway project**:
   ```bash
   railway link
   ```
   - Select your project from the list
   - Select your backend service

#### Step 3: Run Migrations
```bash
railway run python manage.py migrate
```

This will run migrations in your Railway environment.

---

### Method 2: Using Railway Dashboard (One-Time Command)

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your backend service**: `web-production-95239`
3. **Go to "Settings"** tab
4. **Find "Deploy Command"** or **"Start Command"**
5. **Update it to**:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```
6. **Save** - Railway will redeploy and run migrations automatically

---

### Method 3: Using Railway Shell (Temporary)

1. **Go to Railway Dashboard**: https://railway.app
2. **Open your backend service**
3. **Go to "Settings"** tab
4. **Look for "Shell"** or **"Console"** option
5. **Open the shell** and run:
   ```bash
   python manage.py migrate
   ```

---

### Method 4: Add to Startup Script (Best for Production)

Create a file `start.sh` in your backend root:

```bash
#!/bin/bash
python manage.py migrate
gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
```

Then update Railway to use this script:
- **Settings** → **Start Command**: `bash start.sh`

Or update `Procfile`:
```
release: python manage.py migrate
web: gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
```

---

## 🎯 Quick Steps (Easiest Method)

### Option A: Update Deploy Command (Recommended)

1. **Go to Railway Dashboard** → Your backend service
2. **Click "Settings"** tab
3. **Find "Deploy Command"** or **"Start Command"**
4. **Change it to**:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```
5. **Save** - Railway will redeploy and run migrations

### Option B: Use Railway CLI

1. **Install Railway CLI** (if not installed)
2. **Open terminal** in your backend directory
3. **Run**:
   ```bash
   railway login
   railway link
   railway run python manage.py migrate
   ```

---

## ✅ Verify Migrations Ran

1. **Check Railway Logs**:
   - Go to your backend service → **"Deployments"** tab
   - Click on latest deployment
   - Look for: `Running migrations...` or `Applying migrations...`

2. **Test Database**:
   - Try registering a new user
   - If it works, migrations ran successfully!

---

## 🚨 Troubleshooting

### Error: "No such table"
- Migrations haven't run yet
- Use one of the methods above to run migrations

### Error: "Database connection failed"
- Check `DATABASE_URL` is set correctly in Railway variables
- Verify PostgreSQL service is running

### Migrations not running automatically
- Update the deploy/start command (Method 2)
- Or use Railway CLI (Method 1)

---

## 📝 Recommended Setup

For production, I recommend **Method 2** (Update Deploy Command):

1. Go to Railway → Backend service → Settings
2. Update **"Deploy Command"** to:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```
3. Save - This ensures migrations run on every deployment

---

**After running migrations, your database tables will be created and you can start using the app!** 🎉

