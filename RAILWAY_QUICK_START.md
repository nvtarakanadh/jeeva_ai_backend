# 🚂 Railway Quick Start Guide

## Your Backend URL
**Backend**: `https://web-production-95239.up.railway.app`

---

## ✅ Step 1: Add PostgreSQL Database (2 minutes)

1. Go to **Railway Dashboard**: https://railway.app
2. Open your project
3. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
4. Wait 1-2 minutes for database to be created
5. Click on the **PostgreSQL** service
6. Go to **"Variables"** tab
7. **Copy** the `DATABASE_URL` value

---

## ✅ Step 2: Link Database to Backend (1 minute)

1. Go back to your **backend service** (`web-production-95239`)
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the `DATABASE_URL` from PostgreSQL service
5. Click **"Add"**

---

## ✅ Step 3: Add Required Environment Variables (3 minutes)

Add these to your backend service **"Variables"** tab:

### Essential Variables:

1. **`SECRET_KEY`**
   ```
   django-insecure-change-this-to-a-random-secret-key-in-production
   ```
   *(Generate a secure one later)*

2. **`DEBUG`**
   ```
   False
   ```

3. **`CORS_ALLOWED_ORIGINS`**
   ```
   https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000
   ```

4. **`FRONTEND_URL`**
   ```
   https://jeevaai.vercel.app
   ```

### Optional (for email):
5. **`EMAIL_BACKEND`** = `django.core.mail.backends.smtp.EmailBackend`
6. **`EMAIL_HOST`** = `smtp.gmail.com`
7. **`EMAIL_PORT`** = `587`
8. **`EMAIL_USE_TLS`** = `True`
9. **`EMAIL_HOST_USER`** = Your Gmail
10. **`EMAIL_HOST_PASSWORD`** = Your Gmail App Password
11. **`DEFAULT_FROM_EMAIL`** = Your Gmail

---

## ✅ Step 4: Run Database Migrations

Railway should auto-run migrations, but if not:

1. Go to backend service → **"Deployments"** tab
2. Click on latest deployment
3. Check logs for migration output
4. If migrations didn't run, add this to **"Settings"** → **"Deploy Command"**:
   ```bash
   python manage.py migrate && gunicorn jeeva_ai_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## ✅ Step 5: Update Frontend (2 minutes)

1. Go to **Vercel Dashboard**: https://vercel.com
2. Open your frontend project
3. Go to **"Settings"** → **"Environment Variables"**
4. Find or add **`VITE_API_BASE_URL`**
5. Set value to: `https://web-production-95239.up.railway.app`
6. Click **"Save"**
7. Go to **"Deployments"** → Click **"Redeploy"**

---

## ✅ Step 6: Test Everything

1. **Test Backend**: https://web-production-95239.up.railway.app
2. **Test Frontend**: https://jeevaai.vercel.app
3. **Try Login**: Should work now!

---

## 🎯 Quick Checklist

- [ ] PostgreSQL database created
- [ ] `DATABASE_URL` added to backend
- [ ] `SECRET_KEY` added to backend
- [ ] `DEBUG=False` added to backend
- [ ] `CORS_ALLOWED_ORIGINS` added to backend
- [ ] `FRONTEND_URL` added to backend
- [ ] Migrations run successfully
- [ ] `VITE_API_BASE_URL` updated in Vercel
- [ ] Frontend redeployed
- [ ] Test login works

---

## 🚨 Troubleshooting

### Database Connection Error
- Check `DATABASE_URL` is correct
- Verify PostgreSQL service is running

### CORS Errors
- Verify `CORS_ALLOWED_ORIGINS` includes Vercel domain
- Redeploy backend

### Frontend Can't Connect
- Check `VITE_API_BASE_URL` in Vercel
- Verify backend is accessible
- Check browser console

---

**That's it! Your Railway backend should be fully connected now!** 🎉

