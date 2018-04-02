# AWS SES Sender for daily status and errors
import boto3

from botocore.exceptions import ClientError

client = boto3.client('ses')

class Mail():
    def __init__(self, subject, html, content, recipients, sender):
        self.recipients = recipients
        self.sender = sender
        self.content = content
        self.html = html
        self.subject = subject
        self.charset = 'UTF-8'

    def destination(self):
        return { "ToAddresses": self.recipients }

    def message(self):
        return {
            "Body": {
                "Text": {
                    "Charset": self.charset,
                    "Data": self.content
                }
            },
            "Subject": {
                "Charset": self.charset,
                "Data": self.subject
            }
        }

    def __call__(self):
        try:
            resp = client.send_email(
                    Destination = self.destination(),
                    Message = self.message(),
                    Source = self.sender
                    )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(resp['ResponseMetadata']['RequestId'])

