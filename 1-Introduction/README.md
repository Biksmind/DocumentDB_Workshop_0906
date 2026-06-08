# Module 1: Set up Azure DocumentDB and AI Foundry

**Duration:** 60-90 minutes

This module gets the environment ready for the rest of the workshop. Take your time here. If something is wrong in this module, the later copy-paste commands will fail.

You will create an Azure DocumentDB cluster, connect to it from VS Code, and create the AI model deployments used for embeddings and chat.

## Before you start

Keep these open:

- Azure Portal: https://portal.azure.com
- AI Foundry: https://ai.azure.com
- VS Code
- This README

You also need an Azure subscription where you can create resources.

## Prerequisites

- An Azure subscription with contributor access
- [VS Code](https://code.visualstudio.com/) installed
- A web browser for Azure Portal

---

## Part 1: Create Azure DocumentDB Cluster (20 minutes)

### 1.1 Open Azure Portal

1. Open a browser.
2. Go to [https://portal.azure.com](https://portal.azure.com).
3. Sign in with your Azure account.
4. Wait until the Azure Portal home page is fully loaded.

### 1.2 Create DocumentDB Cluster

1. In the Azure Portal top search bar, type **Azure DocumentDB**.
2. Click **Azure DocumentDB** from the search results.
3. Click **Create**.
4. If the portal shows multiple database options, choose **Azure DocumentDB** or **Azure DocumentDB with MongoDB compatibility**.
5. Fill in the Basics page:
   - **Subscription:** Select your subscription
   - **Resource group:** Create new `rg-az-documentdb-workshop` or use existing
   - **Cluster name:** `az-docdb-workshop-cluster` (must be globally unique)
   - **Location:** Choose region (e.g., East US, West Europe)
   - **MongoDB version:** Select latest (8.0)
   - **High Availability:** Uncheck **Enabled**. You do not need it for the lab, and leaving it off saves money.
   - **Cluster tier:** Select **M30** (for vector search support)
   - **Storage:** 128 GB (default)
   - **Compute:** 2 vCores (default for M30)
6. Click **Review + create**.
7. Wait for validation to complete.
8. Click **Create**.

**Wait 10-15 minutes** for deployment to complete

Do not close the browser tab while the deployment is running. You can continue reading the next steps, but you need the deployment to finish before you can copy the connection string.

### 1.3 Configure Firewall

1. When deployment completes, click **Go to resource**.
2. In the left navigation, find **Settings**.
3. Under **Settings**, click **Networking**.
4. Select **Public access from selected IP addresses** or **Public access (allowed IP addresses)**, depending on what the portal shows.
5. Click **+ Add current client IP address**.
6. Confirm your IP address appears in the allowed list.
7. Click **Save**.
8. Wait until the save operation completes.

For a workshop, avoid adding `0.0.0.0 - 255.255.255.255` unless the instructor explicitly asks you to. If you add it temporarily, remove it after the workshop.

### 1.4 Get Connection String

1. In the left navigation, under **Settings**, click **Connection strings**.
2. Find the **Primary Connection String** or **Global read-write connection string**.
3. Click the copy icon next to the connection string.
4. Paste it into a temporary local note. You will use it later in `.env`.

It looks similar to this:

   ```
   mongodb+srv://<username>:<password>@<cluster-name>.mongocluster.cosmos.azure.com/?tls=true
   ```

Do not share the real connection string in chat, screenshots, or slides.

Checkpoint: your DocumentDB cluster is running, your IP is allowed, and you have copied the connection string.

---

## Part 2: Connect DocumentDB via VS Code (15 minutes)

### 2.1 Install DocumentDB Extension for VS Code

**Method 1: Extensions panel**
1. Open **VS Code**.
2. On the left Activity Bar, click the **Extensions** icon.
3. In the search box, type **DocumentDB for VS Code**.
4. Click the extension from Microsoft.
5. Click **Install**.
6. If VS Code asks you to reload, click **Reload**.

**Method 2: Quick install**
1. Open VS Code Command Palette (Ctrl+Shift+P or Cmd+Shift+P on Mac)
2. Paste: `ext install ms-azuretools.vscode-documentdb`
3. Press Enter

**Extension features:**
- Supports both DocumentDB and MongoDB databases
- Provides Table, Tree, and JSON views
- Includes a query editor with syntax highlighting and auto-completion
- Lets you create, edit, and delete documents
- Supports data import and export in JSON and CSV formats
- Includes index management and performance monitoring

### 2.2 Add Connection to Your DocumentDB Cluster
1. In VS Code, click the **DocumentDB** icon on the left Activity Bar.
2. Click **Add New Connection**.
3. Select **Connection String**.
4. Paste the connection string you copied from Azure Portal.
5. Make sure the end includes these parameters:
   ```
   mongodb+srv://<username>:<password>@<cluster>.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256
   ```
6. Press **Enter**.
7. Wait a few seconds.
8. Your cluster should appear in the DocumentDB panel.

**Connection string format:**
- Replace `<username>` with your DocumentDB admin username
- Replace `<password>` with your admin password
- Replace `<cluster>` with your cluster name
- Keep the `?tls=true&authMechanism=SCRAM-SHA-256` parameters

### 2.3 Create Your First Database
1. In the **DocumentDB** panel, find your cluster connection.
2. Right-click the cluster name.
3. Click **Create Database...**.
4. Type:
   ```text
   Workshop_DB
   ```
5. Press **Enter**.
6. Right-click the cluster again.
7. Click **Refresh**.
8. Expand the cluster. You should see `Workshop_DB`.

**Verification:** You should now have a database called `Workshop_DB`

---

## Required Before You Continue

MongoDB Shell (`mongosh`) is required for the copy-paste runbook. If it is not installed, install it now.

- **Windows (winget):** `winget install MongoDB.Shell`
- **macOS (Homebrew):** `brew install mongosh`
- **Linux (APT):** follow the official instructions: https://www.mongodb.com/docs/mongodb-shell/install/

Verify installation:

```bash
mongosh --version
```

---


### 2.4 Verify Your Connection
1. In the DocumentDB panel, expand your cluster.
2. Right-click **Workshop_DB**.
3. Click **New Query Playground**.
4. A new query playground file opens in the editor.
5. Paste this code:

```javascript
// Switch to your workshop database
use('Workshop_DB')

// Confirm the connection is alive
db.runCommand({ ping: 1 })

// Check what collections exist (empty for now — that's expected)
show collections

// View basic database stats
db.stats()
```

6. Click **Run** above the code block.

**Expected output for ping:**
```json
{ "ok": 1 }
```

**Expected output for stats:** a JSON document showing `Workshop_DB` with 0 collections and 0 documents — confirming the database exists and is ready to use.

**Verification:** You are connected to `Workshop_DB` and the database is ready for data

### 2.5 Create Test Collection with Mobile Data
In the open query playground, create your first collection:

```javascript
// Create a collection with sample documents
db.mobiles_preview.insertMany([
  {
    title: "Contoso Phone Lite 5G",
    brand: "Contoso",
    segment: "Budget 5G",
    priceInr: 12999,
    rating: 4.1,
    batteryMah: 5000,
    features: ["5G", "large battery", "budget friendly"],
    createdAt: new Date()
  },
  {
    title: "Contoso Phone Pro",
    brand: "Contoso",
    segment: "Premium",
    priceInr: 69999,
    rating: 4.6,
    batteryMah: 4800,
    features: ["flagship camera", "fast charging", "AMOLED display"],
    createdAt: new Date()
  }
])

// Query all preview mobiles
db.mobiles_preview.find({})

// Count documents
db.mobiles_preview.countDocuments()
```

**Expected results:**
```javascript
// Insert result
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId('...'),
    '1': ObjectId('...')
  }
}

// All preview mobiles
[
  { _id: ObjectId('...'), title: 'Contoso Phone Lite 5G', brand: 'Contoso', ... },
  { _id: ObjectId('...'), title: 'Contoso Phone Pro', brand: 'Contoso', ... }
]

// Count
2
```

Click **Run** above each query to execute it.

**Alternatively: Create the collection using the GUI**

If you prefer not to use a query playground, you can create a collection and add documents directly from the DocumentDB panel in VS Code:

1. In the **DocumentDB** panel, expand your cluster and right-click on **Workshop_DB**
2. Select **"Create Collection..."**
3. Enter the collection name: `mobiles_preview` and press **Enter**
4. The `mobiles_preview` collection now appears under **Workshop_DB**
5. Right-click on **mobiles_preview** and select **"Create Document..."**
6. A JSON editor opens with an empty document template — replace the contents with the first sample document and save:
   ```json
   {
     "title": "Contoso Phone Lite 5G",
     "brand": "Contoso",
     "segment": "Budget 5G",
     "priceInr": 12999,
     "rating": 4.1,
     "batteryMah": 5000,
     "features": ["5G", "large battery", "budget friendly"],
     "createdAt": { "$date": "2026-06-02T00:00:00Z" }
   }
   ```
7. Right-click on **mobiles_preview** again → **"Create Document..."** and add the second document:
   ```json
   {
     "title": "Contoso Phone Pro",
     "brand": "Contoso",
     "segment": "Premium",
     "priceInr": 69999,
     "rating": 4.6,
     "batteryMah": 4800,
     "features": ["flagship camera", "fast charging", "AMOLED display"],
     "createdAt": { "$date": "2026-06-02T00:00:00Z" }
   }
   ```

To view what you inserted, click on the **mobiles_preview** collection in the panel — it opens in Table, Tree, or JSON view depending on your preference.

### 2.6 Explore DocumentDB Extension Features

**Browse and View Data:**
1. In **DocumentDB** panel, right-click your connection → Click **Refresh**
2. Expand your connection → **Workshop_DB** → **mobiles_preview**
3. Click on **mobiles_preview** collection to open it
4. Choose your preferred view:
   - **Table View** - Spreadsheet-like grid with sortable columns
   - **Tree View** - Hierarchical display of document structure
   - **JSON View** - Raw JSON with syntax highlighting
5. Use the pagination controls to browse through documents

**Note:** If your new database or collection does not appear, right-click the connection and select **Refresh**.

**Running more queries:**
Open additional query playgrounds for different queries (right-click database → **New Query Playground**):
```javascript
// Collection names are case-sensitive. Use the exact name shown in the panel.

// Find with filters
db.mobiles_preview.find({ priceInr: { $lte: 20000 } })

// Create indexes
db.mobiles_preview.createIndex({ brand: 1, priceInr: 1 })

// View indexes
db.mobiles_preview.getIndexes()

// Aggregation pipeline
db.mobiles_preview.aggregate([
  { $group: { _id: "$segment", count: { $sum: 1 }, avgPrice: { $avg: "$priceInr" } } },
  { $sort: { avgPrice: -1 } }
])
```

**Expected output:**
```javascript
// Find with filters
[
   {
      _id: ObjectId('...'),
      title: 'Contoso Phone Lite 5G',
      brand: 'Contoso',
      segment: 'Budget 5G',
      priceInr: 12999,
      createdAt: ISODate('...')
   }
]

// Create index
'brand_1_priceInr_1'

// View indexes
[
   { key: { _id: 1 }, name: '_id_' },
   { key: { brand: 1, priceInr: 1 }, name: 'brand_1_priceInr_1' }
]

// Aggregation pipeline
[
   { _id: 'Premium', count: 1, avgPrice: 69999 },
   { _id: 'Budget 5G', count: 1, avgPrice: 12999 }
]
```

**Manage databases and collections:**
Right-click options available:
- **On Cluster:** Create Database, Refresh
- **On Database:** New Query Playground, Open Interactive Shell, Create Collection, Delete Database, Refresh
- **On Collection:** Create Document, Export, Drop Collection, Refresh

**Import/Export Data:**
- Right-click collection → **Export** to save as JSON or CSV
- Right-click database → **Import** to load JSON files

**Using Query Playground**
To run queries:
- Right-click on your database → **New Query Playground**
- Type or paste MongoDB commands
- Click **Run** to execute the query

**Verification:** You can browse databases, run queries through query playgrounds, and manage documents in VS Code

---

## Part 3: Create AI Foundry Project (20 minutes)


### 3.1 Open AI Foundry

1. Open [https://ai.azure.com](https://ai.azure.com).
2. Sign in with the same Azure account.
3. If prompted to select a tenant or directory, choose the one that contains your Azure subscription.

### 3.2 Create New Project
1. Click **+ New project**.
2. Fill in the project details:
   - **Project name:** `az-docdb-ai-workshop`
   - **Subscription:** Select your Azure subscription
   - **Resource group:** Use `rg-az-documentdb-workshop` (same as DocumentDB) or create new
   - **Location:** Choose region (preferably same as DocumentDB)
3. Click **Create**.

**Wait 2-3 minutes** for the project to be created

### 3.3 Deploy Embedding Model
1. In AI Foundry, click **Model catalog** or **Browse models**. The label may vary slightly by portal version.
2. In the search box, type:
   ```text
   text-embedding-3-small
   ```
3. Click the `text-embedding-3-small` model card.
4. Click **Deploy**.
5. Use these settings:
   - **Deployment name:** `text-embedding-3-small`
   - **Model version:** Latest
6. Click **Deploy**.

This is the recommended embedding model for the workshop because it is fast and cost-effective.

**Wait 1-2 minutes** for the deployment to complete

### 3.4 Deploy Chat Model
1. Go back to the model catalog.
2. Search for:
   ```text
   gpt-4.1-mini
   ```
3. Click the model card.
4. Click **Deploy**.
5. Use these settings:
   - **Deployment name:** `gpt-4.1-mini`
   - **Model version:** Latest
   - **Tokens per minute rate limit:** Default (varies by quota)
6. Click **Deploy**.

**Wait 1-2 minutes** for the deployment to complete

If `gpt-4.1-mini` is not available in your region, use `gpt-4o-mini` as fallback.

### 3.5 Verify Deployments
1. Go to **Deployments** page (left navigation)
2. You should see both deployments:
   - `text-embedding-3-small` - Status: Succeeded
   - `gpt-4.1-mini` (or `gpt-4o-mini`) - Status: Succeeded
3. Note the **Deployment names** - you'll use these in your code

**Checkpoint:** Your AI Foundry project is created and both models are deployed

---

## Part 4: Understanding Your Setup

**What you now have:**

```
┌─────────────────────────────────────────────────┐
│                 Azure Cloud                      │
│                                                  │
│  ┌──────────────────────┐  ┌─────────────────┐ │
│  │  DocumentDB Cluster   │  │  AI Foundry     │ │
│  │  Azure DocumentDB     │  │  Project        │ │
│  │                       │  │                 │ │
│  │  • Stores data        │  │  • Embeddings   │ │
│  │  • MongoDB queries    │  │  • Chat models  │ │
│  │  • Vector search      │  │  • AI tools     │ │
│  └──────────────────────┘  └─────────────────┘ │
│           ↓                          ↓           │
└───────────│──────────────────────────│───────────┘
            │                          │
            ↓                          ↓
   ┌────────────────────────────────────────┐
   │        Your VS Code Workspace           │
   │                                         │
   │  • DocumentDB extension                 │
   │  • Query playgrounds for queries        │
   │  • Python/Node.js code                  │
   │  • Integration with both services       │
   └────────────────────────────────────────┘
```

**Components:**

1. **Azure DocumentDB Cluster**
   - A MongoDB-compatible database
   - Stores your application data
   - Supports vector search for AI applications
   - Connects through the DocumentDB extension

2. **AI Foundry Project**
   - Hosts your AI models for embeddings and chat
   - Provides API endpoints for your code
   - Manages deployment and scaling
   - Supports building AI agents

3. **VS Code Workspace**
   - DocumentDB extension for database management
   - Query playgrounds for running queries
   - Code editor for Python and Node.js applications
   - One place to manage everything

**Next Steps in Training:**
- Module 2: Data modeling patterns with DocumentDB
- Module 3: Vector search for AI applications
- Module 4: Building AI agents with DocumentDB + Foundry
- Module 5: Industry use cases and patterns

---

## Quick Reference

### DocumentDB Connection String Format
```
mongodb+srv://<username>:<password>@<cluster>.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256
```

### Basic MongoDB Commands
```javascript
// Show databases
show dbs

// Switch database
use <dbname>

// Show collections
show collections

// Insert document
db.<collection>.insertOne({...})

// Find documents
db.<collection>.find({})

// Create index
db.<collection>.createIndex({field: 1})
```

### AI Foundry Endpoints
- **Portal:** https://ai.azure.com
- **Endpoint format:** `https://<resource>.openai.azure.com/`
- **API version:** Latest (check docs)

---

## Expected Outcomes

After completing this setup, you should have:

Azure DocumentDB cluster provisioned and running.
VS Code connected to DocumentDB with working queries.
AI Foundry project created with models deployed.
Test database with sample data in DocumentDB.
Connection details saved for both services.
Understanding of the infrastructure for AI and database applications.

**Skills gained:**
- Provisioning Azure DocumentDB (with MongoDB compatibility) clusters
- Configuring networking and firewall rules
- Using DocumentDB for VS Code extension
- Running MongoDB queries in playgrounds
- Deploying Azure OpenAI models
- Setting up AI Foundry projects

---

## Additional Resources

### Azure DocumentDB (with MongoDB compatibility)
- [Official Documentation](https://learn.microsoft.com/en-us/azure/documentdb)
- [MongoDB Compatibility](https://learn.microsoft.com/en-us/azure/documentdb/compatibility-query-language)
- [Pricing Calculator](https://azure.microsoft.com/en-us/pricing/details/cosmos-db/mongodb/)
- [Indexing Best Practices](https://learn.microsoft.com/en-us/azure/documentdb/how-to-create-indexes)
- [HA Best Practices](https://learn.microsoft.com/en-us/azure/documentdb/high-availability-replication-best-practices)
### VS Code Extensions
- [DocumentDB for VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-documentdb) - **Recommended**
- [Official Extension Guide](https://documentdb.io/docs/getting-started/vscode-extension-guide) - Complete documentation
- [VS Code Quick Start](https://documentdb.io/docs/getting-started/vscode-quickstart) - Quick setup guide
- [Extension Announcement Blog](https://devblogs.microsoft.com/cosmosdb/meet-the-documentdb-extension-for-vs-code-and-documentdb-local-a-fast-friendly-way-to-work-with-documentdb-locally-and-beyond/)

### AI Foundry
- [AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Model Catalog](https://learn.microsoft.com/azure/ai-studio/how-to/model-catalog-overview)
- [Deployment Guide](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource)

### MongoDB Resources
- MongoDB Query Language documentation
- Aggregation Framework documentation
- Online MongoDB courses available

---

## Next Module

**Module 2: Core Concepts & Data Modeling**
- NoSQL data modeling patterns
- Schema design for MongoDB
- Embedding vs referencing
- Indexing strategies
- Query optimization

**Prerequisites:** Complete this introduction module with a working DocumentDB and AI Foundry setup.

---

**Setup complete.** You now have a fully configured environment for building AI-powered applications with Azure DocumentDB and AI Foundry. You are ready to move on to data modeling.
