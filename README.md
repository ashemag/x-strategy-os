# X (Twitter) to Google Sheets Sync

An open-source tool that fetches your tweets from X (formerly Twitter) and syncs them to a Google Spreadsheet. Can be configured to run on a schedule and deployed to various cloud platforms.

## Features

- Fetches your recent tweets from X/Twitter API
- Syncs tweet data to Google Sheets (ID, text, created_at, likes, retweets, replies, media info)
- Flask web server with health check endpoint
- Manual sync endpoint for on-demand updates
- Scheduled sync capability (configurable)
- Media detection (images, videos, GIFs)
- Automatic formatting and sorting of spreadsheet data

## Prerequisites

1. **X/Twitter API Access:**
   - Create a developer account at https://developer.twitter.com
   - Create an app and get your API keys
   - You'll need: API Key, API Key Secret, and Bearer Token

2. **Google Sheets API:**
   - Create a project in Google Cloud Console
   - Enable Google Sheets API
   - Create a service account and download the JSON credentials
   - Share your Google Sheet with the service account email

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd x-strategy-os
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     - Twitter/X API credentials
     - Google service account JSON
     - Your Twitter username
     - Google Sheet ID

4. **Run locally:**
   ```bash
   python app.py
   ```

## Environment Variables

See `.env.example` for all required environment variables:
- `TWITTER_API_KEY`: Your X/Twitter API Key
- `TWITTER_API_KEY_SECRET`: Your X/Twitter API Key Secret
- `TWITTER_BEARER_TOKEN`: Your X/Twitter Bearer Token
- `TWITTER_USERNAME`: Your Twitter username (without @)
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Your Google service account credentials (JSON string)
- `GOOGLE_SHEET_ID`: The ID of your Google Sheet

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /sync` - Trigger a manual sync
- `GET /` - Welcome page

## Utility Scripts

- `check_rate_limit.py` - Check your Twitter API rate limits
- `check_sheet.py` - Test Google Sheets connection and view current data
- `clear_sheet.py` - Clear all data from the Google Sheet
- `fix_formatting.py` - Fix formatting issues in the spreadsheet
- `get_bearer_token.py` - Helper to generate Bearer Token from API keys
- `get_user_id.py` - Get Twitter user ID from username
- `resort_sheet.py` - Resort spreadsheet data by date
- `test_media_detection.py` - Test media detection functionality
- `test_sync.py` - Test the sync functionality

## Deployment

This app can be deployed to various cloud platforms:
- Fly.io
- Heroku
- Google Cloud Run
- AWS Lambda
- Any platform that supports Python Flask apps

For deployment instructions, create platform-specific configuration files as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.