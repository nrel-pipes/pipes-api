""" I manage notifications in PIPES. """
import os
import json
import hashlib
import time
import datetime
import logging
import logging.config
import boto3  # dynamo is lightweight so including here
from pipes_core.queues import deadline as deadlines_queue
from pipes_core.graph import Vertex
from pipes_core.graph.users import UserVertex
from pipes_core.email.base import Email
from pipes_core.common import settings


if settings.LOG_FILE_CONFIG_LOCATION:
    logging.config.fileConfig(settings.LOG_FILE_CONFIG_LOCATION)

logger = logging.getLogger("notifications.manager")
logger.setLevel(logging.DEBUG)
logger.info("Set DEBUG level to notifications logging.")


def get_deadline_notification_text(
    notification_vertex,
    notification_type,
    object_type,
    recipient_vertex,
    related_project,
    related_project_run,
    related_model,
):
    """
    I return a notification test for particular use cases.

    Parameters
    ----------
    notification_vertex : vertex representing the subject of the notification
    notification_type : the type of notification to create
    object_type : object type being addressed (ex. Project, Model)
    recipient_vertex : vertex representing the recipient of the notification
    related_project : related project information
    related_project_run : replated project run information
    related_model : related model informaiton

    """

    notification_vertex = notification_vertex.properties()
    recipient_vertex = recipient_vertex.properties()

    with open(settings.DEADLINES_HTML_LOCATION, encoding='utf-8') as file:
        html_content = file.read()

        # Replace placeholders with provided text
        html_content = html_content.replace(
            'NAME_HERE', f'{recipient_vertex["first_name"]} {
                recipient_vertex["last_name"]
            }',
        )

    if notification_type == 'Start Date Deadline' and object_type == "Project":
        subject = f'PIPES Notice: Please be aware project {notification_vertex["name"]} is due to begin.'
        notification_text = (
            f'Project {notification_vertex["name"]} is due to begin on {notification_vertex["scheduled_start"]} for project {
                related_project
            } and is scheduled to conclude on {notification_vertex["scheduled_end"]}.'
        )

    if notification_type == 'End Date Deadline' and object_type == "Project":
        subject = f'PIPES Notice: Project {notification_vertex["name"]} is due to end.'
        notification_text = (
            f'Please be aware project {notification_vertex["name"]} is due to conclude on {
                notification_vertex["scheduled_end"]
            }.'
        )

    if notification_type == 'Start Date Deadline' and object_type == "Model":
        subject = f'PIPES Notice: Modelling for {notification_vertex["display_name"]} is due to begin.'
        notification_text = (
            f'Please be aware modelling for {notification_vertex["model"]} is due to begin on {
                notification_vertex["scheduled_start"]
            } '
            f'for project {related_project} for project run {
                related_project_run
            }, and is scheduled to conclude on {notification_vertex["scheduled_end"]}.\n\n'
            'If it appears the work is not expected to complete on time please alert the PI or PM for this effort as soon as possible. '
        )
    if notification_type == 'End Date Deadline' and object_type == "Model":
        subject = f'PIPES Notice: Modelling for {notification_vertex["model"]} is due to conclude.'
        notification_text = (
            f'Please be aware modelling for {notification_vertex["model"]} is due to conclude on {
                notification_vertex["scheduled_end"]
            } '
            f'for project {related_project} for project run {related_project_run}.\n\n'
            'If it appears the work is not expected to complete on time please alert the PI or PM for this effort as soon as possible. '
        )
    if notification_type == 'Start Date Deadline' and object_type == "Project Run":
        subject = f'PIPES Notice: Project run {
            notification_vertex["name"]
        } for project {related_project} is due to begin.'
        notification_text = (
            f'Please be aware project run {notification_vertex["name"]} is due to begin on {
                notification_vertex["scheduled_start"]
            } '
            f' for project {related_project} and is scheduled to conclude on {
                notification_vertex["scheduled_end"]
            }.\n\n'
            'If it appears the work is not expected to complete on time please alert the PI or PM for this effort as soon as possible. '
        )
    if notification_type == 'End Date Deadline' and object_type == "Project Run":
        subject = f'PIPES Notice: Project run {notification_vertex["name"]} is due to conclude.'
        notification_text = (
            f'Please be aware project run {notification_vertex["name"]} is due to conclude on {
                notification_vertex["scheduled_end"]
            } '
            f'for project {related_project}.\n\n'
            'If it appears the work is not expected to complete on time please alert the PI or PM for this effort as soon as possible. '
        )
    message = html_content.replace('NOTIFICATION_HERE', notification_text)
    response_dict = dict(subject=subject, message=message)
    return response_dict


