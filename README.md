# ShadowStream: Enterprise Change Data Capture Platform

![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Docker](https://img.shields.io/badge/docker-available-blue.svg)
![Kafka](https://img.shields.io/badge/Apache-Kafka-231F20.svg)
![gRPC](https://img.shields.io/badge/gRPC-1.76.0+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)




### Overview

ShadowStream is a Change Data Capture (CDC) system that streams database changes in real time, buffers them through Redis Streams, archives them to Kafka, and provides controlled replay over gRPC APIs.
Built for reliability, scalability, and observability.

### Features

- Real-time Change Capture — PostgreSQL logical replication via WAL streaming

- Dual Storage Pipeline — Redis streams (low latency) + Kafka (durable archival)

- Parallel Processing — Kafka consumer groups for high-throughput workloads

- Controlled Replay — Speed-controlled, time-travel replay via gRPC

- Exactly-Once Semantics — Transactional guarantees across Redis + Kafka

- Real-time Monitoring — gRPC progress streaming

- Admin Dashboard — Django-based UI for managing replays



### Quick Start
1. Prerequisites

    Docker & Docker Compose

    Python 3.12+

1. Clone & Setup
git clone https://github.com/mrinalxdev/shadowstream.git
cd shadowstream

2. Start Infrastructure
docker-compose up -d postgres redis kafka

3. Initialize Database
docker-compose exec postgres psql -U postgres -d shadowdb \
  -c "CREATE USER repluser WITH REPLICATION LOGIN PASSWORD 'replpass';"

4. Start Services
```bash
# Start ingestor
docker-compose up -d ingestor

# Start control panel (Django)
docker-compose up -d control

# Start replayer
docker-compose up -d replayer
```

5. Access Dashboard

Admin Panel: http://localhost:8000/admin

Kafka UI: http://localhost:8081

### Configuration
Environment Variables
# PostgreSQL
```bash
PG_HOST=postgres
PG_USER=repluser
PG_PASSWORD=replpass 
```

# Redis
```bash
 REDIS_URL=redis://redis:6379/0  
```

# Kafka
``` KAFKA_BROKERS=kafka:9092 ```

### Kafka Topics

- shadowstream.archive — archived change events

- Consumer groups: analytics-group, backup-group

### API Documentation
gRPC Services
```proto
service Ingestor {
  rpc PushChange(ChangeRecord) returns (PushResponse);
}

service Replayer {
  rpc ReplayEvent(ReplayRequest) returns (ReplayResponse);
}

service ProgressTracker {
  rpc StreamProgress(ReplayRequest) returns (stream ProgressUpdate);
}
```