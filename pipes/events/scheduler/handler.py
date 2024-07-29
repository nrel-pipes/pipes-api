"""
An AWS Lambda function to grab scheduled jobs
and submit to EventBus as events
"""

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def schedule_pipes_jobs(event, context):
    """Grab scheduled jobs from PIPES and push to Event Bus"""
    logger.info("Searching scheduled jobs in PIPES...")
    logger.info(event)

    return {
        "source": "test",
        "status_code": 200,
        "message": "successful run",
    }
