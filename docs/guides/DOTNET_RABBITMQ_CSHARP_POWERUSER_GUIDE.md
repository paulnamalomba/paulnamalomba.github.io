# DOTNET RabbitMQ PowerUser Guide (C#)

**Last updated**: December 05, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/.NET-RabbitMQ-blue.svg)](https://www.rabbitmq.com/dotnet.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

RabbitMQ is a robust message broker implementing AMQP 0-9-1 protocol for asynchronous communication between distributed systems. This guide covers connection management, queue/exchange configuration, message publishing/consuming, acknowledgements, prefetch settings, and TLS security using the official .NET client library. Power users need to understand durability, routing patterns, dead-letter queues, and high-availability strategies for production message-driven architectures.

## Contents

- [DOTNET RabbitMQ PowerUser Guide (C#)](#dotnet-rabbitmq-poweruser-guide-c)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Basic Message Publishing and Consuming](#basic-message-publishing-and-consuming)
    - [Exchange Routing Patterns](#exchange-routing-patterns)
    - [ASP.NET Core Integration with Dependency Injection](#aspnet-core-integration-with-dependency-injection)
    - [Dead Letter Exchange and Retry Strategy](#dead-letter-exchange-and-retry-strategy)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install package**: `dotnet add package RabbitMQ.Client`
2. **Create connection factory**: Configure hostname, port, and credentials
3. **Publish message**: Create channel, declare queue, publish byte array with routing key
4. **Consume message**: Create consumer, bind to queue, process messages with manual acknowledgement
5. **Enable durability**: Set durable flags on queues and persistent delivery mode on messages

## Key Concepts

- **Connection**: Long-lived TCP connection to RabbitMQ broker; expensive to create, should be reused across application
- **Channel**: Lightweight virtual connection multiplexed over a single TCP connection; used for all AMQP operations
- **Exchange**: Message routing component that receives messages and routes to queues based on bindings and routing keys; types include direct, topic, fanout, headers
- **Queue**: Buffer that stores messages until consumed; can be durable (survives broker restart) or transient
- **Binding**: Link between exchange and queue with optional routing key pattern for message filtering
- **Acknowledgement (Ack)**: Consumer confirms message processing; manual ack provides at-least-once delivery guarantee
- **Prefetch (QoS)**: Limits number of unacknowledged messages per consumer; prevents overwhelming slow consumers

## Configuration and Best Practices

**Connection Factory Configuration**:

```csharp
var factory = new ConnectionFactory
{
    HostName = "localhost",
    Port = 5672,
    UserName = "guest",
    Password = "guest",
    VirtualHost = "/",

    // Connection pooling and timeout settings
    RequestedHeartbeat = TimeSpan.FromSeconds(60),
    NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
    AutomaticRecoveryEnabled = true,
    TopologyRecoveryEnabled = true,

    // Performance tuning
    RequestedChannelMax = 2047,
    RequestedFrameMax = 131072,

    // TLS/SSL configuration
    Ssl = new SslOption
    {
        Enabled = true,
        ServerName = "rabbitmq.example.com",
        AcceptablePolicyErrors = SslPolicyErrors.RemoteCertificateNameMismatch
    }
};
```

**Best Practices**:

- Create one connection per application; share across threads
- Use one channel per thread; channels are not thread-safe
- Always declare queues and exchanges before publishing to ensure they exist
- Set `durable = true` for queues and `persistent = true` for messages in production
- Implement manual acknowledgements with proper error handling
- Use prefetch (QoS) to limit unacknowledged messages per consumer
- Enable automatic recovery for connection failures
- Set heartbeat interval to detect network failures quickly

## Security Considerations

1. **Authentication**: Use strong credentials; avoid default `guest/guest` in production; integrate with LDAP or OAuth
2. **TLS Encryption**: Enable SSL/TLS for all connections; use valid certificates; disable weak cipher suites
3. **Virtual Hosts**: Isolate environments using virtual hosts; restrict user permissions per vhost
4. **Access Control**: Use fine-grained permissions (configure, write, read) per user and resource
5. **Message Validation**: Sanitize and validate all message payloads; implement schema validation
6. **Network Security**: Bind RabbitMQ to specific interfaces; use firewall rules; avoid exposing management plugin publicly
7. **Audit Logging**: Enable audit logs for security events; monitor failed login attempts and permission violations

**Secure Connection Setup**:

```csharp
var factory = new ConnectionFactory
{
    HostName = "rabbitmq.production.com",
    Port = 5671, // TLS port
    UserName = Environment.GetEnvironmentVariable("RABBITMQ_USER"),
    Password = Environment.GetEnvironmentVariable("RABBITMQ_PASSWORD"),
    VirtualHost = "/production",

    Ssl = new SslOption
    {
        Enabled = true,
        ServerName = "rabbitmq.production.com",
        Version = System.Security.Authentication.SslProtocols.Tls12 | System.Security.Authentication.SslProtocols.Tls13,
        AcceptablePolicyErrors = SslPolicyErrors.None, // Strict certificate validation
        CertPath = "/path/to/client-cert.pfx",
        CertPassphrase = Environment.GetEnvironmentVariable("CERT_PASSWORD")
    },

    AutomaticRecoveryEnabled = true,
    NetworkRecoveryInterval = TimeSpan.FromSeconds(10)
};
```

## Examples

### Basic Message Publishing and Consuming

Create durable queues, publish messages with persistence, and consume with manual acknowledgements for reliable delivery.

```csharp
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;

public class BasicMessagingExample
{
    public void PublishMessage()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };

        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare durable queue (survives broker restart)
        channel.QueueDeclare(
            queue: "task_queue",
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null
        );

        string message = "Hello RabbitMQ!";
        var body = Encoding.UTF8.GetBytes(message);

        // Publish persistent message
        var properties = channel.CreateBasicProperties();
        properties.Persistent = true; // Survive broker restart

        channel.BasicPublish(
            exchange: "",
            routingKey: "task_queue",
            basicProperties: properties,
            body: body
        );

        Console.WriteLine($" [x] Sent: {message}");
    }

    public void ConsumeMessages()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };

        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare queue (idempotent operation)
        channel.QueueDeclare(
            queue: "task_queue",
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null
        );

        // Set prefetch count (QoS) - process one message at a time
        channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);

        Console.WriteLine(" [*] Waiting for messages...");

        var consumer = new EventingBasicConsumer(channel);
        consumer.Received += (model, ea) =>
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);

            Console.WriteLine($" [x] Received: {message}");

            try
            {
                // Simulate work
                Thread.Sleep(1000);

                // Manual acknowledgement (confirms successful processing)
                channel.BasicAck(deliveryTag: ea.DeliveryTag, multiple: false);
                Console.WriteLine(" [x] Done");
            }
            catch (Exception ex)
            {
                Console.WriteLine($" [!] Error: {ex.Message}");
                // Reject and requeue message on failure
                channel.BasicNack(deliveryTag: ea.DeliveryTag, multiple: false, requeue: true);
            }
        };

        // Start consuming with manual ack
        channel.BasicConsume(
            queue: "task_queue",
            autoAck: false, // Manual acknowledgement for reliability
            consumer: consumer
        );

        Console.WriteLine("Press [enter] to exit.");
        Console.ReadLine();
    }
}
```

### Exchange Routing Patterns

Implement direct, topic, and fanout exchange patterns for flexible message routing across multiple consumers.

```csharp
using RabbitMQ.Client;
using System.Text;

public class ExchangeRoutingExample
{
    // Direct Exchange: Route based on exact routing key match
    public void DirectExchangePublisher()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare direct exchange
        channel.ExchangeDeclare(
            exchange: "logs_direct",
            type: ExchangeType.Direct,
            durable: true
        );

        string[] severities = { "info", "warning", "error" };

        foreach (var severity in severities)
        {
            string message = $"Log message with severity: {severity}";
            var body = Encoding.UTF8.GetBytes(message);

            channel.BasicPublish(
                exchange: "logs_direct",
                routingKey: severity,
                basicProperties: null,
                body: body
            );

            Console.WriteLine($" [x] Sent '{severity}': {message}");
        }
    }

    // Topic Exchange: Route based on pattern matching (wildcard routing keys)
    public void TopicExchangePublisher()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare topic exchange
        channel.ExchangeDeclare(
            exchange: "logs_topic",
            type: ExchangeType.Topic,
            durable: true
        );

        var messages = new Dictionary<string, string>
        {
            { "kern.critical", "Kernel critical error" },
            { "kern.info", "Kernel info message" },
            { "app.error", "Application error" },
            { "app.debug", "Application debug info" }
        };

        foreach (var (routingKey, message) in messages)
        {
            var body = Encoding.UTF8.GetBytes(message);

            channel.BasicPublish(
                exchange: "logs_topic",
                routingKey: routingKey,
                basicProperties: null,
                body: body
            );

            Console.WriteLine($" [x] Sent '{routingKey}': {message}");
        }
    }

    // Topic Exchange Consumer with wildcard binding
    public void TopicExchangeConsumer(string bindingKey)
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        channel.ExchangeDeclare(
            exchange: "logs_topic",
            type: ExchangeType.Topic,
            durable: true
        );

        // Create exclusive queue for this consumer
        var queueName = channel.QueueDeclare().QueueName;

        // Bind with wildcard pattern
        // "kern.*" matches all kern messages
        // "*.critical" matches all critical messages
        // "#" matches all messages
        channel.QueueBind(
            queue: queueName,
            exchange: "logs_topic",
            routingKey: bindingKey
        );

        Console.WriteLine($" [*] Waiting for messages matching '{bindingKey}'...");

        var consumer = new EventingBasicConsumer(channel);
        consumer.Received += (model, ea) =>
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);
            var routingKey = ea.RoutingKey;

            Console.WriteLine($" [x] Received '{routingKey}': {message}");
        };

        channel.BasicConsume(queue: queueName, autoAck: true, consumer: consumer);
        Console.ReadLine();
    }

    // Fanout Exchange: Broadcast to all bound queues (pub/sub pattern)
    public void FanoutExchangePublisher()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare fanout exchange
        channel.ExchangeDeclare(
            exchange: "notifications",
            type: ExchangeType.Fanout,
            durable: false
        );

        string message = "System notification: Server maintenance in 5 minutes";
        var body = Encoding.UTF8.GetBytes(message);

        // Routing key is ignored for fanout exchanges
        channel.BasicPublish(
            exchange: "notifications",
            routingKey: "",
            basicProperties: null,
            body: body
        );

        Console.WriteLine($" [x] Broadcast: {message}");
    }
}
```

### ASP.NET Core Integration with Dependency Injection

Implement RabbitMQ producer and consumer services with proper connection management and graceful shutdown in ASP.NET Core.

```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Text.Json;

// Configuration model
public class RabbitMqSettings
{
    public string HostName { get; set; } = "localhost";
    public int Port { get; set; } = 5672;
    public string UserName { get; set; } = "guest";
    public string Password { get; set; } = "guest";
    public string VirtualHost { get; set; } = "/";
}

// Connection provider (singleton)
public interface IRabbitMqConnectionProvider : IDisposable
{
    IConnection GetConnection();
}

public class RabbitMqConnectionProvider : IRabbitMqConnectionProvider
{
    private readonly IConnection _connection;
    private bool _disposed;

    public RabbitMqConnectionProvider(IOptions<RabbitMqSettings> settings)
    {
        var factory = new ConnectionFactory
        {
            HostName = settings.Value.HostName,
            Port = settings.Value.Port,
            UserName = settings.Value.UserName,
            Password = settings.Value.Password,
            VirtualHost = settings.Value.VirtualHost,
            AutomaticRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
            RequestedHeartbeat = TimeSpan.FromSeconds(60)
        };

        _connection = factory.CreateConnection();
    }

    public IConnection GetConnection() => _connection;

    public void Dispose()
    {
        if (_disposed) return;
        _connection?.Close();
        _connection?.Dispose();
        _disposed = true;
    }
}

// Message publisher service
public interface IMessagePublisher
{
    Task PublishAsync<T>(string queueName, T message) where T : class;
}

public class RabbitMqPublisher : IMessagePublisher
{
    private readonly IRabbitMqConnectionProvider _connectionProvider;
    private readonly ILogger<RabbitMqPublisher> _logger;

    public RabbitMqPublisher(
        IRabbitMqConnectionProvider connectionProvider,
        ILogger<RabbitMqPublisher> logger)
    {
        _connectionProvider = connectionProvider;
        _logger = logger;
    }

    public Task PublishAsync<T>(string queueName, T message) where T : class
    {
        return Task.Run(() =>
        {
            using var channel = _connectionProvider.GetConnection().CreateModel();

            // Declare durable queue
            channel.QueueDeclare(
                queue: queueName,
                durable: true,
                exclusive: false,
                autoDelete: false,
                arguments: null
            );

            // Serialize message to JSON
            var json = JsonSerializer.Serialize(message);
            var body = Encoding.UTF8.GetBytes(json);

            // Set persistent delivery mode
            var properties = channel.CreateBasicProperties();
            properties.Persistent = true;
            properties.ContentType = "application/json";
            properties.Timestamp = new AmqpTimestamp(DateTimeOffset.UtcNow.ToUnixTimeSeconds());

            channel.BasicPublish(
                exchange: "",
                routingKey: queueName,
                basicProperties: properties,
                body: body
            );

            _logger.LogInformation(
                "Published message to queue {Queue}: {Message}",
                queueName, json);
        });
    }
}

// Background consumer service
public class RabbitMqConsumerService : BackgroundService
{
    private readonly IRabbitMqConnectionProvider _connectionProvider;
    private readonly ILogger<RabbitMqConsumerService> _logger;
    private readonly IServiceProvider _serviceProvider;
    private IModel _channel;

    public RabbitMqConsumerService(
        IRabbitMqConnectionProvider connectionProvider,
        ILogger<RabbitMqConsumerService> logger,
        IServiceProvider serviceProvider)
    {
        _connectionProvider = connectionProvider;
        _logger = logger;
        _serviceProvider = serviceProvider;
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _channel = _connectionProvider.GetConnection().CreateModel();

        const string queueName = "orders_queue";

        _channel.QueueDeclare(
            queue: queueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null
        );

        _channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);

        var consumer = new EventingBasicConsumer(_channel);
        consumer.Received += async (model, ea) =>
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);

            _logger.LogInformation("Received message from {Queue}: {Message}", queueName, message);

            try
            {
                // Process message using scoped service
                using var scope = _serviceProvider.CreateScope();
                var orderService = scope.ServiceProvider.GetRequiredService<IOrderService>();

                var order = JsonSerializer.Deserialize<Order>(message);
                await orderService.ProcessOrderAsync(order);

                // Acknowledge successful processing
                _channel.BasicAck(deliveryTag: ea.DeliveryTag, multiple: false);
                _logger.LogInformation("Message processed successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing message");

                // Reject and requeue on failure
                _channel.BasicNack(
                    deliveryTag: ea.DeliveryTag,
                    multiple: false,
                    requeue: true);
            }
        };

        _channel.BasicConsume(
            queue: queueName,
            autoAck: false,
            consumer: consumer
        );

        _logger.LogInformation("Consumer service started for queue {Queue}", queueName);

        return Task.CompletedTask;
    }

    public override void Dispose()
    {
        _channel?.Close();
        _channel?.Dispose();
        base.Dispose();
    }
}

// Startup configuration
public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // Register RabbitMQ services
        builder.Services.Configure<RabbitMqSettings>(
            builder.Configuration.GetSection("RabbitMq"));

        builder.Services.AddSingleton<IRabbitMqConnectionProvider, RabbitMqConnectionProvider>();
        builder.Services.AddScoped<IMessagePublisher, RabbitMqPublisher>();
        builder.Services.AddHostedService<RabbitMqConsumerService>();

        // Register application services
        builder.Services.AddScoped<IOrderService, OrderService>();

        var app = builder.Build();
        app.Run();
    }
}

// Models
public class Order
{
    public Guid Id { get; set; }
    public string CustomerName { get; set; }
    public decimal TotalAmount { get; set; }
    public DateTime CreatedAt { get; set; }
}

public interface IOrderService
{
    Task ProcessOrderAsync(Order order);
}
```

### Dead Letter Exchange and Retry Strategy

Implement dead letter queues for handling failed messages with automatic retry logic and exponential backoff.

```csharp
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Text.Json;

public class DeadLetterExchangeExample
{
    public void SetupQueuesWithDLX()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        // Declare dead letter exchange
        channel.ExchangeDeclare(
            exchange: "dlx",
            type: ExchangeType.Direct,
            durable: true
        );

        // Declare dead letter queue
        channel.QueueDeclare(
            queue: "failed_messages",
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null
        );

        channel.QueueBind(
            queue: "failed_messages",
            exchange: "dlx",
            routingKey: "failed"
        );

        // Declare main queue with DLX configuration
        var arguments = new Dictionary<string, object>
        {
            { "x-dead-letter-exchange", "dlx" },
            { "x-dead-letter-routing-key", "failed" },
            { "x-message-ttl", 60000 } // 60 seconds TTL (optional)
        };

        channel.QueueDeclare(
            queue: "orders_queue",
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: arguments
        );

        Console.WriteLine("Queues and DLX configured successfully");
    }

    public void ConsumeWithRetryLogic()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);

        var consumer = new EventingBasicConsumer(channel);
        consumer.Received += (model, ea) =>
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);

            // Get retry count from headers
            int retryCount = 0;
            if (ea.BasicProperties.Headers != null &&
                ea.BasicProperties.Headers.TryGetValue("x-retry-count", out var retryObj))
            {
                retryCount = Convert.ToInt32(retryObj);
            }

            Console.WriteLine($" [x] Processing (attempt {retryCount + 1}): {message}");

            try
            {
                // Simulate processing that might fail
                if (new Random().Next(3) == 0)
                {
                    throw new Exception("Simulated processing error");
                }

                // Successful processing
                channel.BasicAck(deliveryTag: ea.DeliveryTag, multiple: false);
                Console.WriteLine(" [x] Message processed successfully");
            }
            catch (Exception ex)
            {
                Console.WriteLine($" [!] Error: {ex.Message}");

                const int maxRetries = 3;

                if (retryCount < maxRetries)
                {
                    // Retry with exponential backoff
                    var delay = TimeSpan.FromSeconds(Math.Pow(2, retryCount));

                    var retryProperties = channel.CreateBasicProperties();
                    retryProperties.Persistent = true;
                    retryProperties.Headers = new Dictionary<string, object>
                    {
                        { "x-retry-count", retryCount + 1 },
                        { "x-original-routing-key", ea.RoutingKey }
                    };

                    // Publish to retry queue with delay
                    var retryQueueArgs = new Dictionary<string, object>
                    {
                        { "x-message-ttl", (int)delay.TotalMilliseconds },
                        { "x-dead-letter-exchange", "" },
                        { "x-dead-letter-routing-key", "orders_queue" }
                    };

                    var retryQueueName = $"retry_{delay.TotalSeconds}s";
                    channel.QueueDeclare(
                        queue: retryQueueName,
                        durable: true,
                        exclusive: false,
                        autoDelete: false,
                        arguments: retryQueueArgs
                    );

                    channel.BasicPublish(
                        exchange: "",
                        routingKey: retryQueueName,
                        basicProperties: retryProperties,
                        body: body
                    );

                    // Ack original message (moved to retry queue)
                    channel.BasicAck(deliveryTag: ea.DeliveryTag, multiple: false);
                    Console.WriteLine($" [x] Scheduled retry in {delay.TotalSeconds}s (attempt {retryCount + 2}/{maxRetries + 1})");
                }
                else
                {
                    // Max retries exceeded - send to DLX
                    channel.BasicReject(deliveryTag: ea.DeliveryTag, requeue: false);
                    Console.WriteLine($" [x] Max retries exceeded. Message sent to dead letter queue.");
                }
            }
        };

        channel.BasicConsume(
            queue: "orders_queue",
            autoAck: false,
            consumer: consumer
        );

        Console.WriteLine(" [*] Waiting for messages. Press [enter] to exit.");
        Console.ReadLine();
    }

    // Monitor and process failed messages
    public void ProcessDeadLetterQueue()
    {
        var factory = new ConnectionFactory { HostName = "localhost" };
        using var connection = factory.CreateConnection();
        using var channel = connection.CreateModel();

        var consumer = new EventingBasicConsumer(channel);
        consumer.Received += (model, ea) =>
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);

            Console.WriteLine($" [DLQ] Failed message: {message}");

            // Log to monitoring system, alert ops team, store for manual review
            LogFailedMessage(message, ea.BasicProperties.Headers);

            // Acknowledge DLQ message
            channel.BasicAck(deliveryTag: ea.DeliveryTag, multiple: false);
        };

        channel.BasicConsume(
            queue: "failed_messages",
            autoAck: false,
            consumer: consumer
        );

        Console.WriteLine(" [*] Monitoring dead letter queue...");
        Console.ReadLine();
    }

    private void LogFailedMessage(string message, IDictionary<string, object> headers)
    {
        var log = new
        {
            Timestamp = DateTime.UtcNow,
            Message = message,
            Headers = headers,
            Source = "RabbitMQ Dead Letter Queue"
        };

        Console.WriteLine(JsonSerializer.Serialize(log, new JsonSerializerOptions { WriteIndented = true }));
    }
}
```

## Troubleshooting

**Connection Refused**:

- **Error**: "None of the specified endpoints were reachable"
  - **Check service**: Verify RabbitMQ is running: `rabbitmqctl status`
  - **Check firewall**: Ensure port 5672 (AMQP) or 5671 (AMQPS) is open
  - **Check hostname**: Verify DNS resolution or use IP address
  - **Check credentials**: Test with `rabbitmqctl authenticate_user username password`

**Channel Shutdown Errors**:

- **Error**: "Channel shutdown: PRECONDITION_FAILED"
  - **Queue mismatch**: Declaring queue with different parameters than existing
  - **Fix**: Delete queue or use matching parameters (durable, exclusive, autodelete)
  - **Check**: Use RabbitMQ management UI to inspect queue configuration

**Memory/Disk Alarms**:

- **Error**: "Connection blocked: LOW on memory/disk"
  - **Check status**: `rabbitmqctl status` to see alarm details
  - **Clear disk**: Free up disk space (RabbitMQ needs 50MB minimum)
  - **Increase memory**: Configure `vm_memory_high_watermark` in rabbitmq.conf
  - **Temporary fix**: Clear alarms with `rabbitmqctl eval 'rabbit_alarm:clear_alarm(disk_limit).'`

**Message Loss**:

```csharp
// Ensure durability at all levels
var factory = new ConnectionFactory
{
    AutomaticRecoveryEnabled = true, // Recover connections automatically
    TopologyRecoveryEnabled = true   // Recreate queues/exchanges on recovery
};

using var connection = factory.CreateConnection();
using var channel = connection.CreateModel();

// Durable queue
channel.QueueDeclare(queue: "important_queue", durable: true, ...);

// Persistent messages
var properties = channel.CreateBasicProperties();
properties.Persistent = true;
properties.DeliveryMode = 2; // Persistent

// Manual acknowledgements
channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);
consumer.Received += (model, ea) =>
{
    // Process message
    channel.BasicAck(ea.DeliveryTag, multiple: false);
};
```

**Common Logs**:

- RabbitMQ logs: `/var/log/rabbitmq/rabbit@hostname.log`
- Check with: `rabbitmqctl log_tail`
- Management UI: `http://localhost:15672` (default guest/guest)

## Performance and Tuning

**Connection and Channel Pooling**:

```csharp
public class RabbitMqChannelPool
{
    private readonly IConnection _connection;
    private readonly ConcurrentBag<IModel> _channels = new();
    private readonly SemaphoreSlim _semaphore;

    public RabbitMqChannelPool(ConnectionFactory factory, int maxChannels = 100)
    {
        _connection = factory.CreateConnection();
        _semaphore = new SemaphoreSlim(maxChannels);
    }

    public async Task<IModel> AcquireChannelAsync()
    {
        await _semaphore.WaitAsync();

        if (_channels.TryTake(out var channel) && channel.IsOpen)
        {
            return channel;
        }

        return _connection.CreateModel();
    }

    public void ReleaseChannel(IModel channel)
    {
        if (channel.IsOpen)
        {
            _channels.Add(channel);
        }
        else
        {
            channel.Dispose();
        }

        _semaphore.Release();
    }
}
```

**Prefetch (QoS) Configuration**:

```csharp
// Low prefetch (1-10) for slow/CPU-intensive consumers
channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);

// Medium prefetch (20-50) for balanced workloads
channel.BasicQos(prefetchSize: 0, prefetchCount: 30, global: false);

// High prefetch (100+) for fast/I/O-bound consumers
channel.BasicQos(prefetchSize: 0, prefetchCount: 100, global: false);
```

**Batch Publishing**:

```csharp
public void PublishBatch(IModel channel, string queueName, List<string> messages)
{
    // Use transactions for batching (slower but atomic)
    channel.TxSelect();

    foreach (var message in messages)
    {
        var body = Encoding.UTF8.GetBytes(message);
        channel.BasicPublish("", queueName, null, body);
    }

    channel.TxCommit();

    // OR use publisher confirms (faster, eventual consistency)
    channel.ConfirmSelect();

    foreach (var message in messages)
    {
        var body = Encoding.UTF8.GetBytes(message);
        channel.BasicPublish("", queueName, null, body);
    }

    channel.WaitForConfirmsOrDie(TimeSpan.FromSeconds(5));
}
```

**Monitoring Metrics**:

```csharp
// Get queue message count
var queueInfo = channel.QueueDeclarePassive("my_queue");
Console.WriteLine($"Messages: {queueInfo.MessageCount}");
Console.WriteLine($"Consumers: {queueInfo.ConsumerCount}");

// Use RabbitMQ Management API for detailed metrics
var httpClient = new HttpClient();
httpClient.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Basic",
        Convert.ToBase64String(Encoding.ASCII.GetBytes("guest:guest")));

var response = await httpClient.GetStringAsync("http://localhost:15672/api/queues");
Console.WriteLine(response);
```

**Performance Recommendations**:

- **Connections**: 1 per application (shared, thread-safe)
- **Channels**: 1 per thread or use pooling (not thread-safe)
- **Prefetch**: Start with 10-30, tune based on consumer performance
- **Message size**: Keep <128KB; use external storage for large payloads
- **Durability**: Trade-off with throughput; use transient queues for non-critical data
- **Clustering**: Use mirrored queues for HA; avoid clustering across WANs

## References and Further Reading

- [RabbitMQ .NET Client Documentation](https://www.rabbitmq.com/dotnet.html) - Official .NET client library guide
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html) - Step-by-step tutorials covering all patterns
- [AMQP 0-9-1 Protocol Reference](https://www.rabbitmq.com/amqp-0-9-1-reference.html) - Complete AMQP protocol specification
- [RabbitMQ Best Practices](https://www.cloudamqp.com/blog/part1-rabbitmq-best-practice.html) - Production deployment patterns
- [RabbitMQ Performance Testing](https://www.rabbitmq.com/blog/2012/04/25/rabbitmq-performance-measurements-part-2) - Benchmarking and tuning guide
