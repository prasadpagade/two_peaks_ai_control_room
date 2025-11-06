# dashboard/tabs/support_tab.py
import os, json, re, time
from collections import Counter, deque
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from support_agent.support_shared import load_tickets

# ---------------------------------------------------------
# AUTO REFRESH (every 10 seconds)
# ---------------------------------------------------------
if hasattr(st, "autorefresh"):
    st.autorefresh(interval=10 * 1000, key="support_refresh")

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def _extract_keywords(text: str):
    stop = {
        "the","and","a","to","of","in","is","on","for","or","it","my","are","with","can","you","your",
        "how","what","who","when","where","why","which","about","from","this","that","our","me","do",
        "we","an","if","will","order","orders","help"
    }
    words = re.findall(r"\b\w+\b", (text or "").lower())
    return [w for w in words if w not in stop and len(w) > 2]

def _topic_dataframe(tickets):
    counter = Counter()
    for t in tickets:
        counter.update(_extract_keywords(t.get("user_query","")))
    top = counter.most_common(5)
    if not top:
        top = [("Shipping",18), ("Status",10), ("Refunds",7), ("Product",4), ("Payment",3)]
    df = pd.DataFrame(top, columns=["Topic","Tickets"])
    df["Topic"] = df["Topic"].str.title()
    return df

def _recent_items(tickets, n=3):
    return tickets[-n:] if tickets else []

# ---------------------------------------------------------
# OPENAI CLIENT
# ---------------------------------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4-turbo"

# ---------------------------------------------------------
# STREAMLIT OWNER VIEW
# ---------------------------------------------------------
def show():
    st.markdown("<h2 style='color:#3A4D39;'>💼 Support Command Center (Owner View)</h2>", unsafe_allow_html=True)
    st.caption("Monitor sentiment, trends, and customer requests in real time. Ask your AI assistant for insights, summaries, and next steps.")

    # Load ticket data
    tickets = load_tickets()
    total = len(tickets)
    topic_df = _topic_dataframe(tickets)
    recent = _recent_items(tickets, 3)

    # Layout
    col_analytics, col_chatbot = st.columns([1, 2], gap="large")

    # -------------------------------------------------
    # LEFT PANEL — LIVE ANALYTICS
    # -------------------------------------------------
    with col_analytics:
        st.markdown("""
        <div style="background-color:#f8f6f1; border:2px solid #b99746; border-radius:14px; padding:1.5rem; box-shadow:0 4px 12px rgba(185,151,70,0.07);">
        <h4 style="color:#b99746;">📊 Real-Time Support Analytics</h4>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div style='font-size:1.7em;font-weight:700;color:#b99746;'>{total}</div><div style='font-size:0.96em;color:#3A4D39;'>Tickets</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='font-size:1.7em;font-weight:700;color:#b99746;'>—</div><div style='font-size:0.96em;color:#3A4D39;'>Avg. Response Time</div>", unsafe_allow_html=True)
        with col3:
            top_topic = topic_df.iloc[0]["Topic"] if not topic_df.empty else "—"
            st.markdown(f"<div style='font-size:1.7em;font-weight:700;color:#b99746;'>{top_topic}</div><div style='font-size:0.96em;color:#3A4D39;'>Top Topic</div>", unsafe_allow_html=True)

        # Chart
        fig, ax = plt.subplots(figsize=(3.6, 2.0))
        ax.barh(topic_df["Topic"], topic_df["Tickets"], color="#b99746", edgecolor="#A0862C")
        ax.set_xlabel("Tickets", fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='y', labelsize=9, colors="#3A4D39")
        ax.tick_params(axis='x', labelsize=8, colors="#3A4D39")
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("<div style='color:#3A4D39;font-weight:600;margin-top:0.6rem;'>Recent Tickets</div>", unsafe_allow_html=True)
        if recent:
            for t in recent:
                ts = (t.get("timestamp","")[:19]).replace("T"," ")
                q = t.get("user_query","").strip()
                st.markdown(f"<div style='font-size:0.95em;'><span style='color:#b99746'>{ts}</span> — {q}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:0.95em;color:#b99746;'>No tickets yet.</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # RIGHT PANEL — OWNER AI ASSISTANT
    # -------------------------------------------------
    with col_chatbot:
        st.markdown("""
        <div style="background-color:#f8f6f1; border:2.5px solid #b99746; border-radius:18px; 
        box-shadow:0 6px 20px rgba(185,151,70,0.10); padding:1.3rem; margin-bottom:0.8rem;">
        <h4 style="color:#b99746;">🧠 Ask Your AI Support Assistant</h4>
        <p style="color:#3A4D39;">Ask about customer sentiment, refund trends, or generate emails. 
        The model reads your latest support logs automatically.</p>
        </div>
        """, unsafe_allow_html=True)

        if "support_chat_history" not in st.session_state:
            st.session_state.support_chat_history = deque(maxlen=4)

        # --- Owner prompt entry (explicit Send button; suggestions populate input) ---
        if "owner_query" not in st.session_state:
            st.session_state["owner_query"] = ""
        if "owner_query_text" not in st.session_state:
            st.session_state["owner_query_text"] = ""

        suggestions = [
            "Summarize customer sentiment this week",
            "Draft a refund apology email",
            "Which product has the most complaints?",
            "What keywords appear most in negative feedback?",
            "Summarize all refund-related issues"
        ]

        cols = st.columns(3)
        for i, q in enumerate(suggestions):
            if cols[i % 3].button(q, key=f"suggest_{i}", use_container_width=True):
                st.session_state["owner_query"] = q
                st.session_state["owner_query_text"] = q
                st.rerun()

        owner_query = st.text_input(
            "Ask a question about customer support insights...",
            value=st.session_state.get("owner_query_text", ""),
            key="owner_query_text",
            placeholder="Type or click a suggested question…",
        )

        # Keep session state in sync if user types
        if owner_query != st.session_state.get("owner_query", ""):
            st.session_state["owner_query"] = owner_query

        send_btn = st.button("Send", disabled=not st.session_state["owner_query"].strip())
        query = st.session_state["owner_query"].strip() if send_btn else None

        # Display prior chat turns
        for i, (role, content) in enumerate(st.session_state.support_chat_history):
            with st.chat_message(role):
                if role == "assistant":
                    # Use olive/dark green for assistant text
                    st.markdown(
                        f"<div style='color:#3A4D39;font-size:1.05em;'>{content}</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(content)

        # Process new query
        if query:
            with st.chat_message("user"):
                st.markdown(query)
            st.session_state.support_chat_history.append(("user", query))

            # Simulated order tracking data
            order_statuses = {
                "TP001": "Delayed",
                "TP002": "Canceled",
                "TP003": "On its way"
            }

            # Check for order ID in query
            order_id_match = re.search(r"\b(TP\d{3})\b", query, re.IGNORECASE)
            answer = None
            if order_id_match:
                found_id = order_id_match.group(1).upper()
                if found_id in order_statuses:
                    status = order_statuses[found_id]
                    answer = f"Order **{found_id}** status: <span style='color:#3A4D39;font-weight:700'>{status}</span>."

            # Build context summary
            context = ""
            for t in tickets[-10:]:
                context += f"- {t.get('timestamp','')}: {t.get('user_query','')}\n"

            # If no order match, fall back to OpenAI completion
            if not answer:
                with st.spinner("Analyzing..."):
                    try:
                        completion = client.chat.completions.create(
                            model=MODEL,
                            temperature=0.5,
                            messages=[
                                {"role": "system", "content": (
                                    "You are the Two Peaks Chai Co. support operations assistant. "
                                    "You help the owner analyze customer sentiment, generate emails, and detect trends. "
                                    "Be concise, data-driven, and empathetic. If asked to draft an email, keep it short and polite."
                                )},
                                {"role": "user", "content": f"Context from support logs:\n{context}\n\nQuestion: {query}"}
                            ],
                        )
                        answer = completion.choices[0].message.content.strip()
                    except Exception as e:
                        answer = f"⚠️ Error: {e}"

            with st.chat_message("assistant"):
                st.markdown(
                    f"<div style='color:#3A4D39;font-size:1.05em;'>{answer}</div>",
                    unsafe_allow_html=True
                )
            st.session_state.support_chat_history.append(("assistant", answer))