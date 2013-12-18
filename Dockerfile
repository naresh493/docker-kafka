# Dockerfile for Kafka

FROM mpetazzoni/maestro-base

MAINTAINER Maxime Petazzoni <max@signalfuse.com>

# Get Python ZooKeeper and Maestro for guest utils
RUN apt-get update
RUN apt-get -y install python-pip python-dev python-setuptools
RUN pip install kazoo
RUN easy_install http://github.com/signalfuse/maestro-ng/archive/maestro-0.1.4.zip

# Get latest available release of Kafka (no stable release yet).
RUN mkdir -p /opt
RUN git clone https://github.com/apache/kafka.git /opt/kafka
# Checkout "blessed" commit from trunk (we need KAFKA-1092)
RUN cd /opt/kafka && git checkout -b blessed a55ec0620f6ce805fafe2e1d4035ec3e0ab4e0d0
RUN cd /opt/kafka && ./sbt update
RUN cd /opt/kafka && ./sbt package
RUN cd /opt/kafka && ./sbt assembly-package-dependency

ADD jmxagent.jar /opt/kafka/lib/
ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
VOLUME /var/lib/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
