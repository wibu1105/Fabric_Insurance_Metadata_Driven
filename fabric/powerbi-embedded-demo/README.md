# Power BI Embedded Demo Website

This folder contains a small Node.js + React demo website for embedding the two CarPro Power BI dashboards.

The goal is a simple stakeholder-facing shell, not a production identity system. The visual design is intentionally minimal and should stay focused on demonstrating Power BI embedding, dashboard switching, and row-level-security behaviour.

## Dashboards included

| Dashboard | Repository artifact | Semantic model usage | Demo purpose |
| --- | --- | --- | --- |
| Sales & Quotation Dashboard | `quotation_sale.Report` | `dashboard_semantic_model` only | Business view for quotation status, premium, provider, branch, and agent analytics. |
| Policy & Payment Operation Dashboard | Power BI policy/payment operation report | `OperationalDashboard` semantic model ID stored in `POLICY_PAYMENT_OPERATION_DASHBOARD_SEMANTIC_MODEL_ID` | Operations view for policy issuance, policy lifecycle, payment collection, outstanding payments, and cancellation visibility. |

Both dashboards are expected to use the same RLS setup in their semantic models.

## Application structure

```text
powerbi-embedded-demo/
├── server/                    # Node/Express API and static file server
│   ├── index.js               # Express routes and Power BI REST orchestration
│   ├── logger.js              # Structured request/API logging with redaction
│   ├── microsoftInteractiveAuth.js
│   ├── powerBiEmbed.js
│   ├── warehouseUsers.js
│   └── __tests__/
├── src/
│   ├── components/            # One file per reusable block/component
│   ├── data/                  # Dashboard catalog
│   ├── pages/                 # Page-level master files
│   │   ├── LoginPage.jsx
│   │   └── LandingPage.jsx
│   ├── services/              # Frontend API helpers
│   ├── styles/                # NashTech themed CSS
│   └── __tests__/             # Vitest tests
├── public/assets/             # Copied NashTech logo assets from the repo
├── Dockerfile                 # Deployment-ready container build
├── .env.example               # Required environment variable template
└── package.json
```

The webpage intentionally contains only two pages:

1. **Login** — username/password sign-in against `web.app_users_rls`.
2. **Landing** — header, dashboard switcher, embedded dashboard area, logout, and demo footer.

## Brand styling

The UI uses the NashTech red from the repository logo asset: `#e30613` (`rgb(227, 6, 19)`). Logo files were copied from:

```text
../Rookie2Engineer/dashboard/Nash_Tech_Red-version.png
../Rookie2Engineer/dashboard/White-logo.png
```

into:

```text
public/assets/nashtech-logo-red.png
public/assets/nashtech-logo-white.png
```

## Local setup

```bash
cd powerbi-embedded-demo
npm install
npm run dev
```

During local development:

- Vite serves the React app on `http://localhost:5173`.
- Vite proxies `/api/*` requests to the Node backend on `http://localhost:8080`.
- The backend health endpoint is `http://localhost:8080/api/health`.

Use `http://localhost:5173` as the normal developer entry point.

## Environment configuration

Copy `.env.example` to `.env` and fill in the values.

