from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration
)
from . import config

class FitbitNotifier(Construct):
    
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # lambda Layer
        lambda_layer_twitter = _lambda.LayerVersion(
            self,
            "Python38-twitter",
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8],
            code = _lambda.AssetCode('layers/python38_twitter')
        )

        lambda_layer_gspreads = _lambda.LayerVersion(
            self,
            "Python38-gspreads",
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8],
            code = _lambda.AssetCode('layers/python38_gspreads')
        )

        # lambda
        lambda_function = _lambda.Function(
            self, 'FitbitNotifierHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            function_name = 'fitbit-notifier',
            code = _lambda.Code.from_asset('lambda/fitbit_notifier'),
            handler = 'main.handler',
            layers = [lambda_layer_twitter, lambda_layer_gspreads],
            timeout = Duration.seconds(30),
        )

        # lambda:fitbit-notifierからSecretManagerを呼べるようにする
        iam.Grant.add_to_principal(
            actions=["secretsmanager:GetSecretValue"],
            grantee=lambda_function,
            resource_arns=[
                config.TWITTER_API_SECRET_MANAGER_ARN,
                config.GOOGLE_SPREAD_SHEET_API_SECRET_MANAGER_ARN 
            ]
        )

        # lambda:fitbit-notifierからlambda:fitbit-api-store-dataを呼べるようにする
        iam.Grant.add_to_principal(
            actions=['lambda:InvokeFunction'],
            grantee=lambda_function,
            resource_arns=[
                config.FITBIT_API_STORE_DATA_LAMBDA_ARN
            ]
        )

        # EventBridgeで定期実行を登録する
        rule = events.Rule(self, 'rule',
            rule_name='everyday-0020',
            schedule=events.Schedule.cron(hour="15", minute="20"),
        )
        rule.add_target(targets.LambdaFunction(lambda_function))