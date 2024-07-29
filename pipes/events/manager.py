import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EventManager:

    def get_scheduled_jobs(self):

        print("Processing PIPES test events...")

        return {
            "name": "module-run",
            "data": {
                "key": "value",
            },
        }
