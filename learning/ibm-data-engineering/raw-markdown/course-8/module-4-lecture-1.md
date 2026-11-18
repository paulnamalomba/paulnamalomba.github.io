# Module 4, lecture 2: Apache Kafka overview & architecture

Transitioning from abstract event streaming concepts to a concrete implementation requires a system capable of handling relentless data velocity without dropping state. Apache Kafka is the de facto standard for this tier of infrastructure.

---

## 1. The operational scope of Kafka

LinkedIn developed Kafka to handle large volumes of user activity data, including page views and keystrokes. It is now used to move event streams between enterprise systems.

Kafka can track thousands of concurrent student session states or aggregate real-time computational metrics from a distributed solver. Backend applications use it for:

- **Metric Streaming:** Ingesting high-frequency sensor readings, hardware utilization, or application logs into a centralized, immutable repository.
- **Event Sourcing & Transactions:** Recording fintech state changes where each change (e.g., a payment execution) must be securely ordered, audited, and strictly compliant with governance regulations.
- **Real-Time Analytics:** Feeding data into stream-processing engines (like Apache Flink) or machine learning pipelines with sub-millisecond latency.

---

## 2. Core architectural paradigms

Kafka is a distributed, real-time system built on a strictly decoupled client-server architecture communicating via a custom TCP-based protocol.

### 2.1 The broker cluster

A Kafka deployment is never a single server; it is a cluster of independent nodes called **Brokers**.

- **Ingestion:** Brokers receive payloads from Producers.
- **Storage:** They persist these records to disk. Kafka divides this storage into **Partitions** and replicates them across multiple brokers. This ensures that if a server rack in a Cape Town data center goes offline, the data remains highly available and fault-tolerant.
- **Distribution:** Brokers serve these persistent records to subscribing Consumers. Because data is stored permanently (based on retention policies), consumers can read and replay events at their own processing speed.

### 2.2 The consensus protocol shift: ZooKeeper to KRaft

Historically, managing the metadata, leader election, and health of a distributed Kafka cluster required an entirely separate distributed system running alongside it: **Apache ZooKeeper**.

Managing two distinct distributed systems simultaneously is a notorious operational headache. Modern Kafka (post-version 2.8) introduced **KRaft (Kafka Raft)**.

KRaft implements the Raft consensus algorithm directly within Kafka, eliminating the ZooKeeper dependency. This consolidates metadata management into dedicated Kafka Controller nodes, streamlining deployment and drastically increasing the partition scaling limits.

```mermaid
graph TD
    subgraph "Legacy Architecture (Pre-2.8)"
        Z1[ZooKeeper Node] --- Z2[ZooKeeper Node]
        Z2 --- Z3[ZooKeeper Node]
        B1_Old[Kafka Broker] -. Metadata .-> Z1
        B2_Old[Kafka Broker] -. Metadata .-> Z2
    end

    subgraph "Modern KRaft Architecture"
        C1[Kafka Controller Quorum] --- C2[Controller]
        C2 --- C3[Controller]
        B1_New[Kafka Broker] --> C1
        B2_New[Kafka Broker] --> C1
    end

```

---

## 3. Infrastructure as Code: C# admin API

Kafka has clients for Java, C/C++, Python, Go, and REST APIs. These clients can produce and consume messages; administrative APIs also let backend applications manage the cluster.

Using the `Confluent.Kafka` library, here is how you programmatically define and provision a new topic with specific partition and replication constraints before your deployment pipelines run.

```csharp
using System;
using System.Threading.Tasks;
using Confluent.Kafka;
using Confluent.Kafka.Admin;

public class KafkaInfrastructureManager
{
    private readonly AdminClientConfig _adminConfig;

    public KafkaInfrastructureManager(string bootstrapServers)
    {
        _adminConfig = new AdminClientConfig
        {
            BootstrapServers = bootstrapServers
        };
    }

    public async Task ProvisionTopicAsync(string topicName, int numPartitions, short replicationFactor)
    {
        using var adminClient = new AdminClientBuilder(_adminConfig).Build();

        try
        {
            var topicSpec = new TopicSpecification
            {
                Name = topicName,
                NumPartitions = numPartitions,
                ReplicationFactor = replicationFactor
            };

            await adminClient.CreateTopicsAsync(new[] { topicSpec });
            Console.WriteLine($"Successfully provisioned topic: {topicName} with {numPartitions} partitions.");
        }
        catch (CreateTopicsException e)
        {
            foreach (var result in e.Results)
            {
                if (result.Error.Code == ErrorCode.TopicAlreadyExists)
                {
                    Console.WriteLine($"Topic '{result.Topic}' already exists. Proceeding.");
                }
                else
                {
                    Console.WriteLine($"An error occurred creating topic {result.Topic}: {result.Error.Reason}");
                }
            }
        }
    }
}

```

---

## 4. Managed ESP providers

Running a distributed consensus protocol requires rigorous tuning of JVM heaps, OS page caches, and network I/O. For teams focused on building computational software or web applications rather than managing server infrastructure, managed services are standard:

| Provider              | Core Value Proposition                                                                                                                                                                   |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Confluent Cloud**   | Founded by the original creators of Kafka. Offers a fully managed, serverless, cloud-native Kafka experience with extensive pre-built connectors (e.g., syncing directly to PostgreSQL). |
| **Amazon MSK**        | (Managed Streaming for Apache Kafka). Integrated with AWS services, offering simplified provisioning while retaining raw access to the underlying cluster configurations.    |
| **IBM Event Streams** | Focuses heavily on enterprise-grade security, auditing, and compliance capabilities built on top of the open-source Kafka core.                                                          |
