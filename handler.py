import boto3 
import json
import os
from botocore.vendored import requests

def lambda_handler(event, context):
    print event
    if event['queryStringParameters'] != None and 'ping' in event['queryStringParameters']:
        if  event['queryStringParameters']['ping']=='gif':
            return {
                "statusCode": 200,
                "headers": {
                    'Content-Type': 'image/gif',
                    "Access-Control-Allow-Origin": '*'
                },
                "body": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
                "isBase64Encoded": True
            }
        else:
            return {
                "statusCode": 200,
                "headers" : {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": '*',
                },
                "body": json.dumps({
                    'success':'true',
            	    'message':'Pong'
                } )
            }
    
    errors = '';
    inputNames = {'recaptcha_token':'Recaptcha',
                  'inputName1':'Name',
                  'inputEmail2':'Email Address',
                  'inputBody4':'Message Body',
                  'user':'user'
    }
    body = json.loads(event['body'])
    for key, value in inputNames.iteritems():
        if key not in body:
            errors += value+' not provided<br/>'
            
    if len(errors):
        return {
            "statusCode": 200,
            "headers" : {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                'success':'false',
        	    'message':errors
            } )
        }
        
    body['message'] = os.environ['message']
    myValues = body
    
    gSecret = os.environ['gSecret'] #Enter Secret from https://www.google.com/recaptcha/ or disable captcha by removing lines 64-78
    toDomain = os.environ['toDomain'] #Enter the domain name to send the message (The portion of the email address after @)
    fromAddress = os.environ['fromAddress'] #Enter the from address for the email. This must be verified by SES
    emailSubject = os.environ['emailSubject'] #Subject line of the Email
    
    gToken = myValues['recaptcha_token'];
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data = {"secret":gSecret,"response":gToken } )
    responsejson = response.json()
    if responsejson['success'] != True:
        return {
            "statusCode": 200,
            "headers" : {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": '*',
            },
            "body": json.dumps({
                'success':'false',
        	    'message':'Recaptcha Failed'
            } )
        }

    toAddress = myValues['user'] + '@' + toDomain
    
    client = boto3.client('ses')
    
    message = """%(message)s
    From: %(inputName1)s
    Email: %(inputEmail2)s
    Message: %(inputBody4)s""" % myValues
    
    sesresponse = client.send_email(
        Source = fromAddress,
        Destination = {
            'ToAddresses': [ toAddress ]
        },
        Message = {
            'Subject': {
                'Data': emailSubject
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        },
        ReplyToAddresses=[
            myValues['inputEmail2']
        ]
    )
    
    return {
            "statusCode": 200,
            "headers" : {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": '*',
            },
            "body": json.dumps({
                'success':'true',
        	    'message':'Message Sent'
            } )
        }
