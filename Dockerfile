FROM python:3.7-slim
MAINTAINER Yaroslav <hello@unimarijo.com>
ENV INSTALL_PATH /data

COPY . $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN pip install -r requirements/requirements.txt

CMD python run.py
