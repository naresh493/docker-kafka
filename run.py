#!/usr/bin/env python

# Copyright (C) 2013 SignalFuse, Inc.

# Start script for the Kafka service.
# Requires kazoo, a pure-Python ZooKeeper client.

from kazoo.client import KazooClient
import logging
import os
import sys

from maestro.guestutils import get_container_name, \
    get_container_host_address, \
    get_environment_name, \
    get_node_list, \
    get_port, \
    get_service_name

# Setup logging for Kazoo.
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

KAFKA_CONFIG_FILE = os.path.join('config', 'server.properties')
KAFKA_LOGGING_CONFIG = os.path.join('config', 'log4j.properties')
KAFKA_ZOOKEEPER_BASE = os.environ.get('ZOOKEEPER_BASE',
                                      '/{}/kafka'.format(get_environment_name()))

LOG_PATTERN = "%d{yyyy'-'MM'-'dd'T'HH:mm:ss.SSSXXX} %-5p [%-35.35t] [%-36.36c]: %m%n"

ZOOKEEPER_NODE_LIST = ','.join(get_node_list('zookeeper', ports=['client']))

KAFKA_CONFIG_TEMPLATE = """# Kafka configuration for %(node_name)s
broker.id=%(broker_id)d
advertised.host.name=%(host_address)s
port=%(broker_port)d

num.network.threads=%(num_threads)d
num.io.threads=%(num_threads)d

socket.send.buffer.bytes=1048576
socket.receive.buffer.bytes=1048576
socket.request.max.bytes=104857600

log.dirs=%(log_dirs)s
num.partitions=%(num_partitions)d

log.flush.interval.messages=%(flush_interval_msgs)s
log.flush.interval.ms=%(flush_interval_ms)d
log.retention.hours=%(retention_hours)d
log.retention.bytes=%(retention_bytes)d
log.segment.bytes=536870912
log.cleanup.interval.mins=1

default.replication.factor=%(replication_factor)d
num.replica.fetchers=%(num_replica_fetchers)d
replica.fetch.max.bytes=1048576
replica.fetch.wait.max.ms=500
replica.high.watermark.checkpoint.interval.ms=5000
replica.socket.timeout.ms=%(replica_socket_timeout_ms)d
replica.socket.receive.buffer.bytes=65536

replica.lag.time.max.ms=%(replica_lag_max_ms)d
replica.lag.max.messages=%(replica_lag_max_msgs)d

zookeeper.connect=%(zookeeper_nodes)s%(zookeeper_base)s
zookeeper.connection.timeout.ms=6000
zookeeper.session.timeout.ms=6000
zookeeper.sync.time.ms=2000

kafka.metrics.polling.interval.secs=5
kafka.metrics.reporters=kafka.metrics.KafkaCSVMetricsReporter
kafka.csv.metrics.dir=/var/lib/kafka/metrics/
kafka.csv.metrics.reporter.enabled=false
"""

KAFKA_LOGGING_TEMPLATE = """# Log4j configuration, logs to rotating file
log4j.rootLogger=INFO,R

log4j.appender.R=org.apache.log4j.RollingFileAppender
log4j.appender.R.File=/var/log/%(service_name)s/%(container_name)s.log
log4j.appender.R.MaxFileSize=100MB
log4j.appender.R.MaxBackupIndex=10
log4j.appender.R.layout=org.apache.log4j.PatternLayout
log4j.appender.R.layout.ConversionPattern=%(log_pattern)s
"""

replication = min(int(os.environ.get("REPLICATION", 2)), len(get_node_list('kafka')))
# Generate the Kafka configuration from the defined environment variables.
config_model = {
    'node_name': get_container_name(),
    'broker_id': int(os.environ.get('BROKER_ID', 0)),
    'host_address': get_container_host_address(),
    'broker_port': get_port('broker', 9092),
    # Default log directory is /var/lib/kafka/logs.
    'log_dirs': os.environ.get('LOG_DIRS', '/var/lib/kafka/logs'),
    'num_partitions': int(os.environ.get('NUM_PARTITIONS', 8)),
    # Default retention is 7 days (168 hours).
    'retention_hours': int(os.environ.get('RETENTION_HOURS', 168)),
    # Default retention is only based on time.
    'retention_bytes': int(os.environ.get('RETENTION_BYTES', -1)),
    'zookeeper_nodes': ZOOKEEPER_NODE_LIST,
    'zookeeper_base': KAFKA_ZOOKEEPER_BASE,
    'flush_interval_ms': int(os.environ.get('FLUSH_INTERVAL_MS', 10000)),
    'flush_interval_msgs': int(os.environ.get('FLUSH_INTERVAL_MSGS', 10000)),
    'num_threads': int(os.environ.get('NUM_THREADS', 8)),
    'replication_factor': replication,
    'num_replica_fetchers': int(os.environ.get('NUM_REPLICA_FETCHERS', 4)),
    'replica_socket_timeout_ms': int(os.environ.get('REPLICA_SOCKET_TIMEOUT_MS', 2500)),
    'replica_lag_max_ms': int(os.environ.get('REPLICA_LAG_MAX_MS', 5000)),
    'replica_lag_max_msgs': int(os.environ.get('REPLICA_LAG_MAX_MSGS', 1000)),
}

with open(KAFKA_CONFIG_FILE, 'w+') as conf:
    conf.write(KAFKA_CONFIG_TEMPLATE % config_model)


# Setup the logging configuration.
logging_model = {
    'service_name': get_service_name(),
    'container_name': get_container_name(),
    'log_pattern': LOG_PATTERN
}
with open(KAFKA_LOGGING_CONFIG, 'w+') as f:
    f.write(KAFKA_LOGGING_TEMPLATE % logging_model)

# Ensure the existence of the ZooKeeper root node for Kafka
print 'Ensuring existance of the ZooKeeper zNode chroot path %s...' % KAFKA_ZOOKEEPER_BASE


def ensure_kafka_zk_path(retries=3):
    while retries >= 0:
        # Connect to the ZooKeeper nodes. Use a pretty large timeout in case they were
        # just started. We should wait for them for a little while.
        zk = KazooClient(hosts=ZOOKEEPER_NODE_LIST, timeout=30000)
        try:
            zk.start()
            zk.ensure_path(KAFKA_ZOOKEEPER_BASE)
            return True
        except:
            retries -= 1
        finally:
            zk.stop()
    return False

if not ensure_kafka_zk_path():
    sys.stderr.write('Could not create the base ZooKeeper path for Kafka!\n')
    sys.exit(1)

# Setup the JMX Java agent and various JVM options.
jvm_opts = [
    '-server',
    '-showversion',
    '-Dvisualvm.display.name="{}/{}"'.format(
        get_environment_name(), get_container_name()),
]

jmx_port = get_port('jmx', -1)
if jmx_port != -1:
    os.environ['JMX_PORT'] = str(jmx_port)
    jvm_opts += [
        '-Djava.rmi.server.hostname={}'.format(get_container_host_address()),
        '-Dcom.sun.management.jmxremote.port={}'.format(jmx_port),
        '-Dcom.sun.management.jmxremote.rmi.port={}'.format(jmx_port),
        '-Dcom.sun.management.jmxremote.authenticate=false',
        '-Dcom.sun.management.jmxremote.local.only=false',
        '-Dcom.sun.management.jmxremote.ssl=false',
    ]

os.environ['KAFKA_OPTS'] = ' '.join(jvm_opts) + os.environ.get('JVM_OPTS', '')

# Start the Kafka broker.
os.execl('bin/kafka-server-start.sh', 'kafka', KAFKA_CONFIG_FILE)
