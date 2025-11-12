# Update Backend CORS for Vercel Deployment

## Your Frontend URL
**Frontend**: https://jeevaai.vercel.app/

## Quick Fix: Update CORS on Render

### Step 1: Go to Render Dashboard
1. Go to https://render.com
2. Sign in to your account
3. Click on your backend service: `jeeva-ai-backend-sms7`

### Step 2: Update Environment Variables
1. Go to **"Environment"** tab
2. Find `CORS_ALLOWED_ORIGINS` variable
3. **Update it** to include your Vercel domain:
   ```
   https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000
   ```
   **Note**: Include both the main domain and the preview domain (with `-git-main`)

4. **If the variable doesn't exist**, click "Add Environment Variable":
   - **Key**: `CORS_ALLOWED_ORIGINS`
   - **Value**: `https://jeevaai.vercel.app,https://jeevaai-git-main.vercel.app,http://localhost:8080,http://localhost:3000`

### Step 3: Save and Redeploy
1. Click **"Save Changes"**
2. Render will automatically redeploy your backend
3. Wait for deployment to complete (usually 2-3 minutes)

### Step 4: Verify
1. Check your backend is running: https://jeeva-ai-backend-sms7.onrender.com
2. Try logging in from your frontend: https://jeevaai.vercel.app/
3. Check browser console for any CORS errors

## Why This Fixes the Issue

The delay you're experiencing is likely due to:
1. **CORS preflight requests** being blocked
2. Browser waiting for CORS response
3. Eventually timing out or getting rejected

By adding your Vercel domain to `CORS_ALLOWED_ORIGINS`, the backend will allow requests from your frontend.

## Alternative: Allow All Origins (Temporary - Not Recommended for Production)

If you want to test quickly, you can temporarily set:
```
CORS_ALLOW_ALL_ORIGINS=True
```

But this is **NOT recommended for production** as it allows any website to make requests to your API.

## Verify CORS is Working

After updating, check browser console:
- **Before fix**: CORS errors in console
- **After fix**: No CORS errors, requests go through quickly

