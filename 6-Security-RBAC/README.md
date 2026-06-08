# Module 6: RBAC and Security for Azure DocumentDB

**Duration:** 30-45 minutes | **Goal:** Secure Azure DocumentDB access using least privilege, safe secrets handling, network controls, and production-ready operational practices.

## Why this module matters

The workshop uses simple local credentials because that is the fastest way to learn. Before using this pattern in a real app, you need to understand which parts should change.

In this module, you will review:

- Difference between Azure RBAC and database authentication.
- How to use least privilege for workshop and application access.
- How to protect connection strings and API keys.
- How firewall, private networking, and TLS fit into the security model.
- What to check before moving a workshop app toward production.

---

## Part 1: Understand the security layers

Azure DocumentDB access usually has multiple layers:

| Layer | Purpose | Example |
|---|---|---|
| Azure RBAC | Controls who can manage Azure resources | Create cluster, view settings, change networking |
| Database authentication | Controls who can connect to the database endpoint | Username/password in MongoDB connection string |
| Database roles | Controls what an application identity can do inside the database | Read-only, read-write, admin-style access |
| Network access | Controls where connections can come from | Firewall rules, private endpoint, allowed IPs |
| Secret management | Controls where credentials are stored | `.env` for lab, Key Vault for production |

**Key point:** Azure RBAC lets a user manage the Azure resource. It does not automatically mean the application should use an admin database connection string.

---

## Part 2: Azure RBAC for workshop participants

For a hands-on workshop, participants commonly need permissions to:

- Create or access the DocumentDB resource.
- Read connection information.
- Configure networking for their client IP.
- Create or access Azure AI Foundry / Azure OpenAI deployments.

Recommended workshop roles depend on how the environment is prepared:

| Scenario | Recommended access |
|---|---|
| Attendees create their own resources | Contributor on a workshop resource group |
| Instructor pre-provisions resources | Reader plus a controlled way to retrieve connection details |
| Shared team environment | Least-privilege custom role or resource-group scoped Contributor |

Avoid giving subscription-wide access when a resource-group scope is enough.

---

## Part 3: Database users and least privilege

The workshop starts with an admin-style connection string because it is simple for setup. For production, use separate identities for different application responsibilities.

Suggested access model:

| Identity | Access | Used by |
|---|---|---|
| Admin user | Cluster/database administration | Instructor or operator only |
| App read-write user | Read/write required collections | Module 4 application |
| Read-only user | Read search data only | Reporting, demo dashboards, validation |

### Hands-on discussion

Review the connection string in `.env`:

```text
DOCUMENTDB_CONNECTION_STRING=mongodb+srv://<username>:<password>@<cluster-name>.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000
```

Discuss:

1. Which username is being used?
2. Is it an admin user or an app-specific user?
3. Which collections does the app really need?
4. Could the AI agent run with read-only access after data is loaded?

For this workshop, the running agents only need to read from:

- `mobiles`
- `retail_offers`

Data loading scripts need write access, but the running agent does not.

---

## Part 4: Secrets handling

The workshop uses `.env` for local development:

```powershell
Copy-Item .env.template .env
```

This is acceptable for a local workshop lab, but follow these rules:

- Never commit `.env`.
- Never paste connection strings or API keys into slides, screenshots, chat, or shared notes.
- Rotate credentials after public demos or shared workshops.
- Use Azure Key Vault, managed identity patterns, or your organization's approved secret store for production.

Verify `.env` is ignored:

```powershell
git status --short
```

`.env` should not appear as a tracked file.

---

## Part 5: Network access

During the lab, you may allow your current client IP so VS Code and local Python scripts can connect.

For production:

- Prefer private networking where possible.
- Avoid broad public ranges such as `0.0.0.0 - 255.255.255.255`.
- Keep firewall rules specific and documented.
- Remove temporary workshop IP rules after the event.
- Keep TLS enabled in the connection string.

Workshop check:

1. Open the DocumentDB resource in Azure Portal.
2. Go to **Networking**.
3. Confirm only expected IP ranges are allowed.
4. Remove broad test rules when the workshop is complete.

---

## Part 6: Production readiness checklist

Use this checklist before turning the workshop sample into a real application:

| Area | Check |
|---|---|
| Identity | App uses least-privilege database credentials |
| Secrets | Connection strings and API keys are stored outside source control |
| Network | Public access is restricted or private networking is used |
| TLS | Connection strings keep TLS enabled |
| Indexes | Query, text, and vector indexes are explicitly created |
| Connection reuse | Application reuses a single `MongoClient` per process |
| Monitoring | Slow queries, CPU, memory, and storage are monitored |
| Scaling | Cluster tier is selected based on working set and vector workload |
| High availability | HA is enabled for production workloads |
| Cleanup | Lab resources and temporary firewall rules are removed |

---

## Instructor talking points

- Separate "who can manage the Azure resource" from "who can read/write database data."
- Admin connection strings are convenient for labs but risky for applications.
- AI agents often need only read access after ingestion is complete.
- Vector workloads need secure access to both the database and the embedding model.
- Security is part of the application architecture, not a final add-on.

---

## Next steps

- Revisit [Module 5](../5-Performance-and-Cost-Optimization/README.md) to connect security choices with scale and cost.
- Replace local `.env` secrets with an approved secret-management pattern before production use.
- Review your organization's compliance requirements before using real customer, healthcare, or regulated data.
