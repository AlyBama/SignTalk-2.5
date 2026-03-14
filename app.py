import streamlit as st
from google import genai
from google.genai import types
import cv2
import tempfile
import time
from gtts import gTTS
import os
import json
from dotenv import load_dotenv

# تحميل مفتاح الأمان من ملف .env
load_dotenv()
api_key = os.getenv("API_KEY")

st.set_page_config(page_title="SignTalk 2.5 Pro Max", layout="wide")
st.title("🤟 SignTalk 2.5 Pro Max")
st.subheader("Universal Sign Language Translator - Two Way")

if 'history' not in st.session_state:
    st.session_state.history = []

# إعداد العميل
client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-1.5-flash" # الموديل المستقر للنسخة المجانية

# مكتبة الفيديوهات المحلية
video_clips = {
    "FINE": "fine.mp4", "FORGET": "forget.mp4", "GO": "go.mp4",
    "HAPPY": "happy.mp4", "LIKE": "like.mp4", "MORE": "more.mp4",
    "NEED": "need.mp4", "PLEASE": "please.mp4", "RIGHT": "right.mp4",
    "SAD": "sad.mp4", "THANK YOU": "thank_you.mp4", "WANT": "want.mp4",
    "WRONG": "wrong.mp4", "YES": "yes.mp4"
}

# --- نظام الكاش ---
CACHE_FILE = "text_cache.json"
def load_text_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_text_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)

# ====================== الجزء الأول: من إشارة إلى صوت ونص ======================
st.header("1️⃣ Sign → Speech + Text")

col_vid, col_res = st.columns([2, 1])
with col_vid:
    frame_placeholder = st.empty()
    status_placeholder = st.empty()
with col_res:
    st.subheader("📊 Result")
    confidence_placeholder = st.empty()

if st.button("🎬 Start Sign (DroidCam)"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ DroidCam is not connected")
    else:
        for i in range(3, 0, -1):
            status_placeholder.warning(f"⏳ Get ready... {i}")
            time.sleep(1)
        status_placeholder.error("🎥 RECORDING...")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
            temp_path = tfile.name
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_path, fourcc, 30.0, (640, 480))
            
            start_time = time.time()
            while (time.time() - start_time) < 4:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    frame_placeholder.image(frame, channels="BGR", caption="Live Feed", use_container_width=True)
                else: break
            cap.release()
            out.release()

        with st.spinner('🧬 Gemini is analyzing...'):
            try:
                with open(temp_path, 'rb') as f:
                    file_bytes = f.read()
                
                prompt = "Analyze this ASL video. Return ONLY: [WORD] | [CONFIDENCE%] from the predefined list."
                
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[prompt, types.Part.from_bytes(data=file_bytes, mime_type="video/mp4")]
                )
                
                full_res = response.text.strip()
                word = full_res.split('|')[0].strip() if '|' in full_res else full_res
                conf = full_res.split('|')[1].strip() if '|' in full_res else "N/A"
                
                st.session_state.history.append(f"Sign → {word}")
                status_placeholder.success(f"✅ Result: {word}")
                confidence_placeholder.metric("Confidence", conf)
                
                tts = gTTS(text=word, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3", autoplay=True)
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ زحمة طلبات! جوجل بتقولك استنى 10 ثواني وجرب تاني (Quota Limit).")
                else:
                    st.error(f"❌ حدث خطأ: {e}")

# ====================== الجزء الثاني: من نص/صوت إلى فيديو إشارة ======================
st.header("2️⃣ Text or Speech → Sign Video")
tab1, tab2 = st.tabs(["✍️ Type the word", "🎤 Speak"])

with tab1:
    text_input = st.text_input("Type the word in English")
    if st.button("Analyze Text with Gemini"):
        if text_input:
            text_lower = text_input.strip().lower()
            cache = load_text_cache()
            
            if text_lower in cache:
                word = cache[text_lower]
                st.info("🔄 Retrieved from Cache")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=[f"Match this text to ONE: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return word only.", text_input]
                        )
                        word = response.text.strip().upper()
                        cache[text_lower] = word
                        save_text_cache(cache)
                    except Exception as e:
                        st.error("⚠️ السيرفر مشغول حالياً، جرب كمان ثواني.")
                        word = "ERROR"

            if word in video_clips:
                col_centered = st.columns([1, 2, 1])
                with col_centered[1]:
                    st.video(video_clips[word], autoplay=True) 
                st.success(f"✅ Showing sign: {word}")
            elif word != "ERROR":
                st.error(f"Word '{word}' not supported")

with tab2:
    audio_input = st.audio_input("Speak now")
    if audio_input is not None:
        with st.spinner("Gemini is listening..."):
            try:
                audio_bytes = audio_input.read()
                part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
                
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=["Convert speech to ONE exact ASL word from the list. Return word only.", part]
                )
                word = response.text.strip().upper()
                
                if word in video_clips:
                    col_centered = st.columns([1, 2, 1])
                    with col_centered[1]:
                        st.video(video_clips[word], autoplay=True)
                    st.success(f"✅ Recognized: {word}")
                else:
                    st.error(f"Word ({word}) not supported")
            except Exception as e:
                st.error("⚠️ ضغط كبير على الخدمة، استنى شوية وجرب تتكلم تاني.")

with st.sidebar:
    st.header("📜 History")
    for item in reversed(st.session_state.history):
        st.write(f"• {item}")

st.caption("SignTalk 2.5 | Stable Version with Error Handling")