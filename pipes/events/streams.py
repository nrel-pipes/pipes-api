import logging
import boto3
import urllib
import json

import pipes.config.settings as settings

session = boto3.Session(region_name=settings.AWS_REGION)
event_bus_client = session.client('events')
dynamo_client = session.client('dynamodb')

neptune_stream_url = settings.NEPTUNE_STREAM_ENDPOINT
dynamo_table = settings.DYNAMO_CHECKPOINT_TABLE_NAME

logger = logging.getLogger("eventspackage.neptune")


class NeptuneOp():
    """
    NeptuneOp - represents a Neptune op and commit number set for processing the stream.
    """

    def __init__(self, op_num, commit_num) -> None:
        """
        __init__ Initialize the NaptuneOp

        Parameters
        ----------
        op_num : int
            The operation number of interest
        commit_num : int
            The commit number of interest
        """

        self.op_num = int(op_num)
        self.commit_num = int(commit_num)


class NeptuneStreamReader():
    """
    NeptuneStreamReader Reads the configured neptune stream for transactions.
    """

    def __init__(self):
        self._host = neptune_stream_url
        logger.info(f'Neptune stream host: {self._host}')

    def get_trim_horizon_op(self):
        """
        get_trim_horizon_op Returns the op and commit for the trim horizon of the Neptune stream

        Returns
        -------
        NeptuneOp
            Returns NeptuneOp with the current values for reuse.
        """

        trim_horizon_url = f'{self._host}?iteratorType=TRIM_HORIZON&limit=1'
        th = urllib.request.urlopen(trim_horizon_url)
        trim_data = th.read().decode()

        th_js = json.loads(trim_data)

        if len(th_js['records']) == 0:
            return None

        for event in th_js['records']:
            th_op_num = event['eventId']['opNum']
            th_commit_num = event['eventId']['commitNum']
            trim_horizon_op = NeptuneOp(th_op_num, th_commit_num)

        return trim_horizon_op

    def get_current_checkpoint_op(self):
        """
        get_current_checkpoint_op Retrieves the last processed checkpoint op and commit from DynamoDB

        Returns
        -------
        NeptuneOp
            Returns the Dynamo information as a NeptuneOp object
        """
        response = dynamo_client.get_item(
            TableName=dynamo_table,
            Key={
                'neptune': {
                    'N': '1',
                },
            },
            ConsistentRead=True,
        )

        checkpoint_op = NeptuneOp(
            op_num=response['Item']['opNum']['N'],
            commit_num=response['Item']['commitNum']['N'],
        )
        return checkpoint_op

    def get_stream_start_op(self):
        """
        get_stream_start_op Determines if the current checkpoint op is still active in the stream.
                            If not it will use the trim horizon.

        Returns
        -------
        NeptuneOp
            The NeptuneOp to use to start reading the stream.
        """
        checkpoint_op = self.get_current_checkpoint_op()
        trim_horizon_op = self.get_trim_horizon_op()

        if trim_horizon_op.commit_num > checkpoint_op.commit_num:
            return trim_horizon_op
        else:
            return checkpoint_op

    def get_new_transactions(self, checkpoint_op):
        """
        get_new_transactions Ruturns the JSON represeting the current stream operations.

        Parameters
        ----------
        checkpoint_op : NeptuneOp
            Initial op and commit to use to begin reading the stream.

        Returns
        ----
        ---
        JSON
            The JSON returned form the Neptune stream
        """
        op_num = checkpoint_op.op_num
        commit_num = checkpoint_op.commit_num
        if op_num == 1 and commit_num == 1:
            iterator = 'AT_SEQUENCE_NUMBER'
        else:
            iterator = 'AFTER_SEQUENCE_NUMBER'
        url = f'{neptune_stream_url}?limit=100000&commitNum={commit_num}&opNum={op_num}&iteratorType={iterator}'
        logger.info(f'Stream processor URL: {url}')
        neptune_transactions_json = urllib.request.urlopen(url)
        data = neptune_transactions_json.read().decode()

        if len(data):
            transactions_json = json.loads(data)
        else:
            transactions_json = None

        return transactions_json

    def set_new_checkpoint(self, checkpoint_op, last_checkpoint_op):
        """
        set_new_checkpoint Sets the checkpoint values in DynamoDB.

        Parameters
        ----------
        checkpoint_op : NeptuneOp
            The NetuneOp representing the commit and op to set for the checkpoint.
        """
        response = dynamo_client.update_item(
            TableName=dynamo_table,
            Key={
                'neptune': {
                    'N': '1',
                },
            },

            AttributeUpdates={
                'opNum': {
                    'Value': {
                        'N': str(checkpoint_op.op_num),

                    },
                },
                'commitNum': {
                    'Value': {
                        'N': str(checkpoint_op.commit_num),
                    },
                },
            },
            Expected={
                'opNum': {
                    'Value': {
                        'N': str(last_checkpoint_op.op_num),
                    },
                },
                'commitNum': {
                    'Value': {
                        'N': str(last_checkpoint_op.commit_num),
                    },
                },
            },
        )
        return response
