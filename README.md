# 🍽️ Menu AI Agent

An AI-powered restaurant ordering assistant with voice support.

## ✨ Features

- 🎤 **STT** — Groq Whisper API converts your voice to text
- 🤖 **AI Agent** — LangGraph ReAct agent powered by Groq LLM
- 🔍 **Menu Search** — Semantic search across menu items with mandatory choices & add-ons
- 🔊 **TTS** — Browser Web Speech API reads responses aloud
- 💬 **Chat UI** — Clean browser-based interface, no installation needed

---

## 🏗️ Architecture

```
🎤 User speaks
    ↓
Browser records audio (MediaRecorder)
    ↓
POST /transcribe  →  Groq Whisper API  →  text
    ↓
POST /chat  →  LangGraph ReAct Agent
                ├── search_menu_tool()    → vector DB search
                └── validate_order_item() → price calculation
    ↓
🔊 Browser TTS (Web Speech API) reads the response aloud
```

---

## 📁 Project Structure

```
menu-agent/
├── main.py                        ← FastAPI: /transcribe /chat
├── chat_ui.html                   ← Browser UI (mic + chat + browser TTS)
├── .env                           ← API keys
├── requirements.txt
└── src/
    ├── agent/
    │   ├── menu_agent.py          ← LangGraph ReAct agent + Groq LLM
    │   └── tools.py               ← search_menu_tool, validate_order_item
    ├── database/
    │   └── chroma_db.py           ← In-memory keyword search (TF-IDF)
    ├── models/
    │   └── menu.py                ← MenuItem, MandatoryChoice, Addon
    └── data/
        └── menu_data.py           ← 10 menu items (burgers, pizza, pasta, drinks, sides)
```

---

## ⚙️ Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/your-username/menu-agent.git
cd menu-agent
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama3-70b-8192
```

Get your Groq API key: https://console.groq.com/keys

### 5. Run

```bash
uvicorn main:app --reload --port 8000
```

Open: **http://127.0.0.1:8000**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat UI |
| `POST` | `/chat` | Send message to agent |
| `POST` | `/transcribe` | Audio file → text (Groq Whisper) |
| `GET` | `/menu` | Full menu (JSON) |
| `GET` | `/menu/search?q=burger` | Search menu directly |

### Chat example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a burger", "session_id": "test1"}'
```

---

## 🎤 Voice Flow (step by step)

```
1. User holds mic button in browser
2. MediaRecorder captures audio (WebM format)
3. User releases → audio sent to POST /transcribe
4. Backend sends audio to Groq Whisper API
5. Groq returns transcribed text
6. Text is sent to POST /chat automatically
7. LangGraph agent processes and responds
8. Browser Web Speech API reads the response aloud
```

> TTS uses the browser's built-in speech engine — works in any modern browser,
> no extra API key needed.

---

## 🤖 How the Agent Works

The agent uses the **ReAct** (Reasoning + Acting) pattern:

```
User: "I want a spicy burger"

Thought:  Search the menu for spicy burger options
Action:   search_menu_tool(query="spicy burger")
Result:   { Spicy Crispy Chicken Burger, ... }

Thought:  Found a match — ask for mandatory choices
Answer:   "I found the Spicy Crispy Chicken Burger ($10.99).
           What spice level? Mild / Medium / Hot / Extra Hot"

[User picks spice level and bun]

Action:   validate_order_item(
            item_id="burger-002",
            chosen_options='{"Spice Level":"Hot","Bun":"Brioche"}'
          )
Result:   { valid: true, total_price: 11.49 }

Answer:   "Order confirmed! Total: $11.49. Shall I place the order?"
```

---

## 🧠 LangGraph Agent

```python
agent = create_react_agent(
    model=ChatGroq(model="llama3-70b-8192"),
    tools=[search_menu_tool, validate_order_item, get_menu_categories],
    checkpointer=MemorySaver(),   # remembers conversation per session_id
    prompt=SystemMessage(content=SYSTEM_PROMPT),
)
```

---

## 📦 Requirements

```
fastapi
uvicorn[standard]
langchain-groq
langchain-core
langgraph
chromadb
sentence-transformers
pydantic
loguru
python-dotenv
httpx
```

---

## 🗺️ Menu Items

| Category | Items |
|----------|-------|
| Burger | Classic Cheeseburger, Spicy Crispy Chicken, Mushroom Swiss |
| Pizza | Margherita, BBQ Chicken |
| Pasta | Spaghetti Bolognese, Creamy Alfredo |
| Drink | Fresh Lemonade, Milkshake |
| Side | French Fries |

Each item has **mandatory choices** (e.g. size, bun type) and optional **add-ons**.

---

