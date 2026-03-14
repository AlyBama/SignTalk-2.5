import streamlit as st
from google import genai
from google.genai import types
import cv2
import tempfile
import time
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# ---------------- إضافة الكاش هنا ----------------
@st.cache_resource
def get_video_clips():
    """تحميل قائمة مسارات الفيديو (مرة واحدة فقط)"""
    return {
        "FINE": "fine.mp4",
        "FORGET": "forget.mp4",
        "GO": "go.mp4",
        "HAPPY": "happy.mp4",
        "LIKE": "like.mp4",
        "MORE": "more.mp4",
        "NEED": "need.mp4",
        "PLEASE": "please.mp4",
        "RIGHT": "right.mp4",
        "SAD": "sad.mp4",
        "THANK YOU": "thank_you.mp4",
        "WANT": "want.mp4",
        "WRONG": "wrong.mp4",
        "YES": "yes.mp4"
    }

@st.cache_data(ttl=3600)  # تخزين النتائج لمدة ساعة
def analyze_text_with_gemini(text):
    """إرسال النص إلى Gemini وتحويله إلى كلمة ASL (مع الكاش)"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[f"Analyze this text and convert it to one of these exact ASL signs only: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return the matching word only.", text]
    )
    return response.text.strip().upper()

@st.cache_data(ttl=3600)
def analyze_speech_with_gemini(audio_bytes, mime_type):
    """إرسال الصوت إلى Gemini وتحويله إلى كلمة ASL (الكاش يعمل فقط إذا تكرر نفس الصوت تمامًا)"""
    client = genai.Client(api_key=api_key)
    part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Analyze this speech and convert it to one of these exact ASL signs only: FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES. Return the matching word only.", part]
    )
    return response.text.strip().upper()

@st.cache_resource
def load_video_bytes(video_path):
    """تحميل ملف الفيديو كـ bytes مرة واحدة فقط"""
    if os.path.exists(video_path):
        with open(video_path, 'rb') as f:
            return f.read()
    return None
# ---------------- نهاية الكاش ----------------

st.set_page_config(page_title="SignTalk 2.5 Pro Max", layout="wide")
st.title("🤟 SignTalk 2.5 Pro Max")
st.subheader("Universal Sign Language Translator - Two Way")

if 'history' not in st.session_state:
    st.session_state.history = []

client = genai.Client(api_key=api_key)

# استخدام دالة الكاش للحصول على الفيديوهات
video_clips = get_video_clips()

# ====================== PART 1: Sign → Speech + Text ONLY ======================
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
            status_placeholder.warning(f"⏳ Get ready... Start in {i}")
            time.sleep(1)
        status_placeholder.error("🎥 RECORDING... Perform the sign now!")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
            temp_path = tfile.name
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_path, fourcc, 30.0, (640, 480))
            
            start_time = time.time()
            while (time.time() - start_time) < 4:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    frame_placeholder.image(frame, channels="BGR", caption="Live Feed")
                else:
                    break
            cap.release()
            out.release()

        with st.spinner('🧬 Gemini is analyzing the sign...'):
            with open(temp_path, 'rb') as f:
                file_bytes = f.read()
            
            prompt = """
            Analyze this video. You are an expert in American Sign Language (ASL).
            Identify one of these signs only:
            FINE, FORGET, GO, HAPPY, LIKE, MORE, NEED, PLEASE, RIGHT, SAD, THANK YOU, WANT, WRONG, YES
            Return ONLY: [WORD] | [CONFIDENCE%]
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, types.Part.from_bytes(data=file_bytes, mime_type="video/mp4")]
            )
            
            full_res = response.text.strip()
            word = full_res.split('|')[0].strip() if '|' in full_res else full_res
            conf = full_res.split('|')[1].strip() if '|' in full_res else "N/A"
            
            st.session_state.history.append(f"Sign → {word} ({conf})")
            status_placeholder.success(f"✅ Result: {word}")
            confidence_placeholder.metric("Confidence", conf)
            
            tts = gTTS(text=word, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
            st.audio(fp.name, format="audio/mp3", autoplay=True)

# ====================== PART 2: Text/Speech → Sign Video (with real analysis) ======================
st.header("2️⃣ Text or Speech → Sign Video")

tab1, tab2 = st.tabs(["✍️ Type the word", "🎤 Speak"])

with tab1:
    text_input = st.text_input("Type the word in English")
    if st.button("Analyze Text with Gemini"):
        with st.spinner("Gemini is analyzing the text..."):
            # استخدام الكاش لتحليل النص
            word = analyze_text_with_gemini(text_input)
            
            if word in video_clips and os.path.exists(video_clips[word]):
                # استخدام الكاش لتحميل الفيديو
                video_bytes = load_video_bytes(video_clips[word])
                if video_bytes:
                    st.video(video_bytes, format="video/mp4", width=500, autoplay=True)
                    st.success(f"✅ Showing sign for: {word}")
                    st.session_state.history.append(f"Text → {word}")
                else:
                    st.error("Video file not found")
            else:
                st.error("Word not supported")

with tab2:
    audio_input = st.audio_input("Speak now")
    if audio_input is not None:
        with st.spinner("Gemini is listening and analyzing..."):
            audio_bytes = audio_input.read()
            mime_type = audio_input.type or "audio/wav"
            # استخدام الكاش لتحليل الصوت
            word = analyze_speech_with_gemini(audio_bytes, mime_type)
            
            if word in video_clips and os.path.exists(video_clips[word]):
                video_bytes = load_video_bytes(video_clips[word])
                if video_bytes:
                    st.video(video_bytes, format="video/mp4", width=500, autoplay=True)
                    st.success(f"✅ Showing sign for: {word}")
                    st.session_state.history.append(f"Speech → {word}")
                else:
                    st.error("Video file not found")
            else:
                st.error(f"Word ({word}) not supported")

with st.sidebar:
    st.header("📜 History")
    for item in reversed(st.session_state.history):
        st.write(f"• {item}")

st.caption("SignTalk 2.5 | Gemini Live Agent Challenge - Two Way")