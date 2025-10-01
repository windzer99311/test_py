import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YouTube Video Downloader", page_icon="▶️", layout="wide", initial_sidebar_state="expanded")

download_path = "Downloads"

# Create Downloads folder
if not os.path.exists(download_path):
    os.makedirs(download_path)

def get_video_info(url):
    """Fetch video information"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception:
            return None

def video_downloader(url, format_choice, quality_choice):
    try:
        # Fetch video information
        with st.spinner("Analyzing video..."):
            video_info = get_video_info(url)
            
        if not video_info:
            st.error("❌ Failed to fetch video information!")
            return
        
        # Video preview
        col1, col2 = st.columns([1, 2])
        
        title = video_info.get('title', 'Unknown')
        uploader = video_info.get('uploader', 'Unknown')
        duration = video_info.get('duration', 0)
        view_count = video_info.get('view_count', 0)
        thumbnail = video_info.get('thumbnail', None)
        
        with col1:
            if thumbnail:
                st.image(thumbnail, width=300)
        
        with col2:
            st.write(f"**Title:** {title}")
            st.write(f"**Channel:** {uploader}")
            st.write(f"**Duration:** {duration} seconds ({duration//60}:{duration%60:02d})")
            st.write(f"**Views:** {view_count:,}")
            
        st.divider()
        
        # Download settings
        if format_choice == "MP4 (Video)":
            if quality_choice == "Highest Quality":
                format_selector = 'best[ext=mp4]'
                quality_info = "Highest Quality"
            elif quality_choice == "720p":
                format_selector = 'best[height<=720][ext=mp4]/best[ext=mp4]'
                quality_info = "720p or best available"
            elif quality_choice == "480p":
                format_selector = 'best[height<=480][ext=mp4]/best[ext=mp4]'
                quality_info = "480p or best available"
            else:  # 360p
                format_selector = 'best[height<=360][ext=mp4]/worst[ext=mp4]'
                quality_info = "360p or lowest available"
        else:  # MP3 (Audio)
            format_selector = 'bestaudio/best'
            quality_info = "Best Audio Quality"
        
        # Generate safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        output_template = os.path.join(download_path, f"{safe_title}.%(ext)s")
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        # MP3 conversion settings
        if format_choice == "MP3 (Audio)":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        st.success(f"✅ Format: {format_choice} - Quality: {quality_info}")
        
        # Download process
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"📥 Downloading {title}...")
        
        class ProgressHook:
            def __init__(self, progress_bar, status_text):
                self.progress_bar = progress_bar
                self.status_text = status_text
            
            def __call__(self, d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        self.progress_bar.progress(min(percent / 100, 1.0))
                        self.status_text.text(f"📥 Downloading... {percent:.1f}%")
                elif d['status'] == 'finished':
                    self.progress_bar.progress(1.0)
                    self.status_text.text("✅ Download completed!")
        
        ydl_opts['progress_hooks'] = [ProgressHook(progress_bar, status_text)]
        
        with st.spinner('Downloading...'):
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        st.success(f"🎉 **{title}** downloaded successfully!")
        st.info(f"📁 File location: {os.path.abspath(download_path)}")
        
        # List downloaded files
        files = os.listdir(download_path)
        matching_files = [f for f in files if safe_title in f]
        
        if matching_files:
            st.write("📋 Downloaded files:")
            for file in matching_files:
                file_path = os.path.join(download_path, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                st.write(f"- **{file}** ({file_size:.1f} MB)")
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        if "age-restricted" in str(e).lower():
            st.error("🔞 This video may have age restrictions.")
        elif "private" in str(e).lower():
            st.error("🔒 This video may be private.")
        elif "ffmpeg" in str(e).lower():
            st.error("🔧 FFmpeg is required! Please check the installation instructions.")
        else:
            st.error("🌐 Check your internet connection or ensure the URL is correct.")

st.title("▶️ YouTube Video Downloader")
st.write("Advanced YouTube video downloader powered by yt-dlp")

# Options
col1, col2, col3 = st.columns(3)

with col1:
    format_choice = st.selectbox(
        "📄 Format:",
        ["MP4 (Video)", "MP3 (Audio)"],
        help="Download as video or audio file"
    )

with col2:
    if format_choice == "MP4 (Video)":
        quality_choice = st.selectbox(
            "🎯 Quality:",
            ["Highest Quality", "720p", "480p", "360p"],
            help="Select video quality"
        )
    else:
        quality_choice = "Audio"
        st.selectbox(
            "🎯 Quality:",
            ["Best Audio Quality"],
            disabled=True,
            help="Automatically selects the best quality for audio"
        )

with col3:
    st.info(f"📁 Download folder:\n`{os.path.abspath(download_path)}`")

st.divider()

# URL input
video_url = st.text_input(
    "🔗 YouTube Video URL:",
    placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    help="Paste the YouTube video link here"
)

# Download button
if st.button("🚀 Analyze and Download", type="primary", use_container_width=True):
    if video_url:
        if any(site in video_url for site in ["youtube.com", "youtu.be", "m.youtube.com"]):
            video_downloader(video_url, format_choice, quality_choice)
        else:
            st.error("❌ Invalid YouTube URL! Please enter a valid YouTube link.")
    else:
        st.warning("⚠️ Please enter a YouTube video URL!")

# Usage information
with st.expander("ℹ️ Usage Information"):
    st.markdown("""
    ### How to Use:
    1. **Select format:** Video (MP4) or Audio (MP3)
    2. **Choose quality:** Select your desired video quality
    3. **Paste URL:** Enter the YouTube video link
    4. **Click the download button**
    
    ### Supported URL Formats:
    - `https://www.youtube.com/watch?v=VIDEO_ID`
    - `https://youtu.be/VIDEO_ID`
    - `https://m.youtube.com/watch?v=VIDEO_ID`
    
    ### Notes:
    - Files are saved in the `Downloads` folder
    - FFmpeg is required for MP3 conversion
    - yt-dlp is a reliable and up-to-date solution
    """)

# FFmpeg installation guide
with st.expander("🔧 FFmpeg Installation Guide"):
    st.markdown("""
    ### FFmpeg Installation (Required for MP3):
    
    **Windows:**
    ```bash
    # Using Chocolatey
    choco install ffmpeg
    
    # Using Winget
    winget install ffmpeg
    
    # Manual: https://ffmpeg.org/download.html
    ```
    
    **Linux (Ubuntu/Debian):**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```
    
    **macOS:**
    ```bash
    # Using Homebrew
    brew install ffmpeg
    ```
    
    ### Verify Installation:
    Run the following command in the terminal:
    ```bash
    ffmpeg -version
    ```
    """)