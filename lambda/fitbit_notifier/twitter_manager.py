import twitter
import json
from secret_manager import SecretManager

class Twitter:
    
    def __init__(self):
        self.client = self.__get_client()
        
    def __get_client(self):
        sm = SecretManager('Twitter')
        secret = sm.get()
        auth = twitter.OAuth(
            consumer_key=secret['API_KEY'],
            consumer_secret=secret['API_SECRET'],
            token=secret['ACCESS_TOKEN'],
            token_secret=secret['ACCESS_TOKEN_SECRET']
        )
        t = twitter.Twitter(auth=auth)
        return t
        
    def status_update(self, statuses):
        self.client.statuses.update(status=statuses)
