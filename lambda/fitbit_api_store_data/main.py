import json
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import boto3
from boto3.dynamodb.conditions import Key


ddb = boto3.resource('dynamodb')
table = ddb.Table('fitbit-api-store')
yesterday = (datetime.now(timezone(timedelta(hours=9)))-timedelta(days=1)).strftime('%Y-%m-%d')

# DynamoDB:fitbit-api-store か Lambda:fitbit-api からfitbitのデバイス情報を取得する
def handler(event, context):
    # 有効なAPIリクエスト結果が保存されていればそれを返す
    try:
        response = get_valid_data()
        if (response is not None and len(response) > 0):
            print('from fitbit-api-store')
            return {
                'statusCode': 200,
                'body' : json.dumps(response, default=decimal_default_proc)
            }
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': f"get_valid_data:{str(e)}"
        }
    
    # APIリクエスト処理
    try:
        fitbit_json_body = call_fitbit_api_request()
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': f"call_fitbit_api_request:{str(e)}"
        }

    # APIリクエスト結果をDynamoDBへ保存する
    try:
        store_response_data(fitbit_json_body)
    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': f"store_response_data:{str(e)}"
        }
    # APIリクエスト結果を返す
    print('from fitbit-api')
    return {
         'statusCode': 200,
         'body': json.dumps(
             {
                'date': yesterday,
                'data': fitbit_json_body
            }, 
            default=decimal_default_proc)
    }

# https://qiita.com/ekzemplaro/items/5fa8900212252ab554a3
def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_valid_data():
    # dynamodbから検索
    yesterday = (datetime.now(timezone(timedelta(hours=9)))-timedelta(days=1)).strftime('%Y-%m-%d')
    response = table.query(
        KeyConditionExpression=Key('date').eq(yesterday)
    )
    if ('Items' in response.keys()):
        return response['Items']
    return None

def call_fitbit_api_request():
    fitbit_api = boto3.client("lambda")
    fitbit_res = fitbit_api.invoke(
        FunctionName='fitbit-api'
    )
    fitbit_json = json.loads(fitbit_res['Payload'].read())
    fitbit_json_body = json.loads(fitbit_json['body'])
    if (fitbit_json['statusCode'] != 200):
        raise Exception(fitbit_json_body)
    return fitbit_json_body

def store_response_data(data):
    yesterday = (datetime.now(timezone(timedelta(hours=9)))-timedelta(days=1)).strftime('%Y-%m-%d')
    item = json.loads(
        json.dumps(
        {
            'date': yesterday,
            'data': data
        }),
        parse_float = Decimal
    )
    table.put_item(Item=item)
