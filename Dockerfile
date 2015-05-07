# Dockerfile for Kafka

FROM quay.io/signalfuse/maestro-base:15.04-0.2.6
MAINTAINER Maxime Petazzoni <max@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN apt-get -y install python-pip && pip install kazoo && apt-get clean

# Get latest available release of Kafka (no stable release yet).
RUN mkdir -p /opt
RUN git clone https://github.com/apache/kafka.git /opt/kafka
# Checkout "blessed" commit from trunk (we need KAFKA-1092 and KAFKA-1112)
# (KAFKA-1092 was a55ec0620f6ce805fafe2e1d4035ec3e0ab4e0d0)
RUN cd /opt/kafka && \
    git checkout -b blessed 855340a2e65ffbb79520c49d0b9a231b94acd538 && \
    ./sbt update && \
    ./sbt package && \
    ./sbt assembly-package-dependency

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
