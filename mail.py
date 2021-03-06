# AWS SES Sender for daily status and errors
import boto3
import time

from botocore.exceptions import ClientError
from utils import get_logger

client = boto3.client('ses')
logger = get_logger(__name__)

class Mail():
    first = True
    ctime = time.time()
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
        if not self.first and (time.time() - self.ctime) < 1800:
                logger.info("Rate limiting {} Seconds until next message".format(int((time.time() - self.ctime) - 1800)))
                return
        Mail.ctime = time.time()
        Mail.first = False
        try:
            resp = client.send_email(
                    Destination = self.destination(),
                    Message = self.message(),
                    Source = self.sender
                    )
        except ClientError as e:
            logger.info(e.response['Error']['Message'])
        else:
            logger.info(resp['ResponseMetadata']['RequestId'])

