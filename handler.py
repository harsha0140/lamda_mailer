import boto3 
import json
import os
from botocore.vendored import requests

def getReturn(type,body):
    binary_types = ['image/gif']
    ret = {
        "statusCode": 200,
        "headers": {
            'Content-Type': type,
            "Access-Control-Allow-Origin": '*'
        },
    }
    if type=='application/json':
        ret['body']=json.dumps(body)
    else:
        ret['body']=body
    if type in binary_types:
        ret['isBase64Encoded'] = True
    return ret

def checkCaptcha(token):
    gSecret = os.environ['gSecret']
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data = {"secret":gSecret,"response":token } )
    responsejson = response.json()
    if responsejson['success'] != True:
        return False
    else:
        return True

def lambda_handler(event, context):
    
    if event['queryStringParameters'] != None and 'ping' in event['queryStringParameters']:
        if  event['queryStringParameters']['ping']=='gif':
            
            return(getReturn('image/gif',"R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"))
            
        else:
            
            return(getReturn('application/json',{
                'success':'true',
            	'message':'Pong'
            }))
            
    errors = '';
    inputNames = {'recaptcha_token':'Recaptcha',
                  'inputName1':'Name',
                  'inputEmail2':'Email Address',
                  'inputBody4':'Message Body',
                  'user':'user'
    }
    body = json.loads(event['body'])
    for key, value in inputNames.items():
        if key not in body:
            errors += value+' not provided<br/>'
            
    if len(errors):

        return(getReturn('application/json',{
            'success':'false',
        	'message':errors
        }))

    body['message'] = os.environ['message']
    myValues = body
    
    gSecret = os.environ['gSecret'] #Enter Secret from https://www.google.com/recaptcha/ or disable captcha by removing lines 20-25
    toDomain = os.environ['toDomain'] #Enter the domain name to send the message (The portion of the email address after @)
    fromAddress = os.environ['fromAddress'] #Enter the from address for the email. This must be verified by SES
    emailSubject = os.environ['emailSubject'] #Subject line of the Email
    
    if checkCaptcha(myValues['recaptcha_token']) != True:
        
        return(getReturn('application/json',{
            'success':'false',
        	'message':'Recaptcha Failed'
        }))
        
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
    
    if 'MessageId' in sesresponse:
    
        d = {
            'success':'true',
        	'message':'Message Sent'
        }
    
    else:
        
        d = {
            'success':'false',
        	'message':'Message not sent. Internal Problem'
        }
   
    return(getReturn('application/json',d))
    
   
