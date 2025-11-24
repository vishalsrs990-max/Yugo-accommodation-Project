'''
    SQS demo
    @author a. e. chis
'''

import logging
import boto3
from botocore.exceptions import ClientError

''' a simple class to demonstrate how to deliver a message to a given queue'''

class Producer:
    
   
    def send_message(self, queue_name, message):
        
        try:
            # Create a session and use it to make our client
            session = boto3.session.Session()
            sqs_client = session.client('sqs')
            # sqs_client = boto3.client('sqs')
            # retrive the URL of an existing Amazon SQS queue
            response = sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
            
            print('\n==>message to send to the queue {} ...\n'.format(message))
            response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=message)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True
