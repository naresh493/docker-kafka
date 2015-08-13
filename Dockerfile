# Dockerfile for Kafka

FROM quay.io/signalfuse/maestro-base:15.04-0.2.6
MAINTAINER Maxime Petazzoni <max@signalfx.com>

ENV DEBIAN_FRONTEND noninteractive

# Get Python ZooKeeper (Kazoo)
RUN apt-get -y install python-pip && pip install kazoo && apt-get clean

# Gradle - required to build kafka
ENV GRADLE_VERSION 2.6
RUN mkdir -p /opt/gradle-${GRADLE_VERSION}
RUN cd /opt/gradle-${GRADLE_VERSION} && \
    wget "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" && \
    unzip "gradle-${GRADLE_VERSION}-bin.zip" && \
    ln -s "gradle-${GRADLE_VERSION}" gradle && \
    rm "gradle-${GRADLE_VERSION}-bin.zip"

# Set appropriate environment variables
ENV PATH $PATH:/opt/gradle-${GRADLE_VERSION}/gradle/bin

# Git user config for cherry-pick to work
RUN git config --global user.email "max@signalfx.com" && \
    git config --global user.name "Maxime Petazzoni"

# Get latest available release of Kafka (no stable release yet).
RUN mkdir -p /opt
RUN git clone https://github.com/apache/kafka.git /opt/kafka
# Get 0.8.2.1 but cherry-pick the commit that uses 
# zk client 0.5 since it is supposed to fix some bugs.
RUN cd /opt/kafka && \
    git checkout -b blessed tags/0.8.2.1 && \
    git cherry-pick 41ba26273b497e4cbcc947c742ff6831b7320152 && \
    gradle && \
    ./gradlew jar

ADD run.py /opt/kafka/.docker/

WORKDIR /opt/kafka
CMD ["python", "/opt/kafka/.docker/run.py"]
