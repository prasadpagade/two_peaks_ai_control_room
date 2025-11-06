# support_agent/support_shared.py
"""
Shared utility module for both Support Agents:
- Customer-facing RAG bot (rag_support_bot.py)
- Owner-facing Support Command Center (support_tab.py)
Handles: vector store access, ticket loading, and context retrieval.
"""

import os, json, glob, uuid, chromadb
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("two_peaks_faqs")

# ---------------------------------------------------------
# LOAD LOCAL FAQ DOCS
# ---------------------------------------------------------
def load_docs():
    """Load all markdown FAQ files for embedding into the shared Chroma DB."""
    docs = []
    for path in glob.glob(os.path.join("support_agent", "*.md")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                docs.append({
                    "id": str(uuid.uuid4()),
                    "text": f.read(),
                    "source": os.path.basename(path)
                })
        except Exception as e:
            print(f"⚠️ Error reading {path}: {e}")
    return docs

# ---------------------------------------------------------
# VECTOR QUERYING
# ---------------------------------------------------------
def query_context(query: str, n_results: int = 3) -> str:
    """
    Retrieve top contextual snippets from the shared Chroma vector store.
    Returns concatenated text ready for prompting.
    """
    try:
        q_emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding

        results = collection.query(query_embeddings=[q_emb], n_results=n_results)
        if results and results.get("documents"):
            return "\n\n".join(results["documents"][0])
        return ""
    except Exception as e:
        print(f"❌ Chroma query error: {e}")
        return ""

# ---------------------------------------------------------
# LOAD SUPPORT TICKETS
# ---------------------------------------------------------
def load_tickets():
    """Safely load all support tickets saved by either bot."""
    ticket_path = os.path.join(os.path.dirname(__file__), "support_tickets.json")
    if not os.path.exists(ticket_path):
        return []

    try:
        with open(ticket_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("⚠️ Invalid ticket file format; expected list.")
                return []
    except json.JSONDecodeError:
        print("⚠️ Could not decode support_tickets.json; resetting.")
        return []
    except Exception as e:
        print(f"❌ Error loading tickets: {e}")
        return []