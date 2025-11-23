import logging
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal


class DynamoDBDemo:

    def create_table(self, table_name, key_schema, attribute_definitions,
                     provisioned_throughput, region):

        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            print("\ncreating the table {} ...".format(table_name))
            self.table = dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput
            )

            # Wait until the table exists.
            self.table.meta.client.get_waiter('table_exists').wait(
                TableName=table_name
            )

        except ClientError as e:
            logging.error(e)
            return False
        return True

    def store_an_item(self, region, table_name, item):
        try:
            print("\nstoring the item {} in the table {} ..."
                  .format(item, table_name))
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            table.put_item(Item=item)

        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_an_item(self, region, table_name, key):
        try:
            print("\nretrieving the item with the key {} from the table {} ..."
                  .format(key, table_name))
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            response = table.get_item(Key=key)
            item = response['Item']
            print(item)

        except ClientError as e:
            logging.error(e)
            return False
        return True


def save_room_to_dynamodb(room):
    """
    Helper used by Django signals:
    takes a Room model instance and stores it in DynamoDB YugoRooms table,
    using the same style as DynamoDBDemo.store_an_item().
    """

    region = 'us-east-1'          # Learner Lab region
    table_name = 'YugoRooms'      # your DynamoDB table name

    d = DynamoDBDemo()

    item = {
        "room_id": str(room.id),
        "name": room.name,
        "location": room.location,
        "room_type": room.room_type,
        "price_per_night": Decimal(str(room.price_per_night)),
        "description": room.description or "",
        "image_url": room.s3_url or "",
        "available": room.available,
        "booking_status": "available" if room.available else "booked",
        "created_at": room.created_at.isoformat() if room.created_at else "",
    }

    d.store_an_item(region, table_name, item)


# OPTIONAL: if you still want a standalone demo like your original code,
# you can keep or adapt this main(). It will NOT run when imported by Django.

def main():
    """Simple test when running this file directly, not needed for Django."""
    region = 'us-east-1'
    table_name = 'YugoRooms'

    d = DynamoDBDemo()

    key_schema = [
        {
            "AttributeName": "room_id",
            "KeyType": "HASH"
        }
    ]

    attribute_definitions = [
        {
            "AttributeName": "room_id",
            "AttributeType": "S"
        }
    ]

    provisioned_throughput = {
        "ReadCapacityUnits": 1,
        "WriteCapacityUnits": 1
    }

    # Uncomment this if you want to create the table from code
    # d.create_table(table_name, key_schema, attribute_definitions,
    #                provisioned_throughput, region)

    # Example test item
    test_item = {
        "room_id": "test-1",
        "name": "Test Room",
        "location": "Dublin",
        "room_type": "classic",
        "price_per_night": 50,
        "description": "Test description",
        "image_url": "",
        "available": True,
        "booking_status": "available",
        "created_at": "",
    }

    d.store_an_item(region, table_name, test_item)

    key_info = {
        "room_id": "test-1"
    }
    d.get_an_item(region, table_name, key_info)


if __name__ == '__main__':
    main()