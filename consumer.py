'''
    SQS demo
    @author a. e. chis
'''

import logging
import boto3
from botocore.exceptions import ClientError

''' a simple class to demonstrate how to retrieve one or more messages from a given queue'''

class Consumer:
    def consume_message(self, queue_name):
        
        try:
            # Create a session and use it to make our client
            session = boto3.session.Session()
            sqs_client = session.client('sqs')
            #sqs_client = boto3.client('sqs')
            # retrive the URL of an existing Amazon SQS queue
            response = sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
            
            print('\n\t\t<=== requesting messages from the queue...\n')
            # receive a message from the specified queue
            response = sqs_client.receive_message(QueueUrl=queue_url,
                            MaxNumberOfMessages=1, # a number between 1 and 10
                            VisibilityTimeout=10, #default 30 seconds
                        )
            print("\t\t\t<=== consumer received the response: {}".format(response)) # this is not really needed
          
            print('\n')
          
            messages = response.get('Messages')
            if messages != None:
                # consume the message(s) according to the specific processing you'd like to perform
                messages = response['Messages'] # a list with all the messages
                # in this example we only retrieved one message, so the list contains only one element
                current_message = messages[0] # retrieve the message from the list
                print("\t\t\t<=== consumer has the message: {}".format(current_message))
                print("\n\t\t\t<=== The message I'm proccessing is:\n {}".format(current_message['Body']))
            
          
                ''' once the message has been processed, ensure that the message is deleted from the queue.
                    delete the specified message from the specified queue. 
                    the message to be deleted is identified by the message ReceiptHandle
                '''
                receipt_handle = current_message['ReceiptHandle']
                response = sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                print("\t\t\t<=== sqs_client deleted the message, and the response is {}".format(response))
            else:
                print('\t\t\tNo message has been received, you should repeat the request...')
                
            
        except ClientError as e:
            logging.error(e)
            return False
        return True
