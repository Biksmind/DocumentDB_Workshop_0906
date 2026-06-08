# Azure DocumentDB Workshop Participant Guide

## Workshop Overview

In this workshop, you will provision Azure DocumentDB, connect using VS Code, load sample data, explore full-text and vector search capabilities, run AI-powered agents, and review performance and security best practices.

## Learning Objectives

By the end of this workshop, you will be able to:

- Deploy an Azure DocumentDB cluster
- Connect to Azure DocumentDB using VS Code
- Load and validate workshop datasets
- Execute document queries
- Perform full-text and vector searches
- Explore AI-powered agent scenarios
- Review performance optimization techniques
- Apply security best practices

---

## What you will build

You will build a mobile shopping assistant using Azure DocumentDB with pre-generated workshop embeddings and sample data.

The workshop flow is:

```text
Create Azure resources
  -> connect from VS Code
  -> prepare local Python environment
   -> verify pre-generated embedding files
  -> load mobile catalog data
  -> run basic queries
  -> run full-text search
  -> run vector search
  -> run AI agents
  -> review performance and security
  -> cleanup
```

## Module 1: Create Azure DocumentDB

### 1. Open Azure Portal

1. Open a browser.
2. Go to:

   ```text
   https://portal.azure.com
   ```

3. Sign in with your Azure account.
4. Wait until the Azure Portal home page is fully loaded.

### 2. Create a resource group

If you already have a workshop resource group, you can use it. Otherwise:

1. In the top search bar, type:

   ```text
   Resource groups
   ```

2. Click **Resource groups**.
3. Click **Create**.
4. Select your **Subscription**.
5. For **Resource group name**, enter:

   ```text
   rg-az-documentdb-workshop
   ```

6. Select a region close to you.
7. Click **Review + create**.
8. Click **Create**.

### 3. Create the Azure DocumentDB cluster

1. In Azure Portal, use the top search bar.
2. Type:

   ```text
   Azure DocumentDB
   ```

3. Click **Azure DocumentDB** from the search results.
4. Click **Create**.
5. If the portal shows multiple options, choose **Azure DocumentDB** or **Azure DocumentDB with MongoDB compatibility**.
6. Fill in the Basics page:

   | Field | Value |
   |---|---|
   | Subscription | Select your subscription |
   | Resource group | `rg-az-documentdb-workshop` |
   | Cluster name | Use a globally unique name, for example `az-docdb-workshop-<yourname>` |
   | Region | Choose a region close to you |
   | MongoDB version | Latest available version |
   | High availability | Disabled for the workshop |
   | Cluster tier | M30 or higher |
   | Storage | Default value |

7. Click **Review + create**.
8. Wait for validation to pass.
9. Click **Create**.
10. Wait for deployment to complete. This can take 10-15 minutes.
11. When deployment is complete, click **Go to resource**.

### 4. Configure networking

1. In the DocumentDB resource page, look at the left navigation.
2. Under **Settings**, click **Networking**.
3. Select the option that allows access from selected IP addresses.
4. Click **+ Add current client IP address**.
5. Confirm your IP address appears in the allowed list.
6. Click **Save**.
7. Wait until the save operation completes.

Do not use a broad IP range such as `0.0.0.0 - 255.255.255.255` unless the instructor explicitly asks you to do it for a temporary lab.

### 5. Copy the connection string

1. In the DocumentDB resource left navigation, under **Settings**, click **Connection strings**.
2. Find the primary or global read-write connection string.
3. Click the copy icon.
4. Paste it into a temporary local note. You will use it later in `.env`.

The connection string looks similar to this:

```text
mongodb+srv://<username>:<password>@<cluster-name>.mongocluster.cosmos.azure.com/?tls=true
```

Do not share the real connection string in screenshots, chat, or slides.

## Module 1: Connect from VS Code

### 1. Install VS Code extension

1. Open **VS Code**.
2. On the left Activity Bar, click **Extensions**.
3. In the search box, type:

   ```text
   DocumentDB for VS Code
   ```

4. Click the Microsoft DocumentDB extension.
5. Click **Install**.
6. If VS Code asks you to reload, click **Reload**.

### 2. Add the DocumentDB connection

1. In VS Code, click the **DocumentDB** icon on the left Activity Bar.
2. Click **Add New Connection**.
3. Select **Connection String**.
4. Paste the DocumentDB connection string.
5. If your connection string does not already include the auth mechanism, add it so the end looks like this:

   ```text
   ?tls=true&authMechanism=SCRAM-SHA-256
   ```

6. Press **Enter**.
7. Wait a few seconds.
8. The cluster should appear in the DocumentDB panel.

### 3. Create the workshop database

1. In the DocumentDB panel, find your cluster.
2. Right-click the cluster.
3. Click **Create Database...**.
4. Enter:

   ```text
   Workshop_DB
   ```

5. Press **Enter**.
6. Right-click the cluster again.
7. Click **Refresh**.
8. Expand the cluster and confirm `Workshop_DB` is visible.

### 4. Verify the connection

1. Right-click **Workshop_DB**.
2. Click **New Query Playground**.
3. Paste this:

   ```javascript
   use('Workshop_DB')
   db.runCommand({ ping: 1 })
   show collections
   db.stats()
   ```

