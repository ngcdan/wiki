---
title: "Kafka"
source: "Notion"
synced_date: "2026-04-05"
---

## Kafka Overview

### Kafka giải quyết

- **Tight Coupling**: Kafka decouples producer and consumer systems
- **Async Communication**: Enables asynchronous message passing between services
- **Scalability**: Khả năng mở rộng qua Topics và Partitions
- **Reliability**: Khả năng chịu lỗi qua Data Persistence và Replication

## Core Concepts

### Pub/Sub System

Kafka operates as a publish-subscribe messaging system where:
- Producers publish messages to topics
- Consumers subscribe to topics and receive messages
- Multiple consumers can read the same message

### Zookeeper Roles

Zookeeper manages:
- Broker coordination
- Leader election
- Cluster metadata

### Kafka Connect vs Streams

- **Kafka Connect**: Framework for integrating external systems with Kafka
- **Kafka Streams**: Stream processing library for building applications

## Topics and Partitions

### Topics/Partitions/Rebalance

Topics are divided into partitions for parallel processing and scalability.

#### CLI Examples

```bash
# List topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Create topic
kafka-topics.sh --create --topic my-topic --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092

# Describe topic
kafka-topics.sh --describe --topic my-topic --bootstrap-server localhost:9092

# Consume messages
kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server localhost:9092

# Produce messages
kafka-console-producer.sh --topic my-topic --bootstrap-server localhost:9092
```

## Consumer Groups

### Consumer Group Demo

Consumer groups allow multiple consumers to work together on processing a topic:

```bash
# Create consumer group
kafka-console-consumer.sh --topic my-topic --group my-group --bootstrap-server localhost:9092

# List consumer groups
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# Describe consumer group
kafka-consumer-groups.sh --describe --group my-group --bootstrap-server localhost:9092
```

### Partition-Consumer Mapping

Each partition is assigned to one consumer in a group:

| Partition | Consumer |
|-----------|----------|
| 0         | Consumer-1 |
| 1         | Consumer-2 |
| 2         | Consumer-1 |

## Message Keys and Routing

### Key-Based Routing

Messages with the same key are sent to the same partition, ensuring order:

| Key   | Partition | Content |
|-------|-----------|---------|
| key-1 | Partition-0 | Message-A |
| key-1 | Partition-0 | Message-B |
| key-2 | Partition-1 | Message-C |

## Key Sections 🧩

### 1. Partition Basics

Partitions enable parallel processing and horizontal scaling of topics.

### 2. Consumer Groups

Multiple consumers in a group process partitions in parallel.

### 3. Message Keys

Keys determine which partition receives a message for ordering guarantees.

### 4. Demo Scenarios

Practical examples of Kafka producer-consumer interactions.

### 5. Kafka Consumer Groups CLI

Using kafka-consumer-groups.sh to manage consumer group operations.

### 6. Serializers and Producer Configuration

#### Java Code Example

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("acks", "all");
props.put("retries", 3);
props.put("linger.ms", 10);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
```

### 7. Consumer API

The Kafka Consumer API allows applications to:
- Subscribe to topics or partitions
- Poll for records
- Commit offsets
- Handle rebalancing

Partition-consumer relationships:
- Each consumer receives one or more partitions
- Partitions are distributed evenly across consumers
- On rebalancing, partitions are reassigned

### 8. Kafka Connect

#### Source and Sink Connectors

- **Source Connectors**: Ingest data from external systems into Kafka
- **Sink Connectors**: Export data from Kafka to external systems

#### Standalone vs Distributed Modes

- **Standalone Mode**: Single process, development/testing
- **Distributed Mode**: Multiple workers, production deployment

#### CDC Pipeline Setup with PostgreSQL

Change Data Capture (CDC) pipeline using Debezium:

1. Configure PostgreSQL for logical replication
2. Deploy Debezium PostgreSQL connector
3. Configure connector to monitor tables
4. Messages flow to Kafka topics
5. Consumers process change events
