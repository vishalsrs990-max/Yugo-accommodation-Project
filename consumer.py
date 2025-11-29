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
            
            session = boto3.session.Session()
            sqs_client = session.client('sqs')
            
            response = sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
            
            print('\n\t\t<=== requesting messages from the queue...\n')
            
            response = sqs_client.receive_message(QueueUrl=queue_url,
                            MaxNumberOfMessages=1, 
                            VisibilityTimeout=10, 
                        )
            print("\t\t\t<=== consumer received the response: {}".format(response)) 
          
            print('\n')
          
            messages = response.get('Messages')
            if messages != None:
                
                messages = response['Messages'] 
                
                current_message = messages[0] 
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
