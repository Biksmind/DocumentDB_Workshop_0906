# Azure DocumentDB Search Workshop - Deep Self Learning Guide

# Introduction

Modern applications store millions of records. Finding the right information quickly is a challenge.

Traditionally, databases relied on exact word matching. Today, AI-powered applications use semantic understanding to find information based on meaning rather than exact words.

In this lab, you will learn the evolution of search:

1. Keyword Search
2. Full Text Search
3. Vector Search
4. Why RAG applications use Vector Search

This guide is intentionally descriptive. After every exercise you will learn not only what happened, but why it happened.

---

# Module 1 - Create Sample Dataset

We will simulate a customer support system.

Create a collection named:

```javascript
supportInc
```

Insert the following data:

```javascript
db.supportInc.insertMany([
{
    _id: 1,
    ticketId: "SUP-1001",
    title: "Login failure after password reset",
    description: "User is unable to login after changing account password. Authentication keeps failing.",
    category: "Authentication",
    priority: "High"
},
{
    _id: 2,
    ticketId: "SUP-1002",
    title: "Storage quota exceeded during migration",
    description: "Database migration process stopped because available storage space was exhausted.",
    category: "Migration",
    priority: "Critical"
},
{
    _id: 3,
    ticketId: "SUP-1003",
    title: "Application timeout while uploading files",
    description: "Users experience connection timeout errors when transferring large documents.",
    category: "Networking",
    priority: "Medium"
},
{
    _id: 4,
    ticketId: "SUP-1004",
    title: "Email notifications not delivered",
    description: "System generated emails are not reaching customer inboxes due to mail delivery issues.",
    category: "Notifications",
    priority: "High"
},
{
    _id: 5,
    ticketId: "SUP-1005",
    title: "High CPU utilization on database server",
    description: "Database server is experiencing unusually high processor consumption during peak workload.",
    category: "Performance",
    priority: "Critical"
}
])
```

---

# Module 2 - Keyword Search

## What is Keyword Search?

Keyword Search is the simplest form of search.

The database looks for the exact text supplied by the user.

It does not understand:

- Meaning
- Context
- Synonyms
- Word variations

It simply compares characters.

Think of it as:

> "Find me documents containing exactly this word."

---

## Exercise 1

```javascript
db.supportInc.find({
  title: /login/i
})
```

Expected Result:

```text
SUP-1001
```

### Why did this work?

The document contains:

```text
Login failure after password reset
```

The query searched for:

```text
login
```

The exact word exists in the title.

Keyword Search performs direct pattern matching and therefore returns the document.

### Key Learning

Keyword Search works well when the user knows the exact word stored in the database.

---

## Exercise 2

```javascript
db.supportInc.find({
  title: /logins/i
})
```

Expected Result:

```text
[]
```

### Why did this fail?

The document contains:

```text
login
```

The query contains:

```text
logins
```

Humans understand that both words are related.

The database does not.

To the database:

```text
login != logins
```

Because the exact word is not present, no results are returned.

### Key Learning

Keyword Search compares text literally.

It does not understand grammar or language.

---

# Module 3 - Full Text Search

## What is Full Text Search?

Full Text Search is more intelligent than Keyword Search.

Instead of comparing raw text, it performs linguistic analysis.

Common capabilities:

- Tokenization
- Stemming
- Relevance Ranking

Full Text Search attempts to understand how words relate to each other.

However, it is still fundamentally a word-based search system.

---

## Create Full Text Index

```javascript
db.runCommand({
  createIndexes: "supportInc",
  indexes: [
    {
      key: {
        title: "text",
        description: "text"
      },
      name: "support_text_idx"
    }
  ]
})
```

---

## Exercise 3

```javascript
db.supportInc.find({
  $text: {
    $search: "logins"
  }
})
```

Expected Result:

```text
SUP-1001
```

### Why did this work?

Document:

```text
login
```

Query:

```text
logins
```

Full Text Search analyzes language.

Internally it recognizes that:

