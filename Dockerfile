FROM python:3.11.4

USER root

ENV WORK_DIR /data/python/liaz-spider

ARG PROFILES_ACTIVE
ENV PROFILES_ACTIVE $PROFILES_ACTIVE

ENV SERVER_PORT 8083

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

COPY . $WORK_DIR/

WORKDIR $WORK_DIR/

ENTRYPOINT ["python3", "main.py", "-e", "test"]

HEALTHCHECK --interval=20s --timeout=10s --retries=10 CMD wget --quiet --tries=1 --spider http://localhost:$SERVER_PORT || exit 1