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

curl -v -X GET http://172.17.0.4:8083/spider/script/execute?script=dongmanla\&page_type=1

curl -v -X GET http://172.17.0.4:8083/spider/transfer/upload?resource_url=8.134.215.58:9000

docker run -p 8083:8083 --name liaz-spider -v /data/python/liaz-spider/:/data/python/liaz-spider -d liaz-spider
