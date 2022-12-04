import json
import boto3
from twitter_manager import Twitter
from google_spread_sheet import Google_SpreadSheet

def handler(event, context):
    try: 
        # 1日1回だけのアクセスなので、DynamoDBからの取得で問題ない。
        fitbit_api = boto3.client("lambda")
        fitbit_res = fitbit_api.invoke(
            FunctionName='fitbit-api-store-data'
        )
        fitbit_json = json.loads(fitbit_res['Payload'].read())
        fitbit_json_body = json.loads(fitbit_json['body'])[0]['data']
        if (fitbit_json['statusCode'] != 200):
            raise Exception(fitbit_json_body)
        print(fitbit_json_body)
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': str(e)
        }
    
    try:
        # activities
        battery_level = fitbit_json_body['battery_level']
        activities = fitbit_json_body['activities']
        message = build_message_for_activities(activities)
        message += '\n'+build_message_for_mytasks()
        print(message)
        
        # sleep
        sleep = fitbit_json_body['sleep']
        sleep_message = build_message_for_sleep(sleep, activities['datetime'], battery_level)
        print(sleep_message)
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': str(e)
        }
    
    try:
        # twitterへメッセージを投稿する
        twitter = Twitter()
        twitter.status_update(message)
        twitter.status_update(sleep_message)
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': str(e)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(activities)
    }
    
def build_message_for_activities(activities):
    distances = float(activities['activities-tracker-distance']) * 1.61
    calorie_balance = int(activities['foods-log-caloriesIn']) - int(activities['activities-tracker-calories']) 
    message =  f"本日({activities['datetime']})の運動 from Fitbit\n\n"
    message += f"座っていた: {activities['activities-tracker-minutesSedentary']}分\n"
    message += f"軽い運動: {activities['activities-tracker-minutesLightlyActive']}分\n"
    message += f"アクティブな運動: {activities['activities-tracker-minutesFairlyActive']}分\n"
    message += f"激しい運動: {activities['activities-tracker-minutesVeryActive']}分\n\n"
    message += f"本日の歩数: {activities['activities-tracker-steps']}歩 ({distances:.3f}km)\n\n"
    message += f"消費カロリー: {activities['activities-tracker-calories']}kcal\n"
    message += f"カロリー収支: {'+' if calorie_balance >0 else ''}{calorie_balance}kcal\n"
    message += f"飲んだ水:{float(activities['foods-log-water']) :.2f} (ml)"
    return message

def build_message_for_sleep(sleep, datetime, battery_level):
    sleep_message = f"本日({datetime})の睡眠時間 from Fitbit\n\n"
    if (sleep != 'no-sleep-data' and 'startTime' in sleep.keys()):
        sleep_message += f"睡眠時間: {sleep['totalMinutesAsleep']/60 :.3f}時間\n\n"
        sleep_message += f"{sleep['startTime'].split('T')[1].split('.')[0]} ~ {sleep['endTime'].split('T')[1].split('.')[0]}\n\n"
    else:
        sleep_message += f"睡眠時間が記録されていませんでした\n\n"
    sleep_message += f"バッテリ残量:{battery_level}%\n"
    return sleep_message
    
def build_message_for_mytasks():
    latest_point = getTaskLatestPoint()
    return f"合計タスク達成ポイント:{latest_point}\n"

def getTaskLatestPoint():
    gs = Google_SpreadSheet('spreadsheet-updater')
    last_row_values = gs.get_last_rows('マイホームワーク', 'デイリー集計シート')
    return last_row_values[-1]