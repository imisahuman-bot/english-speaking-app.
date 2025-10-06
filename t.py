import streamlit as st
from streamlit_audiorecorder import audiorecorder
import speech_recognition as sr
import io

# ======================
# 🎧 GIAO DIỆN CHÍNH
# ======================
st.set_page_config(page_title="Luyện nói Tiếng Anh", page_icon="🎙️", layout="centered")
st.title("🎙️ Ứng dụng luyện nói Tiếng Anh")
st.write("Bấm **Record** để bắt đầu ghi âm, sau đó bấm **Stop** để nghe lại và xem phần nhận diện giọng nói.")

# ======================
# 🎤 GHI ÂM
# ======================
audio = audiorecorder("🎙️ Bắt đầu ghi âm", "⏹️ Dừng ghi âm")

if len(audio) > 0:
    # Phát lại âm thanh
    st.audio(audio.tobytes(), format="audio/wav")

    # Lưu file tạm
    wav_bytes = audio.tobytes()
    with open("voice_temp.wav", "wb") as f:
        f.write(wav_bytes)

    st.success("✅ Ghi âm thành công! Đang nhận diện giọng nói...")

    # ======================
    # 🧠 NHẬN DIỆN GIỌNG NÓI
    # ======================
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            st.subheader("📄 Kết quả nhận diện:")
            st.success(text)
        except sr.UnknownValueError:
            st.error("❌ Không nhận diện được giọng nói, hãy thử lại.")
        except sr.RequestError:
            st.error("⚠️ Lỗi khi kết nối tới dịch vụ nhận diện. Hãy thử lại sau.")

    # ======================
    # 💾 LƯU FILE (TÙY CHỌN)
    # ======================
    with st.expander("💾 Tải xuống file âm thanh"):
        st.download_button(
            label="Tải file WAV",
            data=wav_bytes,
            file_name="voice_record.wav",
            mime="audio/wav"
        )

else:
    st.info("👉 Hãy bấm **Record** để bắt đầu ghi âm.")