4. Click **Run** above the code block.
5. Confirm the ping output contains:

   ```json
   { "ok": 1 }
   ```

### 5. Import sample documents

The `sample-docs` folder contains small representative JSON files for each collection. Import them now to confirm the database accepts data before you set up the full Python environment in Module 2.

The folder contains:

| File | Collection | Documents |
|---|---|---|
| `sample-docs\mobiles_sample.json` | `mobiles` | 30 mobile phones across Budget, Mid Range, Premium, Foldable, and Gaming segments |
| `sample-docs\support_articles_sample.json` | `support_articles` | 30 knowledge-base articles covering Battery, Camera, Connectivity, Bluetooth, Payments, and more |
| `sample-docs\retail_offers_sample.json` | `retail_offers` | 30 phones with retailer offer details |

#### Step 1: Create the collections

1. In the Query Playground, run the following commands to create the collections:

```javascript
use Workshop_DB

db.createCollection("mobiles")
db.createCollection("support_articles")
db.createCollection("retail_offers")
```

2. Verify the collections are created by running:

```javascript
show collections
```

#### Step 2: Import sample documents

#### Option A: mongosh (quickest)


```javascript
use Workshop_DB

db.mobiles.insertMany([ /* paste contents of mobiles_sample.json here */ ])
db.support_articles.insertMany([ [
  {
    "articleId": "KB001",
    "title": "Battery drains quickly after software update",
    "product": "Mobile OS",
    "category": "Battery",
    "severity": "Medium",
    "content": "After a software update, background sync and app re-indexing can temporarily increase battery usage. Ask the user to restart the phone, check battery usage by app, disable unused background refresh, and install pending app updates.",
    "tags": ["battery", "software update", "background sync", "power usage"]
  },
  {
    "articleId": "KB002",
    "title": "Phone charges slowly with fast charger",
    "product": "Mobile Hardware",
    "category": "Charging",
    "severity": "Medium",
    "content": "Slow charging can happen when the cable does not support fast charging, the adapter wattage is too low, or the charging port has dust. Ask the user to test a certified cable, clean the port carefully, and verify fast charging is enabled.",
    "tags": ["charging", "fast charging", "cable", "adapter"]
  },
  {
    "articleId": "KB003",
    "title": "5G signal drops indoors",
    "product": "Network",
    "category": "Connectivity",
    "severity": "Low",
    "content": "5G coverage can drop indoors because high-frequency bands are blocked by walls. Ask the user to check carrier coverage, switch airplane mode on and off, update carrier settings, and test LTE fallback.",
    "tags": ["5G", "network", "signal", "connectivity"]
  },
  {
    "articleId": "KB004",
    "title": "Camera photos look blurry in low light",
    "product": "Camera",
    "category": "Camera",
    "severity": "Low",
    "content": "Blurry low-light photos are often caused by motion, dirty lenses, or aggressive digital zoom. Ask the user to clean the lens, hold the phone steady, use night mode, and avoid zooming in dark scenes.",
    "tags": ["camera", "low light", "photos", "night mode"]
  },
  {
    "articleId": "KB005",
    "title": "Apps crash after opening",
    "product": "Mobile Apps",
    "category": "Apps",
    "severity": "High",
    "content": "App crashes can be caused by corrupted cache, incompatible app versions, or low storage. Ask the user to update the app, clear cache, restart the phone, and check available storage.",
    "tags": ["apps", "crash", "cache", "storage"]
  },
  {
    "articleId": "KB006",
    "title": "Phone heats up during gaming",
    "product": "Mobile Hardware",
    "category": "Performance",
    "severity": "Medium",
    "content": "Gaming can heat the device because CPU, GPU, display, and network are active together. Ask the user to lower graphics settings, close background apps, remove thick cases, and avoid charging while gaming.",
    "tags": ["gaming", "heating", "performance", "thermal"]
  },
  {
    "articleId": "KB007",
    "title": "Fingerprint unlock is not working",
    "product": "Security",
    "category": "Authentication",
    "severity": "Medium",
    "content": "Fingerprint unlock can fail because of wet fingers, screen protector issues, or corrupted biometric data. Ask the user to clean the sensor, remove and re-add fingerprints, and check for software updates.",
    "tags": ["fingerprint", "unlock", "biometric", "security"]
  },
  {
    "articleId": "KB008",
    "title": "Face unlock fails in dark room",
    "product": "Security",
    "category": "Authentication",
    "severity": "Low",
    "content": "Face unlock may fail in low light if the device relies on the front camera. Ask the user to improve lighting, clean the front camera area, re-enroll face data, or use PIN/fingerprint fallback.",
    "tags": ["face unlock", "low light", "authentication", "camera"]
  },
  {
    "articleId": "KB009",
    "title": "Wi-Fi connects but internet does not work",
    "product": "Network",
    "category": "Connectivity",
    "severity": "High",
    "content": "If Wi-Fi connects but internet is unavailable, the issue may be DNS, router, captive portal, or IP conflict. Ask the user to forget and reconnect to Wi-Fi, restart router, test another network, and reset network settings.",
    "tags": ["wifi", "internet", "router", "dns"]
  },
  {
    "articleId": "KB010",
    "title": "Bluetooth earbuds disconnect frequently",
    "product": "Accessories",
    "category": "Bluetooth",
    "severity": "Medium",
    "content": "Frequent Bluetooth disconnections may be caused by low earbud battery, interference, old firmware, or pairing corruption. Ask the user to charge earbuds, forget and re-pair, update firmware, and test away from interference.",
    "tags": ["bluetooth", "earbuds", "disconnect", "pairing"]
  },
  {
    "articleId": "KB011",
    "title": "Storage is full and phone is slow",
    "product": "Mobile OS",
    "category": "Storage",
    "severity": "Medium",
    "content": "Low storage can slow the phone and cause app failures. Ask the user to delete large videos, move photos to cloud storage, clear app cache, uninstall unused apps, and keep at least 10 percent storage free.",
    "tags": ["storage", "slow phone", "cache", "cleanup"]
  },
  {
    "articleId": "KB012",
    "title": "Mobile data works but hotspot fails",
    "product": "Network",
    "category": "Hotspot",
    "severity": "Medium",
    "content": "Hotspot may fail because of carrier restrictions, data saver, incorrect APN, or device limit. Ask the user to check hotspot plan support, disable data saver, restart the phone, and verify APN settings.",
    "tags": ["hotspot", "mobile data", "carrier", "apn"]
  },
  {
    "articleId": "KB013",
    "title": "Notifications are delayed",
    "product": "Mobile Apps",
    "category": "Notifications",
    "severity": "Low",
    "content": "Delayed notifications are often caused by battery optimization, data saver, or background restrictions. Ask the user to allow background activity, disable battery optimization for the app, and check notification permissions.",
    "tags": ["notifications", "battery optimization", "background activity", "permissions"]
  },
  {
    "articleId": "KB014",
    "title": "Phone cannot install system update",
    "product": "Mobile OS",
    "category": "Updates",
    "severity": "Medium",
    "content": "System update installation can fail because of low battery, low storage, unstable Wi-Fi, or interrupted downloads. Ask the user to charge above 50 percent, free storage, use stable Wi-Fi, and retry the update.",
    "tags": ["system update", "install failure", "storage", "wifi"]
  },
  {
    "articleId": "KB015",
    "title": "Call audio is not clear",
    "product": "Voice",
    "category": "Calls",
    "severity": "High",
    "content": "Poor call audio can be caused by network signal, blocked microphone, Bluetooth routing, or carrier issues. Ask the user to test speaker mode, clean microphone area, disconnect Bluetooth, and try another location.",
    "tags": ["calls", "audio", "microphone", "network"]
  },
  {
    "articleId": "KB016",
    "title": "Screen touch is not responding properly",
    "product": "Display",
    "category": "Touch",
    "severity": "High",
    "content": "Touch issues can be caused by screen protectors, moisture, software freezes, or hardware damage. Ask the user to clean the screen, remove thick screen protectors, restart the phone, and test safe mode.",
    "tags": ["touch", "screen", "display", "safe mode"]
  },
  {
    "articleId": "KB017",
    "title": "GPS location is inaccurate",
    "product": "Location",
    "category": "GPS",
    "severity": "Low",
    "content": "Location accuracy can be affected by indoor use, battery saver, denied permissions, or poor satellite visibility. Ask the user to enable high accuracy mode, check app permissions, and test outdoors.",
    "tags": ["gps", "location", "permissions", "battery saver"]
  },
  {
    "articleId": "KB018",
    "title": "Payment app fails during checkout",
    "product": "Payments",
    "category": "Payments",
    "severity": "High",
    "content": "Payment failures can be caused by outdated app versions, network issues, disabled NFC, or bank authentication failures. Ask the user to update the app, check network, enable NFC, and retry bank verification.",
    "tags": ["payments", "checkout", "nfc", "bank authentication"]
  },
  {
    "articleId": "KB019",
    "title": "Phone speaker volume is too low",
    "product": "Mobile Hardware",
    "category": "Audio",
    "severity": "Low",
    "content": "Low speaker volume can be caused by dirt in the speaker grille, software volume limits, or Do Not Disturb mode. Ask the user to clean the grille gently, check volume settings, disable DND, and test with headphones to isolate the issue.",
    "tags": ["speaker", "volume", "audio", "do not disturb"]
  },
  {
    "articleId": "KB020",
    "title": "App does not open after install",
    "product": "Mobile Apps",
    "category": "Apps",
    "severity": "Medium",
    "content": "An app that fails to open after installation may have a corrupted download, missing permissions, or incompatible OS version. Ask the user to uninstall and reinstall the app, grant all required permissions, and verify the OS version meets requirements.",
    "tags": ["app install", "permissions", "crash", "os version"]
  },
  {
    "articleId": "KB021",
    "title": "Phone restarts randomly",
    "product": "Mobile OS",
    "category": "Stability",
    "severity": "High",
    "content": "Random restarts can be caused by a faulty app, overheating, low battery health, or a software bug. Ask the user to boot in safe mode to isolate apps, check battery health, and update the OS.",
    "tags": ["restart", "crash", "battery health", "safe mode"]
  },
  {
    "articleId": "KB022",
    "title": "SIM card not detected",
    "product": "Mobile Hardware",
    "category": "SIM",
    "severity": "High",
    "content": "A SIM not detected error may be caused by a loose SIM tray, dirty contacts, or a network issue. Ask the user to re-seat the SIM, clean the tray contacts, test another SIM if available, and check with the carrier.",
    "tags": ["sim", "no signal", "hardware", "carrier"]
  },
  {
    "articleId": "KB023",
    "title": "Screen brightness does not adjust automatically",
    "product": "Display",
    "category": "Display",
    "severity": "Low",
    "content": "Auto-brightness relies on the ambient light sensor. It can fail if the sensor is covered, disabled, or the display calibration is off. Ask the user to uncover the sensor area, enable adaptive brightness, and recalibrate the display.",
    "tags": ["brightness", "auto brightness", "ambient light sensor", "display"]
  },
  {
    "articleId": "KB024",
    "title": "Mobile gets very hot while charging",
    "product": "Mobile Hardware",
    "category": "Charging",
    "severity": "Medium",
    "content": "Excessive heat during charging can happen when using a non-certified charger, charging on a soft surface, or using the phone heavily while charging. Ask the user to use the original charger, charge on a hard flat surface, and avoid using the phone while charging.",
    "tags": ["charging", "heating", "thermal", "charger"]
  },
  {
    "articleId": "KB025",
    "title": "Calls drop in the middle of a conversation",
    "product": "Network",
    "category": "Calls",
    "severity": "High",
    "content": "Call drops are usually caused by poor signal, VoLTE issues, or SIM problems. Ask the user to check signal strength, enable VoLTE if available, re-seat the SIM, and contact the carrier if the problem persists.",
    "tags": ["call drop", "signal", "volte", "sim"]
  },
  {
    "articleId": "KB026",
    "title": "Wireless charging is not working",
    "product": "Mobile Hardware",
    "category": "Charging",
    "severity": "Low",
    "content": "Wireless charging can fail if the phone is misaligned on the pad, a thick case is blocking the coil, or wireless charging is disabled. Ask the user to remove the case, center the phone on the pad, and ensure wireless charging is turned on.",
    "tags": ["wireless charging", "qi", "case", "charging pad"]
  },
  {
    "articleId": "KB027",
    "title": "App draining battery in background",
    "product": "Mobile Apps",
    "category": "Battery",
    "severity": "Medium",
    "content": "Background apps can drain battery by running location, sync, or refresh tasks. Ask the user to check battery usage stats, restrict background activity for the offending app, and consider disabling location access when not needed.",
    "tags": ["battery drain", "background app", "location", "battery optimization"]
  },
  {
    "articleId": "KB028",
    "title": "Phone microphone not working during video calls",
    "product": "Mobile Hardware",
    "category": "Audio",
    "severity": "High",
    "content": "If the microphone works for regular calls but not video calls, the issue is likely app-level permission. Ask the user to check microphone permission for the video call app, restart the app, and test with another video call app to confirm.",
    "tags": ["microphone", "video call", "permissions", "audio"]
  },
  {
    "articleId": "KB029",
    "title": "Display colors look washed out",
    "product": "Display",
    "category": "Display",
    "severity": "Low",
    "content": "Washed-out colors can occur when reading mode, night mode, or a low-saturation color profile is active. Ask the user to disable reading mode, check display color settings, and reset the color profile to the default vivid or natural mode.",
    "tags": ["display", "colors", "reading mode", "night mode"]
  },
  {
    "articleId": "KB030",
    "title": "Phone does not vibrate for notifications",
    "product": "Mobile OS",
    "category": "Notifications",
    "severity": "Low",
    "content": "Missing vibration for notifications can be caused by vibration intensity set to zero, Do Not Disturb mode, or per-app notification settings. Ask the user to check vibration intensity, disable DND, and verify notification vibration is enabled for the specific app.",
    "tags": ["vibration", "notifications", "do not disturb", "haptics"]
  }
]
 ])
db.retail_offers.insertMany([ /* paste contents of retail_offers_sample.json here */ ])
```


