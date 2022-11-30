#!/usr/bin/env python3

import aws_cdk as cdk

from aws_cdk_python.aws_cdk_python_stack import AwsCdkPythonStack


app = cdk.App()
AwsCdkPythonStack(app, "aws-cdk-python")

app.synth()
