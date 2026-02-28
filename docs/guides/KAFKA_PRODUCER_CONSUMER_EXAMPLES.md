# Distributed Event Streaming Platform Components

<br>
**Last updated**: February 28, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Framework](https://img.shields.io/badge/Enterprise-Auth_Services-blue.svg)](https://learn.microsoft.com/en-us/azure/active-directory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

this document serves to ddescribe the instantiation of prudoducer consumer archetecture for Apache Kafka, which is a distributed message/streaming platform.

## Contents

- [Distributed Event Streaming Platform Components](#distributed-event-streaming-platform-components)
  - [Overview](#overview)
  - [Contents](#contents)
    - [1. Prerequisites](#1-prerequisites)
    - [2. The Producer: Fire and Forget (or Acknowledge)](#2-the-producer-fire-and-forget-or-acknowledge)
    - [3. The Consumer: The Infinite Polling Loop](#3-the-consumer-the-infinite-polling-loop)
    - [Architectural Considerations for the Pipeline](#architectural-considerations-for-the-pipeline)

---

### 1. Prerequisites

#Implementing a robust event streaming layer in C# relies almost exclusively on the `Confluent.Kafka` library. It is a highly optimized .NET wrapper around the native C `librdkafka` library, meaning it delivers the raw throughput required for high-volume backend systems while exposing a clean, asynchronous C# API.

First, you need the NuGet package.

```bash
dotnet add package Confluent.Kafka

```

To keep the data model immutable and thread-safe, we will define our event using a C# `record`:

```csharp
using System.Text.Json;

public record EnrollmentEvent(string StudentId, string CourseCode, DateTimeOffset Timestamp);

```

---

### 2. The Producer: Fire and Forget (or Acknowledge)

The Producer's job is to serialize the event and route it to the correct Kafka broker and topic. For critical backend pipelines, we use `ProduceAsync` to ensure we receive a delivery acknowledgment (an offset) from the broker without blocking the calling thread.

```csharp
using System;
using System.Text.Json;
using System.Threading.Tasks;
using Confluent.Kafka;

public class KafkaEventProducer
{
    private readonly string _topic = "enrollment-requests";
    private readonly ProducerConfig _config;

    public KafkaEventProducer(string bootstrapServers)
    {
        _config = new ProducerConfig
        {
            BootstrapServers = bootstrapServers,
            // Acks.All ensures the leader AND all replicas acknowledge the message.
            // Slower, but prevents data loss in a distributed cluster.
            Acks = Acks.All 
        };
    }

    public async Task PublishEnrollmentAsync(EnrollmentEvent evt)
    {
        // The producer handles unmanaged resources, so 'using' is mandatory 
        // to prevent catastrophic memory leaks in a long-running service.
        using var producer = new ProducerBuilder<string, string>(_config).Build();

        try
        {
            var message = new Message<string, string>
            {
                Key = evt.StudentId, // Hashing by StudentId ensures chronological order per student
                Value = JsonSerializer.Serialize(evt)
            };

            var deliveryResult = await producer.ProduceAsync(_topic, message);
            
            Console.WriteLine($"Delivered '{deliveryResult.Value}' to '{deliveryResult.TopicPartitionOffset}'");
        }
        catch (ProduceException<string, string> e)
        {
            Console.WriteLine($"Delivery failed: {e.Error.Reason}");
            // In a production pipeline, this is where you route to a Dead Letter Queue (DLQ)
        }
    }
}

```

---

### 3. The Consumer: The Infinite Polling Loop

Unlike HTTP endpoints that passively wait for requests, Kafka Consumers actively poll the broker for new data. They are designed to run continuously in a background service.

A critical concept here is the `GroupId`. Kafka tracks which messages have been read based on this group ID. If a consumer crashes and restarts, it resumes from the last committed offset for its group.

```csharp
using System;
using System.Threading;
using Confluent.Kafka;

public class KafkaEventConsumer
{
    private readonly string _topic = "enrollment-requests";
    private readonly ConsumerConfig _config;

    public KafkaEventConsumer(string bootstrapServers, string groupId)
    {
        _config = new ConsumerConfig
        {
            BootstrapServers = bootstrapServers,
            GroupId = groupId,
            // If there is no previous offset, start reading from the earliest available message
            AutoOffsetReset = AutoOffsetReset.Earliest, 
            EnableAutoCommit = true // For absolute control, set to false and commit manually after processing
        };
    }

    public void StartConsuming(CancellationToken cancellationToken)
    {
        using var consumer = new ConsumerBuilder<string, string>(_config).Build();
        consumer.Subscribe(_topic);

        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                // The Consume method blocks until a message is available or the token is canceled.
                var consumeResult = consumer.Consume(cancellationToken);
                
                Console.WriteLine($"Processing enrollment for Student: {consumeResult.Message.Key}");
                
                // Processing logic goes here...
            }
        }
        catch (OperationCanceledException)
        {
            // Graceful exit triggered by the cancellation token.
            Console.WriteLine("Closing consumer gracefully.");
        }
        finally
        {
            // This ensures the consumer leaves the group cleanly and partition locks are released.
            // Without this, the broker waits for a timeout before reassigning partitions.
            consumer.Close(); 
        }
    }
}

```

---

### Architectural Considerations for the Pipeline

* **Partitioning Keys:** In the producer code, `evt.StudentId` is explicitly set as the `Key`. Kafka guarantees order *only* within a specific partition. By keying on the `StudentId`, you ensure that all events for a specific student go to the same partition and are processed sequentially.
* **Idempotency:** A dry reality of distributed systems is that the network will eventually lie to you. The producer might send a message, the broker might save it, but the acknowledgment fails. The producer will retry, resulting in a duplicate. Your downstream database logic must be idempotent (e.g., using `UPSERT` statements) to handle this gracefully.