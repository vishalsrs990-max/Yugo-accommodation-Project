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
    region = 'us-east-1'
    table_name = 'YugoRooms'

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


def main():
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
