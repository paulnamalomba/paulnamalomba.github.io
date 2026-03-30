# Clean Architecture & Project Structures — C#, Dart (Flutter) & TypeScript

<br>
**Last updated**: March 04, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Architecture](https://img.shields.io/badge/Architecture-Clean%20Architecture-blue.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
[![Languages](https://img.shields.io/badge/Languages-C%23%20%7C%20Dart%20%7C%20TypeScript-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

Architecting software is a battle between the convenience of framework defaults and the necessary rigor of enterprise maintainability. The "typical" structures are optimized for getting a "Hello World" running in five minutes. Clean Architecture is optimized for surviving five years of shifting business requirements without rewriting the entire codebase.

This guide provides a detailed breakdown of typical, framework-default project structures versus their production-grade Clean Architecture counterparts for **C# (.NET)**, **Dart (Flutter)**, and **TypeScript (Node.js)**. It includes a glossary of fundamental architectural terms, concrete folder structures, comparison tables, a full data-flow walkthrough, and practical guidance on when (and when not) to apply Clean Architecture.

## Contents

- [Clean Architecture \& Project Structures — C#, Dart (Flutter) \& TypeScript](#clean-architecture--project-structures--c-dart-flutter--typescript)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Architectural Glossary](#architectural-glossary)
    - [Layer Terms](#layer-terms)
    - [Component Terms](#component-terms)
    - [Principle Terms](#principle-terms)
  - [The Core Idea: The Dependency Rule](#the-core-idea-the-dependency-rule)
  - [1. C# (.NET Web API)](#1-c-net-web-api)
    - [Typical Structure (Single Project Monolith)](#typical-structure-single-project-monolith)
    - [Clean Architecture Structure (Multi-Project Solution)](#clean-architecture-structure-multi-project-solution)
    - [C# Project References (Enforcing the Dependency Rule)](#c-project-references-enforcing-the-dependency-rule)
  - [2. Dart (Flutter for iOS/Android)](#2-dart-flutter-for-iosandroid)
    - [Typical Structure (Folder-by-Type)](#typical-structure-folder-by-type)
    - [Clean Architecture Structure (Feature-First)](#clean-architecture-structure-feature-first)
    - [Dart Dependency Injection Mechanics](#dart-dependency-injection-mechanics)
  - [3. TypeScript (Node.js Backend)](#3-typescript-nodejs-backend)
    - [Typical Structure (Express.js Default)](#typical-structure-expressjs-default)
    - [Clean Architecture Structure](#clean-architecture-structure)
    - [TypeScript DI \& Interface Enforcement](#typescript-di--interface-enforcement)
  - [Comparison Matrix: Typical vs Clean](#comparison-matrix-typical-vs-clean)
  - [Data Flow Walkthrough: User Registration](#data-flow-walkthrough-user-registration)
    - [Step-by-Step: From HTTP to Database and Back](#step-by-step-from-http-to-database-and-back)
    - [Concrete Code Example (TypeScript)](#concrete-code-example-typescript)
  - [When to Use Clean Architecture (and When Not To)](#when-to-use-clean-architecture-and-when-not-to)
  - [Common Pitfalls](#common-pitfalls)
  - [References \& Further Reading](#references--further-reading)

---

## Architectural Glossary

Before dissecting folder structures, it is critical to establish precise definitions. These terms appear throughout Clean Architecture literature and are often misused or conflated.

### Layer Terms

| Term | Definition |
| :--- | :--- |
| **Domain** | The innermost layer. Contains the core business rules and enterprise logic that exist regardless of any framework, UI, or database. This layer defines *what* the system does in pure business terms. It has **zero** external dependencies — no NuGet packages, no npm modules, no Flutter plugins. If your company's business rules would survive the complete replacement of your tech stack, they belong here. |
| **Application** | Orchestrates the domain. Contains **Use Cases** (also called Interactors or Application Services) that coordinate domain entities and interfaces to fulfill a specific user intent (e.g., "Register a new user," "Process a payment"). This layer defines *how* domain rules are triggered. It references the Domain layer and nothing else. |
| **Infrastructure** | The implementation layer. This is where all concrete, framework-dependent code lives: database access (Entity Framework, Mongoose, Drift), external API clients (Stripe, Twilio, SendGrid), file system access, caching (Redis), message brokers (RabbitMQ, Kafka). It *implements* the interfaces (contracts) defined in the Domain layer. It references both Domain and Application. |
| **Presentation** | The delivery mechanism. The outermost layer that adapts user input into something the Application layer understands and formats Application output for the user. For a backend API, this is your HTTP controllers, middleware, and route definitions. For Flutter, this is your Widgets, Pages, and state management (Bloc, Riverpod). This layer calls Application Use Cases but never touches Infrastructure directly. |
| **Core** | A cross-cutting shared module containing utilities, constants, error/failure classes, and networking primitives (HTTP clients, interceptors) used across all features. In Flutter Clean Architecture, `core/` often holds the `Failure` base class, theme data, and the configured `Dio` client. In backend apps, this might hold shared value objects or extension methods. Not a formal Clean Architecture layer, but a practical necessity. |

### Component Terms

| Term | Definition |
| :--- | :--- |
| **Entity** | A domain object that is defined by its **identity** (an ID), not by its attributes. A `User` entity with `id: 42` is the same user even if their name changes. Entities encapsulate the most critical business rules. In the Domain layer, entities are plain classes with no framework annotations — no `[Table]`, no `@Entity()`, no `@JsonSerializable()`. |
| **Model** | A data-transfer representation of an entity, augmented with serialization logic. A `UserModel` in the Infrastructure/Data layer might extend or map to a `User` entity but includes `fromJson()`, `toMap()`, or Entity Framework `[Column]` annotations. Models know about the outside world; entities do not. |
| **DTO (Data Transfer Object)** | A plain object used to shuttle data across layer boundaries. A `RegisterUserRequest` DTO carries input from the Presentation layer to the Application layer. A `UserResponse` DTO carries output back. DTOs decouple HTTP request/response shapes from internal domain structures. If your API contract changes, only the DTO changes — not the entity. |
| **Repository** | An abstraction (interface) that defines data access operations without specifying *how* data is stored. `IUserRepository` declares `GetByIdAsync(int id)` — it does not say whether the backing store is PostgreSQL, MongoDB, or an in-memory list. The interface lives in the Domain layer; the concrete implementation (e.g., `UserRepositoryImpl`) lives in Infrastructure. |
| **Use Case (Interactor)** | A single, named unit of application logic. One Use Case = one user intention. `RegisterUserUseCase` validates input, checks for duplicates, hashes the password, persists the user, and dispatches a welcome email. Use Cases orchestrate but do not implement — they call repository interfaces and service interfaces defined in the Domain layer. |
| **Service (Domain Service)** | Business logic that does not naturally belong to any single entity. For example, a `PricingService` that calculates a ride fare based on distance, surge multiplier, and vehicle type operates across multiple entities. Domain Services live in the Domain layer and have no external dependencies. |
| **Service (Infrastructure Service)** | A concrete implementation of an external capability: `EmailService` wrapping SendGrid, `PaymentService` wrapping Stripe, `CacheService` wrapping Redis. These implement interfaces defined in the Domain layer and live in Infrastructure. The distinction from a Domain Service is that Infrastructure Services depend on third-party SDKs. |
| **Middleware** | A pipeline component that intercepts requests before they reach a controller or responses before they leave the server. Common middleware includes authentication (JWT validation), logging, CORS enforcement, rate limiting, and global error handling. Middleware lives in the Presentation layer. |
| **Validator** | A component that enforces input correctness rules before a Use Case executes. Validators live in the Application layer and use libraries like FluentValidation (C#), `class-validator` (TypeScript), or `dartz`/`fpdart` (Dart) to reject malformed requests early. |

### Principle Terms

| Term | Definition |
| :--- | :--- |
| **Dependency Rule** | The cardinal rule of Clean Architecture: **source code dependencies must point inward only.** The Domain layer knows nothing about Application, Infrastructure, or Presentation. Application knows about Domain but not Infrastructure or Presentation. This is enforced by project/package references, not by developer discipline alone. |
| **Dependency Injection (DI)** | A technique where a class receives its dependencies (typically via constructor parameters) rather than creating them internally. This enables the Dependency Rule: a Use Case depends on `IUserRepository` (an abstraction from Domain). At startup, the DI container wires `IUserRepository` to `UserRepositoryImpl` (a concrete from Infrastructure). The Use Case never imports or references Infrastructure code. |
| **Inversion of Control (IoC)** | The broader principle that DI implements. Traditional code calls libraries; with IoC, the framework calls your code. In Clean Architecture, the inner layers define interfaces (control the contract), and the outer layers provide implementations (invert the typical dependency direction). |
| **Separation of Concerns (SoC)** | Each layer or module has a single, well-defined responsibility. Controllers do not validate. Validators do not query databases. Repositories do not format HTTP responses. SoC is the philosophical foundation; Clean Architecture is the structural enforcement. |
| **CQRS (Command Query Responsibility Segregation)** | A pattern often paired with Clean Architecture in C# where write operations (Commands) and read operations (Queries) are handled by separate pipelines. MediatR is the canonical .NET library for implementing CQRS with Clean Architecture. Commands mutate state; Queries return data and are side-effect-free. |

---

## The Core Idea: The Dependency Rule

Clean Architecture, as formalized by Robert C. Martin (Uncle Bob), is not a folder structure — it is a **dependency rule** enforced by project boundaries, package imports, or module references.

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION                            │
│  (Controllers, Widgets, CLI, gRPC handlers)                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 INFRASTRUCTURE                      │    │
│  │  (Database, External APIs, File I/O, Cache)         │    │
│  │                                                     │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │              APPLICATION                    │    │    │
│  │  │  (Use Cases, DTOs, Validators)              │    │    │
│  │  │                                             │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │            DOMAIN                   │    │    │    │
│  │  │  │  (Entities, Interfaces, Services)   │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

Arrows point INWARD. Outer layers depend on inner layers. Never the reverse.
```

The key constraint: **inner layers define interfaces; outer layers implement them.** This inversion is what makes the architecture "clean" — you can replace your entire database or swap your presentation framework without modifying a single line of business logic.

---

## 1. C# (.NET Web API)

The .NET ecosystem is heavily opinionated out of the box. The default scaffold (`dotnet new webapi`) produces a single project assembly, which converges toward a monolithic MVC pattern. This is fine for small microservices with single responsibilities but quickly turns into a tightly coupled mess for enterprise systems with evolving requirements.

### Typical Structure (Single Project Monolith)

```text
Solution_Name/
└── Project_Name.API/
    ├── Controllers/         # Handles HTTP requests AND business logic
    ├── Models/              # Database entities mixed with DTOs
    ├── Services/            # Business logic and database calls mixed
    ├── appsettings.json     # Configuration
    └── Program.cs           # Entry point and dependency injection
```

**Why this becomes problematic:**

- **Controllers bloat.** Developers add validation, business rules, and DB queries directly into action methods because there is no structural incentive to separate them.
- **Models are overloaded.** The same `User` class is sometimes the EF Core entity, the API request body, and the API response — violating SoC and making schema changes dangerous.
- **Services are a dumping ground.** `UserService` starts as a clean abstraction but accumulates 40 methods covering creation, authentication, password resets, profile management, and report generation.
- **Testing is painful.** Unit testing a controller that directly calls `DbContext` requires mocking the entire database layer.

### Clean Architecture Structure (Multi-Project Solution)

In production C#, the solution is split into distinct **Class Libraries** (separate `.csproj` projects) to enforce dependency rules via assembly references. The compiler itself prevents inner layers from referencing outer layers.

```text
EnterpriseSolution/
│
├── src/
│   ├── Project.Domain/                    # Layer 1: Core (innermost)
│   │   ├── Entities/
│   │   │   ├── Driver.cs                  # Identity-based domain object
│   │   │   ├── Ride.cs
│   │   │   └── Vehicle.cs
│   │   ├── Enums/
│   │   │   ├── RideStatus.cs              # Requested, InProgress, Completed, Cancelled
│   │   │   └── VehicleType.cs
│   │   ├── Exceptions/
│   │   │   ├── DomainException.cs         # Base domain exception
│   │   │   └── RideAlreadyAcceptedException.cs
│   │   ├── Interfaces/
│   │   │   ├── IRideRepository.cs         # Data access contract
│   │   │   ├── IDriverRepository.cs
│   │   │   └── INotificationService.cs    # External capability contract
│   │   └── Services/
│   │       └── FareCalculationService.cs  # Pure business logic (no dependencies)
│   │
│   ├── Project.Application/               # Layer 2: References Domain ONLY
│   │   ├── DTOs/
│   │   │   ├── RequestRideDto.cs
│   │   │   └── RideResponseDto.cs
│   │   ├── Interfaces/
│   │   │   └── IRideApplicationService.cs
│   │   ├── Mappings/
│   │   │   └── RideMappingProfile.cs      # AutoMapper or manual mapping
│   │   ├── UseCases/                      # Or Commands/Queries (CQRS)
│   │   │   ├── RequestRideUseCase.cs
│   │   │   ├── AcceptRideUseCase.cs
│   │   │   └── CompleteRideUseCase.cs
│   │   └── Validators/
│   │       └── RequestRideValidator.cs    # FluentValidation rules
│   │
│   ├── Project.Infrastructure/            # Layer 3: References Application & Domain
│   │   ├── Data/
│   │   │   ├── AppDbContext.cs            # EF Core DbContext
│   │   │   ├── Configurations/
│   │   │   │   └── RideConfiguration.cs   # Fluent API entity config
│   │   │   └── Migrations/
│   │   ├── Repositories/
│   │   │   ├── RideRepository.cs          # Implements IRideRepository
│   │   │   └── DriverRepository.cs
│   │   ├── Services/
│   │   │   ├── PushNotificationService.cs # Implements INotificationService
│   │   │   └── StripePaymentService.cs
│   │   └── DependencyInjection.cs         # Extension method: services.AddInfrastructure()
│   │
│   └── Project.Api/                       # Layer 4: References Application & Infrastructure
│       ├── Controllers/
│       │   └── RidesController.cs         # Thin: parse HTTP → call UseCase → return DTO
│       ├── Middlewares/
│       │   ├── ExceptionHandlingMiddleware.cs
│       │   └── JwtAuthMiddleware.cs
│       ├── Filters/
│       │   └── ValidationFilter.cs
│       ├── appsettings.json
│       └── Program.cs                     # Wires DI container, middleware pipeline
│
├── tests/
│   ├── Project.Domain.Tests/
│   ├── Project.Application.Tests/
│   └── Project.Api.IntegrationTests/
│
└── EnterpriseSolution.sln
```

### C# Project References (Enforcing the Dependency Rule)

The `.csproj` files enforce the Dependency Rule at compile time:

```xml
<!-- Project.Domain.csproj — ZERO project references -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
```

```xml
<!-- Project.Application.csproj — References Domain ONLY -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\Project.Domain\Project.Domain.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="FluentValidation" Version="11.*" />
  </ItemGroup>
</Project>
```

```xml
<!-- Project.Infrastructure.csproj — References Application & Domain -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\Project.Domain\Project.Domain.csproj" />
    <ProjectReference Include="..\Project.Application\Project.Application.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.*" />
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.*" />
  </ItemGroup>
</Project>
```

```xml
<!-- Project.Api.csproj — References Application & Infrastructure -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\Project.Application\Project.Application.csproj" />
    <ProjectReference Include="..\Project.Infrastructure\Project.Infrastructure.csproj" />
  </ItemGroup>
</Project>
```

If a developer in `Project.Domain` tries to `using Project.Infrastructure;`, the compiler will reject it. The dependency rule is structurally enforced, not merely documented.

---

## 2. Dart (Flutter for iOS/Android)

Flutter is inherently a UI toolkit. It provides zero architectural guidance out of the box, which means that without deliberate structure, codebases gravitate toward the "God Widget" anti-pattern — where UI rendering, state management, HTTP calls, JSON parsing, and business logic coexist in the same file.

### Typical Structure (Folder-by-Type)

```text
lib/
├── models/          # ALL data models in the app
├── screens/         # ALL UI pages
├── services/        # ALL network and database calls
├── widgets/         # ALL reusable UI components
└── main.dart
```

**Why this becomes problematic:**

- **Feature discovery is archaeological.** To understand the "Ride Tracking" feature, you must open `models/ride.dart`, `screens/ride_screen.dart`, `services/ride_service.dart`, and `widgets/ride_map.dart` across four different directories. Multiply by 30 features and discovery becomes excavation.
- **Implicit coupling.** Without layer boundaries, a screen widget directly calls an HTTP service, which directly deserializes into a model that is also used as UI state. Changing the API response format forces changes in the UI layer.
- **Testing is ad hoc.** No clear seam for mocking exists because there are no interfaces — just concrete classes passed around by type.

### Clean Architecture Structure (Feature-First)

For highly scalable mobile applications, a feature-first Clean Architecture is preferred. Each feature (Authentication, Ride Tracking, Payments) contains its own isolated Clean Architecture layers.

```text
lib/
├── core/                           # App-wide shared utilities
│   ├── constants/
│   │   └── app_constants.dart
│   ├── errors/
│   │   ├── failures.dart           # Failure sealed class hierarchy
│   │   └── exceptions.dart         # Raw exception wrappers
│   ├── network/
│   │   ├── api_client.dart         # Configured Dio instance
│   │   └── interceptors.dart       # Auth token, retry logic
│   ├── theme/
│   │   └── app_theme.dart
│   └── usecases/
│       └── usecase.dart            # Abstract UseCase<Type, Params> base class
│
├── features/
│   ├── authentication/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── user.dart       # Pure Dart class, no annotations
│   │   │   ├── repositories/
│   │   │   │   └── i_auth_repository.dart
│   │   │   └── usecases/
│   │   │       ├── login_user.dart
│   │   │       └── register_user.dart
│   │   ├── data/
│   │   │   ├── models/
│   │   │   │   └── user_model.dart # extends/maps to User entity + fromJson/toJson
│   │   │   ├── datasources/
│   │   │   │   ├── auth_remote_datasource.dart
│   │   │   │   └── auth_local_datasource.dart  # SharedPreferences/SQLite
│   │   │   └── repositories/
│   │   │       └── auth_repository_impl.dart   # Implements IAuthRepository
│   │   └── presentation/
│   │       ├── controllers/        # Riverpod StateNotifiers / Bloc
│   │       │   └── auth_controller.dart
│   │       ├── pages/
│   │       │   ├── login_page.dart
│   │       │   └── register_page.dart
│   │       └── widgets/
│   │           └── auth_form.dart
│   │
│   └── ride_tracking/
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── ride.dart
│       │   │   └── location_point.dart
│       │   ├── repositories/
│       │   │   └── i_ride_repository.dart
│       │   └── usecases/
│       │       ├── request_ride.dart
│       │       └── track_active_ride.dart
│       ├── data/
│       │   ├── models/
│       │   │   └── ride_model.dart
│       │   ├── datasources/
│       │   │   ├── ride_remote_datasource.dart
│       │   │   └── ride_local_datasource.dart
│       │   └── repositories/
│       │       └── ride_repository_impl.dart
│       └── presentation/
│           ├── controllers/
│           │   └── ride_tracking_controller.dart
│           ├── pages/
│           │   └── active_ride_page.dart
│           └── widgets/
│               ├── map_overlay_widget.dart
│               └── driver_card.dart
│
├── injection_container.dart        # get_it / riverpod setup
└── main.dart                       # ProviderScope and routing
```

### Dart Dependency Injection Mechanics

Flutter does not have a built-in DI container. The community standard is `get_it` (a service locator) combined with `injectable` (code generation). Alternatively, Riverpod's `Provider` system serves as a functional DI mechanism.

```dart
// injection_container.dart (using get_it)
import 'package:get_it/get_it.dart';

final sl = GetIt.instance;  // sl = service locator

Future<void> init() async {
  // Use Cases
  sl.registerLazySingleton(() => LoginUser(sl()));
  sl.registerLazySingleton(() => RegisterUser(sl()));

  // Repositories — interface mapped to implementation
  sl.registerLazySingleton<IAuthRepository>(
    () => AuthRepositoryImpl(
      remoteDatasource: sl(),
      localDatasource: sl(),
    ),
  );

  // Data Sources
  sl.registerLazySingleton<AuthRemoteDatasource>(
    () => AuthRemoteDatasourceImpl(client: sl()),
  );

  // External
  sl.registerLazySingleton(() => Dio());
}
```

The Use Case `LoginUser` receives `IAuthRepository` (an abstraction from the domain layer). It never knows whether the concrete implementation hits Firebase, a REST API, or an in-memory stub. This is the Dependency Rule in action.

---

## 3. TypeScript (Node.js Backend)

TypeScript brings type safety to JavaScript, but Node.js frameworks (particularly Express) are notoriously unopinionated. Without deliberate structure, developers build massive, untyped route handlers that parse JSON, validate inputs, execute business rules, and query the database in a single function.

### Typical Structure (Express.js Default)

```text
src/
├── controllers/     # Req/Res handlers and business logic
├── models/          # Mongoose or TypeORM schemas
├── routes/          # Express router definitions
├── utils/           # Helper functions
└── index.ts         # Server setup
```

**Why this becomes problematic:**

- **Controller Bloat.** A single `userController.ts` ends up at 500+ lines because it handles request parsing, input validation, password hashing, database queries, email dispatch, and response formatting.
- **Framework lock-in.** Business logic scattered across Express route handlers means migrating to Fastify, Hono, or a GraphQL resolver requires rewriting business rules alongside transport code.
- **Untestable.** Testing a controller requires spinning up Express, mocking `req`/`res` objects, and seeding a database — integration testing disguised as unit testing.

### Clean Architecture Structure

TypeScript excels at Clean Architecture because of its robust interface support (`interface`, `abstract class`), enabling strict Dependency Injection.

```text
src/
├── domain/                          # Enterprise business rules
│   ├── entities/
│   │   ├── User.ts                  # Plain class with business invariants
│   │   └── Session.ts
│   ├── enums/
│   │   └── UserRole.ts
│   ├── interfaces/
│   │   ├── IUserRepository.ts       # Data access contract
│   │   ├── ISessionRepository.ts
│   │   └── IEmailService.ts         # External capability contract
│   └── services/
│       └── PasswordPolicyService.ts # Pure business logic
│
├── application/                     # Application business rules
│   ├── use-cases/
│   │   ├── RegisterUserUseCase.ts
│   │   ├── AuthenticateUserUseCase.ts
│   │   └── GetUserProfileUseCase.ts
│   ├── dtos/
│   │   ├── RegisterUserRequestDto.ts
│   │   └── UserResponseDto.ts
│   └── validators/
│       └── RegisterUserValidator.ts
│
├── infrastructure/                  # Frameworks and drivers
│   ├── database/
│   │   ├── PostgresConnection.ts
│   │   └── migrations/
│   ├── repositories/
│   │   ├── UserRepositoryImpl.ts    # Implements IUserRepository
│   │   └── SessionRepositoryImpl.ts
│   ├── services/
│   │   ├── SendGridEmailService.ts  # Implements IEmailService
│   │   ├── JwtAuthService.ts
│   │   └── RedisCacheService.ts
│   └── config/
│       └── env.ts                   # Environment variable parsing
│
├── presentation/                    # Interface adapters (delivery mechanism)
│   ├── http/
│   │   ├── controllers/
│   │   │   └── UserController.ts    # Parses HTTP, calls UseCase, returns DTO
│   │   ├── middlewares/
│   │   │   ├── AuthMiddleware.ts
│   │   │   └── ErrorHandlerMiddleware.ts
│   │   └── routes/
│   │       └── userRoutes.ts
│   └── Server.ts                    # Express/Fastify instantiation
│
├── container.ts                     # DI wiring (tsyringe, inversify, or manual)
└── main.ts                          # Application bootstrap
```

### TypeScript DI & Interface Enforcement

TypeScript interfaces are erased at runtime, so DI requires either a container library or manual wiring. Common approaches:

**Option A: Manual Constructor Injection (zero dependencies)**

```typescript
// main.ts — Composition Root
import { UserController } from './presentation/http/controllers/UserController';
import { RegisterUserUseCase } from './application/use-cases/RegisterUserUseCase';
import { UserRepositoryImpl } from './infrastructure/repositories/UserRepositoryImpl';
import { SendGridEmailService } from './infrastructure/services/SendGridEmailService';
import { PostgresConnection } from './infrastructure/database/PostgresConnection';

const db = new PostgresConnection();
const userRepository = new UserRepositoryImpl(db);
const emailService = new SendGridEmailService();
const registerUser = new RegisterUserUseCase(userRepository, emailService);
const userController = new UserController(registerUser);

// Wire into Express
app.post('/api/users', (req, res) => userController.register(req, res));
```

**Option B: `tsyringe` (decorator-based DI container)**

```typescript
import { container } from 'tsyringe';
import { IUserRepository } from './domain/interfaces/IUserRepository';
import { UserRepositoryImpl } from './infrastructure/repositories/UserRepositoryImpl';

container.register<IUserRepository>('IUserRepository', { useClass: UserRepositoryImpl });

// In RegisterUserUseCase.ts
@injectable()
export class RegisterUserUseCase {
  constructor(
    @inject('IUserRepository') private userRepo: IUserRepository,
    @inject('IEmailService') private emailService: IEmailService,
  ) {}
}
```

Both approaches satisfy the Dependency Rule: `RegisterUserUseCase` depends on `IUserRepository` (a Domain interface), never on `UserRepositoryImpl` (an Infrastructure class).

---

## Comparison Matrix: Typical vs Clean

| Dimension | Typical (Framework Default) | Clean Architecture |
| :--- | :--- | :--- |
| **Optimized for** | Speed of initial setup | Long-term maintainability |
| **Dependency direction** | Ad hoc (anything imports anything) | Strictly inward (enforced by project/package boundaries) |
| **Business logic location** | Controllers, route handlers, services | Domain layer (entities, domain services) and Application layer (use cases) |
| **Database coupling** | Models are often ORM entities used everywhere | ORM models isolated in Infrastructure; domain entities are framework-free |
| **Testability** | Integration tests masquerading as unit tests | True unit tests: domain and application layers have zero framework deps |
| **Onboarding time** | Low (familiar folder names) | Medium (requires understanding the layer rules) |
| **Refactoring cost** | High (changes ripple across layers) | Low (changes are contained within layer boundaries) |
| **Framework migration** | Rewrite | Replace Presentation and/or Infrastructure; Domain and Application untouched |
| **Ideal team size** | 1–3 developers | 3+ developers, or any team expecting >12 months of active development |
| **Ideal project lifespan** | Prototypes, hackathons, microservices with single responsibility | Enterprise systems, products with evolving requirements, multi-year codebases |

---

## Data Flow Walkthrough: User Registration

To make Clean Architecture concrete, this section traces a single operation — **registering a new user** — through every layer, from the HTTP request to the database write and back.

### Step-by-Step: From HTTP to Database and Back

```
Client (HTTP POST /api/users)
    │
    ▼
┌──────────────────────────────────────────┐
│ PRESENTATION: UserController.register()  │
│  1. Parse request body into DTO          │
│  2. Call RegisterUserUseCase.execute()    │
│  3. Return formatted HTTP response       │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ APPLICATION: RegisterUserUseCase         │
│  1. Validate DTO (RegisterUserValidator) │
│  2. Check IUserRepository.existsByEmail()│
│  3. Hash password (IHashService)         │
│  4. Create User entity                   │
│  5. Call IUserRepository.save(user)      │
│  6. Call IEmailService.sendWelcome()     │
│  7. Map User entity → UserResponseDto    │
│  8. Return UserResponseDto               │
└──────────────┬───────────────────────────┘
               │ (calls interfaces)
               ▼
┌──────────────────────────────────────────┐
│ INFRASTRUCTURE: UserRepositoryImpl       │
│  1. Map User entity → UserModel (ORM)    │
│  2. INSERT INTO users ... (PostgreSQL)   │
│  3. Map result back to User entity       │
│  4. Return User entity                   │
│                                          │
│ INFRASTRUCTURE: SendGridEmailService     │
│  1. Build email template                 │
│  2. Call SendGrid API                    │
└──────────────────────────────────────────┘
```

**Key observation:** The Application layer calls `IUserRepository.save()` and `IEmailService.sendWelcome()`. It has no idea whether the repository is backed by PostgreSQL, MongoDB, or a file. It has no idea whether the email service uses SendGrid, Mailgun, or `console.log()`. That is the entire point.

### Concrete Code Example (TypeScript)

**Domain: Entity**
```typescript
// domain/entities/User.ts
export class User {
  constructor(
    public readonly id: string,
    public readonly email: string,
    public readonly hashedPassword: string,
    public readonly createdAt: Date,
  ) {}
}
```

**Domain: Interface**
```typescript
// domain/interfaces/IUserRepository.ts
import { User } from '../entities/User';

export interface IUserRepository {
  existsByEmail(email: string): Promise<boolean>;
  save(user: User): Promise<User>;
  findById(id: string): Promise<User | null>;
}
```

**Application: Use Case**
```typescript
// application/use-cases/RegisterUserUseCase.ts
import { User } from '../../domain/entities/User';
import { IUserRepository } from '../../domain/interfaces/IUserRepository';
import { IEmailService } from '../../domain/interfaces/IEmailService';
import { IHashService } from '../../domain/interfaces/IHashService';
import { RegisterUserRequestDto } from '../dtos/RegisterUserRequestDto';
import { UserResponseDto } from '../dtos/UserResponseDto';
import { v4 as uuidv4 } from 'uuid';

export class RegisterUserUseCase {
  constructor(
    private userRepo: IUserRepository,
    private emailService: IEmailService,
    private hashService: IHashService,
  ) {}

  async execute(dto: RegisterUserRequestDto): Promise<UserResponseDto> {
    // 1. Check uniqueness
    const exists = await this.userRepo.existsByEmail(dto.email);
    if (exists) {
      throw new Error('Email already registered');
    }

    // 2. Hash password
    const hashed = await this.hashService.hash(dto.password);

    // 3. Create domain entity
    const user = new User(uuidv4(), dto.email, hashed, new Date());

    // 4. Persist
    const saved = await this.userRepo.save(user);

    // 5. Side effect: send welcome email (fire-and-forget or awaited)
    await this.emailService.sendWelcome(saved.email);

    // 6. Map to response DTO
    return { id: saved.id, email: saved.email, createdAt: saved.createdAt.toISOString() };
  }
}
```

**Infrastructure: Repository Implementation**
```typescript
// infrastructure/repositories/UserRepositoryImpl.ts
import { IUserRepository } from '../../domain/interfaces/IUserRepository';
import { User } from '../../domain/entities/User';
import { Pool } from 'pg';

export class UserRepositoryImpl implements IUserRepository {
  constructor(private pool: Pool) {}

  async existsByEmail(email: string): Promise<boolean> {
    const result = await this.pool.query('SELECT 1 FROM users WHERE email = $1', [email]);
    return result.rowCount > 0;
  }

  async save(user: User): Promise<User> {
    await this.pool.query(
      'INSERT INTO users (id, email, hashed_password, created_at) VALUES ($1, $2, $3, $4)',
      [user.id, user.email, user.hashedPassword, user.createdAt],
    );
    return user;
  }

  async findById(id: string): Promise<User | null> {
    const result = await this.pool.query('SELECT * FROM users WHERE id = $1', [id]);
    if (result.rows.length === 0) return null;
    const row = result.rows[0];
    return new User(row.id, row.email, row.hashed_password, row.created_at);
  }
}
```

**Presentation: Controller**
```typescript
// presentation/http/controllers/UserController.ts
import { Request, Response } from 'express';
import { RegisterUserUseCase } from '../../../application/use-cases/RegisterUserUseCase';

export class UserController {
  constructor(private registerUser: RegisterUserUseCase) {}

  async register(req: Request, res: Response): Promise<void> {
    try {
      const dto = req.body; // In production, validate/parse with zod or class-validator
      const result = await this.registerUser.execute(dto);
      res.status(201).json(result);
    } catch (error: any) {
      if (error.message === 'Email already registered') {
        res.status(409).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
```

Notice the controller is **thin**: it parses HTTP, delegates to the Use Case, and formats the HTTP response. It contains zero business logic.

---

## When to Use Clean Architecture (and When Not To)

Clean Architecture is not universally appropriate. Over-engineering a weekend project with four layers and a DI container is as harmful as under-engineering a five-year enterprise product with a single-file Express handler.

**Use Clean Architecture when:**

- The project is expected to live and evolve for more than 12 months.
- The team has 3+ developers (separation prevents merge conflicts and cognitive overload).
- Business logic is complex and needs to be independently testable.
- You anticipate swapping infrastructure (e.g., migrating from MongoDB to PostgreSQL, or from REST to gRPC).
- Regulatory or compliance requirements demand auditable, well-separated codebases.

**Use the typical/default structure when:**

- Building a prototype, proof of concept, or hackathon project.
- The microservice has a single responsibility (e.g., an image resizer, a webhook relay).
- The team is 1–2 developers and the project has a defined, short lifespan.
- Time-to-market is the dominant constraint and you need to ship in days, not months.

**Hybrid approach:**

Many teams start with the typical structure for speed, then refactor toward Clean Architecture as the codebase grows past a complexity threshold. This is pragmatic if (and only if) you proactively refactor before the monolith becomes load-bearing. The refactoring cost increases exponentially with codebase size.

---

## Common Pitfalls

1. **Premature Abstraction.** Creating `IUserRepository`, `UserRepositoryImpl`, `UserRepositoryImplFactory`, and `UserRepositoryImplFactoryProvider` for a CRUD app with three endpoints is not Clean Architecture — it is ceremony. Abstractions should be introduced at the point of genuine need.

2. **Anemic Domain Model.** Placing all logic in Use Cases and leaving entities as dumb data bags defeats the purpose. Entities should enforce their own invariants: a `Ride` entity should reject a `Complete()` call if its status is `Cancelled`.

3. **Leaking Infrastructure into Domain.** Decorating domain entities with `[Table("users")]` or `@Entity()` couples the innermost layer to a specific ORM. Use separate model classes in Infrastructure and map between them.

4. **Over-layering.** Clean Architecture has four layers, not forty. Adding `Mappers/`, `Adapters/`, `Gateways/`, `Ports/`, `Translators/`, and `Coordinators/` folders creates navigational overhead without proportional benefit. Keep the structure as flat as the complexity demands.

5. **Ignoring the DI Composition Root.** If your DI wiring is scattered across multiple files with no clear entry point, debugging dependency resolution failures becomes a nightmare. Centralize registration in a single `DependencyInjection.cs`, `injection_container.dart`, or `container.ts`.

6. **Feature Slicing vs Layer Slicing Confusion (Flutter/Mobile).** In Flutter, always prefer feature-first (`features/auth/domain/...`) over layer-first (`domain/auth/...`). Feature-first keeps related code co-located, which matches how developers think about and navigate a mobile app.

---

## References & Further Reading

- Robert C. Martin, *Clean Architecture: A Craftsman's Guide to Software Structure and Design* (2017)
- Robert C. Martin, [The Clean Architecture (blog post)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- Jason Taylor, [Clean Architecture Solution Template for .NET](https://github.com/jasontaylordev/CleanArchitecture)
- Reso Coder, [Flutter TDD Clean Architecture (series)](https://resocoder.com/flutter-clean-architecture-tdd/)
- MediatR (CQRS for .NET): https://github.com/jbogard/MediatR
- tsyringe (TypeScript DI): https://github.com/microsoft/tsyringe
- InversifyJS (TypeScript IoC): https://inversify.io/
- get_it (Dart Service Locator): https://pub.dev/packages/get_it
- FluentValidation (.NET): https://docs.fluentvalidation.net/

---

*This guide follows the tone, structure, and style of other guides in this repository: header metadata, badges, an overview, contents list, thorough sections, code blocks, comparison tables, pitfalls, and practical recommendations.*
