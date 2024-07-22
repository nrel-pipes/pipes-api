import re
from typing import Dict, List
import datetime
import json
import logging
import logging.config
import boto3

from pipes.config.settings import settings

if settings.LOG_FILE_CONFIG_LOCATION:
    logging.config.fileConfig(settings.LOG_FILE_CONFIG_LOCATION)

logger = logging.getLogger("eventspackage.base")

client = boto3.client("events", region_name=settings.AWS_REGION)
dynamodb = boto3.client("dynamodb", region_name=settings.AWS_REGION)

# Name of the table and hash key to check
event_tracker_table_name = settings.DYNAMO_STATE_BASED_EVENTS_TABLE_NAME


class Event:
    """Event Class for Sending Events"""

    @staticmethod
    def create_activity_type(activity):
        """
        Creates new event in the event bus

        Parameters
        ----------
        activity :
            The activity being created
        """

        this_event_bus_event = dict(
            name=activity["name"],
            affected_identifier=activity["affected_identifier"],
            event_time=str(activity["event_time"]),
            event_type=activity["event_type"],
            source=dict(
                identifier=activity["source_identitifer"],
                system=activity["source_system"],
                type=activity["source_type"],
            ),
            relationships=dict(
                project_id=activity["relationships_project_id"],
                project=activity["relationships_project"],
                project_run_id=activity["relationships_project_run_id"],
                project_run=activity["relationships_project_run"],
                model_id=activity["relationships_model_id"],
                model=activity["relationships_model"],
                model_run_id=activity["relationships_model_run_id"],
                model_run=activity["relationships_model_run"],
                qa=activity["relationships_qa_run"],
                qa_id=activity["relationships_qa_run_id"],
                transform=activity["relationships_transform_run"],
                transform_id=activity["relationships_transform_run_id"],
                creator=activity["relationships_creator"],
                creator_id=activity["relationships_creator_id"],
            ),
            data=activity["data"],
        )

        response = client.put_events(
            Entries=[
                {
                    "Time": str(datetime.datetime.now()),
                    "Source": this_event_bus_event["source"]["identifier"],
                    "Resources": [
                        settings.NEPTUNE_HOST,
                    ],
                    "DetailType": "C2C Neptune Sourced Event",
                    "Detail": json.dumps(this_event_bus_event),
                    "EventBusName": settings.EVENT_BUS_NAME,
                },
            ],
        )

        logger.info(f"Activity logged to event bus: " + json.dumps(response))
        return dict(EventId=response["Entries"][0]["EventId"])

    @staticmethod
    def create_exception_type(pipes_exception):
        """
        Creates new event in the event bus

        Parameters
        ----------
        props : dict
            Additional properties to add to load the event per Event schema.
        """

        # client = boto3.client("events", region_name=settings.AWS_REGION)
        logger.info(pipes_exception)
        response = client.put_events(
            Entries=[
                {
                    "Time": str(datetime.datetime.now()),
                    "Source": pipes_exception["source"]["identifier"],
                    "DetailType": "Exception Event",
                    "Detail": json.dumps(pipes_exception),
                    "EventBusName": settings.EVENT_BUS_NAME,
                },
            ],
        )

        # pprint(response)

        logger.info(response)
        return dict(EventId=response["Entries"][0]["EventId"])

    @staticmethod
    def create_deadline_type(pipes_deadline):
        """
        Creates new deadline event in the event bus

        Parameters
        ----------
        props : dict
            Additional properties to add to load the event per Event schema.
        """

        logger.info(pipes_deadline)
        response = client.put_events(
            Entries=[
                {
                    "Time": str(datetime.datetime.now()),
                    "Source": pipes_deadline["source"]["identifier"],
                    "DetailType": "Deadline Event",
                    "Detail": json.dumps(pipes_deadline),
                    "EventBusName": settings.EVENT_BUS_NAME,
                },
            ],
        )

        logger.info(response)
        return dict(EventId=response["Entries"][0]["EventId"])

    @classmethod
    def create(cls, type="activity", **props):

        if type == "activity":
            response = cls.create_activity_type(props)
        elif type == "deadline":
            response = cls.create_deadline_type(props)
        elif type == "exception":
            response = cls.create_exception_type(props)
        return response
