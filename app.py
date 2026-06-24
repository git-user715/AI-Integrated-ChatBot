import streamlit as st
from openai import OpenAI
from datetime import datetime
import random

# ============================================
# CONFIG
# ============================================
st.set_page_config(page_title="Student AI Chatbot", page_icon="🤖", layout="wide")

# 
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# ============================================
# LLM RESPONSE FUNCTION
# ============================================
def get_ai_response(user_message, mood, history):
    """Builds a prompt using mood + recent chat history and calls the HF model."""
    recent = history[-6:]  # keep last few turns so the prompt doesn't get too long
    convo = ""
    for m in recent:
        speaker = "Student" if m["role"] == "user" else "Assistant"
        convo += f"{speaker}: {m['content']}\n"

    prompt = f"""You are a friendly, patient AI study assistant for students.
You help with homework, explaining concepts simply, study tips, and general questions.
The student is currently feeling {mood}.
If they seem stressed, sad, or confused, briefly acknowledge it with empathy before helping.
Keep answers clear, encouraging, and not too long.

Conversation so far:
{convo}Student: {user_message}
Assistant:"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt
          }
    ],
    max_tokens=300,
    temperature=0.7
    )

    return response.choices[0].message.content


# ============================================
# SESSION STATE
# ============================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood" not in st.session_state:
    st.session_state.mood = "🙂 Happy"

if "mood_history" not in st.session_state:
    st.session_state.mood_history = []

if "goal" not in st.session_state:
    st.session_state.goal = ""

QUOTES = [
    "Every expert was once a beginner — keep going.",
    "Small steps every day add up to big progress.",
    "You don't need to be perfect, just consistent.",
    "Mistakes mean you're learning. Keep at it.",
    "Rest is productive too — take breaks when you need them.",
    "Progress, not perfection.",
]
if "quote" not in st.session_state:
    st.session_state.quote = random.choice(QUOTES)

# ============================================
# SIDEBAR - HEADER
# ============================================
st.sidebar.title("🤖 Student AI Chatbot")
st.sidebar.caption("Your study buddy, available anytime.")
st.sidebar.markdown("---")

# ============================================
# SIDEBAR - MOOD TRACKER
# ============================================
st.sidebar.header("💭 Mood Check-in")

mood = st.sidebar.radio(
    "How are you feeling today?",
    ["🙂 Happy", "😔 Sad", "😣 Stressed", "😌 Calm", "😕 Confused", "💪 Motivated"]
)
st.session_state.mood = mood

if st.sidebar.button("Save Mood"):
    st.session_state.mood_history.append(
        {"time": datetime.now().strftime("%d-%m-%Y %H:%M"), "mood": mood}
    )
    st.sidebar.success("Mood saved!")

if st.session_state.mood_history:
    st.sidebar.markdown("📊 Recent moods")
    for m in st.session_state.mood_history[-5:]:
        st.sidebar.write(f"{m['time']} → {m['mood']}")

st.sidebar.markdown("---")

# ============================================
# SIDEBAR - QUICK HELP PROMPTS
# ============================================
st.sidebar.header("⚡️ Quick Help")

quick_prompts = {
    "📘 Explain a concept": "Can you explain a concept to me in simple terms? I'll tell you which one.",
    "📝 Homework help": "I need help understanding a homework question. I'll share it now.",
    "🧠 Study tips": "Can you give me effective study tips for my upcoming exams?",
    "😮‍💨 Exam stress": "I'm feeling stressed about my exams. Can you help me calm down and make a plan?",
    "✍️ Improve my writing": "Can you help me improve a paragraph I wrote? I'll paste it now.",
}

for label, text in quick_prompts.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": text})
        with st.spinner("Thinking..."):
            reply = get_ai_response(text, st.session_state.mood, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

st.sidebar.markdown("---")

# ============================================
# SIDEBAR - TODAY'S GOAL
# ============================================
st.sidebar.header("🎯 Today's Goal")
goal = st.sidebar.text_input("What do you want to get done today?", value=st.session_state.goal)
st.session_state.goal = goal
if goal:
    st.sidebar.info(f"Goal: {goal}")

st.sidebar.markdown("---")

# ============================================
# SIDEBAR - DAILY MOTIVATION
# ============================================
st.sidebar.header("✨ Daily Motivation")
st.sidebar.write(st.session_state.quote)
if st.sidebar.button("New quote"):
    st.session_state.quote = random.choice(QUOTES)
    st.rerun()

st.sidebar.markdown("---")

# ============================================
# SIDEBAR - CLEAR CHAT
# ============================================
if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ This chatbot can make mistakes. Double-check anything important, "
    "and talk to a teacher or counselor for serious concerns."
)

# ============================================
# MAIN PAGE
# ============================================
st.title("🤖 Student AI Chatbot")
st.caption(f"Currently feeling: {st.session_state.mood}")

if not st.session_state.chat_history:
    st.info(
        "👋 Hi! I'm your AI study buddy. Ask me anything — homework help, "
        "explanations, study tips, or just to talk things through. "
        "Try a quick-help button in the sidebar to get started."
    )

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================
# CHAT INPUT
# ============================================
user_input = st.chat_input("Ask me anything about your studies...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_ai_response(user_input, st.session_state.mood, st.session_state.chat_history)
        st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
