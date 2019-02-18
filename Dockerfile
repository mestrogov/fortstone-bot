FROM python:3.7.2-slim-stretch
MAINTAINER Yaroslav <hello@unimarijo.com>
ENV INSTALL_PATH /data

COPY . $INSTALL_PATH
WORKDIR $INSTALL_PATH

RUN pip install -r requirements/requirements.txt

CMD python run.py
