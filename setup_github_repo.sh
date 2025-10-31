#!/bin/bash
# ==========================================================
# Two Peaks AI Control Room – GitHub Auto Setup Script
# ==========================================================

REPO_NAME="two_peaks_ai_control_room"
GITHUB_USER="YOUR_GITHUB_USERNAME"   # 👈🏽 replace with your GitHub username
DEFAULT_BRANCH="main"

echo "🚀 Initializing local git repository..."
git init -b $DEFAULT_BRANCH

echo "🛠  Creating .gitignore..."
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.venv/
.env
*.env
.vscode/
.DS_Store
.streamlit/secrets.toml
EOF

echo "🧩 Creating .env.example..."
cat > .env.example <<'EOF'
OPENAI_API_KEY=your_api_key_here
N8N_WEBHOOK_URL=https://your-n8n-endpoint
CHROMADB_PATH=./support_agent/chroma_db
EOF

echo "📦 Creating requirements.txt..."
cat > requirements.txt <<'EOF'
streamlit
gradio
openai
chromadb
pandas
python-dotenv
langchain
requests
EOF

echo "📝 Creating README.md..."
cat > README.md <<'EOF'
# Two Peaks AI Control Room

An autonomous AI operations hub for **Two Peaks Chai Co.**  
Built with **Streamlit**, **Gradio**, **OpenAI**, and **n8n**.

## Setup
python -m venv .venv  
source .venv/bin/activate  
pip install -r requirements.txt  
cp .env.example .env  
streamlit run dashboard/control_room_app.py
EOF

echo "💾 Creating initial commit..."
git add .
git commit -m "Initial commit: Two Peaks AI Control Room setup"

echo "🌐 Creating remote repository on GitHub..."
gh repo create $REPO_NAME --public --source=. --remote=origin --push

echo "✅ Repository initialized and pushed!"
