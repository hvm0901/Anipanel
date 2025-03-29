import streamlit as st
import imageio
import os
import numpy as np
from PIL import Image
import tempfile
from pathlib import Path
import time

# --- Helper Functions ---
def create_video(image_files, framerate, output_format):
    temp_dir = Path(tempfile.gettempdir())
    output_ext = "gif" if output_format == "GIF" else "mp4"
    output_path = temp_dir / f"animation.{output_ext}"
    
    image_files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in Path(x.name).stem.split()])
    frames = []
    target_size = None
    
    for img in image_files:
        try:
            image = Image.open(img).convert("RGB")
            if target_size is None:
                target_size = image.size
            else:
                image = image.resize(target_size, Image.LANCZOS)
            frames.append(np.array(image))
        except Exception as e:
            st.error(f"Error processing image '{img.name}': {e}")
            return None
    
    if not frames:
        st.error("No valid images were uploaded.")
        return None
    
    try:
        if output_format == "GIF":
            imageio.mimsave(output_path, frames, fps=framerate, format='GIF')
        else:
            imageio.mimsave(output_path, frames, fps=framerate, format='FFMPEG')
        return str(output_path)
    except Exception as e:
        st.error(f"Error creating video: {e}")
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Animate your ideas!", layout="wide")

# Custom CSS for premium UI with better button positioning
st.markdown(
    """
    <style>
    body { background-color: #121212; color: #ffffff; }
    .st-emotion-cache-0 { background: linear-gradient(135deg, #1e1e1e, #232323); padding: 2rem; border-radius: 10px; }
    .stButton>button { background: linear-gradient(90deg, #ff8c00, #ff2d55); color: white; border-radius: 8px; width: 100%; padding: 12px; font-size: 18px; }
    .stButton>button:hover { background: linear-gradient(90deg, #ff6a00, #ff1e40); }
    .stSlider>div>div>div[data-baseweb="slider"] { background-color: #ff2d55; }
    .stVideo>video { border-radius: 10px; border: 2px solid #ff2d55; }
    .stFileUploader { border: 2px dashed #ff2d55; padding: 10px; border-radius: 10px; }
    .button-container { display: flex; justify-content: center; margin-top: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎞️ Animate your ideas!")
st.write("Upload panels in sequence, customize frame rates, and download your animations with ease!")

uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
st.write("Preview your images below:")
if uploaded_files:
    cols = st.columns(min(len(uploaded_files), 4))
    for i, file in enumerate(uploaded_files):
        cols[i % len(cols)].image(file, use_container_width=True)
    
framerate = st.slider("Frame Rate (FPS)", 1, 30, 10)
output_format = st.radio("Select Output Format", ("MP4", " GIF (Preview not available for this format, download)"))

# Centered button for better UX
with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Animation"):
            with st.spinner("Processing..."):
                progress_bar = st.progress(0)
                for percent in range(0, 101, 10):
                    time.sleep(0.2)
                    progress_bar.progress(percent)
                
                video_path = create_video(uploaded_files, framerate, output_format)
            
            if video_path:
                st.success("Animation created successfully!")
                video_bytes = open(video_path, "rb").read()
                st.video(video_bytes, format=f"video/{output_format.lower()}")
                st.download_button("📥 Download Animation", video_bytes, f"animation.{output_format.lower()}", f"video/{output_format.lower()}")
                os.remove(video_path)
            else:
                st.error("Failed to generate the animation. Ensure your images are valid.")