def hash_message(recipient, subject, message, medium):
    """
    I hash a notification message for a quick lookup method.

    Parameters
    ----------
    recipient : string
    subject : string
    message : string
    medium : string
    """
    mashup = recipient + subject + message + medium
    this_hash = hashlib.sha1(mashup.encode('utf-8')).hexdigest()
    return this_hash


def log_notification(sender, recipient, subject, message, medium):
    """
    I log a notification message.

    Parameters
    ----------
    sender : string
    recipient : string
    subject : string
    message : string
    medium : string
    """
    this_hash = hash_message(recipient, subject, message, medium)
    # Set up the DynamoDB resource and table name
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    table_name = settings.DYNAMO_NOTIFICATION_TABLE_NAME

    # Get a reference to the table
    table = dynamodb.Table(table_name)

    # Define the record to be inserted
    send_time = int(time.time())
    record = {
        'notice_hash': this_hash,  # Hash key
        'date_sent': send_time,  # Range key
        'recipient': recipient,
        'sender': sender,
        'subject': subject,
        'body': message,
        'medium': 'email',
        'success': 0,
        'date_sent_for_humans': datetime.datetime.utcfromtimestamp(send_time).strftime('%Y-%m-%d %H:%M:%S'),
    }

    # Insert the record into the table
    response = table.put_item(Item=record, ConditionExpression='attribute_not_exists(notice_hash)')

    # Log the response from DynamoDB
    logger.info("Email send hash lookup result:")
    logger.info(response)


# not worrying about the sender - just the message itself - when logging
def validate_notification_send(recipient, subject, message, medium):
    """
    I check to see if a notification message has already been sent.

    Parameters
    ----------
    recipient : string
    subject : string
    message : string
    medium : string
    """

    mashup = hash_message(recipient, subject, message, medium)

    # Create a DynamoDB client
    dynamodb = boto3.client('dynamodb', region_name=settings.AWS_REGION)

    # Name of the table and hash key to check
    table_name = settings.DYNAMO_NOTIFICATION_TABLE_NAME
    hash_key = mashup

    # Check if the hash key exists in the table
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'notice_hash': {'S': hash_key},
            },
        )
        # If the response is not empty, the hash key exists in the table
        if 'Item' in response:
            logger.info(f"The hash key '{hash_key}' exists in the table '{table_name} for notification'.")
            return False
        else:
            logger.info(f"The hash key '{hash_key}' does not exist in the table '{table_name} for notification'.")
            return True
    except Exception as notification_exception:
        logger.error(f"Error checking if hash key '{hash_key}' exists in the table '{
                     table_name
                     }': {str(notification_exception)}")


def send_email_if_required(from_address, to_address, subject, message, email_type):
    """
    I check to see if a notification message has already been sent.

    Parameters
    ----------
    from_address : string
    to_address : string
    subject : string
    message : string
    """
    if validate_notification_send(to_address, subject, message, 'email'):
        this_email = Email(from_address, to_address)
        this_email.send_email(subject, message, email_type)
        log_notification(from_address, to_address, subject, message, 'email')
        logger.info(f"Notification sent to {from_address} for subject {subject}.")


def process_deadline_notification_events():
    """
    I process waiting deadline notification events in related queue.
    """
    this_queue = deadlines_queue.DeadLinesQueue()
    this_queue.load_deadline_messages()

    for message in this_queue.messages:
        body = json.loads(message['Body'])

        this_v = Vertex(body['detail']['affected_identifier'], ignore_id_validation=True)
        related_project = body['detail']['relationships']['project']
        related_project_run = body['detail']['relationships']['project_run']
        related_model = body['detail']['relationships']['model']
        notification_type = body['detail']['event_type']
        object_type = body['detail']['data']['notification_object_type']
        # Handling logic for 3 vertex types:  Project, Project Run, Model
        edges_list = []
        if this_v.label() == 'Project':
            edges_list.append('Owns')
        else:
            edges_list.append('Requires')
            edges_list.append('Delegated')
        user_v_ids = this_v.get_related_users(edges_list)
        for u in user_v_ids:
            this_user = UserVertex(u)
            response_text = get_deadline_notification_text(
                this_v,
                notification_type,
                object_type,
                this_user,
                related_project,
                related_project_run,
                related_model,
            )

            # if this_user.properties()["email"].lower() == 'david.rager@nrel.gov':
            send_email_if_required(
                settings.EMAIL_NOTIFICATIONS_FROM_ADDRESS,
                this_user.properties()["email"].lower(),
                response_text['subject'],
                response_text['message'],
                'Html',
            )

            # Try and avoid the SES throttle
            time.sleep(2)
