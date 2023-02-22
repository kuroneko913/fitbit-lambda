#!/usr/bin/env python3

import aws_cdk as cdk
from FitbitCDK.fitbit_lambda_stack import FitbitLambdaStack

app = cdk.App()
FitbitLambdaStack(app, "FitbitCDK")
app.synth()