#### Option B: VS Code DocumentDB extension

1. In VS Code, click the **DocumentDB** icon in the Activity Bar.
2. In the DocumentDB explorer, expand your connected cluster.
3. Expand **Databases** and click **Workshop_DB** to select the workshop database.
4. Expand **Workshop_DB** so you can see the collections created in Step 1:
  - `mobiles`
  - `support_articles`
  - `retail_offers`

5. Import records into `support_articles`:
  - Right-click **support_articles**.
  - Click **Import Documents...**.
  - Select `sample-docs\support_articles_sample.json`.
6. Import records into `retail_offers`:
  - Right-click **retail_offers**.
  - Click **Import Documents...**.
  - Select `sample-docs\retail_offers_sample.json`.
7. Right-click **Workshop_DB** and click **Refresh**.

#### Verify the import

In `mongosh`:

```javascript
use Workshop_DB
db.mobiles.countDocuments()           // expect 30
db.support_articles.countDocuments()  // expect 30
db.retail_offers.countDocuments()     // expect 30
```

You should see 30 documents in each collection.

> **Note:** The sample documents match the complete workshop dataset (30 mobiles, 30 support articles, 30 retail offers). You can skip the Module 3 data load script if you have already imported these files. If you run the script anyway, it will re-insert documents and may create duplicates.
>
> To avoid duplicates, drop these collections before running the full load:
>
> ```javascript
> use Workshop_DB
> db.mobiles.drop()
> db.support_articles.drop()
> db.retail_offers.drop()
> ```

