from TwitterAPI import TwitterAPI, HydrateType
import json

class TweetsSearcher:
  def __init__(self, credentials):
    self.api = TwitterAPI(credentials['api_key'],
                          credentials['api_key_secret'],
                          credentials['access_token'],
                          credentials['access_token_secret'],
                          api_version='2',
                          auth_type='oAuth2')

  def run(self, filter, start_time, end_time, max_results):
    stream = self.api.request('tweets/search/all',
                              {
                                'query': {filter},
                                'start_time': start_time,
                                'end_time': end_time,
                                'max_results': max_results,
                                'expansions': 'author_id',
                                'tweet.fields': 'created_at,lang,public_metrics',
                                'user.fields': 'username,location,public_metrics'
                              },
                              hydrate_type=HydrateType.APPEND)

    for tweet in stream:
      print(json.dumps(tweet, indent=2))
      # print(tweet['text'] if 'text' in tweet else tweet)

      # if self.__is_tweet_valid(tweet):
      #   print(tweet['text'] if 'text' in tweet else tweet)
      #   self.__reply(tweet['id'])
