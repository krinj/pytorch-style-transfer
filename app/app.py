#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import json
import os
import time
import boto3
import cv2

from logic.transfer_net import TransferNet

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"
__version__ = "0.0.0"

K_AWS_ACCESS_KEY = "AWS_ACCESS_KEY_ID"
K_AWS_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"


if __name__ == "__main__":
    print("Running Style Transfer Service")

    net = TransferNet()

    # ===================================================================================================
    # Check AWS Credentials.
    # ===================================================================================================

    print("Checking AWS Credentials")
    if K_AWS_ACCESS_KEY not in os.environ:
        raise Exception(f"Environment variable {K_AWS_ACCESS_KEY} is not set.")

    if K_AWS_SECRET_KEY not in os.environ:
        raise Exception(f"Environment variable {K_AWS_SECRET_KEY} is not set.")

    # ===================================================================================================
    # Receive a SQS Message.
    # ===================================================================================================

    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/535707483867/StyleTransferJobs'

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    print("Response Received")
    print(response)

    if "Messages" not in response or len(response) == 0:
        print("No messages remaining")
        exit(0)

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # ===================================================================================================
    # See if there is a valid URL.
    # ===================================================================================================

    print("Loading Message")
    body = message["Body"]
    message_data = json.loads(body)

    job_id = message_data["id"]
    content_image_url = message_data["content_url"]
    style_image_url = message_data["style_url"]

    # Delete the message from SQS.
    # sqs.delete_message(
    #     QueueUrl=queue_url,
    #     ReceiptHandle=receipt_handle
    # )

    print(f"Message Deleted from SQS: {receipt_handle}")
    print(f"Job ID: {job_id}")
    print(f"Content Image: {content_image_url}")
    print(f"Style Image: {style_image_url}")

    s3 = boto3.resource('s3')
    BUCKET_NAME = 'krinj-style-transfer-data'

    s3_key = content_image_url.split(f"{BUCKET_NAME}/")[-1]
    content_local_path = s3_key.split("/")[-1]
    print(f"Loading from: {s3_key} to {content_local_path}")
    s3.Bucket(BUCKET_NAME).download_file(s3_key, content_local_path)
    print("Success")

    s3_key = style_image_url.split(f"{BUCKET_NAME}/")[-1]
    style_local_path = s3_key.split("/")[-1]
    print(f"Loading from: {s3_key} to {style_local_path}")
    s3.Bucket(BUCKET_NAME).download_file(s3_key, style_local_path)
    print("Success")

    # ===================================================================================================
    # Process the image.
    # ===================================================================================================

    content_image = cv2.imread(content_local_path)
    style_image = cv2.imread(style_local_path)

    target_image = cv2.cvtColor(content_image, cv2.COLOR_BGR2GRAY)
    # target_image = cv2.cvtColor(target_image, cv2.COLOR_GRAY2BGR)

    # ===================================================================================================
    # Update the progress.
    # ===================================================================================================

    # Get the DDB table.
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('style-transfer-table')
    net.prepare_network(content_image, style_image, 10)

    saved_progress = 0

    while True:

        progress = int(100 * net.step())

        if progress != saved_progress:
            saved_progress = progress
            table.update_item(
                Key={
                    'job_id': job_id
                },
                UpdateExpression='SET progress = :val1',
                ExpressionAttributeValues={
                    ':val1': progress
                }
            )
            print(f"Updated Progress: {progress}")

        if progress == 100:
            break

    target_image = net.get_current_target_image()

    # ===================================================================================================
    # Process is complete.
    # ===================================================================================================

    s3 = boto3.client('s3')
    target_file = f"output_{job_id}.png"
    s3_target_key = f"output/{target_file}"
    cv2.imwrite(target_file, target_image)
    print(f"Uploading: {target_file} to {s3_target_key}")
    s3.upload_file(target_file, BUCKET_NAME, s3_target_key, ExtraArgs={'ACL': 'public-read'})

    # Get result image.
    bucket_location = s3.get_bucket_location(Bucket=BUCKET_NAME)
    result_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        BUCKET_NAME,
        s3_target_key)

    table.update_item(
        Key={
            'job_id': job_id
        },
        UpdateExpression='SET result_image = :val1',
        ExpressionAttributeValues={
            ':val1': result_url
        }
    )

    print("Upload Complete")