## Module 2: Prepare local environment

### 1. Open PowerShell/Terminal

Open PowerShell and go to the folder where you cloned this repository.

Example:

```powershell
cd C:\Users\<your-user>\source\repos\DocumentDB-Workshop
```

Check that you are in the right folder:

```powershell
Get-ChildItem
```

You should see:

```text
README.md
WORKSHOP-RUNBOOK.md
1-Introduction
2-NoSQL-Core-Concepts
3-AI-Vector-Search
4-AI-Agents
5-Performance-and-Cost-Optimization
6-Security-RBAC
scripts
```

### 2. Create Python virtual environment

Run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You should see `(.venv)` at the beginning of your PowerShell prompt.

If activation is blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Create `.env`

Run:

```powershell
Copy-Item .env.template .env
notepad .env
```

Fill in the values:

```text
DOCUMENTDB_CONNECTION_STRING=<paste your DocumentDB connection string>
DOCUMENTDB_DATABASE=Workshop_DB
AZURE_OPENAI_ENDPOINT=<optional: required for Module 4 agents and support app vector mode>
AZURE_OPENAI_API_KEY=<optional: required for Module 4 agents and support app vector mode>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
EMBEDDING_DIMENSIONS=256
```

Important:

- Do not add quotes around values.
- Do not add spaces before or after `=`.
- Save the file before closing Notepad.
- Do not commit `.env`.

