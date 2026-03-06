# 🌐 Deploy OrchestRAI Public Interface

## Quick Deploy Options

### Option 1: GitHub Pages (Recommended - Free & Easy)

1. **Create a GitHub Repository**:
   ```bash
   # In your project folder
   git init
   git add public_interface.html
   git commit -m "Add OrchestRAI public interface"
   ```

2. **Push to GitHub**:
   - Create a new repository on GitHub (e.g., `orchestrai-interface`)
   - Follow GitHub's instructions to push your code

3. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from branch `main`
   - Folder: `/ (root)`
   - Click Save

4. **Access Your Site**:
   ```
   https://YOUR_USERNAME.github.io/orchestrai-interface/public_interface.html
   ```

---

### Option 2: Netlify Drop (Fastest - 30 seconds)

1. Go to: https://app.netlify.com/drop
2. Drag and drop `public_interface.html`
3. Get instant public URL like: `https://random-name-123.netlify.app`
4. (Optional) Customize the URL in Netlify settings

**That's it!** Share the URL with anyone.

---

### Option 3: AWS S3 Static Website (Your AWS Account)

1. **Create S3 Bucket**:
   ```bash
   set AWS_DEFAULT_REGION=us-east-1
   C:\Python313\python.exe -m awscli s3 mb s3://orchestrai-public-interface
   ```

2. **Upload Interface**:
   ```bash
   C:\Python313\python.exe -m awscli s3 cp public_interface.html s3://orchestrai-public-interface/ --acl public-read
   ```

3. **Enable Static Website Hosting**:
   ```bash
   C:\Python313\python.exe -m awscli s3 website s3://orchestrai-public-interface/ --index-document public_interface.html
   ```

4. **Update Bucket Policy** (make it public):
   Create file `bucket-policy.json`:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::orchestrai-public-interface/*"
       }
     ]
   }
   ```

   Apply policy:
   ```bash
   C:\Python313\python.exe -m awscli s3api put-bucket-policy --bucket orchestrai-public-interface --policy file://bucket-policy.json
   ```

5. **Access Your Site**:
   ```
   http://orchestrai-public-interface.s3-website-us-east-1.amazonaws.com
   ```

---

### Option 4: Vercel (Free & Fast)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy:
   ```bash
   vercel public_interface.html
   ```

3. Follow prompts and get instant URL

---

## Custom Domain Setup

### For GitHub Pages:
1. Buy domain (e.g., from Namecheap, GoDaddy)
2. Add CNAME record pointing to: `YOUR_USERNAME.github.io`
3. In GitHub repo settings → Pages → Custom domain: `orchestrai.yourdomain.com`

### For Netlify:
1. Go to Netlify dashboard → Domain settings
2. Add custom domain
3. Follow DNS configuration instructions

### For AWS S3:
1. Use CloudFront for HTTPS and custom domain
2. Create CloudFront distribution pointing to S3 bucket
3. Add custom domain in Route 53 or your DNS provider

---

## 🔒 Security Enhancements (Optional)

### Hide API Key (Recommended for Production)

Instead of embedding the API key in the HTML, create a backend proxy:

1. **Create Lambda Function** (API Proxy):
   ```python
   import json
   import urllib.request

   API_KEY = 'hcRNhlLtFh4Mjc5A4uKbax5mpKw3DUB2aQD06O2d'
   API_BASE = 'https://yt103tg9n6.execute-api.us-east-1.amazonaws.com/prod/api/v1'

   def lambda_handler(event, context):
       # Forward request to actual API with hidden key
       path = event['path']
       method = event['httpMethod']
       body = event.get('body', '')
       
       url = f"{API_BASE}{path}"
       req = urllib.request.Request(url, data=body.encode(), method=method)
       req.add_header('x-api-key', API_KEY)
       req.add_header('Content-Type', 'application/json')
       
       response = urllib.request.urlopen(req)
       return {
           'statusCode': response.status,
           'body': response.read().decode(),
           'headers': {
               'Content-Type': 'application/json',
               'Access-Control-Allow-Origin': '*'
           }
       }
   ```

2. **Update Interface** to use proxy URL instead of direct API

---

## 📊 Analytics (Optional)

Add Google Analytics to track usage:

```html
<!-- Add before </head> in public_interface.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR_GA_ID');
</script>
```

---

## 🎨 Customization

### Change Branding:
Edit `public_interface.html`:
- Line 7: Change title
- Line 157: Change header text
- Line 158: Change tagline
- Colors: Search for `#667eea` and `#764ba2` to change gradient colors

### Add Logo:
```html
<!-- Add in header section -->
<img src="your-logo.png" alt="Logo" style="height: 60px; margin-bottom: 10px;">
```

---

## 🚀 Quick Deploy Script

Create `deploy_to_netlify.bat`:
```batch
@echo off
echo Deploying OrchestRAI Interface to Netlify...
echo.

REM Install Netlify CLI if not installed
where netlify >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing Netlify CLI...
    npm install -g netlify-cli
)

REM Deploy
netlify deploy --prod --dir=. --site=orchestrai

echo.
echo Deployment complete!
pause
```

Run: `.\deploy_to_netlify.bat`

---

## ✅ Verification

After deployment, test your public interface:

1. Open the public URL
2. Try uploading text content
3. Check status with a workflow ID
4. Verify all tabs work correctly

---

## 📱 Share Your Link

Once deployed, share with:
- **Direct Link**: `https://your-site.com/public_interface.html`
- **QR Code**: Generate at https://www.qr-code-generator.com/
- **Social Media**: Post with demo video
- **Email**: Send to beta testers

---

## 💡 Tips

1. **Test First**: Use local file before deploying publicly
2. **Monitor Costs**: Check AWS Cost Explorer regularly
3. **Set Alerts**: Create CloudWatch alarms for high usage
4. **Backup**: Keep a copy of your interface file
5. **Version Control**: Use Git to track changes

---

**Your OrchestRAI interface is ready to share with the world!** 🌍
