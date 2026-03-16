import streamlit as st
from google import genai
from google.genai import types
import cv2
import tempfile
import time
from gtts import gTTS
import os
from dotenv import load_dotenv

# --- إضافة مكتبات Firebase ---
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
api_key = os.getenv("API_KEY")

# --- تهيئة Firebase (Spark Plan - بدون فيزا) ---
if not firebase_admin._apps:
    try:
        # تأكد من وجود ملف JSON الصلاحيات بجانب الكود
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    except Exception:
        pass 

db = firestore.client() if firebase_admin._apps else None

def save_to_cloud(action, word, confidence="N/A"):
    """حفظ النتائج في Firestore لإثبات استخدام Google Cloud للمحكمين"""
    if db:
        try:
            db.collection('SignTalk_Logs').add({
                'action': action,
                'word': word,
                'confidence': confidence,
                'time': firestore.SERVER_TIMESTAMP
            })
        except:
            pass

# ---------------- الكاش وتعديل مسار الفيديوهات ----------------
@st.cache_resource
def get_video_clips():
    """تحميل الفيديوهات من فولدر video"""
    return {
        "FINE": "video/fine.mp4",
        "FORGET": "video/forget.mp4",
        "GO": "video/go.mp4",
        "HAPPY": "video/happy.mp4",
        "LIKE": "video/like.mp4",
        "MORE": "video/more.mp4",
        "NEED": "video/need.mp4",
        "PLEASE": "video/please.mp4",
        "RIGHT": "video/right.mp4",
        "SAD": "video/sad.mp4",
        "THANK YOU": "video/thank_you.mp4",
        "WANT": "video/want.mp4",
        "WRONG": "video/wrong.mp4",
        "YES": "video/yes.mp4"
    }

@st.cache_data(ttl=3600)
def analyze_text_with_gemini(text):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"Analyze this text and convert it to one of these exact ASL signs only: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return the matching word only.", text]
    )
    return response.text.strip().upper()

@st.cache_data(ttl=3600)
def analyze_speech_with_gemini(audio_bytes, mime_type):
    client = genai.Client(api_key=api_key)
    part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Analyze this speech and convert it to one of these exact ASL signs only: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return the matching word only.", part]
    )
    return response.text.strip().upper()

@st.cache_resource
def load_video_bytes(video_path):
    if os.path.exists(video_path):
        with open(video_path, 'rb') as f:
            return f.read()
    return None

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SignTalk 2.5 Pro Max", layout="wide")
st.title("🤟 SignTalk 2.5 Pro Max")
st.subheader("Universal Sign Language Translator - Two Way")

if 'history' not in st.session_state:
    st.session_state.history = []

client = genai.Client(api_key=api_key)
video_clips = get_video_clips()

# ====================== PART 1: Sign → Speech + Text ======================
st.header("1️⃣ Sign → Speech + Text")

col1, col2 = st.columns([2, 1])
with col1:
    frame_placeholder = st.empty()
    status_placeholder = st.empty()
with col2:
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
            out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, (640, 480))
            
            start_time = time.time()
            while (time.time() - start_time) < 4:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    frame_placeholder.image(frame, channels="BGR")
                else: break
            cap.release()
            out.release()

        with st.spinner('🧬 Gemini 2.5 is analyzing...'):
            with open(temp_path, 'rb') as f:
                file_bytes = f.read()
            
            prompt = "Identify one of these ASL signs: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return ONLY: [WORD] | [CONFIDENCE%]"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, types.Part.from_bytes(data=file_bytes, mime_type="video/mp4")]
            )
            
            full_res = response.text.strip()
            word = full_res.split('|')[0].strip() if '|' in full_res else full_res
            conf = full_res.split('|')[1].strip() if '|' in full_res else "N/A"
            
            st.session_state.history.append(f"Sign → {word} ({conf})")
            save_to_cloud("Sign to Speech", word, conf) # الحفظ في السحابة
            
            status_placeholder.success(f"✅ Result: {word}")
            confidence_placeholder.metric("Confidence", conf)
            
            tts = gTTS(text=word, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
            st.audio(fp.name, format="audio/mp3", autoplay=True)

# ====================== PART 2: Text/Speech → Sign Video ======================
st.header("2️⃣ Text or Speech → Sign Video")

tab1, tab2 = st.tabs(["✍️ Type", "🎤 Speak"])

with tab1:
    text_input = st.text_input("Type the word")
    if st.button("Analyze Text"):
        with st.spinner("Analyzing text..."):
            word = analyze_text_with_gemini(text_input)
            if word in video_clips:
                v_bytes = load_video_bytes(video_clips[word])
                if v_bytes:
                    st.success(f"✅ Result: {word}")
                    # تصغير حجم الفيديو وعرضه في المنتصف
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c2:
                        st.video(v_bytes, format="video/mp4", autoplay=True)
                    st.session_state.history.append(f"Text → {word}")
                    save_to_cloud("Text to Sign", word)
            else: 
                st.error("Not supported")

with tab2:
    audio_input = st.audio_input("Speak now")
    if audio_input:
        # إضافة زر لتأكيد بدء التحليل وتجنب إرسال بيانات فارغة
        if st.button("Analyze Speech"):
            with st.spinner("Gemini is analyzing speech..."):
                # استخدام getvalue بدلاً من read لحل مشكلة الـ Empty Bytes
                audio_bytes = audio_input.getvalue()
                mime_type = audio_input.type or "audio/wav"
                word = analyze_speech_with_gemini(audio_bytes, mime_type)
                
                if word in video_clips:
                    v_bytes = load_video_bytes(video_clips[word])
                    if v_bytes:
                        st.success(f"✅ Result: {word}")
                        # تصغير حجم الفيديو وعرضه في المنتصف
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c2:
                            st.video(v_bytes, format="video/mp4", autoplay=True)
                        st.session_state.history.append(f"Speech → {word}")
                        save_to_cloud("Speech to Sign", word)
                else: 
                    st.error(f"Word ({word}) not supported")

with st.sidebar:
    st.header("📜 History")
    for item in reversed(st.session_state.history):
        st.write(f"• {item}")

st.caption("SignTalk 2.5 | Gemini Live Agent Challenge")