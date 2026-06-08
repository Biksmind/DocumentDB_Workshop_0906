# MongoDB to Azure DocumentDB Migration using VS Code Extension (DMS Based)

## Objective

In this exercise, we will migrate data from an existing MongoDB environment to Azure DocumentDB using the Azure DocumentDB Migration extension in Visual Studio Code.

We will perform:

1. Pre-Migration Assessment
2. Offline Migration
3. Online Migration
4. Application Cutover Validation

---

# Prerequisites

## MongoDB Source Connection

Connect to the MongoDB source using the following connection string:

```text
mongodb://readonly:drinkchaidaily123@20.71.118.158:27017/?directConnection=true
```

> Note: If credentials are not provided during the workshop, please obtain them from the workshop sponsors.

---

# Part 1: Connect to MongoDB using VS Code

1. Open Visual Studio Code.
2. Open the DocumentDB for VS Code Extension.
3. Create a new MongoDB connection using the provided connection string.
4. Verify that the MongoDB cluster appears in the Connections pane.

Once connected successfully, proceed to the migration workflow.

---

# Part 2: Pre-Migration Assessment

Before performing any migration, we will run a compatibility assessment against Azure DocumentDB.

## Launch Assessment

1. Right-click the MongoDB cluster.
2. Select **Data Migration**.
3. If prompted, install the **Azure DocumentDB Migration** extension.
4. After installation, select:

   **Pre-Migration Assessment for Azure DocumentDB**

---

## Validate Source Environment

1. Verify the MongoDB source connection.
2. Click **Run Validation**.
3. Wait for validation to complete.

---

## Create Assessment

1. Enter an Assessment Name.
2. Optionally specify:

   * Report Path
   * Log Path
3. Click **Start Assessment**.

The assessment process will analyze your MongoDB deployment and identify any potential compatibility considerations.

---

## Review Assessment Results

1. Open the completed assessment.
2. Download the assessment report.
3. Review:

   * Compatibility findings
   * Unsupported features
   * Migration recommendations

After reviewing the report, close the assessment window.

---

# Part 3: Offline Migration

Now we will perform a full offline migration.

## Create Migration Job

1. Right-click the MongoDB cluster again.

2. Select:

   **Migrate to Azure DocumentDB**

3. The Create Migration Job wizard will open.

---

## Configure Migration Job

### Migration Details

Provide:

* Migration Job Name
* Migration Mode: **Offline**
* Network Connectivity: **Public**

For this workshop we will use:

* Offline Migration
* Public Connectivity

> Source connection string is optional because the extension can use the existing connection.

Click **Next**.

---

## Configure Target Environment

Provide Azure DocumentDB target details:

* Subscription
* Resource Group
* Azure DocumentDB Cluster

Click **Next**.

---

## Configure Azure DMS

Migration uses Azure Database Migration Service (DMS).

If DMS already exists:

* Select the existing DMS instance.

Otherwise:

* Create a new DMS instance in the same subscription and resource group.

Click **Next**.

---

## Firewall Configuration

Update source and target firewall rules when prompted.

Ensure:

* MongoDB source is reachable
* Azure DocumentDB target is reachable

Click **Next**.

---

## Select Databases and Collections

Choose:

* Database(s)
* Collection(s)

Select the migration action.

Click **Start Migration**.

---

## Monitor Migration

Azure will provision migration resources in the background.

This may take several minutes.

Monitor the migration status.

Wait until the migration status becomes:

```text
Succeeded
```

---

## Validate Migrated Data

Connect to Azure DocumentDB and run:

```javascript
use <your_database_name>

db.getCollectionNames().forEach(function(c) {
    print(c + ": " + db.getCollection(c).countDocuments());
});
```

Verify collection counts between source and target.

---

# Part 4: Generate Live Workload

Before performing Online Migration, we will generate ongoing database activity.

## Launch Sample Application

Open:

```text
https://mongocsgen-app1.azurewebsites.net/
```

---

## Generate Activity

The workshop administrator will start the workload generator.

Participants should observe:

* Continuous inserts
* Updates
* Deletes
* Increasing document counts

This workload will help demonstrate Azure DMS change replication during Online Migration.

---

# Part 5: Online Migration

Repeat the migration steps performed earlier.

Navigate again to:

```text
MongoDB Cluster
→ Data Migration
→ Migrate to Azure DocumentDB
```

---

## Configure Online Migration

Provide:

* Migration Job Name
* Migration Mode: Online
* Network Connectivity: Public

Since DMS was already created during Offline Migration:

* Reuse the existing DMS instance.

Proceed through:

* Target Configuration
* Firewall Updates
* Database Selection
* Collection Selection

Start Migration.

---

## Monitor Migration Progress

You will observe the following migration states:

```text
Provisioning
```

↓

```text
Bulk Copy In Progress
```

↓

```text
Replication In Progress
```

↓

```text
Ready To Cutover
```

During Replication:

* New inserts are copied continuously.
* Updates are synchronized.
* Deletes are synchronized.

This keeps Azure DocumentDB in sync with the source MongoDB environment.

---

# Part 6: Cutover

Once migration reaches:

```text
Ready To Cutover
```

perform the following steps.

---

## Stop Application Workload

Before cutover:

1. Stop the workload generator.
2. Allow remaining changes to synchronize.

This ensures no new writes occur during final synchronization.

---

## Perform Cutover

Click:

```text
Cutover
```

Migration status will change through:

```text
Ready To Cutover
```

↓

```text
Completing
```

↓

```text
Succeeded
```

---

# Part 7: Final Data Validation

Run the same validation query against Azure DocumentDB:

```javascript
use <your_database_name>

db.getCollectionNames().forEach(function(c) {
    print(c + ": " + db.getCollection(c).countDocuments());
});
```

Verify:

* Collection counts match source.
* No pending replication items remain.
* Migration status is successful.

---

# Part 8: Application Migration Validation

One of the key benefits of Azure DocumentDB is MongoDB compatibility.

No application code changes are required.

---

## Test Application Connectivity

Update only the application connection string.

### Before

```text
MongoDB Connection String
```

### After

```text
Azure DocumentDB Connection String
```

No code modifications are necessary.

---

## Verify Application Functionality

Perform the following operations:

* Create Records
* Read Records
* Update Records
* Delete Records

Observe that the application continues to function normally against Azure DocumentDB.

---

# Expected Outcome

At the end of this lab, you will have successfully:

✅ Assessed MongoDB compatibility

✅ Performed Offline Migration

✅ Performed Online Migration

✅ Executed Production Cutover

✅ Validated Data Consistency

✅ Connected Existing MongoDB Application to Azure DocumentDB

✅ Verified Application Functionality without Code Changes

This demonstrates a complete MongoDB to Azure DocumentDB migration workflow using Azure Database Migration Service (DMS) and the Azure DocumentDB VS Code Migration Extension.
