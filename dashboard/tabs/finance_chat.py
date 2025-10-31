import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def finance_chat_interface(df: pd.DataFrame):
    st.markdown("### 💹 Financial Insights Chat")
    st.caption("Ask questions like: *'Total revenue this quarter?'* or *'Show expenses by category.'*")

    user_query = st.text_area("Ask your financial question:")

    if st.button("Analyze") and user_query.strip():
        with st.spinner("Analyzing your data..."):
            try:
                csv_preview = df.head(50).to_csv(index=False)
                prompt = f"""
                You are a financial data analyst.
                Here is a preview of the dataset (first 50 rows):
                ```
                {csv_preview}
                ```
                Answer this question clearly and precisely:
                "{user_query}"
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a financial analysis assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                answer = response.choices[0].message.content
                st.success("✅ Result:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Error: {e}")

# ✅ TEST BLOCK: Run standalone if executed directly
if __name__ == "__main__":
    st.set_page_config(page_title="Finance Chat", layout="centered", page_icon="💬")
    st.title("🧮 Finance Chat Prototype")

    # Small mock dataset for testing
    data = {
        "Month": ["Jan", "Feb", "Mar", "Apr"],
        "Revenue": [12000, 15000, 17000, 16000],
        "Expenses": [8000, 9500, 10000, 9000],
    }
    df = pd.DataFrame(data)

    finance_chat_interface(df)