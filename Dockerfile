# Dockerfile for Kafka 0.10.2.0
FROM quay.io/signalfuse/maestro-base:alp-3.2-jdk8
MAINTAINER Uday Sagar Shiramshetty <uday@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN pip install kazoo

# Get Kafka 0.10.2.1
ENV KAFKA_VERSION 0.10.2.1
RUN curl -s https://apache.osuosl.org/kafka/${KAFKA_VERSION}/kafka_2.10-${KAFKA_VERSION}.tgz | \
    tar xfz - -C /opt && \
    mv /opt/kafka_2.10-${KAFKA_VERSION} /opt/kafka

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
