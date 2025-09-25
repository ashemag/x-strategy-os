#!/usr/bin/env python3
import os
import tweepy
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_rate_limit():
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
    client = tweepy.Client(bearer_token=bearer_token)

    try:
        # Make a simple request to check rate limit
        response = client.get_user(username='twitter')

        # Check rate limit headers
        print("Rate limit info:")
        print(f"Current time: {datetime.now()}")

    except tweepy.TooManyRequests as e:
        print(f"Rate limit exceeded: {e}")
        print(f"Current time: {datetime.now()}")
        print("Please wait approximately 15 minutes before retrying.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_rate_limit()