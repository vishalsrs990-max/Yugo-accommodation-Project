import logging
import boto3
from botocore.exceptions import ClientError


def create_bucket(bucket_name, region=None):
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
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f'  {bucket["Name"]}')


def upload_file(file_name, bucket, object_key=None):
    if object_key is None:
        object_key = file_name

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_key)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_object(region, bucket_name, object_key):
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_bucket(region, bucket_name):
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
    upload_file(args.file_name, args.bucket_name, args.object_key)


if __name__ == '__main__':
    main()
