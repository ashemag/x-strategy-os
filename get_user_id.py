#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

def get_user_id():
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
    username = os.environ.get('TWITTER_USERNAME')

    client = tweepy.Client(bearer_token=bearer_token)
    user = client.get_user(username=username)

    print(f"Username: {username}")
    print(f"User ID: {user.data.id}")
    return user.data.id

if __name__ == "__main__":
    get_user_id()