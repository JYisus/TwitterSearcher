#!/usr/bin/python3

from TwitterAPI import TwitterAPI, HydrateType
from os import environ
import pandas as pd
import json
import utils
import time

API_KEY = utils.getenv('API_KEY','')
API_KEY_SECRET = utils.getenv('API_KEY_SECRET','')
ACCESS_TOKEN = utils.getenv('ACCESS_TOKEN','')
ACCESS_TOKEN_SECRET = utils.getenv('ACCESS_TOKEN_SECRET','')

api = TwitterAPI(
    API_KEY,
    API_KEY_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    api_version='2',
    auth_type='oAuth2'
)

search_filter = "(#leytrans)" \
        + " lang:es" \
        + " -is:retweet"

expansions = "author_id"
# date format YYYY-MM-DDTHH:mm:ssZ
start_time = '2021-05-18T00:00:00Z'
end_time = '2021-05-18T23:59:59Z'
# start_time = '2021-06-29T00:00:00Z'
# end_time = '2021-06-29T23:59:59Z'
tweet_fields = 'created_at,lang,public_metrics,conversation_id,attachments'
user_fields = 'username,location,public_metrics'
max_results = 500
def get_tweets(next_token):
    return api.request('tweets/search/all',
                        {
                            'query': {search_filter},
                            'start_time': start_time,
                            'end_time': end_time,
                            'max_results': max_results,
                            'expansions': expansions,
                            'tweet.fields': tweet_fields,
                            'user.fields': user_fields,
                            'next_token': next_token
                        },
                        hydrate_type=HydrateType.APPEND)

def format_tweet(tweet):
    username = tweet['author_id_hydrate']['username']
    conversation = ''
    if (tweet['id'] != tweet['conversation_id']):
        conversation = 'https://twitter.com/a/status/' + tweet['conversation_id']

    has_image =  'attachments' in tweet

    return {
        'Text': tweet['text'].replace('\n', ' '),
        'Date': tweet['created_at'],
        'Retweets': tweet['public_metrics']['retweet_count'],
        'Favs': tweet['public_metrics']['like_count'],
        'Cites': tweet['public_metrics']['quote_count'],
        'Replys': tweet['public_metrics']['reply_count'],
        'Languaje': tweet['lang'],
        'Author': username,
        'Followers': tweet['author_id_hydrate']['public_metrics']['followers_count'],
        'Link': 'https://twitter.com/' + username + '/status/' + tweet['id'],
        'Replying to': conversation,
        'Has image': has_image
    }

stream = get_tweets(None)
# print(json.dumps(stream.json()['data'], indent=2))
# for tweet in stream:
#     print(json.dumps(tweet, indent=2))

tweets = list(map(format_tweet, stream))

while(('next_token' in stream.json()['meta'])):
    time.sleep(3)
    next_token = stream.json()['meta']['next_token']
    stream = get_tweets(next_token)
    if(stream.status_code == 429):
        time.sleep(5)
        stream = get_tweets(next_token)
    tweets = tweets + list(map(format_tweet, stream))


# formated_tweets = map(format_tweet, tweets)
df = pd.DataFrame(tweets)
df.to_csv(start_time + 'SOLO_LEYTRANS.csv', sep=';', encoding='utf-8-sig')
