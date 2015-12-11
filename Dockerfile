# Dockerfile for Kafka

FROM quay.io/signalfuse/maestro-base:alp-3.2-jdk8
MAINTAINER Maxime Petazzoni <max@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN pip install kazoo
# Git user config for cherry-pick to work
RUN git config --global user.email "max@signalfx.com" \
  && git config --global user.name "Maxime Petazzoni"

# Gradle - required to build kafka
ENV GRADLE_VERSION 2.6
RUN mkdir -p /opt/gradle-${GRADLE_VERSION} \
  && cd /opt/gradle-${GRADLE_VERSION} \
  && wget "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" \
  && unzip "gradle-${GRADLE_VERSION}-bin.zip" \
  && ln -s "gradle-${GRADLE_VERSION}" gradle \
  && rm "gradle-${GRADLE_VERSION}-bin.zip"
ENV PATH=$PATH:/opt/gradle-${GRADLE_VERSION}/gradle/bin

ADD build.patch /opt/

# Get Kafka 0.8.2.1 but cherry-pick the commit that uses zk client 0.5 since it
# is supposed to fix some bugs.
RUN mkdir -p /opt \
  && git clone https://github.com/apache/kafka.git /opt/kafka \
  && cd /opt/kafka \
  && git checkout 0.9.0 \
  && git am < /opt/build.patch \
  && gradle \
  && ./gradlew jar

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
