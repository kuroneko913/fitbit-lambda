from .fitbit_api_caller import FitbitApiCaller
from .fitbit_api import FitbitApi
from .fitbit_notifier import FitbitNotifier
from .fitbit_lowpower_notifier import FitbitLowpowerNotifier
from constructs import Construct
from aws_cdk import (
    Stack
)
class FitbitLambdaStack(Stack):
    def __init__(self, scope:Construct, id:str, **kwargs):
        super().__init__(scope, id, **kwargs)

        FitbitApi(self, 'FitbitApi')
        FitbitApiCaller(self, 'FitbitApiCaller')
        FitbitNotifier(self, 'FitbitNotifier')
        FitbitLowpowerNotifier(self, 'FitbitLowpowerNotifier')
