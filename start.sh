SERVICE_PORT=8083
APPLICATION_NAME=liaz-spider
WEB_DIR=/data/python/$APPLICATION_NAME

docker build -f $WEB_DIR/Dockerfile -t $APPLICATION_NAME --build-arg PROFILES_ACTIVE=test --build-arg SERVICE_PORT=$SERVICE_PORT $WEB_DIR

docker run --rm -p $SERVICE_PORT:$SERVICE_PORT --name $APPLICATION_NAME -v $WEB_DIR/:$WEB_DIR -d $APPLICATION_NAME || exit

docker run -p 8083:8083 --name liaz-spider -v /data/python/liaz-spider/:/data/python/liaz-spider -d liaz-spider