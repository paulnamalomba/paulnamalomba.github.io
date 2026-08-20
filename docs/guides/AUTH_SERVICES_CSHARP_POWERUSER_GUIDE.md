# AUTH_SERVICES PowerUser Guide (C#)

**Last updated**: December 05, 2025<br>
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

Enterprise authentication services provide centralized identity management, single sign-on (SSO), multi-factor authentication (MFA), and federated identity protocols (OAuth2, OIDC, SAML) for securing distributed systems at scale. This guide covers implementation patterns in C# for integrating with identity providers, token validation, claim-based authorization, SCIM provisioning, certificate-based authentication, and audit logging. Power users need to understand token lifecycle management, refresh strategies, key rotation, HSM/KeyVault integration, and high-availability architectures for production authentication infrastructure.

## Contents

- [AUTH\_SERVICES PowerUser Guide (C#)](#auth_services-poweruser-guide-c)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstarts](#quickstarts)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Example 1: OAuth 2.0 Authorization Code Flow with PKCE](#example-1-oauth-20-authorization-code-flow-with-pkce)
    - [Example 2: Custom Claims Transformation and Policy-Based Authorization](#example-2-custom-claims-transformation-and-policy-based-authorization)
    - [Example 3: SCIM 2.0 User Provisioning Implementation](#example-3-scim-20-user-provisioning-implementation)
    - [Example 4: Token Refresh and Rotation Strategy](#example-4-token-refresh-and-rotation-strategy)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstarts

1. **Install packages**: `dotnet add package Microsoft.Identity.Web` and `dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer`
2. **Configure identity provider**: Register application in Azure AD, Okta, Auth0, or Keycloak; obtain client ID, tenant ID, and client secret
3. **Add authentication middleware**: Configure `AddMicrosoftIdentityWebApi()` or `AddJwtBearer()` in `Program.cs`
4. **Protect endpoints**: Apply `[Authorize]` attribute to controllers or endpoints requiring authentication
5. **Validate tokens**: Use built-in token validation with issuer, audience, and signing key verification
6. **Extract claims**: Access `User.Claims` in controllers for user identity, roles, and permissions

## Key Concepts

- **Identity Provider (IdP)**: Centralized service that authenticates users and issues tokens (Azure AD, Okta, Auth0, Keycloak, Ping Identity)
- **OAuth 2.0**: Authorization framework enabling third-party applications to obtain limited access to resources; uses authorization code, client credentials, refresh token flows
- **OpenID Connect (OIDC)**: Identity layer on top of OAuth 2.0 providing authentication and user profile information via ID tokens
- **SAML 2.0**: XML-based protocol for exchanging authentication and authorization data between identity provider and service provider; common in legacy enterprise systems
- **JWT (JSON Web Token)**: Compact, self-contained token format for securely transmitting claims between parties; consists of header, payload, and signature
- **Claims**: Key-value pairs representing user attributes (identity, roles, permissions); included in JWT payload and accessible in application code
- **Token Lifetime**: Time period during which token is valid; access tokens typically short-lived (5-60 min), refresh tokens long-lived (days/months)
- **Refresh Token**: Long-lived credential for obtaining new access tokens without re-authentication; must be stored securely and rotated periodically
- **SCIM (System for Cross-domain Identity Management)**: RESTful protocol for automating user provisioning and de-provisioning across systems
- **Token Revocation**: Process of invalidating tokens before expiration; requires centralized token store or distributed cache for validation
- **Certificate-Based Authentication**: Uses X.509 certificates for mutual TLS authentication; common in B2B scenarios and high-security environments

## Configuration and Best Practices

```csharp
// Program.cs - ASP.NET Core minimal API with Azure AD authentication
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add authentication with Azure AD
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

// Add authorization policies
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"))
    .AddPolicy("RequireMfa", policy => policy.RequireClaim("amr", "mfa"));

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/api/secure", () => "Protected resource")
    .RequireAuthorization();

app.MapGet("/api/admin", () => "Admin only resource")
    .RequireAuthorization("AdminOnly");

app.Run();
```

```json
// appsettings.json - Azure AD configuration
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "Audience": "api://your-api-id"
  },
  "Logging": {
    "LogLevel": {
      "Microsoft.Identity": "Information"
    }
  }
}
```

**Best Practices**:

- Use managed identities or KeyVault for client secrets; never hardcode credentials
- Implement token caching to reduce IdP calls; use `IDistributedCache` with Redis
- Validate token signature, issuer, audience, and expiration on every request
- Use short-lived access tokens (15-30 min) with refresh token rotation
- Implement proper CORS policies; avoid wildcard origins in production
- Log authentication failures with correlation IDs for security auditing
- Use HTTPS only; disable insecure protocols (TLS < 1.2)
- Implement rate limiting to prevent token endpoint abuse
- Store refresh tokens encrypted in database; rotate on each use
- Use PKCE (Proof Key for Code Exchange) for public clients (SPAs, mobile)

## Security Considerations

**Token Security**:

```csharp
// Custom token validation with additional security checks
builder.Services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme, options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ClockSkew = TimeSpan.FromMinutes(2), // Reduce default 5 min skew
        RequireExpirationTime = true,
        RequireSignedTokens = true
    };

    options.Events = new JwtBearerEvents
    {
        OnTokenValidated = async context =>
        {
            // Check token revocation against distributed cache
            var tokenId = context.Principal?.FindFirst("jti")?.Value;
            var cache = context.HttpContext.RequestServices.GetRequiredService<IDistributedCache>();
            var revoked = await cache.GetStringAsync($"revoked:{tokenId}");

            if (revoked != null)
            {
                context.Fail("Token has been revoked");
            }
        },
        OnAuthenticationFailed = context =>
        {
            // Log authentication failures with security context
            var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();
            logger.LogWarning(
                "Authentication failed: {Exception} | IP: {IP} | Path: {Path}",
                context.Exception.Message,
                context.HttpContext.Connection.RemoteIpAddress,
                context.HttpContext.Request.Path
            );
            return Task.CompletedTask;
        }
    };
});
```

**Certificate-Based Authentication**:

```csharp
// Mutual TLS authentication with client certificates
builder.Services.AddAuthentication(CertificateAuthenticationDefaults.AuthenticationScheme)
    .AddCertificate(options =>
    {
        options.AllowedCertificateTypes = CertificateTypes.All;
        options.RevocationMode = X509RevocationMode.Online;
        options.ValidateCertificateUse = true;

        options.Events = new CertificateAuthenticationEvents
        {
            OnCertificateValidated = context =>
            {
                // Validate against trusted certificate store
                var validationService = context.HttpContext.RequestServices
                    .GetRequiredService<ICertificateValidationService>();

                if (!validationService.IsTrusted(context.ClientCertificate))
                {
                    context.Fail("Certificate not trusted");
                }

                // Add certificate thumbprint as claim
                var claims = new[]
                {
                    new Claim("cert_thumbprint", context.ClientCertificate.Thumbprint),
                    new Claim("cert_subject", context.ClientCertificate.Subject)
                };

                context.Principal = new ClaimsPrincipal(
                    new ClaimsIdentity(claims, context.Scheme.Name));
                context.Success();

                return Task.CompletedTask;
            }
        };
    });

// Configure Kestrel for client certificates
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(https =>
    {
        https.ClientCertificateMode = ClientCertificateMode.RequireCertificate;
        https.ClientCertificateValidation = (cert, chain, errors) =>
        {
            // Custom validation logic
            return errors == SslPolicyErrors.None;
        };
    });
});
```

**Key Security Measures**:

- Use Azure KeyVault or AWS Secrets Manager for signing keys; rotate every 90 days
- Implement key versioning with graceful rollover period (accept both old and new keys for 24 hours)
- Store private keys in HSM (Hardware Security Module) for production environments
- Use separate signing keys per environment (dev, staging, production)
- Implement token binding to prevent token replay attacks
- Use nonce values in authentication requests to prevent replay
- Implement proper session management with secure, httponly, samesite cookies
- Use content security policy (CSP) headers to prevent XSS attacks
- Implement account lockout after failed login attempts (5 attempts, 15 min lockout)
- Audit all authentication events with user context, IP, user-agent, timestamp

## Examples

### Example 1: OAuth 2.0 Authorization Code Flow with PKCE

```csharp
// OAuth2 client implementation with PKCE
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Mvc;

public class OAuth2Controller : ControllerBase
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _config;
    private readonly IDistributedCache _cache;

    public OAuth2Controller(IHttpClientFactory httpClientFactory,
        IConfiguration config, IDistributedCache cache)
    {
        _httpClientFactory = httpClientFactory;
        _config = config;
        _cache = cache;
    }

    [HttpGet("login")]
    public IActionResult Login()
    {
        // Generate PKCE code verifier and challenge
        var codeVerifier = GenerateCodeVerifier();
        var codeChallenge = GenerateCodeChallenge(codeVerifier);
        var state = Guid.NewGuid().ToString("N");

        // Store code verifier and state in cache
        _cache.SetString($"verifier:{state}", codeVerifier,
            new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10) });

        // Build authorization URL
        var authUrl = $"{_config["OAuth:AuthorizationEndpoint"]}" +
            $"?response_type=code" +
            $"&client_id={_config["OAuth:ClientId"]}" +
            $"&redirect_uri={Uri.EscapeDataString(_config["OAuth:RedirectUri"])}" +
            $"&scope={Uri.EscapeDataString("openid profile email")}" +
            $"&state={state}" +
            $"&code_challenge={codeChallenge}" +
            $"&code_challenge_method=S256";

        return Redirect(authUrl);
    }

    [HttpGet("callback")]
    public async Task<IActionResult> Callback(string code, string state)
    {
        if (string.IsNullOrEmpty(code) || string.IsNullOrEmpty(state))
            return BadRequest("Missing code or state");

        // Retrieve and validate code verifier
        var codeVerifier = await _cache.GetStringAsync($"verifier:{state}");
        if (codeVerifier == null)
            return BadRequest("Invalid state or expired session");

        // Exchange authorization code for tokens
        var client = _httpClientFactory.CreateClient();
        var tokenRequest = new HttpRequestMessage(HttpMethod.Post, _config["OAuth:TokenEndpoint"])
        {
            Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["grant_type"] = "authorization_code",
                ["code"] = code,
                ["redirect_uri"] = _config["OAuth:RedirectUri"],
                ["client_id"] = _config["OAuth:ClientId"],
                ["code_verifier"] = codeVerifier
            })
        };

        var response = await client.SendAsync(tokenRequest);
        if (!response.IsSuccessStatusCode)
            return StatusCode((int)response.StatusCode, "Token exchange failed");

        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>();

        // Store tokens securely
        await StoreTokensSecurely(tokenResponse);

        return Ok(new { message = "Authentication successful", tokenResponse.AccessToken });
    }

    private static string GenerateCodeVerifier()
    {
        var bytes = new byte[32];
        RandomNumberGenerator.Fill(bytes);
        return Convert.ToBase64String(bytes)
            .TrimEnd('=')
            .Replace('+', '-')
            .Replace('/', '_');
    }

    private static string GenerateCodeChallenge(string codeVerifier)
    {
        var bytes = SHA256.HashData(Encoding.ASCII.GetBytes(codeVerifier));
        return Convert.ToBase64String(bytes)
            .TrimEnd('=')
            .Replace('+', '-')
            .Replace('/', '_');
    }

    private async Task StoreTokensSecurely(TokenResponse tokens)
    {
        // Encrypt and store refresh token in database
        var userId = User.FindFirst("sub")?.Value;
        // Implementation: Store encrypted refresh token with user ID
        await Task.CompletedTask;
    }
}

public record TokenResponse(
    string AccessToken,
    string RefreshToken,
    int ExpiresIn,
    string TokenType,
    string IdToken
);
```

### Example 2: Custom Claims Transformation and Policy-Based Authorization

```csharp
// Claims transformation service
using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;

public class CustomClaimsTransformer : IClaimsTransformation
{
    private readonly IUserRoleService _roleService;

    public CustomClaimsTransformer(IUserRoleService roleService)
    {
        _roleService = roleService;
    }

    public async Task<ClaimsPrincipal> TransformAsync(ClaimsPrincipal principal)
    {
        // Clone current identity
        var claimsIdentity = new ClaimsIdentity();
        claimsIdentity.AddClaims(principal.Claims);

        // Get user ID from existing claims
        var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userId == null) return principal;

        // Load roles from database and add as claims
        var roles = await _roleService.GetUserRolesAsync(userId);
        foreach (var role in roles)
        {
            claimsIdentity.AddClaim(new Claim(ClaimTypes.Role, role));
        }

        // Add custom claims from business logic
        var permissions = await _roleService.GetUserPermissionsAsync(userId);
        foreach (var permission in permissions)
        {
            claimsIdentity.AddClaim(new Claim("permission", permission));
        }

        return new ClaimsPrincipal(claimsIdentity);
    }
}

// Register claims transformation
builder.Services.AddTransient<IClaimsTransformation, CustomClaimsTransformer>();

// Custom authorization requirement
using Microsoft.AspNetCore.Authorization;

public class PermissionRequirement : IAuthorizationRequirement
{
    public string Permission { get; }

    public PermissionRequirement(string permission)
    {
        Permission = permission;
    }
}

public class PermissionAuthorizationHandler : AuthorizationHandler<PermissionRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        PermissionRequirement requirement)
    {
        if (context.User.HasClaim("permission", requirement.Permission))
        {
            context.Succeed(requirement);
        }

        return Task.CompletedTask;
    }
}

// Register authorization policies
builder.Services.AddSingleton<IAuthorizationHandler, PermissionAuthorizationHandler>();
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("CanCreateUsers", policy =>
        policy.Requirements.Add(new PermissionRequirement("users.create")))
    .AddPolicy("CanDeleteUsers", policy =>
        policy.Requirements.Add(new PermissionRequirement("users.delete")));

// Use in controllers
[Authorize(Policy = "CanCreateUsers")]
[HttpPost("users")]
public async Task<IActionResult> CreateUser([FromBody] UserDto user)
{
    // Implementation
    return Ok();
}
```

### Example 3: SCIM 2.0 User Provisioning Implementation

```csharp
// SCIM user provisioning controller
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("scim/v2")]
[Authorize(Roles = "SCIMClient")]
public class ScimUsersController : ControllerBase
{
    private readonly IUserProvisioningService _provisioningService;

    public ScimUsersController(IUserProvisioningService provisioningService)
    {
        _provisioningService = provisioningService;
    }

    [HttpGet("Users")]
    public async Task<IActionResult> GetUsers(
        [FromQuery] string filter,
        [FromQuery] int startIndex = 1,
        [FromQuery] int count = 100)
    {
        var users = await _provisioningService.GetUsersAsync(filter, startIndex, count);

        return Ok(new
        {
            schemas = new[] { "urn:ietf:params:scim:api:messages:2.0:ListResponse" },
            totalResults = users.TotalCount,
            startIndex,
            itemsPerPage = count,
            Resources = users.Items
        });
    }

    [HttpGet("Users/{id}")]
    public async Task<IActionResult> GetUser(string id)
    {
        var user = await _provisioningService.GetUserByIdAsync(id);
        if (user == null) return NotFound();

        return Ok(user);
    }

    [HttpPost("Users")]
    public async Task<IActionResult> CreateUser([FromBody] ScimUser user)
    {
        var created = await _provisioningService.CreateUserAsync(user);
        return CreatedAtAction(nameof(GetUser), new { id = created.Id }, created);
    }

    [HttpPut("Users/{id}")]
    public async Task<IActionResult> UpdateUser(string id, [FromBody] ScimUser user)
    {
        var updated = await _provisioningService.UpdateUserAsync(id, user);
        if (updated == null) return NotFound();

        return Ok(updated);
    }

    [HttpPatch("Users/{id}")]
    public async Task<IActionResult> PatchUser(string id, [FromBody] ScimPatchRequest patch)
    {
        var updated = await _provisioningService.PatchUserAsync(id, patch);
        if (updated == null) return NotFound();

        return Ok(updated);
    }

    [HttpDelete("Users/{id}")]
    public async Task<IActionResult> DeleteUser(string id)
    {
        var result = await _provisioningService.DeleteUserAsync(id);
        if (!result) return NotFound();

        return NoContent();
    }
}

public record ScimUser(
    string Id,
    string UserName,
    ScimName Name,
    string[] Emails,
    bool Active,
    ScimMeta Meta
);

public record ScimName(string GivenName, string FamilyName);
public record ScimMeta(string ResourceType, DateTime Created, DateTime LastModified);

public record ScimPatchRequest(
    string[] Schemas,
    ScimPatchOperation[] Operations
);

public record ScimPatchOperation(string Op, string Path, object Value);
```

### Example 4: Token Refresh and Rotation Strategy

```csharp
// Token refresh service with rotation
public class TokenRefreshService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _config;
    private readonly ITokenStore _tokenStore;
    private readonly ILogger<TokenRefreshService> _logger;

    public TokenRefreshService(
        IHttpClientFactory httpClientFactory,
        IConfiguration config,
        ITokenStore tokenStore,
        ILogger<TokenRefreshService> logger)
    {
        _httpClientFactory = httpClientFactory;
        _config = config;
        _tokenStore = tokenStore;
        _logger = logger;
    }

    public async Task<TokenResponse> RefreshAccessTokenAsync(string userId)
    {
        // Retrieve stored refresh token
        var refreshToken = await _tokenStore.GetRefreshTokenAsync(userId);
        if (refreshToken == null)
            throw new InvalidOperationException("No refresh token found");

        // Check if token is still valid
        if (refreshToken.ExpiresAt < DateTime.UtcNow)
            throw new InvalidOperationException("Refresh token expired");

        // Exchange refresh token for new access token
        var client = _httpClientFactory.CreateClient();
        var request = new HttpRequestMessage(HttpMethod.Post, _config["OAuth:TokenEndpoint"])
        {
            Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["grant_type"] = "refresh_token",
                ["refresh_token"] = refreshToken.Token,
                ["client_id"] = _config["OAuth:ClientId"],
                ["client_secret"] = _config["OAuth:ClientSecret"]
            })
        };

        var response = await client.SendAsync(request);
        if (!response.IsSuccessStatusCode)
        {
            _logger.LogError("Token refresh failed for user {UserId}: {StatusCode}",
                userId, response.StatusCode);

            // If refresh token is invalid, revoke and force re-authentication
            await _tokenStore.RevokeRefreshTokenAsync(userId);
            throw new InvalidOperationException("Token refresh failed");
        }

        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>();

        // Rotate refresh token (store new one, invalidate old one)
        if (!string.IsNullOrEmpty(tokenResponse.RefreshToken))
        {
            await _tokenStore.StoreRefreshTokenAsync(userId, new RefreshTokenData
            {
                Token = tokenResponse.RefreshToken,
                ExpiresAt = DateTime.UtcNow.AddSeconds(tokenResponse.ExpiresIn),
                IssuedAt = DateTime.UtcNow
            });
        }

        _logger.LogInformation("Token refreshed successfully for user {UserId}", userId);

        return tokenResponse;
    }

    public async Task RevokeTokenAsync(string userId, string token)
    {
        // Revoke token at identity provider
        var client = _httpClientFactory.CreateClient();
        var request = new HttpRequestMessage(HttpMethod.Post, _config["OAuth:RevocationEndpoint"])
        {
            Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["token"] = token,
                ["token_type_hint"] = "refresh_token",
                ["client_id"] = _config["OAuth:ClientId"],
                ["client_secret"] = _config["OAuth:ClientSecret"]
            })
        };

        await client.SendAsync(request);

        // Remove from local store
        await _tokenStore.RevokeRefreshTokenAsync(userId);

        _logger.LogInformation("Token revoked for user {UserId}", userId);
    }
}

public interface ITokenStore
{
    Task<RefreshTokenData?> GetRefreshTokenAsync(string userId);
    Task StoreRefreshTokenAsync(string userId, RefreshTokenData token);
    Task RevokeRefreshTokenAsync(string userId);
}

public record RefreshTokenData
{
    public string Token { get; init; }
    public DateTime ExpiresAt { get; init; }
    public DateTime IssuedAt { get; init; }
}
```

## Troubleshooting

**Token Validation Failures**:

```csharp
// Enhanced logging for token validation issues
builder.Services.Configure<JwtBearerOptions>(JwtBearerDefaults.AuthenticationScheme, options =>
{
    options.Events = new JwtBearerEvents
    {
        OnAuthenticationFailed = context =>
        {
            var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();

            // Log detailed token validation errors
            if (context.Exception is SecurityTokenExpiredException)
            {
                logger.LogWarning("Token expired: {Message}", context.Exception.Message);
                context.Response.Headers.Add("X-Token-Expired", "true");
            }
            else if (context.Exception is SecurityTokenInvalidSignatureException)
            {
                logger.LogError("Invalid token signature: {Message}", context.Exception.Message);
            }
            else if (context.Exception is SecurityTokenInvalidIssuerException)
            {
                logger.LogError("Invalid issuer: {Message}", context.Exception.Message);
            }
            else if (context.Exception is SecurityTokenInvalidAudienceException)
            {
                logger.LogError("Invalid audience: {Message}", context.Exception.Message);
            }
            else
            {
                logger.LogError(context.Exception, "Authentication failed");
            }

            return Task.CompletedTask;
        },
        OnMessageReceived = context =>
        {
            var logger = context.HttpContext.RequestServices.GetRequiredService<ILogger<Program>>();
            logger.LogDebug("Token received from {Source}",
                context.Request.Headers.Authorization.FirstOrDefault()?.Substring(0, 20) ?? "none");
            return Task.CompletedTask;
        }
    };
});
```

**Common Issues**:

- **401 Unauthorized**: Check token expiration, signature validation, issuer/audience mismatch
- **403 Forbidden**: User lacks required claims/roles; verify claims transformation pipeline
- **Token refresh loop**: Ensure refresh token rotation logic doesn't create circular dependencies
- **CORS errors**: Configure proper CORS policy with credentials support for cross-origin requests
- **Clock skew**: Adjust `ClockSkew` parameter in token validation; default 5 minutes may be too large
- **Missing claims**: Ensure IdP is configured to include required claims in tokens; check scope mappings
- **Certificate validation failures**: Verify certificate chain, CRL/OCSP endpoints, and trust store configuration

**Diagnostic Commands**:

```bash
# Decode JWT token (use jwt.io or jwt-cli)
dotnet tool install --global jwt-cli
jwt decode <token>

# Test token validation
curl -H "Authorization: Bearer <token>" https://api.example.com/validate

# Check certificate validity
openssl x509 -in certificate.pem -text -noout
openssl verify -CAfile ca-bundle.pem certificate.pem
```

## Performance and Tuning

**Token Caching Strategy**:

```csharp
// Implement distributed token cache with Redis
public class RedisTokenCache
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<RedisTokenCache> _logger;

    public RedisTokenCache(IDistributedCache cache, ILogger<RedisTokenCache> logger)
    {
        _cache = cache;
        _logger = logger;
    }

    public async Task<string?> GetAccessTokenAsync(string userId)
    {
        var cacheKey = $"access_token:{userId}";
        var token = await _cache.GetStringAsync(cacheKey);

        if (token != null)
        {
            _logger.LogDebug("Cache hit for user {UserId}", userId);
        }

        return token;
    }

    public async Task SetAccessTokenAsync(string userId, string token, int expiresIn)
    {
        var cacheKey = $"access_token:{userId}";
        var options = new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = TimeSpan.FromSeconds(expiresIn - 60) // 60s buffer
        };

        await _cache.SetStringAsync(cacheKey, token, options);
        _logger.LogDebug("Cached token for user {UserId} with expiry {ExpiresIn}s", userId, expiresIn);
    }
}

// Use in application
public class SecureApiClient
{
    private readonly HttpClient _httpClient;
    private readonly RedisTokenCache _tokenCache;
    private readonly ITokenService _tokenService;

    public async Task<string> GetAccessTokenAsync(string userId)
    {
        // Try cache first
        var cachedToken = await _tokenCache.GetAccessTokenAsync(userId);
        if (cachedToken != null)
            return cachedToken;

        // Fetch new token and cache
        var tokenResponse = await _tokenService.GetTokenAsync(userId);
        await _tokenCache.SetAccessTokenAsync(userId, tokenResponse.AccessToken, tokenResponse.ExpiresIn);

        return tokenResponse.AccessToken;
    }
}
```

**Performance Optimizations**:

- Cache validated tokens in memory for duration of their lifetime; use `MemoryCache` for single-instance apps
- Use Redis or another distributed cache for multi-instance deployments to share token validation cache
- Implement connection pooling for HTTP clients calling IdP endpoints; use `IHttpClientFactory`
- Enable response compression for token endpoints returning large ID tokens
- Use async/await throughout authentication pipeline to prevent thread pool starvation
- Implement circuit breaker pattern for IdP calls to handle temporary outages gracefully
- Pre-fetch signing keys from JWKS endpoint on startup and cache with background refresh
- Use bulk operations for SCIM provisioning instead of individual API calls
- Implement pagination for large user/group queries (max 100-200 items per page)
- Monitor authentication latency and set alerts for p95 > 500ms

**Monitoring Metrics**:

```csharp
// Custom metrics for authentication monitoring
using System.Diagnostics.Metrics;

public class AuthenticationMetrics
{
    private readonly Meter _meter;
    private readonly Counter<long> _authSuccessCounter;
    private readonly Counter<long> _authFailureCounter;
    private readonly Histogram<double> _tokenValidationDuration;
    private readonly Histogram<double> _tokenRefreshDuration;

    public AuthenticationMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("Authentication");
        _authSuccessCounter = _meter.CreateCounter<long>("auth.success", "count");
        _authFailureCounter = _meter.CreateCounter<long>("auth.failure", "count");
        _tokenValidationDuration = _meter.CreateHistogram<double>("auth.validation.duration", "ms");
        _tokenRefreshDuration = _meter.CreateHistogram<double>("auth.refresh.duration", "ms");
    }

    public void RecordAuthSuccess(string provider)
        => _authSuccessCounter.Add(1, new KeyValuePair<string, object?>("provider", provider));

    public void RecordAuthFailure(string provider, string reason)
        => _authFailureCounter.Add(1,
            new KeyValuePair<string, object?>("provider", provider),
            new KeyValuePair<string, object?>("reason", reason));

    public void RecordTokenValidation(double milliseconds)
        => _tokenValidationDuration.Record(milliseconds);

    public void RecordTokenRefresh(double milliseconds)
        => _tokenRefreshDuration.Record(milliseconds);
}
```

**Scaling Considerations**:

- Deploy multiple instances behind load balancer with sticky sessions if using in-memory cache
- Use Redis Cluster for distributed cache in high-throughput scenarios (>10K req/s)
- Implement rate limiting per user/IP to prevent abuse (use AspNetCoreRateLimit library)
- Consider dedicated authentication service/sidecar pattern for microservices architecture
- Use connection multiplexing for HTTP/2 to IdP endpoints
- Implement background token refresh for long-running processes to avoid synchronous delays
- Monitor IdP rate limits and implement backoff/retry strategies

## References and Further Reading

**Official Documentation**:

- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [SAML 2.0 Technical Overview](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [SCIM 2.0 RFC 7643](https://datatracker.ietf.org/doc/html/rfc7643)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)

**Libraries and Tools**:

- [Microsoft.Identity.Web](https://github.com/AzureAD/microsoft-identity-web) - Azure AD integration
- [IdentityServer](https://duendesoftware.com/products/identityserver) - .NET OAuth/OIDC server
- [Auth0 .NET SDK](https://github.com/auth0/auth0.net) - Auth0 integration
- [Okta .NET SDK](https://github.com/okta/okta-sdk-dotnet) - Okta integration
- [JWT.NET](https://github.com/jwt-dotnet/jwt) - JWT encoding/decoding
- [BouncyCastle](https://www.bouncycastle.org/csharp/) - Cryptography library

**Best Practices Guides**:

- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
- [Microsoft Identity Platform Best Practices](https://learn.microsoft.com/en-us/azure/active-directory/develop/identity-platform-integration-checklist)

**Community Resources**:

- [Auth0 Blog - Identity & Security](https://auth0.com/blog/)
- [Identity Server Documentation](https://docs.duendesoftware.com/)
- [.NET Security on GitHub](https://github.com/dotnet/aspnetcore/tree/main/src/Security)
