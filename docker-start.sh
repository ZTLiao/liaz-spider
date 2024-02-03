#!/usr/bin/env bash
ROOT_DIR=/root/python/liaz-spider
APPLICATION_NAME=$1
SERVER_PORT=$2
PROFILES_ACTIVE=prod

if [ -z "$APPLICATION_NAME" ]
then
  echo 'applicationName is null!'
  exit
fi

WORK_DIR=/data/python/$APPLICATION_NAME

mkdir -p $WORK_DIR

mkdir -p $WORK_DIR/logs

cd $ROOT_DIR && docker build -f $ROOT_DIR/Dockerfile -t $APPLICATION_NAME --build-arg APPLICATION_NAME=$APPLICATION_NAME --build-arg PROFILES_ACTIVE=$PROFILES_ACTIVE --build-arg SERVER_PORT=$SERVER_PORT $WORK_DIR

docker run --rm -p $SERVER_PORT:$SERVER_PORT --name $APPLICATION_NAME -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro -v $ROOT_DIR/:$WORK_DIR/ -d $APPLICATION_NAME python3 main.py -e $PROFILES_ACTIVE -p $SERVER_PORT > $WORK_DIR/logs/web_info.log || exit