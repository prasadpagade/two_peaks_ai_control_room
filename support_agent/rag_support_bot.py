import os
import glob
import uuid
import gradio as gr
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------------
# LOAD ENV + INIT CLIENTS
# ---------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("two_peaks_faqs")

# ---------------------------------------------------------
# LOAD LOCAL FAQ DOCS
# ---------------------------------------------------------
def load_docs():
    docs = []
    for path in glob.glob("support_agent/*.md"):
        with open(path, "r", encoding="utf-8") as f:
            docs.append({
                "id": str(uuid.uuid4()),
                "text": f.read(),
                "source": os.path.basename(path)
            })
    return docs

docs = load_docs()
print(f"📄 Loaded {len(docs)} FAQ files:")
for d in docs:
    print("  -", d["source"])

# ---------------------------------------------------------
# STORE EMBEDDINGS INTO CHROMA
# ---------------------------------------------------------
for doc in docs:
    try:
        if not collection.get(ids=[doc["id"]])["ids"]:
            emb = client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["text"]
            ).data[0].embedding
            collection.add(
                ids=[doc["id"]],
                embeddings=[emb],
                documents=[doc["text"]],
                metadatas=[{"source": doc["source"]}]
            )
    except Exception as e:
        print(f"❌ Embedding error for {doc['source']}: {e}")

# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are the official Two Peaks Chai Co. support assistant.
Your tone is warm, friendly, and aligned with the brand’s story — blending Indian heritage and modern wellness.
Use the retrieved context to answer customer questions clearly and personally.
If you detect the user is new or a first-time buyer, recommend the Founder's Ritual Sampler Box.
Always keep your tone human, empathetic, and concise.
"""

# ---------------------------------------------------------
# RESPONSE GENERATOR
# ---------------------------------------------------------
def generate_answer(message: str, history: list):
    query = message
    print(f"🗣️ Received query: {query}")

    # Retrieve relevant context
    try:
        q_emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding

        results = collection.query(query_embeddings=[q_emb], n_results=3)
        context = "\n\n".join(results["documents"][0]) if results["documents"] else ""
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return "⚠️ Sorry, I had trouble retrieving the right answer."

    # Detect first-time buyers
    if any(w in query.lower() for w in ["first time", "new customer", "recommend", "try"]):
        context += "\n\n[Suggest the Founder's Ritual Sampler Box — perfect for first-time buyers!]"

    # Generate chat completion
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
        text = text.replace("_", "").replace("*", "").replace("`", "")
        return text

    except Exception as e:
        import traceback
        print("🔥 Chat completion error:")
        traceback.print_exc()
        return f"⚠️ OpenAI API error: {e}"

# ---------------------------------------------------------
# GRADIO CHAT INTERFACE
# ---------------------------------------------------------
def welcome_message():
    return (
        "🌿 **Welcome to Two Peaks Chai Co. Support!**\n\n"
        "Ask me anything about our blends, brewing rituals, shipping, or your order. "
        "If you’re new here, I can help you pick your perfect chai ☕."
    )

# ✅ Compatible theme definition (Gradio ≥ 4)
theme = gr.themes.Soft(
    primary_hue="orange",
    neutral_hue="gray"
).set(
    body_background_fill="#1c1b18",
    button_primary_background_fill="#b99746",
    button_primary_background_fill_hover="#e7c66b",
    button_primary_text_color="#1c1b18",
    block_title_text_color="#b99746",
)

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

# ---------------------------------------------------------
# LAUNCH APP
# ---------------------------------------------------------
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)