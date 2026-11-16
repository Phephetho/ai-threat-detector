import streamlit as st
from PIL import Image
import io
import tempfile
import os
from chat_app import render_chat_app

st.set_page_config(
    page_title="AI Threat Detector",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI Threat Detector")
st.markdown("Lesotho Tourism Development Corporation - AI Threat Detection Platform")
st.markdown("Detect AI-generated phishing emails and deepfake media.")

module = st.sidebar.radio(
    "Select detection type:",
    [
        "📧 Phishing Email Detector",
        "🖼️ Deepfake Image Detector",
        "🎙️ Deepfake Audio Detector",
        "🎬 Deepfake Video Detector",
        "🔐 End-to-End Encrypted Chat"
    ]
)

@st.cache_resource
def load_phishing_model():
    from models.phishing_detector import PhishingDetector
    return PhishingDetector()

@st.cache_resource
def load_image_model():
    from models.image_detector import ImageDeepfakeDetector
    return ImageDeepfakeDetector()

@st.cache_resource
def load_audio_model():
    from models.audio_detector import AudioDeepfakeDetector
    return AudioDeepfakeDetector()

@st.cache_resource
def load_video_model():
    from models.video_detector import VideoDeepfakeDetector
    return VideoDeepfakeDetector()


if module == "📧 Phishing Email Detector":
    st.header("Phishing Email Detection")
    input_method = st.radio("Input method:", ["Paste Text", "Upload File"], horizontal=True)
    email_text = ""
    if input_method == "Paste Text":
        email_text = st.text_area("Email content:", height=300)
    else:
        uploaded_file = st.file_uploader("Upload email file", type=["txt", "eml"])
        if uploaded_file:
            email_text = uploaded_file.read().decode("utf-8", errors="ignore")
            st.text_area("File content:", email_text, height=200, disabled=True)
    if st.button("🔍 Analyze Email", type="primary"):
        if email_text.strip():
            with st.spinner("Analyzing..."):
                detector = load_phishing_model()
                result = detector.analyze(email_text)
                st.markdown("---")
                st.subheader("Analysis Results")
                col1, col2 = st.columns(2)
                with col1:
                    if result['is_phishing']:
                        st.error("🚨 **PHISHING DETECTED**")
                    else:
                        st.success("✅ **LEGITIMATE**")
                    st.metric("Confidence", f"{result['confidence']:.1%}")
                with col2:
                    st.markdown("**Risk Indicators:**")
                    for indicator in result['indicators']:
                        st.markdown(f"- {indicator}")
        else:
            st.warning("Please provide email content.")

elif module == "🖼️ Deepfake Image Detector":
    st.header("Deepfake Image Detection")
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_image:
        image = Image.open(uploaded_image).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)
        if st.button("🔍 Analyze Image", type="primary"):
            with st.spinner("Analyzing..."):
                detector = load_image_model()
                result = detector.analyze(image)
                st.markdown("---")
                st.subheader("Analysis Results")
                col1, col2 = st.columns(2)
                with col1:
                    if result['is_fake']:
                        st.error("🚨 **AI-GENERATED IMAGE**")
                    else:
                        st.success("✅ **AUTHENTIC IMAGE**")
                    st.metric("Confidence", f"{result['confidence']:.1%}")
                with col2:
                    st.markdown(f"- Model: {result['model_name']}")
                    st.markdown(f"- Input Size: {result['input_size']}")
                    st.markdown(f"- Inference Time: {result['inference_time']:.2f}s")

elif module == "🎙️ Deepfake Audio Detector":
    st.header("Deepfake Audio Detection")
    uploaded_audio = st.file_uploader("Choose an audio file...", type=["wav", "mp3", "flac", "m4a"])
    if uploaded_audio:
        st.audio(uploaded_audio, format="audio/wav")
        if st.button("🔍 Analyze Audio", type="primary"):
            with st.spinner("Analyzing..."):
                import librosa
                audio_bytes = uploaded_audio.read()
                audio_array, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
                detector = load_audio_model()
                result = detector.analyze(audio_array, sr)
                st.markdown("---")
                st.subheader("Analysis Results")
                col1, col2 = st.columns(2)
                with col1:
                    if result['is_fake']:
                        st.error("🚨 **AI-GENERATED AUDIO**")
                    else:
                        st.success("✅ **AUTHENTIC AUDIO**")
                    st.metric("Confidence", f"{result['confidence']:.1%}")
                with col2:
                    st.markdown(f"- Model: {result['model_name']}")
                    st.markdown(f"- Inference Time: {result['inference_time']:.2f}s")

elif module == "🎬 Deepfake Video Detector":
    st.header("Deepfake Video Detection")
    st.info("Note: Works best on Sora/Veo2-style AI videos.")
    uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov", "mkv"])
    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_video.read())
            video_path = tmp.name
        st.video(video_path)
        if st.button("🔍 Analyze Video", type="primary"):
            with st.spinner("Analyzing video..."):
                detector = load_video_model()
                result = detector.analyze(video_path, num_frames=16)
                st.markdown("---")
                st.subheader("Analysis Results")
                if result.get('error'):
                    st.error(f"Error: {result['error']}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        if result['is_fake']:
                            st.error("🚨 **AI-GENERATED VIDEO**")
                        else:
                            st.success("✅ **AUTHENTIC VIDEO**")
                        st.metric("Confidence", f"{result['confidence']:.1%}")
                        st.metric("Frames Analyzed", result['frames_analyzed'])
                    with col2:
                        st.markdown(f"- Avg Fake Prob: {result['avg_fake_probability']:.2%}")
                        st.markdown(f"- Inference Time: {result['inference_time']:.2f}s")
        
        # Cleanup the temp file safely
        if os.path.exists(video_path):
            os.remove(video_path)

elif module == "🔐 End-to-End Encrypted Chat":
    render_chat_app()