### 4. Check `.env`

Run:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DOCUMENTDB_DATABASE')); print(os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT'))"
```

Expected output:

```text
Workshop_DB
gpt-4.1-mini
```

If you see `None`, the `.env` file is missing, not saved, or not in the repository root.

## Module 2: Basic DocumentDB checks

Install `mongosh` if you have not already installed it.

Windows:

```powershell
winget install MongoDB.Shell
```

Check:

```powershell
mongosh --version
```

Connect:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`, run:

```javascript
use Workshop_DB
db.runCommand({ ping: 1 })
```

You should see `{ ok: 1 }`.

Exit `mongosh` for now:

```javascript
exit
```

## Module 3: Use pre-generated embeddings

Embedding files are already included in this workshop. You do not need to generate them.

From the repository root, confirm the files exist:

```powershell
Get-ChildItem .\3-AI-Vector-Search\mobile-data\mobiles_with_vectors.json
Get-ChildItem .\3-AI-Vector-Search\mobile-data\query_embeddings.json
Get-ChildItem .\3-AI-Vector-Search\support-data\support_articles_with_vectors.json
```

If all three files are present, continue to data load.

## Module 3: Load data and create indexes

Run:

```powershell
python .\scripts\load_workshop_data.py
```

The script loads:

- `mobiles`
- `support_articles`
- `retail_offers`

The script creates:

- `mobile_text_index`
- `vector_index`
- `support_text_index`
- `support_vector_index`
- `mobile_brand_index`
- `mobile_segment_index`
- `mobile_price_index`
- `offer_title_index`
- `offer_retailer_index`

If this fails with a network or timeout error:

1. Go to Azure Portal.
2. Open your DocumentDB resource.
3. Click **Networking**.
4. Click **+ Add current client IP address**.
5. Click **Save**.
6. Wait 30 seconds.
7. Run the script again.

Validate:

```powershell
python .\scripts\validate_workshop_setup.py
```

Expected:

```text
Workshop setup validation passed.
```

## Module 3: Run full-text search

Connect again:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`:

```javascript
// Switch to the workshop database.
use Workshop_DB

// Full-text search on mobiles using the text index.
// $search contains keywords. MongoDB scores results by relevance.
db.mobiles.find(
  { $text: { $search: "camera phone battery 5G" } },
  {
    // Include text relevance score in output.
    score: { $meta: "textScore" },
    // Return only useful fields for quick inspection.
    title: 1,
    brand: 1,
    segment: 1,
    priceInr: 1,
    rating: 1,
    // Hide internal ObjectId for cleaner output.
    _id: 0
  }
// Sort by text relevance (highest first), return top 5 only.
).sort({ score: { $meta: "textScore" } }).limit(5)
```

If you get `MongoServerError[IndexNotFound]: A text index is necessary to perform a $text query`, create the text indexes once and re-run the query:

```javascript
// Create text index for mobiles (required for db.mobiles.find({ $text: ... })).
db.mobiles.createIndex(
  {
    title: "text",
    brand: "text",
    segment: "text",
    description: "text",
    features: "text",
    useCases: "text"
  },
  { name: "mobile_text_index" }
)