```text
login
logins
```

share the same root.

The search engine reduces both words to a common form and performs matching.

### Key Learning

Full Text Search understands word variations.

---

## Exercise 4

```javascript
db.supportInc.find({
  $text: {
    $search: "procesor"
  }
})
```

Expected Result:

```text
[]
```

### Why did this fail?

Document contains:

```text
processor
```

Query contains:

```text
procesor
```

This is not a variation of the word.

This is a spelling mistake.

Full Text Search understands:

```text
processor
processors
processing
```

because these share a linguistic relationship.

However:

```text
procesor
```

is treated as an entirely different token.

### Key Learning

Full Text Search understands language.

It does not automatically understand spelling mistakes.

---

# Module 4 - Why Full Text Search Is Still Not Enough

Imagine a user searches:

```text
I changed my password and cannot access my account
```

Our document says:

```text
User unable to login after changing account password
```

Humans immediately understand both statements describe the same issue.

Traditional search engines may not.

The words are different.

The meaning is the same.

This is the problem Vector Search solves.

---

# Module 5 - Understanding Embeddings

## What is an Embedding?

An embedding is a numerical representation of meaning.

Text:

```text
User unable to login
```

may become:

```text
[0.124, -0.451, 0.778, ...]
```

The actual numbers are not important.

What matters is:

Documents discussing similar topics generate vectors that are close together.

---

## Example

Sentence 1:

```text
Unable to login
```

Sentence 2:

```text
Cannot access my account
```

The words are different.

However, their embeddings will be very similar because their meaning is similar.

---

# Module 6 - Generate Embeddings

Generate embeddings for every document using Azure OpenAI.

Store the vector in:

```text
embedding
```

field.

After completion verify:

```javascript
db.supportInc.findOne(
  {_id:1},
  {
    ticketId:1,
    embedding:{$slice:5}
  }
)
```

### What happened?

Your document now contains:

1. Human-readable text
2. AI-readable vectors

DocumentDB can now perform semantic search.

---

# Module 7 - Create Vector Index

```javascript
db.runCommand({
  createIndexes: "supportInc",
  indexes: [
    {
      name: "support_vector_idx",
      key: {
        embedding: "cosmosSearch"
      },
      cosmosSearchOptions: {
        kind: "vector-ivf",
        similarity: "COS",
        dimensions: 1536,
        numLists: 1
      }
    }
  ]
})
```

### Why do we need a vector index?

Without a vector index, DocumentDB would need to compare every vector against every document.

This becomes expensive at scale.

The vector index allows DocumentDB to quickly find the nearest vectors.

---

# Module 8 - Vector Search

User Query:

```text
I changed my password and now I cannot access my account
```

Generate an embedding for the query.

Run vector search.

Expected Top Result:

```text
SUP-1001
```

---

## Why did this work?

Document:

```text
User unable to login after changing account password
```

Query:

```text
I changed my password and now I cannot access my account
```

Notice:

| Document | Query |
|-----------|--------|
| unable to login | cannot access account |
| changing account password | changed my password |

Very few words overlap.

Keyword Search struggles.

Full Text Search struggles.

Vector Search succeeds because it compares meaning.

---

# Module 9 - The Big Picture

## Keyword Search

Question:

```text
login
```

Database asks:

> Do I see this exact word?

---

## Full Text Search

Question:

```text
logins
```

Database asks:

> Is this a linguistic variation of a known word?

---

## Vector Search

Question:

```text
I changed my password and now I cannot access my account
```

Database asks:

> Which stored documents have a similar meaning?

---

# Final Comparison

| Capability | Keyword | Full Text | Vector |
|------------|----------|-----------|---------|
| Exact Match | Yes | Yes | No |
| Word Variations | No | Yes | Yes |
| Understand Meaning | No | Limited | Yes |
| AI Ready | No | Limited | Yes |
| Best For RAG | No | No | Yes |

# Final Takeaway

Keyword Search matches words.

Full Text Search matches smarter words.

