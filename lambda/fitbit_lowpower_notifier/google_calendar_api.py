from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from secret_manager import SecretManager

class GoogleCalendarApi:

    def __init__(self, secret_name):
        self.secret_name = secret_name
        self.client = self.__get_GoogleCalendarApiClient()

    def __get_GoogleCalendarApiClient(self):
        sm = SecretManager(self.secret_name)
        secret = sm.get()
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            secret, 
            scopes = 'https://www.googleapis.com/auth/calendar'
        )
        return build('calendar','v3', credentials=credentials)

    def createEvent(self,calendarId,event):
        event = self.client.events().insert(calendarId=calendarId,body=event).execute()
        return event