```bash
DEMO_MODE=false
PORT=8080
SESSION_SECRET=<long-random-string-for-session-cookie-signing>
SESSION_COOKIE_SECURE=false
SESSION_MAX_AGE_MS=28800000
FRONTEND_APP_URL=http://localhost:5173

MICROSOFT_REDIRECT_URI=http://localhost:5173/api/auth/microsoft/callback
POWERBI_AUTH_SCOPES=https://analysis.windows.net/powerbi/api/.default

TENANT_ID=<microsoft-entra-tenant-id>
CLIENT_ID=<app-registration-application-client-id-guid>
CLIENT_SECRET=<app-registration-client-secret-value>

AUDIT_WAREHOUSE_NAME=<fabric-warehouse-name>
AUDIT_WAREHOUSE_WORKSPACE_ID=<workspace-guid>
AUDIT_WAREHOUSE_ID=<warehouse-guid>
AUDIT_WAREHOUSE_SQL_ENDPOINT=<fabric-warehouse-sql-endpoint>
APP_USERS_USER_MAIL_COLUMN=user_mail
POWERBI_RLS_ROLE=rls_level

AUDIT_WAREHOUSE_NAME=Rookie2Engineer_Warehouse
AUDIT_WAREHOUSE_WORKSPACE_ID=5db1b4b5-9a8b-4bf9-808d-ed9af21bd9a8
AUDIT_WAREHOUSE_ID=0cbc1668-221f-4824-865d-49e8e013e43e
AUDIT_WAREHOUSE_SQL_ENDPOINT=3ukzqa5oadlurln3behjhxf4ae-ww2lcxmltl4uxaen5wnpeg6zva.datawarehouse.fabric.microsoft.com

SALES_QUOTATION_WORKSPACE_ID=<workspace-id>
SALES_QUOTATION_REPORT_ID=<report-id>
SALES_QUOTATION_DASHBOARD_SEMANTIC_MODEL_ID=<dashboard_semantic_model-id>

POLICY_PAYMENT_OPERATION_WORKSPACE_ID=<workspace-guid>
POLICY_PAYMENT_OPERATION_REPORT_ID=<report-guid>
POLICY_PAYMENT_OPERATION_DASHBOARD_SEMANTIC_MODEL_ID=<operational-dashboard-semantic-model-guid>
POLICY_PAYMENT_OPERATION_OPERATIONALDASHBOARD_SEMANTIC_MODEL_ID=<upstream-operational-dashboard-semantic-model-guid>
```

Important notes:

- `CLIENT_ID` must be the **Application (client) ID** from the app registration Overview page.
- `CLIENT_SECRET` must be the client secret **Value**, not the Secret ID.
- `MICROSOFT_REDIRECT_URI` must exactly match a redirect URI registered on the app registration.
- For Vite local development, register `http://localhost:5173/api/auth/microsoft/callback`.
- For direct built-server testing on Express only, register `http://localhost:8080/api/auth/microsoft/callback` and change `MICROSOFT_REDIRECT_URI` accordingly.
- The Microsoft access token is never sent to the browser. It is stored only in the Node server session.

## How the System Works: Authentication & RLS

The demo uses a two-stage authentication architecture because the tenant blocks non-interactive service-principal style embedding through MFA/policy constraints. The interactive presenter login supplies the Power BI REST API access token, while the custom database login supplies the mock RLS identity.

### Stage 1: Microsoft Admin Login — Infrastructure Auth

Purpose: give the Node backend a Microsoft access token that can call the Power BI REST API.

1. The presenter opens the React app at `http://localhost:5173`.
2. `src/App.jsx` calls `GET /api/auth/microsoft/status` with `credentials: 'include'`.
3. If the backend session does not contain a valid Microsoft token, the browser is redirected to `GET /api/auth/microsoft/login`.
4. `server/microsoftInteractiveAuth.js` uses `@azure/msal-node` and the Authorization Code Flow to build the Microsoft login URL.
5. The presenter signs in interactively with their MFA-enabled Microsoft account.
6. Microsoft redirects back to `/api/auth/microsoft/callback`.
7. The backend calls `acquireTokenByCode`, receives the Power BI API access token, and stores it in `request.session.microsoftAuth`.
8. The backend redirects the browser back to the React frontend (`/` or `FRONTEND_APP_URL`).

The session is created with `express-session` and an HttpOnly cookie named `carpro.sid`. The browser only receives the session cookie. It does **not** receive the Microsoft access token.

Session fields used for the Microsoft stage:

```js
request.session.microsoftAuth = {
  accessToken,
  expiresOn,
  accountUsername
};
```

### Stage 2: Custom Mock Login — DB Auth