// Create text index for support articles (required for db.support_articles.find({ $text: ... })).
db.support_articles.createIndex(
  {
    title: "text",
    product: "text",
    category: "text",
    content: "text",
    tags: "text"
  },
  { name: "support_text_index" }
)
```

**This is keyword search.**

**Find phones with "camera" in features**

db.mobiles.find(
  {
    features: /camera/i
  },
  {
    _id: 0,
    title: 1,
    features: 1
  }
)


Now suppose you want "camera + battery + 5G"

db.mobiles.find({
  $and: [
    {
      $or: [
        { description: /camera/i },
        { features: /camera/i },
        { useCases: /camera/i }
      ]
    },
    {
      $or: [
        { description: /battery/i },
        { features: /battery/i },
        { useCases: /battery/i }
      ]
    },
    {
      connectivity: "5G"
    }
  ]
},
{
  _id: 0,
  title: 1,
  brand: 1
})


Run the same type of query on support articles:

```javascript
// Full-text search on support articles.
db.support_articles.find(
  { $text: { $search: "battery update" } },
  {
    // Relevance score for each article.
    score: { $meta: "textScore" },
    // Keep output compact and support-focused.
    articleId: 1,
    title: 1,
    category: 1,
    severity: 1,
    _id: 0
  }
// Sort by relevance and keep top 5.
).sort({ score: { $meta: "textScore" } }).limit(5)
```

## Module 3: Try search in a web page

The `mongosh` query proves the database search works. Now run a side-by-side comparison of:

1. Keyword search (exact word or regex style)
2. Full-text search (`$text` index + relevance score)
3. Vector search (semantic meaning)

Use the same user intent so the difference is easy to explain.

### Step A: Keyword search baseline in mongosh

Use this query first as a baseline. It matches literal words in the `content` field and does not use text relevance scoring.

```javascript
// Keyword baseline: regex/contains style matching.
// This checks whether "battery" OR "update" appears in content.
db.support_articles.find(
  {
    $or: [
      { content: /battery/i },
      { content: /update/i }
    ]
  },
  {
    _id: 0,
    articleId: 1,
    title: 1,
    category: 1,
    severity: 1
  }
).limit(5)
```

### Step B: Full-text, Vector, and Hybrid in the support web app

Now use the support web app to compare ranked search modes with the same intent.

The app supports three modes:

| Mode | What it does |
|---|---|
| Full-text | Uses the DocumentDB text index and keyword matching |
| Vector | Generates an embedding for your query and uses vector search |
| Hybrid | Runs full-text and vector search, then combines the results |

Open a new PowerShell window from the repository root. If your virtual environment is not active, activate it:

```powershell
# Activate workshop virtual environment so dependencies are available.
.\.venv\Scripts\Activate.ps1
```

Start the web app:

```powershell
# Start local support-search web app (runs on port 5050).
python .\3-AI-Vector-Search\support-search-app\app.py
```

The browser should open automatically. If it does not, open:

```text
http://localhost:5050
```

If you removed Azure OpenAI configuration from `.env`, use only **Full-text** mode in this page.
Vector and Hybrid modes in this web app require runtime embedding generation through Azure OpenAI.
If Vector mode shows `Search failed: Connection error`, continue with the mongosh vector section below (`Run vector search`) using pre-generated embeddings from `query_embeddings.json`.

Use this comparison flow:

1. Search query:

```text
battery update
```

2. Run in **Full-text** mode first.
3. Switch to **Vector** mode and run the same query again.
4. Switch to **Hybrid** mode and run the same query again.

Then try this natural-language query that usually benefits vector search:

```text
my phone loses charge very fast after installing new version
```

Run it in all three modes again (Full-text -> Vector -> Hybrid).

Optional additional queries:

```text
wifi connected but internet not working
```

```text
bluetooth earbuds keep disconnecting
```

```text
phone heats up while gaming
```

```text
camera blurry in dark room
```

This support app is intentionally simpler than the mobile search app. It is designed to make the difference between full-text, vector, and hybrid search easier to explain.

What to notice:

- The page is using the `support_articles` collection.
- Keyword search (Step A) depends on literal word matches and usually has no relevance ranking.
- Full-text search works best when the exact issue words appear in the article and returns text relevance.
- Vector search works better when the user describes the issue in different words.
- Hybrid search is useful when you want both keyword precision and semantic matching in one result list.
- The cards show text, vector, or hybrid scores depending on the selected mode.

When you are done testing the page, go back to the PowerShell window where the app is running and press:

```text
Ctrl+C
```

## Module 3: Run vector search

In VS Code:

1. Open:

   ```text
   3-AI-Vector-Search\mobile-data\query_embeddings.json
   ```

2. Find:

   ```text
   best camera phone for portraits and low light photography
   ```

3. Copy the full `embedding` array.

In `mongosh`, paste the embedding array:

```javascript
const queryVector = [/* paste embedding array here */]
```

Then run:

```javascript
db.mobiles.aggregate([
  {
    $search: {
      cosmosSearch: {
        vector: queryVector,
        path: "contentVector",
        k: 5
      }
    }
  },
  {
    $project: {
      title: 1,
      brand: 1,
      segment: 1,
      priceInr: 1,
      rating: 1,
      cameraMp: 1,
      batteryMah: 1,
      score: { $meta: "searchScore" },
      _id: 0
    }
  }
])
```

## Module 3: Run filtered vector search

Use the same `queryVector`.

Run:

```javascript
db.mobiles.aggregate([
  {
    $search: {
      cosmosSearch: {
        vector: queryVector,
        path: "contentVector",
        k: 10,
        filter: {
          priceInr: { $lte: 50000 }
        }
      }
    }
  },
  {
    $project: {
      title: 1,
      brand: 1,
      priceInr: 1,
      rating: 1,
      score: { $meta: "searchScore" },
      _id: 0
    }
  }
])
```

Exit `mongosh`:

```javascript
exit
```

## Module 4: Run AI agents

From PowerShell, go to the mobile agents folder:

```powershell
cd .\4-AI-Agents\mobile-agents
python app.py
```

If the browser opens automatically, use it.

If not, open:

```text
http://localhost:8080
```

You should see two agents:

- `MobileAdvisor`
- `RetailOfferFinder`

### Test MobileAdvisor

1. Click **MobileAdvisor**.
2. Paste:

   ```text
   Recommend a phone under 50000 for camera and battery
   ```

3. Press **Enter**.
4. Try:

   ```text
   I need a gaming phone with fast charging
   ```

5. Try:

   ```text
   Tell me about Samsung Galaxy S24 Ultra
   ```

### Test RetailOfferFinder

1. Go back to the agent list.
2. Click **RetailOfferFinder**.
3. Paste:

   ```text
   Where can I buy OnePlus 12?
   ```

4. Press **Enter**.
5. Try:

   ```text
   What mobiles are available from Flipkart?
   ```

To stop the app, go to PowerShell and press:

```text
Ctrl+C
```

Return to the repository root:

```powershell
cd ..\..
```

## Module 5: Performance checks

This module demonstrates how indexes dramatically improve query performance using a dedicated `headsets` collection.

### 5.1 Create headsets collection

Connect with `mongosh` again:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`:

