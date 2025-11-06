# support_agent/rag_support_bot.py
import os, json, uuid, glob
import chromadb
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from support_shared import load_docs, query_context

# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("two_peaks_faqs")

# ---------------------------------------------------------
# Load docs once
# ---------------------------------------------------------
docs = load_docs()
print(f"📄 Loaded {len(docs)} FAQ files.")
for d in docs:
    print("  -", d["source"])

# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are the official Two Peaks Chai Co. support assistant.
Your tone is warm, friendly, and aligned with the brand’s story — blending Indian heritage and modern wellness.
Use the retrieved context to answer customer questions clearly and personally.
If you detect the user is new or a first-time buyer, recommend the Founder's Ritual Sampler Box.
Always keep your tone human, empathetic, and concise.
"""

# ---------------------------------------------------------
# Main chat handler
# ---------------------------------------------------------
def generate_answer(message: str, history: list):
    query = message
    print(f"🗣️ Received query: {query}")

    try:
        context = query_context(query)
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        context = ""

    # Detect first-time buyers
    if any(w in query.lower() for w in ["first time", "new customer", "recommend", "try"]):
        context += "\n\n[Suggest the Founder's Ritual Sampler Box — perfect for first-time buyers!]"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.5,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nUser: {query}"}
            ]
        )
        text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI error: {e}")
        return "⚠️ Sorry, something went wrong."

    # Log ticket
    ticket_path = os.path.join(os.path.dirname(__file__), "support_tickets.json")
    now = datetime.utcnow().isoformat()
    new_ticket = {"timestamp": now, "user_query": query, "assistant_response": text}
    try:
        tickets = []
        if os.path.exists(ticket_path):
            with open(ticket_path, "r", encoding="utf-8") as f:
                tickets = json.load(f)
        tickets.append(new_ticket)
        with open(ticket_path, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
    except Exception as e:
        print(f"❌ Ticket log error: {e}")

    return text

def welcome_message():
    return (
        "🌿 **Welcome to Two Peaks Chai Co. Support!**\n\n"
        "Ask me anything about our blends, brewing rituals, shipping, or your order. "
        "If you’re new here, I can help you pick your perfect chai ☕."
    )

theme = gr.themes.Soft(primary_hue="amber", neutral_hue="stone")

demo = gr.ChatInterface(
    fn=generate_answer,
    title="Two Peaks Chai Support Assistant",
    description="Your personal chai guide — here to help with orders, brewing, and product recommendations.",
    chatbot=gr.Chatbot(value=[[None, welcome_message()]]),
    examples=[
        "What’s the best chai for first-time buyers?",
        "How do I brew your Signature Masala?",
        "What’s your refund policy?",
        "Tell me about the founders."
    ],
    theme=theme
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)