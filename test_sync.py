#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import functions from app
from app import sync_tweets_to_sheets

def test_sync():
    print("Testing Twitter to Google Sheets incremental sync...")
    print(f"Username: {os.environ.get('TWITTER_USERNAME')}")

    # Run the sync
    tweet_count = sync_tweets_to_sheets()

    if tweet_count > 0:
        print(f"\n✓ Successfully synced {tweet_count} new tweets!")
    elif tweet_count == 0:
        print("\n✓ No new tweets to sync (already up to date)")
    else:
        print("\n✗ Sync failed")

    print(f"\nSpreadsheet URL: https://docs.google.com/spreadsheets/d/1bIngxeeaZ8cI-SHAg3XpzqEzkIt_Ne3SMvWwneVbXAs/")

if __name__ == "__main__":
    test_sync()