Vector Search matches meaning.

This shift from matching words to matching meaning is what enables modern AI applications, copilots, chatbots, semantic search engines, and Retrieval Augmented Generation (RAG) systems.

---

# Module 10 - Introduction to RAG

## What is RAG?

RAG stands for:

```text
Retrieval Augmented Generation
```

This may sound complex, but the idea is simple.

A normal LLM answers from what it already knows.

A RAG application first searches your private data, retrieves relevant information, and then asks the LLM to answer using that retrieved data.

---

## Normal LLM Flow

```text
User Question
      ↓
LLM
      ↓
Answer
```

This is simple, but it has some problems:

- The LLM may not know your company data
- The LLM may give a generic answer
- The LLM may hallucinate
- The answer may not be grounded in your database

---

## RAG Flow

```text
User Question
      ↓
Generate Query Embedding
      ↓
Search Azure DocumentDB
      ↓
Retrieve Relevant Tickets
      ↓
Send Tickets + Question to GPT
      ↓
Generate Final Answer
```

In this flow, Azure DocumentDB acts as the retrieval layer.

Azure OpenAI acts as:

1. Embedding generator
2. Answer generator

---

## Why RAG is Useful

Suppose the user asks:

```text
Why am I unable to access my account after changing password?
```

The LLM alone may not know your support ticket data.

But with RAG, the application first retrieves this ticket:

```text
SUP-1001 - Login failure after password reset
```

Then GPT answers using that ticket.

This makes the answer more grounded and useful.

---

# Module 11 - RAG Architecture Using Azure DocumentDB

## Components Used

This mini RAG application uses:

| Component | Purpose |
|----------|---------|
| Azure DocumentDB | Stores support tickets and embeddings |
| Azure OpenAI Embedding Model | Converts user question into vector |
| Azure DocumentDB Vector Search | Finds relevant tickets |
| Azure OpenAI Chat Model | Generates final answer |
| Python | Connects all components together |

---

## End-to-End Flow

```text
User asks question
      ↓
Python app receives question
      ↓
Azure OpenAI creates embedding for question
      ↓
Azure DocumentDB vector search finds matching tickets
      ↓
Python builds context from retrieved tickets
      ↓
Azure OpenAI chat model generates answer
      ↓
User receives final response
```

---

## Important Concept

Azure DocumentDB does not generate embeddings by itself.

Azure DocumentDB stores vectors and searches vectors.

Azure OpenAI generates embeddings.

So the responsibility is split like this:

| Responsibility | Service |
|---------------|---------|
| Store documents | Azure DocumentDB |
| Store embeddings | Azure DocumentDB |
| Generate embeddings | Azure OpenAI |
| Search similar vectors | Azure DocumentDB |
| Generate natural language answer | Azure OpenAI GPT model |

---

# Module 12 - Build Your First RAG Application

## Prerequisites

Before running the RAG app, make sure you have already completed:

1. Inserted the `supportInc` sample data
2. Generated embeddings for all support tickets
3. Created the vector index on the `embedding` field
4. Confirmed that vector search works

You also need these Python packages:

```bash
pip install pymongo openai
```

---

## Create Python File

Create a file named:

```text
rag_app.py
```

Paste the following code:

