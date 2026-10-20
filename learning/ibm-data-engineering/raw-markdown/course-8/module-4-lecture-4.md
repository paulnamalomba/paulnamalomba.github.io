# Module 4, lecture 4: Kafka streaming process & stream topology

Systems that process finite element data or university enrollments need to transform and aggregate records as they move between components. Stream processing performs that work while the data is in transit.

This lecture shifts the focus from "dumb pipes" to smart, real-time computational pipelines using the **Kafka Streams API**.

---

## 1. The "ad hoc" Anti-Pattern

Before adopting a dedicated stream processing framework, engineers often default to the "Ad Hoc" approach.

Suppose you need to read raw weather JSON, filter out normal temperatures, and publish only "extreme weather" events to a dashboard.

- **The Naive Design:** You write a background service with a `while(true)` loop. It spins up a Kafka Consumer to read from `raw_weather_topic`, applies an `if` statement to check the temperature, and uses a Kafka Producer to send the result to `processed_weather_topic`.

Writing bespoke consumer-producer loops for every data transformation works for a single topic, but it is a fantastic way to introduce unmanageable tech debt when scaling an engineering team. Handling failure states, stateful aggregations (like "average temperature over the last 5 minutes"), and exactly-once processing becomes an algorithmic nightmare.

---

## 2. Enter Kafka streams API

The Kafka Streams API is a client library designed specifically to solve the complexities of event-driven data processing.

- **Native Integration:** Both its input and output are strictly Kafka topics.
- **Record-by-Record:** It processes events individually as they arrive (millisecond latency), rather than waiting for micro-batches.
- **Exactly-Once Semantics (EOS):** Through a combination of transactional producers and consumer offset management, it guarantees that even if a node crashes mid-computation, a record is processed and reflected in the state store exactly once.

---

## 3. Stream processing topology (the DAG)

The Kafka Streams API organizes processing logic as a **computational graph** called a Stream Processing Topology.

Mathematically, this topology is a Directed Acyclic Graph (DAG), denoted as $G = (V, E)$, where:

- The vertices $V$ are the **Stream Processors** (the computational logic).
- The edges $E$ are the **I/O Streams** (the data flowing between nodes).

There are three primary types of processors in this DAG:

1. **Source Processor:** The entry point. It has no upstream nodes. It is an embedded consumer, continuously reading records from one or more Kafka topics and pushing them into the topology.
2. **Stream Processor:** The intermediary nodes. These apply data transformations—mapping, filtering, formatting, or joining streams together.
3. **Sink Processor:** The exit point. It has no downstream nodes. It is an embedded producer, publishing the final transformed records back into a new Kafka topic.

---

## 4. Technical implementation in .NET/C#

Natively, Kafka Streams is a Java library. However, in the .NET ecosystem, the gold standard for achieving the exact same topological processing is **`Streamiz.Kafka.Net`** (a highly mature, open-source C# port of the Kafka Streams API).

Here is how you would programmatically construct the extreme weather topology using C#:

```csharp
using System;
using System.Threading.Tasks;
using Streamiz.Kafka.Net;
using Streamiz.Kafka.Net.SerDes;
using Streamiz.Kafka.Net.Stream;

public class WeatherTopologyManager
{
    public static async Task StartTopologyAsync()
    {
        // 1. Configure the Stream Application
        var config = new StreamConfig<StringSerDes, StringSerDes>
        {
            ApplicationId = "weather-processor-app",
            BootstrapServers = "localhost:9092",
            AutoOffsetReset = Confluent.Kafka.AutoOffsetReset.Earliest
        };

        // 2. Build the DAG Topology
        StreamBuilder builder = new StreamBuilder();

        // SOURCE NODE: Consume from raw_weather_topic
        builder.Stream<string, string>("raw_weather_topic")

               // STREAM PROCESSOR NODE: Filter logic
               .Filter((key, weatherJson) =>
               {
                   // Assume a hypothetical ParseAndCheck method
                   return ParseAndCheckHighTemp(weatherJson);
               })

               // SINK NODE: Publish to processed_weather_topic
               .To("processed_weather_topic");

        Topology topology = builder.Build();

        // 3. Execute the Stream
        KafkaStream stream = new KafkaStream(topology, config);

        Console.CancelKeyPress += (o, e) => { stream.Dispose(); };
        await stream.StartAsync();
    }

    private static bool ParseAndCheckHighTemp(string json)
    {
        // Implementation to deserialize JSON and check temp > threshold
        return true;
    }
}

```

---

### Architectural synthesis

By utilizing a Stream Builder topology, you offload the heavy lifting of network I/O, threading models, and fault tolerance to the underlying library. You define the _logic_ of the pipeline, and the API manages the _execution_.

When transitioning from the high-throughput batch runs of your structural engineering software to the real-time needs of web systems, this DAG-based streaming model is what prevents database locks and API timeouts.
