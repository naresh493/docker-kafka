# Dockerfile for Alpine-based Kafka

FROM quay.io/signalfuse/maestro-base:alp-3.4-jdk8
MAINTAINER Maxime Petazzoni <max@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

ADD ./install_kafka /opt/install_kafka
RUN /opt/install_kafka

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
