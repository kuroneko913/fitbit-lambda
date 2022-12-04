from secret_manager import SecretManager
import requests
import json
    
class LINE_Notify:

    def __init__(self):
        self.url = 'https://notify-api.line.me/api/notify'
        self.headers = {'Authorization': f"Bearer {self.__get_secret()['ACCESS_TOKEN']}"}

    def call(self, message):
        requests.post(self.url, headers = self.headers, data = {'message': message})

    def __get_secret(self):
        sm = SecretManager('LINE_Notify')
        return sm.get()
