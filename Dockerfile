# Dockerfile for Kafka

FROM mpetazzoni/sf-base

MAINTAINER Maxime Petazzoni <max@signalfuse.com>

# Get Python ZooKeeper
RUN apt-get update
RUN apt-get -y install python-pip python-dev
RUN pip install kazoo

# Get latest available release of Kafka (no stable release yet).
RUN mkdir -p /opt
RUN git clone https://github.com/apache/kafka.git /opt/kafka
RUN cd /opt/kafka && ./sbt update
RUN cd /opt/kafka && ./sbt package
RUN cd /opt/kafka && ./sbt assembly-package-dependency

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
VOLUME /var/lib/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
