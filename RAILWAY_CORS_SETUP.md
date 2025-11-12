# 🔧 Fix: Railway CORS Configuration

## Problem
Password reset and other API calls are timing out. This is likely because CORS is not configured on Railway.

## ✅ Solution: Add CORS Environment Variable on Railway

### Step 1: Go to Railway Dashboard
1. Visit: **https://railway.app**
2. Sign in to your account
3. Open your project
4. Click on your **backend service**: `web-production-95239`

### Step 2: Add CORS Environment Variable
1. Click **"Variables"** tab
2. Click **"+ New Variable"** button
3. Add:
   - **Key**: `CORS_ALLOWED_ORIGINS`
   - **Value**: `https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000`
4. Click **"Add"** or **"Save"**

### Step 3: Verify Other Required Variables
Make sure these are also set:
- `DATABASE_URL` - From PostgreSQL service
- `SECRET_KEY` - Your Django secret key
- `DEBUG` - `False`
- `FRONTEND_URL` - `https://jeevaai.vercel.app`

### Step 4: Redeploy (if needed)
Railway should auto-redeploy when you add variables. If not:
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on latest deployment

---

## ✅ Verify CORS is Working

After adding CORS, test:
1. Go to: **https://jeevaai.vercel.app**
2. Try password reset
3. Check browser console - should not see CORS errors
4. Requests should complete within 5-10 seconds

---

## 🚨 If Still Timing Out

1. **Check Railway logs** for errors
2. **Verify backend is running** - Check Railway dashboard status
3. **Test backend directly**: `https://web-production-95239.up.railway.app`
4. **Check environment variables** are saved correctly

---

**After adding CORS, password reset and other API calls should work!** 🎉

