import json
import boto3
from django.conf import settings

# Use the same region as your Lambda and SNS (us-east-1)
AWS_REGION = getattr(settings, "AWS_REGION_NAME", "us-east-1")
LAMBDA_FUNCTION_NAME = getattr(settings, "BOOKING_LAMBDA_NAME", "yugo-booking")

lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def invoke_booking_lambda(booking):
    """
    Called from views.book_room after a Booking is created.
    Sends booking details to the Lambda function, which then publishes to SNS.
    """

    payload = {
        "booking_id": booking.id,
        "user_email": booking.user_email,
        "room_name": booking.room.name,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "total_price": str(booking.total_price),
    }

    lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,  # <-- uses setting or default
        InvocationType="Event",             # async, don't block the web request
        Payload=json.dumps(payload).encode("utf-8"),
    )
