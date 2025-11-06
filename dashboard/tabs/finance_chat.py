import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache embeddings and vector store
@st.cache_data(show_spinner=False)
def build_finance_embeddings(df: pd.DataFrame, force_rebuild=False):
    """
    Create embeddings for each row of the financial dataset and cache them persistently.
    Loads from disk if available, unless force_rebuild is True.
    """
    INDEX_PATH = "finance_agent/faiss_index.pkl"
    try:
        # Convert all rows to text for embedding
        text_rows = [" | ".join(map(str, r)) for r in df.values.tolist()]

        # If not force_rebuild and index exists, load it
        if not force_rebuild and os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "rb") as f:
                embeddings, cached_text_rows = pickle.load(f)
            st.info("Loaded cached finance embeddings from disk.")
            return embeddings, cached_text_rows

        # Otherwise, build embeddings
        embeddings = []
        for chunk_start in range(0, len(text_rows), 50):
            chunk = text_rows[chunk_start:chunk_start+50]
            resp = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            for emb in resp.data:
                embeddings.append(emb.embedding)
        embeddings = np.array(embeddings)
        # Save to disk
        with open(INDEX_PATH, "wb") as f:
            pickle.dump((embeddings, text_rows), f)
        st.success("Built and cached finance embeddings to disk.")
        return embeddings, text_rows
    except Exception as e:
        st.error(f"Embedding error: {e}")
        return None, None

@st.cache_data(show_spinner=False)
def retrieve_context(query: str, df, embeddings, text_rows, top_k=5):
    """Find the top_k most relevant rows for the query."""
    q_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    ).data[0].embedding

    sims = cosine_similarity([q_emb], embeddings)[0]
    top_idx = sims.argsort()[-top_k:][::-1]
    top_rows = [text_rows[i] for i in top_idx]
    return "\n".join(top_rows)

# -----------------------------
# Chat Interface
# -----------------------------
def finance_chat_interface(df: pd.DataFrame):
    # Initialize session state keys if missing
    if "user_query" not in st.session_state:
        st.session_state["user_query"] = ""
    if "loading" not in st.session_state:
        st.session_state["loading"] = False
    if "last_answer" not in st.session_state:
        st.session_state["last_answer"] = ""

    st.markdown("### 💹 Financial Insights Chat")
    st.caption("Ask questions like: *'Total revenue this quarter?'* or *'Which category has the highest cost?'*")

    # Build vector store (cached) with spinner
    with st.spinner("Loading financial data and embeddings..."):
        embeddings, text_rows = build_finance_embeddings(df)
    if embeddings is None:
        st.warning("Embeddings not ready yet. Displaying lightweight mode.")
        return

    # Suggested Questions
    st.markdown("### 💡 Suggested Questions")

    suggestions = [
        "What is the total revenue this month?",
        "Which expense category has the highest cost?",
        "How has profit margin changed over time?",
        "What are the top-performing sales channels?",
        "Show me the weekly revenue trend.",
        "Identify any unusual spending patterns."
    ]

    cols = st.columns(3)
    for i, q in enumerate(suggestions):
        if cols[i % 3].button(q, key=f"suggested_{i}", use_container_width=True):
            st.session_state["user_query"] = q
            st.session_state["user_query_textarea"] = q  # Sync with text area
            st.rerun()

    # Single text area for user query
    user_query = st.text_area(
        "Ask your financial question:",
        value=st.session_state.get("user_query_textarea", ""),
        key="user_query_textarea",
        placeholder="Type or click a suggested question...",
    )

    # Update session state if user types directly
    if user_query != st.session_state.get("user_query", ""):
        st.session_state["user_query"] = user_query

    analyze_btn = st.button("Analyze", disabled=st.session_state.get("loading", False) or not st.session_state["user_query"].strip())
    if analyze_btn:
        st.session_state["loading"] = True
        try:
            with st.spinner("Generating insights..."):
                # Retrieve top context
                context = retrieve_context(st.session_state["user_query"], df, embeddings, text_rows)

                # Compose the prompt
                prompt = f"""
                You are a financial analyst AI.
                Use the following dataset excerpts to answer the user's question:
                ```
                {context}
                ```
                User's question:
                "{st.session_state['user_query']}"
                Give a concise, actionable financial insight.
                """

                # Generate answer
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a financial data assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                )

                answer = response.choices[0].message.content
                st.session_state["last_answer"] = answer
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state["loading"] = False

    # Show result and scroll to bottom if available
    if "last_answer" in st.session_state and st.session_state["last_answer"]:
        st.markdown("### ✅ Insight Generated")
        st.markdown(st.session_state["last_answer"])
        st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

# ✅ TEST BLOCK (standalone)
if __name__ == "__main__":
    st.set_page_config(page_title="Finance Chat", layout="centered", page_icon="💬")
    st.title("🧮 Finance Chat Prototype")

    # Load your real 100-row financial dataset
    df = pd.read_csv("finance_agent/financial_data.csv")
    finance_chat_interface(df)