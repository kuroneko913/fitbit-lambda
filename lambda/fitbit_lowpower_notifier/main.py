import json
import boto3
from datetime import datetime,timedelta,timezone
from line_notify import LINE_Notify
from google_calendar_api import GoogleCalendarApi

LOW_LEVEL_THRESHOLD = 10
LIMIT_OF_CHARGE_EVENT_HOUR = 2
TIMEZONE_OFFSET_FOR_JST = 9
SERVICE_ACCOUNT_SECRET_NAME = 'spreadsheet-updater' #SecretManagerのキー名 
CALENDAR_ID = "myblackcat7112@gmail.com"

def handler(event, context):
    try:
        battery_level = get_battery_level()
        if (battery_level <= LOW_LEVEL_THRESHOLD):
            # LINENotifyに飛ばす
            notify = LINE_Notify()
            notify.call(f"バッテリレベルが下がっています。\n充電してください!\nバッテリレベル:{battery_level}\n")
            # GoogleCalendarに登録する
            calendarEvent = createEventForLowPowerNotification()
            calendar = GoogleCalendarApi(SERVICE_ACCOUNT_SECRET_NAME)
            calendar.createEvent(CALENDAR_ID,calendarEvent)
    except Exception as e:
        print(e)
        
    return {
        'statusCode': 200,
        'body': json.dumps(battery_level)
    }
    
def createEventForLowPowerNotification():
    isoformat_time = (datetime.now(timezone(timedelta(hours=TIMEZONE_OFFSET_FOR_JST)))+timedelta(hours=LIMIT_OF_CHARGE_EVENT_HOUR)).isoformat()
    event = {
        'summary': f'{LIMIT_OF_CHARGE_EVENT_HOUR}時間以内にFitbitを充電して！',
        'description': f'Fitbitのバッテリレベルが下がっています。{LIMIT_OF_CHARGE_EVENT_HOUR}時間以内に充電してください！',
        'start': {
            'dateTime': isoformat_time,
            'timeZone': 'Japan', 
        },
        'end': {
            'dateTime': isoformat_time,
            'timeZone': 'Japan', 
        }
    }
    return event
    
def get_battery_level():
    fitbit_api = boto3.client("lambda")
    fitbit_res = fitbit_api.invoke(
        FunctionName='fitbit-api'
    )
    fitbit_json = json.loads(fitbit_res['Payload'].read())
    fitbit_json_body = json.loads(fitbit_json['body'])
    if (fitbit_json['statusCode'] != 200):
        raise Exception(fitbit_json_body)
    return fitbit_json_body['battery_level']
