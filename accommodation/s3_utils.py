# source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
# some of the code included here is taken or adapted from the Amazon S3 examples available on Boto3 documentation

import logging
import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created by default in the region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
    except ClientError as e:
        logging.error(e)
        return False
    return True


def list_buckets():
    """List existing S3 buckets"""
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()

    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')


def upload_file(file_name, bucket, object_key=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload (local path)
    :param bucket: Bucket to upload to
    :param object_key: S3 object key. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 key was not specified, use file_name
    if object_key is None:
        object_key = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_key)
        """
        Example with ExtraArgs to set ACL 'public-read':
        s3_client.upload_file(
            file_name,
            bucket,
            object_key,
            ExtraArgs={'ACL': 'public-read'}
        )
        """
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_object(region, bucket_name, object_key):
    """Delete a given object from an S3 bucket"""
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_bucket(region, bucket_name):
    """Delete an S3 bucket

    NOTE: The bucket must be empty.
    """
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="S3 demo script")
    parser.add_argument('bucket_name', help='S3 bucket name')
    parser.add_argument('file_name', help='Local file to upload')
    parser.add_argument('object_key', help='Object key in S3')

    region = 'us-east-1'

    args = parser.parse_args()
    create_bucket(args.bucket_name)
    # list_buckets()
    upload_file(args.file_name, args.bucket_name, args.object_key)
    # delete_object(region, args.bucket_name, args.object_key)
    # delete_bucket(region, args.bucket_name)


if __name__ == '__main__':
    main()
