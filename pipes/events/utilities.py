import os
import logging
import logging.config
import hashlib
from datetime import datetime
from pipes.events import streams as neptune_stream
from pipes_core.graph.base import Vertex
from pipes_core.schemas.event import EventSchema
from pipes_core.schemas.exception import ExceptionSchema
from pipes_core.events.base import Event

from pipes.config.settings import settings
from pipes_core.managers.graph import GraphManager

if settings.LOG_FILE_CONFIG_LOCATION:
    logging.config.fileConfig(settings.LOG_FILE_CONFIG_LOCATION)

logger = logging.getLogger("events.manager")


def add_related_verticies_on_event(this_event, this_vertex, this_label):
    if this_label not in ["User", "Project"]:
        related_project = this_vertex.get_related_project()
    else:
        related_project = None
    if this_label not in ["User", "Project"]:
        related_project_run = this_vertex.get_related_project_run()
        related_model = this_vertex.get_related_model()
    else:
        related_project_run = None
        related_model = None
    if this_label not in ["Project Run", "Project", "Model", "User"]:
        related_model_run = this_vertex.get_related_model_run()
    else:
        related_model_run = None

    if this_label != 'User':
        related_user = this_vertex.get_source_user()
    else:
        related_user = None

    if related_project is not None:
        this_event['relationships_project_id'] = related_project.id
        this_event['relationships_project'] = related_project.properties()['name']
    else:
        this_event['relationships_project_id'] = ''
        this_event['relationships_project'] = ''
    if related_project_run is not None:
        this_event['relationships_project_run_id'] = related_project_run.id
        this_event['relationships_project_run'] = related_project_run.properties()['name']
    else:
        this_event['relationships_project_run_id'] = ''
        this_event['relationships_project_run'] = ''
    if related_model is not None:
        this_event['relationships_model_id'] = related_model.id
        this_event['relationships_model'] = related_model.properties()['model']
    else:
        this_event['relationships_model_id'] = ''
        this_event['relationships_model'] = ''
    if related_model_run is not None:
        this_event['relationships_model_run_id'] = related_model_run.id
        this_event['relationships_model_run'] = f"{related_model_run.properties()['name']} {
            related_model_run.properties()['version']
        }"
    else:
        this_event['relationships_model_run_id'] = ''
        this_event['relationships_model_run'] = ''
    if related_user is not None:
        this_event['relationships_creator_id'] = related_user.id
        this_event['relationships_creator'] = related_user.properties()['username']
    else:
        this_event['relationships_creator'] = ''
        this_event['relationships_creator_id'] = ''

    return this_event


def process_neptune_events():
    """
    Process the neptune stream.
    """
    reader = neptune_stream.NeptuneStreamReader()
    checkpoint_op = reader.get_stream_start_op()
    dynamo_op = reader.get_current_checkpoint_op()
    logger.info(f'Processing from opNum: {checkpoint_op.op_num}, commitNum: {checkpoint_op.commit_num}')
    transactions = reader.get_new_transactions(checkpoint_op)

    previous_op = dynamo_op
    count = 0
    logger.info(f"{len(transactions['records'])} records to process:")
    for t in transactions['records']:
        this_op_num = t['eventId']['opNum']
        this_commit_num = t['eventId']['commitNum']
        this_id = t['data']['id']
        this_type = t['data']['type']
        this_op = t['op']
        this_key = t['data']['key']
        this_value = t['data']['value']['value']
        this_timestamp = t['commitTimestamp']

        # TODO: Add capability for delete logic (may need API implementation to get full information on deleted objects).
        if not (this_value == "Activity" and this_op == 'ADD'):

            logger.info(f'Processing op: {this_op}, type: {this_type}, value: {this_value}, id: {this_id}')

            # Identify new vertex additions by matching on the vertex lable
            if this_op == 'ADD' and this_type == 'vl':
                count = count + 1

                try:
                    logger.info(f"Handling activity: {this_id}")
                    this_vertex = Vertex(id=this_id, ignore_id_validation=True)
                    this_label = this_vertex.label()

                    if this_label not in ["User", "Project"]:
                        related_project = this_vertex.get_related_project()
                    else:
                        related_project = None
                    if this_label not in ["User", "Project"]:
                        related_project_run = this_vertex.get_related_project_run()
                        related_model = this_vertex.get_related_model()
                    else:
                        related_project_run = None
                        related_model = None
                    if this_label not in ["Project Run", "Project", "Model", "User"]:
                        related_model_run = this_vertex.get_related_model_run()
                    else:
                        related_model_run = None

                    if this_label != 'User':
                        related_user = this_vertex.get_source_user()
                    else:
                        related_user = None

                    this_event = {}
                    this_event['name'] = f'{this_label} created'
                    this_event['affected_identifier'] = this_vertex.id
                    this_event['event_time'] = datetime.now()
                    this_event['event_type'] = 'Neptune Object Creation'
                    this_event['source_identitifer'] = settings.NEPTUNE_HOST
                    this_event['source_system'] = 'Neptune'
                    this_event['source_type'] = 'Graph DB'

                    if related_project is not None:
                        this_event['relationships_project_id'] = related_project.id
                        this_event['relationships_project'] = related_project.properties()['name']
                    else:
                        this_event['relationships_project_id'] = ''
                        this_event['relationships_project'] = ''
                    if related_project_run is not None:
                        this_event['relationships_project_run_id'] = related_project_run.id
                        this_event['relationships_project_run'] = related_project_run.properties()['name']
                    else:
                        this_event['relationships_project_run_id'] = ''
                        this_event['relationships_project_run'] = ''
                    if related_model is not None:
                        this_event['relationships_model_id'] = related_model.id
                        this_event['relationships_model'] = related_model.properties()['model']
                    else:
                        this_event['relationships_model_id'] = ''
                        this_event['relationships_model'] = ''
                    if related_model_run is not None:
                        this_event['relationships_model_run_id'] = related_model_run.id
                        this_event['relationships_model_run'] = f"{related_model_run.properties()['name']} {
                            related_model_run.properties()['version']
                        }"
                    else:
                        this_event['relationships_model_run_id'] = ''
                        this_event['relationships_model_run'] = ''
                    if related_user is not None:
                        this_event['relationships_creator_id'] = related_user.id
                        this_event['relationships_creator'] = related_user.properties()['username']
                    else:
                        this_event['relationships_creator'] = ''
                        this_event['relationships_creator_id'] = ''
                    this_event['data'] = this_vertex.properties()
                    valid_data = EventSchema.validate(this_event).dict()
                    Event.create(**valid_data)
                    logger.info('Activity created.')
                except Exception as e:
                    logger.exception(f'Caught exception: {str(e)}')

        last_op = neptune_stream.NeptuneOp(commit_num=this_commit_num, op_num=this_op_num)
        reader.set_new_checkpoint(last_op, previous_op)
        previous_op = last_op

    logger.info(f'Processed {count} events.')


