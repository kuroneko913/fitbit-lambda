from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration
)
from . import config

class FitbitApi(Construct):
    
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # FitbitAPIを叩くためのLambda
        # lambda Layer
        lambda_layer_fitbit = _lambda.LayerVersion(
            self,
            "Python38-fitbit",
            compatible_runtimes = [_lambda.Runtime.PYTHON_3_8],
            code = _lambda.AssetCode('layers/python38_fitbit')
        )

        # lambda
        lambda_function = _lambda.Function(
            self, 'FitbitApiHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            function_name = 'fitbit-api',
            code = _lambda.Code.from_asset('lambda/fitbit_api'),
            handler = 'main.handler',
            layers = [lambda_layer_fitbit],
            timeout = Duration.seconds(30),
        )

        # lambda:fitbit-apiからSecretManagerを呼べるようにする
        iam.Grant.add_to_principal(
            actions=['secretsmanager:*'],
            grantee=lambda_function,
            resource_arns=[config.FITBIT_API_SECRET_MANAGER_ARN]
        )