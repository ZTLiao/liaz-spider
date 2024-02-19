FROM python:3.11.4

USER root

ARG PROFILES_ACTIVE
ARG APPLICATION_NAME
ARG SERVER_PORT

ENV WORK_DIR /data/python/$APPLICATION_NAME
ENV PROFILES_ACTIVE $PROFILES_ACTIVE
ENV SERVER_PORT $SERVER_PORT
ENV NODE_PATH /usr/local/lib/node_modules

RUN sed -i s/deb.debian.org/mirrors.aliyun.com/g /etc/apt/sources.list.d/debian.sources && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

RUN apt update

RUN echo 'Y' | apt-get install xvfb

RUN apt-get install unzip

RUN apt-get update

RUN echo 'Y' | apt-get install libnss3

RUN echo 'Y' | apt-get install libgtk2.0-0 libgconf-2-4 libpango1.0-0 libcairo2 libcups2 libxss1 libxkbfile1 fonts-liberation libasound2 libatk-bridge2.0-0 libatspi2.0-0 libgbm1  libgtk-3-0 libu2f-udev libvulkan1 libxkbcommon0 xdg-utils

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

RUN dpkg -i google-chrome-stable_current_amd64.deb

RUN apt-get install -f

RUN apt-get install -y nodejs

RUN apt-get install -y npm

RUN npm config set registry http://registry.npm.taobao.org

RUN npm install -g crypto-js

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

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com zhconv

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com selenium

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com Pillow

RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com PyExecJS

WORKDIR $WORK_DIR/

RUN mkdir -p $WORK_DIR/logs

CMD ["python3", "main.py", "-e", "test", "-p", "8083"]

HEALTHCHECK --interval=20s --timeout=10s --retries=10 CMD wget --quiet --tries=1 --spider http://localhost:$SERVER_PORT || exit 1