import os
import json
import boto3
if os.getenv("AWS_SAM_LOCAL"):
    votes_table = boto3.resource(
        'dynamodb',
        endpoint_url="http://docker.for.mac.localhost:8000/"
    ).Table("spaces-tabs-votes")
else:
    votes_table = boto3.resource('dynamodb').Table(os.getenv('TABLE_NAME'))



def lambda_handler(event, context):
    print(event)
    if event['httpMethod'] == 'GET':
        resp = votes_table.scan()
        return {'body': json.dumps({item['id']: int(item['votes']) for item in resp['Items']})}
    elif event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
        except:
            return {'statusCode': 400, 'body': 'malformed json input'}
        if 'vote' not in body:
            return {'statusCode': 400, 'body': 'missing vote in request body'}
        if body['vote'] not in ['spaces', 'tabs']:
            return {'statusCode': 400, 'body': 'vote value must be "spaces" or "tabs"'}

        resp = votes_table.update_item(
            Key={'id': body['vote']},
            UpdateExpression='ADD votes :incr',
            ExpressionAttributeValues={':incr': 1},
            ReturnValues='ALL_NEW'
        )
        return {'body': "{} now has {} votes".format(body['vote'], resp['Attributes']['votes'])}
