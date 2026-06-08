# Workshop runbook

Follow this file during the workshop. The commands are written so you can copy and paste them directly.

If you are new to Azure DocumentDB, keep this file open in one window and VS Code or Azure Portal open in another window.

## What you are building

The lab uses a mobile shopping scenario.

You will:

1. Prepare your local Python environment.
2. Add your Azure DocumentDB values to `.env`.
3. Verify pre-generated embedding files.
4. Load the catalog into Azure DocumentDB.
5. Create indexes.
6. Run normal queries, full-text search, and vector search.
7. Start a small AI agent app.

## Before you start

Make sure these are ready:

- Azure DocumentDB cluster, M30 or higher.
- Optional: Azure OpenAI deployment only if you plan to run AI agents or support app vector/hybrid mode.
- Python 3.10 or later.
- VS Code.
- MongoDB Shell (`mongosh`).
- Git.

If you have not created the Azure resources yet, complete [Module 1](1-Introduction/README.md) first.

## 1. Open the repository folder

Open PowerShell.

Go to the folder where you cloned this repo. Example:

```powershell
cd C:\Users\<your-user>\source\repos\DocumentDB-Workshop
```

Check that you are in the right folder:

```powershell
Get-ChildItem
```

You should see files and folders like:

```text
README.md
WORKSHOP-RUNBOOK.md
1-Introduction
2-NoSQL-Core-Concepts
3-AI-Vector-Search
4-AI-Agents
scripts
```

If you do not see these files, you are in the wrong folder.

## 2. Create the Python environment

Run these commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You should see `(.venv)` at the beginning of your PowerShell prompt after activation.

If PowerShell blocks activation, run this command and then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. Create the `.env` file

Run:

```powershell
Copy-Item .env.template .env
notepad .env
```

Notepad opens the `.env` file.

Replace the placeholder values with your real values:

```text
DOCUMENTDB_CONNECTION_STRING=<your DocumentDB connection string>
DOCUMENTDB_DATABASE=Workshop_DB
AZURE_OPENAI_ENDPOINT=<optional: required for AI agents and support app vector mode>
AZURE_OPENAI_API_KEY=<optional: required for AI agents and support app vector mode>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
EMBEDDING_DIMENSIONS=256
```

Do not add quotes around the values.

When done:

1. Click **File**.
2. Click **Save**.
3. Close Notepad.

## 4. Check that `.env` is readable

Run:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DOCUMENTDB_DATABASE')); print(bool(os.getenv('DOCUMENTDB_CONNECTION_STRING')))"
```

You should see:

```text
Workshop_DB
True
```

If you see `None`, reopen `.env` and check that the file was saved in the repository root.

## 5. Verify pre-generated embeddings

Embedding files are already included in this workshop. You do not need to generate them.

Run:

```powershell
Get-ChildItem .\3-AI-Vector-Search\mobile-data\mobiles_with_vectors.json
Get-ChildItem .\3-AI-Vector-Search\mobile-data\query_embeddings.json
```

If both files are listed, continue.

Also confirm support embeddings:

```powershell
Get-ChildItem .\3-AI-Vector-Search\support-data\support_articles_with_vectors.json
```

If this step fails:

- Make sure the repository was cloned with all workshop files.
- Confirm the file paths are correct.

## 6. Load data into DocumentDB

Run:

```powershell
python .\scripts\load_workshop_data.py
```

The script loads:

- `mobiles`
- `retail_offers`

The script also creates the indexes used later in the workshop.

If this step fails with a network or timeout error:

- Go to your DocumentDB resource in Azure Portal.
- Click **Networking**.
- Add your current client IP.
- Click **Save**.
- Wait about 30 seconds.
- Run the command again.

## 7. Validate the setup

Run:

```powershell
python .\scripts\validate_workshop_setup.py
```

If everything is ready, you should see:

```text
Mobile workshop setup validation passed.
```

If validation fails, read the failed line carefully. Most failures mean the data load did not complete or the vector files were not generated.

## 8. Connect with `mongosh`

Open `.env`, copy the value of `DOCUMENTDB_CONNECTION_STRING`, and run:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`, run:

```javascript
use Workshop_DB
db.runCommand({ ping: 1 })
db.mobiles.countDocuments()
db.retail_offers.countDocuments()
db.mobiles.getIndexes()
```

You should see:

- `ping` returns `{ ok: 1 }`
- `db.mobiles.countDocuments()` returns `30`
- `db.retail_offers.countDocuments()` returns `30`
- `db.mobiles.getIndexes()` includes `mobile_text_index` and `vector_index`

## 9. Run a full-text search

Still inside `mongosh`, run:

```javascript
db.mobiles.find(
  { $text: { $search: "camera phone battery 5G" } },
  {
    score: { $meta: "textScore" },
    title: 1,
    brand: 1,
    segment: 1,
    priceInr: 1,
    rating: 1,
    _id: 0
  }
).sort({ score: { $meta: "textScore" } }).limit(5)
```

This is keyword search. It works best when the user gives words that appear in the catalog, such as `camera`, `battery`, `Samsung`, or `5G`.

## 10. Run a vector search

Open this file in VS Code:

```text
3-AI-Vector-Search\mobile-data\query_embeddings.json
```

Find the query:

```text
best camera phone for portraits and low light photography
```

Copy the full `embedding` array for that query.

In `mongosh`, paste it here:

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

This is semantic search. It does not only match words. It tries to find phones that match the meaning of the request.

## 11. Run a filtered vector search

Use the same `queryVector` from the previous step.

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

This query asks for semantic matches, but only for phones under INR 50,000.

## 12. Start the AI agents

Go back to PowerShell.

If you are still inside `mongosh`, type:

```javascript
exit
```

Then run:

```powershell
cd .\4-AI-Agents\mobile-agents
python app.py
```

The browser should open automatically. If it does not, open this URL manually:

```text
http://localhost:8080
```

You should see two agents:

- `MobileAdvisor`
- `RetailOfferFinder`

Try these prompts:

```text
Recommend a phone under 50000 for camera and battery
```

```text
I need a gaming phone with fast charging
```

```text
Tell me about Samsung Galaxy S24 Ultra
```

```text
Where can I buy OnePlus 12?
```

```text
What mobiles are available from Flipkart?
```

## 13. Stop the app

Go to the PowerShell window where `python app.py` is running.

Press:

```text
Ctrl+C
```

If you want to return to the repository root, run:

```powershell
cd ..\..
```

Deactivate the Python environment:

```powershell
deactivate
```

## 14. Cleanup

After the workshop:

1. Delete or scale down Azure resources you no longer need.
2. Remove temporary firewall rules.
3. Do not commit `.env`.
4. Rotate keys if they were shared during a live session.

## If you get stuck

Start with these checks:

```powershell
python --version
mongosh --version
Get-Content .env
python .\scripts\validate_workshop_setup.py
```

Do not paste secrets into chat or screenshots. If you need help, share only the error message, not your connection string or API key.