```javascript
use Workshop_DB
```

Create the `headsets` collection explicitly:

```javascript
// Create the headsets collection.
// This collection will hold 30 headsets across different categories.
db.createCollection("headsets")

// Verify the collection was created.
show collections
```

You should see `headsets` in the output.

### 5.2 Import headsets sample data

Now import the headset documents into the newly created collection.

**Option A: Direct import via mongosh**

```javascript
// Import 30 headsets for performance testing.
// This collection has brand, priceInr, type, and other fields.
// We will query it to demonstrate the impact of indexes.
db.headsets.insertMany([
  // Copy all 30 headsets from sample-docs\headsets_sample.json here
  // For quick import, use VS Code DocumentDB extension (see Option B below)
])

// Verify import.
db.headsets.countDocuments()  // expect 30
```

**Option B: Use VS Code DocumentDB extension (recommended)**

1. In the DocumentDB panel, expand **Workshop_DB**.
2. Right-click the **headsets** collection (now visible).
3. Click **Import Documents...**.
4. Select `sample-docs\headsets_sample.json`.
5. Wait for the import to complete.

Verify the import in mongosh:

```javascript
// Confirm 30 documents imported.
db.headsets.countDocuments()  // expect 30

// View a sample document.
db.headsets.findOne({}, { _id: 0 })
```

### 5.3 Demonstrate query performance WITHOUT an index

First, run a query **before creating an index** to see poor performance:

```javascript
// Query: Find all gaming headsets under 20000 INR.
// This query will perform a full collection scan (COLLSCAN) because no index exists.
db.headsets.find(
  {
    type: "Gaming Over-ear",
    priceInr: { $lte: 20000 }
  },
  {
    _id: 0,
    name: 1,
    brand: 1,
    type: 1,
    priceInr: 1,
    rating: 1
  }
)
```

Now check the **execution plan** to see the performance cost:

```javascript
// View the execution statistics BEFORE indexing.
// Look for "stage": "COLLSCAN" in the output — this means every document is scanned.
db.headsets.find(
  {
    type: "Gaming Over-ear",
    priceInr: { $lte: 20000 }
  }
).explain("executionStats")
```

**What to notice (WITHOUT index):**
- `executionStats.executionStages.stage` = `COLLSCAN` (full collection scan)
- `executionStats.totalDocsExamined` = ~30 (every document checked)
- `executionStats.executionStats.nReturned` = a few results (only 2 or 3 match the criteria)
- This is inefficient: the database scans ALL 30 documents to find a handful of matches.

### 5.4 Create a compound index

Now create an index on the fields used in the query:

```javascript
// Create a compound index on type and priceInr.
// This allows the database to jump directly to matching documents instead of scanning all.
db.headsets.createIndex(
  {
    type: 1,           // Field 1: type (ascending order)
    priceInr: 1        // Field 2: priceInr (ascending order)
  },
  { name: "headset_type_price_index" }
)
```

Verify the index was created:

```javascript
// List all indexes on the headsets collection.
db.headsets.getIndexes()
```

You should see:
- `_id_` (default)
- `headset_type_price_index` (newly created)

### 5.5 Demonstrate query performance WITH an index

Now run the **same query again** after creating the index:

```javascript
// Run the exact same query as before.
// This time, the database will use the index instead of scanning all documents.
db.headsets.find(
  {
    type: "Gaming Over-ear",
    priceInr: { $lte: 20000 }
  },
  {
    _id: 0,
    name: 1,
    brand: 1,
    type: 1,
    priceInr: 1,
    rating: 1
  }
)
```

Check the **execution plan** to see the improvement:

