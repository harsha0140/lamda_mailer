import boto3 
import requests 

# This script allows a static website hosted on S3 or Cloudfront to Send an Email through AWS API Gateway and AWS Lamda
# This script can also prevent spam by using Google Recaptcha
# This script takes a json-encoded string with the following keys:
#   name : The name of the person the message is from
#   email : The email address of the person the message is from
#   phone : The phone number of the person the message is from
#   message : The email body
#   user : The destination email user (The portion before @)
#   recaptcha_token : The token returned from Google Recaptcha

def lambda_handler(event, context):
    
    gSecret = '' #Enter Secret from https://www.google.com/recaptcha/ or disable captcha by removing lines 20-25
    toDomain = '' #Enter the domain name to send the message (The portion of the email address after @)
    fromAddress = '' #Enter the from address for the email. This must be verified by SES
    emailSubject = '' #Subject line of the Email
    
    gToken = event.pop('recaptcha_token',False);
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data = {"secret":gSecret,"response":gToken } )

    responsejson = response.json()
    if responsejson['success'] != True:
        return responsejson
    
    toAddress = event.pop('user',False) + '@' + toDomain
    
    client = boto3.client('ses')
    
    message = """The following message was sent from the operation graduate website
    From: %(name)s
    Email: %(email)s
    Phone: %(phone)s
    Message: %(message)s""" % event
    
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
            event['email']
        ]
    )
    
    return {
        'success':'true',
	'mail':'sent'
    } 
