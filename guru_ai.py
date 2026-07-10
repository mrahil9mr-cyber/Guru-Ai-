
import streamlit as st
from langchain_community.llms import Ollama
import sqlite3

# --- DATABASE SETUP (Permanent Memory) ---
conn = sqlite3.connect("guru_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS memory (
        user_msg TEXT,
        ai_msg TEXT
    )
"""
)
conn.commit()


# --- Memory Functions ---
def save_to_memory(user_msg, ai_msg):
    cursor.execute(
        "INSERT INTO memory (user_msg, ai_msg) VALUES (?, ?)", (user_msg, ai_msg)
    )
    conn.commit()


def get_all_memory():
    cursor.execute("SELECT user_msg, ai_msg FROM memory")
    return cursor.fetchall()


def clear_all_memory():
    cursor.execute("DELETE FROM memory")
    conn.commit()


# --- APP SETUP ---
st.set_page_config(page_title="Guru AI", page_icon="🧠", layout="centered")
st.title("🧠 Guru AI - Powered by Local Model")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Guru AI Controls")
app_mode = st.sidebar.radio("Connection Mode:", ("Offline",))

st.sidebar.markdown("---")

if st.sidebar.button("Guru Ki Memory Clear Karein"):
    clear_all_memory()
    st.sidebar.success("Guru sab kuch bhool gaya!")
    st.rerun()

# --- MAIN AI ENGINE ---
def get_ai_response(prompt):
    # 'llama3' ki jagah aap apne terminal me downloaded model ka naam bhi likh sakte hain (jaise llama2, mistral)
    llm = Ollama(model="llama3")
    response = llm.invoke(prompt)
    return response


db_memory = get_all_memory()

context = "Aapka naam 'Guru AI'. Aap user ke personal guide ho. Aapki memory permanent hai."
for human, ai in db_memory:
    context += f"Human: {human}\nGuru AI: {ai}\n"

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Guru se kuch bhi pucho, offline kaam karega..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_context = context + f"Human: {prompt}\nAI:"
        response = get_ai_response(full_context)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    save_to_memory(prompt, response)
        
