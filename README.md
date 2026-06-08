# Azure DocumentDB in a Day

This is a full-day, hands-on workshop for Azure DocumentDB.

The scenario is simple: we are building a small mobile shopping assistant. You will load a mobile catalog into Azure DocumentDB, search it with normal queries, try full-text search, generate embeddings, run vector search, and finally place an AI agent on top of the same data.

The goal is not to read a lot of theory. The goal is to finish the day with a working setup and a clear understanding of where DocumentDB fits in an application.

## If you are attending the workshop

Start with this file:

[WORKSHOP-RUNBOOK.md](WORKSHOP-RUNBOOK.md)

That runbook is written as the main attendee path. It includes the commands to copy, where to run them, and what output to expect.

Use the module README files when you want more explanation or when the instructor asks you to open a specific module.

## What we are building

During the workshop, you will build this flow:

```text
Mobile catalog data
  -> Azure DocumentDB
  -> full-text search and vector search
  -> Python tools
  -> AI agent in DevUI
```

By the end, you should be able to ask questions like:

```text
Recommend a phone under 50000 for camera and battery
```

or:

```text
Where can I buy OnePlus 12?
```

The agent will use DocumentDB behind the scenes to find matching phones and retail offers.

## What you need before starting

You need these installed or available:

- An Azure subscription where you can create resources.
- VS Code.
- Python 3.10 or later.
- Git.
- MongoDB Shell (`mongosh`).
- Access to Azure AI Foundry or Azure OpenAI.

You will create or use:

- An Azure DocumentDB cluster.
- An embedding model deployment, usually `text-embedding-3-small`.
- A chat model deployment, usually `gpt-4.1-mini` or `gpt-4o-mini`.

For the vector search lab, use an Azure DocumentDB cluster tier that supports DiskANN. For this workshop, use **M30 or higher**.

## 7-hour workshop flow

| Time | Session | What happens |
|---|---|---|
| 09:00-09:30 | Welcome and architecture | Walk through the mobile shopping scenario and the services used |
| 09:30-10:30 | Module 1: Setup | Create DocumentDB, connect from VS Code, create AI model deployments |
| 10:30-10:45 | Break | |
| 10:45-11:45 | Module 2: NoSQL basics | Query the mobile catalog using MongoDB-compatible commands |
| 11:45-12:45 | Module 3: Search | Generate embeddings, create indexes, run full-text and vector searches |
| 12:45-13:15 | Lunch | |
| 13:15-14:30 | Module 4: AI agents | Run the mobile advisor and retail offer agents in DevUI |
| 14:30-15:15 | Module 5: Performance | Use explain plans, indexes, projections, and limits |
| 15:15-15:30 | Break | |
| 15:30-16:00 | Module 6: Security | Review RBAC, secrets, firewall rules, and least privilege |
| 16:00-16:30 | Wrap-up | Recap, cleanup, questions, and next steps |

## Modules

| Module | Folder | Purpose |
|---|---|---|
| 1 | [1-Introduction](1-Introduction/README.md) | Create Azure resources and verify the basic connection |
| 2 | [2-NoSQL-Core-Concepts](2-NoSQL-Core-Concepts/README.md) | Learn basic document queries with the mobile catalog |
| 3 | [3-AI-Vector-Search](3-AI-Vector-Search/README.md) | Generate embeddings and compare full-text search with vector search |
| 4 | [4-AI-Agents](4-AI-Agents/README.md) | Run AI agents that call DocumentDB tools |
| 5 | [5-Performance-and-Cost-Optimization](5-Performance-and-Cost-Optimization/README.md) | Tune common mobile catalog queries |
| 6 | [6-Security-RBAC](6-Security-RBAC/README.md) | Review access, secrets, networking, and cleanup |

There is also an optional healthcare example under `Industry-solutions`. It is not part of the main 7-hour path.

## Folder guide

```text
.
├── WORKSHOP-RUNBOOK.md
├── 1-Introduction
├── 2-NoSQL-Core-Concepts
├── 3-AI-Vector-Search
│   └── mobile-data
├── 4-AI-Agents
│   └── mobile-agents
├── 5-Performance-and-Cost-Optimization
├── 6-Security-RBAC
└── scripts
```

## Data used in the workshop

The main collections are:

| Collection | What it stores |
|---|---|
| `mobiles` | Mobile catalog, specifications, features, use cases, and embeddings |
| `retail_offers` | Retailer availability, price, and offer notes |

The setup script creates the required indexes for you:

- `mobile_text_index`
- `vector_index`
- `mobile_brand_index`
- `mobile_segment_index`
- `mobile_price_index`
- `offer_title_index`
- `offer_retailer_index`

## A note for first-time Azure users

Do not rush the setup section. Most issues in this workshop come from one of these:

- The DocumentDB cluster is still deploying.
- The current client IP was not added to the firewall.
- The connection string was copied incorrectly.
- The `.env` file was not saved.
- The Azure OpenAI deployment name in `.env` does not match the deployment name in AI Foundry.

If something fails, check those items first.

## Cleanup after the workshop

When you are done:

1. Stop the local Python app.
2. Delete or scale down workshop Azure resources you no longer need.
3. Remove temporary firewall rules.
4. Do not commit `.env`.
5. Rotate any keys that were shared during a live workshop.
