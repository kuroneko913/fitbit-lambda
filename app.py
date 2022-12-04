#!/usr/bin/env python3

import aws_cdk as cdk
from FitbitCDK.api_stack import ApiStack

app = cdk.App()
ApiStack(app, "FitbitCDK")
app.synth()
