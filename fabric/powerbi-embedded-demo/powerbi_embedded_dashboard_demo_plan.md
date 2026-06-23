# Power BI Embedded Dashboard Demo Plan

## Purpose

This document proposes the recommended setup for embedding the **Car Insurance / CarPro Power BI dashboard** into a demo stock-style website for stakeholders.

The intended demo experience is:

- The website has its own login page.
- Employees sign in through the website.
- Each employee has a different permission level.
- The same embedded dashboard is shown inside the webpage.
- The dashboard data is filtered according to the signed-in employee's access level.

The recommended best-practice approach is:

> **Power BI Embedded — App owns data — using a service principal, embed tokens, and row-level security (RLS).**

This approach allows the website to control user login while Power BI enforces data-level security through RLS.

---

## Recommended Architecture

```text
Employee
  ↓
Stock website login page
  ↓
Website backend validates user and permissions
  ↓
Backend maps user to Power BI RLS identity
  ↓
Backend authenticates to Power BI using service principal
  ↓
Backend generates Power BI embed token
  ↓
Frontend embeds Power BI report using Power BI JavaScript SDK
  ↓
User sees only the data allowed for their access level
```

### Example Access Mapping

| Website user | Website role | Power BI RLS identity | Data visible |
|---|---|---|---|
| alice@nashtech.com | Executive | alice@nashtech.com | All insurance data |
| bob@nashtech.com | Branch Manager | bob@nashtech.com | Assigned branch data |
| minh@nashtech.com | Sales Agent | minh@nashtech.com | Assigned agent policies |
| unknown@nashtech.com | No access | N/A | Access denied |

---

## Why This Approach

### Why not Publish to Web

Do **not** use **Publish to web** for this dashboard.

`Publish to web` creates a public embed link. Anyone with the link may be able to access the report. It is not suitable for insurance data, even for a stakeholder demo, unless the data is fully public and sanitized.

### Why not only use Power BI App audiences

Power BI App audiences are useful for distributing reports inside Power BI Service, but they are not enough for this requirement.

| Feature | Purpose |
|---|---|
| Website login | Authenticates the user in the custom website |
| Backend user mapping | Determines what access the user should receive |
| Embed token | Authorizes the embedded report session |
| RLS | Enforces data-level filtering |
| Power BI App audience | Controls Power BI App navigation/content visibility |

For this demo, **RLS and embed tokens are the core security mechanism**. Power BI App publishing is optional and can be used separately for stakeholders who want to view the report in Power BI Service.

---

## Required Components

### Fabric / Power BI

- Fabric or Power BI workspace
- Published Power BI report
- Semantic model with RLS configured
- Workspace access for the service principal
- Capacity suitable for embedding/demo usage

### Microsoft Entra ID

- App registration
- Service principal
- Client secret or certificate
- Security group for service principals

### Website Application

- Login page
- Backend API
- User-to-access mapping table
- Embed token generation endpoint
- Frontend page using Power BI JavaScript SDK

---

## Step-by-Step Setup

## Step 1 — Prepare the Power BI Report

In **Power BI Desktop**:

1. Build the Car Insurance / CarPro report.
2. Confirm the semantic model contains the fields needed for permission filtering.
3. Add or prepare a user access mapping table.

Example `UserAccess` table:

| UserKey | Branch | AgentID | AccessLevel |
|---|---|---|---|
| alice@nashtech.com | ALL | ALL | Executive |
| bob@nashtech.com | HCM | null | BranchManager |
| minh@nashtech.com | HCM | AGENT_102 | Agent |

Example insurance fact table:

| PolicyID | Branch | AgentID | Premium | ClaimAmount |
|---|---|---|---|---|
| P001 | HCM | AGENT_102 | 1200 | 0 |
| P002 | Hanoi | AGENT_205 | 900 | 300 |

The semantic model should allow `UserAccess` to filter the relevant insurance data tables through relationships.

---

## Step 2 — Configure Dynamic RLS

In **Power BI Desktop**:

```text
Modeling → Manage roles
```

Create a role:

```text
WebsiteUser
```

Apply a dynamic RLS filter on the user access table:

```DAX
UserAccess[UserKey] = USERPRINCIPALNAME()
```

Alternatively:

```DAX
UserAccess[UserKey] = USERNAME()
```

For embedded analytics with service principal, the value returned by `USERPRINCIPALNAME()` or `USERNAME()` comes from the **effective identity** passed in the embed token.

Recommended model pattern:

```text
UserAccess
  ↓
Branch / Agent dimension
  ↓
Policy / Claims fact tables
```

For the demo, a simple branch-level filter is acceptable if the stakeholder objective is to demonstrate permission-aware embedding.

---

## Step 3 — Test RLS in Power BI Desktop

In Power BI Desktop:

```text
Modeling → View as
```

Test the `WebsiteUser` role with sample users:

| Test user | Expected result |
|---|---|
| alice@nashtech.com | Sees all data |
| bob@nashtech.com | Sees assigned branch data |
| minh@nashtech.com | Sees assigned agent data |
| unknown@nashtech.com | Sees no data |

Do not proceed to embedding until RLS works correctly in Power BI Desktop.

---

## Step 4 — Publish the Report to Fabric Workspace

In Power BI Desktop:

```text
Home → Publish
```

Publish to the target workspace, for example:

```text
Car Insurance Demo
```

Then validate in Power BI Service:

1. Open the workspace.
2. Confirm the report loads.
3. Confirm the semantic model exists.
4. Configure refresh credentials if required.
5. Configure gateway if the source is on-premises.
6. Test RLS in the Power BI Service.

---

## Step 5 — Register a Microsoft Entra Application

In Azure Portal:

```text
Microsoft Entra ID → App registrations → New registration
```

Suggested name:

```text
car-insurance-embedded-demo
```

Recommended account type:

```text
Single tenant
```

Record these values:

```text
Tenant ID
Client ID / Application ID
```

Create a secret:

```text
Certificates & secrets → New client secret
```

Record the secret value immediately. For production, a certificate is preferred over a client secret. For a stakeholder demo, a short-lived secret is acceptable.

Important: for this service principal embedding scenario, avoid adding unnecessary delegated or application API permissions in Azure Portal unless explicitly required by a separate design. Power BI service principal access is mainly controlled through Power BI tenant settings and workspace access.

---

## Step 6 — Create a Security Group for the Service Principal

In Microsoft Entra ID:

```text
Groups → New group
```

Suggested group name:

```text
PowerBI-Embedded-ServicePrincipals
```

Add the service principal from the app registration to this group.

This allows the Power BI admin to enable embedding/API permissions only for this controlled group instead of the full tenant.

---

## Step 7 — Enable Power BI Tenant Settings

A Power BI / Fabric admin must enable the required settings.

In Power BI Service:

```text
Admin portal → Tenant settings → Developer settings
```

Enable:

```text
Embed content in apps
Allow service principals to use Power BI APIs
```

Best practice:

```text
Enable only for: PowerBI-Embedded-ServicePrincipals
```

Avoid enabling these settings for the entire organization unless there is a clear governance decision.

---

## Step 8 — Add Service Principal to the Workspace

In Power BI Service / Fabric:

```text
Workspace → Manage access
```

Add either:

```text
PowerBI-Embedded-ServicePrincipals
```

or the service principal directly.

For the demo, assign:

```text
Member
```

This is the simplest role for validating report access and token generation. For production hardening, review whether a more restrictive role can satisfy the required API operations.

---

## Step 9 — Capture Workspace, Report, and Semantic Model IDs

From the Power BI report URL:

```text
https://app.powerbi.com/groups/{workspaceId}/reports/{reportId}/...
```

Record:

```text
WORKSPACE_ID
REPORT_ID
DATASET_ID / SEMANTIC_MODEL_ID
```

The backend configuration should contain:

```env
TENANT_ID=...
CLIENT_ID=...
CLIENT_SECRET=...
WORKSPACE_ID=...
REPORT_ID=...
DATASET_ID=...
```

Do not expose these values in frontend code or public repositories.

---

## Step 10 — Build Website User Access Mapping

The website backend should map the logged-in user to a Power BI RLS identity.

Example demo mapping:

```json
{
  "alice@nashtech.com": {
    "powerbiUsername": "alice@nashtech.com",
    "roles": ["WebsiteUser"],
    "accessLevel": "Executive"
  },
  "bob@nashtech.com": {
    "powerbiUsername": "bob@nashtech.com",
    "roles": ["WebsiteUser"],
    "accessLevel": "BranchManager"
  },
  "minh@nashtech.com": {
    "powerbiUsername": "minh@nashtech.com",
    "roles": ["WebsiteUser"],
    "accessLevel": "Agent"
  }
}
```

The `powerbiUsername` value must match the value stored in `UserAccess[UserKey]` in the semantic model.

---

