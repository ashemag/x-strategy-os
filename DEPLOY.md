# Deployment Guide

## Fly.io Deployment

### Prerequisites

1. **Install Fly CLI:**
   ```bash
   # macOS
   brew install flyctl

   # Linux/WSL
   curl -L https://fly.io/install.sh | sh

   # Windows
   pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Sign up/Login to Fly.io:**
   ```bash
   flyctl auth login
   ```

### Step-by-Step Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ashemag/x-strategy-os.git
   cd x-strategy-os
   ```

2. **Copy and configure fly.toml:**
   ```bash
   cp fly.toml.example fly.toml
   ```
   Edit `fly.toml` and update the app name to something unique.

3. **Launch the app (first time only):**
   ```bash
   flyctl launch --now=false
   ```
   - Choose your app name (must be globally unique)
   - Select your preferred region
   - Don't deploy yet when prompted

4. **Set your secrets/environment variables:**
   ```bash
   # Twitter/X API credentials
   flyctl secrets set TWITTER_API_KEY="your_api_key_here"
   flyctl secrets set TWITTER_API_KEY_SECRET="your_api_secret_here"
   flyctl secrets set TWITTER_BEARER_TOKEN="your_bearer_token_here"
   flyctl secrets set TWITTER_USERNAME="your_username_without_@"

   # Google Sheets configuration
   flyctl secrets set GOOGLE_SHEET_ID="your_sheet_id_here"

   # Google Service Account (paste as single line)
   flyctl secrets set GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
   ```

5. **Deploy the application:**
   ```bash
   flyctl deploy
   ```

6. **Verify deployment:**
   ```bash
   # Check app status
   flyctl status

   # View logs
   flyctl logs

   # Open app in browser
   flyctl open
   ```

### Testing Your Deployment

1. **Check health endpoint:**
   ```bash
   curl https://your-app-name.fly.dev/health
   ```

2. **Trigger manual sync:**
   ```bash
   curl https://your-app-name.fly.dev/sync
   ```

### Monitoring & Maintenance

- **View live logs:**
  ```bash
  flyctl logs --tail
  ```

- **SSH into container:**
  ```bash
  flyctl ssh console
  ```

- **Scale resources:**
  ```bash
  # Scale up memory
  flyctl scale memory 512

  # Add more instances
  flyctl scale count 2
  ```

### Updating Your Deployment

After making changes to your code:

```bash
git add .
git commit -m "Your update message"
git push origin main
flyctl deploy
```

### Troubleshooting

1. **App won't start:**
   - Check logs: `flyctl logs`
   - Verify all environment variables are set: `flyctl secrets list`

2. **Google Sheets not updating:**
   - Ensure service account has access to your sheet
   - Verify GOOGLE_SERVICE_ACCOUNT_JSON is properly formatted

3. **Twitter API errors:**
   - Check rate limits with `check_rate_limit.py`
   - Verify API credentials are correct

### Cost Optimization

- The configuration uses `auto_stop_machines = true` to stop when not in use
- Minimum configuration (256MB RAM) keeps costs low
- Consider scheduling syncs during specific hours only

## Alternative Deployment Options

### Heroku
1. Create `Procfile`:
   ```
   web: python app.py
   ```
2. Deploy using Heroku CLI or GitHub integration

### Google Cloud Run
1. Build container: `docker build -t gcr.io/PROJECT_ID/x-strategy .`
2. Push to registry: `docker push gcr.io/PROJECT_ID/x-strategy`
3. Deploy: `gcloud run deploy --image gcr.io/PROJECT_ID/x-strategy`

### AWS Lambda
Consider using Zappa or Serverless Framework for Lambda deployment.

## Security Best Practices

1. **Never commit secrets to the repository**
2. **Use environment variables for all sensitive data**
3. **Regularly rotate API keys**
4. **Monitor usage and set up alerts**
5. **Keep dependencies updated**