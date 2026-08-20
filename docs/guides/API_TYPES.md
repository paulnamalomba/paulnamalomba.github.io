# API TYPES Deep Dive: Modern API Architectures & Protocols

<br>
**Last updated**: December 29, 2025<br>
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

This document provides a comprehensive overview of the most widely used API architectures and protocols in modern software development. It covers REST, SOAP, gRPC, GraphQL, WebHooks, WebSockets, and WebRTC, explaining their technical cores, how they work, language support, reasons for use, and real-world industry applications.

## Contents

- [API TYPES Deep Dive: Modern API Architectures \& Protocols](#api-types-deep-dive-modern-api-architectures--protocols)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. REST API (Representational State Transfer)](#1-rest-api-representational-state-transfer)
    - [Technical Core](#technical-core)
    - [How it Works](#how-it-works)
    - [Language Support](#language-support)
    - [Why it is used](#why-it-is-used)
    - [Industry Application: The Public Web \& SaaS](#industry-application-the-public-web--saas)
  - [2. SOAP API (Simple Object Access Protocol)](#2-soap-api-simple-object-access-protocol)
    - [Technical Core](#technical-core-1)
    - [How it Works](#how-it-works-1)
    - [Language Support](#language-support-1)
    - [Why it is used](#why-it-is-used-1)
    - [Industry Application: Finance \& Legacy Enterprise](#industry-application-finance--legacy-enterprise)
  - [3. gRPC API (Google Remote Procedure Call)](#3-grpc-api-google-remote-procedure-call)
    - [Technical Core](#technical-core-2)
    - [How it Works](#how-it-works-2)
    - [Language Support](#language-support-2)
    - [Why it is used](#why-it-is-used-2)
    - [Industry Application: Internal Microservices](#industry-application-internal-microservices)
  - [4. GraphQL API](#4-graphql-api)
    - [Technical Core](#technical-core-3)
    - [How it Works](#how-it-works-3)
    - [Language Support](#language-support-3)
    - [Why it is used](#why-it-is-used-3)
    - [Industry Application: Complex Frontends \& Mobile](#industry-application-complex-frontends--mobile)
  - [5. WebHooks](#5-webhooks)
    - [Technical Core](#technical-core-4)
    - [How it Works](#how-it-works-4)
    - [Language Support](#language-support-4)
    - [Why it is used](#why-it-is-used-4)
    - [Industry Application: Automation \& CI/CD](#industry-application-automation--cicd)
  - [6. WebSockets](#6-websockets)
    - [Technical Core](#technical-core-5)
    - [How it Works](#how-it-works-5)
    - [Language Support](#language-support-5)
    - [Why it is used](#why-it-is-used-5)
    - [Industry Application: Real-Time Interaction](#industry-application-real-time-interaction)
  - [7. WebRTC (Web Real-Time Communication)](#7-webrtc-web-real-time-communication)
    - [Technical Core](#technical-core-6)
    - [How it Works](#how-it-works-6)
    - [Language Support](#language-support-6)
    - [Why it is used](#why-it-is-used-6)
    - [Industry Application: Video Conferencing](#industry-application-video-conferencing)

---

## 1. REST API (Representational State Transfer)

**"The Standard of the Web"**

REST is not a protocol but an architectural style defined by Roy Fielding in 2000. It treats everything as a **resource**, accessible via a standard Uniform Resource Identifier (URI). It relies heavily on standard HTTP methods.

### Technical Core

- **Statelessness:** The server stores no client context between requests. Every request must contain all necessary information (auth tokens, parameters) to be understood.
- **Resource-Based:** Data is viewed as resources (nouns), e.g., `/users`, `/orders`.
- **Uniform Interface:** Uses standard HTTP verbs:
  - `GET`: Retrieve a resource.
  - `POST`: Create a new resource.
  - `PUT`: Update/Replace a resource.
  - `PATCH`: Partially update a resource.
  - `DELETE`: Remove a resource.
- **Caching:** Responses explicitly state if they can be cached to improve performance.

### How it Works

When you make a REST request, the client sends an HTTP request with a method (GET, POST, etc.), a URL representing the resource, headers (metadata), and optionally a body containing data. The server processes this stateless request, performs the action on the resource, and returns a response with a status code (200 for success, 404 for not found, 500 for error) and response body. The beauty of REST is that every request is independent; the server doesn't remember previous requests.

**Example Request & Response:**

```
GET /api/users/123 HTTP/1.1
Host: api.example.com
Authorization: Bearer token123
Content-Type: application/json

Response:
200 OK
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```

REST works by leveraging HTTP's inherent features: status codes indicate success/failure, headers transmit metadata, and the resource URI (the URL path) explicitly identifies what you're operating on. This makes it predictable and easy to understand.

### Language Support

REST is language-agnostic since it relies on standard HTTP. Nearly **every modern language** supports REST out-of-the-box:

- **JavaScript/Node.js:** `fetch()`, `axios`, `request`
- **Python:** `requests`, `httpx`, `urllib`
- **Java:** `HttpClient`, `RestTemplate`, `OkHttp`
- **C#/.NET:** `HttpClient`, `RestSharp`
- **Go:** `net/http`
- **Ruby:** `Net::HTTP`, `HTTParty`
- **PHP:** `cURL`, `Guzzle`

### Why it is used

REST is the de facto standard because it is **decoupled** and **cacheable**. It is human-readable (mostly JSON) and extremely widely supported. It allows frontend and backend teams to work independently as long as the API contract (schema) is respected.

### Industry Application: The Public Web & SaaS

- **Public APIs:** Companies like **Twitter (X)**, **Stripe**, and **Google Maps** use REST because it is easy for third-party developers to understand and integrate using standard tools (curl, Postman).
- **Microservices (External facing):** While internal microservices might use gRPC, the "Edge" service (API Gateway) usually exposes REST to mobile apps and browsers because browsers have native support for HTTP/1.1 and JSON.

---

## 2. SOAP API (Simple Object Access Protocol)

**"The Enterprise Fortress"**

SOAP is a protocol (unlike REST, which is a style). It is highly structured, strictly typed, and relies exclusively on XML. It was designed by Microsoft in 1998 to ensure programs running on different operating systems could communicate.

### Technical Core

- **WSDL (Web Services Description Language):** A rigorous XML document that defines the structure of the API. It acts as a strict contract; if the request doesn't match the WSDL, it fails.
- **Envelope Structure:**
  - `Header`: Meta-information (security, transactions).
  - `Body`: The actual message/data.
  - `Fault`: Error handling.
- **Transport Independence:** While usually sent over HTTP, SOAP can technically operate over SMTP (email), TCP, or JMS (Java Message Service).
- **ACID Compliance:** SOAP has built-in protocols for **WS-AtomicTransaction**, ensuring that a distributed transaction either fully succeeds or fully fails (crucial for money transfers).

### How it Works

SOAP requests are XML documents wrapped in an envelope. The client constructs a XML message (often using generated code from the WSDL), sends it via HTTP POST, and the server parses it, validates it against the WSDL, executes the operation, and returns another XML-wrapped response.

**Example SOAP Request:**

```xml
<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <TransferMoney xmlns="http://banking.example.com/">
      <FromAccount>12345</FromAccount>
      <ToAccount>67890</ToAccount>
      <Amount>1000</Amount>
    </TransferMoney>
  </soap:Body>
</soap:Envelope>
```

The WSDL file (an XML schema) defines every possible operation, the exact parameter names, types, and their order. This rigidity ensures that typos or incorrect data types are caught _before_ execution. If you send a string when an integer is expected, SOAP immediately rejects it.

SOAP also includes advanced features:

- **WS-Security:** Encrypts the entire message and signs it digitally, making it impossible to tamper with.
- **WS-AtomicTransaction:** Ensures that in a distributed transaction (A sends money to B, B sends to C), if any step fails, all steps are rolled back.

### Language Support

SOAP requires code generation tools since the strict typing is complex to handle manually:

- **Java:** `Apache Axis2`, `Apache CXF`, `JAX-WS`
- **C#/.NET:** `WCF (Windows Communication Foundation)`, `SOAP support built into Visual Studio`
- **Python:** `zeep`, `suds-community`
- **PHP:** `SoapClient`, `NuSOAP`
- **Go:** `github.com/hooklift/gowsdl`
- **Node.js:** `soap`, `easysoap`

Most tools auto-generate client code from the WSDL, so developers rarely hand-write SOAP messages.

### Why it is used

Developers choose SOAP when **security**, **transactional integrity**, and **strict contracts** are more important than development speed or bandwidth usage.

### Industry Application: Finance & Legacy Enterprise

- **Banking:** When transferring money between banks (SWIFT network, etc.), partial failure is unacceptable. SOAP's built-in transaction compliance ensures that money is not deducted from A without being added to B.
- **Telecommunications & Healthcare:** Systems requiring **WS-Security** (enterprise-grade security extensions) often rely on SOAP for handling sensitive patient data or billing records.

---

## 3. gRPC API (Google Remote Procedure Call)

**"The High-Performance Microservices Connector"**

Released by Google in 2015, gRPC is designed for low latency and high throughput. It connects services as if they were local functions within the same code base.

### Technical Core

- **Protocol Buffers (Protobuf):** Instead of text-based JSON, gRPC uses a binary format. Data is serialized into binary (1s and 0s) making it much smaller and faster to transmit and parse.
- **HTTP/2 Transport:** It runs exclusively on HTTP/2, enabling:
  - **Multiplexing:** Multiple requests sent over a single TCP connection.
  - **Header Compression:** Reducing overhead.
- **Streaming:** gRPC supports four modes:
  1.  Unary (Standard Request/Response).
  2.  Server Streaming (Server sends a stream of data).
  3.  Client Streaming (Client sends a stream of data).
  4.  Bidirectional Streaming (Both talk simultaneously).

### How it Works

You define your API using `.proto` files (Protocol Buffer definition files). These files specify message types (like Java classes) and service methods:

```proto
service UserService {
  rpc GetUser(UserID) returns (User);
  rpc ListUsers(Empty) returns (stream User);
  rpc UpdateUser(User) returns (Empty);
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

You then compile these `.proto` files using the `protoc` compiler, which generates client and server code in your target language. The compiler produces highly optimized code that serializes data into binary format (tiny, usually 3-10x smaller than JSON) and deserializes it with minimal CPU overhead.

**Performance Example:**

```
JSON: {"id": 123, "name": "John", "email": "john@example.com"}
= ~60 bytes

Protobuf binary: \x08\x7b\x12\x04John\x1a\x15john@example.com
= ~30 bytes (50% reduction)
```

With HTTP/2 multiplexing, you can send 100 gRPC requests over a single TCP connection simultaneously, whereas HTTP/1.1 requires separate connections, adding latency.

### Language Support

gRPC is officially supported by Google for major languages:

- **Go:** First-class support, `google.golang.org/grpc`
- **Java:** `io.grpc:grpc-java`
- **Python:** `grpcio` (PyPI)
- **Node.js/TypeScript:** `@grpc/grpc-js`
- **C++:** Official support for performance-critical applications
- **C#/.NET:** `Grpc.Net.Client`, `Grpc.AspNetCore`
- **Ruby:** `grpc` gem
- **PHP:** `grpc` extension

Community implementations also exist for Kotlin, Rust, Scala, and Swift.

### Why it is used

It is used to eliminate the "bloat" of JSON and HTTP/1.1. In a microservices architecture where Service A calls Service B thousands of times a second, the milliseconds saved by binary serialization add up to massive performance gains and cost savings.

### Industry Application: Internal Microservices

- **Netflix & Uber:** These companies have thousands of microservices. They use gRPC for internal communication (East-West traffic) to reduce latency and server load.
- **IoT Devices:** Because Protobuf messages are tiny, gRPC is excellent for communicating with low-power devices with poor internet connections.

---

## 4. GraphQL API

**"The Frontend's Best Friend"**

Developed by Facebook in 2012 (open-sourced in 2015), GraphQL is a query language for APIs. It shifts control from the server to the client.

### Technical Core

- **Single Endpoint:** Unlike REST (which has `/users`, `/posts`, `/comments`), GraphQL exposes one endpoint (usually `/graphql`).
- **Client-Driven Query:** The client sends a JSON body describing _exactly_ what it wants.
  - _Example:_ "Give me the user's name and their last 3 posts, but don't give me their address."
- **Solves Over-fetching/Under-fetching:**
  - _REST problem:_ To get a user and their posts, you might need 2 requests, or the server sends a massive object with data you don't need.
  - _GraphQL solution:_ You get exactly what you asked for in one trip.
- **Strongly Typed Schema:** The backend defines a schema (SDL), and the frontend can introspect it to know exactly what data is available.

### How it Works

You define a schema in GraphQL Schema Definition Language (SDL):

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  getUser(id: ID!): User
  listPosts: [Post!]!
}
```

The client sends a JSON query to the `/graphql` endpoint:

```json
POST /graphql
{
  "query": "{
    getUser(id: \"123\") {
      name
      email
      posts {
        title
      }
    }
  }"
}
```

The server parses this query, validates it against the schema, executes only the requested fields, and returns:

```json
{
  "data": {
    "getUser": {
      "name": "John Doe",
      "email": "john@example.com",
      "posts": [{ "title": "GraphQL Basics" }, { "title": "API Design" }]
    }
  }
}
```

Notice the client got _exactly_ what it asked for—no extra fields, no wasted bandwidth. The resolver functions on the backend fetch data from databases or other services and assemble the response.

**Key Concepts:**

- **Introspection:** The schema is queryable. Your client can ask "What fields are available on the User type?" and the server responds. This enables IDE autocomplete and documentation.
- **Aliases & Fragments:** Reduce query complexity for large applications.
- **Mutations:** Separate from queries, mutations represent write operations (creating, updating, deleting data).

### Language Support

GraphQL has implementations for virtually every language:

- **JavaScript/Node.js:** `apollo-server`, `graphql-js`, `express-graphql`
- **Python:** `graphene`, `strawberry`, `ariadne`
- **Java:** `graphql-java`, `DGS Framework`
- **Go:** `graphql-go`, `gqlgen`
- **C#/.NET:** `Hot Chocolate`, `GraphQL for .NET`
- **Ruby:** `graphql-ruby`
- **PHP:** `webonyx/graphql-php`
- **TypeScript:** `type-graphql`, `apollo-server-ts`

### Why it is used

It allows frontend teams to iterate fast without asking backend developers to build new endpoints for every UI change. It is ideal for complex relational data graphs.

### Industry Application: Complex Frontends & Mobile

- **Facebook & Shopify:** Complex dashboards where a single page loads user data, notifications, feed items, and ads simultaneously. GraphQL allows fetching all this in a single network call.
- **Mobile Apps:** For users with slow data, fetching only the specific fields required (reducing payload size) improves the user experience significantly.

---

## 5. WebHooks

**"The Reverse API"**

While most APIs are "request-based" (Client asks Server), WebHooks are "event-based" (Server tells Client). They are essentially user-defined HTTP callbacks.

### Technical Core

- **Event-Driven:** The interaction is triggered by an event (e.g., "Payment Successful"), not a request.
- **Registration:** The client registers a URL (e.g., `https://myapp.com/payment-hook`) with the provider.
- **Payload:** When the event happens, the provider sends an HTTP POST request with a JSON payload to the registered URL.
- **Retry Logic:** If the client's server is down (returns 500 error), good WebHook providers (like Stripe) will retry sending the event with exponential backoff.

### How it Works

The flow is reversed from typical APIs:

1. **Registration Phase:** Your app sends a request to the provider (e.g., Stripe) saying: "When a payment succeeds, send me a POST request to `https://myapp.com/webhooks/payment`."

2. **Event Occurs:** The provider's system processes a payment. Once it succeeds, the provider's system triggers the webhook.

3. **HTTP POST to Your Endpoint:** The provider sends an HTTP POST with a JSON payload:

```json
POST /webhooks/payment HTTP/1.1
Host: myapp.com
Content-Type: application/json
X-Stripe-Signature: t=1234567890,v1=abcd1234...

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_1234567890",
      "amount": 5000,
      "currency": "usd",
      "status": "succeeded"
    }
  }
}
```

4. **Your Server Responds:** Your server must respond with a `200 OK` status within a timeout (usually 3-5 seconds) to acknowledge receipt.

5. **Retry Logic:** If your server doesn't respond (timeout or 5xx error), the provider retries with exponential backoff: 5 seconds, then 5 minutes, then 30 minutes, etc.

**Security Considerations:**

- **Signatures:** Providers sign the webhook payload using a secret key. Your app must verify the signature to ensure the webhook came from the provider, not a malicious actor.
- **Idempotency:** Webhooks might be delivered twice (due to retries). Your app must handle duplicate deliveries gracefully (store processed IDs, check for duplicates).

### Language Support

WebHooks are just HTTP POST requests, so every language supports them:

- **Node.js/Express.js:** `app.post('/webhook', (req, res) => {})`
- **Python/Flask:** `@app.route('/webhook', methods=['POST'])`
- **Java/Spring Boot:** `@PostMapping("/webhook")`
- **C#/ASP.NET:** `[HttpPost("/webhook")]`
- **PHP:** `$_POST` superglobal or `php://input`
- **Go:** `http.HandleFunc("/webhook", handler)`
- **Ruby/Rails:** `post '/webhook' do`

Security libraries for signature verification are available in all languages (e.g., `stripe-python`, `stripe-node`).

### Why it is used

To avoid **Polling**. Without WebHooks, a client would have to ask the server every 5 seconds: "Is the payment done? Is the payment done?" This wastes massive resources. WebHooks let the app "sleep" until the server wakes it up.

### Industry Application: Automation & CI/CD

- **Payment Gateways (Stripe/PayPal):** Your app initiates a payment, but the confirmation happens asynchronously. Stripe uses a WebHook to notify your backend "Payment Succeeded" so you can ship the product.
- **GitHub/GitLab:** When a developer pushes code, GitHub triggers a WebHook to a CI/CD server (like Jenkins) to start building and testing the code automatically.

---

## 6. WebSockets

**"The Persistent Tunnel"**

WebSockets provide a full-duplex communication channel over a single TCP connection. Unlike HTTP (which closes after a response), WebSockets stay open.

### Technical Core

- **The Handshake:** The connection starts as a standard HTTP request with an `Upgrade: websocket` header. If accepted, the protocol switches from HTTP to WebSocket (ws:// or wss://).
- **Full-Duplex:** The server can send data to the client _without_ the client requesting it, and vice versa, at any time.
- **Stateful:** The connection is kept alive. The server knows exactly which client is connected.

### How it Works

WebSockets begin with an HTTP upgrade handshake:

```
GET /chat HTTP/1.1
Host: chat.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Once upgraded, the HTTP connection transforms into a persistent, low-overhead WebSocket. Now both client and server can send messages at any time:

**Client → Server:** User types "Hello!"

```
Client sends: {"message": "Hello!", "user": "john"}
```

**Server → All Clients:** Server broadcasts to everyone in the chat:

```
Server sends: {"user": "john", "message": "Hello!", "timestamp": 1234567890}
```

The protocol overhead is minimal—WebSocket frames have just a few bytes of header compared to HTTP (which includes method, path, all headers, etc. for every request).

**Connection Management:**

- **Ping/Pong:** To detect dead connections (client/server disconnects without closing), WebSocket uses periodic ping/pong frames.
- **Graceful Closure:** Either party can initiate closure with a close frame and status code.
- **Backpressure:** If the client can't keep up with incoming messages, it can signal the server to slow down.

### Language Support

- **JavaScript/Node.js:** `ws`, `socket.io`, `Engine.IO`
- **Python:** `websockets`, `python-socketio`
- **Java:** `Tyrus`, `Spring WebSocket`, `Jetty WebSocket`
- **Go:** `gorilla/websocket`, `nhooyr.io/websocket`
- **C#/.NET:** `WebSocketHandler` in `System.Net.WebSockets`
- **Ruby:** `websocket-eventmachine-server`, `actioncable`
- **PHP:** `Ratchet`, `workerman`

### Why it is used

For scenarios requiring **low-latency, bidirectional, real-time** updates where overhead must be minimized. HTTP headers are heavy; WebSocket frames are very lightweight.

### Industry Application: Real-Time Interaction

- **Chat Applications (Slack, WhatsApp Web):** When you receive a message, the server pushes it instantly to your browser through the open socket.
- **Financial Trading:** Stock tickers need to update prices thousands of times a second. Polling via REST is too slow; WebSockets stream the price changes instantly.
- **Multiplayer Gaming:** Sending player movement coordinates requires milliseconds of latency.

---

## 7. WebRTC (Web Real-Time Communication)

**"The Peer-to-Peer Powerhouse"**

WebRTC is an open source project that enables real-time media communication directly between browsers and devices.

### Technical Core

- **Peer-to-Peer (P2P):** Unlike the others, WebRTC tries to send data directly from Client A to Client B, bypassing the server (after the initial setup).
- **UDP Protocol:** It utilizes UDP (User Datagram Protocol) rather than TCP.
  - _TCP:_ Reliable. If a packet is lost, it stops and resends. Good for files, bad for video (causes buffering).
  - _UDP:_ Fast. If a packet (frame of video) is lost, it ignores it and moves to the next. Good for live streaming.
- **Signaling:** P2P requires a "Signaling Server" (often via WebSockets) just to introduce Client A to Client B (exchange IP addresses).
- **NAT Traversal (STUN/TURN):** Since most users are behind firewalls, WebRTC uses STUN/TURN servers to figure out how to route traffic through the firewall.

### How it Works

WebRTC involves several steps:

1. **Signaling (via WebSocket or HTTP):** Client A and Client B connect to a signaling server (often using WebSockets) and exchange metadata:
   - IP address and port
   - Audio/video codecs they support
   - ICE (Interactive Connectivity Establishment) candidates

```javascript
// Client A:
sendSignal({ type: "offer", sdp: sessionDescription });

// Server relays to Client B
// Client B responds:
sendSignal({ type: "answer", sdp: sessionDescription });

// Both exchange ICE candidates to find the best network path
```

2. **NAT Traversal (STUN/TURN):** Since most users are behind firewalls (NAT), WebRTC uses:
   - **STUN servers:** Tell you your public IP address.
   - **TURN servers:** Act as a relay if a direct P2P connection is impossible (rare).

3. **P2P Connection:** Once both parties have each other's network info, they establish a direct UDP connection and begin streaming media.

4. **Media Streaming (UDP):** Audio/video data flows directly using UDP (not TCP), which is fast but allows packet loss. This is acceptable for video—a lost frame is imperceptible; a lost TCP packet causing buffering would be terrible.

**Codecs Supported:**

- **Video:** VP8, VP9, H.264, AV1
- **Audio:** Opus, G.711, PCMU

5. **Data Channel (Optional):** WebRTC includes a data channel for non-media data, allowing file transfers, messages, or game state updates with the same low latency as media.

### Language Support

- **JavaScript/Web:** `RTCPeerConnection` (native browser API)
- **Python:** `aiortc`, `pyrtc`
- **Go:** `pion/webrtc`
- **Java:** `OpenWebRTC`, `AndroidRTC`
- **C++:** `libwebrtc` (Google's native implementation)
- **C#/.NET:** `WebRTC for .NET`, `Unified` RTC libraries
- **Swift (iOS):** `native RTCPeerConnection API`
- **Android:** `native WebRTC library`

Note: WebRTC in browsers is standardized, but server-side implementations vary by language.

### Why it is used

It is the standard for high-bandwidth, latency-intolerant media streaming. It reduces server costs (since video goes P2P) and provides the lowest possible latency for video/voice.

### Industry Application: Video Conferencing

- **Zoom (Web client), Google Meet, Discord:** These apps rely on WebRTC to transmit audio and video.
- **File Sharing:** Apps like **Sharedrop** allow you to transfer files between computers on the same WiFi without uploading them to a cloud server first, using the WebRTC data channel.
