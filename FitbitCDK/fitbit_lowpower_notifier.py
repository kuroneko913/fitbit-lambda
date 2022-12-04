from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration
)
from . import config

class FitbitLowpowerNotifier(Construct):
    
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # lambda Layer
        lambda_layer_googleapiclient = _lambda.LayerVersion(
            self,
            "Python38-googleapiclient",
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8],
            code = _lambda.AssetCode('layers/python38_googleapiclient')
        )

        # lambda
        lambda_function = _lambda.Function(
            self, 'FitbitNotifierHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            function_name = 'fitbit-lowpower-notifier',
            code = _lambda.Code.from_asset('lambda/fitbit_lowpower_notifier'),
            handler = 'main.handler',
            layers = [lambda_layer_googleapiclient],
            timeout = Duration.seconds(30),
        )

        # lambda:fitbit-lowpower-notifierからSecretManagerを呼べるようにする
        iam.Grant.add_to_principal(
            actions=["secretsmanager:GetSecretValue"],
            grantee=lambda_function,
            resource_arns=[
                config.LINE_NOTIFIER_SECRET_MANAGER_ARN,
                config.GOOGLE_SPREAD_SHEET_API_SECRET_MANAGER_ARN 
            ]
        )

        # lambda:fitbit-notifierからlambda:fitbit-apiを呼べるようにする
        iam.Grant.add_to_principal(
            actions=['lambda:InvokeFunction'],
            grantee=lambda_function,
            resource_arns=[
                config.FITBIT_API_CALLER_ARN
            ]
        )

        # EventBridgeで定期実行を登録する
        rule = events.Rule(self, 'rule',
            rule_name='6hour-per-exec',
            schedule=events.Schedule.rate(Duration.hours(6))
        )
        rule.add_target(targets.LambdaFunction(lambda_function))