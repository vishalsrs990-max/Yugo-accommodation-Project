import json
import boto3
from django.conf import settings

AWS_REGION = getattr(settings, "AWS_REGION_NAME", "us-east-1")
LAMBDA_FUNCTION_NAME = getattr(settings, "BOOKING_LAMBDA_NAME", "yugo-booking")

lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def invoke_booking_lambda(booking):
    payload = {
        "booking_id": booking.id,
        "user_email": booking.user_email,
        "room_name": booking.room.name,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "total_price": str(booking.total_price),
    }

    lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )
