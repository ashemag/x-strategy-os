import os
import json
import re
import tweepy
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import pytz
import schedule
import time
from flask import Flask, jsonify

app = Flask(__name__)

SPREADSHEET_ID = '1bIngxeeaZ8cI-SHAg3XpzqEzkIt_Ne3SMvWwneVbXAs'
RANGE_NAME = 'posts!A:V'  # Extended for new media columns

def get_twitter_client():
    api_key = os.environ.get('TWITTER_API_KEY')
    api_key_secret = os.environ.get('TWITTER_API_KEY_SECRET')
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')

    if not api_key or not api_key_secret:
        raise ValueError("TWITTER_API_KEY and TWITTER_API_KEY_SECRET environment variables are required")

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        bearer_token=bearer_token
    )
    return client

def get_sheets_service():
    service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '{}'))

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )

    service = build('sheets', 'v4', credentials=credentials)
    return service

def get_time_period(hour):
    """Categorize hour into time period"""
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

def count_hashtags(text):
    """Count hashtags in tweet text"""
    return len(re.findall(r'#\w+', text))

def count_mentions(text):
    """Count mentions in tweet text, excluding the user's own handle"""
    username = os.environ.get('TWITTER_USERNAME', '')
    mentions = re.findall(r'@\w+', text)
    # Filter out the user's own handle
    mentions = [m for m in mentions if m.lower() != f"@{username.lower()}"]
    return len(mentions)

def has_link(text):
    """Check if tweet has links"""
    # Look for URLs in tweet text
    url_pattern = r'https?://\S+|www\.\S+'
    return "TRUE" if re.search(url_pattern, text) else "FALSE"

def count_images(tweet):
    """Count number of images in tweet"""
    # Check attachments for images
    if hasattr(tweet, 'attachments') and tweet.attachments:
        media_keys = tweet.attachments.get('media_keys', [])
        # For now return count of media keys (would need expansion for exact type)
        return len(media_keys)
    return 0

def has_images(tweet):
    """Check if tweet has images"""
    return "TRUE" if count_images(tweet) > 0 else "FALSE"

def has_video(tweet):
    """Check if tweet has video"""
    # Would need media expansion to properly detect, using basic check for now
    if hasattr(tweet, 'attachments') and tweet.attachments:
        # If there are attachments but we can't determine type, assume it might have video
        # In production, you'd expand media objects to check type
        return "POSSIBLE"
    return "FALSE"

def get_tweet_type(tweet):
    """Determine tweet type based on content"""
    text = tweet.text if hasattr(tweet, 'text') else ''
    if text.startswith('RT @'):
        return "Retweet"
    elif hasattr(tweet, 'referenced_tweets'):
        ref_tweets = tweet.referenced_tweets or []
        for ref in ref_tweets:
            if ref.type == 'replied_to':
                return "Reply"
            elif ref.type == 'quoted':
                return "Quote"
    return "Regular"

def get_last_tweet_id(service):
    """Get the ID of the most recent tweet in the spreadsheet (should be in row 2 for descending order)"""
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='posts!A2:V2'  # Just check row 2 (first data row)
        ).execute()

        values = result.get('values', [])
        if values and len(values[0]) > 20:  # Tweet ID is now in column 21 (index 20) after adding new columns
            return values[0][20]
    except Exception as e:
        print(f"Error getting last tweet ID: {e}")
    return None

def fetch_tweets(since_id=None):
    try:
        twitter_client = get_twitter_client()

        # Hardcoded user ID for ashebytes to save API calls
        user_id = '1237140914558164992'

        kwargs = {
            'id': user_id,
            'max_results': 100,  # Get up to 100 tweets
            'tweet_fields': ['created_at', 'public_metrics', 'author_id', 'text', 'referenced_tweets', 'attachments'],
            'expansions': ['referenced_tweets.id']
        }

        if since_id:
            kwargs['since_id'] = since_id

        tweets = twitter_client.get_users_tweets(**kwargs)

        return tweets.data if tweets.data else []
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []

def update_spreadsheet(tweets, append_mode=True):
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        # Check if spreadsheet has headers
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='posts!A1:V1'
        ).execute()

        existing_headers = result.get('values', [])
        sync_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S ET')

        if not existing_headers or not existing_headers[0]:
            # Add headers if sheet is empty
            headers = [['Date', 'Time', 'Time Period', 'Day of Week', 'Tweet Content', 'Total Engagements',
                       'Likes', 'Retweets', 'Bookmarks', 'Replies', 'Quote Tweets', 'Impressions',
                       'Engagement Rate', 'Tweet Type', 'Has Link', 'Has Image', 'Number of Images', 'Has Video',
                       'Hashtag Count', 'Mention Count', 'Tweet ID', 'Sync Time']]

            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='posts!A1:V1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()

        values = []

        for tweet in tweets:
            metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}

            # Calculate metrics
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            bookmarks = metrics.get('bookmark_count', 0)
            replies = metrics.get('reply_count', 0)
            quotes = metrics.get('quote_count', 0)
            impressions = metrics.get('impression_count', 0)
            total_engagements = likes + retweets + bookmarks + replies + quotes

            # Calculate engagement rate
            engagement_rate = 0
            if impressions > 0:
                engagement_rate = round((total_engagements / impressions) * 100, 2)

            # Time analysis - Convert to Eastern Time
            created_at = tweet.created_at if tweet.created_at else datetime.now()
            # Twitter returns times in UTC, convert to Eastern
            utc_time = created_at.replace(tzinfo=pytz.UTC)
            eastern = pytz.timezone('US/Eastern')
            eastern_time = utc_time.astimezone(eastern)

            hour = eastern_time.hour
            time_period = get_time_period(hour)
            day_of_week = eastern_time.strftime('%A')

            # Content analysis
            tweet_text = tweet.text if hasattr(tweet, 'text') else ''
            hashtag_count = count_hashtags(tweet_text)
            mention_count = count_mentions(tweet_text)
            tweet_type = get_tweet_type(tweet)

            # Media analysis
            link_status = has_link(tweet_text)
            image_status = has_images(tweet)
            image_count = count_images(tweet)
            video_status = has_video(tweet)

            values.append([
                eastern_time.strftime('%Y-%m-%d'),
                eastern_time.strftime('%H:%M:%S') + ' ET',
                time_period,
                day_of_week,
                tweet_text[:500],
                total_engagements,
                likes,
                retweets,
                bookmarks,
                replies,
                quotes,
                impressions,
                f"{engagement_rate}%",
                tweet_type,
                link_status,
                image_status,
                image_count,
                video_status,
                hashtag_count,
                mention_count,
                str(tweet.id),
                sync_time  # Add sync time to each row
            ])

        if not values:
            print("No new tweets to add")
            return True

        # Insert new tweets after the header row (row 2) to maintain descending order
        # This puts newest tweets at the top
        body = {
            'values': values,
            'majorDimension': 'ROWS'
        }

        # Insert at row 2 (after header) instead of appending
        insert_range = f'posts!A2:V{1 + len(values)}'

        # First, insert blank rows
        insert_request = {
            "requests": [
                {
                    "insertRange": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 1,  # After header
                            "endRowIndex": 1 + len(values),
                            "startColumnIndex": 0,
                            "endColumnIndex": 22  # V column
                        },
                        "shiftDimension": "ROWS"
                    }
                }
            ]
        }

        sheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=insert_request
        ).execute()

        # Then update the newly inserted rows with data
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=insert_range,
            valueInputOption='RAW',
            body=body
        ).execute()

        # Only format the header row as bold if we just added headers
        if not existing_headers or not existing_headers[0]:
            formatting_request = {
                "requests": [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startRowIndex": 0,
                                "endRowIndex": 1
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "textFormat": {
                                        "bold": True
                                    }
                                }
                            },
                            "fields": "userEnteredFormat.textFormat.bold"
                        }
                    }
                ]
            }

            sheet.batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=formatting_request
            ).execute()

        print(f"Updated {result.get('updatedCells')} cells in the spreadsheet")
        return True
    except Exception as e:
        print(f"Error updating spreadsheet: {e}")
        return False

def sync_tweets_to_sheets():
    print(f"Starting tweet sync at {datetime.now()}")

    # Get the last tweet ID from the spreadsheet
    service = get_sheets_service()
    last_tweet_id = get_last_tweet_id(service)

    if last_tweet_id:
        print(f"Fetching tweets newer than ID: {last_tweet_id}")
    else:
        print("First sync - fetching recent tweets")

    tweets = fetch_tweets(since_id=last_tweet_id)

    if tweets:
        # Don't reverse - keep tweets in newest-first order
        # tweets are already returned newest-first from Twitter API
        success = update_spreadsheet(tweets)
        if success:
            print(f"Successfully synced {len(tweets)} new tweets to Google Sheets")
        else:
            print("Failed to update Google Sheets")
    else:
        print("No new tweets found or error fetching tweets")
    return len(tweets) if tweets else 0

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/sync', methods=['GET'])
def manual_sync():
    try:
        tweet_count = sync_tweets_to_sheets()
        return jsonify({'status': 'success', 'tweets_synced': tweet_count}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_scheduler():
    eastern = pytz.timezone('US/Eastern')

    def job():
        """Wrapper to run sync in Eastern Time context"""
        current_time = datetime.now(eastern)
        print(f"Running scheduled sync at {current_time.strftime('%Y-%m-%d %H:%M:%S ET')}")
        sync_tweets_to_sheets()

    # Convert 6 AM ET to UTC for consistent scheduling
    # Schedule library runs in local time, so we'll check manually
    print(f"Scheduler started. Will sync daily at 6:00 AM ET")
    print(f"Current time: {datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S ET')}")

    # Run an initial sync on startup
    sync_tweets_to_sheets()

    last_run_date = None

    while True:
        now_et = datetime.now(eastern)

        # Check if it's 6 AM ET and we haven't run today
        if now_et.hour == 6 and now_et.minute == 0 and last_run_date != now_et.date():
            job()
            last_run_date = now_et.date()

        # Sleep for 30 seconds between checks
        time.sleep(30)

if __name__ == '__main__':
    import threading

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)