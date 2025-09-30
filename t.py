import streamlit as st
import sounddevice as sd
import numpy as np
import tempfile
import whisper
import difflib
import pyttsx3
import time
import soundfile as sf

# ===============================
# 1. Cache Whisper model (load 1 lần)
# ===============================
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")  # dùng tiny cho nhanh

model = load_whisper_model()

# ===============================
# 2. Hàm ghi âm
# ===============================
def record_audio(duration=5, fs=16000):
    st.info("🎤 Đang ghi âm... Nói đi bạn!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    st.success("✅ Ghi âm xong!")
    return np.squeeze(recording)

# ===============================
# 3. Chấm điểm phát âm (so sánh với IPA/từ gốc)
# ===============================
def check_pronunciation(user_text, target_word):
    ratio = difflib.SequenceMatcher(None, user_text.lower(), target_word.lower()).ratio()
    return ratio

# ===============================
# 4. Đọc to từ vựng
# ===============================
def speak_word(word):
    engine = pyttsx3.init()
    engine.say(word)
    engine.runAndWait()

# ===============================
# 5. Streamlit UI
# ===============================
def main():
    st.title("📚 Luyện phát âm từ vựng")
    st.write("Nói theo từ hệ thống đưa ra, rồi kiểm tra đúng sai 🚀")

    # Từ vựng mẫu
    vocab = {
        "apple": {"mean": "quả táo", "ipa": "/ˈæp.l̩/"},
        "banana": {"mean": "quả chuối", "ipa": "/bəˈnɑː.nə/"},
        "orange": {"mean": "quả cam", "ipa": "/ˈɒr.ɪndʒ/"}
    }

    word = st.selectbox("Chọn từ để luyện:", list(vocab.keys()))
    st.write(f"**Nghĩa:** {vocab[word]['mean']}")
    st.write(f"**IPA:** {vocab[word]['ipa']}")

    if st.button("🔊 Nghe phát âm"):
        speak_word(word)

    if st.button("🎙 Ghi âm & Kiểm tra"):
        audio = record_audio()

        # Lưu tạm file wav
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            sf.write(tmpfile.name, audio, 16000)
            file_path = tmpfile.name

        # Nhận diện bằng Whisper
        result = model.transcribe(file_path, fp16=False, language="en")
        user_text = result["text"].strip()

        st.write(f"🗣 Bạn nói: `{user_text}`")

        # Đánh giá đúng sai
        score = check_pronunciation(user_text, word)
        if score > 0.8:
            st.success(f"✅ Chuẩn rồi! ({score*100:.1f}%)")
        else:
            st.error(f"❌ Chưa chuẩn lắm ({score*100:.1f}%)")

if __name__ == "__main__":
    main()
