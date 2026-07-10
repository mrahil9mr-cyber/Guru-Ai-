import streamlit as st
import google.generativeai as genai
from langchain_community.llms import Ollama
import sqlite3

# --- DATABASE SETUP (Permanent Memory) ---
conn = sqlite3.connect("guru_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_msg TEXT,
        ai_msg TEXT
    )
''')
conn.commit()

# Memory functions
def save_to_memory(user_msg, ai_msg):
    cursor.execute("INSERT INTO memory (user_msg, ai_msg) VALUES (?, ?)", (user_msg, ai_msg))
    conn.commit()

def get_all_memory():
    cursor.execute("SELECT user_msg, ai_msg FROM memory")
    return cursor.fetchall()

def clear_all_memory():
    cursor.execute("DELETE FROM memory")
    conn.commit()

# --- APP SETUP ---
st.set_page_config(page_title="Guru AI", page_icon="🧠", layout="centered")
st.title("🧠 Guru AI — Powered by Google Live Search")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Guru AI Controls")
app_mode = st.sidebar.radio("Connection Mode:", ("Online (Google Live Search)", "Offline (Local & Secure)"))

st.sidebar.markdown("---")
# Reset Button in Sidebar
if st.sidebar.button("💥 Guru ki Memory Clear Karein"):
    clear_all_memory()
    st.sidebar.success("Guru sab kuch bhool gaya!")
    st.rerun()

# --- MAIN AI ENGINE ---
def get_ai_response(prompt, mode):
    # Database se purani saari baatein nikalna
    db_memory = get_all_memory()
    
    context = "Aapka naam 'Guru AI' hai. Aap user ke personal guide ho. Aapki memory permanent hai. Niche di gayi purani baatein yaad rakhein aur unke aadhar par jawab dein:\n"
    for human, ai in db_memory:
        context += f"User: {human}\nGuru AI: {ai}\n"

    # API KEY Setup - Aapki Key bilkul sahi format me yahan daal di hai
    GOOGLE_API_KEY = "AQ.Ab8RN6KG0wD6HjAhhz3-DRZFo5KAunORE_53x1wJ3SN0MaX1hg" 
    
    if mode == "Online (Google Live Search)":
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
            return "Kripya code me apni Gemini API Key dalein ya Offline mode select karein."
        
        # Google API ko configure karna
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Google Search Tool ko enable karna (Google Grounding Feature)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools='google_search' 
        )
        
        full_prompt = f"{context}\nUser Question: {prompt}\n\nGoogle Search ka use karke ekdum sacha aur up-to-date jawab dein."
        
        with st.spinner("Google par jankari dhoondh raha hoon... 🌐"):
            try:
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                return f"Google search me dikkat aayi: {e}"

    else:
        # Offline mode (Bina Internet ke - Local Engine)
        full_prompt = f"{context}\nUser: {prompt}\nGuru AI:"
        try:
            llm = Ollama(model="llama3")
            return llm.invoke(full_prompt)
        except Exception:
            return "Offline mode ke liye pehle computer me Ollama start karein."

# --- CHAT INTERFACE ---
chat_history = get_all_memory()
for user_msg, ai_msg in chat_history:
    with st.chat_message("user"):
        st.write(user_msg)
    with st.chat_message("assistant"):
        st.write(ai_msg)

# User Input
if user_input := st.chat_input("Guru se kuch bhi pucho, Google se dhoondh kar batayega..."):
    with st.chat_message("user"):
        st.write(user_input)

    # CHECK FOR FORGET COMMAND
    if "bhool jao" in user_input.lower() or "delete" in user_input.lower():
        clear_all_memory()
        with st.chat_message("assistant"):
            st.write("Ji, mai aapki kahi saari baatein bhool gaya hoon. Ab naye sire se shuru karte hain. 🙏")
    else:
        with st.chat_message("assistant"):
            response_text = get_ai_response(user_input, app_mode)
            st.write(response_text)
            
        # Permanent Database me save karna
        save_to_memory(user_input, response_text)
      