```javascript
// View the execution statistics AFTER indexing.
// Look for "stage": "IXSCAN" in the output — this means the index was used.
db.headsets.find(
  {
    type: "Gaming Over-ear",
    priceInr: { $lte: 20000 }
  }
).explain("executionStats")
```

**What to notice (WITH index):**
- `executionStats.executionStages.stage` = `IXSCAN` (index scan, not collection scan)
- `executionStats.totalDocsExamined` = ~4 (only relevant documents examined)
- `executionStats.nReturned` = ~4 (matches found)
- **Result: Much faster!** The database jumps to the index, finds matches, and returns them immediately.

### 5.6 Compare performance side-by-side

Run both queries and observe the difference:

```javascript
// Query 1: Complex price-based filter.
// With index, this scans only documents in the price range.
db.headsets.find(
  {
    priceInr: { $gte: 10000, $lte: 20000 }
  }
).explain("executionStats")

// Query 2: Multiple filter conditions.
// With index, both type and price conditions are resolved via the index.
db.headsets.find(
  {
    type: "Over-ear",
    noiseCancel: true,
    priceInr: { $lte: 30000 }
  }
).explain("executionStats")
```

### 5.7 Create additional indexes for other queries

Create indexes for other common filter patterns:

```javascript
// Index for brand searches.
db.headsets.createIndex(
  { brand: 1 },
  { name: "headset_brand_index" }
)

// Index for connectivity type searches.
db.headsets.createIndex(
  { connectivity: 1 },
  { name: "headset_connectivity_index" }
)

// Index for high-rated headsets (sorted by rating).
db.headsets.createIndex(
  { rating: -1 },
  { name: "headset_rating_index" }
)

// Verify all indexes.
db.headsets.getIndexes()
```

### 5.8 Run optimized queries with indexes

Now run queries that leverage the indexes:

```javascript
// Find premium headsets by Bose.
db.headsets.find(
  { brand: "Bose" },
  { _id: 0, name: 1, brand: 1, priceInr: 1, rating: 1 }
).explain("executionStats")

// Find highly-rated gaming headsets.
db.headsets.find(
  { type: "Gaming Over-ear", rating: { $gte: 4.5 } },
  { _id: 0, name: 1, type: 1, rating: 1, priceInr: 1 }
).explain("executionStats")

// Find wireless headsets sorted by price (highest first).
db.headsets.find(
  { connectivity: "Bluetooth 5.3" },
  { _id: 0, name: 1, connectivity: 1, priceInr: 1 }
).sort({ priceInr: -1 }).limit(5).explain("executionStats")
```

### 5.9 Key takeaways

| Aspect | WITHOUT Index | WITH Index |
|---|---|---|
| **Stage** | COLLSCAN | IXSCAN |
| **Docs Examined** | All (~30) | Only matching (~4) |
| **Speed** | Slower (scans all) | Faster (index lookup) |
| **Use Case** | One-time queries | Frequent queries |

**When to index:**
- Frequently queried fields (brand, type, price, rating)
- Filter conditions (`find({ brand: "X" })`)
- Sort operations (`.sort({ rating: -1 })`)
- Compound conditions (`type: "Gaming", priceInr: { $lte: 20000 }`)

**Exit mongosh:**

```javascript
exit
```

## Module 6: Security review

Before you finish, review these checks:

1. In Azure Portal, open the DocumentDB resource.
2. Click **Networking**.
3. Confirm you did not leave broad public IP ranges open.
4. If you added temporary broad access, remove it.
5. Click **Save** if you changed anything.
6. Check that `.env` is not committed:

   ```powershell
   git status --short
   ```

7. Confirm `.env` does not appear in the output.

For production, do not use the workshop admin connection string directly in application code. Use least-privilege access and store secrets in an approved secret store such as Azure Key Vault.

## Final cleanup

Stop local app if it is still running:

```text
Ctrl+C
```

Deactivate Python environment:

```powershell
deactivate
```

If you created Azure resources only for this workshop and no longer need them:

1. Open Azure Portal.
2. Search for **Resource groups**.
3. Open:

   ```text
   rg-az-documentdb-workshop
   ```

4. Review the resources.
5. If you are sure you no longer need them, click **Delete resource group**.
6. Follow the confirmation prompts.

Only delete the resource group if you are sure nothing important is inside it.

## Troubleshooting quick list

### `DOCUMENTDB_CONNECTION_STRING not set`

Open `.env` and confirm the value is present and saved.

### Authentication failed

Check the username/password in the DocumentDB connection string. Copy it again from Azure Portal if needed.

### Network timeout

Add your current IP address under DocumentDB **Networking**.

### Missing embedding files

Make sure these files exist before running data load:

- `3-AI-Vector-Search\mobile-data\mobiles_with_vectors.json`
- `3-AI-Vector-Search\mobile-data\query_embeddings.json`
- `3-AI-Vector-Search\support-data\support_articles_with_vectors.json`

### Vector index creation fails

Check:

- Cluster tier is M30 or higher.
- `EMBEDDING_DIMENSIONS=256`.
- `mobiles_with_vectors.json` exists.

### DevUI does not open

Open manually:

```text
http://localhost:8080
```

### Port 8080 already in use

Close the previous app instance or restart PowerShell and run `python app.py` again.
