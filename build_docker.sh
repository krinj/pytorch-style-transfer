#!/usr/bin/env bash

export DOCKER_USERNAME=${DOCKER_USERNAME:-"user"}
export IMAGE=${IMAGE:-"style-transfer-worker"}
version=`cat version`

echo "Docker User: $DOCKER_USERNAME"
echo "Docker Image: $IMAGE"
echo "Docker Image Version: $version"

docker build -t ${DOCKER_USERNAME}/${IMAGE}:latest ./app/
docker tag ${DOCKER_USERNAME}/${IMAGE}:latest ${DOCKER_USERNAME}/${IMAGE}:${version}
docker push ${DOCKER_USERNAME}/${IMAGE}:latest
docker push ${DOCKER_USERNAME}/${IMAGE}:${version}