#!/bin/bash

# Start script for the Kafka service.
#
# This is where service configuration before starting the Kafka broker can be
# performed, if needed, for example to configure the Kafka broker ID and data
# path locations in the configuration file.

cd $(dirname $(readlink -f $0))/../

KAFKA_CONFIG_FILE=config/server.properties

[ -z "$ZOOKEEPER_NODE_LIST" ] && \
  echo "ZooKeeper node list is missing (set ZOOKEEPER_NODE_LIST)!" && \
  exit 1

# Environment variables driving the Kafka configuration and their defaults.
[ -z "$KAFKA_CONFIG_DATA_DIR" ] && KAFKA_CONFIG_DATA_DIR=/var/lib/kafka
[ -z "$KAFKA_CONFIG_BROKER_ID" ] && KAFKA_CONFIG_BROKER_ID=0
[ -z "$KAFKA_CONFIG_BROKER_PORT" ] && KAFKA_CONFIG_BROKER_PORT=9092
[ -z "$KAFKA_CONFIG_ZOOKEEPER_BASE" ] && KAFKA_CONFIG_ZOOKEEPER_BASE=/local/kafka/central

# Generate the Kafka configuration from the defined environment variables.
cat > $KAFKA_CONFIG_FILE << EOF
broker.id=$KAFKA_CONFIG_BROKER_ID
port=$KAFKA_CONFIG_BROKER_PORT

num.network.threads=2
num.io.threads=2
socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

num.partitions=1
log.dir=$KAFKA_CONFIG_DATA_DIR
log.flush.interval.messages=10000
log.flush.interval.ms=100
log.retention.hours=168
log.segment.bytes=536870912
log.cleanup.interval.mins=1

zookeeper.connection.timeout=1000000

kafka.csv.metrics.reporter.enabled=false
kafka.csv.metrics.dir=$KAFKA_CONFIG_DATA_DIR/.metrics/
kafka.metrics.polling.interval.secs=5
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter
EOF

# Generate the ZooKeeper connection string based on the ZooKeeper node list, or
# defaults to a locally-running ZooKeeper node.
ZK_NODE_ID=0
IFS=,
for node in $ZOOKEEPER_NODE_LIST ; do
  KAFKA_ZK_CONNECT[$ZK_NODE_ID]="${node}${KAFKA_CONFIG_ZOOKEEPER_BASE}"
  ZK_NODE_ID=$(($ZK_NODE_ID + 1))
done

echo "Kafka will connect to ZooKeeper with ${KAFKA_ZK_CONNECT[*]}"
echo "zookeeper.connect=${KAFKA_ZK_CONNECT[*]}" >> $KAFKA_CONFIG_FILE

# Start the Kafka broker.
exec bin/kafka-server-start.sh $KAFKA_CONFIG_FILE
