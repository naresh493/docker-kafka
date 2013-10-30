Kafka on Docker
===============

This `Dockerfile` creates a Docker image that can be used as the base for
running Kafka within a Docker container. The Kafka service is ran by the run.sh
script which is in charge of setting up the Kafka configuration from
environment variables passed to the container when it is run.

The version of Kafka is defined in the `Dockerfile` and currently points at the
last available beta release.

Environment variables
---------------------

The following environment variables are understood by the startup script to
seed the service's configuration:

  - `ZOOKEEPER_NODE_LIST` is a comma-separated list of `host:port`
    definitions that define, in order, *all* the nodes of the ZooKeeper
    cluster that Kafka is to use. Each host will be placed, followed by the
    `KAFKA_CONFIG_ZOOKEEPER_BASE` chroot path, in the `zookeeper.connect`
    configuration variable;
  - `KAFKA_CONFIG_ZOOKEEPER_BASE`, the ZooKeeper tree chroot for Kafka to use
    in the `zookeeper.connect` string and properly namespace the Kafka zNodes
    for this deployment. Defaults to `/local/kafka/central`;
  - `KAFKA_CONFIG_DATA_DIR`, which controls the `data.dir` configuration
    setting. Defaults to `/var/lib/kafka`;
  - `KAFKA_CONFIG_BROKER_PORT`, which controls which port the Kafka broker will
    listen on. Defaults to 9092;
  - `KAFKA_CONFIG_BROKER_ID`, which controls the `broker.id` configuration
    setting and useful for multi-node Kafka clusters. Defaults to 0.

Usage
-----

To build a new image, simply run from this directory:

```
$ docker build -t `whoami`/kafka:0.8.0-beta1 .
```

The Docker image will be built and now available in Docker to start a new
container from:

```
$ docker images | grep kafka
mpetazzoni/kafka       0.8.0-beta1         6c58d1f6ff3c        5 seconds ago       12.29 kB (virtual 900.1 MB)
```
