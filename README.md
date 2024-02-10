yum install python3-devel

pip3 install fastapi

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com  "uvicorn[standard]"==0.24.0

pip3 install pymysql

pip3 install redis

pip3 install nacos-sdk-python

pip3 install pyyaml

pip3 install requests

pip3 install beautifulsoup4

pip3 install lxml

pip3 install -U cos-python-sdk-v5

pip3 install apscheduler

pip3 install pycryptodome

pip3 install asn1crypto

pip3 install grpcio

pip3 install grpcio-tools

pip3 install protobuf

pip3 install zhconv

pip3 install selenium

pip3 install Pillow

python3 -m grpc_tools.protoc --python_out=. -I=. dongmanzhijia_comic.proto

curl -v -X GET http://172.17.0.1:8083/spider/script/execute?script=dongmanla\&page_type=1

curl -v -X GET http://172.17.0.1:8084/spider/script/execute?script=shuhuangwang\&page_type=0

docker run -p 8083:8083 --name liaz-spider -v /data/python/liaz-spider/:/data/python/liaz-spider -d liaz-spider
