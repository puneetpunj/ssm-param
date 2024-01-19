import json
import boto3
import urllib3

http = urllib3.PoolManager()


def send(event, context, response_status, response_data, physical_resource_id):
  response_url = event['ResponseURL']

  response_body = {
      'Status': response_status,
      'Reason': f'See the details in CloudWatch Log Stream: {context.log_stream_name}',
      'PhysicalResourceId': physical_resource_id,
      'StackId': event['StackId'],
      'RequestId': event['RequestId'],
      'LogicalResourceId': event['LogicalResourceId'],
      'NoEcho': False,
      'Data': response_data
  }

  json_response_body = json.dumps(response_body)

  headers = {
      'content-type': '',
      'content-length': str(len(json_response_body))
  }

  try:
      response = http.request('PUT',response_url, body=json_response_body, headers=headers)
      print(f"Status code: {response.status}")
  except Exception as e:
      print(f"send(..) failed executing requests.put(..): {e}")

def handler(event, context):
  print(event)

  ssm = boto3.client('ssm')
  props = event['ResourceProperties']

  split_stack_arn = event['StackId'].split(':')
  region = split_stack_arn[3]
  account_id = split_stack_arn[4]

  stack_name = split_stack_arn[5].split("/")[1]
  param_name = props.get('Name', f'cfn-{stack_name}-{event["LogicalResourceId"]}')
  param_arn = f'arn:aws:ssm:{region}:{account_id}:parameter{param_name}'

  try:
      params = {
              'Name': param_name,
              'Type': props['Type'],
              'Value': props['Value'],
              'Overwrite': False
          }

      if 'Description' in props:
              params['Description'] = props['Description']
      if 'KeyId' in props:
              params['KeyId'] = props['KeyId']

      if event['RequestType'] == 'Create':                      
          ssm.put_parameter(**params)
          send(event, context, 'SUCCESS', {'Arn': param_arn, 'Name': param_name}, param_arn)

      elif event['RequestType'] == 'Update':
          params['Overwrite'] = True
          ssm.put_parameter(**params)
          send(event, context, 'SUCCESS', {'Arn': param_arn, 'Name': param_name}, param_arn)
      
      elif event['RequestType'] == 'Delete':
          ssm.delete_parameter(Name=param_name)
          send(event, context, 'SUCCESS', {'Arn': param_arn, 'Name': param_name}, param_arn)

  except Exception as err:
      print(err)
      send(event, context, 'FAILED', {'Arn': param_arn, 'Name': param_name}, param_arn)