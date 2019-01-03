#!/bin/sh

docker run -it \
    -e AWS_ACCESS_KEY_ID=<REDACTED> \
    -e AWS_SECRET_ACCESS_KEY=<REDACTED> \
    -e AWS_DEFAULT_REGION=ap-southeast-2 \
    -e SQS_QUEUE_URL=<REDACTED> \
    -e S3_BUCKET_NAME=<REDACTED> \
    -e DYNAMO_DB_TABLE_NAME=<REDACTED> \
    -e EPOCHS=5000 \
    infrarift/style-transfer-worker