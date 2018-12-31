# -*- coding: utf-8 -*-

"""
This service class can be used to call the various AWS services that we need to process the job.
"""

import json
import os
import boto3
import cv2
from k_util.logger import Logger
from logic.transfer_net import TransferNet

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Service:

    K_AWS_ACCESS_KEY = "AWS_ACCESS_KEY_ID"
    K_AWS_SECRET_KEY = "AWS_SECRET_ACCESS_KEY"
    K_SQS_QUEUE_URL = "SQS_QUEUE_URL"
    K_S3_BUCKET_NAME = "S3_BUCKET_NAME"
    K_DYNAMO_DB_TABLE_NAME = "DYNAMO_DB_TABLE_NAME"
    K_EPOCHS = "EPOCHS"

    # ===================================================================================================
    # Initialization.
    # ===================================================================================================

    def __init__(self):

        # Initialize the NN.
        self.net = TransferNet()

        # Reference to all the AWS clients.
        self.sqs_client = None
        self.s3_resource = None
        self.dynamo_db_resource = None
        self.dynamo_db_table = None

        # AWS Settings.
        self.s3_bucket_name: str = None
        self.sqs_queue_url: str = None
        self.dynamo_db_table_name: str = None

        self.n_epochs = int(os.environ[self.K_EPOCHS]) if self.K_EPOCHS in os.environ else 10

        # Validate and initialize.
        self.assert_valid_credentials()
        self.create_clients()

    def create_clients(self):
        """ Initialize all the AWS clients. """

        self.dynamo_db_table_name = os.environ[self.K_DYNAMO_DB_TABLE_NAME]
        self.sqs_queue_url = os.environ[self.K_SQS_QUEUE_URL]
        self.s3_bucket_name = os.environ[self.K_S3_BUCKET_NAME]

        self.sqs_client = boto3.client('sqs')
        self.s3_resource = boto3.resource('s3')
        self.dynamo_db_resource = boto3.resource('dynamodb')
        self.dynamo_db_table = self.dynamo_db_resource.Table(self.dynamo_db_table_name)

    def assert_valid_credentials(self):
        """ Make sure that we have populated the AWS credentials in the environment. """
        keys = [
            self.K_AWS_ACCESS_KEY,
            self.K_AWS_SECRET_KEY,
            self.K_SQS_QUEUE_URL,
            self.K_S3_BUCKET_NAME,
            self.K_DYNAMO_DB_TABLE_NAME
        ]

        Logger.field("Environment Variables", "Checking...")

        for k in keys:
            if k not in os.environ:
                raise Exception(f"Environment variable {k} is not set.")

        Logger.field("Environment Variables", "OK! (All Keys Exist)")

    # ===================================================================================================
    # Service API.
    # ===================================================================================================

    def check_for_message(self) -> (dict, dict):
        """ Check for a message in the SQS queue.
        Returns None if no messages are found, else returns the message.
        """
        # Receive message from SQS queue
        response = self.sqs_client.receive_message(
            QueueUrl=self.sqs_queue_url,
            AttributeNames=['SentTimestamp'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        if "Messages" not in response or len(response) == 0:
            Logger.field("SQS Message", "Empty")
            return None, None

        # Found a message.
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        Logger.field("SQS Message", message)
        return message, receipt_handle

    def delete_message(self, receipt_handle: dict):
        """ Erase the message from the queue. """
        self.sqs_client.delete_message(
            QueueUrl=self.sqs_queue_url,
            ReceiptHandle=receipt_handle
        )

    def process_message(self, message: dict, receipt_handle: dict):
        """ Process the message. """

        Logger.field("Service", "Processing Message")
        body = message["Body"]
        message_data = json.loads(body)

        # Get the keys we want from our message.
        job_id = message_data["id"]
        content_image_url = message_data["content_url"]
        style_image_url = message_data["style_url"]

        # Delete the message so we don't keep repeating it.
        self.delete_message(receipt_handle)

        # Log some information.
        Logger.field("Job ID", job_id)
        Logger.field("Content Image", content_image_url)
        Logger.field("Style Image", style_image_url)

        # Download the images.
        content_local_path = self.download_image(content_image_url)
        style_local_path = self.download_image(style_image_url)

        # Prepare the network and execute the transfer.
        self.prepare_network(content_local_path, style_local_path)
        self.run_transfer_loop(job_id)

        # Process is complete. Execute the upload.
        target_image = self.net.get_current_target_image()
        self.upload_result(target_image, job_id)

    def download_image(self, image_url: str) -> str:
        """ Download the image from S3 to prepare to process. Returns the local saved path. """
        s3_key = image_url.split(f"{self.s3_bucket_name}/")[-1]
        image_local_path = s3_key.split("/")[-1]
        Logger.field("Downloading Image", f"From {s3_key} to P{image_local_path}")
        self.s3_resource.Bucket(self.s3_bucket_name).download_file(s3_key, image_local_path)
        Logger.log("Image Download Success")
        return image_local_path

    def prepare_network(self, content_local_path: str, style_local_path: str):
        """ Prepare the style transfer network to do the job. """

        Logger.field("Preparing to Run Network. Epochs", self.n_epochs)

        # Prepare the images.
        content_image = cv2.imread(content_local_path)
        style_image = cv2.imread(style_local_path)
        self.net.prepare_network(content_image, style_image, self.n_epochs)

        Logger.log("Network Prepared")

    def run_transfer_loop(self, job_id: str):
        """ Run the transfer process loop. """
        saved_progress = 0
        while True:

            progress = int(100 * self.net.step())

            if progress != saved_progress:
                saved_progress = progress
                self.dynamo_db_table.update_item(
                    Key={
                        'job_id': job_id
                    },
                    UpdateExpression='SET progress = :val1',
                    ExpressionAttributeValues={
                        ':val1': progress
                    }
                )
                Logger.field("Progress Updated", progress)

            if progress == 100:
                break

    def upload_result(self, target_image, job_id: str):
        """ Upload the target image. """
        s3_client = boto3.client('s3')

        # Create the image and keys.
        target_file = f"output_{job_id}.png"
        s3_target_key = f"output/{target_file}"
        cv2.imwrite(target_file, target_image)
        Logger.field("Uploading", f"{target_file} to {s3_target_key}")
        s3_client.upload_file(target_file, self.s3_bucket_name, s3_target_key,
                              ExtraArgs={'ACL': 'public-read'})

        # Get result image URL.
        bucket_location = s3_client.get_bucket_location(Bucket=self.s3_bucket_name)
        result_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            self.s3_bucket_name,
            s3_target_key)

        # Update the URL on the DB.
        self.dynamo_db_table.update_item(
            Key={
                'job_id': job_id
            },
            UpdateExpression='SET result_image = :val1',
            ExpressionAttributeValues={
                ':val1': result_url
            }
        )

        Logger.field("Target Image Updated", result_url)
