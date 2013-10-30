# Dockerfile for Kafka

FROM mpetazzoni/sf-base

MAINTAINER Maxime Petazzoni <max@signalfuse.com>

# Get latest available release of Kafka (no stable release yet).
RUN wget -q -O - https://dist.apache.org/repos/dist/release/kafka/kafka_2.8.0-0.8.0-beta1.tgz \
  | tar -C /opt -xz

ADD run.py /opt/kafka_2.8.0-0.8.0-beta1/.docker/

WORKDIR /opt/kafka_2.8.0-0.8.0-beta1
CMD ["python", "/opt/kafka_2.8.0-0.8.0-beta1/.docker/run.py"]
