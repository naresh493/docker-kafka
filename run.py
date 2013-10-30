#!/usr/bin/env python

# Start script for the Kafka service.
#
# This is where service configuration before starting the Kafka broker can be
# performed, if needed, for example to configure the Kafka broker ID and data
# path locations in the configuration file.

import os
import sys

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

KAFKA_CONFIG_FILE = 'config/server.properties'
KAFKA_CONFIG_TEMPLATE = """
broker.id=%(broker_id)d
port=%(broker_port)d

num.network.threads=2
num.io.threads=2
socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

num.partitions=1
log.dir=%(data_dir)s
log.flush.interval.messages=10000
log.flush.interval.ms=100
log.retention.hours=168
log.segment.bytes=536870912
log.cleanup.interval.mins=1

kafka.csv.metrics.reporter.enabled=false
kafka.csv.metrics.dir=%(data_dir)s/.metrics/
kafka.metrics.polling.interval.secs=5
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter

zookeeper.connect=%(zookeeper_nodes)s
zookeeper.connection.timeout=1000000
"""

# Environment variables driving the Kafka configuration and their defaults.
KAFKA_CONFIG_DATA_DIR = os.environ.get('KAFKA_CONFIG_DATA_DIR', '/var/lib/kafka')
KAFKA_CONFIG_BROKER_ID = int(os.environ.get('KAFKA_CONFIG_BROKER_ID', 0))
KAFKA_CONFIG_BROKER_PORT = int(os.environ.get('KAFKA_CONFIG_BROKER_PORT', 9092))
KAFKA_CONFIG_ZOOKEEPER_BASE = os.environ.get('KAFKA_CONFIG_ZOOKEEPER_BASE', '')

# ZooKeeper node list, required. Comma-separated list of the ZooKeeper nodes,
# as host:port definitions. If defined, the KAFKA_CONFIG_ZOOKEEPER_BASE will be
# appended to each of them for zNode chroot.
ZOOKEEPER_NODE_LIST = os.environ.get('ZOOKEEPER_NODE_LIST', '')
if not ZOOKEEPER_NODE_LIST:
    sys.stderr.write('ZooKeeper node list is required for the Kafka configuration!\n')
    sys.exit(1)

ZOOKEEPER_NODES = ['%s%s' % (node, KAFKA_CONFIG_ZOOKEEPER_BASE)
        for node in ZOOKEEPER_NODE_LIST.split(',')]

# Generate the Kafka configuration from the defined environment variables.
with open(KAFKA_CONFIG_FILE, 'w+') as conf:
    conf.write(KAFKA_CONFIG_TEMPLATE % {
        'broker_id': KAFKA_CONFIG_BROKER_ID,
        'broker_port': KAFKA_CONFIG_BROKER_PORT,
        'data_dir': KAFKA_CONFIG_DATA_DIR,
        'zookeeper_nodes': ','.join(ZOOKEEPER_NODES)
    })

print 'Kafka will connect to ZooKeeper at', ', '.join(ZOOKEEPER_NODES)

# Start the Kafka broker.
os.execl('bin/kafka-server-start.sh', 'kafka', KAFKA_CONFIG_FILE)
