from botocore.exceptions import ClientError
import base64
import boto3
import json

class SecretManager:
    
    def __init__(self, secret_name, region_name = 'ap-northeast-1'):
        self.region_name = region_name
        self.secret_name = secret_name
        self.client = self.get_client()

    # secret manager client
    def get_client(self):
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name = 'secretsmanager',
            region_name = self.region_name
        )
        return client
    
    # secret manager トークン更新
    def update(self, update_json):
        try:
            return self.client.update_secret(
                SecretId = self.secret_name, 
                SecretString = json.dumps(update_json)
            )
        except ClientError as e:
            print(e)
    
    # Secrets Managerのサンプルコードを参考に
    def get(self):
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.secret_name
            )   
        except ClientError as e:
            print(e)
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return json.loads(secret)
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)