Purpose: choose the demo user identity that the Power BI semantic model should see for RLS simulation.

1. After Microsoft auth is available, `src/App.jsx` displays the existing custom login page.
2. The presenter types a warehouse demo user such as `EXECUTIVE`, `AG001`, or `BIC`.
3. `src/services/authApi.js` calls `POST /api/auth/login` with `credentials: 'include'`.
4. `server/warehouseUsers.js` validates the username/password against the Fabric Warehouse table `web.app_users_rls`.
5. The backend stores the mock user in the same server-side session.

Session fields used for the mock user stage:

```js
request.session.appUser = {
  userMail,
  effectiveUsername,
  username,
  role,
  rlsLevel,
  accessValue,
  powerbiUsername,
  powerbiRoles
};
```

### Stage 3: Dashboard Embedding with RLS

Purpose: generate the Power BI embed configuration using the Microsoft master token and the selected mock RLS user.

1. The landing page renders `PowerBIEmbed` for the active dashboard.
2. The frontend calls `GET /api/powerbi/embed-config?dashboardId=...` with the session cookie.
3. The backend reads `request.session.microsoftAuth.accessToken` to authorize Power BI REST API calls.
4. The backend reads `request.session.appUser` to build the effective identity.
5. The backend calls Power BI REST API to read report metadata and generate an embed token.
6. The backend returns only the safe embed configuration to React: report ID, embed URL, embed token, semantic model IDs, and expiration.

The frontend never sees the Microsoft master access token.

The backend also merges the report metadata `datasetId` with the configured semantic model IDs and sends those datasets with `xmlaPermissions: ReadOnly`. This supports reports whose visible report model is linked to another semantic model through the MSOLAP/XMLA path.

## RLS mapping into Power BI effective identities

The warehouse table is expected to follow this shape:

```text
web.app_users_rls(user_mail, password, rls_level, access_value)
```

Recommended demo levels:

| rls_level | Meaning | access_value |
| ---: | --- | --- |
| 1 | Executive, all data | `NULL` |
| 2 | Agent, own agent only | Agent code such as `AG001` |
| 3 | Provider, own provider only | Provider code such as `BIC` |

The backend maps the warehouse row into the Power BI `identities` payload used by `GenerateToken`:

```js
{
  username: appUser.powerbiUsername,
  roles: [process.env.POWERBI_RLS_ROLE || 'rls_level'],
  datasets: semanticModelIds,
  customData: JSON.stringify({
    rls_level: appUser.rlsLevel,
    access_value: appUser.accessValue
  })
}
```

Current mapping rule:

- If `access_value` exists, it becomes the effective `powerbiUsername`.
- If `access_value` is `NULL`, the prefix before `@` in `user_mail` becomes the effective `powerbiUsername`.
- `POWERBI_RLS_ROLE=rls_level` is the default Power BI role name.
- `customData` carries `rls_level` and `access_value` only. The Power BI identity username carries the RLS value used by semantic models that match on `USERNAME()` / `USERPRINCIPALNAME()`.

The semantic model can therefore use either:

- `USERPRINCIPALNAME()` / effective username matching, or
- `CUSTOMDATA()` parsing, depending on the RLS design selected by the dashboard teammate.

## Developer test flow for local RLS switching

1. Start the app:

```bash
npm run dev
```

2. Open:

```text
http://localhost:5173
```

3. If the Microsoft login screen appears, sign in with the presenter account. This is expected. It is the infrastructure authentication stage.

4. After redirecting back to the custom CarPro login page, log in as a mock warehouse user:

```text
web.app_users_rls(user_mail, password, rls_level, access_value)
```

For the current demo, passwords are stored in the warehouse table as plain text. The server keeps `user_mail` as `userMail`, then derives `effectiveUsername` / `powerbiUsername` for Power BI RLS. The login page reads selectable users from `/api/auth/users`, which queries the warehouse and never returns passwords.

