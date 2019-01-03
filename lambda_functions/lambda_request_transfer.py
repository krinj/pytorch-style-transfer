import json
import uuid
import base64
import boto3


def lambda_handler(event, context):

    try:

        body = event["body"]
        body = json.loads(body)

        # Generate a unique ID to mark the process.
        id = uuid.uuid4().hex

        # Decode the image.
        K_FILENAME_KEY = "contentName"
        K_FILEDATA_KEY = "contentData"
        K_STYLE_NAME_KEY = "styleName"
        K_STYLE_DATA_KEY = "styleData"
        K_BUCKET_NAME = "krinj-style-transfer-data"

        image_success = False
        upload_success = False
        object_url = None

        # Verify job doesn't exist on DB.
        # Get the service resource.
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('style-transfer-table')
        response = table.get_item(Key={"job_id": id})
        print("DB Response", response)

        if "Item" in response:
            # Item exists, we must abort.
            response = {
                "exception": f"Key {id} already exists in the database."
            }
            return {
                'statusCode': 200,
                'body': json.dumps(response),
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                }
            }

        if K_FILEDATA_KEY in body and K_FILENAME_KEY in body and K_STYLE_NAME_KEY in body and K_STYLE_DATA_KEY in body:
            print("Content key, content data, style key and style data exists.")

            s3 = boto3.client('s3')

            image_string = body[K_FILEDATA_KEY].split(",")[1]
            image_data = base64.b64decode(image_string)
            extension = body[K_FILENAME_KEY].split(".")[-1]

            file_name = f"transfer_{id}.{extension}"
            local_path = f'/tmp/{file_name}'
            with open(local_path, 'wb') as f:
                f.write(image_data)

            image_success = True

            # Attempt upload.
            print("Uploading content image")
            s3_path = f"source/{file_name}"
            s3.upload_file(local_path, K_BUCKET_NAME, s3_path, ExtraArgs={'ACL': 'public-read'})

            # Get the upload path.
            bucket_location = s3.get_bucket_location(Bucket=K_BUCKET_NAME)
            content_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
                bucket_location['LocationConstraint'],
                K_BUCKET_NAME,
                s3_path)

            image_string = body[K_STYLE_DATA_KEY].split(",")[1]
            image_data = base64.b64decode(image_string)
            extension = body[K_STYLE_NAME_KEY].split(".")[-1]

            # Upload style image.

            file_name = f"style_{id}.{extension}"
            local_path = f'/tmp/{file_name}'
            with open(local_path, 'wb') as f:
                f.write(image_data)
            image_success = True

            # Attempt upload.
            print("Uploading style image")
            s3_path = f"style/{file_name}"
            s3.upload_file(local_path, K_BUCKET_NAME, s3_path, ExtraArgs={'ACL': 'public-read'})

            # Get the upload path.
            style_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
                bucket_location['LocationConstraint'],
                K_BUCKET_NAME,
                s3_path)

            # Create the job on DynamoDB.
            db_item = {
                "job_id": id,
                "progress": 0,
                "result_image": None,
                "content_image": content_url,
                "style_image": style_url
            }

            # Put the item job into the DB.
            table.put_item(Item=db_item)

            # Queue the job in SQS and let ECS take over.
            sqs = boto3.resource('sqs')
            queue = sqs.get_queue_by_name(QueueName='StyleTransferJobs')
            sqs_body = {"id": id, "content_url": content_url, "style_url": style_url}
            sqs_payload = json.dumps(sqs_body)
            queue.send_message(MessageBody=sqs_payload)

        else:
            print("File key and body does not exist")

        response = {
            "id": id,
            "image_success": image_success,
            "object_url": object_url
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        response = {"exception": str(e)}
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Access-Control-Allow-Origin': '*'
            }
        }
