import json
import boto3
from fitbit_manager import Fitbit

OZ_UNIT = 29.565 # 1floz(アメリカ)≒29.57ml
POND_UNIT = 2.2046 # 1pond = 0.45359237kg

# 前日の活動記録を返す
def handler(event, context):
    try:
        fitbit = Fitbit()
        sleep = fitbit.sleep()
        results = {'sleep':{}}
        results['battery_level'] = fitbit.devices()[0]['batteryLevel']
        results['activities'] = get_fitbit_activities(fitbit)
        if ('sleep' in sleep and len(sleep['sleep']) == 1):
            results['sleep']['startTime'] = sleep['sleep'][0]['startTime']
            results['sleep']['endTime'] = sleep['sleep'][0]['endTime']
            results['sleep']['totalMinutesAsleep'] = sleep['summary']['totalMinutesAsleep']
        else:
            results['sleep'] = 'no-sleep-data'
        print(results)
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': str(e)
        }
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }

def get_fitbit_activities(fitbit):
    results = {}
    for resource in fitbit.get_resources():
        data = fitbit.intraday_time_series(resource)
        results[list(data.keys())[0]] = list(data.values())[0][0]['value']
    results['datetime'] = list(data.values())[0][0]['dateTime']
    results['foods-log-water'] = float(results['foods-log-water']) * OZ_UNIT
    results['body-weight'] = float(results['body-weight']) / POND_UNIT   
    return results
    