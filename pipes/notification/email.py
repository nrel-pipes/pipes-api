import time
from datetime import datetime
import hashlib
import boto3
from botocore.exceptions import ClientError

from pipes.config.settings import settings

import logging

logger = logging.getLogger("emailpackage.base")


class Email:
    def __init__(self, sender, recipient):
        self.sender = sender
        self.recipient = recipient

    def send_email(self, subject, body, email_type="Text"):
        logging.info(
            f"{self.sender},  {self.recipient}, {subject}, {body}, {email_type}",
        )
        ses_client = boto3.client("ses", region_name=settings.AWS_REGION)

        if settings.SEND_EMAILS:
            # if 1==1:
            try:
                response = ses_client.send_email(
                    Destination={
                        "ToAddresses": [
                            self.recipient,
                        ],
                    },
                    Message={
                        "Body": {
                            email_type: {
                                "Charset": "UTF-8",
                                "Data": body,
                            },
                        },
                        "Subject": {
                            "Charset": "UTF-8",
                            "Data": subject,
                        },
                    },
                    Source=self.sender,
                )
            except ClientError as e:
                return e.response["Error"]["Message"]
            else:
                return f"Email sent! Message ID: {response['MessageId']}"
        else:
            logging.info("Emails are not being sent do to the setting SEND_EMAILS=0")