```python
from pymongo import MongoClient
from openai import AzureOpenAI

# -----------------------------
# Azure OpenAI Configuration
# -----------------------------
AZURE_OPENAI_ENDPOINT = "https://<your-openai-resource>.openai.azure.com/"
AZURE_OPENAI_KEY = "<your-azure-openai-key>"
AZURE_OPENAI_API_VERSION = "2024-02-01"

EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
CHAT_DEPLOYMENT = "<your-chat-model-deployment-name>"
# Example: gpt-4o-mini or gpt-4o

# -----------------------------
# Azure DocumentDB Configuration
# -----------------------------
MONGO_URI = "mongodb+srv://<user>:<password>@<cluster-name>.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

DB_NAME = "Workshop_DB"
COLLECTION_NAME = "supportInc"

# -----------------------------
# Clients
# -----------------------------
openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[DB_NAME][COLLECTION_NAME]


def generate_embedding(text: str):
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding


def vector_search(user_question: str, top_k: int = 3):
    query_vector = generate_embedding(user_question)

    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_vector,
                    "path": "embedding",
                    "k": top_k
                },
                "returnStoredSource": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "ticketId": 1,
                "title": 1,
                "description": 1,
                "category": 1,
                "priority": 1,
                "score": {"$meta": "searchScore"}
            }
        }
    ]

    return list(collection.aggregate(pipeline))


def build_context(search_results):
    context = ""

    for item in search_results:
        context += f\"\"\"
Ticket ID: {item.get("ticketId")}
Title: {item.get("title")}
Description: {item.get("description")}
Category: {item.get("category")}
Priority: {item.get("priority")}
Score: {item.get("score")}
---
\"\"\"

    return context.strip()


def generate_answer(user_question: str, context: str):
    system_prompt = \"\"\"
You are a support assistant.
Answer the user's question using only the provided support ticket context.
If the answer is not present in the context, say that you do not have enough information.
Keep the answer simple and clear.
\"\"\"

    user_prompt = f\"\"\"
User Question:
{user_question}

Support Ticket Context:
{context}

Answer:
\"\"\"

    response = openai_client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def main():
    print("\\nAzure DocumentDB RAG Demo")
    print("Type 'exit' to stop.\\n")

    while True:
        user_question = input("Ask your question: ")

        if user_question.lower() == "exit":
            break

        print("\\nSearching Azure DocumentDB...\\n")

        results = vector_search(user_question)

        print("Retrieved Tickets:")
        for item in results:
            print(f"- {item['ticketId']} | {item['title']} | Score: {item.get('score')}")

        context = build_context(results)

        print("\\nGenerating answer using Azure OpenAI...\\n")

        answer = generate_answer(user_question, context)

        print("\\nAnswer:")
        print(answer)
        print("\\n" + "-" * 80 + "\\n")


if __name__ == "__main__":
    main()
```

---

# Module 13 - Understanding the RAG Code

This section explains the code step by step.

The goal is not just to run the script, but to understand how the RAG flow works.

---

## Step 1 - Import Libraries

```python
from pymongo import MongoClient
from openai import AzureOpenAI
```

### Why do we need these?

`pymongo` is used to connect to Azure DocumentDB using the MongoDB-compatible API.

`AzureOpenAI` is used to call Azure OpenAI for:

1. Creating embeddings
2. Generating the final answer

---

## Step 2 - Configure Azure OpenAI

```python
AZURE_OPENAI_ENDPOINT = "https://<your-openai-resource>.openai.azure.com/"
AZURE_OPENAI_KEY = "<your-azure-openai-key>"
AZURE_OPENAI_API_VERSION = "2024-02-01"

EMBEDDING_DEPLOYMENT = "text-embedding-3-small"
CHAT_DEPLOYMENT = "<your-chat-model-deployment-name>"
```

### What does this mean?

The embedding deployment converts text into vectors.

The chat deployment generates the final natural language answer.

Both deployments are required because RAG has two AI tasks:

| Task | Model Type |
|------|------------|
| Convert question into vector | Embedding model |
| Generate final answer | Chat model |

---

## Step 3 - Configure Azure DocumentDB

```python
MONGO_URI = "mongodb+srv://<user>:<password>@<cluster-name>.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

DB_NAME = "Workshop_DB"
COLLECTION_NAME = "supportInc"
```

### What does this mean?

This connects the Python app to your Azure DocumentDB cluster.

The application will search inside:

```text
Workshop_DB.supportInc
```

This is the same collection used earlier for Keyword Search, Full Text Search, and Vector Search.

---

## Step 4 - Create Clients

```python
openai_client = AzureOpenAI(...)
mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[DB_NAME][COLLECTION_NAME]
```

### Why do we create clients?