## Step 11 — Backend Obtains Power BI API Access Token

The backend authenticates using the service principal.

Token endpoint:

```text
https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token
```

OAuth grant type:

```text
client_credentials
```

Scope:

```text
https://analysis.windows.net/powerbi/api/.default
```

The backend uses:

```text
client_id
client_secret
```

The frontend must never receive the client secret.

---

## Step 12 — Backend Generates Embed Token with RLS Identity

Use the Power BI REST API:

```http
POST https://api.powerbi.com/v1.0/myorg/GenerateToken
```

Example request body:

```json
{
  "datasets": [
    {
      "id": "<DATASET_ID>"
    }
  ],
  "reports": [
    {
      "id": "<REPORT_ID>",
      "allowEdit": false
    }
  ],
  "targetWorkspaces": [
    {
      "id": "<WORKSPACE_ID>"
    }
  ],
  "identities": [
    {
      "username": "bob@nashtech.com",
      "roles": [
        "WebsiteUser"
      ],
      "datasets": [
        "<DATASET_ID>"
      ]
    }
  ]
}
```

Critical field:

```json
"username": "bob@nashtech.com"
```

This is the effective identity used by RLS in the semantic model.

---

## Step 13 — Frontend Embeds the Report

The website frontend should call the backend for embed configuration:

```http
GET /api/powerbi/embed-config
```

The backend returns:

```json
{
  "reportId": "<REPORT_ID>",
  "embedUrl": "<REPORT_EMBED_URL>",
  "embedToken": "<EMBED_TOKEN>"
}
```

Example frontend implementation:

```html
<div id="reportContainer" style="height: 800px; width: 100%;"></div>

<script src="https://cdn.jsdelivr.net/npm/powerbi-client/dist/powerbi.min.js"></script>

<script>
async function loadReport() {
  const response = await fetch('/api/powerbi/embed-config');
  const config = await response.json();

  const models = window['powerbi-client'].models;

  const embedConfig = {
    type: 'report',
    id: config.reportId,
    embedUrl: config.embedUrl,
    accessToken: config.embedToken,
    tokenType: models.TokenType.Embed,
    permissions: models.Permissions.Read,
    settings: {
      panes: {
        filters: { visible: false },
        pageNavigation: { visible: true }
      },
      background: models.BackgroundType.Transparent
    }
  };

  const container = document.getElementById('reportContainer');
  powerbi.embed(container, embedConfig);
}

loadReport();
</script>
```

---
# Validation Plan

## Embedded Website Tests

| Test case | Expected result |
|---|---|
| Executive login | User sees all permitted car insurance data |
| Branch manager login | User sees only assigned branch data |
| Agent login | User sees only assigned agent policies |
| Unknown user login | Website denies access and does not generate embed token |
| Expired token | Website requests a new embed token |
| Direct frontend inspection | No client secret is visible in browser code |

## Power BI Security Tests

| Test case | Expected result |
|---|---|
| RLS test in Desktop | Correct data filtering for each test user |
| RLS test in Power BI Service | Same result as Desktop |
| Service principal workspace access | Report and token generation succeed |
| User without app access | Cannot access the Power BI App |
| User without data permission | Sees no restricted data |

---

# Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Publish to web accidentally used | Data exposure | Disable/avoid public embed; use embed tokens only |
| Client secret exposed in frontend | Service principal compromise | Keep secrets only in backend/key vault |
| RLS relationship incorrectly modeled | Users may see wrong data | Test with multiple user identities before demo |
| App audiences treated as data security | Possible overexposure | Use RLS for data-level filtering |
| Service principal too broadly enabled | Governance risk | Scope tenant settings to a security group |
| Stakeholders get workspace access | Unnecessary edit/data access | Use app audiences or embedded website access instead |

---

# Recommended Demo Implementation Summary

The recommended stakeholder demo setup is:

```text
1. Build Power BI report
2. Add dynamic RLS with a UserAccess table
3. Publish report to Fabric workspace
4. Register Microsoft Entra app
5. Create service principal security group
6. Enable Power BI tenant developer settings for that group
7. Add service principal to workspace
8. Build stock website login
9. Backend maps logged-in user to RLS identity
10. Backend generates embed token
11. Frontend embeds report with Power BI JavaScript SDK
12. Optionally publish Power BI App for Power BI Service distribution
```

Final design principle:

> The website authenticates the user. The backend determines the user's data identity. The embed token carries that identity to Power BI. Power BI RLS enforces what data the user can see.