| user_mail | Effective username | rls_level | access_value | Meaning |
| --- | --- | ---: | --- | --- |
| `EXECUTIVE@mail.com` | `EXECUTIVE` | 1 | `NULL` | Admin, can see all data. |
| `AG001@mail.com` | `AG001` | 2 | `AG001` | Agent-level access. |
| `BIC@mail.com` | `BIC` | 3 | `BIC` | Lowest scoped access. |

The login page also supports changing the password by updating the same warehouse table.

## How the system works

Use this section for teammate handover.

1. **User opens the React app.** `src/App.jsx` checks the server-side Microsoft presenter session, then decides whether to show `LoginPage` or `LandingPage` based on the app user stored in the HttpOnly session cookie.
2. **User signs in.** `src/pages/LoginPage.jsx` posts `userMail` and `password` to `/api/auth/login`. The Node server checks `web.app_users_rls` through the Fabric Warehouse SQL endpoint and returns a signed demo session.
3. **Landing page loads the selected dashboard.** `src/pages/LandingPage.jsx` keeps the active dashboard state. The header buttons switch between Sales & Quotation and Policy & Payment Operation without leaving the page.
4. **Frontend requests embed configuration.** `src/components/PowerBIEmbed.jsx` calls `src/services/embedApi.js`, which requests `/api/powerbi/embed-config?dashboardId=...` with the session cookie.
5. **Node server validates the request.** `server/index.js` checks that the dashboard ID exists and reads the authenticated warehouse user from the signed session.
6. **Demo mode returns a placeholder config.** When `DEMO_MODE` is not set to `false`, the server returns a demo response and the React app shows the prepared Power BI placeholder area.
7. **Live mode generates a real Power BI embed config.** When `DEMO_MODE=false`, the server reads the configured workspace, report, and semantic model IDs from environment variables, uses the Microsoft presenter token stored in the server session, reads report metadata from Power BI REST API, generates an embed token with `username` equal to the effective RLS username, and returns only the embed URL/token to the frontend.
8. **Semantic model rules are dashboard-specific.** Sales & Quotation uses only `dashboard_semantic_model`. Policy & Payment Operation includes both `dashboard_semantic_model` and `OperationalDashboard` in the embed-token `datasets` list and RLS identity.
9. **Debug logs correlate each request.** Every response includes an `x-request-id`. The server writes structured JSON logs for inbound API calls, demo/live embed flow, Entra token calls, and outbound Power BI REST calls.

## Deployment preparation

The deployment platform has not been selected yet, so the app is prepared in a portable way:

- `npm run build` creates the React static assets in `dist/`.
- `npm start` runs the Node/Express server and serves both `/api/*` endpoints and the built frontend.
- `Dockerfile` supports container deployment to Azure App Service for Containers, Azure Container Apps, VM/container host, or another platform later.
- Runtime configuration is environment-variable based; secrets should be supplied by the chosen deployment platform or a secret store, not committed to git.
- Use a persistent session store for deployment. The current `express-session` MemoryStore is acceptable only for local demo development.
- Set `SESSION_COOKIE_SECURE=true` behind HTTPS.

Container build example:

```bash
docker build -t carpro-powerbi-embedded-demo .
docker run --rm -p 8080:8080 --env-file .env carpro-powerbi-embedded-demo
```

## Production hardening notes

Before using this beyond a controlled demo:

1. Replace plain-text demo passwords with Microsoft Entra ID or the chosen enterprise identity flow.
2. Move secrets to a managed secret store.
3. Replace the default in-memory Express session store with Redis, database-backed session storage, or the deployment platform's supported session mechanism.
4. Confirm Power BI/Fabric permissions for the presenter account or embedding identity.
5. Validate RLS in Power BI Desktop and Power BI Service for every warehouse login user.
6. Add audit logging for generated embed tokens and password changes.
7. Review capacity/cost implications for the selected Fabric or Power BI deployment model.
