#!/usr/bin/env python3
"""
Script to get Twitter Bearer Token from API Key and Secret
"""
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

def get_bearer_token():
    API_KEY = os.environ.get('TWITTER_API_KEY')
    API_SECRET = os.environ.get('TWITTER_API_KEY_SECRET')

    response = requests.post(
        "https://api.x.com/oauth2/token",
        auth=HTTPBasicAuth(API_KEY, API_SECRET),
        data={"grant_type": "client_credentials"}
    )

    if response.status_code == 200:
        bearer_token = response.json()["access_token"]
        print("Bearer token:", bearer_token)
        print("\nAdd this to your .env file as:")
        print(f"TWITTER_BEARER_TOKEN={bearer_token}")
        return bearer_token
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    get_bearer_token()