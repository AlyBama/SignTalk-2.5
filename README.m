# 🤟 SignTalk 2.5 Pro Max

**Universal Two-Way Sign Language Translator powered by AI**

SignTalk is an AI-powered application that translates between **American Sign Language (ASL)** and **spoken or written English** in real time using **computer vision and generative AI**.

The system works in **two directions**:

* ✋ **Sign → Speech & Text**
* 🗣 **Speech/Text → Sign Video**

This makes communication easier between **deaf and hearing people**.

---

# 🚀 Features

### 1️⃣ Sign → Speech + Text

* Capture sign language using webcam or DroidCam
* AI analyzes the sign using **Gemini Vision**
* Returns:

  * Detected word
  * Confidence level
* Converts the result into **spoken audio**

Example output:

```
Result: HAPPY
Confidence: 92%
```

---

### 2️⃣ Text → Sign Language

Users type an English word and the system converts it into a **sign language video**.

Example:

```
Input: THANK YOU
Output: Sign video
```

---

### 3️⃣ Speech → Sign Language

Users can speak directly into the microphone.

The AI:

1. Analyzes speech
2. Detects the intended word
3. Displays the corresponding **ASL video**

---

# 🧠 AI Technologies Used

* Generative AI (Gemini)
* Computer Vision
* Speech Processing
* Streamlit interactive UI

---

# 🛠 Tech Stack

* Python
* Streamlit
* OpenCV
* Google Generative AI
* gTTS (Google Text-to-Speech)
* python-dotenv

---

# 📂 Project Structure

```
SignTalk
│
├── app.py
├── fine.mp4
├── forget.mp4
├── go.mp4
├── happy.mp4
├── like.mp4
├── more.mp4
├── need.mp4
├── please.mp4
├── right.mp4
├── sad.mp4
├── thank_you.mp4
├── want.mp4
├── wrong.mp4
├── yes.mp4
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/AlyBama/SignTalk.git
cd SignTalk
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project folder:

```
API_KEY=your_google_api_key
```

⚠️ Never upload the `.env` file to GitHub.

---

# ▶️ Run the App

```bash
streamlit run app.py
```

The app will open in your browser.

---

# 📸 Demo Workflow

1️⃣ Perform a sign using your camera
2️⃣ AI analyzes the video
3️⃣ The detected word is spoken aloud

OR

1️⃣ Speak a word
2️⃣ AI detects it
3️⃣ Corresponding sign video appears

---

# 🌍 Vision

SignTalk aims to reduce communication barriers between **deaf and hearing communities** by making sign language translation **accessible, fast, and AI-powered**.

---

# 🏆 Built For

AI innovation challenges such as:

* Gemini AI Challenge
* AI Hackathons
* Accessibility Technology Projects

---

# 👨‍💻 Developer

**Aly Helmy**

GitHub:
https://github.com/AlyBama

---

# ⭐ Support

If you like this project:

⭐ Star the repository
🤝 Share it with others
