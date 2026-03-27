🤟 SignTalk 2.5 Pro Max

AI-Powered Two-Way Sign Language Translator

SignTalk is an accessibility-focused AI application that enables communication between deaf and hearing communities by translating between American Sign Language (ASL) and spoken or written English.

The system uses Google Gemini models and Google Cloud services to analyze text, speech, and video inputs and convert them into understandable communication formats.

This project was built for the
Gemini Live Agent Challenge.


🚀 Features

1️⃣ Sign → Speech + Text

Users perform a sign gesture using a webcam or DroidCam.

The system:

Records a short video

Sends it to the Gemini 2.5 Flash model

Detects the ASL word

Converts the result to speech using Text-to-Speech

Example output:

Result: HAPPY
Confidence: 92%
2️⃣ Text → Sign Language

Users type a word in English.

The AI analyzes the text and displays the corresponding ASL sign video.

Example:

Input: THANK YOU
Output: Sign video
3️⃣ Speech → Sign Language

Users can speak directly into the microphone.

The system:

Captures speech

Sends audio to Gemini

Detects the intended word

Displays the corresponding sign video

☁️ Google Cloud Integration

SignTalk integrates with
Google Cloud
using Firestore to store translation logs.

Each interaction is recorded in the cloud including:

action type

detected word

confidence score

timestamp

This demonstrates real cloud-based AI application architecture.

🧠 AI Technologies Used

Gemini 2.5 Flash

Google GenAI SDK

Computer Vision

Speech Processing

Streamlit interactive interface

🛠 Tech Stack

Python

Streamlit

OpenCV

Google Generative AI

Firebase Firestore

gTTS (Google Text-to-Speech)

python-dotenv

📂 Project Structure

```
SignTalk-2.5
│
├── app.py
│
├── video/
│   ├── fine.mp4
│   ├── forget.mp4
│   ├── go.mp4
│   ├── happy.mp4
│   ├── like.mp4
│   ├── more.mp4
│   ├── need.mp4
│   ├── please.mp4
│   ├── right.mp4
│   ├── sad.mp4
│   ├── thank_you.mp4
│   ├── want.mp4
│   ├── wrong.mp4
│   └── yes.mp4
│
├── firebase_credentials.json
├── requirements.txt
├── .gitignore
└── README.md

⚙️ Installation
```

Clone the repository:

git clone https://github.com/AlyBama/SignTalk-2.5
cd SignTalk-2.5

Install dependencies:

pip install -r requirements.txt
🔑 Environment Variables

Create a .env file:

API_KEY=your_google_gemini_api_key

⚠️ Do NOT upload .env to GitHub.

▶️ Run the Application
streamlit run app.py

The application will open in your browser.

📸 Demo Workflow
Sign → Speech

Perform a sign gesture

Gemini analyzes the video

The detected word is spoken aloud

Speech → Sign

Speak a word

Gemini identifies the word

The corresponding ASL video appears

Text → Sign

Type a word

AI maps it to a sign language video

🌍 Vision

SignTalk aims to make communication more inclusive by leveraging AI and cloud technologies to bridge the gap between sign language users and spoken language users.

👨‍💻 Developer

Aly Helmy

Video demo link : https://vimeo.com/1173926970?share=copy&fl=sv&fe=ci

GitHub
https://github.com/AlyBama

Project Repository
https://github.com/AlyBama/SignTalk-2.5

⭐ Support

If you like this project:

⭐ Star the repository

🤝 Share it with others

Built for Gemini Live Agent Challenge 2026