def hash_state_event(name, type, source_identifier, affected_identifier):
    """
    I hash a notification message for a quick lookup method.

    Parameters
    ----------
    name : string
    type : string
    source_identifier : string
    affected_identifier : string
    """
    mashup = name + type + source_identifier + affected_identifier
    this_hash = hashlib.sha1(mashup.encode('utf-8')).hexdigest()
    return this_hash


'''
TODO:  Shore this up for new events - commenting code as function is not yet used and has undefined var
def log_state_event_creation(name, type, source_identifier, affected_identifier):
    mashup = hash_state_event(name, type, source_identifier, affected_identifier)
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
    table_name = settings.DYNAMO_STATE_BASED_EVENTS_TABLE_NAME

    # Get a reference to the table
    table = dynamodb.Table(table_name)

    # Define the record to be inserted
    send_time = int(time.time())
    record = {
        'event_hash': this_hash,  # Hash key
        'date_sent': send_time,  # Range key
        'name': name,
        'type': type,
        'source_identifier': source_identifier,
        'affected_identifier': affected_identifier,
        'date_sent_for_humans': datetime.datetime.utcfromtimestamp(send_time).strftime('%Y-%m-%d %H:%M:%S')
    }

    # Insert the record into the table
    response = table.put_item(Item=record, ConditionExpression='attribute_not_exists(notice_hash)')

    # Print the response from DynamoDB
    logger.info("Email send hash lookup result:")
    logger.info(response)
'''


def issue_deadline_events():
    identified_scheduled_start_items = GraphManager.get_scheduled_start_events_for_period(
        settings.STANDARD_FORWARD_DAYS_TO_NOTIFY,
    )
    logger.info("Issuing starting deadline events:")
    for v in identified_scheduled_start_items:
        logger.info(f"Handling deadline on vertex: {v.id}")
        this_vertex = Vertex(id=v.id, ignore_id_validation=True)
        this_label = this_vertex.label()
        this_event = dict()
        this_event['name'] = f'{this_label}: {this_vertex.id} start date deadline'
        this_event['affected_identifier'] = this_vertex.id
        this_event['event_time'] = datetime.now()
        this_event['event_type'] = 'Start Date Deadline'
        this_event['source_identitifer'] = 'PIPES Scheduled Task'
        this_event['source_system'] = 'PIPES Core'
        this_event['source_type'] = 'scheduled task'

        deadline_data = dict(
            scheduled_end_date=this_vertex.properties()['scheduled_end'],
            scheduled_start_date=this_vertex.properties()['scheduled_start'],
            notification_object_type=this_label,
        )

        this_event['data'] = deadline_data

        this_event = add_related_verticies_on_event(this_event, this_vertex, this_label)
        valid_data = EventSchema.validate(this_event).dict()

        Event.create(**valid_data)

        logger.info('Deadline event created.')

    identified_scheduled_end_items = GraphManager.get_scheduled_end_events_for_period(
        settings.STANDARD_FORWARD_DAYS_TO_NOTIFY,
    )
    logger.info("Issuing stopping deadline events:")

    for v in identified_scheduled_end_items:
        logger.info(f"Handling deadline for vertex ID: {v.id}")
        this_vertex = Vertex(id=v.id, ignore_id_validation=True)
        this_label = this_vertex.label()
        this_event = dict()
        this_event['name'] = f'{this_label}: {this_vertex.id} end date deadline'
        this_event['affected_identifier'] = this_vertex.id
        this_event['event_time'] = datetime.now()
        this_event['event_type'] = 'End Date Deadline'
        this_event['source_identitifer'] = 'PIPES Scheduled Task'
        this_event['source_system'] = 'PIPES Core'
        this_event['source_type'] = 'scheduled task'

        deadline_data = dict(
            scheduled_end_date=this_vertex.properties()['scheduled_end'],
            scheduled_start_date=this_vertex.properties()['scheduled_start'],
            notification_object_type=this_label,
        )

        this_event['data'] = deadline_data

        this_event = add_related_verticies_on_event(this_event, this_vertex, this_label)
        valid_data = EventSchema.validate(this_event).dict()
        Event.create(**valid_data)
        logger.info('Deadline event created.')


def log_exception(exception_data):
    valid_data = ExceptionSchema.validate(exception_data).dict()
    valid_data['event_time'] = str(valid_data['event_time'])
    response = Event.create(type='exception', **valid_data)
    logger.exception(exception_data)
    logger.info('Exception Event created.')
    return response
