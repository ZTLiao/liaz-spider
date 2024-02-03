FROM python:3.11.4

USER root

ARG PROFILES_ACTIVE
ARG APPLICATION_NAME
ARG SERVER_PORT

ENV WORK_DIR /data/python/$APPLICATION_NAME
ENV PROFILES_ACTIVE $PROFILES_ACTIVE
ENV SERVER_PORT $SERVER_PORT

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com fastapi

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com "uvicorn[standard]"==0.24.0

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com pymysql

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com redis

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com nacos-sdk-python

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com pyyaml

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com requests

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com beautifulsoup4

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com lxml

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com cos-python-sdk-v5

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com apscheduler

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com pycryptodome

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com asn1crypto

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com grpcio

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com grpcio-tools

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com protobuf

WORKDIR $WORK_DIR/

RUN mkdir -p $WORK_DIR/logs

CMD ["python3", "main.py", "-e", "test", "-p", "8083"]

HEALTHCHECK --interval=20s --timeout=10s --retries=10 CMD wget --quiet --tries=1 --spider http://localhost:$SERVER_PORT || exit 1