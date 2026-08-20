# AUTH_SERVICES PowerUser Guide (PowerShell)

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

Enterprise authentication services provide centralized identity management, single sign-on (SSO), multi-factor authentication (MFA), and federated identity protocols for securing distributed systems at scale. This guide covers operational tasks using PowerShell 7+ on Windows for managing Azure AD, Active Directory Federation Services (AD FS), certificate authorities, token lifecycle automation, user provisioning via Microsoft Graph API, and security auditing. Power users need to understand certificate management, service principal automation, conditional access policies, and high-availability monitoring for production authentication infrastructure.

## Contents

- [AUTH\_SERVICES PowerUser Guide (PowerShell)](#auth_services-poweruser-guide-powershell)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Example 1: Automated User Provisioning with Microsoft Graph API](#example-1-automated-user-provisioning-with-microsoft-graph-api)
    - [Example 2: Service Principal Creation and Permission Management](#example-2-service-principal-creation-and-permission-management)
    - [Example 3: Certificate Management and Rotation](#example-3-certificate-management-and-rotation)
    - [Example 4: Group-Based License Assignment Automation](#example-4-group-based-license-assignment-automation)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install modules**: `Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force`
2. **Connect to Azure AD**: `Connect-MgGraph -Scopes "User.Read.All","Application.Read.All"`
3. **List users**: `Get-MgUser -Top 10 | Select-Object DisplayName, UserPrincipalName`
4. **Create service principal**: `New-MgServicePrincipal -AppId <app-id> -DisplayName "MyApp"`
5. **Generate certificate**: `New-SelfSignedCertificate -Subject "CN=MyAppCert" -CertStoreLocation Cert:\CurrentUser\My`
6. **Export certificate**: `Export-Certificate -Cert $cert -FilePath .\cert.cer`

## Key Concepts

- **Azure Active Directory (Azure AD)**: Cloud-based identity and access management service providing authentication, authorization, and SSO for Microsoft 365 and Azure resources
- **Service Principal**: Identity for applications and services in Azure AD; used for authentication and authorization in automated workflows
- **Managed Identity**: Azure-managed service principal that eliminates need for credential management; assigned to Azure resources for accessing other resources
- **Conditional Access**: Policy-based access control evaluating signals (user, location, device, risk) to enforce MFA, block access, or require compliant devices
- **Certificate-Based Authentication**: Uses X.509 certificates instead of passwords for authentication; common for service accounts and federated scenarios
- **Microsoft Graph API**: RESTful API for accessing Azure AD, Microsoft 365, and other Microsoft cloud services; supports user/group management, mail, calendar, and more
- **App Registration**: Process of registering applications in Azure AD to enable authentication and authorization; generates client ID and allows configuring permissions
- **OAuth 2.0 Flows**: Authorization code (web apps), client credentials (daemon apps), on-behalf-of (middle-tier services), device code (input-constrained devices)
- **Token Lifetime**: Configurable duration for access tokens (default 1 hour) and refresh tokens (default 90 days); can be customized per application or tenant-wide
- **Emergency Access Accounts**: Break-glass accounts with highest privileges, excluded from conditional access policies, used only in emergencies

## Configuration and Best Practices

```powershell
# Install and import Microsoft Graph PowerShell SDK
Install-Module Microsoft.Graph -Scope CurrentUser -AllowClobber -Force
Import-Module Microsoft.Graph.Authentication
Import-Module Microsoft.Graph.Users
Import-Module Microsoft.Graph.Applications

# Connect with delegated permissions (interactive)
Connect-MgGraph -Scopes "User.ReadWrite.All","Application.ReadWrite.All","Directory.ReadWrite.All"

# Connect with application permissions (service principal)
$clientId = $env:AZURE_CLIENT_ID
$tenantId = $env:AZURE_TENANT_ID
$clientSecret = $env:AZURE_CLIENT_SECRET | ConvertTo-SecureString -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($clientId, $clientSecret)

Connect-MgGraph -ClientSecretCredential $credential -TenantId $tenantId

# Verify connection
Get-MgContext | Select-Object Scopes, Account, TenantId
```

**Best Practices**:

- Use managed identities for Azure resources instead of storing credentials
- Store client secrets in Azure Key Vault; retrieve via PowerShell with `Get-AzKeyVaultSecret`
- Use certificate-based authentication for service principals in production (more secure than secrets)
- Implement least privilege principle; grant only required Graph API permissions
- Enable MFA for all admin accounts; exclude only emergency access accounts
- Set conditional access policies to require compliant devices for sensitive operations
- Implement automated certificate rotation before expiration (90 days notice)
- Use separate service principals per application/environment (dev, staging, production)
- Enable audit logging for all authentication events; export logs to SIEM/Log Analytics
- Implement monitoring and alerts for failed sign-ins, suspicious activities, and certificate expiration

## Security Considerations

**Certificate-Based Service Principal Authentication**:

```powershell
# Generate self-signed certificate for service principal (development only)
$cert = New-SelfSignedCertificate `
    -Subject "CN=MyApp-ServicePrincipal" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeySpec Signature `
    -KeyLength 2048 `
    -KeyAlgorithm RSA `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddMonths(12)

# Export certificate (public key only)
$certPath = ".\MyApp-ServicePrincipal.cer"
Export-Certificate -Cert $cert -FilePath $certPath

# Upload certificate to app registration
$appId = "your-app-id"
$certBytes = [System.IO.File]::ReadAllBytes($certPath)
$certBase64 = [System.Convert]::ToBase64String($certBytes)

Update-MgApplication -ApplicationId $appId -KeyCredentials @{
    Type = "AsymmetricX509Cert"
    Usage = "Verify"
    Key = $certBase64
}

# Connect using certificate authentication
$tenantId = "your-tenant-id"
Connect-MgGraph -ClientId $appId -TenantId $tenantId -CertificateThumbprint $cert.Thumbprint

# Production: Use Azure Key Vault for certificate storage
# Import certificate from Key Vault
$keyVaultName = "your-keyvault"
$certName = "MyAppCert"
$kvCert = Get-AzKeyVaultCertificate -VaultName $keyVaultName -Name $certName

# Retrieve certificate from local store (imported from Key Vault)
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.Thumbprint -eq $kvCert.Thumbprint }
Connect-MgGraph -ClientId $appId -TenantId $tenantId -Certificate $cert
```

**Conditional Access Policy Automation**:

```powershell
# Create conditional access policy requiring MFA for admin roles
$policy = @{
    DisplayName = "Require MFA for Admins"
    State = "enabled"
    Conditions = @{
        Users = @{
            IncludeRoles = @(
                "62e90394-69f5-4237-9190-012177145e10"  # Global Administrator
                "194ae4cb-b126-40b2-bd5b-6091b380977d"  # Security Administrator
            )
            ExcludeUsers = @("emergency-access-account@domain.com")
        }
        Applications = @{
            IncludeApplications = @("All")
        }
        ClientAppTypes = @("browser", "mobileAppsAndDesktopClients")
    }
    GrantControls = @{
        Operator = "OR"
        BuiltInControls = @("mfa")
    }
}

New-MgIdentityConditionalAccessPolicy -BodyParameter $policy

# List all conditional access policies
Get-MgIdentityConditionalAccessPolicy | Select-Object DisplayName, State, CreatedDateTime
```

**Security Monitoring and Audit Logs**:

```powershell
# Query sign-in logs for failed authentication attempts
$startDate = (Get-Date).AddDays(-7)
$endDate = Get-Date

$failedSignIns = Get-MgAuditLogSignIn `
    -Filter "status/errorCode ne 0 and createdDateTime ge $($startDate.ToString('yyyy-MM-dd'))" `
    -Top 100 |
    Select-Object CreatedDateTime, UserPrincipalName, AppDisplayName,
                  @{N='ErrorCode';E={$_.Status.ErrorCode}},
                  @{N='FailureReason';E={$_.Status.FailureReason}},
                  IpAddress, Location

$failedSignIns | Format-Table -AutoSize

# Export to CSV for analysis
$failedSignIns | Export-Csv -Path ".\failed-signins.csv" -NoTypeInformation

# Query directory audit logs for privileged operations
$auditLogs = Get-MgAuditLogDirectoryAudit `
    -Filter "activityDisplayName eq 'Add member to role' and activityDateTime ge $($startDate.ToString('yyyy-MM-dd'))" `
    -Top 50 |
    Select-Object ActivityDateTime, ActivityDisplayName,
                  @{N='InitiatedBy';E={$_.InitiatedBy.User.UserPrincipalName}},
                  @{N='TargetUser';E={$_.TargetResources[0].UserPrincipalName}},
                  @{N='Result';E={$_.Result}}

$auditLogs | Format-Table -AutoSize
```

**Key Security Measures**:

- Rotate service principal secrets/certificates every 90 days; automate with Azure Automation
- Use Azure Key Vault for storing and managing certificates, secrets, and keys
- Enable Azure AD Identity Protection for risk-based conditional access policies
- Implement just-in-time admin access with Privileged Identity Management (PIM)
- Configure Azure AD Connect Health for monitoring on-premises AD FS infrastructure
- Enable security defaults for new tenants (enforces MFA, blocks legacy authentication)
- Implement named locations for trusted IP ranges to reduce MFA prompts
- Use application consent policies to prevent users from granting excessive permissions
- Enable continuous access evaluation (CAE) for real-time token revocation
- Configure token lifetime policies to balance security (shorter) and usability (longer)

## Examples

### Example 1: Automated User Provisioning with Microsoft Graph API

```powershell
# Function to create bulk users from CSV
function New-BulkUsers {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CsvPath,

        [Parameter(Mandatory=$false)]
        [string]$DefaultPassword = "ChangeMe@123!",

        [Parameter(Mandatory=$false)]
        [string]$UsageLocation = "US"
    )

    # Import users from CSV (columns: FirstName, LastName, Email, Department)
    $users = Import-Csv -Path $CsvPath
    $results = @()

    foreach ($user in $users) {
        try {
            $passwordProfile = @{
                ForceChangePasswordNextSignIn = $true
                Password = $DefaultPassword
            }

            $newUser = @{
                AccountEnabled = $true
                DisplayName = "$($user.FirstName) $($user.LastName)"
                GivenName = $user.FirstName
                Surname = $user.LastName
                UserPrincipalName = $user.Email
                MailNickname = $user.Email.Split('@')[0]
                PasswordProfile = $passwordProfile
                UsageLocation = $UsageLocation
                Department = $user.Department
            }

            $createdUser = New-MgUser -BodyParameter $newUser

            Write-Host "✓ Created user: $($createdUser.UserPrincipalName)" -ForegroundColor Green

            $results += [PSCustomObject]@{
                Email = $createdUser.UserPrincipalName
                DisplayName = $createdUser.DisplayName
                UserId = $createdUser.Id
                Status = "Success"
                Message = "User created successfully"
            }
        }
        catch {
            Write-Host "✗ Failed to create user: $($user.Email) - $($_.Exception.Message)" -ForegroundColor Red

            $results += [PSCustomObject]@{
                Email = $user.Email
                DisplayName = "$($user.FirstName) $($user.LastName)"
                UserId = $null
                Status = "Failed"
                Message = $_.Exception.Message
            }
        }
    }

    # Export results
    $results | Export-Csv -Path ".\user-creation-results.csv" -NoTypeInformation

    # Summary
    $successCount = ($results | Where-Object { $_.Status -eq "Success" }).Count
    $failCount = ($results | Where-Object { $_.Status -eq "Failed" }).Count

    Write-Host "`nSummary: $successCount succeeded, $failCount failed" -ForegroundColor Cyan
    Write-Host "Results exported to: user-creation-results.csv" -ForegroundColor Cyan
}

# Usage
Connect-MgGraph -Scopes "User.ReadWrite.All"
New-BulkUsers -CsvPath ".\users.csv"
```

### Example 2: Service Principal Creation and Permission Management

```powershell
# Function to create service principal with Graph API permissions
function New-ServicePrincipalWithPermissions {
    param(
        [Parameter(Mandatory=$true)]
        [string]$DisplayName,

        [Parameter(Mandatory=$true)]
        [string[]]$Permissions  # e.g., "User.Read.All", "Mail.Send"
    )

    # Get Microsoft Graph service principal
    $graphSp = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"

    # Create app registration
    $app = New-MgApplication -DisplayName $DisplayName
    Write-Host "✓ Created app registration: $($app.DisplayName) (AppId: $($app.AppId))" -ForegroundColor Green

    # Create service principal
    $sp = New-MgServicePrincipal -AppId $app.AppId -DisplayName $DisplayName
    Write-Host "✓ Created service principal: $($sp.DisplayName)" -ForegroundColor Green

    # Map permission names to IDs
    $requiredResourceAccess = @()

    foreach ($permission in $Permissions) {
        $graphPermission = $graphSp.AppRoles | Where-Object { $_.Value -eq $permission }

        if ($graphPermission) {
            $requiredResourceAccess += @{
                Id = $graphPermission.Id
                Type = "Role"
            }
            Write-Host "✓ Added permission: $permission" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Permission not found: $permission" -ForegroundColor Yellow
        }
    }

    # Update app with required permissions
    Update-MgApplication -ApplicationId $app.Id -RequiredResourceAccess @{
        ResourceAppId = $graphSp.AppId
        ResourceAccess = $requiredResourceAccess
    }

    # Generate client secret (valid for 1 year)
    $secretName = "Auto-generated-secret"
    $secretEnd = (Get-Date).AddYears(1)

    $passwordCred = Add-MgApplicationPassword -ApplicationId $app.Id -PasswordCredential @{
        DisplayName = $secretName
        EndDateTime = $secretEnd
    }

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Service Principal Details:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Display Name: $($app.DisplayName)"
    Write-Host "Application ID: $($app.AppId)"
    Write-Host "Object ID: $($app.Id)"
    Write-Host "Service Principal ID: $($sp.Id)"
    Write-Host "Client Secret: $($passwordCred.SecretText)" -ForegroundColor Yellow
    Write-Host "Secret Expires: $($secretEnd.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "⚠️  Save the client secret now! It won't be shown again." -ForegroundColor Yellow
    Write-Host "`n⚠️  Admin consent required! Grant permissions in Azure Portal:" -ForegroundColor Yellow
    Write-Host "https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/$($app.AppId)" -ForegroundColor Cyan

    return @{
        AppId = $app.AppId
        ObjectId = $app.Id
        ServicePrincipalId = $sp.Id
        ClientSecret = $passwordCred.SecretText
        SecretExpiry = $secretEnd
    }
}

# Usage
Connect-MgGraph -Scopes "Application.ReadWrite.All"
$sp = New-ServicePrincipalWithPermissions `
    -DisplayName "MyAutomation-ServicePrincipal" `
    -Permissions @("User.Read.All", "Mail.Send", "Group.Read.All")

# Store credentials in environment variables or Key Vault
$env:AZURE_CLIENT_ID = $sp.AppId
$env:AZURE_CLIENT_SECRET = $sp.ClientSecret
```

### Example 3: Certificate Management and Rotation

```powershell
# Function to monitor and rotate expiring certificates
function Update-ExpiringCertificates {
    param(
        [Parameter(Mandatory=$false)]
        [int]$DaysBeforeExpiry = 30,

        [Parameter(Mandatory=$false)]
        [string]$KeyVaultName,

        [Parameter(Mandatory=$false)]
        [switch]$AutoRotate
    )

    # Get all app registrations
    $apps = Get-MgApplication -All
    $expiringCerts = @()

    foreach ($app in $apps) {
        if ($app.KeyCredentials.Count -eq 0) { continue }

        foreach ($cert in $app.KeyCredentials) {
            $daysUntilExpiry = ($cert.EndDateTime - (Get-Date)).Days

            if ($daysUntilExpiry -le $DaysBeforeExpiry) {
                $expiringCerts += [PSCustomObject]@{
                    AppName = $app.DisplayName
                    AppId = $app.AppId
                    ApplicationObjectId = $app.Id
                    CertThumbprint = $cert.CustomKeyIdentifier
                    ExpiryDate = $cert.EndDateTime
                    DaysRemaining = $daysUntilExpiry
                    Status = if ($daysUntilExpiry -le 0) { "EXPIRED" } else { "EXPIRING" }
                }
            }
        }
    }

    if ($expiringCerts.Count -eq 0) {
        Write-Host "✓ No expiring certificates found" -ForegroundColor Green
        return
    }

    # Display expiring certificates
    Write-Host "`nExpiring Certificates:" -ForegroundColor Yellow
    $expiringCerts | Format-Table -AutoSize

    # Auto-rotate if enabled
    if ($AutoRotate -and $KeyVaultName) {
        Write-Host "`n🔄 Auto-rotating certificates..." -ForegroundColor Cyan

        foreach ($item in $expiringCerts) {
            try {
                # Generate new certificate in Key Vault
                $certName = "$($item.AppName -replace '[^a-zA-Z0-9-]','')-$(Get-Date -Format 'yyyyMMdd')"

                $policy = New-AzKeyVaultCertificatePolicy `
                    -SubjectName "CN=$($item.AppName)" `
                    -ValidityInMonths 12 `
                    -ReuseKeyOnRenewal `
                    -KeyType RSA `
                    -KeySize 2048

                $newCert = Add-AzKeyVaultCertificate `
                    -VaultName $KeyVaultName `
                    -Name $certName `
                    -CertificatePolicy $policy

                # Wait for certificate creation
                do {
                    Start-Sleep -Seconds 5
                    $certStatus = Get-AzKeyVaultCertificateOperation -VaultName $KeyVaultName -Name $certName
                } while ($certStatus.Status -eq "inProgress")

                # Get certificate and upload to app registration
                $kvCert = Get-AzKeyVaultCertificate -VaultName $KeyVaultName -Name $certName
                $certBytes = [System.Convert]::FromBase64String($kvCert.Certificate)
                $certBase64 = [System.Convert]::ToBase64String($certBytes)

                Update-MgApplication -ApplicationId $item.ApplicationObjectId -KeyCredentials @{
                    Type = "AsymmetricX509Cert"
                    Usage = "Verify"
                    Key = $certBase64
                }

                Write-Host "✓ Rotated certificate for: $($item.AppName)" -ForegroundColor Green
            }
            catch {
                Write-Host "✗ Failed to rotate certificate for: $($item.AppName) - $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }

    # Export report
    $expiringCerts | Export-Csv -Path ".\expiring-certificates-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
}

# Usage - Check for certificates expiring in next 60 days
Connect-MgGraph -Scopes "Application.Read.All"
Connect-AzAccount
Update-ExpiringCertificates -DaysBeforeExpiry 60

# Auto-rotate expiring certificates using Key Vault
Update-ExpiringCertificates -DaysBeforeExpiry 30 -KeyVaultName "my-keyvault" -AutoRotate
```

### Example 4: Group-Based License Assignment Automation

```powershell
# Function to assign licenses based on group membership
function Set-GroupBasedLicensing {
    param(
        [Parameter(Mandatory=$true)]
        [string]$GroupId,

        [Parameter(Mandatory=$true)]
        [string]$SkuId,  # e.g., "c42b9cae-ea4f-4ab7-9717-81576235ccac" for Office 365 E3

        [Parameter(Mandatory=$false)]
        [string[]]$DisabledPlans = @()
    )

    # Prepare license configuration
    $disabledPlansArray = @()
    foreach ($plan in $DisabledPlans) {
        $disabledPlansArray += $plan
    }

    $licenseOptions = @{
        SkuId = $SkuId
        DisabledPlans = $disabledPlansArray
    }

    # Assign license to group
    Update-MgGroup -GroupId $GroupId -AssignedLicenses @{
        AddLicenses = @($licenseOptions)
        RemoveLicenses = @()
    }

    Write-Host "✓ License assigned to group: $GroupId" -ForegroundColor Green

    # Monitor processing status
    Write-Host "`n🔄 Monitoring license assignment..." -ForegroundColor Cyan

    $members = Get-MgGroupMember -GroupId $GroupId -All
    $totalMembers = $members.Count
    $processedCount = 0

    foreach ($member in $members) {
        $user = Get-MgUser -UserId $member.Id -Property "DisplayName,UserPrincipalName,AssignedLicenses,LicenseAssignmentStates"

        $licenseState = $user.LicenseAssignmentStates | Where-Object {
            $_.SkuId -eq $SkuId -and $_.AssignedByGroup -eq $GroupId
        }

        if ($licenseState) {
            $processedCount++
            $status = switch ($licenseState.State) {
                "Active" { "✓ Assigned" }
                "ActiveWithError" { "✗ Error" }
                default { "⏳ Processing" }
            }

            Write-Host "$status - $($user.DisplayName) ($($user.UserPrincipalName))"
        }
    }

    Write-Host "`nLicense assignment complete: $processedCount / $totalMembers users processed" -ForegroundColor Cyan
}

# Get available licenses in tenant
function Get-TenantLicenses {
    $subscribedSkus = Get-MgSubscribedSku

    $licenses = $subscribedSkus | Select-Object `
        @{N='LicenseName';E={$_.SkuPartNumber}},
        SkuId,
        @{N='TotalLicenses';E={$_.PrepaidUnits.Enabled}},
        ConsumedUnits,
        @{N='AvailableLicenses';E={$_.PrepaidUnits.Enabled - $_.ConsumedUnits}}

    $licenses | Format-Table -AutoSize
    return $licenses
}

# Usage
Connect-MgGraph -Scopes "Group.ReadWrite.All","User.Read.All","Organization.Read.All"

# List available licenses
Get-TenantLicenses

# Assign Office 365 E3 to a group (disable Exchange Online and SharePoint)
$groupId = "your-group-object-id"
$e3SkuId = "c42b9cae-ea4f-4ab7-9717-81576235ccac"  # Office 365 E3
$disabledPlans = @(
    "efb87545-963c-4e0d-99df-69c6916d9eb0",  # Exchange Online (Plan 2)
    "5dbe027f-2339-4123-9542-606e4d348a72"   # SharePoint Online (Plan 2)
)

Set-GroupBasedLicensing -GroupId $groupId -SkuId $e3SkuId -DisabledPlans $disabledPlans
```

## Troubleshooting

**Authentication and Connection Issues**:

```powershell
# Clear cached credentials and reconnect
Disconnect-MgGraph
Clear-MgContext

# Reconnect with verbose logging
Connect-MgGraph -Scopes "User.Read.All" -Verbose

# Check current context
$context = Get-MgContext
$context | Format-List

# Test Graph API access
try {
    $user = Get-MgUser -Top 1
    Write-Host "✓ Graph API connection successful" -ForegroundColor Green
}
catch {
    Write-Host "✗ Graph API connection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Verify token expiration
$tokenExpiry = $context.TokenExpiresOn
$minutesRemaining = ($tokenExpiry - (Get-Date)).TotalMinutes
Write-Host "Token expires in $([Math]::Round($minutesRemaining, 2)) minutes"

# Force token refresh
Disconnect-MgGraph
Connect-MgGraph -Scopes "User.Read.All" -ForceRefresh
```

**Common Issues**:

- **Insufficient privileges**: Verify required Graph API permissions granted with admin consent
- **Token expired**: Reconnect with `Connect-MgGraph` to refresh access token
- **403 Forbidden**: Check conditional access policies blocking automation accounts; add service principal to exclusion list
- **Certificate not found**: Ensure certificate exists in specified store with `Get-ChildItem Cert:\CurrentUser\My`
- **App registration missing**: Verify app exists with `Get-MgApplication -Filter "appId eq '<app-id>'"`
- **Quota exceeded**: Check API rate limits; implement exponential backoff and retry logic
- **Group not found**: Ensure group type is correct (Security vs Microsoft 365); use `Get-MgGroup -Filter "displayName eq '<name>'"`

**Diagnostic Commands**:

```powershell
# Check installed module versions
Get-Module Microsoft.Graph* -ListAvailable | Select-Object Name, Version

# Update to latest version
Update-Module Microsoft.Graph -Force

# Check API permissions for service principal
$appId = "your-app-id"
$sp = Get-MgServicePrincipal -Filter "appId eq '$appId'"
Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id |
    Select-Object AppRoleId, PrincipalDisplayName, ResourceDisplayName

# Test certificate authentication
$certThumbprint = "your-cert-thumbprint"
$cert = Get-ChildItem Cert:\CurrentUser\My\$certThumbprint
if ($cert) {
    Write-Host "✓ Certificate found: $($cert.Subject)" -ForegroundColor Green
    Write-Host "  Expires: $($cert.NotAfter)"
    Write-Host "  Thumbprint: $($cert.Thumbprint)"
}
else {
    Write-Host "✗ Certificate not found" -ForegroundColor Red
}

# Check Azure AD sign-in logs for errors
Get-MgAuditLogSignIn -Top 10 -OrderBy "createdDateTime desc" |
    Where-Object { $_.Status.ErrorCode -ne 0 } |
    Select-Object CreatedDateTime, UserPrincipalName, AppDisplayName,
                  @{N='Error';E={$_.Status.ErrorCode}},
                  @{N='Reason';E={$_.Status.FailureReason}}
```

## Performance and Tuning

**Batch Operations and Pagination**:

```powershell
# Efficient bulk user retrieval with pagination
function Get-AllUsersEfficiently {
    param(
        [Parameter(Mandatory=$false)]
        [int]$PageSize = 999  # Max allowed by Graph API
    )

    $allUsers = @()
    $uri = "https://graph.microsoft.com/v1.0/users?`$top=$PageSize&`$select=id,displayName,userPrincipalName,mail"

    do {
        $response = Invoke-MgGraphRequest -Method GET -Uri $uri
        $allUsers += $response.Value

        Write-Host "Retrieved $($allUsers.Count) users..." -ForegroundColor Cyan

        $uri = $response.'@odata.nextLink'
    } while ($uri)

    Write-Host "✓ Total users retrieved: $($allUsers.Count)" -ForegroundColor Green
    return $allUsers
}

# Batch operations with error handling
function Invoke-BatchOperation {
    param(
        [Parameter(Mandatory=$true)]
        [array]$Items,

        [Parameter(Mandatory=$true)]
        [scriptblock]$ScriptBlock,

        [Parameter(Mandatory=$false)]
        [int]$BatchSize = 20,

        [Parameter(Mandatory=$false)]
        [int]$ThrottleLimit = 5
    )

    $results = @()
    $batches = [Math]::Ceiling($Items.Count / $BatchSize)

    for ($i = 0; $i -lt $batches; $i++) {
        $start = $i * $BatchSize
        $end = [Math]::Min($start + $BatchSize - 1, $Items.Count - 1)
        $batch = $Items[$start..$end]

        Write-Host "Processing batch $($i + 1) of $batches..." -ForegroundColor Cyan

        # Process batch in parallel
        $batchResults = $batch | ForEach-Object -ThrottleLimit $ThrottleLimit -Parallel {
            $item = $_
            $sb = $using:ScriptBlock

            try {
                $result = & $sb $item
                [PSCustomObject]@{
                    Item = $item
                    Result = $result
                    Status = "Success"
                    Error = $null
                }
            }
            catch {
                [PSCustomObject]@{
                    Item = $item
                    Result = $null
                    Status = "Failed"
                    Error = $_.Exception.Message
                }
            }
        }

        $results += $batchResults

        # Throttle between batches to respect rate limits
        Start-Sleep -Milliseconds 500
    }

    return $results
}

# Usage - Bulk user property update
$users = Get-AllUsersEfficiently
$updates = Invoke-BatchOperation -Items $users -BatchSize 20 -ScriptBlock {
    param($user)
    Update-MgUser -UserId $user.id -Department "Engineering"
}

$successCount = ($updates | Where-Object { $_.Status -eq "Success" }).Count
Write-Host "✓ Updated $successCount users successfully" -ForegroundColor Green
```

**Performance Optimizations**:

- Use `-Select` parameter to retrieve only required properties; reduces response size
- Implement pagination with `-Top` and `-Skip` for large datasets (default page size: 100)
- Use `-Filter` for server-side filtering instead of client-side `Where-Object`
- Cache frequently accessed data (users, groups, apps) in memory or Redis with TTL
- Use batch requests for multiple operations; reduces HTTP round-trips (Graph API supports batching)
- Implement exponential backoff with jitter for rate limit (429) errors
- Run operations in parallel with `ForEach-Object -Parallel` (PowerShell 7+)
- Use `-ConsistencyLevel eventual` for faster queries on large datasets
- Store credentials in Azure Key Vault; retrieve once at script start
- Use delta queries to retrieve only changed entities since last query

**Monitoring and Alerting**:

```powershell
# Monitor service principal certificate expiration
$threshold = 30  # days
$apps = Get-MgApplication -All

$expiringCerts = $apps | ForEach-Object {
    $app = $_
    $app.KeyCredentials | Where-Object {
        ($_.EndDateTime - (Get-Date)).Days -le $threshold
    } | Select-Object `
        @{N='AppName';E={$app.DisplayName}},
        @{N='AppId';E={$app.AppId}},
        @{N='ExpiryDate';E={$_.EndDateTime}},
        @{N='DaysRemaining';E={($_.EndDateTime - (Get-Date)).Days}}
}

if ($expiringCerts) {
    # Send alert (integrate with Azure Monitor, email, Teams, etc.)
    $expiringCerts | Format-Table -AutoSize
    Write-Host "⚠️  $($expiringCerts.Count) certificates expiring soon!" -ForegroundColor Yellow
}

# Monitor failed sign-ins (security alerting)
$recentFailures = Get-MgAuditLogSignIn `
    -Filter "status/errorCode ne 0 and createdDateTime ge $((Get-Date).AddHours(-1).ToString('yyyy-MM-ddTHH:mm:ssZ'))" `
    -Top 100

$suspiciousActivity = $recentFailures | Group-Object UserPrincipalName |
    Where-Object { $_.Count -ge 5 }  # 5+ failures in 1 hour

if ($suspiciousActivity) {
    Write-Host "🚨 Suspicious activity detected for $($suspiciousActivity.Count) users!" -ForegroundColor Red
    # Implement automated response (e.g., enable conditional access, revoke tokens)
}
```

## References and Further Reading

**Official Documentation**:

- [Microsoft Graph PowerShell SDK](https://learn.microsoft.com/en-us/powershell/microsoftgraph/)
- [Azure AD PowerShell Reference](https://learn.microsoft.com/en-us/powershell/module/azuread/)
- [Microsoft Graph API Reference](https://learn.microsoft.com/en-us/graph/api/overview)
- [Azure AD Authentication Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [Conditional Access Documentation](https://learn.microsoft.com/en-us/azure/active-directory/conditional-access/)
- [Certificate-Based Authentication](https://learn.microsoft.com/en-us/azure/active-directory/authentication/certificate-based-authentication)

**PowerShell Resources**:

- [Microsoft Graph PowerShell Samples](https://github.com/microsoftgraph/msgraph-sdk-powershell/tree/dev/samples)
- [Azure AD Scripts Gallery](https://github.com/microsoft/AzureAD-Scripts)
- [PowerShell Gallery - Microsoft.Graph](https://www.powershellgallery.com/packages/Microsoft.Graph)

**Security Best Practices**:

- [Azure AD Security Operations Guide](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/security-operations-introduction)
- [Microsoft Identity Platform Best Practices](https://learn.microsoft.com/en-us/azure/active-directory/develop/identity-platform-integration-checklist)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

**Community Resources**:

- [Microsoft 365 Community](https://docs.microsoft.com/en-us/microsoft-365/community/)
- [Azure AD GitHub Discussions](https://github.com/AzureAD/microsoft-authentication-library-for-dotnet/discussions)
- [PowerShell Community Blog](https://devblogs.microsoft.com/powershell/)
