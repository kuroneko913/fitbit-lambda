from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Duration
)
from . import config

class FitbitApiCaller(Construct):
    
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # APIの実行結果を保存するテーブル
        table = ddb.Table(
            self, 'fitbit-api-store',
            table_name = 'fitbit-api-store',
            partition_key = { 'name': 'date', 'type': ddb.AttributeType.STRING }
        )

        # APIGatewayで呼ばれるlambda
        lambda_function = _lambda.Function(
            self, 'StoreDataHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            function_name = 'fitbit-api-store-data',
            code = _lambda.Code.from_asset('lambda/fitbit_api_store_data'),
            handler = 'main.handler',
            timeout = Duration.seconds(30),
        )

        lambda_function_call_api = _lambda.Function.from_function_arn(
            self, 'call_api',
            function_arn=config.FITBIT_API_CALLER_ARN,
        )

        # lambda:fitbit-apiをlambda:FitbitApiStoreDataから呼べるように権限を付与
        iam.Grant.add_to_principal(
            actions=['lambda:InvokeFunction'],
            grantee=lambda_function,
            resource_arns=[config.FITBIT_API_CALLER_ARN]
        )

        # 書き込み権限を付与する
        table.grant_read_write_data(lambda_function)

        # apiGatewayを用意する
        api = apigateway.LambdaRestApi(self, 'fitbit-api',
            handler=lambda_function,
            proxy=False,
            api_key_source_type=apigateway.ApiKeySourceType.HEADER,
            deploy_options=apigateway.StageOptions(stage_name="production")
        )

        # 不必要にアクセスされないようにx-api-keyを指定しないとアクセスできないようにしておく
        # APIキーの作成
        api_key = api.add_api_key('APIKey', api_key_name = config.API_KEY_NAME)
        plan = api.add_usage_plan('ForAPIKey', name=config.USAGE_PLAN_NAME)
        plan.add_api_key(api_key)
        plan.add_api_stage(stage=api.deployment_stage)

        # エンドポイントの指定
        deviceinfo = api.root.add_resource('deviceinfo')
        deviceinfo.add_method('GET', api_key_required = True)




