# Dockerfile for Kafka 1.0
FROM quay.io/signalfuse/maestro-base:alp-3.4-jdk8
MAINTAINER Uday Sagar Shiramshetty <uday@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN pip install kazoo

# Get Kafka 1.0.0
ENV KAFKA_VERSION 1.0.0 
RUN curl -s https://apache.osuosl.org/kafka/${KAFKA_VERSION}/kafka_2.12-${KAFKA_VERSION}.tgz | \
    tar xfz - -C /opt && \
    mv /opt/kafka_2.12-${KAFKA_VERSION} /opt/kafka

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
