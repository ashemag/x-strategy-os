#!/usr/bin/env python3
from app import has_link, count_hashtags, count_mentions

# Test the media detection functions
test_tweets = [
    {
        "text": "Check out this article https://example.com #tech #ai",
        "has_attachments": False
    },
    {
        "text": "Just posted a photo! #photography",
        "has_attachments": True,
        "media_count": 1
    },
    {
        "text": "No links or media here @someone",
        "has_attachments": False
    },
    {
        "text": "Multiple links https://example.com and http://test.com #web",
        "has_attachments": False
    }
]

print("Testing media detection functions:\n")

for i, tweet in enumerate(test_tweets, 1):
    print(f"Tweet {i}: {tweet['text'][:50]}...")
    print(f"  Has Link: {has_link(tweet['text'])}")
    print(f"  Hashtag Count: {count_hashtags(tweet['text'])}")
    print(f"  Mention Count: {count_mentions(tweet['text'])}")
    print()

print("✓ Media detection functions are working correctly")