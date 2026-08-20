# REALTIME CLIENT API Connections - SignalR-Style Cross-Ecosystem Engineering Notes

<br>
**Last updated**: March 11, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Topic](https://img.shields.io/badge/Realtime-Client_API_Connections-blue.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![Stacks](https://img.shields.io/badge/Stacks-SignalR%20%7C%20Socket.IO%20%7C%20ws%20%7C%20python--socketio%20%7C%20Django%20Channels%20%7C%20FastAPI-brightgreen.svg)](https://socket.io/docs/v4/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide compares hub-style realtime communication across C#, JavaScript/TypeScript, and Python with a deliberate SignalR lens. The point is not to repeat framework tutorials. The point is to make the abstraction boundaries explicit: what each stack treats as the equivalent of a hub, how connections are addressed, how groups or rooms are modeled, what scale-out actually requires, and where the term "connection pooling" is technically wrong.

The stacks covered are:

- **C#**: ASP.NET Core SignalR
- **JavaScript/TypeScript**: Socket.IO and raw WebSockets with `ws`
- **Python**: `python-socketio`, Django Channels, and FastAPI/Starlette WebSockets

## Contents

- [REALTIME CLIENT API Connections - SignalR-Style Cross-Ecosystem Engineering Notes](#realtime-client-api-connections---signalr-style-cross-ecosystem-engineering-notes)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Executive Summary](#executive-summary)
  - [1. Core Abstraction Model](#1-core-abstraction-model)
    - [ASP.NET Core SignalR](#aspnet-core-signalr)
    - [Socket.IO](#socketio)
    - [Raw WebSockets with ws](#raw-websockets-with-ws)
    - [python-socketio](#python-socketio)
    - [Django Channels](#django-channels)
    - [FastAPI and Starlette WebSockets](#fastapi-and-starlette-websockets)
  - [2. Basic Architecture](#2-basic-architecture)
    - [SignalR Server Shape](#signalr-server-shape)
    - [Socket.IO Server Shape](#socketio-server-shape)
    - [ws Server Shape](#ws-server-shape)
    - [python-socketio Server Shape](#python-socketio-server-shape)
    - [Django Channels Server Shape](#django-channels-server-shape)
    - [FastAPI and Starlette Server Shape](#fastapi-and-starlette-server-shape)
  - [3. Equivalent Terminology Table](#3-equivalent-terminology-table)
  - [4. Code Examples](#4-code-examples)
    - [C# - ASP.NET Core SignalR](#c---aspnet-core-signalr)
    - [TypeScript - Socket.IO](#typescript---socketio)
    - [TypeScript - Raw WebSockets with ws](#typescript---raw-websockets-with-ws)
    - [Python - python-socketio](#python---python-socketio)
    - [Python - Django Channels](#python---django-channels)
    - [Python - FastAPI WebSockets](#python---fastapi-websockets)
  - [5. Connection Management and the Misuse of "Pooling"](#5-connection-management-and-the-misuse-of-pooling)
    - [What HTTP Connection Pooling Actually Means](#what-http-connection-pooling-actually-means)
    - [What Realtime Systems Actually Manage](#what-realtime-systems-actually-manage)
    - [Correct Terms for Realtime System Design](#correct-terms-for-realtime-system-design)
      - [HTTP connection pooling](#http-connection-pooling)
      - [TCP connection reuse](#tcp-connection-reuse)
      - [Long-lived WebSocket connections](#long-lived-websocket-connections)
      - [Server-side connection registries](#server-side-connection-registries)
      - [Connection fanout and scaling](#connection-fanout-and-scaling)
      - [Connection limits](#connection-limits)
      - [Heartbeat / keepalive](#heartbeat--keepalive)
      - [Idle timeout](#idle-timeout)
      - [Reconnect strategies](#reconnect-strategies)
      - [Backpressure](#backpressure)
      - [Load balancing](#load-balancing)
      - [Sticky sessions](#sticky-sessions)
      - [Redis backplane or broker-based fanout](#redis-backplane-or-broker-based-fanout)
      - [Horizontal scaling across multiple server instances](#horizontal-scaling-across-multiple-server-instances)
  - [6. Production Concerns](#6-production-concerns)
    - [Authentication tokens for WebSocket upgrades](#authentication-tokens-for-websocket-upgrades)
    - [Authorization for rooms and groups](#authorization-for-rooms-and-groups)
    - [Presence tracking](#presence-tracking)
    - [Memory leaks from stale connections](#memory-leaks-from-stale-connections)
    - [Cleanup on disconnect](#cleanup-on-disconnect)
    - [Retries and exponential backoff](#retries-and-exponential-backoff)
    - [Message ordering guarantees](#message-ordering-guarantees)
    - [Delivery guarantees and acknowledgements](#delivery-guarantees-and-acknowledgements)
    - [Observability, logging, and metrics](#observability-logging-and-metrics)
    - [Rate limiting and abuse protection](#rate-limiting-and-abuse-protection)
  - [7. When to Choose Which Tool](#7-when-to-choose-which-tool)
  - [8. Recommended Mental Model](#8-recommended-mental-model)
  - [References and Further Reading](#references-and-further-reading)

---

## Executive Summary

SignalR, Socket.IO, `python-socketio`, and Django Channels all give you a higher-level messaging model on top of transport primitives. Raw WebSockets with `ws` and FastAPI/Starlette WebSockets give you much less abstraction: you own routing semantics, group membership, message contracts, retries, and most lifecycle policy yourself.

The practical split is simple:

- **SignalR / Socket.IO / python-socketio**: choose when you want named events, group membership semantics, reconnection support, and a framework-owned connection registry.
- **Django Channels**: choose when your realtime system must live inside Django's auth/session/routing model and you are comfortable with ASGI channel-layer concepts.
- **Raw WebSockets (`ws`) / FastAPI WebSockets**: choose when you need protocol-level control, low abstraction overhead, or a custom wire contract and you are prepared to build your own hub semantics.

Most engineering failures in realtime systems are not transport failures. They are failures of connection lifecycle management, authorization boundaries, stale membership cleanup, backpressure handling, and scale-out topology.

---

## 1. Core Abstraction Model

### ASP.NET Core SignalR

SignalR is explicitly hub-centric.

- **Hub**: A typed or untyped server-side endpoint class where client invocations land.
- **Client connection**: Addressed by `Context.ConnectionId`.
- **Event/message handler**: A hub method such as `SendMessage` or `JoinRoom`.
- **Room/group**: SignalR **Groups**. Membership is managed via `Groups.AddToGroupAsync` and `Groups.RemoveFromGroupAsync`.
- **Broadcast/fanout**: `Clients.All`, `Clients.Others`, `Clients.Group`, `Clients.Groups`.
- **Per-user messaging**: `Clients.User(userId)` where user identity is resolved by the framework's user id provider.
- **Server-to-client invocation**: `Clients.Caller.SendAsync("ReceiveMessage", ...)` or strongly typed client interfaces.
- **Client-to-server invocation**: client calls `connection.invoke("SendMessage", ...)` and the runtime dispatches to a hub method.

SignalR is closest to RPC-style realtime messaging. It supports event-driven flows, but its API surface encourages thinking in named server methods and named client callbacks.

### Socket.IO

Socket.IO is not just WebSockets. It is a higher-level eventing protocol with namespaces, rooms, acknowledgements, and transport fallback behavior.

- **Hub equivalent**: There is no hub class. The equivalent is the `io.on("connection", socket => ...)` server namespace plus event handlers attached to each `socket`.
- **Client connection**: `socket.id`.
- **Event/message handler**: `socket.on("eventName", handler)`.
- **Room/group**: Socket.IO **rooms** via `socket.join(room)`.
- **Broadcast/fanout**: `io.emit(...)`, `socket.broadcast.emit(...)`, `io.to(room).emit(...)`.
- **Per-user messaging**: Usually implemented by joining every authenticated client to a room named after the user id.
- **Server-to-client invocation**: `socket.emit(...)` or `io.to(room).emit(...)`.
- **Client-to-server invocation**: client emits a named event; server handles it with `socket.on(...)`.

Socket.IO is event-centric, not hub-centric. The wire protocol is Socket.IO-specific, so native WebSocket clients are not interchangeable without a compatible client library.

### Raw WebSockets with ws

`ws` is close to the protocol surface. There are no rooms, no built-in auth model, no typed invocation semantics, and no backplane.

- **Hub equivalent**: None. You define your own router or command dispatcher on top of message frames.
- **Client connection**: the `WebSocket` instance.
- **Event/message handler**: `socket.on("message", ...)` after your own JSON envelope parsing.
- **Room/group**: Not provided. You build a room registry manually.
- **Broadcast/fanout**: Iterate over tracked connections and send frames.
- **Per-user messaging**: Maintain your own `userId -> socket(s)` index.
- **Server-to-client invocation**: Convention only, typically `{ type, payload }` JSON messages.
- **Client-to-server invocation**: Convention only, typically command messages.

`ws` is the right comparison point when you want to understand what the higher-level frameworks are buying you.

### python-socketio

`python-socketio` is the closest Python analogue to Socket.IO rather than SignalR, but in practice it occupies the same architectural slot: a server-managed realtime event bus with room semantics.

- **Hub equivalent**: decorators or class-based namespaces containing event handlers.
- **Client connection**: session id `sid`.
- **Event/message handler**: `@sio.event`, `@sio.on("event")`, or namespace methods.
- **Room/group**: rooms via `enter_room` and `leave_room`.
- **Broadcast/fanout**: `sio.emit(..., room=...)` or `skip_sid=`.
- **Per-user messaging**: room-per-user or `sid` targeting.
- **Server-to-client invocation**: `emit()` with event names.
- **Client-to-server invocation**: client emits event names handled by decorators.

### Django Channels

Django Channels is ASGI-first and centers on **consumers** plus an optional distributed **channel layer**.

- **Hub equivalent**: a `WebsocketConsumer` or `AsyncWebsocketConsumer` class.
- **Client connection**: `self.channel_name` identifies the consumer instance; the WebSocket itself is exposed through the consumer lifecycle.
- **Event/message handler**: `receive`, `receive_json`, or channel-layer event methods like `chat_message`.
- **Room/group**: channel-layer **groups** via `group_add` and `group_discard`.
- **Broadcast/fanout**: `channel_layer.group_send(...)`.
- **Per-user messaging**: user-specific groups, usually `user_{id}`.
- **Server-to-client invocation**: send over the WebSocket from consumer methods.
- **Client-to-server invocation**: inbound frames hit `receive` or `receive_json`.

Channels is structurally closer to an actor/message-bus model than to SignalR RPC.

### FastAPI and Starlette WebSockets

FastAPI and Starlette expose WebSocket endpoints directly. The abstraction level is lower than SignalR, Socket.IO, or Channels.

- **Hub equivalent**: none built-in; a `@app.websocket` endpoint plus your own manager class.
- **Client connection**: `WebSocket` object instance.
- **Event/message handler**: your `while True: await websocket.receive_json()` loop plus a dispatcher.
- **Room/group**: not built-in; usually a manager storing `room -> set[WebSocket]`.
- **Broadcast/fanout**: custom iteration over registered sockets.
- **Per-user messaging**: custom `userId -> set[WebSocket]` mapping.
- **Server-to-client invocation**: `await websocket.send_json(...)`.
- **Client-to-server invocation**: `await websocket.receive_json()`.

FastAPI gives you transport access and DI integration, not a hub abstraction.

---

## 2. Basic Architecture

### SignalR Server Shape

SignalR server structure is usually:

1. Register authentication and authorization middleware.
2. Register SignalR services.
3. Map a hub endpoint such as `/hubs/chat`.
4. Define a `Hub` class with lifecycle hooks and callable methods.
5. Use `IHubContext<T>` when non-hub services need to push messages.

Practical notes:

- **Connection open/close**: override `OnConnectedAsync` and `OnDisconnectedAsync`.
- **Authentication**: bearer token or cookie auth runs before hub method authorization.
- **Authorization**: `[Authorize]` on hub or methods.
- **Joining/leaving groups**: explicit methods calling the `Groups` manager.
- **One/many/group sends**: `Clients.Client`, `Clients.Users`, `Clients.Group`, `Clients.All`.
- **Request/response style**: `InvokeAsync` maps well to request/reply semantics.
- **Event-driven style**: still fine, but event names are more implicit because methods are first-class.

### Socket.IO Server Shape

Socket.IO server structure is usually:

1. Create an HTTP server.
2. Attach a Socket.IO server instance.
3. Authenticate during the Socket.IO handshake.
4. Register per-socket event handlers inside the `connection` handler.
5. Use rooms for tenant, user, or document subscriptions.

Practical notes:

- **Connection open/close**: `connection` and `disconnect` events.
- **Authentication**: handshake auth payload, cookies, or middleware.
- **Authorization**: middleware plus per-event checks.
- **Joining/leaving rooms**: `socket.join(room)` and `socket.leave(room)`.
- **One/many/group sends**: `socket.emit`, `io.emit`, `io.to(room).emit`.
- **Request/response style**: use acknowledgements or correlation ids.
- **Event-driven style**: native fit.

### ws Server Shape

`ws` server structure is usually:

1. Attach a `WebSocketServer` to an HTTP server.
2. Authenticate during HTTP upgrade or immediately after connection.
3. Maintain a connection registry and optional room membership maps.
4. Parse inbound messages into an explicit envelope format.
5. Route commands to handlers.

Practical notes:

- **Connection open/close**: `connection`, `close`, `error`, `pong` handling.
- **Authentication**: verify JWT or session during upgrade request.
- **Authorization**: fully custom.
- **Groups/rooms**: fully custom.
- **Request/response style**: correlation ids in message envelopes.
- **Event-driven style**: type-tagged messages such as `{ type: "joined" }`.

### python-socketio Server Shape

`python-socketio` server structure is usually:

1. Create an async Socket.IO server.
2. Mount it on ASGI, AIOHTTP, or another supported runtime.
3. Authenticate in `connect` or middleware-like wrappers.
4. Register decorators or namespace classes.
5. Use rooms for tenancy and user addressing.

Practical notes mirror Socket.IO closely because the protocol model is the same.

### Django Channels Server Shape

Channels server structure is usually:

1. Define ASGI routing with `ProtocolTypeRouter` and `URLRouter`.
2. Wrap WebSocket routes in auth middleware.
3. Implement a consumer class.
4. Configure a channel layer, typically Redis, for groups and cross-process fanout.
5. Route domain events into `group_send` messages.

Practical notes:

- **Connection open/close**: `connect`, `disconnect`.
- **Authentication**: `scope["user"]` from auth middleware.
- **Authorization**: check in `connect` and before group membership changes.
- **Groups**: first-class via channel layer.
- **Request/response style**: possible but not its strongest model.
- **Event-driven style**: native fit.

### FastAPI and Starlette Server Shape

FastAPI server structure is usually:

1. Define a WebSocket endpoint.
2. Perform auth before `accept()` or immediately after.
3. Accept the socket.
4. Register it in a manager that tracks all connections, user connections, and room memberships.
5. Receive frames in a loop and dispatch by message type.

Practical notes:

- **Connection open/close**: endpoint entry and `WebSocketDisconnect` exception.
- **Authentication**: dependency injection, cookies, query parameters, headers.
- **Authorization**: custom.
- **Groups**: custom.
- **Request/response style**: natural if you add `requestId` and `replyTo` semantics.
- **Event-driven style**: also natural, but entirely convention-driven.

---

## 3. Equivalent Terminology Table

| Concept                          | ASP.NET Core SignalR                           | Socket.IO                       | ws                                    | python-socketio                         | Django Channels                                      | FastAPI / Starlette                    |
| :------------------------------- | :--------------------------------------------- | :------------------------------ | :------------------------------------ | :-------------------------------------- | :--------------------------------------------------- | :------------------------------------- |
| **SignalR Hub**                  | `Hub` class                                    | Namespace + per-socket handlers | Custom message router                 | Namespace / event handlers              | `Consumer` class                                     | WebSocket endpoint + manager           |
| **SignalR Groups**               | Groups                                         | Rooms                           | Custom room registry                  | Rooms                                   | Channel-layer groups                                 | Custom room registry                   |
| **Hub Context**                  | `IHubContext<T>`                               | Global `io` server object       | Shared registry / broadcaster service | `sio` server object                     | `channel_layer`                                      | Connection manager service             |
| **OnConnected / OnDisconnected** | `OnConnectedAsync` / `OnDisconnectedAsync`     | `connection` / `disconnect`     | `connection` / `close`                | `connect` / `disconnect`                | `connect` / `disconnect`                             | endpoint start / `WebSocketDisconnect` |
| **Clients.All**                  | `Clients.All`                                  | `io.emit()`                     | Iterate all sockets                   | `sio.emit()`                            | `group_send` to global group or iterate              | Iterate tracked sockets                |
| **Clients.Group**                | `Clients.Group(name)`                          | `io.to(room)`                   | Iterate room registry                 | `emit(..., room=...)`                   | `group_send(group, ...)`                             | Iterate room membership                |
| **Clients.User**                 | `Clients.User(userId)`                         | user-specific room              | user socket map                       | user room or `sid` map                  | user-specific group                                  | user socket map                        |
| **Transport fallback**           | WebSockets + SSE + Long Polling                | WebSockets + HTTP long polling  | None beyond raw WebSocket             | Same as Socket.IO protocol              | ASGI WebSocket only; fallback is separate app design | WebSocket only                         |
| **Backplane**                    | Redis / Azure SignalR Service                  | Redis adapter / broker adapters | Custom pub-sub                        | Redis / message queue managers          | Redis channel layer                                  | Custom pub-sub                         |
| **Scale-out strategy**           | Sticky sessions or managed service + backplane | Sticky sessions + Redis adapter | Shared broker + custom routing        | Sticky sessions + message queue / Redis | Redis channel layer + ASGI workers                   | Shared broker + custom routing         |

Key differences that matter:

- `ws` and FastAPI do not have a native equivalent to **Hub Context**. You must design a reusable broadcaster service yourself.
- Socket.IO rooms and SignalR groups are conceptually similar, but Socket.IO is more event-bus oriented while SignalR is more invocation oriented.
- Django Channels depends heavily on the channel layer for anything beyond a single process.

---

## 4. Code Examples

### C# - ASP.NET Core SignalR

Server:

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.SignalR;

var builder = WebApplication.CreateBuilder(args);

builder.Services
    .AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.Authority = "https://identity.example.com";
        options.TokenValidationParameters.ValidateAudience = false;

        options.Events = new Microsoft.AspNetCore.Authentication.JwtBearer.JwtBearerEvents
        {
            OnMessageReceived = context =>
            {
                var accessToken = context.Request.Query["access_token"];
                var path = context.HttpContext.Request.Path;

                if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hubs/chat"))
                {
                    context.Token = accessToken;
                }

                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization();
builder.Services.AddSignalR();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.MapHub<ChatHub>("/hubs/chat");
app.Run();

[Authorize]
public class ChatHub : Hub
{
    public override async Task OnConnectedAsync()
    {
        var userId = Context.UserIdentifier;
        if (!string.IsNullOrWhiteSpace(userId))
        {
            await Groups.AddToGroupAsync(Context.ConnectionId, $"user:{userId}");
        }

        await base.OnConnectedAsync();
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        var room = Context.Items.TryGetValue("room", out var value) ? value as string : null;
        if (!string.IsNullOrWhiteSpace(room))
        {
            await Groups.RemoveFromGroupAsync(Context.ConnectionId, room);
        }

        await base.OnDisconnectedAsync(exception);
    }

    public async Task JoinRoom(string room)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, room);
        Context.Items["room"] = room;
        await Clients.Group(room).SendAsync("SystemMessage", $"{Context.UserIdentifier} joined {room}");
    }

    public async Task SendRoomMessage(string room, string text)
    {
        await Clients.Group(room).SendAsync("ReceiveRoomMessage", Context.UserIdentifier, text);
    }

    public async Task SendPrivateMessage(string userId, string text)
    {
        await Clients.User(userId).SendAsync("ReceivePrivateMessage", Context.UserIdentifier, text);
    }
}
```

Client:

```typescript
import * as signalR from "@microsoft/signalr";

const connection = new signalR.HubConnectionBuilder()
  .withUrl("/hubs/chat", {
    accessTokenFactory: async () => localStorage.getItem("access_token") ?? "",
  })
  .withAutomaticReconnect([0, 2000, 5000, 10000])
  .build();

connection.on("ReceiveRoomMessage", (fromUserId: string, text: string) => {
  console.log("room", { fromUserId, text });
});

connection.on("ReceivePrivateMessage", (fromUserId: string, text: string) => {
  console.log("private", { fromUserId, text });
});

connection.onreconnecting((error) => console.warn("reconnecting", error));
connection.onreconnected((connectionId) =>
  console.info("reconnected", connectionId),
);
connection.onclose((error) => console.error("closed", error));

await connection.start();
await connection.invoke("JoinRoom", "project:alpha");
await connection.invoke("SendRoomMessage", "project:alpha", "hello team");
await connection.invoke("SendPrivateMessage", "user-42", "check your queue");
```

### TypeScript - Socket.IO

Server:

```typescript
import http from "node:http";
import { Server } from "socket.io";
import jwt from "jsonwebtoken";

const server = http.createServer();
const io = new Server(server, {
  cors: { origin: "https://app.example.com", credentials: true },
});

io.use((socket, next) => {
  try {
    const token = socket.handshake.auth.token;
    const payload = jwt.verify(token, process.env.JWT_SECRET! as string) as {
      sub: string;
    };
    socket.data.userId = payload.sub;
    return next();
  } catch {
    return next(new Error("unauthorized"));
  }
});

io.on("connection", (socket) => {
  const userRoom = `user:${socket.data.userId}`;
  socket.join(userRoom);

  socket.on(
    "join-room",
    async (room: string, ack?: (response: { ok: boolean }) => void) => {
      socket.join(room);
      io.to(room).emit("system-message", {
        text: `${socket.data.userId} joined ${room}`,
      });
      ack?.({ ok: true });
    },
  );

  socket.on("room-message", ({ room, text }) => {
    io.to(room).emit("room-message", { from: socket.data.userId, text });
  });

  socket.on("private-message", ({ toUserId, text }) => {
    io.to(`user:${toUserId}`).emit("private-message", {
      from: socket.data.userId,
      text,
    });
  });

  socket.on("disconnect", (reason) => {
    console.log("disconnect", socket.id, reason);
  });
});

server.listen(3000);
```

Client:

```typescript
import { io } from "socket.io-client";

const socket = io("https://api.example.com", {
  auth: {
    token: localStorage.getItem("access_token"),
  },
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 10000,
});

socket.on("connect", () => {
  socket.emit("join-room", "project:alpha", (response: { ok: boolean }) => {
    console.log("joined", response.ok);
  });
});

socket.on("room-message", (message) => console.log(message));
socket.on("private-message", (message) => console.log(message));
socket.on("disconnect", (reason) => console.warn("disconnect", reason));
socket.on("connect_error", (error) =>
  console.error("connect_error", error.message),
);

socket.emit("room-message", {
  room: "project:alpha",
  text: "hello from client",
});
socket.emit("private-message", { toUserId: "user-42", text: "private ping" });
```

### TypeScript - Raw WebSockets with ws

Server:

```typescript
import http from "node:http";
import { WebSocketServer, WebSocket } from "ws";
import jwt from "jsonwebtoken";

type MessageEnvelope = {
  type: string;
  room?: string;
  toUserId?: string;
  text?: string;
  requestId?: string;
};

const server = http.createServer();
const wss = new WebSocketServer({ noServer: true });

const allSockets = new Set<WebSocket>();
const rooms = new Map<string, Set<WebSocket>>();
const socketsByUser = new Map<string, Set<WebSocket>>();
const userBySocket = new WeakMap<WebSocket, string>();

function addToRoom(room: string, socket: WebSocket) {
  const members = rooms.get(room) ?? new Set<WebSocket>();
  members.add(socket);
  rooms.set(room, members);
}

function removeSocket(socket: WebSocket) {
  allSockets.delete(socket);

  for (const members of rooms.values()) {
    members.delete(socket);
  }

  const userId = userBySocket.get(socket);
  if (userId) {
    const members = socketsByUser.get(userId);
    members?.delete(socket);
    if (members && members.size === 0) {
      socketsByUser.delete(userId);
    }
  }
}

function sendJson(socket: WebSocket, payload: unknown) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(payload));
  }
}

server.on("upgrade", (request, socket, head) => {
  try {
    const url = new URL(request.url ?? "/", "http://localhost");
    const token = url.searchParams.get("token") ?? undefined;
    const payload = jwt.verify(
      token ?? "",
      process.env.JWT_SECRET! as string,
    ) as { sub: string };

    wss.handleUpgrade(request, socket, head, (ws) => {
      userBySocket.set(ws, payload.sub);
      const userSockets =
        socketsByUser.get(payload.sub) ?? new Set<WebSocket>();
      userSockets.add(ws);
      socketsByUser.set(payload.sub, userSockets);
      wss.emit("connection", ws, request);
    });
  } catch {
    socket.write("HTTP/1.1 401 Unauthorized\r\n\r\n");
    socket.destroy();
  }
});

wss.on("connection", (ws) => {
  allSockets.add(ws);

  ws.on("message", (raw) => {
    const message = JSON.parse(raw.toString()) as MessageEnvelope;
    const fromUserId = userBySocket.get(ws);

    if (message.type === "join-room" && message.room) {
      addToRoom(message.room, ws);
      sendJson(ws, {
        type: "join-room-ack",
        room: message.room,
        requestId: message.requestId,
      });
      return;
    }

    if (message.type === "room-message" && message.room) {
      for (const member of rooms.get(message.room) ?? []) {
        sendJson(member, {
          type: "room-message",
          room: message.room,
          fromUserId,
          text: message.text,
        });
      }
      return;
    }

    if (message.type === "private-message" && message.toUserId) {
      for (const member of socketsByUser.get(message.toUserId) ?? []) {
        sendJson(member, {
          type: "private-message",
          fromUserId,
          text: message.text,
        });
      }
    }
  });

  ws.on("close", () => removeSocket(ws));
  ws.on("error", () => removeSocket(ws));
  ws.on("pong", () => {
    // production systems usually update a last-seen timestamp here
  });
});

server.listen(3001);
```

Client:

```typescript
const token = localStorage.getItem("access_token");
let attempt = 0;
let socket: WebSocket;

function connect() {
  socket = new WebSocket(
    `wss://api.example.com/realtime?token=${encodeURIComponent(token ?? "")}`,
  );

  socket.addEventListener("open", () => {
    attempt = 0;
    socket.send(
      JSON.stringify({
        type: "join-room",
        room: "project:alpha",
        requestId: crypto.randomUUID(),
      }),
    );
  });

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    console.log(message);
  });

  socket.addEventListener("close", () => {
    const delay = Math.min(1000 * 2 ** attempt, 10000);
    attempt += 1;
    setTimeout(connect, delay);
  });
}

connect();
```

Note: browser-native `WebSocket` does not let you set arbitrary headers. In browsers you usually pass the token via query string, cookie, or a pre-upgrade session mechanism. For stricter security posture, prefer an HttpOnly session cookie or a short-lived WebSocket ticket rather than a long-lived bearer token in the URL.

### Python - python-socketio

Server:

```python
import socketio
import jwt

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["https://app.example.com"])
app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid, environ, auth):
    try:
        token = auth["token"]
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        await sio.save_session(sid, {"user_id": payload["sub"]})
        await sio.enter_room(sid, f"user:{payload['sub']}")
    except Exception as exc:
        raise ConnectionRefusedError("unauthorized") from exc


@sio.event
async def join_room(sid, data):
    room = data["room"]
    await sio.enter_room(sid, room)
    session = await sio.get_session(sid)
    await sio.emit("system_message", {"text": f"{session['user_id']} joined {room}"}, room=room)
    return {"ok": True}


@sio.event
async def room_message(sid, data):
    session = await sio.get_session(sid)
    await sio.emit(
        "room_message",
        {"from": session["user_id"], "text": data["text"]},
        room=data["room"],
    )


@sio.event
async def private_message(sid, data):
    session = await sio.get_session(sid)
    await sio.emit(
        "private_message",
        {"from": session["user_id"], "text": data["text"]},
        room=f"user:{data['to_user_id']}",
    )


@sio.event
async def disconnect(sid):
    print("disconnect", sid)
```

Client:

```python
import asyncio
import socketio

sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=0)


@sio.event
async def connect():
    await sio.emit("join_room", {"room": "project:alpha"})
    await sio.emit("room_message", {"room": "project:alpha", "text": "hello from python client"})
    await sio.emit("private_message", {"to_user_id": "user-42", "text": "private ping"})


@sio.event
async def room_message(data):
    print(data)


@sio.event
async def disconnect():
    print("disconnected")


async def main():
    await sio.connect(
        "https://api.example.com",
        auth={"token": "jwt-token"},
        transports=["websocket"],
    )
    await sio.wait()


asyncio.run(main())
```

### Python - Django Channels

Consumer:

```python
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group = f"user:{user.id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, "room_group"):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message_type = content["type"]

        if message_type == "join-room":
            self.room_group = f"room:{content['room']}"
            await self.channel_layer.group_add(self.room_group, self.channel_name)
            await self.channel_layer.group_send(
                self.room_group,
                {
                    "type": "room.message",
                    "from_user_id": self.scope["user"].id,
                    "text": "joined room",
                },
            )
            return

        if message_type == "room-message":
            await self.channel_layer.group_send(
                f"room:{content['room']}",
                {
                    "type": "room.message",
                    "from_user_id": self.scope["user"].id,
                    "text": content["text"],
                },
            )
            return

        if message_type == "private-message":
            await self.channel_layer.group_send(
                f"user:{content['to_user_id']}",
                {
                    "type": "private.message",
                    "from_user_id": self.scope["user"].id,
                    "text": content["text"],
                },
            )

    async def room_message(self, event):
        await self.send_json({
            "type": "room-message",
            "from_user_id": event["from_user_id"],
            "text": event["text"],
        })

    async def private_message(self, event):
        await self.send_json({
            "type": "private-message",
            "from_user_id": event["from_user_id"],
            "text": event["text"],
        })
```

ASGI routing:

```python
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from .consumers import ChatConsumer

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter([
                path("ws/chat/", ChatConsumer.as_asgi()),
            ])
        )
    }
)
```

Browser client:

```typescript
let attempt = 0;
let socket: WebSocket;

function connect() {
  socket = new WebSocket("wss://app.example.com/ws/chat/?token=jwt-token");

  socket.addEventListener("open", () => {
    attempt = 0;
    socket.send(JSON.stringify({ type: "join-room", room: "project:alpha" }));
  });

  socket.addEventListener("message", (event) => {
    console.log(JSON.parse(event.data));
  });

  socket.addEventListener("close", () => {
    const delay = Math.min(1000 * 2 ** attempt, 15000);
    attempt += 1;
    setTimeout(connect, delay);
  });
}

connect();
```

### Python - FastAPI WebSockets

Server:

```python
from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
import jwt

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.all_connections: set[WebSocket] = set()
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self.by_user: dict[str, set[WebSocket]] = defaultdict(set)
        self.user_by_socket: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self.all_connections.add(websocket)
        self.by_user[user_id].add(websocket)
        self.user_by_socket[websocket] = user_id

    def disconnect(self, websocket: WebSocket) -> None:
        self.all_connections.discard(websocket)
        user_id = self.user_by_socket.pop(websocket, None)
        if user_id is not None:
            self.by_user[user_id].discard(websocket)
            if not self.by_user[user_id]:
                self.by_user.pop(user_id, None)

        for members in self.rooms.values():
            members.discard(websocket)

    def join_room(self, websocket: WebSocket, room: str) -> None:
        self.rooms[room].add(websocket)

    async def send_room(self, room: str, payload: dict) -> None:
        for connection in list(self.rooms[room]):
            await connection.send_json(payload)

    async def send_user(self, user_id: str, payload: dict) -> None:
        for connection in list(self.by_user[user_id]):
            await connection.send_json(payload)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def chat_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        user_id = payload["sub"]
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            message = await websocket.receive_json()
            if message["type"] == "join-room":
                manager.join_room(websocket, message["room"])
                await manager.send_room(message["room"], {
                    "type": "system-message",
                    "text": f"{user_id} joined {message['room']}",
                })
            elif message["type"] == "room-message":
                await manager.send_room(message["room"], {
                    "type": "room-message",
                    "from_user_id": user_id,
                    "text": message["text"],
                })
            elif message["type"] == "private-message":
                await manager.send_user(message["to_user_id"], {
                    "type": "private-message",
                    "from_user_id": user_id,
                    "text": message["text"],
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

Client:

```typescript
let attempt = 0;
let socket: WebSocket;

function connect() {
  socket = new WebSocket("wss://api.example.com/ws/chat?token=jwt-token");

  socket.onopen = () => {
    attempt = 0;
    socket.send(JSON.stringify({ type: "join-room", room: "project:alpha" }));
    socket.send(
      JSON.stringify({
        type: "room-message",
        room: "project:alpha",
        text: "hello room",
      }),
    );
    socket.send(
      JSON.stringify({
        type: "private-message",
        to_user_id: "user-42",
        text: "private ping",
      }),
    );
  };

  socket.onmessage = (event) => console.log(JSON.parse(event.data));
  socket.onclose = () => {
    const delay = Math.min(1000 * 2 ** attempt, 10000);
    attempt += 1;
    setTimeout(connect, delay);
  };
}

connect();
```

---

## 5. Connection Management and the Misuse of "Pooling"

This section matters because teams often import HTTP vocabulary into a system that behaves very differently.

### What HTTP Connection Pooling Actually Means

HTTP connection pooling usually means reusing a finite set of outbound TCP connections for many short-lived requests. Typical examples:

- `HttpClient` in .NET reuses sockets under the hood.
- browser connection pools reuse keep-alive connections.
- database or broker clients reuse transport connections to avoid repeated setup cost.

Pooling is about **reusing scarce transport setup cost across many independent request lifecycles**.

### What Realtime Systems Actually Manage

Realtime hub systems usually do **not** pool client WebSocket connections. Each connected client normally owns a long-lived TCP connection upgraded from HTTP to WebSocket. The system problem is not "how do I reuse a pool of sockets for many clients?" The system problem is:

- how do I track thousands of persistent client connections,
- how do I route messages to the correct subset,
- how do I detect dead or stalled peers,
- how do I survive reconnect storms,
- how do I fan messages out across multiple server instances.

The correct concepts are:

- **persistent connection management**
- **connection registry**
- **group membership registry**
- **heartbeat / keepalive**
- **idle timeout management**
- **reconnect policy**
- **backpressure control**
- **distributed fanout**
- **load balancing and affinity**

### Correct Terms for Realtime System Design

#### HTTP connection pooling

- Relevant for outbound REST calls, database drivers, and broker clients.
- Not the right term for client WebSocket hubs.

#### TCP connection reuse

- Applies before upgrade and in non-WebSocket protocols.
- Once upgraded, the connection is usually dedicated to that client until disconnect.

#### Long-lived WebSocket connections

- This is the dominant model in realtime hubs.
- Capacity planning is based on concurrent open sockets, message rate, memory per connection, and slow-consumer behavior.

#### Server-side connection registries

- SignalR, Socket.IO, `python-socketio`, and Channels provide framework-level registries.
- `ws` and FastAPI require your own registry data structures.

#### Connection fanout and scaling

- A single instance can only fan out to its local sockets.
- Once you scale horizontally, you need a distributed fanout path: Redis backplane, managed realtime service, or broker-based pub-sub.

#### Connection limits

- Real limits come from file descriptors, memory per connection, CPU for encoding/dispatch, TLS overhead, and network buffers.
- Measure concurrent open sockets, not only request throughput.

#### Heartbeat / keepalive

- Required to detect silent disconnects and dead mobile clients.
- SignalR and Socket.IO expose keepalive behaviors; raw stacks require explicit ping/pong policy.

#### Idle timeout

- Enforce idle disconnects carefully. Some users are passive listeners and still valid.
- Proxies, load balancers, and managed ingress also impose idle timeouts that must align with keepalive settings.

#### Reconnect strategies

- Use exponential backoff with jitter.
- Rejoin groups after reconnect because membership may be connection-scoped.
- Distinguish transient network failure from auth expiry.

#### Backpressure

- Slow consumers can exhaust server memory if outbound queues grow without bound.
- Framework defaults vary; in lower-level stacks you must define per-connection queue limits, drop policy, or disconnect policy.

#### Load balancing

- Stateless HTTP balancing assumptions break down for connection-oriented systems.
- You need to understand whether the framework or backplane tolerates non-sticky routing.

#### Sticky sessions

- Often required when connection state lives in server memory and reconnects or polling fallbacks must hit the same instance.
- Managed services or fully externalized state reduce the need for affinity.

#### Redis backplane or broker-based fanout

- Used when a message produced on instance A must reach sockets connected to instances B, C, and D.
- Redis is common for fanout and group membership synchronization, but not always ideal for durable messaging semantics.

#### Horizontal scaling across multiple server instances

- Do not confuse scale-out with just adding pods.
- A valid design answers: where does group membership live, how is user presence shared, how are messages replicated, what happens during rolling deploys, and what happens when a node dies mid-broadcast?

Operationally precise statement: for realtime hubs, the right phrase is usually **persistent connection management**, not **connection pooling**.

---

## 6. Production Concerns

### Authentication tokens for WebSocket upgrades

- Browsers do not always let you attach arbitrary headers to native WebSocket connections, so tokens often travel via cookies, query parameters, or framework-specific handshake fields.
- Query-string tokens are common but sensitive; avoid logging them and prefer short TTLs or cookie/session-backed auth when possible.
- Refresh-token logic must account for already-open sockets whose original access token has expired.

### Authorization for rooms and groups

- Never let room membership be purely client-declared without server-side checks.
- Treat room join as an authorization decision based on tenant, document, project, or role membership.
- Recheck authorization after reconnect if membership is re-established automatically.

### Presence tracking

- Presence is not the same as a socket being open.
- A user may have multiple devices and multiple tabs.
- Model presence explicitly: user online, last seen, active room set, and device count.

### Memory leaks from stale connections

- The most common leak is not the socket itself but stale entries in user maps, room maps, timer lists, or outbound queues.
- Every disconnect path must clean membership registries and any per-connection timers or buffers.

### Cleanup on disconnect

- Handle normal close, error close, timeout, and process crash semantics.
- Assume cleanup callbacks are best effort, not guaranteed. Periodic sweeping of stale registries is still useful in custom implementations.

### Retries and exponential backoff

- Immediate reconnect storms after a node restart can self-inflict outage.
- Use capped exponential backoff with jitter.
- Retries must respect auth failures; do not infinitely retry a guaranteed 401.

### Message ordering guarantees

- WebSocket gives in-order delivery on a single TCP connection.
- Ordering across reconnects, across servers, or across broker-mediated fanout is an application-level concern.
- If global ordering matters, define partitioning keys or sequence numbers.

### Delivery guarantees and acknowledgements

- Most realtime hubs are fundamentally best-effort unless you build acknowledgements and replay.
- Socket.IO has event acknowledgements; SignalR supports invocation completion semantics; raw stacks require correlation ids and explicit ack messages.
- If a message must never be lost, you usually need a durable broker and replay model, not only WebSockets.

### Observability, logging, and metrics

- Track concurrent connections, successful upgrades, failed auth, reconnect rate, room membership cardinality, outbound queue depth, message throughput, and disconnect reasons.
- Structured logs should include connection id, user id if allowed, tenant id, room id, and correlation id.
- Trace the HTTP upgrade, auth decision, group join, and downstream domain event that triggered fanout.

### Rate limiting and abuse protection

- Limit connection creation rate, per-user concurrent sockets, per-event frequency, and payload size.
- Validate message schemas before routing.
- Reject pathological room joins, oversized frames, and fanout amplification abuse.

---

## 7. When to Choose Which Tool

**Choose SignalR when:**

- your backend is already ASP.NET Core,
- you want hub semantics and mature auth integration,
- you need strong integration with claims-based identity and .NET dependency injection,
- you value a clean server-to-client invocation model more than protocol minimalism.

**Choose Socket.IO when:**

- you want event-based realtime messaging in Node.js or TypeScript,
- you need rooms, acknowledgements, automatic reconnection, and fallback behavior,
- you control both client and server and are comfortable with the Socket.IO protocol rather than raw WebSocket interoperability.

**Choose raw WebSockets with ws when:**

- you need protocol-level control,
- you want no framework-level event abstraction,
- you are building a custom wire contract,
- you accept that rooms, auth policy, retry semantics, and scale-out plumbing are your responsibility.

**Choose python-socketio when:**

- Python is your backend language and you want Socket.IO-style event semantics,
- your team wants rooms and a framework-managed connection model without inventing protocol conventions,
- you are comfortable running an async Python stack.

**Choose Django Channels when:**

- your realtime features belong inside an existing Django application,
- Django auth, sessions, ORM, and routing are already system anchors,
- you need Redis-backed channel-layer groups and are comfortable with ASGI consumer patterns.

**Choose FastAPI WebSockets when:**

- you want lightweight WebSocket endpoints inside an async Python API,
- you need moderate abstraction and full control over the wire model,
- your application does not need Socket.IO protocol compatibility and you are willing to build your own connection manager.

Short rule: if you need a **hub-like programming model**, prefer SignalR, Socket.IO, `python-socketio`, or Channels. If you need a **transport primitive**, prefer `ws` or FastAPI WebSockets.

---

## 8. Recommended Mental Model

Use this unified model across languages and frameworks:

1. **Connection**
   A connection is a long-lived transport session, usually one TCP connection per client session. It has a connection id and lifecycle events.

2. **Authenticated identity**
   The connection is associated with a principal, user id, tenant id, device id, or anonymous session. Authentication happens at or before connection establishment.

3. **Subscription or group membership**
   Connections subscribe to routing scopes such as rooms, groups, topics, documents, or user channels. Membership is server-authoritative, not client-authoritative.

4. **Message routing**
   Every inbound message must resolve to a routing rule: to one connection, one user, one room, one tenant, or all subscribers. In raw stacks, this is your dispatcher. In hub stacks, the framework gives you part of that dispatcher.

5. **Distributed fanout**
   A local process can only address its local sockets directly. Multi-instance systems require a backplane, broker, or managed service to replicate routing intent across instances.

6. **Scaling strategy**
   Scaling is a combination of connection capacity planning, backplane topology, reconnect policy, and observability. It is not solved merely by adding pods.

If you keep this mental model stable, switching between SignalR, Socket.IO, Channels, FastAPI, or raw WebSockets becomes an implementation detail rather than a conceptual rewrite.

---

## References and Further Reading

- [ASP.NET Core SignalR](https://learn.microsoft.com/aspnet/core/signalr/)
- [Socket.IO](https://socket.io/docs/v4/)
- [ws](https://github.com/websockets/ws)
- [python-socketio](https://python-socketio.readthedocs.io/)
- [Django Channels](https://channels.readthedocs.io/)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Starlette WebSockets](https://www.starlette.io/websockets/)
- [WebSocket RFC 6455](https://www.rfc-editor.org/rfc/rfc6455)
