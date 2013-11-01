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

  - `CONTAINER_HOST_ADDRESS` should contain the address of the Docker
    container's host. It' used by Kafka as the address advertised to ZooKeeper
    for broker discovery and is required for the container to start;
  - `ZOOKEEPER_NODE_LIST` is a comma-separated list of `host:port`
    definitions that define, in order, *all* the nodes of the ZooKeeper
    cluster that Kafka is to use. Each host will be placed, followed by the
    `KAFKA_CONFIG_ZOOKEEPER_BASE` chroot path, in the `zookeeper.connect`
    configuration variable;
  - `KAFKA_CONFIG_ZOOKEEPER_BASE`, the ZooKeeper tree chroot for Kafka to use
    in the `zookeeper.connect` string and properly namespace the Kafka zNodes
    for this deployment. Defaults to `/local/kafka/central`;
  - `KAFKA_CONFIG_BROKER_PORT`, which controls which port the Kafka broker will
    listen on. Defaults to 9092;
  - `KAFKA_CONFIG_BROKER_ID`, which controls the `broker.id` configuration
    setting and useful for multi-node Kafka clusters. Defaults to 0.

Volumes
-------

The Kafka image uses the following volumes you may want to bind from the
container's host:

  - `/var/lib/kafka`, where the Kafka logs will be stored for each topic.

Usage
-----

To build a new image, simply run from this directory:

```
$ docker build -t `whoami`/kafka .
```

The Docker image will be built and now available in Docker to start a new
container from:

```
$ docker images | grep kafka
mpetazzoni/kafka       latest         6c58d1f6ff3c        5 seconds ago       12.29 kB (virtual 900.1 MB)
```
