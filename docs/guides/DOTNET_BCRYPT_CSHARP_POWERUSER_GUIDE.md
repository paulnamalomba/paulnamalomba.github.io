# DOTNET BCrypt PowerUser Guide (C#)

**Last updated**: December 05, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/.NET-BCrypt-blue.svg)](https://github.com/BcryptNet/bcrypt.net)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

BCrypt.Net-Next is a robust password hashing library for .NET implementing the OpenBSD bcrypt algorithm with adaptive cost factors for future-proof security. This guide covers password hashing, verification, work factor selection, salt generation, and secure defaults for authentication systems. Power users need to understand computational cost tuning, hash format compatibility, and migration strategies for production applications.

## Contents

- [DOTNET BCrypt PowerUser Guide (C#)](#dotnet-bcrypt-poweruser-guide-c)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Basic Password Hashing and Verification](#basic-password-hashing-and-verification)
    - [Custom Work Factor and Enhanced Entropy](#custom-work-factor-and-enhanced-entropy)
    - [ASP.NET Core Authentication Implementation](#aspnet-core-authentication-implementation)
    - [Password Migration and Rehashing Strategy](#password-migration-and-rehashing-strategy)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install package**: `dotnet add package BCrypt.Net-Next`
2. **Hash password**: `string hash = BCrypt.Net.BCrypt.HashPassword("password123");`
3. **Verify password**: `bool isValid = BCrypt.Net.BCrypt.Verify("password123", hash);`
4. **Use in ASP.NET Core**: Add to dependency injection and use in user registration/login endpoints

## Key Concepts

- **Work Factor (Cost)**: Number of hashing rounds (2^cost); default is 11, recommended range 10-12 for production; higher values increase security but slow down hashing
- **Salt**: Random data automatically generated and embedded in hash output; prevents rainbow table attacks and ensures identical passwords produce different hashes
- **Hash Format**: Output format is `$2a$[cost]$[22-char salt][31-char hash]`; compatible with bcrypt implementations across languages
- **Enhanced Entropy**: BCrypt.Net supports enhanced hashing with SHA-384 pre-hashing for passwords >72 bytes to overcome bcrypt's built-in length limitation
- **Verification**: Constant-time comparison prevents timing attacks; always use `Verify()` method instead of string comparison
- **Hash Revision**: `$2a$` is standard; `$2b$` fixes rare edge cases; `$2y$` is PHP-specific; stick with `$2a$` or `$2b$` for interoperability

## Configuration and Best Practices

**ASP.NET Core Dependency Injection Setup**:

```csharp
// Program.cs or Startup.cs
builder.Services.AddScoped<IPasswordHasher, BcryptPasswordHasher>();

public interface IPasswordHasher
{
    string HashPassword(string password);
    bool VerifyPassword(string password, string hash);
}

public class BcryptPasswordHasher : IPasswordHasher
{
    private const int WorkFactor = 12; // Adjust based on performance requirements

    public string HashPassword(string password)
    {
        return BCrypt.Net.BCrypt.HashPassword(password, WorkFactor);
    }

    public bool VerifyPassword(string password, string hash)
    {
        return BCrypt.Net.BCrypt.Verify(password, hash);
    }
}
```

**Best Practices**:

- Use work factor 11-12 for web applications; 13-14 for high-security systems
- Never store plaintext passwords or use reversible encryption
- Hash passwords on server-side only; never send hashes from client
- Implement rate limiting on login endpoints to prevent brute-force attacks
- Use `EnhancedEntropy` for passwords that may exceed 72 bytes
- Store hashes in NVARCHAR(60) or VARCHAR(60) database columns
- Implement password complexity requirements before hashing

## Security Considerations

1. **Work Factor Selection**: Balance security and performance; benchmark on production hardware to ensure <250ms hashing time
2. **Timing Attacks**: Always use `BCrypt.Verify()` which implements constant-time comparison; never compare hash strings directly
3. **Password Migration**: When updating work factors, rehash passwords on successful login rather than forcing password resets
4. **Memory Security**: Clear sensitive data from memory after hashing; use `SecureString` for password input when possible
5. **Distributed Systems**: Ensure consistent work factors across all authentication servers to avoid confusion and security gaps
6. **Audit Logging**: Log failed login attempts with rate limiting; avoid logging successful authentication details
7. **Hash Storage**: Store in binary format or base64 to avoid encoding issues; never truncate hash values

**Secure User Registration Example**:

```csharp
public class UserService
{
    private readonly IPasswordHasher _passwordHasher;
    private readonly IUserRepository _userRepository;

    public UserService(IPasswordHasher passwordHasher, IUserRepository userRepository)
    {
        _passwordHasher = passwordHasher;
        _userRepository = userRepository;
    }

    public async Task<Result> RegisterUser(string email, string password)
    {
        // Validate password complexity before hashing
        if (password.Length < 12)
            return Result.Fail("Password must be at least 12 characters");

        if (!HasComplexity(password))
            return Result.Fail("Password must contain uppercase, lowercase, digit, and symbol");

        // Check if user exists
        if (await _userRepository.EmailExists(email))
            return Result.Fail("Email already registered");

        // Hash password
        string passwordHash = _passwordHasher.HashPassword(password);

        // Store user with hash
        var user = new User
        {
            Email = email,
            PasswordHash = passwordHash,
            CreatedAt = DateTime.UtcNow
        };

        await _userRepository.CreateUser(user);
        return Result.Success();
    }

    private bool HasComplexity(string password)
    {
        return password.Any(char.IsUpper) &&
               password.Any(char.IsLower) &&
               password.Any(char.IsDigit) &&
               password.Any(c => !char.IsLetterOrDigit(c));
    }
}
```

## Examples

### Basic Password Hashing and Verification

Hash user passwords during registration and verify them during login with automatic salt generation.

```csharp
using BCrypt.Net;

public class PasswordExample
{
    public void BasicHashingExample()
    {
        // Hash a password with default work factor (11)
        string password = "MySecurePassword123!";
        string hash = BCrypt.Net.BCrypt.HashPassword(password);
        Console.WriteLine($"Hash: {hash}");
        // Output: $2a$11$randomsalt...hashvalue

        // Verify correct password
        bool isValid = BCrypt.Net.BCrypt.Verify(password, hash);
        Console.WriteLine($"Password valid: {isValid}"); // True

        // Verify incorrect password
        bool isInvalid = BCrypt.Net.BCrypt.Verify("WrongPassword", hash);
        Console.WriteLine($"Wrong password: {isInvalid}"); // False

        // Each hash is unique due to random salt
        string hash2 = BCrypt.Net.BCrypt.HashPassword(password);
        Console.WriteLine($"Hashes equal: {hash == hash2}"); // False
        Console.WriteLine($"Both verify: {BCrypt.Net.BCrypt.Verify(password, hash2)}"); // True
    }
}
```

### Custom Work Factor and Enhanced Entropy

Configure work factors for different security requirements and handle long passwords with enhanced entropy mode.

```csharp
using BCrypt.Net;

public class AdvancedHashingExample
{
    public void CustomWorkFactorExample()
    {
        string password = "SecurePassword123!";

        // Low work factor (faster, less secure) - use for testing only
        string hashFast = BCrypt.Net.BCrypt.HashPassword(password, 4);
        Console.WriteLine($"Fast hash (work factor 4): {hashFast}");

        // Standard work factor (recommended for production)
        string hashStandard = BCrypt.Net.BCrypt.HashPassword(password, 11);
        Console.WriteLine($"Standard hash (work factor 11): {hashStandard}");

        // High work factor (slower, more secure)
        string hashSecure = BCrypt.Net.BCrypt.HashPassword(password, 13);
        Console.WriteLine($"Secure hash (work factor 13): {hashSecure}");

        // Benchmark hashing time
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        BCrypt.Net.BCrypt.HashPassword(password, 12);
        stopwatch.Stop();
        Console.WriteLine($"Hashing time (factor 12): {stopwatch.ElapsedMilliseconds}ms");

        // Enhanced entropy for long passwords (>72 bytes)
        string longPassword = new string('x', 100);
        string hashEnhanced = BCrypt.Net.BCrypt.EnhancedHashPassword(longPassword, 11);
        Console.WriteLine($"Enhanced hash: {hashEnhanced}");

        bool verifyEnhanced = BCrypt.Net.BCrypt.EnhancedVerify(longPassword, hashEnhanced);
        Console.WriteLine($"Enhanced verify: {verifyEnhanced}"); // True
    }
}
```

### ASP.NET Core Authentication Implementation

Implement complete user authentication with registration, login, and password change functionality in ASP.NET Core.

```csharp
using Microsoft.AspNetCore.Mvc;
using BCrypt.Net;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IUserRepository _userRepository;
    private readonly ILogger<AuthController> _logger;
    private const int WorkFactor = 12;

    public AuthController(IUserRepository userRepository, ILogger<AuthController> logger)
    {
        _userRepository = userRepository;
        _logger = logger;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        // Validate input
        if (string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Password))
            return BadRequest("Email and password are required");

        // Check password strength
        if (request.Password.Length < 12)
            return BadRequest("Password must be at least 12 characters");

        // Check if email exists
        var existingUser = await _userRepository.GetByEmail(request.Email);
        if (existingUser != null)
            return Conflict("Email already registered");

        // Hash password
        string passwordHash = BCrypt.Net.BCrypt.HashPassword(request.Password, WorkFactor);

        // Create user
        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = request.Email,
            PasswordHash = passwordHash,
            CreatedAt = DateTime.UtcNow
        };

        await _userRepository.Create(user);
        _logger.LogInformation("User registered: {Email}", request.Email);

        return Ok(new { message = "Registration successful", userId = user.Id });
    }

    [HttpPost("login")]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        // Get user by email
        var user = await _userRepository.GetByEmail(request.Email);
        if (user == null)
        {
            _logger.LogWarning("Login attempt for non-existent email: {Email}", request.Email);
            return Unauthorized("Invalid credentials");
        }

        // Verify password
        bool isValid = BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash);
        if (!isValid)
        {
            _logger.LogWarning("Failed login attempt for user: {Email}", request.Email);
            return Unauthorized("Invalid credentials");
        }

        // Check if work factor needs update (optional migration)
        if (NeedsRehash(user.PasswordHash, WorkFactor))
        {
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password, WorkFactor);
            await _userRepository.Update(user);
            _logger.LogInformation("Password rehashed for user: {Email}", request.Email);
        }

        _logger.LogInformation("User logged in: {Email}", request.Email);

        // Generate JWT or session token here
        return Ok(new { message = "Login successful", userId = user.Id });
    }

    [HttpPost("change-password")]
    public async Task<IActionResult> ChangePassword([FromBody] ChangePasswordRequest request)
    {
        // Get user
        var user = await _userRepository.GetById(request.UserId);
        if (user == null)
            return NotFound("User not found");

        // Verify current password
        bool isValid = BCrypt.Net.BCrypt.Verify(request.CurrentPassword, user.PasswordHash);
        if (!isValid)
            return Unauthorized("Current password is incorrect");

        // Validate new password
        if (request.NewPassword.Length < 12)
            return BadRequest("New password must be at least 12 characters");

        // Hash new password
        user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.NewPassword, WorkFactor);
        user.PasswordChangedAt = DateTime.UtcNow;

        await _userRepository.Update(user);
        _logger.LogInformation("Password changed for user: {UserId}", user.Id);

        return Ok(new { message = "Password changed successfully" });
    }

    private bool NeedsRehash(string hash, int targetWorkFactor)
    {
        // Extract work factor from hash (format: $2a$[workfactor]$...)
        var parts = hash.Split('$');
        if (parts.Length < 3)
            return false;

        if (int.TryParse(parts[2], out int currentWorkFactor))
        {
            return currentWorkFactor < targetWorkFactor;
        }

        return false;
    }
}

public record RegisterRequest(string Email, string Password);
public record LoginRequest(string Email, string Password);
public record ChangePasswordRequest(Guid UserId, string CurrentPassword, string NewPassword);
```

### Password Migration and Rehashing Strategy

Migrate existing password hashes to updated work factors without forcing password resets for active users.

```csharp
using BCrypt.Net;

public class PasswordMigrationService
{
    private const int TargetWorkFactor = 12;
    private const int MinimumWorkFactor = 10;
    private readonly IUserRepository _userRepository;
    private readonly ILogger<PasswordMigrationService> _logger;

    public PasswordMigrationService(IUserRepository userRepository, ILogger<PasswordMigrationService> logger)
    {
        _userRepository = userRepository;
        _logger = logger;
    }

    // Opportunistic rehashing on successful login
    public async Task<bool> AuthenticateAndRehash(string email, string password)
    {
        var user = await _userRepository.GetByEmail(email);
        if (user == null)
            return false;

        // Verify password
        bool isValid = BCrypt.Net.BCrypt.Verify(password, user.PasswordHash);
        if (!isValid)
            return false;

        // Check if rehashing is needed
        int currentWorkFactor = ExtractWorkFactor(user.PasswordHash);
        if (currentWorkFactor < TargetWorkFactor)
        {
            _logger.LogInformation(
                "Rehashing password for user {Email} (current factor: {Current}, target: {Target})",
                email, currentWorkFactor, TargetWorkFactor);

            // Rehash with target work factor
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(password, TargetWorkFactor);
            user.PasswordChangedAt = DateTime.UtcNow;
            await _userRepository.Update(user);
        }

        return true;
    }

    // Batch migration for inactive users (run as background job)
    public async Task MigrateWeakHashes()
    {
        var usersWithWeakHashes = await _userRepository.GetUsersWithWorkFactorBelow(MinimumWorkFactor);

        _logger.LogInformation("Found {Count} users with weak password hashes", usersWithWeakHashes.Count);

        foreach (var user in usersWithWeakHashes)
        {
            // For inactive users, force password reset
            user.RequiresPasswordReset = true;
            user.ResetReason = $"Security upgrade required (work factor {ExtractWorkFactor(user.PasswordHash)} < {MinimumWorkFactor})";
            await _userRepository.Update(user);

            _logger.LogInformation("Password reset required for user {Email}", user.Email);
        }
    }

    // Extract work factor from bcrypt hash
    private int ExtractWorkFactor(string hash)
    {
        try
        {
            // Hash format: $2a$[workfactor]$[salt][hash]
            var parts = hash.Split('$');
            if (parts.Length >= 3 && int.TryParse(parts[2], out int workFactor))
            {
                return workFactor;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to extract work factor from hash");
        }

        return 0;
    }

    // Generate password reset token with expiration
    public async Task<string> GeneratePasswordResetToken(string email)
    {
        var user = await _userRepository.GetByEmail(email);
        if (user == null)
            throw new Exception("User not found");

        // Generate secure random token
        string token = Convert.ToBase64String(System.Security.Cryptography.RandomNumberGenerator.GetBytes(32));

        user.PasswordResetToken = BCrypt.Net.BCrypt.HashPassword(token, 10); // Lower work factor for tokens
        user.PasswordResetTokenExpiry = DateTime.UtcNow.AddHours(1);

        await _userRepository.Update(user);

        return token; // Send this to user via email
    }
}
```

## Troubleshooting

**Hash Verification Fails**:

- **Error**: `Verify()` returns false for correct password
  - **Check encoding**: Ensure consistent UTF-8 encoding for password strings
  - **Verify hash format**: Hash must start with `$2a$`, `$2b$`, or `$2y$`
  - **Check truncation**: Verify hash string is not truncated in database (should be 60 characters)
  - **Test hash generation**: Generate new hash and verify immediately to isolate issue

**Performance Issues**:

- **Error**: Hashing takes too long (>500ms)
  - **Reduce work factor**: Lower from 12 to 11 or 10 based on requirements
  - **Benchmark hardware**: Test on production-equivalent hardware before deployment
  - **Use async operations**: Implement async hashing for web applications to avoid blocking
  - **Monitor CPU usage**: High work factors increase CPU load; consider load balancing

**Enhanced Entropy Errors**:

- **Error**: `EnhancedVerify()` fails for passwords hashed with `EnhancedHashPassword()`
  - **Consistency required**: Must use Enhanced methods for both hashing and verification
  - **Password length**: Enhanced mode is for passwords >72 bytes; unnecessary for shorter passwords
  - **Migration**: Cannot mix standard and enhanced hashes without tracking mode per user

**Database Storage Issues**:

```csharp
// Common database column configurations
// SQL Server
CREATE TABLE Users (
    Id UNIQUEIDENTIFIER PRIMARY KEY,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(60) NOT NULL,  -- Must be 60+ chars
    CreatedAt DATETIME2 NOT NULL
);

// PostgreSQL
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(60) NOT NULL,  -- Must be 60+ chars
    created_at TIMESTAMPTZ NOT NULL
);

// Entity Framework Core configuration
public class User
{
    public Guid Id { get; set; }

    [Required]
    [StringLength(255)]
    public string Email { get; set; }

    [Required]
    [StringLength(60)]  // Exactly 60 characters for bcrypt
    public string PasswordHash { get; set; }

    public DateTime CreatedAt { get; set; }
}
```

## Performance and Tuning

**Work Factor Benchmarking**:

```csharp
using System.Diagnostics;
using BCrypt.Net;

public class BcryptBenchmark
{
    public void BenchmarkWorkFactors()
    {
        string password = "TestPassword123!";

        for (int workFactor = 4; workFactor <= 14; workFactor++)
        {
            var stopwatch = Stopwatch.StartNew();
            int iterations = workFactor <= 10 ? 100 : (workFactor <= 12 ? 10 : 1);

            for (int i = 0; i < iterations; i++)
            {
                BCrypt.Net.BCrypt.HashPassword(password, workFactor);
            }

            stopwatch.Stop();
            double avgTime = stopwatch.ElapsedMilliseconds / (double)iterations;

            Console.WriteLine($"Work Factor {workFactor}: {avgTime:F2}ms per hash");
            Console.WriteLine($"  Iterations per second: {1000 / avgTime:F0}");
            Console.WriteLine($"  Security: 2^{workFactor} = {Math.Pow(2, workFactor):N0} iterations");
        }
    }
}

// Example output:
// Work Factor 10: 55ms per hash
// Work Factor 11: 110ms per hash (recommended minimum)
// Work Factor 12: 220ms per hash (recommended production)
// Work Factor 13: 440ms per hash (high security)
```

**Async Hashing for Web Applications**:

```csharp
using System.Threading.Tasks;
using BCrypt.Net;

public class AsyncPasswordService
{
    // Offload CPU-intensive hashing to thread pool
    public async Task<string> HashPasswordAsync(string password, int workFactor = 12)
    {
        return await Task.Run(() => BCrypt.Net.BCrypt.HashPassword(password, workFactor));
    }

    public async Task<bool> VerifyPasswordAsync(string password, string hash)
    {
        return await Task.Run(() => BCrypt.Net.BCrypt.Verify(password, hash));
    }
}

// Usage in ASP.NET Core controller
[HttpPost("register")]
public async Task<IActionResult> Register([FromBody] RegisterRequest request)
{
    var passwordService = new AsyncPasswordService();
    string hash = await passwordService.HashPasswordAsync(request.Password);

    // Save user with hash
    return Ok();
}
```

**Memory and Resource Optimization**:

```csharp
public class OptimizedPasswordService
{
    private const int MaxConcurrentHashOperations = 4;
    private readonly SemaphoreSlim _semaphore;

    public OptimizedPasswordService()
    {
        _semaphore = new SemaphoreSlim(MaxConcurrentHashOperations);
    }

    // Limit concurrent hashing operations to prevent CPU saturation
    public async Task<string> HashPasswordWithThrottling(string password, int workFactor = 12)
    {
        await _semaphore.WaitAsync();
        try
        {
            return await Task.Run(() => BCrypt.Net.BCrypt.HashPassword(password, workFactor));
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
```

**Recommended Work Factors by Use Case**:

- **Development/Testing**: 4-6 (fast feedback)
- **Low-security applications**: 10 (~60ms)
- **Standard web applications**: 11-12 (~120-220ms)
- **High-security systems**: 13-14 (~440-880ms)
- **Offline/batch processing**: 15+ (multiple seconds)

## References and Further Reading

- [BCrypt.Net-Next GitHub Repository](https://github.com/BcryptNet/bcrypt.net) - Official library source code and documentation
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) - Industry best practices for password hashing
- [Original BCrypt Paper](https://www.usenix.org/legacy/events/usenix99/provos/provos.pdf) - "A Future-Adaptable Password Scheme" by Niels Provos
- [Microsoft Identity Best Practices](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/) - ASP.NET Core authentication patterns
- [Bcrypt Calculator](https://bcrypt-generator.com/) - Online tool to test bcrypt hashing and work factors
