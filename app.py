#!/usr/bin/env python3
'''
API code for displaying generic message or echoing a custom message
'''
import boto3
import datetime
import decimal
import json
import os
import sys

import boto3
from boto3.dynamodb.conditions import Key, Attr

COUNTER_TABLE_NAME = 'stellitime-api-counters'
COUNTER_KEY = os.getenv('COUNTER_KEY', 'demo-key')

region_name = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region_name)
counter_table = dynamodb.Table(COUNTER_TABLE_NAME)


def main(argv):
    '''
    CLI interface to call GET and POST for
    '''
    if len(argv) == 1:  # pylint: disable=no-else-return
        return 0, get()
    elif len(argv) == 2:
        body = argv[1]
        try:
            body = json.loads(body)
        except:  # pylint: disable=bare-except
            return 1, {'statusCode': 400, 'body': 'malformed json input'}
        return 0, post(body)
    else:
        return 1, """Usage: %s [ '{ "message" : "some-string" } ]""" % argv[0]


def get():
    '''
    Returns generic message plus time
    '''
    today = datetime.datetime.today()
    value = get_current_counter_item(COUNTER_KEY)
    return {'statusCode': 200, 'body': {
        'counter_value': value,
        'message': 'Automation For The People',
        'timestamp': today.strftime('%m/%d/%Y:%H:%M:%S')}}


def post(request_body):
    '''
    Echos the message you sent in the body of the request in the response
    '''
    value = increment_current_counter_item(COUNTER_KEY)
    today = datetime.datetime.today()

    if 'message' not in request_body:
        return {'statusCode': 400, 'body': 'missing message in request body'}
    return {'statusCode': 200, 'body': {
        'counter_value': value,
        'message': request_body['message'],
        'timestamp': today.strftime('%m/%d/%Y:%H:%M:%S')}}


def get_current_counter_item(key):
    get_item_response = counter_table.get_item(Key={'id': key})
    # create item if not found
    if 'Item' not in get_item_response:
        item = create_new_counter_item(key, 1)
        get_item_response['Item'] = item
    return int(get_item_response['Item']['counter_value'])


def increment_current_counter_item(COUNTER_KEY):
    update_item_response = counter_table.update_item(
        TableName=COUNTER_TABLE_NAME,
        Key={'id': COUNTER_KEY},
        ExpressionAttributeNames={'#field': 'counter_value'},
        ExpressionAttributeValues={':increment': 1},
        UpdateExpression='ADD #field :increment',
        ReturnValues='UPDATED_NEW'
    )
    return int(update_item_response['Attributes']['counter_value'])


def create_new_counter_item(key, value):
    item = {
        "id": key,
        "counter_value": value
    }
    put_item_response = counter_table.put_item(Item=item)
    return item

if __name__ == '__main__':
    exit_code, response = main(sys.argv)  # pylint: disable=invalid-name
    print(json.dumps(response))
    sys.exit(exit_code)
