import streamlit as st
import requests
import base64
from gtts import gTTS
import os
from io import BytesIO
from openai import OpenAI

# ==============================
# SETUP
# ==============================
st.set_page_config(page_title="AI Pronunciation Coach", page_icon="🎤")
st.title("🎤 AI Pronunciation Coach")
st.write("Hãy nói một câu tiếng Anh, AI sẽ nghe, chấm điểm và phản hồi bằng giọng nói!")

# Tạo client OpenAI (đảm bảo anh đã set API key trong Streamlit Cloud secret)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==============================
# HTML + JS Recorder
# ==============================
st.markdown("""
    <style>
    .recorder-container {
        text-align: center;
        margin-top: 20px;
    }
    button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 10px 24px;
        font-size: 16px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

record_html = """
<div class="recorder-container">
  <button id="recordButton">🎙️ Start Recording</button>
  <p id="status"></p>
  <audio id="audioPlayback" controls></audio>
</div>

<script>
  let chunks = [];
  let recorder;
  const recordButton = document.getElementById('recordButton');
  const status = document.getElementById('status');
  const audioPlayback = document.getElementById('audioPlayback');

  recordButton.onclick = async () => {
    if (recordButton.textContent.includes('Start')) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);
      chunks = [];

      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = e => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const audioURL = URL.createObjectURL(blob);
        audioPlayback.src = audioURL;

        // Gửi blob về Streamlit
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
          const base64data = reader.result.split(',')[1];
          window.parent.postMessage({ type: 'streamlit:setComponentValue', value: base64data }, '*');
        };
      };

      recorder.start();
      recordButton.textContent = '⏹ Stop Recording';
      status.textContent = 'Recording...';
    } else {
      recorder.stop();
      recordButton.textContent = '🎙️ Start Recording';
      status.textContent = 'Stopped.';
    }
  };
</script>
"""

base64_audio = st.components.v1.html(record_html, height=300)

# ==============================
# HANDLE AUDIO & AI RESPONSE
# ==============================
if base64_audio:
    st.success("✅ Đã thu âm xong! Đang xử lý...")

    # Lưu file tạm
    audio_bytes = base64.b64decode(base64_audio)
    with open("temp_audio.webm", "wb") as f:
        f.write(audio_bytes)

    # --------------------
    # 1️⃣ Whisper: Chuyển giọng nói thành văn bản
    # --------------------
    with open("temp_audio.webm", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )
    user_text = transcript.text
    st.write(f"🗣️ **Bạn nói:** {user_text}")

    # --------------------
    # 2️⃣ GPT: Chấm điểm & phản hồi
    # --------------------
    prompt = f"""
    Bạn là giáo viên tiếng Anh. Hãy nghe đoạn phát âm sau:
    "{user_text}"
    Đánh giá mức độ phát âm (từ 1 đến 10), nhận xét lỗi chính, và gợi ý cách phát âm tốt hơn.
    Viết bằng tiếng Việt, ngắn gọn.
    """

    feedback = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là giáo viên dạy phát âm tiếng Anh."},
            {"role": "user", "content": prompt}
        ]
    )

    feedback_text = feedback.choices[0].message.content
    st.markdown(f"### 💬 Phản hồi từ AI:\n{feedback_text}")

    # --------------------
    # 3️⃣ gTTS: Đọc lại phản hồi
    # --------------------
    tts = gTTS(text=feedback_text, lang="vi")
    tts_buffer = BytesIO()
    tts.write_to_fp(tts_buffer)
    tts_buffer.seek(0)

    audio_base64 = base64.b64encode(tts_buffer.read()).decode()
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

    # Xóa file tạm
    os.remove("temp_audio.webm")