A client is the object that allows Python to communicate with an external service.

Here we create:

1. One client for Azure OpenAI
2. One client for Azure DocumentDB

---

## Step 5 - Generate Embedding

```python
def generate_embedding(text: str):
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding
```

### What does this function do?

It takes text as input.

Example:

```text
I changed my password and now I cannot access my account
```

It sends this text to Azure OpenAI.

Azure OpenAI returns a vector.

Example:

```text
[0.123, -0.456, 0.789, ...]
```

This vector represents the meaning of the question.

---

## Step 6 - Perform Vector Search

```python
def vector_search(user_question: str, top_k: int = 3):
    query_vector = generate_embedding(user_question)
```

### What happens here?

The user question is converted into a vector.

This is required because DocumentDB vector search compares vectors, not raw text.

---

```python
pipeline = [
    {
        "$search": {
            "cosmosSearch": {
                "vector": query_vector,
                "path": "embedding",
                "k": top_k
            },
            "returnStoredSource": True
        }
    }
]
```

### What does this pipeline do?

It asks Azure DocumentDB:

> Compare this query vector with the stored vectors in the `embedding` field.

The field:

```text
embedding
```

contains vectors generated earlier for each support ticket.

The parameter:

```text
k: 3
```

means:

> Return the top 3 most similar tickets.

---

## Step 7 - Project Useful Fields

```python
"$project": {
    "_id": 0,
    "ticketId": 1,
    "title": 1,
    "description": 1,
    "category": 1,
    "priority": 1,
    "score": {"$meta": "searchScore"}
}
```

### Why do we use projection?

The full document may contain many fields, including the large embedding vector.

We do not want to send the full embedding to the LLM.

We only need useful readable information:

- Ticket ID
- Title
- Description
- Category
- Priority
- Search score

This keeps the context clean and efficient.

---

## Step 8 - Build Context

```python
def build_context(search_results):
    context = ""

    for item in search_results:
        context += f\"\"\"
Ticket ID: {item.get("ticketId")}
Title: {item.get("title")}
Description: {item.get("description")}
Category: {item.get("category")}
Priority: {item.get("priority")}
Score: {item.get("score")}
---
\"\"\"

    return context.strip()
```

### What is context?

Context is the retrieved information that we give to the LLM.

Instead of asking GPT to answer blindly, we say:

> Use these retrieved support tickets to answer the user.

This is the "Augmented" part of RAG.

The answer is augmented with your database content.

---

## Step 9 - Generate Final Answer

```python
def generate_answer(user_question: str, context: str):
```

This function sends two things to the chat model:

1. User question
2. Retrieved support ticket context

---

```python
system_prompt = \"\"\"
You are a support assistant.
Answer the user's question using only the provided support ticket context.
If the answer is not present in the context, say that you do not have enough information.
Keep the answer simple and clear.
\"\"\"
```

### Why is the system prompt important?

The system prompt controls the assistant behavior.

It tells the model:

- Do not answer from imagination
- Use only supplied context
- Be clear and simple
- Admit when context is insufficient

This reduces hallucination.

---

```python
temperature=0.2
```

### Why use low temperature?

Lower temperature makes responses more focused and deterministic.

For support and enterprise applications, we usually want stable answers, not creative answers.

---

# Module 14 - Run the RAG Application

Run the script:

```powershell
python .\rag_app.py
```

You should see:

```text
Azure DocumentDB RAG Demo
Type 'exit' to stop.
```

Ask:

```text
Why am I not able to access my account after changing password?
```

Expected retrieved ticket:

```text
SUP-1001 | Login failure after password reset
```

Expected answer should mention that the issue is related to login/authentication failure after password change.

---

# Module 15 - What Happened Internally?

When you asked:

```text
Why am I not able to access my account after changing password?
```

The application performed these steps:

## Step 1

Converted the question into an embedding.

```text
Question Text
↓
Query Vector
```

## Step 2

Searched Azure DocumentDB using vector similarity.

