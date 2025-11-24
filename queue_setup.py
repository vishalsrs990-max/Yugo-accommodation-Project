'''
    SQS demo
    @author a. e. chis
'''
import logging
import boto3
from botocore.exceptions import ClientError

''' a simple class to demonstrate how to create and delete a queue'''

class MyMessageQueue:

    
    def create_queue(self, queue_name):
        
        try:
            sqs_client = boto3.client('sqs')
            print('\ncreating the queue {}...'.format(queue_name))
            response = sqs_client.create_queue(QueueName=queue_name)
            print(response) # this is not really needed
        
        except ClientError as e:
            logging.error(e)
            return False
        return True
        
    
    def delete_queue(self, queue_name):
        
        try:
            sqs_client = boto3.client('sqs')
            # retrive the URL of an existing Amazon SQS queue
            response = sqs_client.get_queue_url(QueueName=queue_name)
            print(response) # this is not really needed
            queue_url = response['QueueUrl']
            response = sqs_client.delete_queue(QueueUrl=queue_url)
        
            
        except ClientError as e:
            logging.error(e)
            return False
        return True
