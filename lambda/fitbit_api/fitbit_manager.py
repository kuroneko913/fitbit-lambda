import fitbit
from secret_manager import SecretManager
from datetime import datetime, timedelta, timezone
import requests
import json

class Fitbit:
    
    # 取得対象
    RESOURCES = [
        'activities/caloriesBMR',
        'activities/tracker/calories',
        'activities/tracker/steps',
        'activities/tracker/distance',
        'activities/tracker/minutesSedentary',
        'activities/tracker/minutesLightlyActive',
        'activities/tracker/minutesFairlyActive',
        'activities/tracker/minutesVeryActive',
        'activities/tracker/activityCalories',
        'foods/log/water',
        'foods/log/caloriesIn',
        'body/weight',
        'body/fat',
        'body/bmi',
    ]
    
    def __init__(self):
        self.client = self.__get_client()
        
    def __get_client(self):
        sm = SecretManager('Fitbit')
        # あらかじめトークンリフレッシュを行う
        self.__update_tokens(sm)
        secret = sm.get()
        return fitbit.Fitbit(
            secret['CLIENT_ID'], 
            secret['CLIENT_SECRET'], 
            access_token = secret['ACCESS_TOKEN'], 
            refresh_token= secret['REFRESH_TOKEN']
        )
        
    def __get_yesterday(self):
        return datetime.now(timezone(timedelta(hours=9))) - timedelta(days=1)
    
    # 前日のサマリーを取得したいので。
    def intraday_time_series(self, resource):
        yesterday = self.__get_yesterday()
        return self.client.intraday_time_series(resource, base_date = yesterday)

    def get_resources(self):
        return self.RESOURCES
        
    def sleep(self):
        yesterday = self.__get_yesterday()
        return self.client.sleep(yesterday)
        
    def devices(self):
        return self.client.get_devices()

    def __update_tokens(self, fitbit_secret_manager):
        sm = fitbit_secret_manager
        secret = sm.get()
        params = self.__get_refresh_tokens(secret)
        secrets = {
            'BASIC_TOKEN': secret['BASIC_TOKEN'],
            'CLIENT_ID': secret['CLIENT_ID'],
            'CLIENT_SECRET': secret['CLIENT_SECRET'],
            'ACCESS_TOKEN': params['access_token'],
            'REFRESH_TOKEN': params['refresh_token'],
            'UPDATED': datetime.now(timezone(timedelta(hours=9))).strftime('%Y/%m/%d %H:%M:%S'),
        }
        sm.update(secrets)
    
    def __get_refresh_tokens(self, secret):
        headers = {
            'Authorization':'Basic '+secret['BASIC_TOKEN'],
            'Content-Type':'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type':'refresh_token',
            'refresh_token':secret['REFRESH_TOKEN']
        }
        response = requests.post(
            'https://api.fitbit.com/oauth2/token', 
            headers = headers, 
            data = data
        )
        refresh_tokens = json.loads(response.content)
        return refresh_tokens