import streamlit as st
import json
import os
import requests

MODEL = "undi/dolphin-mixtral"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def extract_memory(api_key, chat_text, contact_name):
    prompt = f"""
You are analyzing past Instagram chats between Sam and {contact_name}.
Extract:
1. Interests/hobbies
2. Emotional tone (e.g., casual, romantic)
3. Important facts
4. Style of replying

Return JSON like:
{{
  "interests": [...],
  "tone": "...",
  "facts": [...],
  "style_notes": "..."
}}
Chat:
{chat_text}
"""
    headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    r = requests.post(API_URL, headers=headers, json=data)
    result = json.loads(r.json()["choices"][0]["message"]["content"])
    return result

def save_memory(contact, memory):
    path = "memory.json"
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    data[contact] = memory
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_goal(contact):
    if os.path.exists("goals.json"):
        with open("goals.json", "r") as f:
            goals = json.load(f)
        return goals.get(contact, "")
    return ""


def save_language(contact, lang):
    langs = {}
    if os.path.exists("language.json"):
        with open("language.json", "r") as f:
            langs = json.load(f)
    langs[contact] = lang
    with open("language.json", "w") as f:
        json.dump(langs, f, indent=2)

def load_language(contact):
    if os.path.exists("language.json"):
        with open("language.json", "r") as f:
            langs = json.load(f)
        return langs.get(contact, "Auto")
    return "Auto"


    goals = {}
    if os.path.exists("goals.json"):
        with open("goals.json", "r") as f:
            goals = json.load(f)
    goals[contact] = goal
    with open("goals.json", "w") as f:
        json.dump(goals, f, indent=2)

def generate_replies(api_key, contact, latest_message):
    with open("memory.json", "r") as f:
        memory = json.load(f).get(contact, {})
    goal = load_goal(contact)
    prompt = f"""
You are helping Sam reply to his Instagram friend: {contact}.
Latest message: "{latest_message}"
Goal: {goal}
Memory:
Interests: {memory.get("interests")}
Tone: {memory.get("tone")}
Facts: {memory.get("facts")}
Style notes: {memory.get("style_notes")}
Language: {load_language(contact)}

Give 3 reply suggestions that are smart, personal, and aligned with the goal.
Number them as:
1. ...
2. ...
3. ...
"""
    headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    r = requests.post(API_URL, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]

st.set_page_config(page_title="Instagram Chat Assistant", layout="centered")
st.title("📱 Instagram Chat Assistant (Mobile Ready)")
api_key = st.text_input("🔑 OpenRouter API Key", type="password")
contact = st.text_input("👤 Friend's Instagram Username")

st.header("📁 Step 1: Upload Chat Export")
uploaded = st.file_uploader("Upload Instagram message_1.json", type=["json"])
if uploaded and api_key and contact:
    text = json.load(uploaded)
    messages = "\n".join([msg["text"] for msg in text["messages"] if isinstance(msg["text"], str)])
    memory = extract_memory(api_key, messages, contact)
    save_memory(contact, memory)
    st.success("✅ Memory extracted and saved!")
    st.json(memory)

st.header("🎯 Step 2: Set or Update Goal")
goal = st.text_input("Goal with this person (e.g., Make her fall for me)")
if goal and contact:
    save_goal(contact, goal)
    st.success("🎯 Goal saved!")


st.header("🗣️ Step 2.5: Select Language Style")
lang_choice = st.selectbox("Preferred language style for replies", [
    "Auto", "English", "Hindi", "Marathi", "Romanized Marathi", "Hinglish"
])
if contact:
    save_language(contact, lang_choice)
    st.success(f"🌐 Language style saved as: {lang_choice}")

st.header("💬 Step 3: Get Reply Suggestions")
new_message = st.text_area("Paste the latest message you received")
if st.button("✨ Suggest Replies") and new_message and api_key:
    replies = generate_replies(api_key, contact, new_message)
    st.markdown("### 🤖 Suggested Replies")
    st.markdown(replies)