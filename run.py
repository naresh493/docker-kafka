#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for the Kafka service.
# Requires kazoo, a pure-Python ZooKeeper client.

from kazoo.client import KazooClient
import logging
import os
import re
import sys

if __name__ != '__main__':
    sys.stderr.write('This script is only meant to be executed.\n')
    sys.exit(1)

# Setup logging for Kazoo.
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

KAFKA_CONFIG_FILE = 'config/server.properties'

# Get container/instance name.
CONTAINER_NAME = os.environ.get('CONTAINER_NAME', '')
assert CONTAINER_NAME, 'Container name is missing!'
KAFKA_CONFIG_BASE = re.sub(r'[^\w]', '_', CONTAINER_NAME).upper()

# Get container's host IP address/hostname.
CONTAINER_HOST_ADDRESS = os.environ.get('CONTAINER_HOST_ADDRESS', '')
assert CONTAINER_HOST_ADDRESS, 'Container host address is required for Kafka discovery!'

# Environment variables driving the Kafka configuration and their defaults.
KAFKA_CONFIG_BROKER_ID = int(os.environ.get('KAFKA_CONFIG_BROKER_ID', 0))
KAFKA_CONFIG_BROKER_PORT = int(os.environ.get('KAFKA_%s_BROKER_PORT' % KAFKA_CONFIG_BASE, 9092))
KAFKA_CONFIG_ZOOKEEPER_BASE = os.environ.get('KAFKA_CONFIG_ZOOKEEPER_BASE', '')

# Build ZooKeeper node list with zNode path chroot.
ZOOKEEPER_NODE_LIST = []
for k, v in os.environ.iteritems():
    m = re.match(r'^ZOOKEEPER_(\w+)_HOST$', k)
    if not m: continue
    ZOOKEEPER_NODE_LIST.append(
        '%s:%d' % (v, int(os.environ['ZOOKEEPER_%s_CLIENT_PORT' % m.group(1)])))
assert ZOOKEEPER_NODE_LIST, 'ZooKeeper nodes are required for Kafka discovery!'

# Generate the Kafka configuration from the defined environment variables.
with open(KAFKA_CONFIG_FILE, 'w+') as conf:
    conf.write("""# Kafka configuration for %(node_name)s
broker.id=%(broker_id)d
advertised.host.name=%(host_address)s
port=%(broker_port)d

num.network.threads=2
num.io.threads=2

socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

log.dir=/var/lib/kafka/logs
num.partitions=1

log.flush.interval.messages=10000
log.flush.interval.ms=100
log.retention.hours=168
log.segment.bytes=536870912
log.cleanup.interval.mins=1

zookeeper.connect=%(zookeeper_nodes)s%(zookeeper_base)s
zookeeper.connection.timeout=1000000

kafka.metrics.polling.interval.secs=5
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter
kafka.csv.metrics.dir=/var/lib/kafka/metrics/
kafka.csv.metrics.reporter.enabled=false
""" % {
        'node_name': CONTAINER_NAME,
        'broker_id': KAFKA_CONFIG_BROKER_ID,
        'host_address': CONTAINER_HOST_ADDRESS,
        'broker_port': KAFKA_CONFIG_BROKER_PORT,
        'zookeeper_nodes': ','.join(ZOOKEEPER_NODE_LIST),
        'zookeeper_base': KAFKA_CONFIG_ZOOKEEPER_BASE,
    })

print 'Kafka will connect to ZooKeeper at %s%s' % \
        (', '.join(ZOOKEEPER_NODE_LIST), KAFKA_CONFIG_ZOOKEEPER_BASE)

print 'Ensuring existance of the ZooKeeper zNode chroot path %s...' % \
        KAFKA_CONFIG_ZOOKEEPER_BASE
def ensure_kafka_zk_path(retries=3):
    while retries >= 0:
        # Connect to the ZooKeeper nodes. Use a pretty large timeout in case they were
        # just started. We should wait for them for a little while.
        zk = KazooClient(hosts=','.join(ZOOKEEPER_NODE_LIST), timeout=30000)
        try:
            zk.start()
            zk.ensure_path(KAFKA_CONFIG_ZOOKEEPER_BASE)
            return True
        except:
            retries -= 1
        finally:
            zk.stop()

    return False

if not ensure_kafka_zk_path():
    sys.stderr.write('Could not create the base ZooKeeper path for Kafka!\n')
    sys.exit(1)

# Start the Kafka broker.
os.execl('bin/kafka-server-start.sh', 'kafka', KAFKA_CONFIG_FILE)
