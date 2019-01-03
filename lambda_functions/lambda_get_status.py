import json
import boto3

K_ID = "id"


def create_response(status_code: int, response_data):
    return {
        "statusCode": status_code,
        "body": json.dumps(response_data),
        "headers": {'Access-Control-Allow-Origin': '*'}
    }


def check_job_status(id) -> (bool, int, str):
    """ Check the job's status and progress on DynamoDB. """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('style-transfer-table')
    response = table.get_item(Key={"job_id": id})
    print("DB Response", response)

    if "Item" in response:
        item = response["Item"]
        print(f"Found item: {item}")

        progress = int(item["progress"])
        result_image = item["result_image"]
        return True, progress, result_image
    else:
        return False, 0, None


def lambda_handler(event, context):
    # Check the status of the submitted ID and return the progress or the URL.

    try:

        # Create the response object on standby.
        response = {
            "exists": False,
            "progress": 0,
            "completed": False,
            "result_image": None
        }

        print("Starting Request Process")
        print("Checking if Event has body...")
        print("Event", event)

        # Check the status of the submitted ID.
        if K_ID in event:
            # In case it's directly in the event.
            job_id = event[K_ID]

        else:
            body = event["body"]
            body = json.loads(body)

            if K_ID not in body:
                return create_response(405, "Key 'id' not present in body!")

            job_id = body[K_ID]

        print("Job ID", job_id)

        # Check if the job exists.
        job_exists, job_progress, result_image = check_job_status(job_id)
        print(job_exists, job_progress, result_image)

        response["exists"] = job_exists
        response["progress"] = job_progress

        if job_progress < 100 or "http" not in result_image:
            response["result_image"] = None
            response["progress"] = min(99, job_progress)
        else:
            response["result_image"] = result_image

        response["completed"] = job_progress == 100

    except Exception as e:
        response = {"exception": str(e)}

    return create_response(200, response)
