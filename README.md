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