```text
Query Vector
↓
Compare with stored ticket vectors
↓
Find nearest tickets
```

## Step 3

Retrieved the most relevant ticket.

```text
SUP-1001
Login failure after password reset
```

## Step 4

Built a context block.

```text
Ticket ID: SUP-1001
Title: Login failure after password reset
Description: User is unable to login after changing account password.
```

## Step 5

Sent the context and question to GPT.

```text
Question + Retrieved Context
↓
GPT
↓
Answer
```

This is RAG.

---

# Module 16 - Why This Is Better Than Asking GPT Directly

If you ask GPT directly:

```text
Why am I unable to access my account?
```

GPT may give a generic answer.

But with RAG:

1. The application retrieves your actual support ticket
2. GPT answers using that retrieved ticket
3. The answer is grounded in your DocumentDB data

This is why RAG is useful for:

- Internal support bots
- Knowledge base search
- Customer service assistants
- Enterprise copilots
- Developer support tools
- Document search systems

---

# Module 17 - Try More RAG Questions

Try the following questions:

## Question 1

```text
Why am I not able to access my account after changing password?
```

Expected retrieved ticket:

```text
SUP-1001
```

---

## Question 2

```text
Why did my database migration stop due to lack of space?
```

Expected retrieved ticket:

```text
SUP-1002
```

---

## Question 3

```text
Why are customers not receiving emails from the system?
```

Expected retrieved ticket:

```text
SUP-1004
```

---

## Question 4

```text
Why is the database server slow during peak usage?
```

Expected retrieved ticket:

```text
SUP-1005
```

---

## Question 5

```text
Why does file upload fail for large documents?
```

Expected retrieved ticket:

```text
SUP-1003
```

---

# Module 18 - Common Issues and Fixes

## Issue 1 - PowerShell says `from` keyword is not supported

### Cause

You pasted Python code directly into PowerShell.

PowerShell is not Python.

### Fix

Create a `.py` file and run it:

```powershell
python .\rag_app.py
```

Or start Python shell first:

```powershell
python
```

---

## Issue 2 - Azure OpenAI endpoint error

### Cause

The endpoint may include an incorrect suffix.

Incorrect:

```text
https://<resource>.openai.azure.com/openai/v1
```

Correct:

```text
https://<resource>.openai.azure.com/
```

---

## Issue 3 - Vector dimension mismatch

### Cause

The vector index dimension must match the embedding model output.

For `text-embedding-3-small`, commonly used dimension is:

```text
1536
```

### Fix

Ensure your vector index has:

```javascript
dimensions: 1536
```

---

## Issue 4 - Vector search returns poor results

### Possible Causes

- Embeddings were not generated correctly
- Query is too vague
- Wrong field used in vector index
- Vector index not created
- Documents contain too little descriptive text

### Fix

Verify embeddings exist:

```javascript
db.supportInc.findOne(
  {_id:1},
  {
    ticketId:1,
    embedding:{$slice:5}
  }
)
```

---

# Module 19 - Final End-to-End Summary

You have now built the complete learning path:

```text
Keyword Search
    ↓
Exact word matching

Full Text Search
    ↓
Language-aware word matching

Embeddings
    ↓
Text converted into numerical meaning

Vector Search
    ↓
Meaning-based search

RAG Application
    ↓
Vector Search + GPT-generated answer
```

---

# Final Architecture

```text
User Question
      ↓
Azure OpenAI Embedding Model
      ↓
Query Vector
      ↓
Azure DocumentDB Vector Search
      ↓
Relevant Support Tickets
      ↓
Prompt Construction
      ↓
Azure OpenAI Chat Model
      ↓
Final Answer
```

---

# Final Takeaway

Keyword Search helps when the user knows the exact word.

Full Text Search helps when the user uses word variations.

Vector Search helps when the user describes the same meaning using different words.

RAG uses Vector Search to retrieve relevant business data and then uses an LLM to generate a grounded answer.

This is the foundation for building modern AI-native applications on Azure DocumentDB.
